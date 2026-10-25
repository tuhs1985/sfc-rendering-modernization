"""Default-off early native model timing; no SFC without explicit --execute."""
import argparse
import ctypes as C
import datetime as dt
import json
import os
from pathlib import Path
import re
import shutil
import subprocess as sp
import sys
import time
from capture import analyze,header_at,digest
from supervision import wait_for

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/remix_runtime'))
from return_channel import Channel,valid_name
from run_return_game import preflight,critical_hashes,launcher_paths,compat_flags,game_running,image_path,wait_component_ready,SOURCE,TEST,CLIENT,BIN
OUT=ROOT/'artifacts/render-survey/early-model-probe'
COMPONENT=OUT/'bin/early_component.dll'

def locks():
    paths=[p for p in (ROOT/'tools/early_model_probe').rglob('*') if p.is_file() and p.suffix in ('.h','.cpp','.py','.ps1')]
    paths += [COMPONENT,OUT/'bin/early_native_tests.exe']
    paths += [ROOT/'tools/remix_runtime'/n for n in ('return_wire.h','return_channel.py','run_return_game.py')]
    paths += [BIN/n for n in ('return_launcher.exe','return_host.exe')]
    detours=ROOT/'artifacts/remix-runtime/deps/detours/Detours-e4bfd6b03e50de46b47abfbd1e46b384f0c5f833'
    paths += [detours/'include/detours.h',detours/'lib.X86/detours.lib']
    return {p.relative_to(ROOT).as_posix():digest(p) for p in paths}

def budget():
    sys.path.insert(0,str(ROOT/'tools/d3d9_proof'))
    from run_offline import storage
    extra=sum(p.stat().st_size for name in ('effect-probe','render-survey','remix-api-proof') for p in (ROOT/'artifacts'/name).rglob('*') if p.is_file())
    reserve=112*1024**2
    if storage()+extra+reserve>20_000_000_000 or shutil.disk_usage(ROOT).free<reserve:raise ValueError('Early-model20GB aggregate/source/archive admission')

def run(fixture=False):
    preflight();budget()
    if game_running():raise ValueError('Close the existing SFC normally before this isolated observer')
    work=ROOT/'artifacts/remix-runtime/runs'/('early-'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f'));work.mkdir()
    original=critical_hashes(SOURCE);copied=critical_hashes(TEST);settings=launcher_paths();frozen=locks()
    logs=[];host=launcher=None;channel=None;error=None;normal=False;pid=0
    start=time.monotonic();deadline=start+285
    supervision={'snapshot_checks':0}
    def log(n):
        f=(work/n).open('w');logs.append(f);return f
    def enforce():
        if time.monotonic()>deadline:raise RuntimeError('Prepared285second workflow bound')
        if sum(p.stat().st_size for p in work.rglob('*') if p.is_file())>48*1024**2:raise RuntimeError('16MiB trace plus32MiB ancillary cap')
    def wait(predicate,seconds,message):
        def snapshot():
            supervision['snapshot_checks']+=1
            return channel.snapshot()
        wait_for(predicate,seconds,message,deadline=deadline,enforce=enforce,
                 snapshot=snapshot if channel else None,poll=launcher.poll if launcher else None)
    try:
        shutil.copyfile(COMPONENT,work/'early_component.dll')
        host=sp.Popen([str(BIN/'return_host.exe'),'--observe-only'],cwd=work,stdout=log('host.log'),stderr=sp.STDOUT,creationflags=sp.CREATE_NO_WINDOW)
        wait(lambda:any(l.startswith('SESSION ') for l in (work/'host.log').read_text().splitlines()),30,'Private control channel did not start')
        session=next(l[8:] for l in (work/'host.log').read_text().splitlines() if l.startswith('SESSION '))
        if not valid_name(session):raise ValueError('Invalid session identifier')
        channel=Channel(session)
        env={k:v for k,v in os.environ.items() if not k.startswith(('SFC_REMIX_','SFC_EARLY_','SFC_EFFECT_','SFC_D3D9_','SFC_SURVEY_','SFC_LIGHT_','SFC_NATIVE_'))}
        executable=TEST/'StarFleetOP.exe'
        if fixture:
            executable=work/'d3d11_return_fixture.exe';shutil.copyfile(OUT/'bin/early_native_tests.exe',executable);env['SFC_EARLY_FIXTURE']='1'
        else:
            flags=[f for f in compat_flags().split() if f!='~']
            if any(f.upper()=='RUNASINVOKER' for f in flags):raise ValueError('Invoker override needs review')
            if flags:env['__COMPAT_LAYER']=' '.join(flags)
        env.update(SFC_REMIX_RETURN_SESSION=session,SFC_REMIX_EXPECTED_IMAGE=str(executable),SFC_EARLY_OUTPUT=str(work/'early.bin'))
        (work/'manifest.json').write_text(json.dumps(dict(probe='EARLY-MODEL-AVAILABILITY-001',fixture=fixture,locks=frozen,session=session,accepted_before=original,copied_before=copied,launcher_before=settings,geometry_payload=False,image_payload=False,proxy_changed=False,gate='Owned existing004162B9semantic anchor;no competing gate/controller hook'),indent=2))
        launcher=sp.Popen([str(BIN/'return_launcher.exe'),'--fixture' if fixture else '--game',str(executable),str(work/'early_component.dll'),digest(executable),digest(work/'early_component.dll')],cwd=executable.parent,env=env,stdout=log('launcher.log'),stderr=sp.STDOUT,creationflags=sp.CREATE_NO_WINDOW)
        def verified():
            nonlocal pid
            m=re.search(r'VERIFIED_CHILD pid=(\d+) suspended_path_match=1 disk_sha_match=1',(work/'launcher.log').read_text());pid=int(m[1]) if m else 0;return bool(pid)
        # Exercise the same live-channel/startup polling in the standalone
        # fixture as in gameplay; previously this entire branch was skipped.
        wait(verified,20,'Copied process path verification missing')
        if fixture:
            launcher.wait(timeout=30)
            if launcher.returncode:raise RuntimeError('Actual injected fixture failed')
            normal=True
        else:
            if Path(image_path(pid))!=executable:raise ValueError('Running process is not the copied game')
            wait_component_ready(channel.snapshot,pid,launcher.poll,enforce)
            print('Early model observer ready. Enter a skirmish within120seconds. Nothing new should appear; no Remix ship is drawn in this measurement.',flush=True)
            print('Use your familiar multi-ship setup. Play normally and exit only after the two-beep request.',flush=True)
            wait(lambda:header_at(channel.address)['gateQpc']>0,120,'Automatic tactical gate was not reached')
            print('Tactical scene detected;recording90seconds. Model-loading metadata from before this point is already retained.',flush=True)
            wait(lambda:header_at(channel.address)['status'] in (3,4) and int.from_bytes(bytes(channel.state.padding[:4]),'little')==1,95,'Observer did not restore hooks and finish writing')
            if header_at(channel.address)['error']:raise RuntimeError('Observer restoration failed')
            channel.set('stop',1)
            import winsound
            print('Observation complete;hooks restored. Please exit SFC normally now.',flush=True);winsound.Beep(660,200);winsound.Beep(660,200)
            wait(lambda:launcher.poll() is not None,30,'Normal game exit not confirmed;leave SFC running rather than killing it')
            normal=launcher.returncode==0 and 'CHILD_EXIT code=0' in (work/'launcher.log').read_text()
            if not normal:raise RuntimeError('Game did not exit normally')
    except Exception as exc:
        error=str(exc);print('Stopped safely:',error,'Exit copied SFC normally if still open.',flush=True)
    finally:
        if channel:channel.set('stop',1)
        if host:
            try:host.wait(timeout=8)
            except sp.TimeoutExpired:host.terminate();host.wait(timeout=5)
        if launcher and launcher.poll() is None:launcher.terminate();launcher.wait(timeout=5) # parent only,never SFC
        for f in logs:f.close()
        report=None
        try:
            if (work/'early.bin').exists():report=analyze(work/'early.bin')
        except Exception as exc:error=(error+'; ' if error else '')+'Analysis: '+str(exc)
        after=critical_hashes(SOURCE);copy_after=critical_hashes(TEST)
        if after!=original or copy_after!=copied or launcher_paths()!=settings:error=(error+'; ' if error else '')+'Client/configuration invariant changed'
        if report and any(report['issues'].get(k) for k in ('cleanup_unconfirmed','record_loss','native_read_or_identity_failure')):error=(error+'; ' if error else '')+'Incomplete observer integrity/cleanup'
        result=dict(probe='EARLY-MODEL-AVAILABILITY-001',fixture=fixture,error=error,normal_exit=normal,accepted_unchanged=after==original,copied_unchanged=copy_after==copied,launcher_settings_unchanged=launcher_paths()==settings,host_exit=host.returncode if host else None,report=report,supervision=supervision,seconds=time.monotonic()-start)
        (work/'result.json').write_text(json.dumps(result,indent=2));print('Evidence:',work,flush=True)
        if channel:channel.close()
    if error:raise RuntimeError(error)
    return work,result

def main():
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group();g.add_argument('--execute',action='store_true');g.add_argument('--qualify',action='store_true');a=p.parse_args()
    preflight();budget()
    if a.qualify:
        unit=OUT/('offline-'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f'));unit.mkdir()
        env={k:v for k,v in os.environ.items() if not k.startswith('SFC_EARLY_')}
        t=sp.run([str(OUT/'bin/early_native_tests.exe'),str(unit/'native.bin')],cwd=OUT,env=env,capture_output=True,text=True,timeout=20)
        (unit/'native.log').write_text(t.stdout+t.stderr);match=re.search(r'Early native PASS checks=(\d+) records=(\d+) drops=(\d+)',t.stdout)
        if t.returncode or not match or int(match[1])<58 or not int(match[3]):raise ValueError('Native ABI/SEH/backpressure/restoration qualification failed')
        negative=analyze(unit/'native.bin')
        if negative['issues'].get('cleanup_unconfirmed') or not negative['stopped'] or negative['stopped'][-1]['restored']!=9:raise ValueError('Negative-control trace lost restoration footer')
        work,result=run(fixture=True);r=result['report']
        if not r or r['issues'] or r['result']!='FIXTURE_TIMING_JOIN_PASS' or len(r['joins'])<4 or not result['normal_exit'] or result['host_exit'] or not result['supervision']['snapshot_checks']:raise ValueError('Actual startup-loaded observer fixture failed')
        q=dict(result='ACTUAL_INJECTED_EARLY_MODEL_TIMING_AND_RESTORATION_PASS',locks=locks(),fixture=str(work.relative_to(ROOT)),result_sha256=digest(work/'result.json'),native=dict(path=str(unit.relative_to(ROOT)),checks=int(match[1]),expected_drops=int(match[3]),negative_control_issues=negative['issues'],restoration_footer=negative['stopped'],log_sha256=digest(unit/'native.log'),trace_sha256=digest(unit/'native.bin')))
        (OUT/'qualification.json').write_text(json.dumps(q,indent=2));print(q['result']);return
    q=json.loads((OUT/'qualification.json').read_text())
    if q['locks']!=locks() or q['result']!='ACTUAL_INJECTED_EARLY_MODEL_TIMING_AND_RESTORATION_PASS':raise ValueError('Early-model qualification missing/stale')
    if not a.execute:print('Early-model read-only preflight PASS. No game/renderer started.');return
    if not C.WinDLL('shell32').IsUserAnAdmin():raise ValueError('Use the established elevated parent;no routine UAC requested')
    run()

if __name__=='__main__':main()
