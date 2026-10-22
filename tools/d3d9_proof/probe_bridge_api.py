"""Bounded shipped-binary capability check;no SFC launch or SDK mesh calls."""
import argparse
import datetime as dt
import json
import os
import re
import subprocess as sp
import time
from run_intercept import BASE,RUNTIME,GUARD,freeze_runtime,config,generated_bytes
from run_offline import ROOT,storage,digest,AGGREGATE_BYTES

EXE=ROOT/'artifacts/d3d9-proof/intercept-bin/remix_bridge_capabilities.exe'


def classify(text):
    if re.findall(r'^INITIALIZE result=(\d+) version=([\d.]+)\s*$',text,re.MULTILINE)!=[('0','0.6.4')]:raise ValueError('Matching interface not initialized')
    rows=re.findall(r'^CAPABILITIES (.+)$',text,re.MULTILINE)
    if len(rows)!=1:raise ValueError('Missing/ambiguous capability record')
    pairs=re.findall(r'(\w+)=(0|1)(?=\s|$)',rows[0]);values=dict((key,int(value)) for key,value in pairs)
    expected={'copy_output','external_swapchain','vk_image','set_default_output','request_picking','setup_camera','create_mesh','present'}
    if set(values)!=expected or len(pairs)!=len(expected):raise ValueError('Incomplete/duplicate capability table')
    if 'PROBE_DONE device_refs=0 api_refs=0 sdk_mesh_calls=0' not in text:raise ValueError('Probe lifecycle incomplete')
    available=bool(values['copy_output'] or values['external_swapchain'])
    return dict(status='OUTPUT_ENTRYPOINT_PRESENT_NOT_TRANSFER_QUALIFIED' if available else 'BLOCKED_NORMAL_BRIDGE_OUTPUT_ENTRYPOINTS_ABSENT',
        functions=values,sdk_mesh_calls=0)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');args=parser.parse_args()
    if not args.execute:print('Explicit --execute required;no game changes');return
    if storage()+128*1024*1024>AGGREGATE_BYTES:raise ValueError('20GB allowance lacks128MiB reservation')
    records=freeze_runtime();case=BASE/'capabilities'/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f');case.mkdir(parents=True)
    bridge=RUNTIME/'.trex/bridge.conf';prior=bridge.read_bytes() if bridge.exists() else None
    report=dict(status='PARTIAL',sfc_launched=False,sdk_mesh_calls=0,exe_sha256=digest(EXE),header_sha256=digest(ROOT/'artifacts/remix-runtime/deps/remix_c.h'))
    process=None
    try:
        config(case)
        bridge.write_text(bridge.read_text()+'exposeRemixApi = True\n')
        # Preserve the effective private configuration in the case as evidence.
        (case/'bridge.conf').write_bytes(bridge.read_bytes())
        env={**os.environ,'DXVK_CONFIG_FILE':str(case/'rtx.conf'),'RTX_AUTOMATION_DISABLE_BLOCKING_DIALOG_BOXES':'1','RTX_CAPTURE_REMIX_CONFIGS':'0'}
        for key in ('DXVK_RTX_CAPTURE_ENABLE_ON_FRAME','DXVK_DUMP_SCREENSHOT_FRAME','DXVK_TERMINATE_APP_FRAME'):
            env.pop(key,None)
        command=[str(GUARD),str(case),'90',str(128*1024*1024),str(2*1024*1024),str(EXE),str(RUNTIME/'d3d9.dll')]
        process=sp.Popen(command,env=env,creationflags=sp.CREATE_NO_WINDOW);began=time.monotonic()
        while process.poll() is None:
            if generated_bytes(records)>64*1024*1024 or time.monotonic()-began>100:raise ValueError('Capability workflow limit')
            time.sleep(.1)
        job=json.loads((case/'job-result.json').read_text());report['job']=job
        if process.returncode or job['exit_code'] or job['stop_reason'] or job['remaining_owned_processes']:raise ValueError('Capability inspection did not exit normally')
        report.update(classify((case/'job-console.log').read_text()))
        if any(digest(RUNTIME/name)!=record['sha256'] for name,record in records.items()):raise ValueError('Pinned runtime input changed')
        report['sources']={name:digest(ROOT/name) for name in ('tools/d3d9_proof/remix_bridge_capabilities.cpp','tools/d3d9_proof/build_capabilities.ps1','tools/d3d9_proof/probe_bridge_api.py')}
    except Exception as error:report['error']=str(error);raise
    finally:
        if process is not None and process.poll() is None:process.terminate();process.wait(timeout=10)
        if prior is not None:bridge.write_bytes(prior)
        else:bridge.unlink(missing_ok=True)
        (case/'result.json').write_text(json.dumps(report,indent=2));print('Evidence:',case)
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
