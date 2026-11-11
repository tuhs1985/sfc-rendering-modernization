"""Default-off isolated damage-layer observation, reusing qualified supervision."""
import argparse
import ctypes as C
import datetime as dt
import json
from pathlib import Path
import subprocess as sp
import sys
import importlib.util

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/early_model_probe'))
spec=importlib.util.spec_from_file_location('early_runner',ROOT/'tools/early_model_probe/run_probe.py')
early=importlib.util.module_from_spec(spec);spec.loader.exec_module(early)
sys.path.insert(0,str(Path(__file__).resolve().parent))
from damage_capture import analyze,digest
OUT=ROOT/'artifacts/render-survey/damage-probe'
COMPONENT=OUT/'bin/damage_component.dll'
FIXTURE=OUT/'bin/damage_native_tests.exe'
PROBE='DAMAGE-LAYER-001'

def locks():
    paths=[p for name in ('damage_probe','early_model_probe') for p in (ROOT/'tools'/name).rglob('*') if p.is_file() and p.suffix in ('.inl','.h','.cpp','.py','.ps1')]
    paths += [COMPONENT,FIXTURE,early.BIN/'return_launcher.exe',early.BIN/'return_host.exe']
    paths += [ROOT/'tools/remix_runtime'/name for name in ('return_wire.h','return_channel.py','run_return_game.py','broad_capture.py')]
    paths += [ROOT/'docs/reconnaissance/evidence/20261103-damage-texture-path.json']
    paths += [ROOT/'artifacts/remix-runtime/deps/detours/Detours-e4bfd6b03e50de46b47abfbd1e46b384f0c5f833'/name for name in ('include/detours.h','lib.X86/detours.lib')]
    paths += list((ROOT/'src/session').glob('*.py'))
    return {p.relative_to(ROOT).as_posix():digest(p) for p in paths}

def observe(fixture=False):
    work,result=early.run(fixture,component=COMPONENT,output_name='damage.bin',analyze_trace=analyze,probe=PROBE,fixture_binary=FIXTURE,qualification_locks=locks,run_prefix='damage-',
        instructions='Use the familiar F-CA skirmish. Let hull damage develop (shield hits alone are not enough); use faster game speed if useful. Briefly rotate the camera once damage appears. No need to destroy your ship. Exit after the two-beep request; 90 seconds starts in tactical play.')
    inventory=ROOT/'docs/reconnaissance/evidence/20261103-damage-texture-path.json'
    (work/'damage-resource-inventory.json').write_bytes(inventory.read_bytes())
    print(result['report']['result'], ':',len(result['report']['mappings']),'damage mappings; issues:',result['report']['issues'],flush=True)
    return work,result

def main():
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group();g.add_argument('--execute',action='store_true');g.add_argument('--qualify',action='store_true');a=p.parse_args()
    early.preflight();early.budget()
    if a.qualify:
        work=OUT/('offline-'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f'));work.mkdir(parents=True)
        env={k:v for k,v in __import__('os').environ.items() if not k.startswith(('SFC_EARLY_','SFC_REMIX_'))}
        t=sp.run([str(FIXTURE),str(work/'damage.bin')],cwd=work,env=env,capture_output=True,text=True,timeout=25)
        (work/'native.log').write_text(t.stdout+t.stderr)
        if t.returncode or 'Damage native PASS' not in t.stdout:raise ValueError('Damage native fixture failed: '+t.stdout+t.stderr)
        report=analyze(work/'damage.bin');(work/'review.json').write_text(json.dumps(report,indent=2))
        if report['issues'] or not report['fixture'] or len(report['mappings'])!=2:raise ValueError('Damage fixture evidence incomplete: '+str(report['issues']))
        injected,result=observe(True)
        if result['report']['issues'] or not result['normal_exit'] or result['host_exit'] or len(result['report']['mappings'])!=2:raise ValueError('Actual injected damage fixture failed')
        q=dict(probe=PROBE,result='DAMAGE_NATIVE_AND_INJECTED_FIXTURE_PASS',locks=locks(),native=str(work.relative_to(ROOT)),injected=str(injected.relative_to(ROOT)),native_result_sha256=digest(work/'review.json'),injected_result_sha256=digest(injected/'result.json'))
        (OUT/'qualification.json').write_text(json.dumps(q,indent=2));print(q['result']);return
    q=json.loads((OUT/'qualification.json').read_text())
    if q['locks']!=locks() or q['result']!='DAMAGE_NATIVE_AND_INJECTED_FIXTURE_PASS':raise ValueError('Damage observer qualification missing/stale')
    if not a.execute:print('Damage observer preflight PASS. No game or renderer started.');return
    if not C.WinDLL('shell32').IsUserAnAdmin():raise ValueError('Use the established elevated parent; no routine UAC requested')
    observe()

if __name__=='__main__':main()
