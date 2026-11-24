"""Standalone paired UE output qualification; no SFC launch or native suppression."""
import argparse
import copy
import json
import os
from pathlib import Path
import subprocess
import struct
import sys
import time

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from qualify import runtime_exe
sys.path.insert(0,str(HERE.parent/'ue5_proof'))
from verify import reference as source_reference


def reference(scene,folder,frame_index=0,*,include_depth=False):
    # Current UE adapter's known source-image-origin conversion. Historical
    # proof defaults remain unchanged; original scene/images are never rewritten.
    return source_reference(scene,folder,frame_index,include_depth=include_depth,image_origin='bottom')


def fnv(raw):
    value=14695981039346656037
    for byte in raw:value=((value^byte)*1099511628211)&0xffffffffffffffff
    return value


def run(exe,scene,receiver,output,*,frames=12,readback=True,fault=None,reject=False,
        cancel=None,passive_ms=0,allocation_failure=False,resize=False,device_loss=False,stale_device=False,allocation_epoch=0):
    exe,scene,receiver,output=map(lambda p:p.resolve(),(exe,scene,receiver,output))
    output.mkdir(parents=True,exist_ok=False)
    inputs=output/'input';inputs.mkdir()
    source=json.loads(scene.read_text(encoding='utf-8-sig'))
    source=copy.deepcopy(source)
    first=copy.deepcopy(source['frames'][0])
    second=copy.deepcopy(first)
    second['model'][0][3]+=24.0
    for frame in (first,second):
        frame.pop('source_frame',None);frame.pop('source_sequence',None)
    source['frames']=[first,second]
    if resize:
        for frame in (copy.deepcopy(first),copy.deepcopy(second)):
            frame['viewport']=[200,30,1400,840]
            frame['target_width']=1600;frame['target_height']=900
            source['frames'].append(frame)
    source['source_scope']='Synthetic changing-pose fixture derived from original source arrays; no live SFC frame claim'
    for image in source['images'].values():
        original=scene.parent/image['file'];destination=inputs/image['file']
        if not destination.exists():os.link(original,destination)
    (inputs/'scene.json').write_text(json.dumps(source))
    args=[str(runtime_exe(exe)),'-windowed','-ResX=1920','-ResY=1080','-nosound','-nolog',
          '-SFCDiagnostics','-SFCGpuStream','-SFCNativeWidth=1920','-SFCNativeHeight=1080',f'-SFCStreamFrames={frames}',
          f'-SFCScene={inputs/"scene.json"}',f'-SFCOutput={output}',f'-SFCGpuConsumer={receiver}']
    if not readback:args.append('-SFCStreamNoReadback')
    if fault:args.append(f'-SFCReceiverFault={fault}')
    if allocation_failure:args.append('-SFCExportFailAllocation')
    if allocation_epoch:args.append(f'-SFCExportFailAllocationEpoch={allocation_epoch}')
    if device_loss:args.append('-SFCExportDeviceLoss')
    if stale_device:args.append('-SFCStreamStaleDevice')
    if passive_ms:args.append(f'-SFCStreamPassiveMs={passive_ms}')
    if cancel:args.append('-SFCStreamCancelBeforeFirst' if cancel=='before-first' else '-SFCStreamCancelDuringRead')
    start=time.monotonic()
    process=subprocess.Popen(args,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:code=process.wait(timeout=120)
    finally:
        if process.poll() is None:process.kill();process.wait()
    if reject:
        if not (output/'rejected.txt').exists() or (output/'stream.json').exists():
            raise ValueError('Expected a bounded output rejection, not success or silence')
        return dict(rejected=True,reason=(output/'rejected.txt').read_text(encoding='utf-8-sig'),
                    process_seconds=time.monotonic()-start)
    if cancel:
        if code or (output/'rejected.txt').exists() or not (output/'cancelled.json').exists():
            raise ValueError(f'Cancellation failed: {output}')
        report=json.loads((output/'cancelled.json').read_text(encoding='utf-8-sig'))
        if not report['drained'] or (cancel=='before-first' and report['submitted']):
            raise ValueError('Cancellation released an outstanding GPU lease or produced too early')
        report.update(cancelled=True,process_seconds=time.monotonic()-start)
        return report
    if code or (output/'rejected.txt').exists() or not (output/'stream.json').exists():
        detail=(output/'rejected.txt').read_text(encoding='utf-8-sig') if (output/'rejected.txt').exists() else str(code)
        raise RuntimeError(f'Paired UE output failed: {detail}; evidence: {output}')
    report=json.loads((output/'stream.json').read_text(encoding='utf-8-sig'))
    if report['submitted']!=frames or report['completed']!=frames or len(report['frames'])!=frames:
        raise ValueError('Persistent output did not complete its leases')
    times=np.array([t['total_ms'] for t in report['timings']])
    if len(times)!=frames or not np.isfinite(times).all() or (times<0).any():
        raise ValueError('Missing coherent QPC timing')
    report['capture_to_normalized_ms']=dict(zip(('median','p95','p99','maximum'),map(float,np.quantile(times,[.5,.95,.99,1]))))
    report['over_33_333ms']=int(np.sum(times>1000/30))
    if resize and report['generation_changes']!=(frames-1)//2:
        raise ValueError('Output target did not complete each expected generation transition')
    if not readback:
        if (output/'receiver').exists():raise ValueError('No-readback receiver created recording files')
        report.update(process_seconds=time.monotonic()-start,cpu_transport=False,readback=False)
        (output/'qualified.json').write_text(json.dumps(report,indent=2))
        return report
    received=[];checks=[]
    for index in (1,2,frames-1,frames):
        record=report['frames'][index-1]
        if record['output']!=index or record['frame_index']!=(index-1)%len(source['frames']):
            raise ValueError('Changing frame provenance mismatch')
        raw=output/'receiver'
        packet=(raw/f'{index}.packet').read_bytes()
        if len(packet)!=280 or fnv(packet[:-8])!=struct.unpack_from('<Q',packet,272)[0]:
            raise ValueError('Raw export packet checksum/layout')
        words=struct.unpack_from('<2Q',packet,56)
        if ''.join(f'{word:016x}' for word in words)!=report['replay_session']:
            raise ValueError('Cross-session normalized pixels')
        if packet[72:104].hex()!=source['asset']['content'] or struct.unpack_from('<2Q',packet,104)!=(source['owner_epoch'],source['asset']['revision']):
            raise ValueError('Normalized output lost exact asset/owner/revision identity')
        if struct.unpack_from('<Q',packet,176)[0]!=index or struct.unpack_from('<I',packet,12)[0]!=1:
            raise ValueError('Output sequence or explicit replay identity lost')
        frame=source['frames'][record['frame_index']]
        pose=fnv(struct.pack('<16d',*(n for row in frame['model'] for n in row)))
        for name in ('view','projection','viewport'):
            values=frame[name] if name=='viewport' else [n for row in frame[name] for n in row]
            pose=((pose^fnv(struct.pack('<'+str(len(values))+'d',*values)))*1099511628211)&0xffffffffffffffff
        if struct.unpack_from('<2Q',packet,136)!=(pose,pose):
            raise ValueError('Normalized image camera/pose identity changed')
        target_width,target_height,viewport_x,viewport_y=struct.unpack_from('<4I',packet,32)
        frame=source['frames'][record['frame_index']]
        if (target_width,target_height)!=(frame.get('target_width',1920),frame.get('target_height',1080)) or [viewport_x,viewport_y]!=frame['viewport'][:2]:
            raise ValueError('Normalized target/viewport identity changed')
        colour=np.fromfile(raw/f'{index}-0.raw',np.uint8).reshape(target_height,target_width,4)
        depth=np.fromfile(raw/f'{index}-1.raw',np.float32).reshape(target_height,target_width)
        owners=np.fromfile(raw/f'{index}-2.raw',np.uint32).reshape(target_height,target_width)
        expected,covered,interior,native=reference(source,inputs,record['frame_index'],include_depth=True)
        x,y,w,h=map(int,frame['viewport']);area=np.s_[y:y+h,x:x+w]
        rgb=colour[area][:,:,2::-1]
        stable=interior&covered
        errors=np.max(np.abs(rgb.astype(np.int16)-expected.astype(np.int16)),axis=2)
        accurate=float(np.mean(errors[stable]<=3))
        if accurate<.97:raise ValueError(f'Output {index} colour belongs to wrong pose: {accurate}')
        native_error=np.abs(depth[area][stable]-native[stable])
        if np.quantile(native_error,.995)>1e-4:raise ValueError(f'Output {index} depth belongs to wrong pose')
        if np.mean(owners[area][stable]==source['owner_epoch'])<.999:
            raise ValueError(f'Output {index} owner coverage mismatch')
        outside=np.ones((target_height,target_width),bool);outside[area]=False
        if np.any(owners[outside]) or np.any(depth[outside]!=-1234) or np.any(colour[outside]):
            raise ValueError('Tactical image leaked into native viewport margins')
        received.append(colour)
        checks.append(dict(output=index,frame=record['frame_index'],colour_within_three=accurate,
                           stable_depth_pixels=int(stable.sum()),native_error_p995=float(np.quantile(native_error,.995))))
    changed=int(np.any(received[0]!=received[1],axis=2).sum())
    if changed<100 or (not resize and (not np.array_equal(received[0],received[2]) or not np.array_equal(received[1],received[3]))):
        raise ValueError('Visible output does not follow the alternating source poses')
    if resize and report['generation_changes']<2:raise ValueError('Output generations were not retired and recreated')
    report.update(independent_pixel_checks=checks,changed_pixels=changed,process_seconds=time.monotonic()-start,
                  source_geometry_unchanged=True,cpu_transport=False)
    (output/'qualified.json').write_text(json.dumps(report,indent=2))
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('exe','scene','receiver','output'):parser.add_argument(name,type=Path)
    parser.add_argument('--frames',type=int,default=12)
    parser.add_argument('--no-readback',action='store_true')
    parser.add_argument('--fault',choices=('slow-read','crash-after-acquire','passive-exit','wrong-ack','wrong-receipt','hold-before-ack'))
    parser.add_argument('--reject',action='store_true')
    parser.add_argument('--cancel',choices=('before-first','during-read'))
    parser.add_argument('--passive-ms',type=int,default=0)
    parser.add_argument('--allocation-failure',action='store_true')
    parser.add_argument('--resize',action='store_true')
    parser.add_argument('--device-loss',action='store_true')
    parser.add_argument('--stale-device',action='store_true')
    parser.add_argument('--allocation-epoch',type=int,default=0)
    args=parser.parse_args()
    result=run(args.exe,args.scene,args.receiver,args.output,frames=args.frames,readback=not args.no_readback,
               fault=args.fault,reject=args.reject,cancel=args.cancel,passive_ms=args.passive_ms,allocation_failure=args.allocation_failure,resize=args.resize,
               device_loss=args.device_loss,stale_device=args.stale_device,allocation_epoch=args.allocation_epoch)
    print(json.dumps({k:v for k,v in result.items() if k not in ('frames','timings')},indent=2))
