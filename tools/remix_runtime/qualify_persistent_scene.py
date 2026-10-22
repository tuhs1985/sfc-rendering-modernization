"""Bounded persistent-mode worker/source/ABI preparation;not gameplay PASS."""
import hashlib
import json
import os
from pathlib import Path
import subprocess as sp
import sys
import uuid
from present_calibration import Receiver,ROOT
from live_owner_timing import initialize

BASE=ROOT/'artifacts/d3d9-proof/persistent-tests'
RECEIPT=BASE/'qualification.json'
SOURCES=('tools/scene_bridge/persistent_scene.h','tools/scene_bridge/simulation_pose.py',
    'tools/m1_component/m1_component.cpp','tools/m1_component/m1_contract.h','tools/m1_component/m1_live_scene.h',
    'tools/d3d9_proof/live_owner_wire.h','tools/d3d9_proof/live_light_binding.py','tools/remix_runtime/live_owner_timing.py',
    'tools/remix_runtime/run_return_game.py','tools/remix_runtime/start_return_image_session.ps1',
    'tools/d3d9_proof/start_d3d9_persistent_scene_session.ps1','tests/m1_persistent_scene_tests.cpp',
    'tests/persistent_scene_tests.cpp','tests/test_simulation_pose.py','tools/remix_runtime/qualify_persistent_scene.py')
BINS=('artifacts/remix-runtime/native-light-tests/m1_light_component.dll','artifacts/d3d9-proof/direct64-bin/d3d9_direct_host.exe',
    'artifacts/remix-runtime/return-bin/SFCRemixReturn.dll','artifacts/d3d9-proof/persistent-tests/native_scene.exe')
def hashes(names):return {n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in names}
def require_qualification():
    q=json.loads(RECEIPT.read_text())
    if q.get('result')!='OFFLINE_PERSISTENT_SCENE_PREPARED' or q.get('sources')!=hashes(SOURCES) or q.get('binaries')!=hashes(BINS):
        raise ValueError('Persistent scene qualification stale/missing;no game launch')
    return q
def qualify(fixture):
    sys.path.insert(0,str(ROOT/'tools/m1_component'));import verify_m1_c01_shading_bytes as check
    anchors={0x00796f0c:'8F 4B 41 00',0x00414b92:'E8 2A 0D 00 00',0x00414b97:'F6 44 24 08 01',
        0x00414b9f:'E8 1C A3 31 00',0x004158c1:'B8 13 BB 75 00',0x0069c944:'D8 41 0C',
        0x0069c29f:'D9 80 04 C0 C6 00',0x0069c2a5:'D9 80 04 A0 C6 00'}
    previous=check.ANCHORS
    try:check.ANCHORS=anchors;static=check.verify(Path(r'C:\Project\SFC-Remix-Return-Test\StarFleetOP.exe'))
    finally:check.ANCHORS=previous
    directory=BASE/('worker-'+uuid.uuid4().hex);directory.mkdir();receiver=Receiver()
    try:
        initialize(receiver.channel,persistent=True)
        env={**os.environ,'SFC_PERSISTENT_SCENE':'1','SFC_REMIX_CALIBRATION_SCENE':receiver.name,
            'SFC_D3D9_SOURCE_TIMING':'1','SFC_D3D9_LIVE_TIMING':'1'}
        for name in ('SFC_NATIVE_LIGHT_DISCOVERY','SFC_D3D9_SHARED_LIGHTS','SFC_D3D9_GAME_OUTPUT'):env.pop(name,None)
        run=sp.run([str(BASE/'native_scene.exe'),receiver.name,str(directory)],env=env,
            stdout=sp.PIPE,stderr=sp.STDOUT,timeout=10,creationflags=sp.CREATE_NO_WINDOW)
        (directory/'test.txt').write_bytes(run.stdout)
        if run.returncode or b'frames=120 captures=1 instance_generations=1 offscreen=120' not in run.stdout:
            raise ValueError('Actual persistent native source/worker test failed;see '+str(directory))
        worker=json.loads((directory/'PERSISTENT-SCENE-001.json').read_text())
        if worker['admitted']!=1 or worker['destroyed']!=1 or worker['offscreen_updates']!=120 or worker['publications']!=120 or worker['failed_updates']:
            raise ValueError('Persistent native registry accounting mismatch')
    finally:receiver.close()
    for arch in ('32','64'):
        if 'PASS 18 checks' not in (BASE/f'persistent{arch}.txt').read_text():raise ValueError('Persistent core architecture test missing')
    fixture=Path(fixture).resolve();fixture.relative_to(ROOT/'artifacts/remix-runtime/runs')
    result=json.loads((fixture/'result.json').read_text())
    from live_owner_timing import HEADER
    version=HEADER.unpack_from((fixture/'D3D9-LIVE-TIMING-001.bin').read_bytes())[1]
    if not result.get('persistent_wire_fixture') or version!=2 or result.get('error') or not result['live_owner_timing']['normal_owned_exit']:
        raise ValueError('Actual version2 ordinary-D3D9/Remix GPU return fixture required')
    from additive_qualification import qualify as qualify_gpu
    gpu=qualify_gpu(fixture,persist=not result.get('synchronized_buffer_fixture',False))
    RECEIPT.write_text(json.dumps(dict(result='OFFLINE_PERSISTENT_SCENE_PREPARED',sources=hashes(SOURCES),binaries=hashes(BINS),
        native_worker=str(directory.relative_to(ROOT)),worker=worker,static=static,sfc_launched=False,
        version2_gpu_fixture=str(fixture.relative_to(ROOT)),delivery_draws=gpu['delivery_draws'],delivery_frames=gpu['delivery_frames'],
        limitations=['Native destroy detour runtime still requires corroboration','Player display uses existing single-resident-asset backend','No aggregate TRL or seamless-gameplay PASS']),indent=2))
    require_qualification();print('Persistent native full-rate pose/camera/registry/removal preparation PASS')
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--fixture',required=True)
    qualify(parser.parse_args().fixture)
