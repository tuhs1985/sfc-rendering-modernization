"""Explicit, hash-pinned allowlist packager; never recursively packages a workspace.

The reviewed recipe is a build input, not a discovery mechanism. Vendor files
must name their upstream distribution and bundled notice. Nothing is uploaded.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/release'))
sys.path.insert(0,str(ROOT/'tools/remix_runtime'))
from release_manifest import SCHEMA,digest,REQUIRED_ROLES
from runtime_context import VERSION,CLIENT_SHA256,relative_name
from package_layout import excluded
from inventory_dependencies import production_files

FORBIDDEN_PARTS={'.git','.codex','.codex-attachments','runs','archives','captures','saves','settings','data'}
FORBIDDEN_SUFFIXES={'.mod','.bin','.raw32','.bmp','.dmp','.etl','.nsys-rep','.sqlite','.pdb','.obj','.lib','.exp','.log'}


def validate_recipe(recipe,source_root):
    if (recipe.get('schema')!='sfc.alpha.build.v1' or recipe.get('version')!=VERSION or
            recipe.get('license_review')!='complete' or
            not isinstance(recipe.get('commit'),str) or len(recipe['commit'])!=40):
        raise ValueError('Reviewed release recipe/commit/license inventory required')
    records=recipe.get('files',[])
    if not 1<=len(records)<=20000:raise ValueError('Allowlist file count')
    production_targets={'code/'+p for p in production_files()}
    items=[];seen=set();roles={}
    for item in records:
        source=source_root/relative_name(item['source'])
        name=relative_name(item['target']).as_posix()
        path=Path(name)
        if excluded(name):raise ValueError('Development or wrong-architecture payload: '+name)
        if name.casefold().startswith('code/tools/') and name not in production_targets:
            raise ValueError('Non-production application module: '+name)
        if (path.parts[0].casefold() in FORBIDDEN_PARTS or
                (item.get('kind')!='vendor' and (any(p.casefold() in FORBIDDEN_PARTS for p in path.parts) or path.suffix.lower() in FORBIDDEN_SUFFIXES)) or
                path.suffix.lower()=='.mod' or
                path.name.casefold().startswith('starfleetop.') or name.casefold()=='package.json'):
            raise ValueError('Non-distributable payload: '+name)
        if name.casefold() in seen:raise ValueError('Case-insensitive output collision')
        seen.add(name.casefold())
        if not source.resolve().is_relative_to(source_root.resolve()):raise ValueError('Source escapes reviewed input root')
        for part in (source,*source.parents):
            if part==source_root.parent:break
            if part.is_symlink() or (hasattr(part,'is_junction') and part.is_junction()):raise ValueError('Linked build input')
        if not source.is_file() or digest(source)!=item['sha256']:raise ValueError('Allowlisted input changed: '+item['source'])
        kind=item.get('kind')
        if kind=='vendor':
            if (not isinstance(item.get('upstream'),str) or not item['upstream'].startswith('https://') or
                    not item.get('notice')):raise ValueError('Vendor upstream and bundled notice required')
        elif kind!='project':raise ValueError('Unknown file provenance')
        if 'role' in item:
            if item['role'] in roles:raise ValueError('Duplicate application role')
            roles[item['role']]=name
        items.append((item,source,name))
    if not REQUIRED_ROLES<=roles.keys():raise ValueError('Missing required application roles')
    for item,_,_ in items:
        if item['kind']=='vendor' and item['notice'] not in {n for _,_,n in items}:
            raise ValueError('Vendor notice is not included in the ZIP')
    return items,roles


def build(recipe,source_root,output,*,check_commit=True):
    source_root=Path(source_root).resolve();output=Path(output).resolve()
    if not output.is_relative_to((ROOT/'artifacts/alpha').resolve()):
        raise ValueError('Candidate output must stay under artifacts/alpha')
    if output.exists():raise ValueError('Candidate already exists; never overwrite an earlier reviewed ZIP')
    items,roles=validate_recipe(recipe,source_root)
    if check_commit:
        head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source_root,text=True).strip()
        if head!=recipe['commit']:raise ValueError('Reviewed commit differs from checkout')
        # Untracked user files may coexist, but no modified tracked input is a
        # legitimate substitute for the reviewed source/build state.
        if subprocess.check_output(['git','diff','HEAD','--name-only'],cwd=source_root,text=True).strip():
            raise ValueError('Tracked working tree has unreviewed changes')
        for item,source,_ in items:
            if item['kind']!='project':continue
            if item['source'].startswith('artifacts/'):
                if item.get('build_commit')!=head:
                    raise ValueError('Project binary lacks reviewed-commit build provenance')
            else:
                tracked=subprocess.run(['git','show',head+':'+item['source']],cwd=source_root,
                                       stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                if tracked.returncode or hashlib.sha256(tracked.stdout).hexdigest()!=item['sha256']:
                    raise ValueError('Project input is not the reviewed committed file: '+item['source'])
    manifest=dict(schema=SCHEMA,version=VERSION,platform='windows-x64',client_sha256=CLIENT_SHA256,
                  commit=recipe['commit'],roles=roles,game_profile=recipe['game_profile'],remix=recipe['remix'],
                  files={name:dict(bytes=source.stat().st_size,sha256=item['sha256']) for item,source,name in items},
                  provenance={name:{k:item[k] for k in ('kind','upstream','notice') if k in item} for item,_,name in items})
    payload=json.dumps(manifest,indent=2,sort_keys=True).encode('utf-8')
    launcher=ROOT/'tools/release/SFCRemix-Launch.cmd'
    output.parent.mkdir(parents=True,exist_ok=True)
    temporary=output.with_suffix('.zip.pending')
    if temporary.exists():raise ValueError('Interrupted candidate build exists; review it before retrying')
    try:
        with zipfile.ZipFile(temporary,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
            for item,source,name in sorted(items,key=lambda x:x[2]):
                data=source.read_bytes()
                if hashlib.sha256(data).hexdigest()!=item['sha256']:raise ValueError('Input changed during packaging')
                write(archive,'SFCRemix/'+name,data)
            write(archive,'SFCRemix/package.json',payload)
            write(archive,'SFCRemix-Launch.cmd',launcher.read_bytes())
        with zipfile.ZipFile(temporary) as archive:
            if archive.testzip() is not None:raise ValueError('ZIP integrity failed')
            for name,entry in manifest['files'].items():
                if hashlib.sha256(archive.read('SFCRemix/'+name)).hexdigest()!=entry['sha256']:
                    raise ValueError('Archived input differs from reviewed file')
        temporary.rename(output)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    checksum=digest(output)
    output.with_suffix('.zip.sha256').write_text(checksum+'  '+output.name+'\n',encoding='ascii')
    return dict(zip=str(output),bytes=output.stat().st_size,sha256=checksum,files=len(items),published=False)


def write(archive,name,data):
    info=zipfile.ZipInfo(name,date_time=(2026,11,8,0,0,0))
    info.compress_type=zipfile.ZIP_DEFLATED
    info.external_attr=0o100644<<16
    archive.writestr(info,data)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--recipe',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(build(json.loads(args.recipe.read_text()),ROOT,args.output),indent=2))
