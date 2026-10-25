"""Isolated default-off effect observation. No SFC without explicit --execute."""
import argparse,ctypes as C,datetime as dt,json,os,re,shutil,subprocess as sp,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/remix_runtime'))
from capture import analyze,header_at,digest
from return_channel import Channel,valid_name
from run_return_game import preflight,critical_hashes,launcher_paths,compat_flags,game_running,image_path,wait_component_ready,SOURCE,TEST,CLIENT,BIN
OUT=ROOT/'artifacts/effect-probe';COMPONENT=OUT/'bin/effect_component.dll'
def locks():
    paths=[p for p in (ROOT/'tools/effect_probe').rglob('*') if p.suffix in ('.h','.cpp','.py','.ps1')]
    paths += [COMPONENT,OUT/'bin/effect_native_tests.exe',ROOT/'tools/remix_runtime/return_wire.h',ROOT/'tools/remix_runtime/return_channel.py',ROOT/'tools/remix_runtime/run_return_game.py']
    paths += [BIN/n for n in ('return_launcher.exe','return_host.exe')]+[ROOT/'artifacts/m1/bin'/n for n in ('m1_gate.dll','m1_controller.exe')]
    detours=ROOT/'artifacts/remix-runtime/deps/detours/Detours-e4bfd6b03e50de46b47abfbd1e46b384f0c5f833'
    paths += [detours/'include/detours.h',detours/'lib.X86/detours.lib']
    return {p.relative_to(ROOT).as_posix():digest(p) for p in paths}
def budget():
    sys.path.insert(0,str(ROOT/'tools/d3d9_proof'));from run_offline import storage
    extra=sum(p.stat().st_size for name in ('effect-probe','render-survey','remix-api-proof') for p in (ROOT/'artifacts'/name).rglob('*') if p.is_file())
    if storage()+extra+112*1024*1024>20_000_000_000 or shutil.disk_usage(ROOT).free<112*1024*1024:raise ValueError('20GB evidence/archive admission or free disk limit')
def run(execute=False,fixture=False):
    preflight();budget()
    if execute and game_running():raise ValueError('Close the existing copied SFC normally first')
    work=ROOT/'artifacts/remix-runtime/runs'/('effect-'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f'));work.mkdir()
    original=critical_hashes(SOURCE);copied=critical_hashes(TEST);settings=launcher_paths();frozen=locks()
    logs=[];host=launcher=controller=None;channel=None;error=None;normal=False;gate_clean=False;pid=0;start=time.monotonic();deadline=start+285
    def log(name):
        f=(work/name).open('w');logs.append(f);return f
    def enforce():
        if time.monotonic()>deadline:raise RuntimeError('Five-minute prepared workflow bound')
        total=sum(p.stat().st_size for p in work.rglob('*') if p.is_file())
        if total>48*1024*1024:raise RuntimeError('Effect16MiB plus ancillary32MiB cap')
    def wait(predicate,seconds,message):
        until=min(deadline,time.monotonic()+seconds)
        while time.monotonic()<until:
            enforce()
            if predicate():return
            time.sleep(.05)
        raise RuntimeError(message)
    try:
        shutil.copyfile(COMPONENT,work/'effect_component.dll')
        host=sp.Popen([str(BIN/'return_host.exe'),'--observe-only'],cwd=work,stdout=log('host.log'),stderr=sp.STDOUT,creationflags=sp.CREATE_NO_WINDOW)
        def session_ready():return any(l.startswith('SESSION ') for l in (work/'host.log').read_text().splitlines())
        wait(session_ready,30,'Private control host did not start')
        session=next(l[8:] for l in (work/'host.log').read_text().splitlines() if l.startswith('SESSION '))
        if not valid_name(session):raise ValueError('Invalid private channel')
        channel=Channel(session)
        env={k:v for k,v in os.environ.items() if not k.startswith(('SFC_REMIX_','SFC_EFFECT_','SFC_D3D9_','SFC_SURVEY_','SFC_LIGHT_','SFC_NATIVE_'))}
        env.update(SFC_REMIX_RETURN_SESSION=session,SFC_REMIX_EXPECTED_IMAGE=str(TEST/'StarFleetOP.exe'),SFC_EFFECT_OUTPUT=str(work/'effects.bin'))
        executable=TEST/'StarFleetOP.exe'
        if fixture:
            executable=work/'d3d11_return_fixture.exe';shutil.copyfile(OUT/'bin/effect_native_tests.exe',executable)
            env['SFC_REMIX_EXPECTED_IMAGE']=str(executable);env['SFC_EFFECT_INJECTED_FIXTURE']='1'
        else:
            flags=[f for f in compat_flags().split() if f!='~']
            if any(f.upper()=='RUNASINVOKER' for f in flags):raise ValueError('Invoker override requires review')
            if flags:env['__COMPAT_LAYER']=' '.join(flags)
        (work/'manifest.json').write_text(json.dumps(dict(probe='EFFECT-RESOURCE-JOIN-001',fixture=fixture,locks=frozen,session=session,accepted_before=original,copied_before=copied,launcher_before=settings,geometry_payload=False,image_payload=False,proxy_changed=False),indent=2))
        launcher=sp.Popen([str(BIN/'return_launcher.exe'),'--fixture' if fixture else '--game',str(executable),str(work/'effect_component.dll'),digest(executable),digest(work/'effect_component.dll')],cwd=executable.parent,env=env,stdout=log('launcher.log'),stderr=sp.STDOUT,creationflags=sp.CREATE_NO_WINDOW)
        if fixture:
            launcher.wait(timeout=30)
            if launcher.returncode:raise RuntimeError('Injected fixture exited nonzero')
            normal=True
        else:
            def verified():
                nonlocal pid
                m=re.search(r'VERIFIED_CHILD pid=(\d+) suspended_path_match=1 disk_sha_match=1',(work/'launcher.log').read_text());pid=int(m[1]) if m else 0;return bool(pid)
            wait(verified,20,'Copied client path was not verified')
            if Path(image_path(pid))!=executable:raise ValueError('Running process path mismatch')
            wait_component_ready(channel.snapshot,pid,launcher.poll,enforce)
            # Avoid remote gate setup while the native startup loader still owns
            # initialization: require an actual visible game window first.
            user=C.WinDLL('user32');found=False
            callback=C.WINFUNCTYPE(C.c_bool,C.c_void_p,C.c_void_p)
            def window_ready():
                nonlocal found
                found=False
                @callback
                def visit(hwnd,_):
                    nonlocal found
                    owner=C.c_uint32();user.GetWindowThreadProcessId(C.c_void_p(hwnd),C.byref(owner))
                    if owner.value==pid and user.IsWindowVisible(C.c_void_p(hwnd)):found=True
                    return True
                user.EnumWindows(visit,0);return found
            wait(window_ready,60,'Visible copied game window not ready')
            gate=work/'gate';gate.mkdir();config=gate/'component.ini';ctl=ROOT/'artifacts/m1/bin/m1_controller.exe'
            config.write_text('[m1]\nOutputDirectory='+str(gate)+'\nControllerPath='+str(ctl)+'\nMaxSeconds=120\nStopOnBurst=1\nMaxFrames=1\nMaxEvents=1\nMaxOwners=1\nWarningBytes=16777216\nHardBytes=33554432\n',encoding='ascii')
            controller=sp.Popen([str(ctl),'--pid',str(pid),'--dll',str(ROOT/'artifacts/m1/bin/m1_gate.dll'),'--config',str(config),'--max-seconds','120','--stop-on-burst','1','--already-loaded','0','--unload-after-stop','1'],cwd=ROOT,stdout=log('gate.log'),stderr=sp.STDOUT,creationflags=sp.CREATE_NO_WINDOW)
            print('Enter the usual skirmish within120seconds. Fight normally; fire weapons and allow shield hits. An enemy explosion is useful if practical. No extra ship or visual change is expected. Exit only after the two-beep request.',flush=True)
            wait(lambda:controller.poll() is not None,125,'Automatic tactical gate timeout')
            summary=json.loads((gate/'M1-A-summary.json').read_text(encoding='utf-8-sig'));text=(work/'gate.log').read_text()
            gate_clean=controller.returncode==0 and summary.get('gate_activated') is True and all(s in text for s in ('component_state=removed','hook_bytes_restored=true','component_unloaded=true'))
            if not gate_clean:raise RuntimeError('Automatic gate restoration/unload unconfirmed')
            channel.set('armed',1)
            wait(lambda:header_at(channel.address)['status'] in (3,4) and int.from_bytes(bytes(channel.state.padding[:4]),'little')==1,95,'Effects hooks/worker did not stop cleanly')
            if header_at(channel.address)['error']:raise RuntimeError('Effects observer setup/cleanup error')
            channel.set('stop',1)
            import winsound
            print('Observation finished; effects hooks restored. Please exit SFC normally now.',flush=True);winsound.Beep(660,200);winsound.Beep(660,200)
            wait(lambda:launcher.poll() is not None,30,'Normal SFC exit not confirmed; do not kill the game')
            normal=launcher.returncode==0 and 'CHILD_EXIT code=0' in (work/'launcher.log').read_text()
            if not normal:raise RuntimeError('Game did not exit normally')
    except Exception as exc:error=str(exc);print('Stopped safely:',error,'Exit copied SFC normally if still open.',flush=True)
    finally:
        if channel:channel.set('stop',1)
        if host:
            try:host.wait(timeout=8)
            except sp.TimeoutExpired:host.terminate();host.wait(timeout=5)
        if launcher and launcher.poll() is None:launcher.terminate();launcher.wait(timeout=5) # parent only;never terminate SFC
        for f in logs:f.close()
        report=None
        try:
            if (work/'effects.bin').exists():report=analyze(work/'effects.bin')
        except Exception as exc:error=(error+'; ' if error else '')+'Analysis: '+str(exc)
        after=critical_hashes(SOURCE);copy_after=critical_hashes(TEST)
        if after!=original or copy_after!=copied or launcher_paths()!=settings:error=(error+'; ' if error else '')+'Client/configuration invariants changed'
        result=dict(probe='EFFECT-RESOURCE-JOIN-001',fixture=fixture,error=error,normal_exit=normal,gate_clean_unloaded=gate_clean if not fixture else None,accepted_unchanged=after==original,copied_unchanged=copy_after==copied,launcher_settings_unchanged=launcher_paths()==settings,host_exit=host.returncode if host else None,report=report,seconds=time.monotonic()-start)
        (work/'result.json').write_text(json.dumps(result,indent=2));print('Evidence:',work,flush=True)
        if channel:channel.close()
    if error:raise RuntimeError(error)
    return work,result
def main():
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group();g.add_argument('--execute',action='store_true');g.add_argument('--qualify',action='store_true');a=p.parse_args()
    if a.qualify:
        unit=OUT/('offline-'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f'));unit.mkdir()
        unit_env={k:v for k,v in os.environ.items() if not k.startswith('SFC_EFFECT_')}
        test=sp.run([str(OUT/'bin/effect_native_tests.exe'),str(unit/'native.bin')],cwd=OUT,env=unit_env,capture_output=True,text=True,timeout=20)
        (unit/'native.log').write_text(test.stdout+test.stderr)
        match=re.search(r'Effect native PASS checks=(\d+) records=(\d+) drops=(\d+)',test.stdout)
        if test.returncode or not match or int(match[1])<44 or not int(match[3]):raise ValueError('Native ABI/backpressure/restoration checks failed')
        work,result=run(fixture=True);r=result['report']
        if not r or r['qualified_native_polygons']<4 or r['issues']!={'native_exception_observed':1} or not result['normal_exit']:raise ValueError('Actual injected effects fixture incomplete')
        q=dict(result='ACTUAL_INJECTED_EFFECT_HOOKS_RESOURCES_RESTORATION_PASS',locks=locks(),fixture=str(work.relative_to(ROOT)),result_sha256=digest(work/'result.json'),native=dict(path=str(unit.relative_to(ROOT)),log_sha256=digest(unit/'native.log'),trace_sha256=digest(unit/'native.bin'),checks=int(match[1]),expected_backpressure_drops=int(match[3])))
        (OUT/'qualification.json').write_text(json.dumps(q,indent=2));print(q['result']);return
    preflight();budget();q=json.loads((OUT/'qualification.json').read_text())
    if q['locks']!=locks() or q['result']!='ACTUAL_INJECTED_EFFECT_HOOKS_RESOURCES_RESTORATION_PASS':raise ValueError('Effects qualification stale/missing')
    if not a.execute:print('Effects read-only preflight PASS. No game/renderer started.');return
    run(execute=True)
if __name__=='__main__':main()
