"""Untimed native gameplay and shared process/graphics lifetime."""
from pathlib import Path
import sys

CODE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
sys.path.insert(0,str(CODE/'tools/remix_runtime'))

sys.path.insert(0,str(CODE/'src/runtime'))
sys.path.insert(0,str(CODE/'src/assets'))
sys.path.insert(0,str(CODE/'src/transport'))
sys.path.insert(0,str(CODE/'src/rendering'))
from scene_capacity import OWNERS,ASSETS
import argparse
import ctypes as C
from ctypes import wintypes as W
import datetime as dt
import json
import os
import re
import shutil
import subprocess as sp
import time
import winreg
import winsound
from return_channel import Channel,valid_name
import reports as run_report
import graphics_transaction
from exit_monitor import Monitor,NormalGameExit,retire_controller
from copied_preferences import protected_ini_sha256,prepared_ini_signature,changed_protected_files
from native_config import write as write_native_config
from runtime_files import ROOT,BIN,DLL,TEST,ENV,digest,capture_file_bytes
import sys
sys.path.insert(0,str(ROOT/'tools/remix_runtime'))
from runtime_context import CONTEXT

SOURCE=CONTEXT.accepted_root
CLIENT='4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29'
CRITICAL=('StarFleetOP.exe','DDraw.dll','D3DImm.dll','dxgi.dll','dgVoodoo.conf','ReShade.ini','sfc.ini')


def image_path(pid):
    k=C.WinDLL('kernel32',use_last_error=True)
    k.OpenProcess.argtypes=[W.DWORD,W.BOOL,W.DWORD];k.OpenProcess.restype=W.HANDLE
    k.QueryFullProcessImageNameW.argtypes=[W.HANDLE,W.DWORD,W.LPWSTR,C.POINTER(W.DWORD)]
    k.CloseHandle.argtypes=[W.HANDLE]
    handle=k.OpenProcess(0x1000,False,pid)
    if not handle:raise C.WinError(C.get_last_error())
    try:
        value=C.create_unicode_buffer(32768);size=W.DWORD(len(value))
        if not k.QueryFullProcessImageNameW(handle,0,value,C.byref(size)):raise C.WinError(C.get_last_error())
        return value.value
    finally:k.CloseHandle(handle)

def game_running():
    from windows_processes import game_running as native_inventory
    return native_inventory()

def critical_hashes(folder):return {n:digest(folder/n) for n in CRITICAL}
def launcher_paths():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,r'Software\VB and VBA Program Settings\SFCLauncher\Paths') as key:
            return {n:winreg.QueryValueEx(key,n)[0] for n in ('Client2Op','Server2Op')}
    except FileNotFoundError:return {}
def compat_flags():
    key=r'Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers'
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,key) as handle:return str(winreg.QueryValueEx(handle,str(SOURCE/'StarFleetOP.exe'))[0])
    except FileNotFoundError:return ''

def wait_component_ready(snapshot,pid,poll,enforce,timeout=60,clock=time.monotonic,pause=time.sleep):
    until=clock()+timeout
    while clock()<until:
        enforce();state=snapshot()
        if poll() is not None:
            enforce() # Resolve a normal exit that raced the preceding check.
            raise RuntimeError('Game exited during graphics initialization')
        if state['error']:raise RuntimeError('Component error during graphics initialization')
        if state['gamePid']==pid and state['startupVerified'] and state['startupRestored'] and state['ready']:return state
        pause(.05)
    raise RuntimeError('Graphics initialization readiness timed out; no tactical gate injection attempted')

def tactical_gate_timeout(multi_ship):
    # Multi-ship selection needs longer;retain the285s overall workflow ceiling.
    return 120 if multi_ship else 90


def wait_live_gate(pid,controller,enforce,timeout=90):
    k=C.WinDLL('kernel32',use_last_error=True)
    k.OpenEventW.argtypes=[W.DWORD,W.BOOL,W.LPCWSTR];k.OpenEventW.restype=W.HANDLE
    k.WaitForSingleObject.argtypes=[W.HANDLE,W.DWORD];k.CloseHandle.argtypes=[W.HANDLE]
    deadline=float('inf') if timeout is None else time.monotonic()+timeout;event=None
    try:
        while time.monotonic()<deadline:
            enforce()
            if controller.poll() is not None:
                enforce()
                raise RuntimeError('Semantic controller exited before tactical gate')
            if not event:event=k.OpenEventW(0x100000,False,f'Local\\SFCM1TacticalGate_{pid}')
            if event and k.WaitForSingleObject(event,0)==0:return
            time.sleep(.05)
        raise RuntimeError('Semantic tactical gate timeout')
    finally:
        if event:k.CloseHandle(event)
def preflight():
    if CONTEXT.release:
        from release_manifest import verify,verify_game_profile
        verify_game_profile(CONTEXT,verify(CONTEXT))
        return
    if digest(SOURCE/'StarFleetOP.exe')!=CLIENT or digest(TEST/'StarFleetOP.exe')!=CLIENT:raise RuntimeError('Original/copied client hash mismatch')
    if digest(DLL)!='F7C310821AA98BCDFDEC120330B0A89457B7C5EBA58D21464AF32639611C809F':raise RuntimeError('Pinned runtime mismatch')
    if digest(TEST/'dxgi.dll')!='E35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7':raise RuntimeError('Copied proxy mismatch')
    for p in (BIN/'return_launcher.exe',BIN/'return_host.exe',BIN/'SFCRemixReturn.dll',CONTEXT.artifact('m1/bin/m1_gate.dll'),CONTEXT.artifact('m1/bin/m1_controller.exe')):
        if not p.is_file():raise RuntimeError('Prepared build missing: '+str(p))
    # PlayerName is a game-owned preference. All remaining INI bytes and other
    # critical copied files still match independent preparation.
    manifest=json.loads((CONTEXT.artifact('remix-runtime/test-install/source-copy-files.json')).read_text(encoding='utf-8-sig'))
    expected={v['path'].lower():v['copy_sha256'] for v in manifest}
    actual=critical_hashes(TEST)
    baseline={name:expected.get(name.lower()) for name in actual}
    signature=prepared_ini_signature(CONTEXT.artifact('remix-runtime/test-install/sfc-baseline.ini'),expected['sfc.ini'])
    changed=changed_protected_files(baseline,actual,(TEST/'sfc.ini').read_bytes(),signature)
    if changed:raise RuntimeError('Copied baseline changed: '+', '.join(changed))


def play_options(argv=None):
    """Normal native play only. Optional experiments belong to development tools."""
    parser=argparse.ArgumentParser(description='SFC native multi-ship play')
    parser.add_argument('--execute',action='store_true')
    parser.add_argument('--budget-seconds',type=int,default=285)
    parser.add_argument('--play-session',action='store_true',default=True)
    parser.add_argument('--native-all-ships',action='store_true',default=True)
    parser.add_argument('--native-insertion-policy',choices=('ExtraFrame',),default='ExtraFrame')
    parser.add_argument('--pipeline-mode',choices=('performance',),default='performance')
    parser.add_argument('--native-resolution',action='store_true',default=CONTEXT.release)
    parser.add_argument('--break-models',action='store_true')
    damage=parser.add_mutually_exclusive_group()
    damage.add_argument('--damage-textures',action='store_true',default=None)
    damage.add_argument('--no-damage-textures',dest='damage_textures',action='store_false')
    return parser.parse_args(argv)


class Session:
    """Shared process, graphics and resource lifetime; mode-specific phases are explicit."""
    def __init__(self,argv=None):
        self.argv=argv
        self.full_support=True
        self.semantic_enabled=True
        self.untimed=True
        self.output_enabled=True

    def out(self,name):
        stream=open(self.work/name,'wb')
        self.streams.append(stream)
        return stream

    def run(self):
        if not self._prepare():return
        self._initialize()
        try:
            self._install_proxy()
            self._start_host()
            self._wait_host()
            self._prepare_game()
            self._launch_game()
            self._after_launch()
            self._await_device()
            self._instructions()
            self._configure_controller()
            self._start_controller()
            self._check_observers()
            self._arm()
            self._begin_observation()
            self._observe()
            self._end_observation()
        except NormalGameExit:
            self._normal_exit()
        except Exception as exc:
            self._failure(exc)
        finally:
            self._stop_workers()
            self._restore_graphics()
            self._snapshot()
            self._collect()
            self._close_mappings()
            self._verify_files()
            self._base_result()
            self._report()
        print('Evidence: '+str(self.work),flush=True)
        if self.error:raise RuntimeError(self.error)

    def _prepare(self):
        self.args=play_options(self.argv)
        if self.args.damage_textures is None:self.args.damage_textures=True
        os.environ['SFC_NATIVE_RESOLUTION']='1' if self.args.native_resolution else '0'
        if self.args.execute:
            if not C.windll.shell32.IsUserAnAdmin():
                raise RuntimeError('Use the established elevated testing parent. No automatic UAC requested.')
            if game_running():raise RuntimeError('Exit the existing SFC game normally before starting or recovering the isolated test.')
            from session_recovery import recover_pending
            recovered=recover_pending(game_running)
            if recovered:print('Recovered prior interrupted test: '+recovered,flush=True)
        preflight()
        from native_cohort import require_qualification
        self.q=require_qualification('ExtraFrame')
        self.checkout_backend=self.q['backend_inputs']
        json.dumps(self.q) # Preserve the pre-launch serialization boundary.
        if not CONTEXT.release:
            from evidence_storage import storage
            from evidence_budget import AGGREGATE_BYTES
            if storage()+544*1024*1024>AGGREGATE_BYTES:
                raise RuntimeError('Source timing reservation exceeds20GB evidence allowance')
        from component_qualification import require_qualification as require_light_qualification
        self.light_qualification=require_light_qualification()
        if not self.args.execute:
            print('Read-only preflight PASS. No game/renderer started.')
            print('Damage textures: '+('ON' if self.args.damage_textures else 'OFF'))
            print('Play session: untimed until game exit;minimal bounded recording')
            return False
        return True

    def _initialize(self):
        if not C.windll.shell32.IsUserAnAdmin():
            raise RuntimeError('Use the established elevated testing parent. No automatic UAC requested.')
        if game_running():raise RuntimeError('Exit the existing SFC game normally before starting the isolated test.')
        if not 120<=self.args.budget_seconds<=285:raise RuntimeError('Prepared workflow budget must be120..285seconds')
        self.work=CONTEXT.artifact('remix-runtime/runs')/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f-in-game')
        self.work.mkdir()
        if CONTEXT.release:
            from session_recording import mark
            mark(self.work,os.environ.get('SFC_RELEASE_RECORDING','off'))
        run_report.save(self.work,dict(result='IN_PROGRESS',probe='NATIVE-PLAY-SESSION-001',stage='prepared',final_report_complete=False))
        self.start=time.monotonic();self.deadline=float('inf')
        self.original=critical_hashes(SOURCE);self.paths=launcher_paths();self.compat=compat_flags()
        self.host_exe=BIN/'return_host.exe';self.addon=BIN/'SFCRemixReturn.dll'
        for src,name in ((self.host_exe,'renderer-host.bin'),(BIN/'return_launcher.exe','startup-launcher.bin'),(self.addon,'SFCRemixReturn.dll')):
            shutil.copyfile(src,self.work/name)
        build_files=(BIN/'return_host.exe',BIN/'return_launcher.exe',BIN/'SFCRemixReturn.dll')
        if not CONTEXT.release:build_files+=(DLL,)
        from pipeline_mode import policy
        from renderer_backend import receipt
        self.metadata=dict(probe='NATIVE-COHORT-001',utc=dt.datetime.now(dt.timezone.utc).isoformat(),
            accepted_critical_before=self.original,copied_critical_before=critical_hashes(TEST),
            copied_sfc_protected_sha256=protected_ini_sha256((TEST/'sfc.ini').read_bytes()),
            launcher_settings_before=self.paths,source_compatibility=self.compat,
            full_support_qualification=self.q,build_hashes={p.name:digest(p) for p in build_files},
            scene='Fresh retained ships through native insertion',play_session=True,
            capture_seconds=None,workflow_seconds=None,limits_bytes=32*1024*1024,
            pipeline_policy=policy('performance'),async_material_checkout=receipt(self.checkout_backend),
            native_all_ships=True,break_models=self.args.break_models,
            detail_policy='No frame trace or images;120 recent5second status samples;bounded console;functional assets cached once')
        (self.work/'manifest.json').write_text(json.dumps(self.metadata,indent=2))
        for name in ('host','launcher','controller','channel','receiver','pid','error','proxy_restored',
                     'light_relay','timing_relay','live_timing_result','exit_monitor'):
            setattr(self,name,None)
        for name in ('normal','gate_clean','host_shutdown_expected','tuning_exited','user_exited',
                     'capture_complete','controller_retired'):
            setattr(self,name,False)
        self.streams=[];self.history=[];self.phase_results={};self.last=0
        self.session_stage='startup';self.rollback=self.work/'dxgi-original.rollback'
        self.config_backup=self.work/'ReShade.original.ini';self.last_output_check=0

    def enforce(self):
        if self.exit_monitor:
            self.exit_monitor.check()
        if self.timing_relay and self.timing_relay.servicing:
            self.timing_relay.check_service()
        elif self.receiver:
            self.receiver.drain()
        if self.timing_relay and self.pid:
            self.timing_relay.poll(self.pid)
        if self.light_relay:
            self.light_relay.poll()
        self.now = time.monotonic()
        if self.now > self.deadline:
            raise RuntimeError('Prepared workflow time limit')
        if self.now - self.last_output_check < 5:
            return
        self.last_output_check = self.now
        if CONTEXT.release:
            return
        self.logs = sum((capture_file_bytes(p) for p in self.work.rglob('*') if p.suffix.lower() in ('.log', '.csv', '.jsonl')))
        if self.logs > 32 * 1024 * 1024:
            raise RuntimeError('Play-session logs exceed32MiB')
        return

    def _install_proxy(self):
        if self.full_support:
            shutil.copyfile(TEST / 'ReShade.ini', self.config_backup)
            graphics_transaction.install_test_proxy(TEST / 'dxgi.dll', self.rollback)

    def _start_host(self):
        self.host_env = {**os.environ, **ENV, 'DXVK_LOG_PATH': str(self.work)}
        self.host_env.update(SFC_PLAY_SESSION='1', SFC_PLAY_PARENT_PID=str(os.getpid()))
        self.host_env.pop('SFC_REMIX_TEXTURED_SHIP', None)
        self.host_env.pop('SFC_REMIX_LIGHT_WIRING', None)
        self.host_env.pop('SFC_LIGHT_TUNING', None)
        self.host = sp.Popen([str(self.host_exe), '--observe-only'], cwd=self.work, env=self.host_env, stdout=self.out('host.log'), stderr=sp.STDOUT, creationflags=sp.CREATE_NO_WINDOW)

    def _wait_host(self):
        self.session = None
        self.until = time.monotonic() + 60
        while time.monotonic() < self.until:
            self.enforce()
            if self.host.poll() is not None:
                raise RuntimeError('Renderer exited before session ready')
            self.session = next((s[8:] for s in (self.work / 'host.log').read_text(errors='replace').splitlines() if s.startswith('SESSION ')), None)
            if self.session:
                break
            time.sleep(0.1)
        if not self.session or not valid_name(self.session):
            raise RuntimeError('Renderer startup/session failed')
        self.channel = Channel(self.session)
        self.metadata['return_session'] = self.session
        if self.full_support:
            self.metadata['full_support_qualification'] = self.q
        (self.work / 'manifest.json').write_text(json.dumps(self.metadata, indent=2))

    def _prepare_game(self):
        self.env = {**os.environ, 'SFC_REMIX_RETURN_SESSION': self.session, 'SFC_REMIX_EXPECTED_IMAGE': str(TEST / 'StarFleetOP.exe'), 'SFC_REMIX_PRELOAD_REQUIRED': '1'}
        self.env['SFC_PLAY_SESSION'] = '1'
        self.env['SFC_REMIX_INSPECT_VISIBILITY'] = '0'
        self.env.pop('SFC_REMIX_BROAD_OUTPUT', None)
        self.env.pop('SFC_REMIX_DEPTH_OUTPUT', None)
        self.env.pop('SFC_REMIX_CALIBRATION_SCENE', None)
        self.env.pop('SFC_REMIX_CAPTURE_SHIP_IMAGE', None)
        self.env.pop('SFC_REMIX_CAPTURE_SHIP_IMAGE_DELAY_MS', None)
        self.env.pop('SFC_NATIVE_LIGHT_DISCOVERY', None)
        self.env.pop('SFC_LIGHT_TUNING', None)
        self.env.pop('SFC_D3D9_SOURCE_TIMING', None)
        self.env.pop('SFC_D3D9_LIVE_TIMING', None)
        self.env['SFC_D3D9_SOURCE_TIMING'] = '1'
        self.env['SFC_D3D9_LIVE_TIMING'] = '1'
        self.env.pop('SFC_D3D9_GAME_OUTPUT', None)
        self.env.pop('SFC_LIFECYCLE_CAPTURE', None)
        self.env.update(SFC_D3D9_GAME_OUTPUT='1', SFC_LIGHT_TUNING='1')
        self.env.pop('SFC_D3D9_SHARED_LIGHTS', None)
        self.env.pop('SFC_PERSISTENT_SCENE', None)
        self.env.pop('SFC_D3D9_SYNC_BUFFER', None)
        self.env.pop('SFC_D3D9_MULTISCENE', None)
        self.env['SFC_D3D9_MULTISCENE'] = '1'
        self.env['SFC_D3D9_PLAYER_REPLACEMENT'] = '1'
        self.env['SFC_NATIVE_INSERTION_ALL_SHIPS'] = '1'
        self.env['SFC_DAMAGE_TEXTURES'] = '1' if self.args.damage_textures else '0'
        self.env['SFC_BREAK_SCENE'] = '1' if self.args.break_models else '0'
        self.env['SFC_D3D9_NATIVE_FOREGROUND'] = '0'
        self.env['SFC_NATIVE_INSERTION_OBSERVE'] = '0'
        self.env['SFC_NATIVE_INSERTION_GATE'] = '1'
        if CONTEXT.release:
            from portable_reshade import prepare as prepare_portable_reshade
            self.prepare_portable_reshade = prepare_portable_reshade
            self.env.update(self.prepare_portable_reshade(CONTEXT, self.work))
        self.env.pop('SFC_NATIVE_GATE_BASELINE', None)
        self.env.pop('SFC_NATIVE_GATE_FIXTURE_DELAYS', None)
        self.env['SFC_NATIVE_INSERTION_POLICY'] = 'ExtraFrame'
        self.env.pop('SFC_REPLACEMENT_FIXTURE_FAULTS', None)
        self.env['SFC_PIPELINE_MODE'] = 'performance'
        self.env['SFC_D3D9_SYNC_BUFFER'] = '1'
        self.env['SFC_PERSISTENT_SCENE'] = '1'
        self.env['SFC_D3D9_SHARED_LIGHTS'] = '1'
        self.env['SFC_NATIVE_LIGHT_DISCOVERY'] = '1'
        from scene_receiver import Receiver
        self.Receiver = Receiver
        if self.receiver is None:
            self.receiver = self.Receiver(break_models=self.args.break_models)
        from async_material_checkout import Relay
        self.Relay = Relay
        self.mode_args = {'pipeline_mode': 'performance'}
        self.mode_args['checkout_backend'] = self.checkout_backend
        self.timing_relay = self.Relay(self.work, self.receiver, TEST, additive=True, persistent=True, buffered=True, **self.mode_args)
        self.timing_relay.light_diagnostics = False
        self.timing_relay.damage_textures = self.args.damage_textures
        self.timing_relay.completion_diagnostics = False
        self.timing_relay.play_session = True
        self.timing_relay.live_tuning = False
        self.timing_relay.native_gate_policy = 'ExtraFrame'
        self.timing_relay.native_all_ships = True
        self.timing_relay.break_models = self.args.break_models
        self.timing_relay.legacy_startup_warmup = False
        self.env['SFC_REMIX_CALIBRATION_SCENE'] = self.receiver.name
        self.env.pop('SFC_REMIX_VISIBLE_SHIP', None)
        self.env.pop('SFC_REMIX_TEXTURED_SHIP', None)
        self.component_path = CONTEXT.artifact('remix-runtime/native-light-tests/m1_light_component.dll')
        self.metadata['semantic_calibration'] = {'probe': 'REMIX-CALIBRATION-001', 'scene_session': self.receiver.name, 'maximum_asset_revisions': ASSETS, 'geometry_hook': False, 'same_process_render_thread_required': True, 'component_sha256': digest(self.component_path)}
        from multi_scene_resources import policy
        self.policy = policy
        self.metadata.update(probe='D3D9-MULTISHIP-001', scene='Fresh retained multi-model diagnostic;placement recorded in live-owner analysis', original_suppressed=False, tracked_set_capacity=OWNERS, asset_revisions=ASSETS, image_limit_bytes=self.policy()['aggregate_cap_bytes'], image_policy=self.policy())
        self.metadata.update(probe='NATIVE-GATE-001', scene='Exact-ticket native colour/depth insertion before subsequent engine effects/text', timing_policy='ExtraFrame', reference_hz=60, shield_replay=False, late_composition=False, fallback='Original selected lists remain intact for an uncommitted owner/frame', detail_bytes=8 * 1024 * 1024, display_policy='Current native source frame;absolute deadline;commit colour/depth before zero-count suppression', synchronized_buffer=dict(frames=0, complete_native_HUD_delayed=False, prediction=False, stale_overlay_hold=False, coordinator='Absolute source-frame deadline;immutable completed-output lease'))
        self.metadata.update(probe='NATIVE-COHORT-001', scope='Supported retained ships;per-owner native suppression and physical owner coverage;one shared frame lease', native_all_ships=True, break_models=self.args.break_models)
        (self.work / 'manifest.json').write_text(json.dumps(self.metadata, indent=2))
        self.env.pop('SFC_REMIX_SCENE_DEPTH', None)

    def _launch_game(self):
        if self.compat:
            self.flags = [s for s in self.compat.split() if s != '~']
            if any((s.upper() == 'RUNASINVOKER' for s in self.flags)):
                raise RuntimeError('Existing invoker override requires explicit review; not propagated')
            self.env['__COMPAT_LAYER'] = ' '.join(self.flags)
        self.launcher = sp.Popen([str(BIN / 'return_launcher.exe'), '--game', str(TEST / 'StarFleetOP.exe'), str(self.work / 'SFCRemixReturn.dll'), CLIENT, digest(self.work / 'SFCRemixReturn.dll')], cwd=TEST, env=self.env, stdout=self.out('launcher.log'), stderr=sp.STDOUT, creationflags=sp.CREATE_NO_WINDOW)
        self.exit_monitor = Monitor(self.launcher, self.work / 'launcher.log')
        self.until = time.monotonic() + 20
        while time.monotonic() < self.until:
            self.enforce()
            self.text = (self.work / 'launcher.log').read_text(errors='replace')
            self.match = re.search('VERIFIED_CHILD pid=(\\d+) suspended_path_match=1 disk_sha_match=1', self.text)
            if self.match:
                self.pid = int(self.match[1])
                break
            if self.launcher.poll() is not None:
                raise RuntimeError('Verified copied client did not launch')
            time.sleep(0.1)
        try:
            if not self.pid or Path(image_path(self.pid)) != TEST / 'StarFleetOP.exe':
                raise RuntimeError('Actual process path does not match isolated test copy; no gate activated')
            self.exit_monitor.attach(self.pid)
        except OSError:
            self.exit_monitor.check()
            raise

    def _after_launch(self):
        self.timing_relay.start_on_launch(self.pid)

    def _await_device(self):
        self.ready_at = time.monotonic()
        wait_component_ready(self.channel.snapshot, self.pid, self.launcher.poll, self.enforce)
        self.metadata['graphics_ready_wait_seconds'] = time.monotonic() - self.ready_at
        self.session_stage = 'mission_selection'
        self.metadata['gate_build_hashes'] = {p.name: digest(p) for p in (CONTEXT.artifact('m1/bin/m1_controller.exe'), CONTEXT.artifact('m1/bin/m1_gate.dll'))}
        (self.work / 'manifest.json').write_text(json.dumps(self.metadata, indent=2))

    def _instructions(self):
        print('Start your campaign or skirmish when ready. No session or battle-selection timer.',flush=True)

    def _configure_controller(self):
        self.controller_exe=CONTEXT.artifact('m1/bin/m1_controller.exe')
        self.gate=CONTEXT.artifact('remix-runtime/native-light-tests/m1_light_component.dll')
        self.gate_dir=self.work/'gate';self.gate_dir.mkdir();self.config=self.gate_dir/'component.ini'
        write_native_config(self.config,'[m1]\nOutputDirectory='+str(self.gate_dir)+'\nControllerPath='+str(self.controller_exe)+
            '\nMaxSeconds=0\nStopOnBurst=0\nMaxFrames=120\nMaxEvents=10000\nMaxOwners='+str(OWNERS)+
            '\nWarningBytes=16777216\nHardBytes=33554432\nEnableGeometryHook=0\nEnableWrapperObservation=1'+
            '\nEnableMeshExport=1\nEnableTextureReferences=1\nEnablePrivateCopy=0\nLiveChannel='+self.receiver.name+'\n')
        self.controller_args=[str(self.controller_exe),'--pid',str(self.pid),'--dll',str(self.gate),
            '--config',str(self.config),'--max-seconds','0','--stop-on-burst','0',
            '--already-loaded','0','--unload-after-stop','1','--gate-timeout-seconds','0']
        self.gate_timeout=120
        self.metadata['gate_timeout_seconds']=None
        (self.work/'manifest.json').write_text(json.dumps(self.metadata,indent=2))

    def _launch_controller(self):
        self.controller=sp.Popen(self.controller_args,cwd=ROOT,env=self.env,stdout=self.out('gate-controller.log'),
            stderr=sp.STDOUT,creationflags=sp.CREATE_NO_WINDOW)

    def _start_controller(self):
        self._launch_controller()
        wait_live_gate(self.pid,self.controller,self.enforce,timeout=None)
        self.controller_gate_observed=time.monotonic();self.session_stage='tactical'

    def _check_observers(self):
        self.state = self.channel.snapshot()

    def _arm(self):
        if self.state['gamePid'] != self.pid or not self.state['startupRestored'] or (not self.state['startupVerified']) or (not self.state['ready']):
            raise RuntimeError('Image component startup/device not qualified; original game remains normal')
        self.channel.set('armed', 1)
        self.channel.set('enabled', int(self.output_enabled))
        winsound.Beep(880, 200)
        self.active = time.monotonic()
        self.phase = -1

    def _begin_observation(self):
        print('UNTIMED PLAY:replacement and damage stay enabled across menus/battles. Exit SFC normally to clean up.',flush=True)

    def _normal_exit(self):
        self.normal = True
        self.user_exited = True
        self.tuning_exited = False
        self.capture_complete = True
        print('SFC exited normally. Cleaning up the renderer,workers and test setup now.', flush=True)

    def _failure(self, exc):
        self.error = str(exc)
        print('Test stopped safely: ' + self.error, flush=True)
        if self.pid and (not self.normal):
            print('Please exit SFC normally so graphics files can be restored.', flush=True)

    def _stop_extensions(self):
        pass

    def _stop_workers(self):
        self._stop_extensions()
        if self.channel:
            self.channel.set('enabled', 0)
            self.channel.set('stop', 1)
        if self.timing_relay:
            try:
                self.timing_relay.stop()
            except Exception as exc:
                self.error = (self.error + '; ' if self.error else '') + 'Renderer worker shutdown: ' + str(exc)
        if self.normal:
            try:
                self.controller_retired = retire_controller(self.controller, True)
            except Exception as exc:
                self.error = (self.error + '; ' if self.error else '') + 'Exited-game controller shutdown: ' + str(exc)
        if self.error and self.launcher and self.pid and (self.launcher.poll() is None):
            print('Waiting briefly for normal game exit before restoring the test setup.', flush=True)
            self.until = min(self.deadline, time.monotonic() + 30)
            while self.launcher.poll() is None and time.monotonic() < self.until:
                time.sleep(0.1)
            self.normal = self.launcher.poll() == 0 and 'CHILD_EXIT code=0' in (self.work / 'launcher.log').read_text(errors='replace')
        if self.host and self.host.poll() is None:
            try:
                self.host.wait(timeout=8)
            except sp.TimeoutExpired:
                self.host.terminate()
                self.host.wait(timeout=5)
        if self.launcher and self.launcher.poll() is None:
            self.launcher.terminate()
            self.launcher.wait(timeout=5)

    def _restore_graphics(self):
        if self.full_support and self.rollback.exists():
            if game_running():
                self.proxy_restored = False
                self.error = (self.error + '; ' if self.error else '') + 'Game still running: proxy rollback deferred; exit normally then restore verified backup'
            else:
                try:
                    if (TEST / 'ReShade.log').exists() and (TEST / 'ReShade.log').stat().st_size <= 16 * 1024 * 1024:
                        shutil.copyfile(TEST / 'ReShade.log', self.work / 'ReShade.full-support.log')
                    graphics_transaction.restore_test_proxy(TEST / 'dxgi.dll', self.rollback)
                    self.proxy_restored = True
                    if digest(self.config_backup) != self.metadata['copied_critical_before']['ReShade.ini']:
                        raise ValueError('Copied configuration rollback hash mismatch')
                    shutil.copyfile(TEST / 'ReShade.ini', self.work / 'ReShade.after-test.ini')
                    shutil.copyfile(self.config_backup, TEST / 'ReShade.ini')
                except Exception as exc:
                    self.proxy_restored = False
                    self.error = (self.error + '; ' if self.error else '') + str(exc)

    def _snapshot(self):
        self.final = self.channel.snapshot() if self.channel else None
        if self.launcher and self.launcher.poll() == 0 and ('CHILD_EXIT code=0' in (self.work / 'launcher.log').read_text(errors='replace')):
            self.normal = True
        if self.normal and self.controller and (self.controller.poll() is None):
            try:
                self.controller_retired = retire_controller(self.controller, True) or self.controller_retired
            except Exception as exc:
                self.error = (self.error + '; ' if self.error else '') + 'Exited-game controller shutdown: ' + str(exc)

    def _collect(self):
        if self.timing_relay:
            try:self.live_timing_result=self.timing_relay.finish_play(self.pid)
            except Exception as exc:self.error=(self.error+'; ' if self.error else '')+'Live owner timing: '+str(exc)

    def _close_mappings(self):
        if self.channel:
            self.channel.close()
        if self.exit_monitor:
            self.exit_monitor.close()
        if self.receiver:
            if self.timing_relay and self.timing_relay.servicing and self.timing_relay.service.thread.is_alive():
                self.error = (self.error + '; ' if self.error else '') + 'Recovery service still owns mapping;close deferred'
            else:
                self.receiver.close()
        for f in self.streams:
            f.close()

    def _verify_files(self):
        self.after = critical_hashes(SOURCE)
        self.paths_after = launcher_paths()
        self.copy_after = critical_hashes(TEST)
        self.original_changed = bool(changed_protected_files(self.original, self.after, (SOURCE / 'sfc.ini').read_bytes(), self.metadata['copied_sfc_protected_sha256'])) if CONTEXT.release else self.after != self.original
        if self.original_changed or self.paths_after != self.paths:
            self.error = (self.error + '; ' if self.error else '') + 'Accepted installation or launcher settings changed'
        if self.copy_after['StarFleetOP.exe'] != CLIENT:
            self.error = (self.error + '; ' if self.error else '') + 'Copied client hash changed'
        self.copy_protected_changes = changed_protected_files(self.metadata['copied_critical_before'], self.copy_after, (TEST / 'sfc.ini').read_bytes(), self.metadata['copied_sfc_protected_sha256'])
        if self.full_support and self.copy_protected_changes:
            self.error = (self.error + '; ' if self.error else '') + 'Copied critical baseline not fully restored'

    def _base_result(self):
        self.result = {'probe': 'REMIX-RETURN-001', 'error': self.error, 'seconds': time.monotonic() - self.start, 'target_pid': self.pid, 'normal_game_exit': self.normal, 'gate_clean_unloaded': self.gate_clean, 'gate_controller_pid': self.controller.pid if self.controller else None, 'gate_controller_exit': self.controller.poll() if self.controller else None, 'gate_controller_left_running': self.controller is not None and self.controller.poll() is None, 'renderer_exit': self.host.returncode if self.host else None, 'original_critical_unchanged': not self.original_changed, 'launcher_settings_unchanged': self.paths_after == self.paths, 'accepted_critical_after': self.after, 'copied_critical_after': self.copy_after, 'history': self.history, 'phases': self.phase_results, 'final': self.final, 'sponsor_visible_behavior': 'PENDING sponsor report', 'result': 'RUNTIME_REVIEW_REQUIRED' if not self.error else 'PARTIAL'}

    def _observe(self):
        self.phase=0
        self.phase_results['0']={'seconds':0,'start':self.channel.snapshot()}
        self.channel.set('enabled',1)
        while True:
            self.enforce()
            elapsed=time.monotonic()-self.active
            state=self.channel.snapshot()
            if state['error']:raise RuntimeError('Image component reported an error; original rendering retained')
            self.exit_monitor.check()
            if self.host.poll() is not None and not self.host_shutdown_expected:
                raise RuntimeError('Renderer exited unexpectedly; original rendering retained')
            if elapsed-self.last>5:
                self.history.append({'seconds':elapsed,'phase':0,**state})
                self.last=elapsed
                if len(self.history)>120:del self.history[0]
            time.sleep(.05)

    def _end_observation(self):
        pass # Untimed play exits through the verified process-exit signal.

    def _report(self):
        gate_status=(self.live_timing_result or {}).get('native_gate_summary') or {}
        healthy=not(self.error or gate_status.get('error') or gate_status.get('partial'))
        self.result.update(probe='NATIVE-PLAY-SESSION-001',play_session=True,
            workflow_seconds=None,capture_seconds=None,early_game_exit=False,
            result='PLAY_SESSION_FINISHED_NORMAL_EXIT' if self.normal and healthy else 'PARTIAL_PLAY_SESSION',
            diagnostic_capture=False,damage_textures=self.args.damage_textures,
            native_all_ships=True,break_models=self.args.break_models,timing_policy='ExtraFrame',
            copied_player_preferences_changed=self.copy_after['sfc.ini']!=self.metadata['copied_critical_before']['sfc.ini'] and 'sfc.ini' not in self.copy_protected_changes,
            broad_proxy_restored=self.proxy_restored,final_report_complete=True,
            observation_complete=self.capture_complete,exit_stage=self.session_stage,
            controller_retired_after_game_exit=self.controller_retired,
            cleanup_mode='controlled live unload' if self.gate_clean else 'process-exit reclamation')
        run_report.save(self.work,self.result)

def main(argv=None):
    Session(argv).run()

def cli():
    try:main()
    except BaseException as exc:
        run_report.failure(exc)
        raise

if __name__=='__main__':cli()
