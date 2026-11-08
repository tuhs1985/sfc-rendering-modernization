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
        environment=json.loads((folder/'gpu/environment-preparation.json').read_text())
        if environment.get('version')!=1 or environment.get('offset')!=8192 or environment.get('bytes')!=1920:
            raise ValueError('Prepared environment bootstrap contract missing')
        if environment.get('config_sha256')!=digest(folder/'gpu/lights-config-accepted.toml').lower():
            raise ValueError('Prepared environment differs from accepted lighting')
        if environment.get('project_dome_prepared'):
            if 'PREPARED_ENVIRONMENT project_dome=1 commands_drained=1 retained=1' not in native or native.count('PREPARED_DOME_ADOPTED slot=2 recreated=0')!=1:
                raise ValueError('Actual prepared dome completion/one-time adoption not proven')
        elif 'PREPARED_ENVIRONMENT project_dome=0' not in native:
            raise ValueError('Explicit non-dome preparation evidence missing')
        if r.get('effect_light_fixture'):
            effect=re.search(r'EFFECT_LIGHT_SUMMARY frames=(\d+) active_slots=(\d+) invalid=(\d+) unavailable=(\d+) changes=(\d+) remaining=(\d+)',native)
            if not effect or not 0<int(effect[2])<int(effect[1]) or int(effect[3]) or int(effect[5])<2 or int(effect[6]):
                raise ValueError('Actual moving/pulsing effect-light runtime/cleanup evidence missing')
            for arch in (32,64):
                path=ROOT/f'artifacts/player-replacement/effect-light-tests/effect{arch}.txt'
                match=re.search(r'Effect lights PASS (\d+) checks',path.read_text())
                if not match or int(match[1])<30:raise ValueError('Native effect-light lifecycle checks missing')
                files[path.relative_to(ROOT).as_posix()]=digest(path)
            if r.get('light_diagnostics'):
                trace=json.loads((folder/'effect-light-submissions-summary.json').read_text())
                if trace.get('error') or not trace.get('records') or not trace.get('active_slot_observations') or trace.get('invalid_reads'):
                    raise ValueError('Effect light submission evidence incomplete')
                for name in ('effect-light-submissions.jsonl','effect-light-submissions-summary.json'):
                    files[(folder/name).relative_to(ROOT).as_posix()]=digest(folder/name)
        expected=24 if r.get('legacy_startup_warmup',False) else 1
        if f'STARTUP_POLICY bootstrap_presents={expected} ' not in native:raise ValueError('Explicit startup policy evidence missing')
        summary=re.search(r'MULTISCENE_SUMMARY .*loads=(\d+) shared=(\d+)',native)
        if not summary or int(summary[1])!=2 or int(summary[2])<1:raise ValueError('Different geometry and shared geometry not exercised')
        for name in ('result.json','fixture.log','NATIVE-GATE-001.bin','NATIVE-GATE-001.json','NATIVE-COHORT-001.bin','NATIVE-COHORT-001.json','gpu/job-console.log','gpu/environment-preparation.json'):
            files[(folder/name).relative_to(ROOT).as_posix()]=digest(folder/name)
        policies.append(r['native_insertion_policy']);proofs.append(dict(folder=folder.relative_to(ROOT).as_posix(),policy=r['native_insertion_policy'],owners=c,timing=g))
    out=native_cohort.RECEIPT.parent
    for arch in (32,64):
        match=re.search(r'Native cohort wire PASS (\d+) checks',(out/f'wire{arch}.txt').read_text())
        if not match or int(match[1])<193:raise ValueError('Membership/cache/callback tests missing')
    component=ROOT/'artifacts/player-replacement/native-gate-tests/m1_player_replacement_component_tests.txt'
    match=re.search(r'Player suppression recorder PASS checks=(\d+)',component.read_text())
    if not match or int(match[1])<50:raise ValueError('Actual multi-owner hooks not tested')
    p=(out/'python-tests.txt').read_text()
    if 'OK' not in p or 'FAILED' in p or 'Traceback' in p:raise ValueError('Python tests failed')
    for name in ('tools/remix_ingest/live_scene.py','artifacts/remix-runtime/return-bin/SFCRemixReturn.dll','artifacts/remix-runtime/return-bin/d3d11_return_fixture.exe','artifacts/remix-runtime/return-bin/return_launcher.exe','artifacts/remix-runtime/return-bin/return_host.exe','artifacts/remix-runtime/native-light-tests/m1_light_component.dll','artifacts/d3d9-proof/receiver-bin/output_receiver.exe','artifacts/m1/bin/m1_gate.dll','artifacts/m1/bin/m1_controller.exe','tools/remix_runtime/config/rendering.toml','tools/remix_runtime/config/lights.toml','tools/d3d9_proof/offset_ship.toml'):
        files[name]=digest(ROOT/name)
    for path in (component,out/'wire32.txt',out/'wire64.txt',out/'python-tests.txt',ROOT/'artifacts/remix-runtime/test-install/sfc-baseline.ini'):files[path.relative_to(ROOT).as_posix()]=digest(path)
    submission=ROOT/'artifacts/player-replacement/submission-tests'
    for arch in (32,64):
        for name,marker in ((f'd3d9_submission_policy_tests-{arch}.txt','Submission policy PASS 12 checks'),(f'remix_loaded_light_tests-{arch}.txt','Loaded light PASS ')):
            path=submission/name
            if marker not in path.read_text():raise ValueError('Nonblocking submission policy tests missing')
            files[path.relative_to(ROOT).as_posix()]=digest(path)
    worker=submission/'worker-result.json'
    if not json.loads(worker.read_text()).get('calibration_isolated'):raise ValueError('Diagnostic mirror isolation unproven')
    files[worker.relative_to(ROOT).as_posix()]=digest(worker)
    environment_tests=ROOT/'artifacts/player-replacement/environment-tests'
    for arch in (32,64):
        path=environment_tests/f'wire{arch}.txt'
        if 'Prepared environment PASS 14 checks' not in path.read_text():raise ValueError('Prepared environment native packet cases missing')
        files[path.relative_to(ROOT).as_posix()]=digest(path)
    hull=ROOT/'artifacts/d3d9-proof/direct64-bin/physical-hull-depth-tests.txt'
    if 'draws=256' not in hull.read_text() or 'Physical hull GPU PASS' not in hull.read_text():raise ValueError('Full admitted-scene hull GPU coverage missing')
    files[hull.relative_to(ROOT).as_posix()]=digest(hull)
    q=dict(result='NATIVE_COHORT_PREPARED',policies=sorted(set(policies)),files=files,evidence=proofs,scope='Standalone actual multi-owner GPU insertion qualified;gameplay checkout pending')
    native_cohort.RECEIPT.write_text(json.dumps(q,indent=2));print(q['result'],q['policies'])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('runs',type=Path,nargs='+');qualify(p.parse_args().runs)
