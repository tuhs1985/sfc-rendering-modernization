"""Qualify prepared multi-owner insertion; never claim a gameplay checkout."""
import argparse,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/remix_runtime'))
from additive_qualification import sources,digest
import native_cohort

def qualify(folders):
    files=sources();proofs=[];policies=[]
    for folder in folders:
        folder=folder.resolve();folder.relative_to(ROOT/'artifacts/remix-runtime/runs')
        r=json.loads((folder/'result.json').read_text());log=(folder/'fixture.log').read_text()
        g=r.get('native_gate') or {};h=g.get('header') or {}
        c=(r.get('live_owner_timing') or {}).get('native_cohort') or {}
        if not r.get('native_all_ships') or r['error'] or r['fixture_exit'] or r['host_exit']:raise ValueError('Multi-owner fixture incomplete')
        if g.get('measurement_frames')!=600 or g.get('error') or h.get('error') or h.get('partial') or h.get('dropped'):raise ValueError('Native gate evidence incomplete')
        if log.count('NATIVE_GATE_PIXELS mismatches=0')!=2 or not re.search(r'NATIVE_COHORT_END owners=3\b',log):raise ValueError('Actual independent pixels not proven')
        if not re.search(r'NATIVE_COHORT_PIXELS owners_with_pixels=[23]\b',log):raise ValueError('Two visible owners required')
        if len([x for x in c.get('owners',[]) if x['inserted'] and x['suppressed']])!=3:raise ValueError('Per-owner receipts incomplete')
        native=(folder/'gpu/job-console.log').read_text()
        expected=24 if r.get('legacy_startup_warmup',False) else 1
        if f'STARTUP_POLICY bootstrap_presents={expected} ' not in native:raise ValueError('Explicit startup policy evidence missing')
        summary=re.search(r'MULTISCENE_SUMMARY .*loads=(\d+) shared=(\d+)',native)
        if not summary or int(summary[1])!=2 or int(summary[2])<1:raise ValueError('Different geometry and shared geometry not exercised')
        for name in ('result.json','fixture.log','NATIVE-GATE-001.bin','NATIVE-GATE-001.json','NATIVE-COHORT-001.bin','NATIVE-COHORT-001.json','gpu/job-console.log'):
            files[(folder/name).relative_to(ROOT).as_posix()]=digest(folder/name)
        policies.append(r['native_insertion_policy']);proofs.append(dict(folder=folder.relative_to(ROOT).as_posix(),policy=r['native_insertion_policy'],owners=c,timing=g))
    out=native_cohort.RECEIPT.parent
    for arch in (32,64):
        if 'Native cohort wire PASS 17 checks' not in (out/f'wire{arch}.txt').read_text():raise ValueError('Membership tests missing')
    component=ROOT/'artifacts/player-replacement/native-gate-tests/m1_player_replacement_component_tests.txt'
    match=re.search(r'Player suppression recorder PASS checks=(\d+)',component.read_text())
    if not match or int(match[1])<50:raise ValueError('Actual multi-owner hooks not tested')
    p=(out/'python-tests.txt').read_text()
    if 'OK' not in p or 'FAILED' in p or 'Traceback' in p:raise ValueError('Python tests failed')
    for name in ('artifacts/remix-runtime/return-bin/SFCRemixReturn.dll','artifacts/remix-runtime/return-bin/d3d11_return_fixture.exe','artifacts/remix-runtime/return-bin/return_launcher.exe','artifacts/remix-runtime/return-bin/return_host.exe','artifacts/remix-runtime/native-light-tests/m1_light_component.dll','artifacts/d3d9-proof/receiver-bin/output_receiver.exe','artifacts/m1/bin/m1_gate.dll','artifacts/m1/bin/m1_controller.exe','tools/remix_runtime/config/rendering.toml','tools/remix_runtime/config/lights.toml','tools/d3d9_proof/offset_ship.toml'):
        files[name]=digest(ROOT/name)
    for path in (component,out/'wire32.txt',out/'wire64.txt',out/'python-tests.txt'):files[path.relative_to(ROOT).as_posix()]=digest(path)
    submission=ROOT/'artifacts/player-replacement/submission-tests'
    for arch in (32,64):
        for name,marker in ((f'd3d9_submission_policy_tests-{arch}.txt','Submission policy PASS 12 checks'),(f'remix_loaded_light_tests-{arch}.txt','Loaded light PASS ')):
            path=submission/name
            if marker not in path.read_text():raise ValueError('Nonblocking submission policy tests missing')
            files[path.relative_to(ROOT).as_posix()]=digest(path)
    worker=submission/'worker-result.json'
    if not json.loads(worker.read_text()).get('calibration_isolated'):raise ValueError('Diagnostic mirror isolation unproven')
    files[worker.relative_to(ROOT).as_posix()]=digest(worker)
    q=dict(result='NATIVE_COHORT_PREPARED',policies=sorted(set(policies)),files=files,evidence=proofs,scope='Standalone actual multi-owner GPU insertion qualified;gameplay checkout pending')
    native_cohort.RECEIPT.write_text(json.dumps(q,indent=2));print(q['result'],q['policies'])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('runs',type=Path,nargs='+');qualify(p.parse_args().runs)
