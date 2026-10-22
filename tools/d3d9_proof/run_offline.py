"""Explicit bounded offline D3D9 execution;never launches SFC or Remix."""
from pathlib import Path
import argparse
import datetime as dt
import hashlib
import json
import os
import struct
import subprocess as sp
import sys
import time
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/scene_bridge'))
sys.path.insert(0,str(ROOT/'tools/remix_runtime'))
from evidence_budget import AGGREGATE_BYTES
from scene_bundle import prepare,read_replay

EXE=ROOT/'artifacts/d3d9-proof/bin/d3d9_replay.exe'
CAPTURE=ROOT/'artifacts/m1/runs/20261016-223535-enabled'
GAME=Path(r'C:\Project\SFC-Remix-Return-Test')
SOURCES=('tools/scene_bridge/scene_bundle.py','tools/d3d9_proof/d3d9_replay.cpp',
    'tools/d3d9_proof/build.ps1','tools/d3d9_proof/run_offline.py','tools/d3d9_proof/synthetic.py',
    'tools/d3d9_proof/startup.py','tools/d3d9_proof/d3d9_startup_probe.cpp',
    'tools/remix_ingest/live_scene.py','tools/remix_ingest/live_camera.py',
    'tools/remix_ingest/live_bridge.py','tools/m1_component/analyze_live_camera.py')


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pixels(path):
    raw=Path(path).read_bytes()
    if not 8<=len(raw)<=1920*1080*4+8:raise ValueError('Readback cap')
    w,h=struct.unpack_from('<2I',raw)
    if not w or not h or w>1920 or h>1080 or len(raw)!=8+w*h*4:raise ValueError('Readback dimensions')
    return np.frombuffer(raw,dtype=np.uint8,offset=8).reshape(h,w,4).copy()


def oracle(scene,index,width,height,shade=False,viewport_mode='captured',pixel_center=0.,return_depth=False):
    """Independent native composed transform,not D3D matrices reconstructed by adapter.

    D3D9 raster samples integer pixel centers;no half-pixel correction is silently
    added to native geometry/projection. Compare interior,excluding edge fill rules.
    """
    model=read_replay(scene/'scene.bin')
    manifest=json.loads((scene/'scene.json').read_text())
    composed=np.array(manifest['frames'][index]['native_composed'],dtype=float)
    all_vertices=np.asarray(model['vertices'],dtype=float);points=all_vertices[:,:3]
    clip=np.c_[points,np.ones(len(points))]@composed.T
    if np.any(clip[:,3]<=0):raise ValueError('Near/behind-camera oracle case unqualified')
    projected=clip[:,:3]/clip[:,3,None]
    if viewport_mode=='captured':
        projected[:,0]*=width/1920;projected[:,1]*=height/1080
    elif viewport_mode=='full_frustum':
        x,y,w,h=manifest['frames'][index]['viewport']
        projected[:,0]=(projected[:,0]-x)*width/w;projected[:,1]=(projected[:,1]-y)*height/h
    else:raise ValueError('Unqualified oracle viewport convention')
    z=np.full((height,width),np.inf)
    color=np.zeros((height,width,3),dtype=np.uint8);reliable=np.zeros((height,width),dtype=bool)
    textures={}
    if shade:
        for _,material,_,_ in model['groups']:
            if material not in textures:
                b=(scene/f'texture-{material}.bin').read_bytes();_,tw,th,size=struct.unpack_from('<4I',b)
                if size!=tw*th*4 or len(b)!=16+size:raise ValueError('Oracle texture size')
                textures[material]=np.frombuffer(b,dtype=np.uint8,offset=16).reshape(th,tw,4)
    material_by_tri=[]
    for _,material,_,count in model['groups']:material_by_tri.extend([material]*(count//3))
    for ti,tri in enumerate(projected[np.array(model['indices'])].reshape(-1,3,3)):
        xmin=max(0,int(np.floor(tri[:,0].min())));xmax=min(width-1,int(np.ceil(tri[:,0].max())))
        ymin=max(0,int(np.floor(tri[:,1].min())));ymax=min(height-1,int(np.ceil(tri[:,1].max())))
        if xmax<xmin or ymax<ymin:continue
        a,b,c=tri;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-10:continue
        if pixel_center not in (0.,.5):raise ValueError('Unqualified raster sample center')
        yy,xx=np.mgrid[ymin:ymax+1,xmin:xmax+1];xx=xx+pixel_center;yy=yy+pixel_center
        wa=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
        wb=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;wc=1-wa-wb
        depth=wa*a[2]+wb*b[2]+wc*c[2]
        inside=(wa>=0)&(wb>=0)&(wc>=0)&(depth>=0)&(depth<=1)
        region=z[ymin:ymax+1,xmin:xmax+1];wins=inside&(depth<=region)
        if shade:
            ids=model['indices'][ti*3:ti*3+3];reciprocal=1/clip[ids,3]
            uv=all_vertices[ids,6:8]
            weighted=wa*reciprocal[0]+wb*reciprocal[1]+wc*reciprocal[2]
            u=(wa*reciprocal[0]*uv[0,0]+wb*reciprocal[1]*uv[1,0]+wc*reciprocal[2]*uv[2,0])/weighted
            v=(wa*reciprocal[0]*uv[0,1]+wb*reciprocal[1]*uv[1,1]+wc*reciprocal[2]*uv[2,1])/weighted
            tex=textures[material_by_tri[ti]];th,tw,_=tex.shape
            uf=(u%1)*tw;vf=(v%1)*th
            values=tex[np.floor(vf).astype(int)%th,np.floor(uf).astype(int)%tw,:3]
            region_color=color[ymin:ymax+1,xmin:xmax+1];region_color[wins]=values[wins]
            # Exclude triangle/texel boundaries susceptible to raster precision.
            reliable_region=reliable[ymin:ymax+1,xmin:xmax+1]
            safe=(wa>.01)&(wb>.01)&(wc>.01)&(np.abs(uf-np.round(uf))>.02)&(np.abs(vf-np.round(vf))>.02)
            reliable_region[wins]=safe[wins]
        region[wins]=depth[wins]
    if return_depth:return z
    return (np.isfinite(z),color,reliable) if shade else np.isfinite(z)


def neighborhood(mask,radius):
    h,w=mask.shape;padded=np.pad(mask,radius);out=np.zeros_like(mask)
    for y in range(2*radius+1):
        for x in range(2*radius+1):out|=padded[y:y+h,x:x+w]
    return out


def compare(folder):
    manifest=json.loads((folder/'scene.json').read_text());results=[]
    for index,_ in enumerate(manifest['frames']):
        rgba=pixels(folder/f'color-{index}.bgra');mask=pixels(folder/f'mask-{index}.bgra')
        observed=mask[:,:,:3].max(axis=2)>0
        expected,expected_color,reliable=oracle(folder,index,mask.shape[1],mask.shape[0],shade=True)
        union=(observed|expected).sum();intersection=(observed&expected).sum()
        outside=int((observed&~neighborhood(expected,1)).sum());missing=int((expected&~neighborhood(observed,1)).sum())
        iou=float(intersection/max(1,union))
        if not expected.any() or iou<.95 or outside or missing:raise ValueError(f'D3D9 projection mismatch frame{index}:iou={iou},outside={outside},missing={missing}')
        colors=len(np.unique(rgba[observed,:3],axis=0))
        if colors<(4 if manifest.get('synthetic') else 16):raise ValueError('Textured image has insufficient color variation')
        reliable&=observed
        samples=int(reliable.sum());exact=float(np.all(rgba[:,:,:3][reliable]==expected_color[reliable],axis=1).mean()) if samples else 0
        # Tiny historical silhouettes are placement evidence,not sufficient
        # samples for a per-frame texture claim. Require a useful frame per asset.
        if samples>=64 and exact<.98:raise ValueError(f'Primary texture/UV mismatch frame{index}:samples={samples},exact={exact}')
        Image.fromarray(rgba[:,:,[2,1,0,3]],'RGBA').save(folder/f'color-{index}.png')
        results.append(dict(frame=index,pixels=int(observed.sum()),iou=iou,unexpected_beyond1px=outside,
            missing_beyond1px=missing,colors=colors,texture_interior_samples=samples,texture_exact_fraction=exact,
            texture_qualified=samples>=64 and exact>=.98,
            color_sha256=digest(folder/f'color-{index}.bgra')))
    if not any(r['texture_qualified'] for r in results):raise ValueError('No sufficiently sampled texture frame for asset')
    resized=pixels(folder/'mask-resized.bgra');actual=resized[:,:,:3].max(axis=2)>0
    expected=oracle(folder,0,resized.shape[1],resized.shape[0])
    if np.any(actual&~neighborhood(expected,1)) or np.any(expected&~neighborhood(actual,1)):raise ValueError('Resize projection mismatch')
    return results


def storage():
    return sum(p.stat().st_size for sub in ('remix-runtime/runs','remix-runtime/archives','d3d9-proof','d3d9-intercept/runs','d3d9-intercept/reference','d3d9-intercept/capabilities','d3d9-intercept/direct64-runs')
               for p in (ROOT/'artifacts'/sub).rglob('*') if p.is_file())


def run_native(case):
    with (case/'native.log').open('wb') as log:
        test=sp.run([str(EXE),str(case)],cwd=case,stdout=log,stderr=sp.STDOUT,timeout=45,
            creationflags=sp.CREATE_NO_WINDOW)
    if (case/'native.log').stat().st_size>2*1024*1024:raise ValueError('Native log cap')
    if test.returncode==0:
        log=(case/'native.log').read_text()
        if 'MODULE_AUDIT_PASS' not in log or 'pe=x86' not in log:raise ValueError('Plain system runtime/architecture proof missing')
    return test.returncode


def negative_cases(folder):
    from synthetic import prepare as fixture
    failures=[]
    for name in ('truncated','nonfinite','bad-index','bad-group','bad-frame','missing-texture'):
        case=fixture(folder/name);path=case/'scene.bin';raw=bytearray(path.read_bytes())
        if name=='truncated':raw=raw[:-1]
        if name=='nonfinite':struct.pack_into('<f',raw,32,float('nan'))
        if name=='bad-index':struct.pack_into('<I',raw,32+6*32,6)
        if name=='bad-group':struct.pack_into('<I',raw,32+6*32+6*4+8,1)
        if name=='bad-frame':struct.pack_into('<I',raw,32+6*32+6*4+2*16,0)
        if name=='missing-texture':(case/'texture-0.bin').rename(case/'texture-0.unavailable')
        path.write_bytes(raw)
        code=run_native(case)
        if code!=1 or 'D3D9_PROOF_FAIL' not in (case/'native.log').read_text():raise ValueError('Native negative case not safely rejected:'+name)
        failures.append(dict(case=name,exit=code))
    return failures


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');args=parser.parse_args()
    if not args.execute:print('Offline D3D9 proof prepared;--execute required;no SFC/Remix launch');return
    if storage()+128*1024*1024>AGGREGATE_BYTES:raise ValueError('20GB aggregate evidence cap lacks128MiB reservation')
    folder=ROOT/'artifacts/d3d9-proof/runs'/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
    folder.mkdir(parents=True);start=time.monotonic()
    capture_files=[p for p in CAPTURE.glob('LIVE-SCENE-001-*') if p.is_file()]
    capture_files += [CAPTURE/'run-metadata.json',CAPTURE/'run-result.json']
    inputs={str(p.relative_to(ROOT)):digest(p) for p in capture_files}
    result=dict(result='PARTIAL',sfc_launched=False,remix_loaded=False,exe_sha256=digest(EXE),inputs=inputs,cases=[])
    result['sources']={name:digest(ROOT/name) for name in SOURCES}
    result['system_d3d9_x86_sha256']=digest(Path(os.environ['SystemRoot'])/'SysWOW64/d3d9.dll')
    try:
        from startup import probe
        result['startup']=probe(folder/'startup')
        if result['startup']['status'].startswith('BLOCKED_'):
            result['result']=result['startup']['status']
            raise ValueError('Native startup prerequisite: '+result['startup']['status']+';see startup/startup.log')
        from synthetic import prepare as fixture
        synthetic=fixture(folder/'synthetic')
        if run_native(synthetic):raise ValueError('Known matrix/UV native fixture failed')
        result['known_transform_uv_tests']=compare(synthetic)
        result['native_rejections']=negative_cases(folder)
        for revision in (4,3):
            case=folder/f'asset-{revision}'
            manifest=prepare(CAPTURE/f'LIVE-SCENE-001-asset-{revision}.bin',case,GAME)
            read_replay(case/'scene.bin')
            code=run_native(case)
            if code:raise ValueError(f'D3D9 native case{revision} failed:{code};see native.log')
            comparisons=compare(case)
            result['cases'].append(dict(model=manifest['model_name'],geometry_sha256=manifest['geometry_sha256'],
                replay_sha256=manifest['replay_sha256'],folder=str(case.relative_to(ROOT)),frames=comparisons))
            if time.monotonic()-start>180:raise ValueError('Offline prepared workflow180s limit')
        if len({c['geometry_sha256'] for c in result['cases']})!=2:raise ValueError('Two distinct assets required')
        if any(digest(ROOT/p)!=h for p,h in inputs.items()):raise ValueError('Original capture changed')
        result['result']='OFFLINE_PLAIN_D3D9_TWO_ASSET_PASS'
    except Exception as exc:
        result['error']=str(exc)
        raise
    finally:
        result['seconds']=time.monotonic()-start
        result['output_bytes']=sum(p.stat().st_size for p in folder.rglob('*') if p.is_file())
        if result['output_bytes']>128*1024*1024:result['result']='PARTIAL_OUTPUT_CAP_EXCEEDED'
        (folder/'result.json').write_text(json.dumps(result,indent=2))
        print('Evidence:',folder)
    print(result['result'])
    if result['result']!='OFFLINE_PLAIN_D3D9_TWO_ASSET_PASS':raise ValueError('Offline proof output cap exceeded')


if __name__=='__main__':main()
