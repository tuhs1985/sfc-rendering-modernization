"""Isolated default-off effect observation. No SFC without explicit --execute."""
import argparse,ctypes as C,datetime as dt,json,os,re,shutil,struct,subprocess as sp,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/remix_runtime'))
from capture import analyze,header_at,hook_phase_at,digest
from return_channel import Channel,valid_name
from run_return_game import preflight,critical_hashes,launcher_paths,compat_flags,game_running,image_path,wait_component_ready,SOURCE,TEST,CLIENT,BIN
OUT=ROOT/'artifacts/effect-probe';COMPONENT=OUT/'bin/effect_component.dll'
JOIN_PRODUCER=OUT/'bin/m1_effect_join.dll'
def locks():
    paths=[p for p in (ROOT/'tools/effect_probe').rglob('*') if p.suffix in ('.h','.cpp','.py','.ps1')]
    paths += [COMPONENT,OUT/'bin/effect_native_tests.exe',ROOT/'tools/remix_runtime/return_wire.h',ROOT/'tools/remix_runtime/return_channel.py',ROOT/'tools/remix_runtime/run_return_game.py']
    paths += [BIN/n for n in ('return_launcher.exe','return_host.exe')]+[ROOT/'artifacts/m1/bin'/n for n in ('m1_gate.dll','m1_controller.exe')]
    detours=ROOT/'artifacts/remix-runtime/deps/detours/Detours-e4bfd6b03e50de46b47abfbd1e46b384f0c5f833'
    paths += [detours/'include/detours.h',detours/'lib.X86/detours.lib']
    paths += list((ROOT/'src/session').glob('*.py'))
    return {p.relative_to(ROOT).as_posix():digest(p) for p in paths}
def join_locks():
    paths=[JOIN_PRODUCER,*((ROOT/'tools/m1_component').glob('*.h')),
           ROOT/'tools/m1_component/m1_component.cpp',ROOT/'tools/m1_component/m1_component.def']
    paths += [ROOT/'tools/d3d9_proof'/name for name in ('multi_scene_wire.h','live_owner_wire.h','frame_ingress.h')]
    paths += [ROOT/'src/transport'/name for name in ('scene_receiver.py','live_scene.py','multi_scene.py','scene_capacity.py')]
    return {p.relative_to(ROOT).as_posix():digest(p) for p in paths}
def budget():
    sys.path.insert(0,str(ROOT/'tools/d3d9_proof'));from run_offline import storage
    extra=sum(p.stat().st_size for name in ('effect-probe','render-survey','remix-api-proof') for p in (ROOT/'artifacts'/name).rglob('*') if p.is_file())
    if storage()+extra+112*1024*1024>20_000_000_000 or shutil.disk_usage(ROOT).free<112*1024*1024:raise ValueError('20GB evidence/archive admission or free disk limit')
def stop_join_controller(pid):
    kernel=C.WinDLL('kernel32',use_last_error=True)
    kernel.OpenEventW.argtypes=[C.c_uint32,C.c_int,C.c_wchar_p]
    kernel.OpenEventW.restype=C.c_void_p
    kernel.SetEvent.argtypes=[C.c_void_p]
    kernel.CloseHandle.argtypes=[C.c_void_p]
    handle=kernel.OpenEventW(2,False,f'Local\\SFCM1BurstComplete_{pid}')
    if not handle:raise C.WinError(C.get_last_error())
    try:
        if not kernel.SetEvent(handle):raise C.WinError(C.get_last_error())
    finally:
        kernel.CloseHandle(handle)

def gate_restored(controller,log):
    return controller.poll()==0 and all(marker in log for marker in (
        'component_state=removed','hook_bytes_restored=true','component_unloaded=true'))

def verify_retained_receipt(work,report,pid,session):
    from multi_scene import FRAME_BYTES,fnv
    frame_path=work/'retained-frame.bin'
    receipt_path=work/'retained-frame.json'
    if not (frame_path.is_file() and receipt_path.is_file()):
        return None
    stamp=json.loads(receipt_path.read_text())
    raw=frame_path.read_bytes()
    if len(raw)!=FRAME_BYTES or len(report['batch_draws'])!=1:
        raise ValueError('Retained-frame receipt has no exact packet and draw')
    sequence,offered,frame,*_=struct.unpack_from('<QQ4I',raw)
    session_words=[int(session[-32:][i:i+8],16) for i in range(0,32,8)]
    draw=report['batch_draws'][0]
    if (fnv(raw[:-8])!=stamp['checksum'] or
        struct.unpack_from('<Q',raw,len(raw)-8)[0]!=stamp['checksum'] or
        (stamp['frame'],stamp['sequence'],stamp['pid'],stamp['session_words'])!=(frame,sequence,pid,session_words) or
        report['header']['pid']!=pid or (stamp['thread'],stamp['manager'])!=(draw['thread'],draw['manager']) or
        frame!=draw['native_scene_ordinal'] or draw['present_result']!=1 or
        not stamp['scene_start_qpc']<=offered<=stamp['published_qpc']<=stamp['flushed_qpc']<=stamp['presented_qpc']):
        raise ValueError('Retained-frame receipt does not match saved packet and draw')
    return dict(stamp,packet_sha256=digest(frame_path))

def run(execute=False,fixture=False,quad=False,batch=False,join=False,producer_only=False):
    preflight();budget()
    if execute and game_running():raise ValueError('Close the existing copied SFC normally first')
    work=ROOT/'artifacts/remix-runtime/runs'/('effect-'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f'));work.mkdir()
    original=critical_hashes(SOURCE);copied=critical_hashes(TEST);settings=launcher_paths();frozen=locks()
    if join:frozen.update(join_locks())
    logs=[];host=launcher=controller=None;channel=receiver=None;error=None;normal=False;gate_clean=False;pid=0;start=time.monotonic();deadline=start+285
    first_frame=last_frame=None
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
    def child_exited_normally():
        return launcher.poll()==0 and 'CHILD_EXIT code=0' in (work/'launcher.log').read_text().splitlines()
    def observer_closed():
        return int.from_bytes(bytes(channel.state.padding[:4]),'little')==1
    try:
        shutil.copyfile(COMPONENT,work/'effect_component.dll')
        host=sp.Popen([str(BIN/'return_host.exe'),'--observe-only'],cwd=work,stdout=log('host.log'),stderr=sp.STDOUT,creationflags=sp.CREATE_NO_WINDOW)
        def session_ready():return any(l.startswith('SESSION ') for l in (work/'host.log').read_text().splitlines())
        wait(session_ready,30,'Private control host did not start')
        session=next(l[8:] for l in (work/'host.log').read_text().splitlines() if l.startswith('SESSION '))
        if not valid_name(session):raise ValueError('Invalid private channel')
        channel=Channel(session)
        env={k:v for k,v in os.environ.items() if not k.startswith(('SFC_REMIX_','SFC_EFFECT_','SFC_D3D9_','SFC_SURVEY_','SFC_LIGHT_','SFC_NATIVE_','SFC_RELEASE_','SFC_PERSISTENT_','SFC_BREAK_','SFC_PIPELINE_','SFC_DAMAGE_'))}
        env.update(SFC_REMIX_RETURN_SESSION=session,SFC_REMIX_EXPECTED_IMAGE=str(TEST/'StarFleetOP.exe'),SFC_EFFECT_OUTPUT=str(work/'effects.bin'))
        if quad:env['SFC_EFFECT_QUAD_OBSERVATION']='1'
        if batch:env['SFC_EFFECT_BATCH_OBSERVATION']='1'
        if join:
            from scene_receiver import Receiver
            from live_owner_timing import initialize
            from multi_scene import initialize as initialize_cohort,frame_snapshot
            receiver=Receiver()
            initialize(receiver.channel,persistent=True)
            initialize_cohort(receiver.channel)
            env.update(SFC_EFFECT_JOIN_SCENE=receiver.name,SFC_REMIX_CALIBRATION_SCENE=receiver.name,
                       SFC_D3D9_SOURCE_TIMING='1',SFC_D3D9_LIVE_TIMING='1',SFC_D3D9_MULTISCENE='1',
                       SFC_PERSISTENT_SCENE='1',SFC_PIPELINE_MODE='performance')
        executable=TEST/'StarFleetOP.exe'
        if fixture:
            executable=work/'d3d11_return_fixture.exe';shutil.copyfile(OUT/'bin/effect_native_tests.exe',executable)
            env['SFC_REMIX_EXPECTED_IMAGE']=str(executable);env['SFC_EFFECT_INJECTED_FIXTURE']='1'
        else:
            flags=[f for f in compat_flags().split() if f!='~']
            if any(f.upper()=='RUNASINVOKER' for f in flags):raise ValueError('Invoker override requires review')
            if flags:env['__COMPAT_LAYER']=' '.join(flags)
        (work/'manifest.json').write_text(json.dumps(dict(probe='EFFECT-RESOURCE-JOIN-001',fixture=fixture,locks=frozen,session=session,scene_session=receiver.name if receiver else None,accepted_before=original,copied_before=copied,launcher_before=settings,geometry_payload=quad or batch,batch_observation=batch,image_payload=False,proxy_changed=False),indent=2))
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
            common='[m1]\nOutputDirectory='+str(gate)+'\nControllerPath='+str(ctl)+'\nStopOnBurst=1\nWarningBytes=16777216\nHardBytes=33554432\n'
            if join:
                config.write_text(common+'MaxSeconds=110\nMaxFrames=6000\nMaxEvents=1\nMaxOwners=256\nEnableGeometryHook=0\nEnableWrapperObservation=1\nEnableMeshExport=1\nEnableTextureReferences=1\nEnablePrivateCopy=0\nLiveChannel='+receiver.name+'\n',encoding='ascii')
                producer=JOIN_PRODUCER
                gate_args=['--gate-timeout-seconds','120']
            else:
                config.write_text(common+'MaxSeconds=120\nMaxFrames=1\nMaxEvents=1\nMaxOwners=1\n',encoding='ascii')
                producer=ROOT/'artifacts/m1/bin/m1_gate.dll'
                gate_args=[]
            controller=sp.Popen([str(ctl),'--pid',str(pid),'--dll',str(producer),'--config',str(config),'--max-seconds','110' if join else '120','--stop-on-burst','1','--already-loaded','0','--unload-after-stop','1',*gate_args],cwd=ROOT,stdout=log('gate.log'),stderr=sp.STDOUT,creationflags=sp.CREATE_NO_WINDOW)
            if producer_only:print('Enter a skirmish and play normally until the two beeps, then exit. This checks retained-frame startup and cleanup.',flush=True)
            elif join:print('Enter a skirmish with a drone-equipped ship. Wait for the retained source ready message, then fire drones. Exit normally after the two beeps.',flush=True)
            elif batch:print('Enter a skirmish with a drone-equipped ship. Launch several drones and keep them in view. Exit normally after the two-beep request.',flush=True)
            else:print('Enter the usual skirmish within120seconds. Fight normally; fire weapons and allow shield hits. An enemy explosion is useful if practical. No extra ship or visual change is expected. Exit only after the two-beep request.',flush=True)
            if join:
                from coordinator import wait_live_gate
                wait_live_gate(pid,controller,enforce,timeout=125)
                def retained_source_ready():
                    nonlocal first_frame
                    if controller.poll() is not None or launcher.poll() is not None:
                        raise RuntimeError('Game or retained producer exited before its first frame')
                    receiver.drain()
                    snapshot=frame_snapshot(receiver.channel)
                    if snapshot is None:return False
                    first_frame=snapshot[0]
                    return True
                wait(retained_source_ready,12,'No retained frame published after the tactical gate')
                if producer_only:
                    def retained_source_advances():
                        nonlocal last_frame
                        if controller.poll() is not None or launcher.poll() is not None:
                            raise RuntimeError('Game or retained producer exited during startup verification')
                        receiver.drain()
                        snapshot=frame_snapshot(receiver.channel,minimum=first_frame+120)
                        if snapshot is None:return False
                        last_frame=snapshot[0]
                        return True
                    wait(retained_source_advances,12,'Retained source did not advance by 120 frames')
                    channel.set('stop',1)
            else:
                wait(lambda:controller.poll() is not None,125,'Automatic tactical gate timeout')
                summary=json.loads((gate/'M1-A-summary.json').read_text(encoding='utf-8-sig'))
                gate_clean=summary.get('gate_activated') is True and gate_restored(controller,(work/'gate.log').read_text())
                if not gate_clean:raise RuntimeError('Automatic gate restoration/unload unconfirmed')
            if not producer_only:channel.set('armed',1)
            if batch and not producer_only:
                wait(lambda:channel.snapshot()['ready']==2 or channel.snapshot()['error'] or launcher.poll() is not None,
                     10,'Batch hooks did not attach after tactical gate unload')
                if channel.snapshot()['error']:raise RuntimeError('Batch hooks failed to attach after tactical gate unload')
                if join and channel.snapshot()['ready']==2:
                    print('Retained frame source ready. Fire drones now.',flush=True)
            def observation_done():
                if observer_closed() or launcher.poll() is not None:return True
                if join:
                    if controller.poll() is not None:raise RuntimeError('Retained scene producer exited during observation')
                    receiver.drain()
                return False
            wait(observation_done,95,'Effects hooks/worker did not stop cleanly')
            if not observer_closed():
                normal=child_exited_normally()
                if normal:raise RuntimeError('SFC exited normally before the effects trace closed')
                raise RuntimeError('SFC exited abnormally before the effects trace closed')
            if header_at(channel.address)['status']!=3:raise RuntimeError('Effects observer did not finalize successfully')
            if header_at(channel.address)['error']:raise RuntimeError('Effects observer setup/cleanup error')
            if producer_only and header_at(channel.address)['gateQpc']:
                raise RuntimeError('Observer armed during producer-only test')
            if join:
                stop_join_controller(pid)
                wait(lambda:controller.poll() is not None,18,'Retained producer did not stop cleanly')
                gate_clean=gate_restored(controller,(work/'gate.log').read_text())
                if not gate_clean:raise RuntimeError('Retained producer restoration/unload unconfirmed')
            channel.set('stop',1)
            import winsound
            print('Observation finished; effects hooks restored. Please exit SFC normally now.',flush=True);winsound.Beep(660,200);winsound.Beep(660,200)
            wait(lambda:launcher.poll() is not None,30,'Normal SFC exit not confirmed; do not kill the game')
            normal=launcher.returncode==0 and 'CHILD_EXIT code=0' in (work/'launcher.log').read_text()
            if not normal:raise RuntimeError('Game did not exit normally')
    except Exception as exc:error=str(exc);print('Observation interrupted:',error,flush=True)
    finally:
        if channel:channel.set('stop',1)
        if join and controller and controller.poll() is None and launcher and launcher.poll() is None:
            try:
                wait(observer_closed,7,'Observer still active during cleanup')
                stop_join_controller(pid)
                controller.wait(timeout=17)
                gate_clean=gate_restored(controller,(work/'gate.log').read_text())
            except (OSError,RuntimeError,sp.TimeoutExpired) as exc:
                error=(error+'; ' if error else '')+'Retained producer cleanup: '+str(exc)
        if host:
            try:host.wait(timeout=8)
            except sp.TimeoutExpired:host.terminate();host.wait(timeout=5)
        if launcher and launcher.poll() is None:launcher.terminate();launcher.wait(timeout=5) # parent only;never terminate SFC
        for f in logs:f.close()
        report=None
        retained=None
        try:
            if (work/'effects.bin').exists() and not producer_only:
                report=analyze(work/'effects.bin',allow_unfinalized=error is not None and not fixture)
                if batch and not fixture:
                    draws=report['batch_draws']
                    if len(draws)!=1:
                        report['issues']['batch_draw_unobserved']=1
                    else:
                        draw=draws[0]
                        if not draw['bound_filename']:
                            report['issues']['batch_texture_unverified']=1
                        if not draw['native_scene_ordinal'] or len(draw['native_state'])!=23 or any(
                            row['words'][1] or (row['kind']==2 and row['words'][3])
                            for row in draw['native_state']
                        ) or draw['present_result']!=1:
                            report['issues']['batch_state_or_present_unverified']=1
                    if report['issues']:report['result']='PARTIAL'
                if join and not fixture:
                    retained=verify_retained_receipt(work,report,pid,receiver.name)
                    if not retained:
                        report['issues']['retained_frame_join_unverified']=1
                        report['result']='PARTIAL'
        except Exception as exc:error=(error+'; ' if error else '')+'Analysis: '+str(exc)
        after=critical_hashes(SOURCE);copy_after=critical_hashes(TEST)
        if after!=original or copy_after!=copied or launcher_paths()!=settings:error=(error+'; ' if error else '')+'Client/configuration invariants changed'
        result=dict(probe='EFFECT-RESOURCE-JOIN-001',fixture=fixture,error=error,normal_exit=normal,gate_clean_unloaded=gate_clean if not fixture else None,accepted_unchanged=after==original,copied_unchanged=copy_after==copied,launcher_settings_unchanged=launcher_paths()==settings,host_exit=host.returncode if host else None,report=report,seconds=time.monotonic()-start)
        if join:result['retained_frame']=retained
        if producer_only:
            result['producer_only']=True
            result['producer_frame_range']=[first_frame,last_frame]
            result['producer_startup_and_cleanup_verified']=bool(not error and normal and gate_clean)
        if channel:result['observer_hook_phase']=hook_phase_at(channel.address)
        (work/'result.json').write_text(json.dumps(result,indent=2));print('Evidence:',work,flush=True)
        if channel:channel.close()
        if receiver:receiver.close()
    if error:raise RuntimeError(error)
    return work,result
def main():
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group();g.add_argument('--execute',action='store_true');g.add_argument('--qualify',action='store_true');m=p.add_mutually_exclusive_group();m.add_argument('--quad',action='store_true');m.add_argument('--batch',action='store_true');m.add_argument('--join',action='store_true');m.add_argument('--join-producer-only',action='store_true');a=p.parse_args()
    join=a.join or a.join_producer_only
    if a.qualify:
        unit=OUT/('offline-'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f'));unit.mkdir()
        unit_env={k:v for k,v in os.environ.items() if not k.startswith('SFC_EFFECT_')}
        test=sp.run([str(OUT/'bin/effect_native_tests.exe'),str(unit/'native.bin')],cwd=OUT,env=unit_env,capture_output=True,text=True,timeout=20)
        (unit/'native.log').write_text(test.stdout+test.stderr)
        match=re.search(r'Effect native PASS checks=(\d+) records=(\d+) drops=(\d+)',test.stdout)
        if test.returncode or not match or int(match[1])<44 or not int(match[3]):raise ValueError('Native ABI/backpressure/restoration checks failed')
        parsed=analyze(unit/'native.bin')
        if not any(sample['preclip_corner_words'][0]==tuple(range(1,17)) for sample in parsed['quad_samples']):
            raise ValueError('Native quad sample values not retained')
        work,result=run(fixture=True,quad=True);r=result['report']
        if not r or r['qualified_native_polygons']<4 or r['issues']!={'native_exception_observed':1} or not result['normal_exit']:raise ValueError('Actual injected effects fixture incomplete')
        if not r['quad_samples'] or any(sample['filename']!='assets/textures/fx0.bmp' for sample in r['quad_samples']):
            raise ValueError('Injected quad resource association incomplete')
        batch_work,batch_result=run(fixture=True,batch=True)
        draws=batch_result['report']['batch_draws']
        source_vertices=batch_result['report']['quad_samples'][0]['preclip_corner_words']
        packed=[list(struct.unpack('<4Q',struct.pack('<8I',*source_vertices[i][5:13]))) for i in (0,1,2,0,2,3)]
        if len(draws)!=1 or draws[0]['indices']!=[0,1,2,0,2,3] or draws[0]['vertex_words']!=packed or draws[0]['flush_order']!=4 or draws[0]['native_scene_ordinal']!=2 or draws[0]['present_sequence']!=3 or draws[0]['present_result']!=1:
            raise ValueError('Injected batch fixture did not carry the selected span to the later flush and presentation')
        q=dict(result='ACTUAL_INJECTED_EFFECT_HOOKS_RESOURCES_RESTORATION_PASS',locks=locks(),fixture=str(work.relative_to(ROOT)),result_sha256=digest(work/'result.json'),batch_fixture=str(batch_work.relative_to(ROOT)),native=dict(path=str(unit.relative_to(ROOT)),log_sha256=digest(unit/'native.log'),trace_sha256=digest(unit/'native.bin'),checks=int(match[1]),expected_backpressure_drops=int(match[3])))
        if join:
            join_work,joined=run(fixture=True,batch=True,join=True)
            manifest=json.loads((join_work/'manifest.json').read_text())
            report=joined['report']
            stamp=verify_retained_receipt(join_work,report,report['header']['pid'],manifest['scene_session'])
            if not stamp or stamp['frame']!=42 or stamp['sequence']!=1:
                raise ValueError('Injected shared-mapping join fixture incomplete')
            q.update(join_locks=join_locks(),join_fixture=str(join_work.relative_to(ROOT)))
        (OUT/'qualification.json').write_text(json.dumps(q,indent=2));print(q['result']);return
    preflight();budget();q=json.loads((OUT/'qualification.json').read_text())
    if q['locks']!=locks() or q['result']!='ACTUAL_INJECTED_EFFECT_HOOKS_RESOURCES_RESTORATION_PASS':raise ValueError('Effects qualification stale/missing')
    if join and q.get('join_locks')!=join_locks():raise ValueError('Retained producer qualification stale/missing')
    if not a.execute:print('Effects read-only preflight PASS. No game/renderer started.');return
    run(execute=True,quad=a.quad,batch=a.batch or join,join=join,producer_only=a.join_producer_only)
if __name__=='__main__':main()
