"""Actual native receiver gate driven by synthetic source rows; never launches SFC."""
import argparse,hashlib,json,os,struct,subprocess,sys,time
from pathlib import Path
from qualify_registry import ROOT,source_row,runtime_exe
for part in ('src/rendering/ue','src/rendering','src/transport','src/assets','src/runtime'):
    sys.path.insert(0,str(ROOT/part))
from scene_receiver import Receiver
from live_owner_timing import initialize
from runtime_context import CONTEXT
from native_output_service import AdditiveSourceService,additive_environment
import multi_scene as wire

QUALIFICATION=ROOT/'artifacts/ue-foundation/native-insertion/qualification.json'

def qualification_files():
    files=list((ROOT/'src/rendering/ue').glob('*.h'))
    files += [ROOT/path for path in (
        'src/rendering/ue/native_output_service.py','src/rendering/ue/source_service.py',
        'src/rendering/ue/source_reader.py','src/transport/source_scene_view.h','src/transport/source_target_view.h',
        'tools/d3d9_proof/game_output_wire.h','tools/d3d9_proof/game_output_writer.h',
        'tools/native_insertion/gate_contract.h','tools/native_insertion/gate_wait.h',
        'tools/remix_runtime/d3d9_game_receiver.h','tools/remix_runtime/ship_replacement_compositor.h',
        'tools/remix_runtime/return_addon.cpp','tools/m1_component/m1_component.cpp',
        'artifacts/ue-foundation/gpu-exchange/ue_output_receiver.exe',
        'artifacts/remix-runtime/return-bin/SFCRemixReturn.dll',
        'artifacts/remix-runtime/native-light-tests/m1_light_component.dll')]
    return {str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in files}

def require_native_qualification():
    q=json.loads(QUALIFICATION.read_text())
    if q.get('result')!='UE_ADDITIVE_NATIVE_GATE_QUALIFIED' or q.get('files')!=qualification_files():
        raise ValueError('UE additive native qualification is stale; rerun the standalone gate checkout')
    return q

def run(exe,scene,consumer,fixture,output):
    output=output.resolve();output.mkdir(parents=True,exist_ok=False)
    definition=json.loads(scene.read_text(encoding='utf-8-sig'))
    packet=ROOT/definition['source_packet'];mesh=packet.read_bytes();refs=packet.with_suffix('.json').read_bytes();header=struct.unpack_from('<64I',mesh)
    definition['source_binding']=dict(model=header[10],source=header[12])
    row=source_row(definition,definition['frames'][0],1,1,0)
    rows=output/'rows.bin';rows.write_bytes(struct.pack('<96I',*row))
    receiver=Receiver(retain_assets=False);native=None;service=None
    try:
        channel=receiver.channel;initialize(channel,persistent=True);wire.initialize(channel)
        channel.write(12,struct.pack('<I',1));channel.write(65536,mesh+refs)
        channel.write(256,struct.pack('<6I',1,0,len(mesh),len(refs),header[4],definition['asset']['revision']))
        env={k:v for k,v in os.environ.items() if not k.startswith('SFC_')};env=additive_environment(env)
        env.update(SFC_REMIX_CALIBRATION_SCENE=receiver.name,SFC_D3D9_MULTISCENE='1',SFC_D3D9_SOURCE_TIMING='1',SFC_D3D9_LIVE_TIMING='1',
                   SFC_D3D9_FIXTURE_ROWS=str(rows),SFC_PIPELINE_MODE='diagnostic',SFC_PLAY_SESSION='0')
        with (output/'native.log').open('wb') as log:
            native=subprocess.Popen([str(fixture.resolve()),str(output/'native')],env=env,stdout=log,stderr=subprocess.STDOUT)
            service=AdditiveSourceService(receiver,CONTEXT.game_root,native.pid,output/'service',runtime_exe(exe),consumer=consumer,
                                          world_offset=(-15.897722721099854,0,0),environment=env)
            args=service.arguments()+['-SFCDiagnostics',f'-SFCOutput={output}']
            service.process=subprocess.Popen(args,env=service.environment,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            deadline=time.monotonic()+70
            while native.poll() is None:
                if time.monotonic()>deadline:raise TimeoutError('Native gate fixture ceiling')
                try:service.poll()
                except ValueError:
                    if native.poll() is None and time.monotonic()<deadline:
                        # Native teardown marks the source stopped before its process exits.
                        if struct.unpack('<I',channel.read(wire.OFFSET+32,4))[0]:
                            native.wait(timeout=5);break
                    raise
                time.sleep(.001)
            service.stop()
        if native.returncode:raise RuntimeError((output/'native.log').read_text())
        report=json.loads((output/'native/result.json').read_text())
        report.update(scope='Standalone actual d3d9_game::Receiver Acquire/Commit; no SFC hook or gameplay',service=service.summary())
        report['files']=qualification_files()
        report['result']='UE_ADDITIVE_NATIVE_GATE_QUALIFIED'
        report['evidence']=str(output.relative_to(ROOT))
        (output/'qualified.json').write_text(json.dumps(report,indent=2))
        if 'Shipping' in str(exe):QUALIFICATION.write_text(json.dumps(report,indent=2))
        print(json.dumps({key:value for key,value in report.items() if key not in ('timing_ms','files')},indent=2))
    except Exception as exc:
        (output/'failure.json').write_text(json.dumps(dict(error=str(exc)),indent=2));raise
    finally:
        if native is not None and native.poll() is None:native.terminate();native.wait(timeout=5)
        if service:service.stop()
        receiver.close()

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('exe','scene','consumer','fixture','output'):p.add_argument(name,type=Path)
    a=p.parse_args();run(a.exe,a.scene,a.consumer,a.fixture,a.output)
