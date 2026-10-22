"""Bounded native-light evidence summary and dedicated observer qualification."""
from pathlib import Path
import hashlib
import json
from native_light_state import decode, SIZE

ROOT=Path(__file__).resolve().parents[2]
BIN=ROOT/'artifacts/remix-runtime/native-light-tests'
RECEIPT=BIN/'qualification.json'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sources():
    base=ROOT/'tools/m1_component'
    paths=list(base.glob('*.h'))+list(base.glob('*.cpp'))
    paths += [base/'build_light_discovery.ps1',base/'build_native_light_tests.ps1',base/'native_light_component.def',ROOT/'tests/m1_live_scene_tests.cpp',ROOT/'tests/m1_mesh_export_tests.cpp',ROOT/'tests/native_light_snapshot_tests.cpp',
              ROOT/'tests/native_light_observer_tests.cpp',Path(__file__),
              ROOT/'tools/remix_runtime/native_light_state.py',
              ROOT/'tools/remix_runtime/run_return_game.py',
              ROOT/'tools/remix_runtime/start_return_image_session.ps1',
              ROOT/'tools/remix_runtime/start_light_discovery_session.ps1']
    return {str(p.relative_to(ROOT)):digest(p) for p in sorted(set(paths))}


def require_qualification():
    q=json.loads(RECEIPT.read_text())
    if q.get('result')!='OFFLINE_NATIVE_LIGHT_DISCOVERY_QUALIFIED' or q.get('sources')!=sources() or q.get('component_sha256')!=digest(BIN/'m1_light_component.dll'):
        raise ValueError('Native light discovery qualification stale/missing')
    return q


def analyze(path):
    path=Path(path)
    size=path.stat().st_size
    if not size or size%SIZE or size>900*SIZE:
        raise ValueError('Native lights missing,partial or beyond 900-record bound')
    banks={};session=None;previous=0;owners=set();frames=set()
    with path.open('rb') as file:
        while raw:=file.read(SIZE):
            r=decode(raw)
            if session is None:session=r['session_words']
            if r['session_words']!=session or r['sequence']<=previous:
                raise ValueError('Native light cross-session/nonmonotonic record')
            previous=r['sequence'];owners.add(r['owner_epoch']);frames.add(r['frame'])
            key=str(r['manager_process_local'])
            if key not in banks:
                if len(banks)>=8:raise ValueError('Native light bank identity bound8')
                banks[key]=dict(samples=0,owners=set(),gate_values=set(),prefix_values=set(),slots={})
            bank=banks[key];bank['samples']+=1;bank['owners'].add(r['owner_epoch'])
            bank['gate_values'].add(r['global_gate_raw']);bank['prefix_values'].add(r['consumed_prefix'])
            for slot in r['slots']:
                i=str(slot['slot']);old=bank['slots'].get(i)
                changed=old is not None and (old['last']['raw_words']!=slot['raw_words'] or old['last']['enabled_byte']!=slot['enabled_byte'])
                item=bank['slots'].setdefault(i,dict(changes=0,ever_enabled=False,ever_consumed=False,nonfinite=0,last=None))
                item['changes']+=int(changed);item['ever_enabled']|=bool(slot['enabled_byte']);item['ever_consumed']|=slot['consumed_by_native_response']
                item['nonfinite']+=slot['values'] is None;item['last']=slot
    for bank in banks.values():
        for name in ('owners','gate_values','prefix_values'):bank[name]=sorted(bank[name])
    return dict(result='RAW_NATIVE_LIGHT_OBSERVATIONS_CAPTURED',records=size//SIZE,bytes=size,
        sha256=digest(path),session_words=session,owner_epochs=sorted(owners),distinct_frames=len(frames),banks=banks,
        interpretation='Slot numbers and native types only;no sun/weapon/physical intensity or Remix-light qualification yet')


def qualify():
    import os
    import subprocess as sp
    import time
    import uuid
    from present_calibration import Receiver
    receiver=Receiver()
    directory=BIN/('scene-'+uuid.uuid4().hex);directory.mkdir()
    env={**os.environ,'SFC_NATIVE_LIGHT_DISCOVERY':'1'}
    env.pop('SFC_REMIX_CALIBRATION_SCENE',None)
    process=None
    try:
        process=sp.Popen([str(BIN/'scene_observer.exe'),receiver.name,str(directory)],env=env,
            stdout=sp.PIPE,stderr=sp.STDOUT,creationflags=sp.CREATE_NO_WINDOW)
        limit=time.monotonic()+10
        while process.poll() is None:
            if time.monotonic()>limit:
                process.terminate();process.wait(timeout=5);raise ValueError('Native observer scene test10s limit')
            receiver.drain();time.sleep(.01)
        text=process.communicate()[0];(directory/'test.txt').write_bytes(text)
        (directory/'exit.json').write_text(json.dumps(dict(exit=process.returncode)))
        if process.returncode:raise ValueError('Native observer scene/worker integration failed')
        scene=analyze(directory/'native-lights.bin')
        summary=json.loads((directory/'native-lights-summary.json').read_text())
        if scene['owner_epochs']!=[1,2] or summary['queued'] or summary['io_failed'] or summary['written']!=scene['records']:
            raise ValueError('Actual observer worker drain/identity failed')
    finally:
        if process and process.poll() is None:process.terminate();process.wait(timeout=5)
        receiver.close()
    # Build script already ran both actual fixed-queue binaries and core tests.
    tuning=BIN/('tuning-'+uuid.uuid4().hex);tuning.mkdir()
    receiver=Receiver()
    try:
        test=sp.run([str(BIN/'scene_observer.exe'),receiver.name,str(tuning)],
            env={**env,'SFC_LIGHT_TUNING':'1'},stdout=sp.PIPE,stderr=sp.STDOUT,timeout=10,
            creationflags=sp.CREATE_NO_WINDOW)
        (tuning/'test.txt').write_bytes(test.stdout)
        if test.returncode:raise ValueError('Tuning scene worker failed')
        latest=list(tuning.glob('native-light-latest-*.bin'))
        if len(latest)!=2 or any(p.stat().st_size!=SIZE for p in latest):raise ValueError('Tuning latest-only storage invalid')
        if max(decode(p.read_bytes())['elapsed_ms'] for p in latest)<100000:raise ValueError('Tuning stopped at90seconds')
    finally:receiver.close()
    # Exercise the actual scene worker's raw shared-memory publication, not only
    # a transport round trip or diagnostic file decoder. No game is launched.
    from live_owner_timing import initialize as init_owner
    from light_transport import initialize as init_lights,read_native
    shared_dir=BIN/('shared-'+uuid.uuid4().hex);shared_dir.mkdir()
    receiver=Receiver();init_owner(receiver.channel);init_lights(receiver.channel)
    shared_seen={};process=None
    try:
        shared_env={**env,'SFC_LIGHT_TUNING':'1','SFC_REMIX_CALIBRATION_SCENE':receiver.name,
            'SFC_D3D9_SOURCE_TIMING':'1','SFC_D3D9_LIVE_TIMING':'1',
            'SFC_D3D9_GAME_OUTPUT':'1','SFC_D3D9_SHARED_LIGHTS':'1'}
        process=sp.Popen([str(BIN/'scene_observer.exe'),receiver.name,str(shared_dir)],env=shared_env,
            stdout=sp.PIPE,stderr=sp.STDOUT,creationflags=sp.CREATE_NO_WINDOW)
        limit=time.monotonic()+10
        while process.poll() is None:
            if time.monotonic()>limit:raise ValueError('Shared native worker10s limit')
            receiver.drain()
            for owner in (1,2):
                sample=read_native(receiver.channel,owner,process.pid)
                if sample:
                    raw,captured=sample;decoded=decode(raw)
                    if decoded['owner_epoch']!=owner or captured<=0:raise ValueError('Shared native provenance')
                    shared_seen[owner]=dict(captured_qpc=captured,sha256=hashlib.sha256(raw).hexdigest())
            time.sleep(.002)
        (shared_dir/'test.txt').write_bytes(process.communicate()[0])
        if process.returncode or sorted(shared_seen)!=[1,2]:raise ValueError('Actual shared native worker publication failed')
        if receiver.channel.read(15*1024*1024+32,4)!=b'\x01\0\0\0':raise ValueError('Shared worker not stopped before unmap')
        (shared_dir/'shared.json').write_text(json.dumps(shared_seen,indent=2))
    finally:
        if process and process.poll() is None:process.terminate();process.wait(timeout=5)
        receiver.close()
    checks=[]
    for arch in ('32','64'):
        log=(BIN/f'observer{arch}.txt').read_text()
        if 'NATIVE_LIGHT_OBSERVER_PASS checks=17' not in log:raise ValueError('Observer native tests missing')
        evidence=analyze(BIN/f'observer{arch}.bin')
        if evidence['records']!=8 or evidence['owner_epochs']!=[1,2]:raise ValueError('Observer output decoder mismatch')
        checks.append(dict(arch=arch,output=evidence['sha256'],records=8))
    q=dict(result='OFFLINE_NATIVE_LIGHT_DISCOVERY_QUALIFIED',sources=sources(),
        component_sha256=digest(BIN/'m1_light_component.dll'),checks=checks,
        scene_worker=dict(records=scene['records'],sha256=scene['sha256'],evidence=str(directory.relative_to(ROOT))),
        shared_worker=dict(owners=sorted(shared_seen),evidence=str(shared_dir.relative_to(ROOT)),stopped_before_unmap=True),
        limits=dict(hz_per_owner=5,owners=2,records=900,bytes=900*SIZE),sfc_launched=False)
    RECEIPT.write_text(json.dumps(q,indent=2));require_qualification()
    print('Native light discovery native queue/decoder qualification PASS')


if __name__=='__main__':qualify()
