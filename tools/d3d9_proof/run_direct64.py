"""Approved offline64bit ordinary-D3D9/output alternative;never launches SFC."""
import argparse
import datetime as dt
import json
import os
import subprocess as sp
import time
import struct
from run_offline import ROOT,CAPTURE,GAME,storage,digest,AGGREGATE_BYTES
from run_intercept import BASE,RUNTIME,GUARD,freeze_runtime,generated_bytes
from scene_bundle import prepare

EXE=ROOT/'artifacts/d3d9-proof/direct64-bin/d3d9_direct_host.exe'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');group=parser.add_mutually_exclusive_group();group.add_argument('--asset',type=int,choices=(3,4),default=4);group.add_argument('--synthetic',action='store_true');parser.add_argument('--diagnostic-capture',action='store_true');parser.add_argument('--backbuffer-diagnostic',action='store_true');parser.add_argument('--receiver',choices=('normal','slow','disconnect','exit-acquired','stale-ack','invalid'));parser.add_argument('--single-present',action='store_true')
    parser.add_argument('--paced-frames',type=int,choices=(0,120,300),default=0);parser.add_argument('--timing-only',action='store_true');parser.add_argument('--output-size',type=int,nargs=2,metavar=('WIDTH','HEIGHT'));parser.add_argument('--first-snapshot',action='store_true');parser.add_argument('--investigate-extent',action='store_true')
    parser.add_argument('--latest-input',action='store_true');parser.add_argument('--inject-lag-ms',type=int,choices=(0,35,60),default=0);args=parser.parse_args()
    if args.latest_input and not(args.paced_frames==300 and args.timing_only and args.receiver=='normal'):parser.error('Latest input requires300timing-only updates and normal receiver')
    if args.inject_lag_ms and not args.latest_input:parser.error('Injected lag requires offline latest-input test')
    if args.timing_only and not args.paced_frames:parser.error('Timing-only requires paced proof')
    if args.output_size:
        w,h=args.output_size
        if not 1<=w<=1920 or not 1<=h<=1080:parser.error('Output size outside approved bounds')
        if not qualified_extent(w,h) and not args.investigate_extent:parser.error('Unqualified output layout;explicit --investigate-extent for bounded offline diagnostics only')
        if w*h>1_000_000 and not args.timing_only and not args.first_snapshot:parser.error('Full diagnostic triplets exceed scratch reservation;use timing-only or first-snapshot for this extent')
    if args.first_snapshot and args.paced_frames:parser.error('First-snapshot is a pixel diagnostic,not a paced test')
    if args.paced_frames:
        if args.receiver not in ('normal','slow'):parser.error('Paced proof requires normal or slow receiver')
        args.single_present=True
    if not args.execute:print('Explicit --execute required;offline only');return
    if storage()+128*1024*1024>AGGREGATE_BYTES:raise ValueError('20GB allowance lacks128MiB reservation')
    records=freeze_runtime();folder=BASE/'direct64-runs'/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
    if args.synthetic:
        from synthetic import prepare as synthetic
        folder.parent.mkdir(parents=True,exist_ok=True);synthetic(folder);manifest=json.loads((folder/'scene.json').read_text())
    else:manifest=prepare(CAPTURE/f'LIVE-SCENE-001-asset-{args.asset}.bin',folder,GAME)
    if args.first_snapshot:limit_to_first(folder,manifest)
    if args.output_size:
        resize_output(folder,args.output_size,manifest)
    (folder/'rtx.conf').write_text('''rtx.enableReplacementAssets = False
rtx.enableRaytracing = True
rtx.captureInstances = True
rtx.captureEnableMultiframe = False
rtx.captureInstanceStageName = proof.usda
rtx.captureShowMenuOnHotkey = False
rtx.graphicsPreset = 4
rtx.integrateIndirectMode = 0
rtx.enableRayReconstruction = False
rtx.dlssPreset = 0
rtx.upscalerType = 0
rtx.resolutionScale = 1.0
''')
    header=json.loads((ROOT/'artifacts/remix-runtime/deps/manifest.json').read_text())
    if digest(ROOT/'artifacts/remix-runtime/deps/remix_c.h').upper()!=header['header_sha256'].upper():raise ValueError('Pinned header changed')
    report=dict(result='PARTIAL',sfc_launched=False,sdk_mesh_calls=0,output_api_device_registration=True,single_present_after_startup=args.single_present,paced_frames=args.paced_frames,timing_only=args.timing_only,
        model=manifest.get('model_name','SYNTHETIC asymmetric control'),synthetic=args.synthetic,backbuffer_diagnostic=args.backbuffer_diagnostic,exe_sha256=digest(EXE),runtime_sha256=digest(RUNTIME/'.trex/d3d9.dll'),
        replay_sha256=digest(folder/'scene.bin'),header_sha256=header['header_sha256'],
        sources={name:digest(ROOT/name) for name in ('tools/d3d9_proof/d3d9_replay.cpp','tools/d3d9_proof/d3d9_direct_host.cpp','tools/d3d9_proof/build_direct64.ps1','tools/d3d9_proof/run_direct64.py','tools/scene_bridge/scene_bundle.py')})
    report['extent_investigation']=args.investigate_extent
    report.update(latest_input=args.latest_input,inject_lag_ms=args.inject_lag_ms)
    if args.latest_input:
        report['sources'].update({p:digest(ROOT/p) for p in ('tools/d3d9_proof/frame_ingress.h','tools/d3d9_proof/ingress_replay.h')})
    if args.receiver:
        receiver=ROOT/'artifacts/d3d9-proof/receiver-bin/output_receiver.exe'
        report.update(receiver_mode=args.receiver,receiver_sha256=digest(receiver))
        report['sources'].update({name:digest(ROOT/name) for name in ('tools/d3d9_proof/output_channel.h','tools/d3d9_proof/output_producer.h','tools/d3d9_proof/output_receiver.cpp','tools/d3d9_proof/build_receiver.ps1')})
    process=None
    try:
        env={**os.environ,'DXVK_CONFIG_FILE':str(folder/'rtx.conf'),'RTX_AUTOMATION_DISABLE_BLOCKING_DIALOG_BOXES':'1','RTX_CAPTURE_REMIX_CONFIGS':'0',
            'DXVK_ENABLE_RAYTRACING':'1','DXVK_GRAPHICS_PRESET_TYPE':'4','RTX_INTEGRATE_INDIRECT_MODE':'0','DXVK_DLSS_PRESET':'0'}
        for key in ('DXVK_RTX_CAPTURE_ENABLE_ON_FRAME','DXVK_DUMP_SCREENSHOT_FRAME','DXVK_TERMINATE_APP_FRAME'):
            env.pop(key,None)
        if args.diagnostic_capture:
            env['DXVK_RTX_CAPTURE_ENABLE_ON_FRAME']='12';env['DXVK_DUMP_SCREENSHOT_FRAME']='20'
        env['SFC_DIRECT64_BACKBUFFER_DIAGNOSTIC']='1' if args.backbuffer_diagnostic else '0'
        env['SFC_DIRECT64_SINGLE_PRESENT']='1' if args.single_present else '0'
        env['SFC_DIRECT64_PACED_FRAMES']=str(args.paced_frames)
        env['SFC_DIRECT64_TIMING_ONLY']='1' if args.timing_only else '0'
        env['SFC_DIRECT64_INVESTIGATE_EXTENT']='1' if args.investigate_extent else '0'
        env['SFC_DIRECT64_LATEST_INPUT']='1' if args.latest_input else '0'
        env['SFC_DIRECT64_INJECT_LAG_MS']=str(args.inject_lag_ms)
        command=[str(GUARD),str(folder),'90',str(128*1024*1024),str(2*1024*1024),str(EXE),str(folder),str(RUNTIME/'.trex/d3d9.dll')]
        if args.receiver:command.extend((str(receiver),args.receiver))
        process=sp.Popen(command,env=env,creationflags=sp.CREATE_NO_WINDOW);began=time.monotonic()
        while process.poll() is None:
            if generated_bytes(records)>64*1024*1024 or time.monotonic()-began>100:raise ValueError('Direct64 workflow limit')
            time.sleep(.1)
        report['job']=json.loads((folder/'job-result.json').read_text());job=report['job']
        if process.returncode or job['exit_code'] or job['stop_reason'] or job['remaining_owned_processes']:raise ValueError('Direct64 run failed;preserve partial')
        text=(folder/'job-console.log').read_text()
        if 'DIRECT64_OUTPUT_RETURNED sdk_mesh_calls=0' not in text or 'OUTPUT_API_SHUTDOWN 0' not in text:raise ValueError('No qualified native completion/retirement')
        if any(digest(RUNTIME/name)!=record['sha256'] for name,record in records.items()):raise ValueError('Pinned runtime input changed')
        report['result']='DIRECT64_OUTPUT_RETURNED_PIXEL_ANALYSIS_REQUIRED'
        if args.receiver:
            frames=text.count('RETURNED frame=') if args.latest_input else args.paced_frames or len(manifest['frames'])
            report['receiver_verification']=verify_receiver(folder,args.receiver,frames,sample_stride=59 if args.paced_frames else 0,verify_images=not args.timing_only)
            report['result']='DIRECT64_TIMING_RECEIPTS_ONLY' if args.timing_only else 'DIRECT64_X86_RECEIVER_OFFLINE_VERIFIED'
        if args.latest_input:
            from analyze_ingress import analyze
            report['input_replay']=analyze(folder,args.inject_lag_ms)
            report['result']='OFFLINE_INPUT_RECOVERY_OBSERVED_NOT_LIVE_DELIVERY'
    except Exception as error:report['error']=str(error);raise
    finally:
        if process is not None and process.poll() is None:process.terminate();process.wait(timeout=10)
        (folder/'result.json').write_text(json.dumps(report,indent=2));print('Evidence:',folder,flush=True)
    print(report['result'])


def qualified_extent(width,height):return (width,height) in ((960,540),(640,960),(1920,1080))


def limit_to_first(folder,manifest):
    """Bound full-resolution diagnostics,not source capture or geometry modification."""
    from pathlib import Path
    from scene_bundle import read_replay,FRAME
    folder=Path(folder);path=folder/'scene.bin';scene=read_replay(path);raw=bytearray(path.read_bytes())
    count=len(scene['frames'])
    if count>1:del raw[len(raw)-(count-1)*FRAME.size:]
    struct.pack_into('<I',raw,20,1);path.write_bytes(raw)
    manifest['frames']=manifest['frames'][:1];manifest['first_snapshot_only']=True;manifest['replay_sha256']=digest(path)
    (folder/'scene.json').write_text(json.dumps(manifest,indent=2))


def resize_output(folder,extent,manifest):
    """Consumer output extent ONLY. Captured geometry/camera/source viewport unchanged."""
    from pathlib import Path
    w,h=extent
    if not 1<=w<=1920 or not 1<=h<=1080:raise ValueError('Output extent bound')
    folder=Path(folder);path=folder/'scene.bin';raw=bytearray(path.read_bytes())
    from scene_bundle import read_replay
    read_replay(path)
    if len(raw)<32:raise ValueError('Scene header missing')
    struct.pack_into('<2I',raw,24,w,h);path.write_bytes(raw)
    manifest['output_extent_override']=[w,h];manifest['replay_sha256']=digest(path)
    (folder/'scene.json').write_text(json.dumps(manifest,indent=2))


def verify_receiver(folder,mode,frames,sample_stride=0,verify_images=True):
    """Byte-exact cross-process triplets;not appearance or real-time qualification."""
    folder=__import__('pathlib').Path(folder)
    parent=(folder/'job-console.log').read_text();child=(folder/'receiver.log').read_text()
    if 'OUTPUT_PEER_RETIRED' not in parent:raise ValueError('No receiver retirement')
    matched=[]
    for path in sorted(folder.glob('receiver-*-*.raw32')):
        source=folder/path.name.replace('receiver-','returned-',1)
        if not source.exists() or digest(path)!=digest(source):raise ValueError('Cross-process returned pixels differ')
        matched.append(dict(name=path.name,sha256=digest(path)))
    if mode in ('normal','slow'):
        images=3*(1+frames//sample_stride) if sample_stride else frames*3
        if not verify_images:images=0
        if len(matched)!=images or child.count('RECEIVED sequence=')!=frames or parent.count('OUTPUT_ACK sequence=')!=frames:raise ValueError('Incomplete receiver triplets/ACKs')
        if mode=='slow':
            holds=[int(row.split('held_ms=')[1]) for row in parent.splitlines() if row.startswith('OUTPUT_ACK ')]
            if not holds or min(holds)<200:raise ValueError('Slow receiver not exercised')
    elif mode=='invalid':
        if matched or 'OUTPUT_INVALID_REJECTED' not in parent or 'RECEIVER_REJECTED malformed/' not in child:raise ValueError('Malformed packet not rejected')
    elif mode=='stale-ack':
        if len(matched)!=3 or 'OUTPUT_STALE_ACK_REJECTED' not in parent:raise ValueError('Stale ACK not rejected')
    elif mode=='exit-acquired':
        if matched or 'OUTPUT_PEER_DISCONNECTED acquired=1' not in parent:raise ValueError('Acquired disconnect not exercised')
    elif mode=='disconnect':
        if len(matched)!=3 or 'OUTPUT_PEER_DISCONNECTED' not in parent:raise ValueError('Disconnect not exercised')
    return dict(mode=mode,matching_images=matched,sample_stride=sample_stride,image_verification=verify_images,scope='GPU completion receipts;CPU byte verification only when image_verification true;held snapshots or synthetic60Hz schedule,not original-rate replay/live timing')


if __name__=='__main__':main()
