"""Bounded ordinary-D3D9 material A/B,without SFC or SDK mesh submission."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess as sp
import sys
import numpy as np
from run_offline import ROOT,GAME,storage,AGGREGATE_BYTES
from scene_bundle import prepare
from run_direct64 import limit_to_first,resize_output
from material_binding import prepare as materials

SOURCE=ROOT/'artifacts/remix-runtime/runs/20261020-210035-445207-in-game/gpu/scene.json'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');args=parser.parse_args()
    if not args.execute:print('Explicit --execute required;offline only');return
    if storage()+64*1024*1024>AGGREGATE_BYTES:raise ValueError('Material fixture64MiB reservation within20GB required')
    folder=ROOT/'artifacts/d3d9-proof/material-runs'/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
    folder.mkdir(parents=True);source=json.loads(SOURCE.read_text());report=dict(result='PARTIAL',sfc_launched=False,cases=[])
    runtime=ROOT/'artifacts/d3d9-intercept/deps/remix-1.5.2/.trex/d3d9.dll'
    if hashlib.sha256(runtime.read_bytes()).hexdigest().upper()!='F7C310821AA98BCDFDEC120330B0A89457B7C5EBA58D21464AF32639611C809F':
        raise ValueError('Pinned runtime changed')
    # Explicit,isolated A/B changes only emission;baseline config remains untouched.
    config=(ROOT/'tools/remix_runtime/config/materials.toml').read_bytes()
    off=config.replace(b'illumination_strength = 5.0',b'illumination_strength = 0.0')
    if off==config:raise ValueError('Fixture requires explicit current illumination5 baseline;do not guess TOML edit')
    try:
        for name,raw in [('off',off),('baseline',config),('tuned',config),('lit',config)]:
            case=folder/name
            # Select a useful already-captured view,not the tiny startup row.
            # This offline material test does not alter or fit a camera.
            scene=prepare(ROOT/source['source_packet'],case,GAME)
            scene['fresh_preparation_row']=source['fresh_preparation_row']
            limit_to_first(case,scene);resize_output(case,(960,540),scene)
            binding=materials(case,GAME,raw)
            # No geometry replacement/no Toolkit:only native material replacement.
            config_text='''rtx.enableReplacementAssets = True
rtx.enableReplacementMaterials = True
rtx.enableReplacementMeshes = False
rtx.enableRaytracing = True
rtx.captureInstances = True
rtx.graphicsPreset = 4
rtx.integrateIndirectMode = 0
rtx.enableRayReconstruction = False
rtx.dlssPreset = 0
rtx.upscalerType = 0
rtx.resolutionScale = 1.0
'''
            (case/'rtx.conf').write_text(config_text)
            if name in ('tuned','lit'):
                from image_controls import encode as image_encode
                from quality_controls import encode as quality_encode
                for kind,encoder in [('image',image_encode),('quality',quality_encode)]:
                    raw_controls=(ROOT/f'tools/remix_runtime/config/{kind}.toml').read_bytes()
                    (case/f'{kind}-controls.bin').write_bytes(encoder(raw_controls))
                    (case/f'{kind}-config-accepted.toml').write_bytes(raw_controls)
            env={**os.environ,'DXVK_CONFIG_FILE':str(case/'rtx.conf'),'RTX_AUTOMATION_DISABLE_BLOCKING_DIALOG_BOXES':'1',
                 'RTX_CAPTURE_REMIX_CONFIGS':'0','DXVK_ENABLE_RAYTRACING':'1','DXVK_GRAPHICS_PRESET_TYPE':'4',
                 'RTX_INTEGRATE_INDIRECT_MODE':'0','DXVK_DLSS_PRESET':'0'}
            for key in ('SFC_D3D9_LIVE_TIMING','SFC_DIRECT64_PACED_FRAMES','SFC_DIRECT64_TIMING_ONLY','SFC_DIRECT64_LATEST_INPUT','SFC_DIRECT64_SINGLE_PRESENT','SFC_DIRECT64_INJECT_LAG_MS','DXVK_RTX_CAPTURE_ENABLE_ON_FRAME','DXVK_DUMP_SCREENSHOT_FRAME','DXVK_TERMINATE_APP_FRAME'):
                env.pop(key,None)
            env['SFC_D3D9_VISUAL_SETTINGS']='1' if name in ('tuned','lit') else '0'
            env['SFC_D3D9_LIGHT_SETTINGS']='1' if name=='lit' else '0'
            command=[str(ROOT/'artifacts/remix-ingest/bin/bounded_job.exe'),str(case),'40',str(32*1024*1024),str(2*1024*1024),str(ROOT/'artifacts/d3d9-proof/direct64-bin/d3d9_direct_host.exe'),str(case),str(runtime)]
            replay=None
            try:
                if name=='lit':
                    from light_fixture import Replay
                    replay=Replay(case,scene)
                sp.run(command,env=env,check=True,timeout=50,creationflags=sp.CREATE_NO_WINDOW)
            finally:
                if replay:replay.close()
            job=json.loads((case/'job-result.json').read_text());log=(case/'job-console.log').read_text()
            if job['exit_code'] or job['stop_reason'] or job['remaining_owned_processes'] or 'sdk_mesh_calls=0' not in log or 'OUTPUT_API_SHUTDOWN 0' not in log:
                raise ValueError('Native material fixture/cleanup failed')
            report['cases'].append(dict(name=name,job=job,binding=binding))
        def image(case,index,dtype):
            b=(folder/case/f'returned-0-{index}.raw32').read_bytes()
            if b[:8]!=__import__('struct').pack('<2I',960,540) or len(b)!=8+960*540*4:raise ValueError('Returned image shape')
            return np.frombuffer(b[8:],dtype=dtype)
        before=image('off',0,np.uint8).reshape(-1,4);after=image('baseline',0,np.uint8).reshape(-1,4)
        depth=image('baseline',1,np.float32);mask=np.isfinite(depth)&(depth>=0)&(depth<=1)
        delta=np.abs(after[:,:3].astype(np.int16)-before[:,:3].astype(np.int16)).mean(axis=1)
        report.update(covered_pixels=int(mask.sum()),changed_pixels=int(((delta>2)&mask).sum()),mean_covered_difference=float(delta[mask].mean()) if mask.any() else 0)
        if report['changed_pixels']<8 or report['mean_covered_difference']<2:raise ValueError('No proven material effect on actual returned ship pixels')
        tuned=image('tuned',0,np.uint8).reshape(-1,4)
        report['visual_controls_changed_pixels']=int(((np.abs(tuned[:,:3].astype(np.int16)-after[:,:3].astype(np.int16)).mean(axis=1)>2)&mask).sum())
        if report['visual_controls_changed_pixels']<8:raise ValueError('No proven image/quality effect on actual returned ship pixels')
        lit=image('lit',0,np.uint8).reshape(-1,4)
        report['lights_changed_pixels']=int(((np.abs(lit[:,:3].astype(np.int16)-tuned[:,:3].astype(np.int16)).mean(axis=1)>2)&mask).sum())
        if report['lights_changed_pixels']<8:raise ValueError('No proven light effect on actual returned ship pixels')
        report['result']='NORMAL_D3D9_MATERIAL_BINDING_OBSERVED'
    finally:
        (folder/'result.json').write_text(json.dumps(report,indent=2));print('Material evidence:',folder,flush=True)
    print(report['result'],report['covered_pixels'],report['changed_pixels'])


if __name__=='__main__':main()
