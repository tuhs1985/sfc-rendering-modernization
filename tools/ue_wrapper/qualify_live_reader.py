"""Packaged UE read-only source replay; no SFC launch or game insertion."""
import argparse
import copy
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import time
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
for part in ('src/transport','src/assets','src/runtime'):
    sys.path.insert(0,str(ROOT/part))
from live_scene import SceneChannel
import multi_scene as wire
from owner_rebind import fnv
from qualify_stream import runtime_exe,reference


def run(exe,scene,output,delay=1.5,fault=None):
    output=output.resolve();output.mkdir(parents=True,exist_ok=False)
    source=json.loads(scene.read_text());source=copy.deepcopy(source)
    channel=SceneChannel(create=True)
    process=None
    try:
        wire.initialize(channel)
        channel.write(12,struct.pack('<I',1))
        channel.write(wire.OFFSET+12,struct.pack('<I',os.getpid()))
        source['session']=channel.name
        source['source_scope']='Explicit replay from captured arrays into current source IPC; no live SFC claim'
        inputs=output/'input';inputs.mkdir()
        for image in source['images'].values():
            if not (inputs/image['file']).exists():os.link(scene.parent/image['file'],inputs/image['file'])
        input_path=inputs/'scene.json'
        # A qualified parent's one-time asset publication arrives late. Images are
        # unchanged and no per-frame asset/texture file is written.
        owner=source['owner_epoch'];revision=source['asset']['revision']
        if 'source_binding' in source:
            model_id,source_id=source['source_binding']['model'],source['source_binding']['source']
        else:
            raw=(ROOT/source['source_packet']).read_bytes()
            header=struct.unpack_from('<32I',raw);model_id,source_id=header[10],header[12]
        source['source_binding']=dict(pid=os.getpid(),model=model_id,source=source_id)
        args=[str(runtime_exe(exe)),'-windowed','-ResX=1920','-ResY=1080','-nosound','-nolog',
              '-SFCDiagnostics','-SFCSourceReplay',f'-SFCScene={input_path}',f'-SFCOutput={output}',
              f'-SFCSourceMap={channel.name}',f'-SFCSourcePID={os.getpid()}',f'-SFCOwner={owner}',
              f'-SFCRevision={revision}',f'-SFCModelIdentity={model_id}',f'-SFCSourceIdentity={source_id}',
              '-SFCSourceReplayUpdates=12']
        process=subprocess.Popen(args,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        start=time.monotonic()
        # Wait for the real packaged reader to attach, not a guessed UE startup.
        deadline=start+60
        while not (output/'source-attached.json').exists():
            if process.poll() is not None:raise ValueError(f'UE exited before passive source attachment: {process.returncode}')
            if time.monotonic()>deadline:raise TimeoutError('UE source attachment')
            time.sleep(.01)
        attached=time.monotonic()
        time.sleep(delay)
        if process.poll() is not None:raise ValueError('Passive UE lifetime depended on immediate assets')
        if fault=='stop-passive':
            channel.write(wire.OFFSET+32,struct.pack('<I',1))
            if process.wait(timeout=10)!=0 or (output/'source-result.json').exists():raise ValueError('Passive source stop did not close cleanly')
            result=dict(fault=fault,normal_exit=True,before_assets=True)
            (output/'qualified.json').write_text(json.dumps(result,indent=2));return result
        if fault=='wrong-session':source['session']='Local\\SFCBridge_'+'0'*32
        if fault=='wrong-owner':source['owner_epoch']+=1
        if fault=='wrong-revision':source['asset']['revision']+=1
        if fault=='wrong-binding':source['source_binding']['model']+=1
        temporary=input_path.with_suffix('.tmp');temporary.write_text(json.dumps(source));os.replace(temporary,input_path)
        base_frame=source['frames'][0]
        sequence=base_frame['source_sequence'];frame=base_frame['source_frame']
        published=0
        while process.poll() is None and time.monotonic()<deadline:
            current=copy.deepcopy(base_frame)
            current['model'][0][3]+=24 if published%2 else 0
            current['view'][0][3]+=(published%3+1)*6.0
            row=[0]*96;row[1]=owner;row[2]=frame+published+1;row[4]=1
            row[5:8]=[model_id,source_id,revision];row[48]=1
            for offset,key in ((8,'model'),(49,'view'),(66,'projection')):
                values=[value for line in current[key] for value in line]
                row[offset:offset+16]=struct.unpack('<16I',struct.pack('<16f',*values))
                row[offset+16]=0 if key=='projection' else 0x100
            x,y,w,h=current['viewport'];row[83:89]=struct.unpack('<6I',struct.pack('<6f',x,y,w,h,w/2,h/2))
            seq=sequence+published+1;row[94:96]=[seq&0xffffffff,seq>>32]
            packet=bytearray(wire.FRAME_BYTES)
            struct.pack_into('<QQ4I',packet,0,seq,time.perf_counter_ns(),row[2],owner,revision,1)
            struct.pack_into('<96I',packet,32,*row)
            struct.pack_into('<Q',packet,len(packet)-8,fnv(packet[:-8]))
            base=wire.OFFSET+64+(row[2]%wire.FRAMES)*wire.FRAME_SLOT
            channel.write(base,struct.pack('<II',1,0));channel.write(base+8,bytes(packet))
            channel.write(base,struct.pack('<I',2));channel.write(wire.OFFSET+36,struct.pack('<I',row[2]))
            published+=1;time.sleep(.025)
        if process.poll() is None:raise TimeoutError('Packaged source replay')
        if fault:
            error=output/'rejected.txt'
            if not error.exists() or (output/'source-result.json').exists():raise ValueError('Invalid late activation was not rejected')
            result=dict(fault=fault,rejected=error.read_text(),exit_code=process.returncode)
            (output/'qualified.json').write_text(json.dumps(result,indent=2));return result
        if process.returncode:raise ValueError((output/'rejected.txt').read_text() if (output/'rejected.txt').exists() else f'UE exit {process.returncode}')
        result=json.loads((output/'source-result.json').read_text())
        if result['updates']<12 or result['asset_builds']!=1 or result['session']!=channel.name:
            raise ValueError('Source replay identity/geometry lifetime')
        if not sequence<result['sequence']<=sequence+published:raise ValueError('Source sequence provenance')
        used=result['sequence']-sequence-1
        expected=copy.deepcopy(base_frame);expected['model'][0][3]+=24 if used%2 else 0
        expected['view'][0][3]+=(used%3+1)*6.0
        for key in ('model','view','projection','viewport'):
            if not np.array_equal(np.asarray(expected[key]),np.asarray(result[key])):
                raise ValueError(f'Source {key} did not follow exact accepted sequence')
        if result['frame']!=frame+used+1:raise ValueError('Source frame/sequence association')
        comparison=copy.deepcopy(source);comparison['frames']=[expected]
        rgb,covered,interior=reference(comparison,inputs,0)
        width,height=map(int,expected['viewport'][2:])
        actual=np.fromfile(output/'source-colour.bgra',np.uint8).reshape(height,width,4)[:,:,2::-1]
        stable=interior&covered
        errors=np.max(np.abs(actual.astype(np.int16)-rgb.astype(np.int16)),axis=2)
        accuracy=float(np.mean(errors[stable]<=3))
        if accuracy<.97:raise ValueError(f'Actual UE pixels did not follow source sequence: {accuracy}')
        result.update(passive_seconds=round(time.monotonic()-attached,3),asset_delay_seconds=delay,
                      published=published,replay=True,cpu_image_transport=False,colour_within_three=accuracy)
        (output/'qualified.json').write_text(json.dumps(result,indent=2))
        return result
    finally:
        if process is not None and process.poll() is None:process.kill();process.wait()
        channel.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('exe','scene','output'):parser.add_argument(name,type=Path)
    parser.add_argument('--delay',type=float,default=1.5)
    parser.add_argument('--fault',choices=('wrong-session','wrong-owner','wrong-revision','wrong-binding','stop-passive'))
    args=parser.parse_args();print(json.dumps(run(args.exe,args.scene,args.output,args.delay,args.fault),indent=2))
