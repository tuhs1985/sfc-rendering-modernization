"""Recover combined active screen projection from existing bounded live records.

Read-only algebra, NOT independent pixel/camera ground truth. No game/Kit launch.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct

LIMIT=8*1024*1024


def dot(a,b):return sum(x*y for x,y in zip(a,b))


def multiply(a,b):
    return [[sum(a[i][k]*b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]


def inverse(a):
    n=len(a)
    if not n or any(len(row)!=n for row in a):raise ValueError('Square matrix required')
    rows=[list(row)+[float(i==j) for j in range(n)] for i,row in enumerate(a)]
    if not all(math.isfinite(x) for row in rows for x in row):raise ValueError('Nonfinite matrix')
    for i in range(n):
        pivot=max(range(i,n),key=lambda j:abs(rows[j][i]))
        if abs(rows[pivot][i])<1e-12:raise ValueError('Singular matrix')
        rows[i],rows[pivot]=rows[pivot],rows[i]
        scale=rows[i][i];rows[i]=[v/scale for v in rows[i]]
        for j in range(n):
            if j!=i:
                scale=rows[j][i];rows[j]=[x-scale*y for x,y in zip(rows[j],rows[i])]
    return [row[n:] for row in rows]


def native_matrix(words):
    if len(words)!=17 or any(type(x)is not int or not 0<=x<=0xffffffff for x in words):raise ValueError('Native17word record required')
    f=struct.unpack('<16f',struct.pack('<16I',*words[:16]))
    if not all(math.isfinite(x) for x in f):raise ValueError('Nonfinite native matrix')
    flag=(words[16]>>8)&255
    if flag not in (0,1):raise ValueError('Unknown scalar affine flag')
    result=[list(f[i:i+4]) for i in (0,4,8,12)]
    # 0069CA95–CAA4 bypasses stored bottom row when native affine flag is1.
    if flag:result[3]=[0.,0.,0.,1.]
    return result


def project(matrix, point):
    out=[dot(row,list(point)+[1]) for row in matrix]
    if abs(out[3])<1e-10:raise ValueError('Point on projection plane')
    return [x/out[3] for x in out[:3]]


def camera_candidate(b):
    w=b[3][:3];ww=dot(w,w)
    if ww<1e-12:raise ValueError('Orthographic/degenerate pinhole candidate')
    scale=math.sqrt(ww)
    cx=dot(b[0][:3],w)/ww;cy=dot(b[1][:3],w)/ww
    x=[b[0][i]-cx*w[i] for i in range(3)]
    y=[b[1][i]-cy*w[i] for i in range(3)]
    nx=math.sqrt(dot(x,x));ny=math.sqrt(dot(y,y))
    if min(nx,ny)<1e-10:raise ValueError('Degenerate focal rows')
    skew=dot(x,y)/(nx*ny)
    if abs(skew)>1e-4:raise ValueError('Skewed camera outside qualified subset')
    rotation=[[v/nx for v in x],[-v/ny for v in y],[-v/scale for v in w]]
    center_inverse=inverse([b[0][:3],b[1][:3],b[3][:3]])
    center=[-dot(row,[b[0][3],b[1][3],b[3][3]]) for row in center_inverse]
    view=[row+[-dot(row,center)] for row in rotation]+[[0.,0.,0.,1.]]
    alpha=dot(b[2][:3],w)/ww;beta=b[2][3]-alpha*b[3][3]
    residual=max(abs(b[2][i]-alpha*w[i]) for i in range(3))
    q=[[nx/scale,0.,-cx,0.],[0.,-ny/scale,-cy,0.],
       [0.,0.,-alpha,beta/scale],[0.,0.,-1.,0.]]
    rebuilt=multiply(q,view)
    error=max(abs(b[i][j]/scale-rebuilt[i][j]) for i in range(4) for j in range(4))
    return {'camera_center_native':center,'view_candidate':view,'pixel_projection_candidate':q,
            'principal_point_pixels':[cx,cy],'focal_magnitudes_pixels':[nx/scale,ny/scale],
            'homogeneous_scale':scale,'normalized_skew':skew,
            'depth_alpha':alpha,'depth_beta':beta,'depth_row_residual':residual,
            'factorization_max_error':error,
            'qualification':'Pinhole, no skew; pixel-Y flip/forward convention from static viewport and perspective builder; not directly captured view/projection'}


def recover(record):
    if len(record)==96:record=record[:48] # protocol2 retains original semantic prefix
    if len(record)!=48 or any(type(x)is not int or not 0<=x<=0xffffffff for x in record):raise ValueError('Malformed live record')
    if record[4]!=1 or not record[1] or any(record[42:45]):raise ValueError('Inactive identity/unsupported math dispatch')
    supplied=native_matrix(record[8:25]);composed=native_matrix(record[25:42])
    if supplied[3]!=[0.,0.,0.,1.]:raise ValueError('Supplied transform not affine')
    combined=multiply(composed,inverse(supplied))
    rebuilt=multiply(combined,supplied)
    residual=max(abs(composed[i][j]-rebuilt[i][j]) for i in range(4) for j in range(4))
    candidate=camera_candidate(combined)
    return {'sequence':record[0],'owner_epoch':record[1],'frame':record[2],'elapsed_ms':record[3],
            'combined_world_to_screen_homogeneous':combined,'recomposition_max_error':residual,**candidate}


def inspect(path):
    path=Path(path)
    if path.stat().st_size>LIMIT:raise ValueError('Camera input exceeds8MiB')
    raw=path.read_bytes()
    if len(raw)>LIMIT:raise ValueError('Input changed beyond bound')
    result=[];excluded=[];last=0
    for index,line in enumerate(raw.splitlines()):
        if index>=2700 or len(line)>4096:raise ValueError('Record count/line bound')
        r=json.loads(line)
        if not isinstance(r,list) or len(r) not in (48,96) or type(r[0])is not int or r[0]<=last:raise ValueError('Nonmonotonic/malformed record')
        last=r[0]
        try:result.append(recover(r))
        except ValueError as exc:excluded.append({'sequence':r[0],'reason':str(exc)})
    if not result:raise ValueError('No supported active camera observations')
    def ranges(key):
        return [[min(r[key][i] for r in result),max(r[key][i] for r in result)] for i in range(len(result[0][key]))]
    return {'schema':'sfc.camera.recovery.v1','input_sha256':hashlib.sha256(raw).hexdigest(),
            'records':len(result),'excluded':excluded,'first':result[0],'last':result[-1],
            'camera_center_ranges_native':ranges('camera_center_native'),
            'principal_point_ranges_pixels':ranges('principal_point_pixels'),
            'focal_magnitude_ranges_pixels':ranges('focal_magnitudes_pixels'),
            'max_recomposition_error':max(r['recomposition_max_error'] for r in result),
            'max_factorization_error':max(r['factorization_max_error'] for r in result),
            'max_depth_row_residual':max(r['depth_row_residual'] for r in result),
            'confidence':'CONFIRMED algebra on recorded inputs; STRONG HYPOTHESIS active pinhole camera interpretation',
            'not_proven':['independent native projected-vertex match','direct +628 view/+55C projection capture',
                          'viewport rectangle','clip/depth interval and pixel-center convention','all camera modes'],
            'native_game_or_preview_changes':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();result=inspect(args.input)
    data=(json.dumps(result,indent=2,allow_nan=False)+'\n').encode()
    if len(data)>128*1024:raise ValueError('Camera report exceeds128KiB')
    with args.output.open('xb') as out:out.write(data)
    print(json.dumps({key:result[key] for key in ('records','max_recomposition_error','max_factorization_error',
        'principal_point_ranges_pixels','focal_magnitude_ranges_pixels','camera_center_ranges_native')}))
