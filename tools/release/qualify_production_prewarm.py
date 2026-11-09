"""Standalone installed-host GPU startup/receiver check. Never launches SFC.

Development qualification only, intentionally outside runtime_modules.json.
Uses a previously captured scene and real installed runtime/receiver, with a
synthetic target notice and activation ticket. This is not gameplay acceptance.
"""
import argparse
import ctypes as C
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess as sp
import sys
import time

sys.dont_write_bytecode=True # Qualification must not alter installed code trees.


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package',type=Path,required=True)
    parser.add_argument('--host',type=Path,required=True)
    parser.add_argument('--scene',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--profile',choices=('0','1'),default='0')
    parser.add_argument('--cancel',action='store_true')
    parser.add_argument('--expect-not-ready',action='store_true')
    args=parser.parse_args()
    package=args.package.resolve();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    os.environ['SFC_RELEASE_ROOT']=str(package)
    for name in ('release','remix_runtime','d3d9_proof','scene_bridge','remix_ingest'):
        sys.path.insert(0,str(package/'code/tools'/name))
    from runtime_context import CONTEXT
    from release_manifest import load,verified_role
    from present_calibration import Receiver
    from async_material_checkout import configure_child,backend_inputs
    # Test producer for the version1 native-target contract (output_target.h).
    NOTICE=struct.Struct('<8IQ4IQ');OFFSET=4352
    from owner_rebind import fnv
    from warm_start import initialize,ready,activate,cancel,snapshot
    manifest=load(package)
    for source in args.scene.iterdir():
        if source.is_file() and (source.name in ('scene.bin','rtx.conf','image-controls.bin','quality-controls.bin') or
                source.name.startswith('texture-') and source.suffix=='.bin'):
            shutil.copyfile(source,out/source.name)
    # Private empty mod preserves the initial prewarm configuration. No saved
    # model/template, generated enhancements or game binary is added here.
    policy=out/'rtx-remix/mods/sfc-policy';policy.mkdir(parents=True)
    (policy/'mod.usda').write_text('#usda 1.0\n(defaultPrim = "RootNode")\ndef Xform "RootNode" {}\n')
    header=struct.unpack_from('<8I',(out/'scene.bin').read_bytes())
    width,height=header[6:8]
    receiver=Receiver();process=None
    report=dict(game_started=False,scope='Standalone real GPU startup/output;synthetic ticket and target',profile=args.profile)
    try:
        initialize(receiver.channel,os.getpid())
        words=[int(receiver.name[-32:][i:i+8],16) for i in range(0,32,8)]
        qpc=C.c_int64();C.WinDLL('kernel32').QueryPerformanceCounter(C.byref(qpc))
        raw=NOTICE.pack(0x31544754,1,64,os.getpid(),*words,qpc.value,width,height,1,1,0)
        raw=raw[:-8]+struct.pack('<Q',fnv(raw[:-8]))
        receiver.channel.write(OFFSET+64,raw);receiver.channel.write(OFFSET,struct.pack('<i',2))
        env={k:v for k,v in os.environ.items() if not k.startswith(('SFC_','DXVK_','RTX_'))}
        env.update(SFC_RELEASE_ROOT=str(package),SFC_NATIVE_RESOLUTION='1',SFC_D3D9_PREWARM='1',
            SFC_D3D9_GAME_PID=str(os.getpid()),SFC_REMIX_CALIBRATION_SCENE=receiver.name,
            SFC_PIPELINE_MODE='performance',DXVK_CONFIG_FILE=str(out/'rtx.conf'),
            RTX_AUTOMATION_DISABLE_BLOCKING_DIALOG_BOXES='1',DXVK_ENABLE_RAYTRACING='1')
        extra,_=configure_child(backend_inputs(),env)
        env['SFC_D3D9_STARTUP_PROFILE']=args.profile
        with (out/'rtx.conf').open('a') as stream:stream.write(extra)
        guard=verified_role(CONTEXT,manifest,'job_guard')
        runtime=verified_role(CONTEXT,manifest,'remix_runtime')
        consumer=verified_role(CONTEXT,manifest,'output_receiver')
        command=[str(guard),str(out),'45',str(128*1024*1024),str(2*1024*1024),
            str(args.host.resolve()),str(out),str(runtime),str(consumer),'normal']
        began=time.monotonic();process=sp.Popen(command,env=env,creationflags=sp.CREATE_NO_WINDOW)
        deadline=began+(10 if args.expect_not_ready else 30)
        while time.monotonic()<deadline and process.poll() is None:
            if ready(receiver.channel):break
            time.sleep(.02)
        readiness=ready(receiver.channel)
        report.update(ready=bool(readiness),ready_seconds=time.monotonic()-began,startup=snapshot(receiver.channel))
        if args.expect_not_ready:
            if readiness:raise RuntimeError('Old host unexpectedly completed startup with profiling off')
            cancel(receiver.channel)
            try:process.wait(timeout=6)
            except sp.TimeoutExpired:process.terminate();process.wait(timeout=5)
            report['result']='OLD_HOST_PROFILE_OFF_FAILURE_REPRODUCED'
        else:
            if not readiness:raise RuntimeError('Host did not become ready')
            if args.cancel:cancel(receiver.channel)
            else:
                scene=json.loads((args.scene/'scene.json').read_text())
                row=scene['fresh_preparation_row']
                ticket=dict(SFC_D3D9_GAME_PID=str(os.getpid()),SFC_D3D9_EXPECTED_MODEL=str(row[5]),
                    SFC_D3D9_EXPECTED_SOURCE=str(row[6]),SFC_D3D9_INITIAL_ASSET_MASK='1',
                    SFC_D3D9_REBIND_COOKIE='1',SFC_D3D9_ASSET_SHA256=scene['asset_sha256'],SFC_D3D9_OFFSET_X='0')
                activate(receiver.channel,ticket,receiver.name)
            code=process.wait(timeout=30)
            job=json.loads((out/'job-result.json').read_text())
            text=(out/'job-console.log').read_text(errors='replace')
            consumer_text=(out/'receiver.log').read_text(errors='replace')
            if code or job['exit_code'] or job['stop_reason']:raise RuntimeError('Host/guard did not exit normally')
            if args.cancel:
                if 'WARM_CANCELLED' not in text:raise RuntimeError('Cancellation receipt missing')
            else:
                if 'DIRECT64_OUTPUT_RETURNED' not in text or 'RECEIVER_RETIRED frames=1 result=0' not in consumer_text:
                    raise RuntimeError('Actual output/consumer receipt missing')
                for plane in range(3):
                    host_pixels=(out/f'returned-0-{plane}.raw32').read_bytes()
                    peer_pixels=(out/f'receiver-0-{plane}.raw32').read_bytes()
                    if len(host_pixels)!=8+width*height*4 or struct.unpack_from('<2I',host_pixels)!=(width,height):
                        raise RuntimeError('Wrong output dimensions/size')
                    if host_pixels!=peer_pixels:raise RuntimeError('Host/receiver plane differs')
                report.update(identical_host_receiver_planes=3,bootstrap_only=True,
                    appearance_qualification=False) # First bootstrap is never displayed in SFC.
            report.update(result='PRODUCTION_PREWARM_GPU_PASS',cancel=args.cancel,job=job,
                startup_profile_rows=text.count('STARTUP_PROFILE stage='),output_frames=0 if args.cancel else 1)
            if args.profile=='0' and report['startup_profile_rows']:raise RuntimeError('Profiling was not disabled')
    finally:
        if process and process.poll() is None:process.terminate();process.wait(timeout=5)
        receiver.close()
        (out/'qualification.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
