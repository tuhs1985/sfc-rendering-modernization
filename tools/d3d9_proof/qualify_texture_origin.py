"""Small asymmetric ordinary-D3D9/Remix material control;never starts SFC."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess as sp
import numpy as np
from PIL import Image
from run_offline import ROOT,storage,AGGREGATE_BYTES
from synthetic import prepare
from run_direct64 import limit_to_first
from material_binding import HASHER,shader,encode_generated_dds,encode_remix_material_dds


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');args=parser.parse_args()
    if not args.execute:print('Explicit --execute required;synthetic UV control only,no SFC');return
    if storage()+64*1024*1024>AGGREGATE_BYTES:raise ValueError('64MiB reservation required')
    folder=ROOT/'artifacts/d3d9-proof/material-runs'/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f');folder.mkdir()
    report=dict(result='PARTIAL',sfc_launched=False,synthetic=True,cases=[])
    runtime=ROOT/'artifacts/d3d9-intercept/deps/remix-1.5.2/.trex/d3d9.dll'
    if hashlib.sha256(runtime.read_bytes()).hexdigest().upper()!='F7C310821AA98BCDFDEC120330B0A89457B7C5EBA58D21464AF32639611C809F':raise ValueError('Pinned runtime changed')
    try:
        for name,encoder in [('off',encode_generated_dds),('baseline',encode_remix_material_dds)]:
            case=folder/name;prepare(case);manifest=json.loads((case/'scene.json').read_text());limit_to_first(case,manifest)
            image=Image.new('RGBA',(2,2));image.putdata([(255,0,0,255),(0,255,0,255),(0,0,255,255),(255,255,0,255)])
            # Large constant quadrants avoid2x2bilinear+wrap mixing at samples.
            image=image.resize((64,64),Image.Resampling.NEAREST)
            rgba=np.asarray(image);bgra=rgba[:,:,[2,1,0,3]].tobytes()
            for i in range(2):
                data=bytearray(bgra);data[3]=255-i
                (case/f'texture-{i}.bin').write_bytes(struct.pack('<4I',0x31544653,64,64,len(data))+data)
            hashes=sp.check_output([str(HASHER),'--batch',str(case),'2'],text=True,timeout=5).splitlines()
            output=case/'rtx-remix/mods/sfc-policy';(output/'textures').mkdir(parents=True)
            data=encoder(image);digest=hashlib.sha256(data).hexdigest();path='textures/'+digest+'.dds';(output/path).write_bytes(data)
            blocks=''.join(shader(h.upper().zfill(16),dict(color=path,emission=path),[1,1,0,0,0,1,0,1,0,1]) for h in hashes)
            (output/'mod.usda').write_text('#usda 1.0\n(defaultPrim = "RootNode")\ndef Xform "RootNode"\n{\n def Scope "Looks"\n {\n'+blocks+' }\n}\n')
            (case/'rtx.conf').write_text('rtx.enableReplacementAssets = True\nrtx.enableReplacementMaterials = True\nrtx.enableReplacementMeshes = False\nrtx.enableRaytracing = True\nrtx.graphicsPreset = 4\nrtx.integrateIndirectMode = 0\nrtx.upscalerType = 0\nrtx.enableRayReconstruction = False\nrtx.resolutionScale = 1.0\n')
            env={**os.environ,'DXVK_CONFIG_FILE':str(case/'rtx.conf'),'RTX_AUTOMATION_DISABLE_BLOCKING_DIALOG_BOXES':'1','RTX_CAPTURE_REMIX_CONFIGS':'0','DXVK_ENABLE_RAYTRACING':'1'}
            for key in tuple(env):
                if key.startswith('SFC_') or key in ('DXVK_RTX_CAPTURE_ENABLE_ON_FRAME','DXVK_DUMP_SCREENSHOT_FRAME','DXVK_TERMINATE_APP_FRAME'):env.pop(key,None)
            command=[str(ROOT/'artifacts/remix-ingest/bin/bounded_job.exe'),str(case),'30',str(24*1024*1024),str(2*1024*1024),str(ROOT/'artifacts/d3d9-proof/direct64-bin/d3d9_direct_host.exe'),str(case),str(runtime)]
            sp.run(command,env=env,check=True,timeout=40,creationflags=sp.CREATE_NO_WINDOW)
            job=json.loads((case/'job-result.json').read_text())
            if job['exit_code'] or job['stop_reason'] or job['remaining_owned_processes']:raise ValueError('UV control cleanup')
            raw=(case/'returned-0-0.raw32').read_bytes()
            if raw[:8]!=struct.pack('<2I',960,540) or len(raw)!=8+960*540*4:raise ValueError('UV control shape')
            rgb=np.frombuffer(raw,dtype=np.uint8,offset=8).reshape(540,960,4)[:,:,[2,1,0]]
            labels=[];samples=[]
            colors=np.array([[255,0,0],[0,255,0],[0,0,255],[255,255,0]],dtype=float)
            for x,y in ((450,250),(510,250),(450,290),(510,290)):
                color=np.median(rgb[y-2:y+3,x-2:x+3].reshape(-1,3),axis=0);samples.append(color.tolist())
                scaled=color/max(1,float(color.max()))
                labels.append(int(np.argmin(np.linalg.norm(colors/255-scaled,axis=1))))
            Image.fromarray(rgb).save(case/'quadrants.png')
            report['cases'].append(dict(name=name,labels=labels,rgb=samples,dds_sha256=digest,job=job))
        if report['cases'][0]['labels']!=[0,1,2,3] or report['cases'][1]['labels']!=[2,3,0,1]:raise ValueError('Actual Remix replacement origin not demonstrated')
        report['result']='REMIX_REPLACEMENT_DDS_ORIGIN_QUALIFIED'
    finally:
        (folder/'result.json').write_text(json.dumps(report,indent=2));print('UV control:',folder)
    print(report['result'])


if __name__=='__main__':main()
