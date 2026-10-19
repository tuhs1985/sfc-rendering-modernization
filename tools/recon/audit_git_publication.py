"""Read-only bounded publication preflight for one explicit Git branch/history.

Reports locations/rule names only,never matched credential values. This heuristic
is not a guarantee that all secrets,personal information or rights issues are found.
It deliberately excludes unrelated refs/reflogs/unreachable objects from the scope.
"""
import argparse
import collections
import hashlib
import json
from pathlib import PurePosixPath
import re
import subprocess

def git(*args,stdin=None):
    return subprocess.check_output(['git',*args],input=stdin)

def audit(ref='refs/heads/master'):
    if not re.fullmatch(r'refs/heads/[A-Za-z0-9_./-]+',ref) or '..' in ref:
        raise ValueError('Explicit local branch ref required')
    head=git('rev-parse','--verify',ref+'^{commit}').decode().strip()
    paths=sorted(set(git('-c','core.quotePath=false','log',ref,'--format=','--name-only').decode().splitlines())-{''})
    objects=git('rev-list','--objects',ref).decode().splitlines()
    names={row.split(' ',1)[0]:row.split(' ',1)[1] if ' ' in row else '' for row in objects}
    meta=git('cat-file','--batch-check=%(objectname) %(objecttype) %(objectsize)',stdin=('\n'.join(names)+'\n').encode()).decode().splitlines()
    blobs=[(r.split()[0],int(r.split()[2])) for r in meta if r.split()[1]=='blob']
    total=sum(size for _,size in blobs)
    if len(blobs)>20000 or total>256*1024*1024:raise ValueError('Audit20000blob/256MiB bound exceeded;no partial clean result')
    blocked=[];reviews=[]
    denied=re.compile(r'(?i)(?:^|/)(?:Game Assets|References|captures|dumps|extracted|scratch|node_modules|\.vs)(?:/|$)|\.(?:exe|dll|pdb|lib|obj|zip|7z|rar|iso|bin|trace|etl|rdc|mod|bmp|dds|key|pem|pfx|p12)$|(?:^|/)(?:\.env(?:\..+)?|credentials\.[^/]+|secrets\.[^/]+)$')
    for path in paths:
        if denied.search(path) or path.startswith('artifacts/') and path!='artifacts/README.md':
            blocked.append(dict(path=path,rule='excluded_or_sensitive_historical_path'))
    rules={
        'github_token':rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,})\b',
        'aws_access_key':rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
        'private_key':rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----',
        'slack_token':rb'\bxox[baprs]-[A-Za-z0-9-]{20,}\b',
        'openai_or_anthropic_key':rb'\bsk-(?:proj-|svcacct-|ant-api\d+-)?[A-Za-z0-9_-]{32,}\b',
        'google_api_key':rb'\bAIza[A-Za-z0-9_-]{35}\b',
        'stripe_secret_key':rb'\b(?:sk|rk)_live_[A-Za-z0-9]{20,}\b',
        'credential_url':rb'https?://[^\s/<>"\x27:]+:[^\s/<>"\x27@]{8,}@',
    }
    patterns={name:re.compile(pattern) for name,pattern in rules.items()}
    batch=git('cat-file','--batch',stdin=('\n'.join(oid for oid,_ in blobs)+'\n').encode())
    offset=0;images=[];extensions=collections.Counter();maximum=[]
    for oid,size in blobs:
        end=batch.index(b'\n',offset);header=batch[offset:end].split();offset=end+1
        if header!=[oid.encode(),b'blob',str(size).encode()]:raise ValueError('Unexpected Git blob framing')
        raw=batch[offset:offset+size];offset+=size+1
        if len(raw)!=size:raise ValueError('Truncated Git blob')
        path=names[oid];extensions[PurePosixPath(path).suffix.lower()]+=1
        maximum.append(dict(path=path,object=oid,bytes=size))
        if size>10*1024*1024:blocked.append(dict(path=path,object=oid,rule='blob_over10MiB',bytes=size))
        if raw.startswith(b'\x89PNG\r\n\x1a\n'):
            images.append(dict(path=path,object=oid,bytes=size,sha256=hashlib.sha256(raw).hexdigest()))
            continue
        if b'\0' in raw:
            blocked.append(dict(path=path,object=oid,rule='non_png_binary_blob'));continue
        try:text=raw.decode('utf-8-sig')
        except UnicodeDecodeError:
            blocked.append(dict(path=path,object=oid,rule='non_utf8_blob_manual_review'));continue
        for name,pattern in patterns.items():
            if pattern.search(raw):blocked.append(dict(path=path,object=oid,rule=name))
        if re.search(r'(?i)(?:api[_-]?key|password|client[_-]?secret|access[_-]?token)\s*[:=]\s*["\x27][A-Za-z0-9_+/.=-]{12,}["\x27]',text):
            reviews.append(dict(path=path,object=oid,rule='possible_literal_credential_assignment'))
    if offset!=len(batch):raise ValueError('Trailing Git batch bytes')
    return dict(schema='sfc.git-publication-audit.v1',ref=ref,head=head,
        commits=int(git('rev-list','--count',ref)),historical_paths=len(paths),unique_blobs=len(blobs),
        total_blob_bytes=total,largest_blobs=sorted(maximum,key=lambda r:r['bytes'],reverse=True)[:10],
        blob_extensions=dict(extensions),blocked=blocked,manual_text_review=reviews,images_to_review=images,
        rules=list(rules),scope='Entire selected branch ancestry;not other refs,reflogs,ignored or unreachable data',
        limitations='Heuristic detection only;visual PNG/privacy and provenance review required before publication')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--ref',default='refs/heads/master');args=parser.parse_args()
    print(json.dumps(audit(args.ref),indent=2))
