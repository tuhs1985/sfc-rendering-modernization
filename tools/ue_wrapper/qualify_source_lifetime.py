"""Actual packaged passive supervisor death/cancel and immediate relaunch; no SFC."""
import argparse
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import time
from qualify_registry import SceneChannel,wire,runtime_exe


def run(exe,output,*,consumer=None):
    output=output.resolve();output.mkdir(parents=True,exist_ok=False);results=[]
    for fault in ('cancel-passive','parent-death','cancel-passive','cancel-before-attach','cancel-before-pid'):
        folder=output/str(len(results));folder.mkdir();definitions=folder/'definitions';definitions.mkdir()
        source=SceneChannel(create=True);parent=process=None
        try:
            wire.initialize(source);source.write(12,struct.pack('<I',0 if fault=='cancel-before-attach' else 1));source.write(wire.OFFSET+12,struct.pack('<I',0 if fault.startswith('cancel-before-') else os.getpid()))
            parent=subprocess.Popen([sys.executable,'-c','import time; time.sleep(90)'],creationflags=subprocess.CREATE_NO_WINDOW)
            extra=[];environment=None
            if consumer:
                from native_output_service import additive_environment
                environment=additive_environment({k:v for k,v in os.environ.items() if not k.startswith('SFC_')})
                environment['SFC_REMIX_CALIBRATION_SCENE']=source.name
                extra=['-SFCNativeAdditive',f'-SFCGpuConsumer={consumer.resolve()}','-SFCWorldOffsetX=-15.897722721099854','-SFCWorldOffsetY=0','-SFCWorldOffsetZ=0']
            process=subprocess.Popen([str(runtime_exe(exe)),'-windowed','-ResX=640','-ResY=480','-nosound','-nolog',
                '-SFCDiagnostics',f'-SFCOutput={folder}',f'-SFCDefinitionDirectory={definitions}',
                f'-SFCSourceMap={source.name}',f'-SFCSourcePID={os.getpid()}',f'-SFCParentPID={parent.pid}']+extra,env=environment,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            deadline=time.monotonic()+45
            while not (folder/'source-attached.json').exists():
                if process.poll() is not None:raise ValueError('Packaged source failed before passive attachment')
                if time.monotonic()>deadline:raise TimeoutError('Passive source attach')
                time.sleep(.01)
            if fault=='parent-death':parent.terminate();parent.wait(timeout=5)
            else:source.write(wire.OFFSET+32,struct.pack('<I',1))
            if process.wait(timeout=15)!=0:raise ValueError('Passive source did not exit normally')
            if (folder/'rejected.txt').exists() or list(folder.glob('*.bgra')):raise ValueError('Passive teardown error/recording')
            results.append(dict(fault=fault,session=source.name,normal_exit=True,before_assets=True))
        finally:
            for child in (process,parent):
                if child is not None and child.poll() is None:child.terminate();child.wait(timeout=5)
            source.close()
    if len({r['session'] for r in results})!=len(results):raise ValueError('Relaunch reused source session')
    report=dict(results=results,no_sfc=True,additive=consumer is not None);(output/'qualified.json').write_text(json.dumps(report,indent=2));return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('exe',type=Path);p.add_argument('output',type=Path);p.add_argument('--consumer',type=Path);a=p.parse_args()
    if a.consumer:
        sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src/rendering/ue'))
    print(json.dumps(run(a.exe,a.output,consumer=a.consumer),indent=2))
