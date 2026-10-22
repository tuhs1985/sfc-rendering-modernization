"""Bounded normal x86 Remix interception of the proven offline D3D9 replay."""
from pathlib import Path
import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess as sp
import sys
import time
import zipfile
from run_offline import ROOT,CAPTURE,GAME,storage,digest,AGGREGATE_BYTES
from scene_bundle import prepare

BASE=ROOT/'artifacts/d3d9-intercept'
RUNTIME=BASE/'deps/remix-1.5.2'
ARCHIVE=ROOT/'artifacts/remix-runtime/deps/remix-1.5.2-release.zip'
ARCHIVE_SHA='cc424be4dd1a0c6fd922bc6a7f8e5f6582baea7043a38afa6686d8b6faabad01'
EXE=ROOT/'artifacts/d3d9-proof/intercept-bin/d3d9_intercept.exe'
GUARD=ROOT/'artifacts/remix-ingest/bin/bounded_job.exe'


def freeze_runtime():
    if digest(ARCHIVE)!=ARCHIVE_SHA:raise ValueError('Pinned release ZIP mismatch')
    records={}
    with zipfile.ZipFile(ARCHIVE) as z:
        for row in z.infolist():
            name=Path(row.filename)
            if name.is_absolute() or '..' in name.parts:raise ValueError('Unsafe release entry')
            if row.is_dir():continue
            raw=z.read(row);path=RUNTIME/name
            path.parent.mkdir(parents=True,exist_ok=True)
            if path.is_symlink():raise ValueError('Runtime reparse target')
            if path.exists():
                if digest(path)!=hashlib.sha256(raw).hexdigest():raise ValueError('Private pinned input changed:'+row.filename)
            else:path.write_bytes(raw)
            records[row.filename]=dict(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
    (BASE/'deps/manifest.json').write_text(json.dumps(dict(release='remix-1.5.2',archive_sha256=ARCHIVE_SHA,files=records),indent=2))
    return records


def generated_bytes(records):
    return sum(p.stat().st_size for p in RUNTIME.rglob('*') if p.is_file() and p.relative_to(RUNTIME).as_posix() not in records)


def config(case):
    # Process-local test controls,NOT sponsor's appearance baseline.
    (case/'rtx.conf').write_text('''rtx.captureInstances = True
rtx.enableReplacementAssets = False
rtx.captureEnableMultiframe = False
rtx.captureInstanceStageName = proof.usda
rtx.captureShowMenuOnHotkey = False
rtx.graphicsPreset = 4
rtx.integrateIndirectMode = 0
rtx.dlssPreset = 0
rtx.enableRayReconstruction = False
rtx.upscalerType = 0
rtx.resolutionScale = 1.0
''')
    # The shipped client's own startup log confirms this .trex search location.
    # Keep settings private to this frozen test dependency,never installed SFC.
    (RUNTIME/'.trex/bridge.conf').write_text('''client.enableDpiAwareness = False
client.enableBackbufferCapture = False
logLevel = Info
logAllCalls = False
logAllCommands = False
''')


def run(case,records,capture_frame):
    config(case)
    env={**os.environ,'DXVK_LOG_LEVEL':'info','DXVK_CONFIG_FILE':str(case/'rtx.conf'),
        'DXVK_RTX_CAPTURE_ENABLE_ON_FRAME':str(capture_frame),'DXVK_DUMP_SCREENSHOT_FRAME':str(capture_frame+8),
        'DXVK_GRAPHICS_PRESET_TYPE':'4','RTX_INTEGRATE_INDIRECT_MODE':'0','DXVK_DLSS_PRESET':'0',
        'RTX_AUTOMATION_DISABLE_BLOCKING_DIALOG_BOXES':'1','RTX_CAPTURE_REMIX_CONFIGS':'0'}
    for key in ('DXVK_TERMINATE_APP_FRAME','DXVK_CAPTURE_FLATTEN','SFC_REMIX_SCENE_DEPTH'):
        env.pop(key,None)
    command=[str(GUARD),str(case),'90',str(128*1024*1024),str(2*1024*1024),str(EXE),str(case),str(RUNTIME/'d3d9.dll')]
    process=sp.Popen(command,env=env,creationflags=sp.CREATE_NO_WINDOW)
    began=time.monotonic()
    try:
        while process.poll() is None:
            # Pin shipped binaries as input;count ONLY extra generated runtime
            # log/cache/config bytes in addition to all evidence directories.
            outputs=generated_bytes(records)
            logs=sum(p.stat().st_size for p in RUNTIME.rglob('*.log'))
            if logs>32*1024*1024 or outputs>64*1024*1024:raise ValueError('Bridge dependency-folder generated-output cap')
            if time.monotonic()-began>100:raise ValueError('Owned bridge workflow timeout')
            time.sleep(.1)
    finally:
        if process.poll() is None:
            process.terminate();process.wait(timeout=10) # Guard owns kill-on-close job.
    job=json.loads((case/'job-result.json').read_text())
    for path in RUNTIME.rglob('*.log'):
        if path.stat().st_size>32*1024*1024:raise ValueError('Bridge log cap')
        name='runtime-'+path.relative_to(RUNTIME).as_posix().replace('/','_')
        shutil.copyfile(path,case/name)
    if process.returncode or job['exit_code'] or job['stop_reason'] or job['remaining_owned_processes']:
        raise ValueError('Normal D3D9 bridge client/server job needs review:'+json.dumps(job))
    return job


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');parser.add_argument('--asset',type=int,choices=(3,4),default=4)
    parser.add_argument('--capture-frame',type=int,choices=(12,96),default=12);args=parser.parse_args()
    if not args.execute:print('Prepared normal interception;--execute required;SFC never launched');return
    if storage()+128*1024*1024>AGGREGATE_BYTES:raise ValueError('20GB output allowance lacks128MiB reservation')
    records=freeze_runtime()
    folder=BASE/'runs'/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
    prepare(CAPTURE/f'LIVE-SCENE-001-asset-{args.asset}.bin',folder,GAME)
    result=dict(result='PARTIAL',sfc_launched=False,sdk_registration=False,release='remix-1.5.2',
        release_zip_sha256=ARCHIVE_SHA,exe_sha256=digest(EXE),guard_sha256=digest(GUARD),
        replay_sha256=digest(folder/'scene.bin'),runtime_inputs=records)
    result['sources']={name:digest(ROOT/name) for name in (
        'tools/d3d9_proof/d3d9_replay.cpp','tools/d3d9_proof/build_intercept.ps1',
        'tools/d3d9_proof/run_intercept.py','tools/scene_bridge/scene_bundle.py')}
    try:
        result['capture_frame']=args.capture_frame
        result['job']=run(folder,records,args.capture_frame)
        # Startup/Present alone is NOT capture qualification. Analyze the emitted
        # USD/meshes/materials and compare with original packet in a separate step.
        result['result']='CLIENT_SERVER_EXITED_CAPTURE_REVIEW_REQUIRED'
        result['captures']=[str(p.relative_to(folder)) for p in folder.rglob('*.usd*')]
        if any(digest(RUNTIME/n)!=row['sha256'] for n,row in records.items()):raise ValueError('Pinned private runtime input modified')
    except Exception as exc:result['error']=str(exc);raise
    finally:
        (folder/'result.json').write_text(json.dumps(result,indent=2));print('Evidence:',folder,flush=True)
    print(result['result'])


if __name__=='__main__':main()
