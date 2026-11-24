"""Bounded 1/6/100+ retained-owner replay; no SFC, screenshots or image readback."""
import argparse
import copy
import ctypes as C
import json
import math
import os
from pathlib import Path
import struct
import subprocess
import sys
import time

from qualify_registry import ROOT,SceneChannel,wire,fnv,source_row,publish_frame,publish_state,runtime_exe


def qpc():
    value=C.c_longlong();C.windll.kernel32.QueryPerformanceCounter(C.byref(value));return value.value


def run(exe,scene,output,owners=6,frames=180,normal=False):
    if not 1<=owners<=256 or not 10<=frames<=10000:raise ValueError('Fixture exceeds the existing source transport or bounded test length')
    output=output.resolve();output.mkdir(parents=True,exist_ok=False)
    source=json.loads(scene.read_text());directory=output/'definitions';directory.mkdir()
    channel=SceneChannel(create=True);process=None
    try:
        wire.initialize(channel);channel.write(12,struct.pack('<I',1));channel.write(wire.OFFSET+12,struct.pack('<I',os.getpid()))
        raw=(ROOT/source['source_packet']).read_bytes();header=struct.unpack_from('<32I',raw)
        source['session']=channel.name;source['source_binding']=dict(pid=os.getpid(),model=header[10],source=header[12])
        source['source_scope']='Explicit many-owner source replay; original geometry/images, synthetic independent instances'
        for image in source['images'].values():
            if not (directory/image['file']).exists():os.link(scene.parent/image['file'],directory/image['file'])
        originals=[];first_name=None
        for index in range(owners):
            d=copy.deepcopy(source);d['owner_epoch']+=index;d['asset']['revision']+=index*1000
            d['source_binding']['model']+=index*4096;d['source_binding']['source']+=index*8192
            d['frames']=d['frames'][:1];d['frames'][0]['owner']=d['owner_epoch'];d['frames'][0]['revision']=d['asset']['revision']
            name=f'{d["asset"]["content"]}-{d["owner_epoch"]}-{d["asset"]["revision"]}.json'
            if index:
                d['asset_reference']=first_name
                for field in ('positions','corners','indices','groups','images'):d.pop(field)
            else:first_name=name
            (directory/name).write_text(json.dumps(d));originals.append(d)
            # The real source packet's resource lineage is retained. These
            # descriptors belong only to the isolated synthetic replay session.
            images=sum(i['width']*i['height']*4 for i in source['images'].values())
            digest=int.from_bytes(bytes.fromhex(source['source_packet_sha256'])[:8],'little') or 1
            image_digest=int.from_bytes(bytes.fromhex(next(iter(source['images'].values()))['sha256'])[:8],'little') or 1
            descriptor=wire.ASSET.pack(index+1,index+1,d['owner_epoch'],d['asset']['revision'],d['source_binding']['model'],d['source_binding']['source'],len(raw),images,bytes.fromhex(d['asset']['content']),digest,image_digest,0)
            wire.publish(channel,index+1,descriptor[:-8]+struct.pack('<Q',fnv(descriptor[:-8])))
        channel.write(128,struct.pack('<I',owners))
        args=[str(runtime_exe(exe)),'-windowed','-ResX=1920','-ResY=1080','-nosound','-nolog',
              f'-SFCSourceMap={channel.name}',f'-SFCSourcePID={os.getpid()}',f'-SFCDefinitionDirectory={directory}',
              f'-SFCOutput={output}']
        if not normal:args+=['-SFCDiagnostics',f'-SFCRegistryTiming={frames}',f'-SFCRegistryTimingOwners={owners}']
        process=subprocess.Popen(args,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        deadline=time.monotonic()+120
        while not normal and not (output/'source-attached.json').exists():
            if process.poll() is not None:raise ValueError('Source renderer did not attach')
            if time.monotonic()>deadline:raise TimeoutError('Timing source attachment')
            time.sleep(.01)
        if not normal and not (output/'timing-started.json').exists():raise ValueError('Packaged UE timing mode is not active')
        side=math.ceil(math.sqrt(owners));counter=0;start=time.monotonic()
        while process.poll() is None and time.monotonic()<deadline:
            counter+=1;rows=[]
            for index,d in enumerate(originals):
                pose=copy.deepcopy(source['frames'][0]);pose['model'][0][3]+=(index%side-(side-1)/2)*22
                pose['model'][1][3]+=(index//side-(side-1)/2)*22
                pose['model'][0][3]+=math.sin(counter*.025)*2
                pose['view'][2][3]-=(side-1)*55
                row=source_row(d,pose,1000+counter,counter,index);publish_state(channel,row,index);rows.append(row)
            publish_frame(channel,rows,1000+counter,counter,offered=qpc());time.sleep(.001)
            if normal and time.monotonic()-start>=5:
                channel.write(wire.OFFSET+32,struct.pack('<I',1))
                process.wait(timeout=15);break
        if process.poll() is None:raise TimeoutError('Retained scene timing')
        if process.returncode:raise ValueError(f'UE exited with {process.returncode}')
        if normal:
            if time.monotonic()-start<5:raise ValueError('Normal consumer exited before the source stopped')
            files=[p.name for p in output.iterdir() if p.is_file()]
            if files:raise ValueError(f'Diagnostics-off consumer created recordings: {files}')
            report=dict(normal_exit=True,diagnostics=False,recordings=[],replay=True,producer_frames=counter,owners_offered=owners)
            (output/'qualified.json').write_text(json.dumps(report,indent=2));return report
        if (output/'rejected.txt').exists():raise ValueError((output/'rejected.txt').read_text())
        report=json.loads((output/'registry-timing.json').read_text())
        if report['samples']!=frames or report['owners']!=owners or report['geometry_builds']!=1 or report['actual_meshes']!=1:
            raise ValueError('Representative replay identity/geometry sharing')
        if list(output.glob('*.bgra')) or list(output.glob('*.bmp')):raise ValueError('Timing-only replay created image recordings')
        report.update(replay=True,producer_frames=counter,process_active_seconds=time.monotonic()-start)
        (output/'qualified.json').write_text(json.dumps(report,indent=2));return report
    finally:
        if process is not None and process.poll() is None:process.kill();process.wait()
        channel.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('exe','scene','output'):parser.add_argument(name,type=Path)
    parser.add_argument('--owners',type=int,default=6);parser.add_argument('--frames',type=int,default=180)
    parser.add_argument('--normal',action='store_true',help='Disable all UE diagnostics; stop the source after five seconds')
    args=parser.parse_args();result=run(args.exe,args.scene,args.output,args.owners,args.frames,args.normal)
    print(json.dumps({key:value for key,value in result.items() if key!='samples_ms'},indent=2))
