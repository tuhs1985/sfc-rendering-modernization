"""Standalone synthetic pixel-layout investigation; never launches SFC.

Uses existing pinned candidate host/receiver. The legacy bootstrap toggle is
diagnostic-only here: avoid comparing an uninitialized first output to geometry.
No live configuration or normal startup default is changed.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
for sub in ('tools/d3d9_proof','tools/remix_runtime','tools/scene_bridge'):
    sys.path.insert(0,str(ROOT/sub))
from synthetic import prepare
from run_direct64 import limit_to_first,resize_output
from run_offline import oracle
import numpy as np


def run(width,height):
    # Current binary/parser bounds remain until larger output has an integrated
    # contract. This diagnostic must not silently bless or bypass those limits.
    if not 1<=width<=1920 or not 1<=height<=1080:raise ValueError('Current isolated binary maximum1920x1080')
    folder=ROOT/'artifacts/alpha/extent-investigation'/dt.datetime.now(dt.timezone.utc).strftime(f'%Y%m%d-%H%M%S-%f-{width}x{height}')
    folder.parent.mkdir(parents=True,exist_ok=True);prepare(folder)
    manifest=json.loads((folder/'scene.json').read_text());limit_to_first(folder,manifest);resize_output(folder,(width,height),manifest)
    (folder/'rtx.conf').write_text('rtx.enableReplacementAssets = False\nrtx.enableRaytracing = True\nrtx.graphicsPreset = 4\nrtx.integrateIndirectMode = 0\nrtx.enableRayReconstruction = False\nrtx.upscalerType = 0\nrtx.resolutionScale = 1.0\n')
    host=ROOT/'artifacts/remix-runtime/candidate-1.6.1-bin/d3d9_direct_host.exe'
    runtime=ROOT/'artifacts/remix-runtime/deps/candidate-1.6.1/runtime/d3d9_x64.dll'
    receiver=ROOT/'artifacts/d3d9-proof/receiver-bin/output_receiver.exe'
    env=dict(os.environ,DXVK_CONFIG_FILE=str(folder/'rtx.conf'),RTX_AUTOMATION_DISABLE_BLOCKING_DIALOG_BOXES='1',
             RTX_CAPTURE_REMIX_CONFIGS='0',DXVK_ENABLE_RAYTRACING='1',SFC_DIRECT64_INVESTIGATE_EXTENT='1',
             SFC_DIRECT64_SINGLE_PRESENT='1',SFC_D3D9_LEGACY_STARTUP_WARMUP='1')
    for name in ('SFC_D3D9_PREWARM','SFC_PLAY_SESSION','SFC_D3D9_GAME_OUTPUT','SFC_D3D9_LIVE_TIMING',
                 'SFC_PIPELINE_MODE','SFC_NATIVE_GATE','DXVK_RTX_CAPTURE_ENABLE_ON_FRAME','DXVK_DUMP_SCREENSHOT_FRAME'):
        env.pop(name,None)
    command=[str(ROOT/'artifacts/remix-ingest/bin/bounded_job.exe'),str(folder),'90',str(128*1024*1024),str(2*1024*1024),
             str(host),str(folder),str(runtime),str(receiver),'normal']
    outcome=subprocess.run(command,env=env,timeout=105,creationflags=subprocess.CREATE_NO_WINDOW)
    record=dict(result='PARTIAL',sfc_launched=False,runtime='1.6.1',extent=[width,height],
                diagnostic_bootstrap_presents=24,normal_startup_changed=False,
                host_sha256=digest(host),runtime_sha256=digest(runtime),receiver_sha256=digest(receiver),
                process_exit=outcome.returncode,job=json.loads((folder/'job-result.json').read_text()))
    if all((folder/f'returned-0-{i}.raw32').exists() for i in range(3)):
        record['planes']=[dict(plane=i,sha256=digest(folder/f'returned-0-{i}.raw32'),
                               receiver_equal=digest(folder/f'returned-0-{i}.raw32')==digest(folder/f'receiver-0-{i}.raw32')) for i in range(3)]
        raw=(folder/'returned-0-1.raw32').read_bytes()
        if struct.unpack_from('<2I',raw)!=(width,height) or len(raw)!=8+width*height*4:raise ValueError('Returned depth shape')
        z=np.frombuffer(raw,offset=8,dtype='<f4').reshape(height,width);actual=np.isfinite(z)&(z>=0)&(z<=1)
        expected=oracle(folder,0,width,height,viewport_mode='full_frustum')
        record['coverage']=dict(iou=float((actual&expected).sum()/max(1,(actual|expected).sum())),actual=int(actual.sum()),expected=int(expected.sum()))
        if not outcome.returncode and all(x['receiver_equal'] for x in record['planes']) and record['coverage']['iou']>.99:
            record['result']='SYNTHETIC_LAYOUT_SUBPROOF_ONLY'
    (folder/'analysis.json').write_text(json.dumps(record,indent=2))
    print(folder);print(json.dumps(record,indent=2))
    return 0 if record['result']=='SYNTHETIC_LAYOUT_SUBPROOF_ONLY' else 1


def digest(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--extent',type=int,nargs=2,required=True)
    args=parser.parse_args();sys.exit(run(*args.extent))
