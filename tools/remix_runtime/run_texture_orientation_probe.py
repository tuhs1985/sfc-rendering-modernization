"""Offline-only 60s/8MiB asymmetric UV and emission control; never launches SFC."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import os
import subprocess as sp
import time
import numpy as np
from PIL import Image
from run_return_fixture import ROOT,DLL,ENV,digest

def main():
    work=ROOT/'artifacts/remix-runtime/runs'/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f-texture-control')
    work.mkdir();exe=ROOT/'artifacts/remix-runtime/live-return-bin/texture_orientation_probe.exe'
    if digest(DLL)!='F7C310821AA98BCDFDEC120330B0A89457B7C5EBA58D21464AF32639611C809F':raise ValueError('Pinned runtime mismatch')
    if not exe.is_file():raise ValueError('Build standalone texture control first')
    pixels=np.empty((64,64,4),dtype='u1');pixels[:32,:32]=[128,20,20,255];pixels[:32,32:]=[20,128,20,255]
    pixels[32:,:32]=[20,20,128,255];pixels[32:,32:]=[128,128,20,255]
    image=work/'uv-corners.dds';Image.fromarray(pixels).save(image)
    with Image.open(image) as decoded:
        if not np.array_equal(np.asarray(decoded.convert('RGBA')),pixels):raise ValueError('DDS input changed')
    manifest=dict(probe='REMIX-TEXTURE-CONTROL-001',runtime_sha256=digest(DLL),exe_sha256=digest(exe),
                  source_sha256=digest(ROOT/'tools/remix_runtime/texture_orientation_probe.cpp'),
                  image_sha256=digest(image),limits=dict(seconds=60,bytes=8*1024*1024,frames=64,image_readbacks=2),
                  environment=ENV,geometry='identity quad z6;top-left(-2,+2)UV(0,0);camera up+Y right+X forward+Z',
                  texture='top-left red;top-right green;bottom-left blue;bottom-right yellow')
    (work/'manifest.json').write_text(json.dumps(manifest,indent=2))
    start=time.monotonic();result={'result':'PARTIAL'};process=None
    try:
        with (work/'probe.log').open('wb') as log:
            process=sp.Popen([str(exe),str(DLL),str(image)],cwd=work,env={**os.environ,**ENV,'DXVK_LOG_PATH':str(work)},stdout=log,stderr=sp.STDOUT,creationflags=sp.CREATE_NO_WINDOW)
            while process.poll() is None:
                if time.monotonic()-start>60 or sum(p.stat().st_size for p in work.rglob('*') if p.is_file())>8*1024*1024:
                    process.terminate();raise ValueError('Offline control time/output limit')
                time.sleep(.05)
            result['native_exit']=process.returncode
            if process.returncode:raise ValueError(f'Offline SDK control failed with exit {process.returncode}; retain fenced captures as PARTIAL')
        results={}
        for mode in ('off','on'):
            raw=(work/f'emission-{mode}.bgra').read_bytes()
            if len(raw)!=256*256*4:raise ValueError('Readback size')
            rgb=np.frombuffer(raw,dtype='u1').reshape(256,256,4)[:,:,[2,1,0]]
            Image.fromarray(rgb).save(work/f'emission-{mode}.png')
            samples=[np.median(rgb[y-3:y+4,x-3:x+4],axis=(0,1)).tolist() for x,y in ((98,98),(158,98),(98,158),(158,158))]
            results[mode]=dict(samples_tl_tr_bl_br=samples,quad_mean_rgb=rgb[80:176,80:176].mean(axis=(0,1)).tolist(),
                               sha256=hashlib.sha256(raw).hexdigest())
        result=dict(result='OFFLINE_CONTROL_CAPTURED',sfc_launched=False,seconds=time.monotonic()-start,
                    captures=results,note='Read samples against input corner labels;not native SFC image-upload evidence')
    except Exception as e:result['error']=str(e);raise
    finally:
        if process and process.poll() is None:process.terminate();process.wait(timeout=5)
        (work/'result.json').write_text(json.dumps(result,indent=2));print('Evidence: '+str(work))
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
