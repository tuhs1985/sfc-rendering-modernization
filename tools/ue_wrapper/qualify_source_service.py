"""Actual source transfers -> neutral prep -> UE catalogue consumer; no SFC."""
import argparse
import copy
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import time
from qualify_registry import ROOT,source_row,publish_frame,publish_state,runtime_exe
for part in ('src/rendering/ue','src/transport','src/assets','src/runtime'):
    sys.path.insert(0,str(ROOT/part))
from scene_receiver import Receiver
from source_service import SourceService
from live_owner_timing import initialize
from runtime_context import CONTEXT
import multi_scene as wire
from qualify_registry_timing import qpc


def run(exe,scene,output):
    output=output.resolve();output.mkdir(parents=True,exist_ok=False)
    definition=json.loads(scene.read_text());packet=ROOT/definition['source_packet']
    mesh=packet.read_bytes();refs=packet.with_suffix('.json').read_bytes()
    header=struct.unpack_from('<64I',mesh)
    receiver=Receiver(retain_assets=False);service=None
    try:
        c=receiver.channel;initialize(c,persistent=True);wire.initialize(c)
        c.write(12,struct.pack('<I',1));c.write(wire.OFFSET+12,struct.pack('<I',os.getpid()))
        revision=definition['asset']['revision'];c.write(65536,mesh+refs)
        c.write(256,struct.pack('<6I',1,0,len(mesh),len(refs),header[4],revision))
        definition['session']=c.name;definition['source_binding']=dict(pid=os.getpid(),model=header[10],source=header[12])
        service=SourceService(receiver,CONTEXT.game_root,os.getpid(),output/'service',runtime_exe(exe))
        service.process=subprocess.Popen([str(runtime_exe(exe)),'-windowed','-ResX=1920','-ResY=1080','-nosound','-nolog',
            '-SFCDiagnostics',f'-SFCOutput={output}',f'-SFCDefinitionDirectory={service.publisher.folder}',
            f'-SFCSourceMap={c.name}',f'-SFCSourcePID={os.getpid()}',f'-SFCParentPID={os.getpid()}',
            '-SFCRegistryTiming=20','-SFCRegistryTimingOwners=1'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        counter=0;deadline=time.monotonic()+60
        while service.process.poll() is None:
            if time.monotonic()>deadline:raise TimeoutError('Source service to packaged UE')
            counter+=1;pose=copy.deepcopy(definition['frames'][0]);pose['model'][0][3]+=(counter%3)*2
            row=source_row(definition,pose,1000+counter,counter,0);publish_state(c,row,0);c.write(128,struct.pack('<I',1))
            publish_frame(c,[row],1000+counter,counter,offered=qpc())
            try:service.poll()
            except RuntimeError:
                if not (output/'registry-timing.json').exists():raise
                break
            time.sleep(.005)
        service.process.wait(timeout=10)
        if service.process.returncode or (output/'rejected.txt').exists():raise ValueError('Packaged source service failed')
        result=json.loads((output/'registry-timing.json').read_text())
        if result['samples']!=20 or result['geometry_builds']!=1 or service.published!={revision}:raise ValueError('Fresh transfer admission/geometry reuse')
        if c.read(260,4)!=struct.pack('<I',1) or receiver.assets:raise ValueError('Source transfer was not acknowledged/transferred exactly once')
        fresh=json.loads(next(service.publisher.folder.glob('*.json')).read_text())
        for key in ('positions','corners','indices'):
            if fresh[key]!=definition[key]:raise ValueError('Fresh source geometry changed')
        result=dict(service.summary(),samples=20,geometry_builds=1,actual_source_transfer=True,images_unchanged=True,
            scheduling_anchor=service.anchor,source_pid=os.getpid(),session=c.name)
        (output/'qualified.json').write_text(json.dumps(result,indent=2));return result
    finally:
        if service:service.stop()
        receiver.close()


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for field in ('exe','scene','output'):p.add_argument(field,type=Path)
    a=p.parse_args();print(json.dumps(run(a.exe,a.scene,a.output),indent=2))
