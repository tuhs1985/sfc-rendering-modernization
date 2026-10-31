"""Freeze native insertion comparison preparation,never a gameplay success claim."""
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/remix_runtime'))
import native_gate
from additive_qualification import sources,digest

def qualify(baseline,strict,extra):
    files=sources();proofs=[];endpoint_binaries=None
    for folder,policy,base in ((baseline,'Strict',True),(strict,'Strict',False),(extra,'ExtraFrame',False)):
        folder=folder.resolve();folder.relative_to(ROOT/'artifacts/remix-runtime/runs')
        r=json.loads((folder/'result.json').read_text());g=r.get('native_gate') or {};h=g.get('header') or {}
        if endpoint_binaries is None:endpoint_binaries=r['source_files']
        elif endpoint_binaries!=r['source_files']:raise ValueError('Comparison endpoint binaries differ')
        if r['error'] or r['fixture_exit'] or r['host_exit'] or r['native_insertion_policy']!=policy or r['native_insertion_baseline']!=base:raise ValueError('Incomplete comparison run: '+str(folder))
        if g.get('measurement_frames')!=600 or g.get('error') or h.get('dropped') or h.get('partial') or h.get('error') or h.get('max_active',0)>1:raise ValueError('Gate evidence/lifetime bounds')
        log=(folder/'fixture.log').read_text()
        if 'NATIVE_GATE_END frames=600' not in log or 'state_errors=0' not in log:raise ValueError('Fixture completion/state evidence')
        if not base and (log.count('NATIVE_GATE_PIXELS mismatches=0')!=2 or not g.get('commits') or not g.get('injected_overruns')):raise ValueError('Genuine insertion pixels/delays not exercised')
        if g.get('maximum_slot_occupancy',3)>2:raise ValueError('Output pool exceeded two slots')
        for name in ('result.json','fixture.log','NATIVE-GATE-001.bin','NATIVE-GATE-001.json'):
            path=folder/name;files[path.relative_to(ROOT).as_posix()]=digest(path)
        proofs.append(dict(folder=folder.relative_to(ROOT).as_posix(),policy=policy,baseline=base,timing=g))
    out=native_gate.RECEIPT.parent
    for arch in (32,64):
        if 'Native gate core PASS 1216 checks' not in (out/f'core{arch}.txt').read_text():raise ValueError('Core native deadline tests incomplete')
        if 'Replacement offline PASS 85 checks' not in (ROOT/f'artifacts/remix-runtime/replacement-bin/replacement{arch}.stdout.txt').read_text():raise ValueError('Native compositor tests incomplete')
    if 'Pinned native flush PASS 12300 checks' not in (out/'flush.txt').read_text():raise ValueError('Native flush ABI incomplete')
    component=out/'m1_player_replacement_component_tests.txt'
    if 'Player suppression recorder PASS checks=36' not in component.read_text():raise ValueError('Actual capture/coordinator tests incomplete')
    python_log=(out/'python-tests.txt').read_text()
    if 'OK' not in python_log or 'FAILED' in python_log or 'Traceback' in python_log:raise ValueError('Python regression checks incomplete')
    names=['artifacts/remix-runtime/return-bin/SFCRemixReturn.dll','artifacts/remix-runtime/return-bin/d3d11_return_fixture.exe',
        'artifacts/remix-runtime/return-bin/return_launcher.exe','artifacts/remix-runtime/return-bin/return_host.exe',
        'artifacts/remix-runtime/native-light-tests/m1_light_component.dll','artifacts/m1/bin/m1_gate.dll','artifacts/m1/bin/m1_controller.exe',
        'artifacts/d3d9-proof/receiver-bin/output_receiver.exe','artifacts/player-replacement/native-gate-tests/m1_player_replacement_component_tests.exe',
        'artifacts/player-replacement/native-gate-tests/m1_player_replacement_component_tests.txt','artifacts/player-replacement/native-gate-tests/python-tests.txt',
        'tools/remix_runtime/config/rendering.toml','tools/remix_runtime/config/lights.toml','tools/d3d9_proof/offset_ship.toml']
    for arch in (32,64):names += [f'artifacts/player-replacement/native-gate-tests/core{arch}.exe',f'artifacts/player-replacement/native-gate-tests/core{arch}.txt',f'artifacts/remix-runtime/replacement-bin/replacement{arch}.stdout.txt']
    names+=['artifacts/player-replacement/native-gate-tests/flush.exe','artifacts/player-replacement/native-gate-tests/flush.txt']
    for name in names:files[name]=digest(ROOT/name)
    q=dict(result='NATIVE_GATE_COMPARISON_PREPARED',policies=['Strict','ExtraFrame'],files=files,evidence=proofs,
        scope='Offline qualification only. Both policies need sponsor gameplay. No shield replay,late composition or shared-GPU-fence scheduling.',
        sfc_launched=False,reference_period_ms=1000/60,output_bytes_max=128*1024*1024,log_bytes_max=32*1024*1024,evidence_bytes_max=20000000000)
    native_gate.RECEIPT.write_text(json.dumps(q,indent=2));native_gate.require_qualification('Strict');native_gate.require_qualification('ExtraFrame')
    print('Native insertion comparison prepared;actual SFC checkout remains required')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--strict',type=Path,required=True);p.add_argument('--extra',type=Path,required=True);a=p.parse_args();qualify(a.baseline,a.strict,a.extra)
