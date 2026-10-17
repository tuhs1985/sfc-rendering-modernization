"""Offline bounded scalar-contract checks; not a reproduction of native x87 lighting."""
import argparse
import json
import math
from pathlib import Path
from analyze_m1_corner_snapshot import analyze, float_bits

def dot(a, b):
    return sum(x*y for x,y in zip(a,b))

def norm(v):
    return math.sqrt(dot(v,v))

def matrix(bits):
    if len(bits)!=17: raise ValueError('Expected 68-byte transform')
    f=[float_bits(x) for x in bits[:16]]
    if not all(math.isfinite(x) for x in f): raise ValueError('Nonfinite transform')
    return [f[i:i+3] for i in (0,4,8)], [f[i] for i in (3,7,11)]

def mv(r,v):
    return [dot(row,v) for row in r]

def transpose(r):
    return list(map(list,zip(*r)))

def cross(a,b):
    return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]

def determinant(r):
    return dot(r[0],cross(r[1],r[2]))

def cosine(a,b):
    d=norm(a)*norm(b)
    return dot(a,b)/d if d>1e-15 else None

def analyze_math(packet):
    analyze(packet)  # Reuse collection/index/window/identity safeguards; gaps allowed.
    groups={}
    for s in packet['records']:
        if s['status']!=0: continue
        identity=(s['owner'],s['model'],s['source'])
        g=groups.setdefault(identity,dict(owner=s['owner'],model=s['model'],source=s['source'],
            samples=0,windows=[],basis_patterns=set(),corner_patterns=set(),dispatch_patterns=set(),
            determinant=[],gram=[],roundtrip=[],length_error=[],face_cos=[],corner_face_cos=[],
            degenerate_polygons=0))
        r,t=matrix(s['object_transform']);rt=transpose(r)
        g['samples']+=1;g['windows'].append(s['window'])
        g['basis_patterns'].add(tuple(s['object_transform'][i] for i in (0,1,2,4,5,6,8,9,10)))
        g['corner_patterns'].add(tuple(tuple(c) for c in s['corners']))
        g['dispatch_patterns'].add(tuple(s['dispatch']))
        g['determinant'].append(determinant(r))
        g['gram'].append(max(abs(dot(r[i],r[j])-int(i==j)) for i in range(3) for j in range(3)))
        polygon_corners={}
        for c in s['corners']:
            n=[float_bits(x) for x in c[2:5]];p=[float_bits(x) for x in c[5:8]]
            if not all(math.isfinite(x) for x in n+p): raise ValueError('Nonfinite corner')
            transformed=[x+y for x,y in zip(mv(r,p),t)]
            recovered=mv(rt,[x-y for x,y in zip(transformed,t)])
            g['roundtrip'].append(norm([x-y for x,y in zip(recovered,p)])/max(1,norm(p)))
            if norm(n)>1e-15: g['length_error'].append(abs(norm(mv(r,n))/norm(n)-1))
            polygon_corners.setdefault(c[0],[]).append((n,p))
        for index, corners in polygon_corners.items():
            face=[float_bits(x) for x in s['polygons'][index][4:7]]
            if not all(math.isfinite(x) for x in face): raise ValueError('Nonfinite face')
            for n,p in corners:
                value=cosine(n,face)
                if value is not None: g['corner_face_cos'].append(value)
            if len(corners)>=3:
                p0,p1,p2=[c[1] for c in corners[:3]]
                area=cross([x-y for x,y in zip(p1,p0)],[x-y for x,y in zip(p2,p0)])
                value=cosine(area,face)
                if value is None: g['degenerate_polygons']+=1
                else: g['face_cos'].append(value)
    reports=[]
    for g in groups.values():
        for name in ('basis_patterns','corner_patterns','dispatch_patterns'):
            values=g.pop(name)
            g[name+'_count']=len(values)
            if name=='dispatch_patterns': g['dispatch_patterns']=[list(v) for v in sorted(values)]
        for name in ('determinant','gram','roundtrip','length_error','face_cos','corner_face_cos'):
            values=g.pop(name)
            g[name+'_min']=min(values) if values else None
            g[name+'_max']=max(values) if values else None
        reports.append(g)
    return dict(schema='m1.corner-math.v1',groups=reports,normal_contract_fully_qualified=False,
        limitations=['Sampled prefixes only; separate literal epochs.',
                     'Python binary64 algebra, not native x87 output verification.',
                     'Dispatch observed at entry, not continuously.',
                     'Roundtrip constructed offline; no observed downstream vertex/light output.'])

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_dirs',nargs='+',type=Path)
    args=parser.parse_args()
    if len(args.run_dirs)>2: parser.error('At most two bounded runs')
    for run in args.run_dirs:
        path=run/'M1-C01-corners.json'
        if path.stat().st_size>3*1024*1024: parser.error('Packet exceeds 3 MiB')
        try: result=analyze_math(json.loads(path.read_text(encoding='utf-8-sig')))
        except (ValueError,KeyError,TypeError) as error: parser.error(str(error))
        (run/'M1-C01-math-analysis.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(run=str(run),**result)))

if __name__=='__main__': main()
