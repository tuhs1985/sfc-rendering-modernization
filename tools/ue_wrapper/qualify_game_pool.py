"""Explicit packaged UE -> x64 normalization -> real x86 native GPU-pool fixture."""
import argparse
import copy
import ctypes as C
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import time
import numpy as np
from qualify_registry import ROOT,source_row,publish_frame,runtime_exe
from qualify_stream import reference
for part in ('src/rendering','src/transport','src/runtime'):
    sys.path.insert(0,str(ROOT/part))
from live_scene import SceneChannel
from live_owner_timing import initialize
from owner_rebind import fnv
import multi_scene as wire

def run(exe,scene,receiver,consumer,output):
    output=output.resolve();output.mkdir(parents=True,exist_ok=False)
    inputs=output/'input';inputs.mkdir()
    channel=SceneChannel(create=True);ue=native=None
    kernel=C.WinDLL("kernel32",use_last_error=True)
    kernel.CreateEventW.argtypes=[C.c_void_p,C.c_int,C.c_int,C.c_wchar_p];kernel.CreateEventW.restype=C.c_void_p
    kernel.CloseHandle.argtypes=[C.c_void_p]
    event_name=channel.name+"-ue-fixture-read";event=kernel.CreateEventW(None,False,False,event_name)
    if not event:raise OSError(C.get_last_error(),"Fixture read event")
    try:
        initialize(channel,persistent=True);wire.initialize(channel)
        channel.write(12,struct.pack('<I',1));channel.write(wire.OFFSET+12,struct.pack('<I',os.getpid()))
        channel.write(10*1024*1024+28,struct.pack('<I',os.getpid()))
        data=json.loads(scene.read_text(encoding='utf-8-sig'))
        packet=(ROOT/data['source_packet']).read_bytes();header=struct.unpack_from('<32I',packet)
        data['session']=channel.name;data['source_binding']=dict(pid=os.getpid(),model=header[10],source=header[12])
        for image in data['images'].values():
            destination=inputs/image['file']
            if not destination.exists():os.link(scene.parent/image['file'],destination)
        first=copy.deepcopy(data['frames'][0]);second=copy.deepcopy(first);second['model'][0][3]+=24
        frames=[];rows=[]
        for index,frame in enumerate((first,second)):
            # Explicit odd-size/tactical-offset fixture, not a captured live target.
            frame['viewport']=[13,9,499,277];frame['target_width']=513;frame['target_height']=289
            for key in ('model','view','projection'):
                frame[key]=np.asarray(frame[key],dtype=np.float32).astype(float).tolist()
            frame['source_frame']=101+index;frame['source_sequence']=201+index
            row=source_row(data,frame,101+index,201+index,0)
            rows.append(row);frames.append(frame)
            publish_frame(channel,[row],101+index,201+index,offered=1)
            slot=wire.OFFSET+64+((101+index)%wire.FRAMES)*wire.FRAME_SLOT
            frame['native_frame_hash']=f'{struct.unpack("<Q",channel.read(slot+8+wire.FRAME_BYTES-8,8))[0]:016x}'
        data['frames']=frames;data['source_scope']='Explicit native-pool boundary fixture; captured arrays/images, changing synthetic poses and target'
        revision=data['asset']['revision'];owner=data['owner_epoch']
        channel.write(10*1024*1024+32,struct.pack('<Q',owner|(revision<<32)))
        raw=wire.ASSET.pack(revision,revision,owner,revision,header[10],header[12],len(packet),0,bytes.fromhex(data['asset']['content']),fnv(packet),1,0)
        wire.publish(channel,revision,raw[:-8]+struct.pack('<Q',fnv(raw[:-8])))
        words=[int(channel.name[-32:][n:n+8],16) for n in range(0,32,8)]
        notice=struct.pack('<8IQ4IQ',0x31544754,1,64,os.getpid(),*words,1,513,289,1,1,0)
        channel.write(4352,struct.pack('<I',1));channel.write(4352+64,notice[:-8]+struct.pack('<Q',fnv(notice[:-8])));channel.write(4352,struct.pack('<I',2))
        (inputs/'scene.json').write_text(json.dumps(data),encoding='utf-8')
        env={k:v for k,v in os.environ.items() if not k.startswith('SFC_')}
        env.update(SFC_REMIX_CALIBRATION_SCENE=channel.name,SFC_D3D9_GAME_OUTPUT='1',SFC_D3D9_SYNC_BUFFER='1',SFC_D3D9_MULTISCENE='1',SFC_NATIVE_RESOLUTION='1')
        native=subprocess.Popen([str(consumer.resolve()),channel.name,str(os.getpid()),str(output/'native'),'6',event_name],env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        args=[str(runtime_exe(exe)),'-windowed','-ResX=640','-ResY=480','-nosound','-nolog','-SFCDiagnostics','-SFCGpuStream',
              '-SFCGamePoolFixture',f'-SFCFixtureReadEvent={event_name}','-SFCStreamNoReadback','-SFCNativeWidth=513','-SFCNativeHeight=289','-SFCStreamFrames=6',
              f'-SFCScene={inputs/"scene.json"}',f'-SFCOutput={output}',f'-SFCGpuConsumer={receiver.resolve()}']
        start=time.monotonic();ue=subprocess.Popen(args,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        code=ue.wait(timeout=120)
        if code or (output/'rejected.txt').exists():
            raise RuntimeError((output/'rejected.txt').read_text(encoding='utf-8-sig') if (output/'rejected.txt').exists() else f'UE exit {code}')
        report=json.loads((output/'stream.json').read_text(encoding='utf-8-sig'))
        text=native.communicate(timeout=10)[0].decode(errors='replace')
        if native.returncode:raise RuntimeError(text)
        if report['submitted']!=6 or report['completed']!=6:raise ValueError('UE raw export leases incomplete')
        checks=[];received=[]
        for index in (1,2,5,6):
            raw=(output/'native'/f'{index}.packet').read_bytes();meta=(output/'native'/f'{index}.metadata').read_bytes()
            frame_index=(index-1)%2;frame=frames[frame_index]
            source_frame=struct.unpack_from('<Q',raw,40)[0]
            if source_frame!=frame['source_frame'] or struct.unpack_from('<Q',meta)[0]!=frame['source_sequence'] or list(struct.unpack_from('<4I',meta,8))!=words:
                raise ValueError('Native publication lost frame/sequence/session provenance')
            if struct.unpack_from('<Q',raw,96)[0]!=int(frame['native_frame_hash'],16):raise ValueError('Native sealed-frame hash mismatch')
            colour=np.fromfile(output/'native'/f'{index}-0.raw',np.uint8).reshape(289,513,4)
            depth=np.fromfile(output/'native'/f'{index}-1.raw',np.float32).reshape(289,513)
            owners=np.fromfile(output/'native'/f'{index}-2.raw',np.uint32).reshape(289,513)
            expected,covered,interior,z=reference(data,inputs,frame_index,include_depth=True)
            area=np.s_[9:286,13:512];stable=covered&interior
            errors=np.max(np.abs(colour[area][:,:,2::-1].astype(np.int16)-expected.astype(np.int16)),axis=2)
            accurate=float(np.mean(errors[stable]<=3));depth_error=float(np.quantile(np.abs(depth[area][stable]-z[stable]),.995))
            if accurate<.97 or depth_error>1e-4 or np.mean(owners[area][stable]==owner)<.999:
                raise ValueError(f'Actual game-pool pixels disagree: {accurate}, {depth_error}')
            margins=np.ones((289,513),bool);margins[area]=False
            if np.any(colour[margins]) or np.any(owners[margins]) or np.any(depth[margins]!=-1234):raise ValueError('Native viewport margin contamination')
            checks.append(dict(output=index,source_frame=source_frame,colour_within_three=accurate,depth_error_p995=depth_error,stable_pixels=int(stable.sum())))
            received.append(colour)
        if np.any(received[0]!=received[1],axis=2).sum()<20 or not np.array_equal(received[0],received[2]) or not np.array_equal(received[1],received[3]):
            raise ValueError('Current source metadata hid stale or wrong frame pixels')
        result=dict(scope='Standalone actual packaged UE/x64 receiver/x86 GPU consumer, no SFC insertion',checks=checks,
                    exports=6,consumer=text.strip(),cpu_pixel_transport=False,source_arrays_images_unchanged=True,seconds=time.monotonic()-start)
        (output/'qualified.json').write_text(json.dumps(result,indent=2));return result
    finally:
        for p in (ue,native):
            if p is not None and p.poll() is None:p.terminate();p.wait(timeout=5)
        channel.close();kernel.CloseHandle(event)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('exe','scene','receiver','consumer','output'):p.add_argument(name,type=Path)
    a=p.parse_args();print(json.dumps(run(a.exe,a.scene,a.receiver,a.consumer,a.output),indent=2))
