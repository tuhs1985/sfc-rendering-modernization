"""Explicit opt-in returned-image test. Accepted installation is read-only input."""
from pathlib import Path
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
from return_channel import Channel,valid_name,visibility_result
import run_report
import depth_search_channel
import broad_capture
from run_return_fixture import ROOT,BIN,DLL,TEST,ENV,digest

SOURCE=Path(r'C:\Games\Taldren Software Inc\Starfleet Command Orion Pirates')
CLIENT='4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29'
CRITICAL=('StarFleetOP.exe','DDraw.dll','D3DImm.dll','dxgi.dll','dgVoodoo.conf','ReShade.ini','sfc.ini')

def observation_phase(elapsed,continuous=False):
    """Routine textured observation stays on; diagnostic fallback cycle is retained."""
    return 0 if continuous else (0 if elapsed<30 else 1 if elapsed<45 else 2 if elapsed<60 else 3)

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
        if poll() is not None:raise RuntimeError('Game exited during graphics initialization')
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
    deadline=time.monotonic()+timeout;event=None
    try:
        while time.monotonic()<deadline:
            enforce()
            if controller.poll() is not None:raise RuntimeError('Semantic controller exited before tactical gate')
            if not event:event=k.OpenEventW(0x100000,False,f'Local\\SFCM1TacticalGate_{pid}')
            if event and k.WaitForSingleObject(event,0)==0:return
            time.sleep(.05)
        raise RuntimeError('Semantic tactical gate timeout')
    finally:
        if event:k.CloseHandle(event)
def preflight():
    if digest(SOURCE/'StarFleetOP.exe')!=CLIENT or digest(TEST/'StarFleetOP.exe')!=CLIENT:raise RuntimeError('Original/copied client hash mismatch')
    if digest(DLL)!='F7C310821AA98BCDFDEC120330B0A89457B7C5EBA58D21464AF32639611C809F':raise RuntimeError('Pinned runtime mismatch')
    if digest(TEST/'dxgi.dll')!='E35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7':raise RuntimeError('Copied proxy mismatch')
    for p in (BIN/'return_launcher.exe',BIN/'return_host.exe',BIN/'SFCRemixReturn.dll',ROOT/'artifacts/m1/bin/m1_gate.dll',ROOT/'artifacts/m1/bin/m1_controller.exe'):
        if not p.is_file():raise RuntimeError('Prepared build missing: '+str(p))
    # Critical copied configuration is unchanged from independent preparation;
    # generated log/screenshot files are deliberately not part of this freeze.
    manifest=json.loads((ROOT/'artifacts/remix-runtime/test-install/source-copy-files.json').read_text(encoding='utf-8-sig'))
    expected={v['path'].lower():v['copy_sha256'] for v in manifest}
    for name,sha in critical_hashes(TEST).items():
        if expected.get(name.lower())!=sha:raise RuntimeError('Copied baseline changed: '+name)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');parser.add_argument('--budget-seconds',type=int,default=285)
    inspect=parser.add_mutually_exclusive_group()
    inspect.add_argument('--inspect-visibility',action='store_true',help='At most eight read-only late depth-binding observations; no suppression')
    inspect.add_argument('--inspect-early-depth',action='store_true',help='Eight read-only pre-effects Present depth-binding observations; no suppression')
    inspect.add_argument('--search-depth',action='store_true',help='Continuous bounded six-phase engine/presentation depth search')
    inspect.add_argument('--broad-capture',action='store_true',help='Approved full-support public event burst;10seconds/2GB')
    inspect.add_argument('--depth-snapshots',action='store_true',help='Three paired depth/color snapshots,20seconds,no rendering changes')
    inspect.add_argument('--source-timing',action='store_true',help='Read-only semantic-offer to presentation timing;no Remix runtime/image')
    parser.add_argument('--live-owner-timing',action='store_true',help='Fresh raw semantic owner to separate ordinary-D3D9 renderer;no game drawing')
    parser.add_argument('--d3d9-additive',action='store_true',help='Qualified ordinary-D3D9 extra ship;original rendering untouched')
    parser.add_argument('--lifecycle-capture',action='store_true',help='Separate bounded camera-gap/destruction observations;no native death inference')
    parser.add_argument('--camera-recovery',action='store_true',help='Two alive camera-away/back checks;no destruction requested')
    parser.add_argument('--offscreen-position',action='store_true',help='Default-off external read-only ship position across camera gaps;not renderer input')
    parser.add_argument('--persistent-scene',action='store_true',help='Simulation-driven retained native instances;player-ship display first')
    parser.add_argument('--synchronized-buffer',action='store_true',help='One complete game-frame delay paired with same-frame ship/depth;default off')
    parser.add_argument('--multi-ship',action='store_true',help='Fresh retained different models,configured camera-left diagnostic;originals remain')
    parser.add_argument('--experimental-parallel-assets',action='store_true',help='Sponsor-authorized experimental checkout: parallel parts/progressive materials;late-update delivery gate remains unresolved')
    parser.add_argument('--pipeline-mode',choices=('performance','test'),default='performance',help='Performance baseline;test adds diagnostic comparisons. Essential safeguards remain in both')
    inspect.add_argument('--private-ship',action='store_true',help='Fresh semantic SDK ship return into private game-side target;no visible change')
    inspect.add_argument('--visible-ship',action='store_true',help='Fresh matching magenta ship at world-offset position in original camera viewport;original ships unchanged')
    inspect.add_argument('--textured-ship',action='store_true',help='Original textures,screen-resolution output,bounded delayed additive display;no suppression')
    parser.add_argument('--observation-only',action='store_true',help='Use control-only host; do not start Remix or display triangle')
    parser.add_argument('--calibration',action='store_true',help='Opt-in current-frame semantic records paired with three depth snapshots')
    parser.add_argument('--capture-ship-image',action='store_true',help='One exact prepared textured ship-layer image;external readback only')
    parser.add_argument('--capture-native-lights',action='store_true',help='Read-only bounded native light bank discovery;no lighting changes')
    parser.add_argument('--light-wiring',action='store_true',help='Normal90s two-native-directional-light/config wiring check;not long tuning mode')
    parser.add_argument('--light-tuning',action='store_true',help='Low-recording live controls until normal game exit;30minute tactical ceiling')
    parser.add_argument('--scene-depth',action='store_true',help='Default-off depth-filtered additive ship;original drawing/UI path unchanged')
    args=parser.parse_args()
    if args.experimental_parallel_assets and (not args.multi_ship or args.pipeline_mode!='performance'):
        parser.error('--experimental-parallel-assets requires --multi-ship --pipeline-mode performance')
    if args.experimental_parallel_assets:
        print('EXPERIMENTAL PARALLEL ASSETS ENABLED: within-ship tasks and progressive materials. Late material updates may interrupt the extra ships;original SFC drawing stays enabled.',flush=True)
    if args.multi_ship:args.d3d9_additive=True;args.synchronized_buffer=True
    if args.synchronized_buffer:
        if not args.d3d9_additive:parser.error('--synchronized-buffer requires --d3d9-additive')
        args.persistent_scene=True
        from qualify_synchronized_buffer import require_qualification as buffer_qualified
        if not args.multi_ship:buffer_qualified()
    if args.persistent_scene:
        if not args.d3d9_additive or args.offscreen_position:parser.error('--persistent-scene requires additive and excludes diagnostic external reader')
        args.camera_recovery=True
        from qualify_persistent_scene import require_qualification as persistent_qualified
        if not args.multi_ship:persistent_qualified()
    if args.scene_depth:
        if args.light_tuning or args.capture_ship_image:parser.error('--scene-depth is a bounded standalone test,not tuning/image capture')
        args.light_wiring=True
    if args.light_tuning:args.light_wiring=True
    if args.light_wiring:args.capture_native_lights=True
    if args.capture_native_lights:args.textured_ship=True
    if args.capture_ship_image:args.textured_ship=True
    if args.textured_ship:args.visible_ship=True
    if args.visible_ship:args.private_ship=True
    if args.offscreen_position:
        if not args.d3d9_additive:parser.error('--offscreen-position requires --d3d9-additive')
        args.camera_recovery=True
        from offscreen_position import verify_client
        verify_client(TEST/'StarFleetOP.exe')
        from qualify_offscreen_position import require_qualification as offscreen_qualified
        offscreen_qualified()
    if args.camera_recovery:args.lifecycle_capture=True
    if args.multi_ship and args.pipeline_mode=='performance':args.lifecycle_capture=False
    if args.lifecycle_capture and not args.d3d9_additive:parser.error('--lifecycle-capture requires --d3d9-additive')
    if args.lifecycle_capture:
        from qualify_lifecycle_capture import require_qualification as lifecycle_qualified
        if not args.multi_ship:lifecycle_qualified()
    if args.d3d9_additive:
        if args.private_ship or args.calibration or args.light_tuning or args.broad_capture or args.depth_snapshots or args.search_depth:parser.error('--d3d9-additive is separate from SDK/private/capture modes')
        args.source_timing=True;args.live_owner_timing=True;args.observation_only=True;args.capture_native_lights=True
    if args.private_ship and (args.calibration or args.observation_only):parser.error('--private-ship is separate from calibration/observation-only')
    semantic_enabled=args.calibration or args.private_ship or args.source_timing
    if args.live_owner_timing and not(args.source_timing and args.observation_only):parser.error('--live-owner-timing requires --source-timing --observation-only')
    live_bin=ROOT/'artifacts/remix-runtime/live-return-bin'
    if args.calibration and not (args.depth_snapshots and args.observation_only):parser.error('--calibration requires --depth-snapshots --observation-only')
    if args.observation_only and not (args.inspect_early_depth or args.search_depth or args.broad_capture or args.depth_snapshots or args.source_timing):parser.error('--observation-only requires --inspect-early-depth or --search-depth or --broad-capture or --depth-snapshots or --source-timing')
    if args.source_timing and (not args.observation_only or args.private_ship or args.calibration):parser.error('--source-timing requires observation-only and excludes private/calibration render modes')
    if args.depth_snapshots and not args.observation_only:parser.error('--depth-snapshots requires --observation-only')
    full_support=args.broad_capture or args.depth_snapshots or args.scene_depth or args.d3d9_additive
    if args.broad_capture and not args.observation_only:parser.error('--broad-capture requires --observation-only')
    if args.search_depth and not args.observation_only:parser.error('--search-depth requires --observation-only')
    if args.execute:
        if not C.windll.shell32.IsUserAnAdmin():raise RuntimeError('Use the established elevated testing parent. No automatic UAC requested.')
        if game_running():raise RuntimeError('Exit the existing SFC game normally before starting or recovering the isolated test.')
        if full_support:
            from recover_broad_session import recover_pending
            recovered=recover_pending(game_running)
            if recovered:print('Recovered prior interrupted test: '+recovered,flush=True)
    preflight()
    if args.source_timing:
        if args.multi_ship:from qualify_multiship import require_qualification
        elif args.d3d9_additive:from additive_qualification import require_qualification
        elif args.live_owner_timing:from live_owner_timing import require_qualification
        else:from source_timing import require_qualification
        q=require_qualification()
        import sys
        sys.path.insert(0,str(ROOT/'tools/d3d9_proof'))
        from run_offline import storage,AGGREGATE_BYTES
        reserve=(192 if args.d3d9_additive else 128 if args.live_owner_timing else 64)*1024*1024
        if storage()+reserve>AGGREGATE_BYTES:raise RuntimeError('Source timing reservation exceeds20GB evidence allowance')
    if args.capture_native_lights:
        from light_discovery import require_qualification as require_light_qualification
        light_qualification=require_light_qualification()
    if args.private_ship:
        from live_return import require_qualification as require_private_qualification
        require_private_qualification(visible=args.visible_ship,textured=args.textured_ship,capture_image=args.capture_ship_image,light_wiring=args.light_wiring)
        for path in (live_bin/'ship_live_host.exe',live_bin/'SFCRemixReturn.dll'):
            if not path.is_file():raise RuntimeError('Private return build missing: '+str(path))
        q=json.loads((ROOT/'artifacts/remix-runtime/deps/present-calibration-qualification.json').read_text())
        if q['component_sha256']!=digest(ROOT/'artifacts/m1/bin/m1_component.dll'):raise RuntimeError('Accepted semantic component changed; requalify ABI before private test')
    if args.calibration and not (ROOT/'artifacts/m1/bin/m1_component.dll').is_file():raise RuntimeError('Full semantic component build required')
    if args.calibration:
        from present_calibration import require_qualification as require_calibration
        require_calibration()
    if args.scene_depth:
        from scene_depth import require_qualification as require_depth_test
        require_depth_test()
    if full_support and not args.scene_depth and not args.d3d9_additive:
        broad_capture.qualified_full()
        broad_capture.reserve_capture_budget()
        qualification=ROOT/'artifacts/remix-runtime/deps/reshade-full-6.7.1/qualification.json'
        q=json.loads(qualification.read_text())
        if q.get('proxy_sha256')!=broad_capture.FULL_SHA or q.get('result')!='OFFLINE_EVENT_AND_STATE_PASS':raise RuntimeError('Full-support offline qualification missing')
        from prepare_full_reshade import source_hashes
        if q.get('source_hashes')!=source_hashes():raise RuntimeError('Broad collector sources changed since offline qualification; requalify first')
        if args.depth_snapshots:
            from depth_snapshot_analysis import require_qualification
            require_qualification()
    inspect_requested=args.inspect_visibility or args.inspect_early_depth
    if not args.execute:print('Read-only preflight PASS. No game/renderer started.');return
    if not C.windll.shell32.IsUserAnAdmin():raise RuntimeError('Use the established elevated testing parent. No automatic UAC requested.')
    if game_running():raise RuntimeError('Exit the existing SFC game normally before starting the isolated test.')
    if not 120<=args.budget_seconds<=285:raise RuntimeError('Prepared workflow budget must be120..285seconds')
    if args.textured_ship:
        reserve=384*1024*1024 #128MiB images+32MiB evidence,plus worst-case archive coexistence
        if broad_capture.storage_bytes()+reserve>broad_capture.OVERALL or shutil.disk_usage(ROOT).free<reserve:raise RuntimeError('Textured run/archive exceeds available20GB allowance or disk space')
    work=ROOT/'artifacts/remix-runtime/runs'/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f-in-game');work.mkdir()
    run_report.save(work,dict(result='IN_PROGRESS',probe='REMIX-RETURN-001',stage='prepared',
                              light_wiring=args.light_wiring,final_report_complete=False))
    start=time.monotonic();deadline=start+(1980 if args.light_tuning else args.budget_seconds)
    original=critical_hashes(SOURCE);paths=launcher_paths();compat=compat_flags()
    host_exe=live_bin/'ship_live_host.exe' if args.private_ship else BIN/'return_host.exe'
    addon=live_bin/'SFCRemixReturn.dll' if args.private_ship else BIN/'SFCRemixReturn.dll'
    for src,name in [(host_exe,'renderer-host.bin'),(BIN/'return_launcher.exe','startup-launcher.bin'),(addon,'SFCRemixReturn.dll')]:shutil.copyfile(src,work/name)
    metadata={'probe':'REMIX-RETURN-001','utc':dt.datetime.now(dt.timezone.utc).isoformat(),'accepted_critical_before':original,'copied_critical_before':critical_hashes(TEST),'launcher_settings_before':paths,'source_compatibility':compat,'scene':'SDK default-material triangle with green sphere light; no SFC draw suppression','output_resources_bytes':2*256*256*4,'capture_seconds':90,'workflow_seconds':args.budget_seconds,'limits_bytes':32*1024*1024,'build_hashes':{p.name:digest(p) for p in (BIN/'return_host.exe',BIN/'return_launcher.exe',BIN/'SFCRemixReturn.dll',DLL)}}
    metadata['visibility_probe']={'enabled':inspect_requested,'scope':'early-present' if args.inspect_early_depth else 'late-overlay','max_samples':8,'minimum_interval_ms':1000,'read_only':True,'qualified_scene_depth':False}
    metadata['observation_only']=args.observation_only
    metadata['scene_depth_test']=args.scene_depth
    if args.source_timing:metadata.update(probe='D3D9-SOURCE-TIMING-001',scene='Metadata-only semantic offer to Present/overlay;no image or Remix runtime',output_resources_bytes=0,
        source_timing={'geometry_hook':False,'record_capacity':32768,'record_bytes':80,'max_detailed_owners_per_callback':8,'storage_bytes':2621568,'stages':['present','overlay'],'source_qpc_extension_words':[89,90,91,92,93]})
    metadata['light_tuning']=args.light_tuning
    from pipeline_mode import policy as mode_policy
    metadata['pipeline_policy']=mode_policy(args.pipeline_mode)
    metadata['experimental_parallel_assets']=args.experimental_parallel_assets
    if args.light_tuning:metadata.update(capture_seconds=1800,workflow_seconds=1980,detail_policy='100 scene rows per owner;latest-only native bank;5second presentation samples')
    if args.private_ship:
        metadata.update(probe='REMIX-LIVE-RETURN-001',scene='Fresh selected ship rendered by SDK to PRIVATE game-side target;no backbuffer changes',output_resources_bytes=4*256*256*4)
        metadata['private_ship']={'strict_current_frame':True,'saved_template':False,'expected_visible_change':bool(args.visible_ship),'host_sha256':digest(host_exe),'addon_sha256':digest(addon)}
        if args.visible_ship:metadata['scene']='Fresh SDK magenta ship at diagnostic WORLD offset in original camera viewport;transparent background,original ships ON,no scene-depth or replacement claim'
        if args.textured_ship:metadata.update(scene='Fresh original primary textures,1920x1080 output,100ms delayed additive copy;NOT synchronized replacement',output_resources_bytes=4*1920*1080*4,image_limit_bytes=128*1024*1024,display_policy='v4 source request age<=100ms;captured pose/camera retained')
        if args.textured_ship:metadata['private_ship'].update(strict_current_frame=False,identity_checked=True,source_provenance_retained=True,maximum_request_age_ms=100)
        metadata['build_hashes']={p.name:digest(p) for p in (host_exe,BIN/'return_launcher.exe',addon,DLL)}
        if args.capture_ship_image:
            metadata['prepared_ship_image']={'probe':'REMIX-PREPARED-IMAGE-001','shots':1,'delay_after_first_display_ms':15000,'reader_sha256':digest(live_bin/'ship_image_reader.exe'),'extra_gpu_bytes':2*1920*1080*4,'max_raw_bytes':256+1920*1080*4,'render_thread_readback':False,'camera_motion_cues':False}
    metadata['depth_snapshots']={'enabled':args.depth_snapshots,'probe':'REMIX-DEPTH-001','maximum_pairs':3,'tactical_seconds':20,'image_limit_bytes':64*1024*1024,'expected_source_samples':8}
    if args.calibration:metadata['probe']='REMIX-CALIBRATION-001'
    metadata['broad_capture']={'enabled':args.broad_capture,'proxy_sha256':broad_capture.FULL_SHA,'tactical_detail_seconds':10,'trace_hard_bytes':broad_capture.HARD,'trace_warning_bytes':1_000_000_000,'overall_ceiling_bytes':broad_capture.OVERALL,'prelude':'resource/view/device/command lifecycle plus target bindings/reset before tactical gate','coverage':'enumerated public events, not exhaustive GPU/geometry capture'}
    if args.broad_capture:metadata['capture_seconds']=10.1
    if args.depth_snapshots:metadata['capture_seconds']=20;metadata['limits_bytes']=96*1024*1024
    if args.broad_capture:
        metadata['limits_bytes']=broad_capture.HARD+32*1024*1024
        metadata['ancillary_limit_bytes']=32*1024*1024
    metadata['expanded_search']={'enabled':args.search_depth,'phases':depth_search_channel.PHASES,'resource_limit':32,'duration_seconds':90,'mapping_extension_bytes':2304}
    if args.observation_only:metadata['scene']='No Remix runtime started; read-only early depth-binding observation'
    if args.source_timing:metadata['scene']='Semantic source/Present timing,no game drawing'
    if args.live_owner_timing:metadata['scene']='Fresh semantic owner to separate ordinary-D3D9/Remix GPU receiver;current Present audit only,no game drawing'
    if args.d3d9_additive:metadata.update(probe='D3D9-ADDITIVE-001',scene='Fresh ordinary-D3D9/Remix textured ship at fixed world offset;exact-current-frame GPU return;original drawing ON',output_resources_bytes=82944000,image_limit_bytes=128*1024*1024,display_policy='Exact source identity/frame only;no stale hold;resize hides until fresh session')
    if args.persistent_scene:metadata['persistent_scene']=dict(protocol=2,registry_owners=32,pose_source='SHIP_SIMULATION_FIELDS',renderer='Existing ordinary D3D9 retained assets',initial_display='Configured player fixture',visibility_does_not_retire=True)
    if args.synchronized_buffer:
        metadata['synchronized_buffer']=dict(frames=1,max_age_ms=50,complete_native_HUD_delayed=True,prediction=False,stale_overlay_hold=False)
        metadata.update(output_resources_bytes=1920*1080*4*14,display_policy='One adjacent complete game frame with matching output/depth;50ms bound;no stale overlay on a newer scene')
    if args.lifecycle_capture:
        from lifecycle_capture import PHASES,RECOVERY_PHASES
        if args.camera_recovery:PHASES=RECOVERY_PHASES
        if args.persistent_scene:
            from offscreen_position import PHASES
        if args.synchronized_buffer:PHASES=()
        if args.offscreen_position:
            from offscreen_position import PHASES
            metadata['offscreen_position']=dict(probe='OFFSCREEN-POSITION-001',owners=2,hz_max=20,
                seconds_max=120,records_per_ship=2700,bytes_max=8*1024*1024,external_read_only=True,
                renderer_input=False,lifetime_proven=False)
        metadata['lifecycle_capture']=dict(probe='D3D9-LIFECYCLE-001',detail_hz_max=20,detail_records_per_slot=2700,detail_bytes=16*1024*1024,event_queue_records=256,event_bytes=1024*1024,phases=PHASES,native_death_signal_qualified=False)
        metadata['lifecycle_capture']['mode']='camera_return_alive' if args.camera_recovery else 'camera_gap_then_destruction'
        if args.synchronized_buffer:metadata['lifecycle_capture']['mode']='freeform_buffered_comparison_alive'
    if args.broad_capture:metadata['scene']='No Remix renderer; full-support read-only resource/binding/draw metadata'
    if args.depth_snapshots:metadata['scene']='No Remix renderer; three paired read-only depth/color snapshots; no original draws suppressed'
    (work/'manifest.json').write_text(json.dumps(metadata,indent=2))
    host=launcher=controller=channel=None;receiver=None;streams=[];pid=None;error=None;normal=False;gate_clean=False;history=[];phase_results={};last=0;host_shutdown_expected=False;proxy_restored=None;image_reader=None;image_result=None
    light_relay=None;tuning_exited=False;timing_relay=None;live_timing_result=None;offscreen=None
    rollback=work/'dxgi-original.rollback'
    config_backup=work/'ReShade.original.ini'
    def out(name):f=open(work/name,'wb');streams.append(f);return f
    last_output_check=0
    def enforce():
        nonlocal last_output_check
        if offscreen and offscreen.error:raise RuntimeError('Offscreen position reader: '+offscreen.error)
        if timing_relay and timing_relay.servicing:timing_relay.check_service()
        elif receiver:receiver.drain()
        if timing_relay and pid:timing_relay.poll(pid)
        if light_relay:light_relay.poll()
        if args.multi_ship and args.pipeline_mode=='performance':
            now=time.monotonic()
            if now>deadline:raise RuntimeError('Prepared workflow time limit')
            if now-last_output_check<1:return
            last_output_check=now
        size=sum(p.stat().st_size for p in work.rglob('*') if p.is_file())
        other=sum(p.stat().st_size for p in work.rglob('*') if p.is_file() and p.name!='broad.bin')
        if args.d3d9_additive:
            images=sum(p.stat().st_size for p in (work/'gpu').rglob('*') if p.is_file() and (p.suffix.lower()=='.dds' or re.fullmatch(r'texture-\d+\.bin',p.name)))
            if not args.multi_ship and images>128*1024*1024:raise RuntimeError('Additive image128MiB cap;original rendering retained')
            # Multi-ship asset worker checks authorized project/disk capacity
            # before/after preparation;never rescan the whole project each poll.
            size-=images;other-=images
        if args.textured_ship:
            textures=sum(p.stat().st_size for p in (work/'textures').glob('*') if p.is_file())
            if textures>128*1024*1024:raise RuntimeError('Original/derived image128MiB cap')
            if textures>64*1024*1024 and not phase_results.get('texture_warned'):print('Image output64MiB warning;128MiB cap remains.',flush=True);phase_results['texture_warned']=True
            size-=textures;other-=textures
        if full_support and (TEST/'ReShade.log').exists():other+=(TEST/'ReShade.log').stat().st_size
        image_bytes=sum(p.stat().st_size for p in work.glob('depth-*.bin'))
        if args.depth_snapshots:other-=image_bytes
        if args.source_timing:size+=2621568;other+=2621568 # reserve final metadata export,not written in render callbacks
        if args.live_owner_timing:size+=1154688;other+=1154688
        if args.broad_capture and (work/'broad.bin').exists() and (work/'broad.bin').stat().st_size>=1_000_000_000 and not phase_results.get('broad_warned'):
            print('Broad trace warning1GB; strict2GB writer cap remains active.',flush=True);phase_results['broad_warned']=True
        if args.depth_snapshots and image_bytes>64*1024*1024:raise RuntimeError('Depth image64MiB cap; original rendering retained')
        if args.depth_snapshots and image_bytes>32*1024*1024 and not phase_results.get('image_warned'):print('Depth images exceed32MiB warning; three-pair64MiB cap remains.',flush=True);phase_results['image_warned']=True
        if time.monotonic()>deadline or other>32*1024*1024 or size>(broad_capture.HARD+32*1024*1024 if args.broad_capture else (96*1024*1024 if args.depth_snapshots else 32*1024*1024)):raise RuntimeError('Prepared workflow time/output cap; original rendering retained')
        if other>16*1024*1024 and not phase_results.get('warned'):print('Evidence warning16MiB; still bounded.',flush=True);phase_results['warned']=True
    try:
        if full_support:
            # No accepted-install or translator changes. Restore only after game exit.
            shutil.copyfile(TEST/'ReShade.ini',config_backup)
            broad_capture.install_test_proxy(TEST/'dxgi.dll',rollback)
        host_env={**os.environ,**ENV,'DXVK_LOG_PATH':str(work)}
        if args.private_ship:
            from live_return import FreshReceiver
            receiver=FreshReceiver(work,textured=args.textured_ship);host_env['SFC_REMIX_CALIBRATION_SCENE']=receiver.name
        host_env.pop('SFC_REMIX_TEXTURED_SHIP',None)
        host_env.pop('SFC_REMIX_LIGHT_WIRING',None)
        host_env.pop('SFC_LIGHT_TUNING',None)
        if args.light_tuning:host_env['SFC_LIGHT_TUNING']='1'
        if args.light_wiring:
            from live_lights import Relay
            light_relay=Relay(work,receiver,tuning=args.light_tuning);host_env['SFC_REMIX_LIGHT_WIRING']='1'
        if args.textured_ship:host_env['SFC_REMIX_TEXTURED_SHIP']='1'
        host=sp.Popen([str(host_exe),'--observe-only' if args.observation_only else str(DLL)],cwd=work,env=host_env,stdout=out('host.log'),stderr=sp.STDOUT,creationflags=sp.CREATE_NO_WINDOW)
        session=None;until=time.monotonic()+60
        while time.monotonic()<until:
            enforce()
            if host.poll() is not None:raise RuntimeError('Renderer exited before session ready')
            session=next((s[8:] for s in (work/'host.log').read_text(errors='replace').splitlines() if s.startswith('SESSION ')),None)
            if session:break
            time.sleep(.1)
        if not session or not valid_name(session):raise RuntimeError('Renderer startup/session failed')
        channel=Channel(session)
        metadata['return_session']=session
        if full_support:metadata['full_support_qualification']=q
        (work/'manifest.json').write_text(json.dumps(metadata,indent=2))
        env={**os.environ,'SFC_REMIX_RETURN_SESSION':session,'SFC_REMIX_EXPECTED_IMAGE':str(TEST/'StarFleetOP.exe'),'SFC_REMIX_PRELOAD_REQUIRED':'1'}
        env['SFC_REMIX_INSPECT_VISIBILITY']='3' if args.search_depth else ('2' if args.inspect_early_depth else ('1' if args.inspect_visibility else '0'))
        env.pop('SFC_REMIX_BROAD_OUTPUT',None)
        env.pop('SFC_REMIX_DEPTH_OUTPUT',None)
        env.pop('SFC_REMIX_CALIBRATION_SCENE',None)
        env.pop('SFC_REMIX_CAPTURE_SHIP_IMAGE',None);env.pop('SFC_REMIX_CAPTURE_SHIP_IMAGE_DELAY_MS',None)
        env.pop('SFC_NATIVE_LIGHT_DISCOVERY',None)
        env.pop('SFC_LIGHT_TUNING',None)
        env.pop('SFC_D3D9_SOURCE_TIMING',None)
        env.pop('SFC_D3D9_LIVE_TIMING',None)
        if args.source_timing:env['SFC_D3D9_SOURCE_TIMING']='1'
        if args.live_owner_timing:env['SFC_D3D9_LIVE_TIMING']='1'
        env.pop('SFC_D3D9_GAME_OUTPUT',None)
        env.pop('SFC_LIFECYCLE_CAPTURE',None)
        if args.lifecycle_capture:env['SFC_LIFECYCLE_CAPTURE']='1'
        if args.d3d9_additive:env.update(SFC_D3D9_GAME_OUTPUT='1',SFC_LIGHT_TUNING='1')
        env.pop('SFC_D3D9_SHARED_LIGHTS',None)
        env.pop('SFC_PERSISTENT_SCENE',None)
        env.pop('SFC_D3D9_SYNC_BUFFER',None)
        env.pop('SFC_D3D9_MULTISCENE',None)
        if args.multi_ship:env['SFC_D3D9_MULTISCENE']='1'
        env['SFC_PIPELINE_MODE']=args.pipeline_mode if args.multi_ship else 'test'
        if args.synchronized_buffer:env['SFC_D3D9_SYNC_BUFFER']='1'
        if args.persistent_scene:env['SFC_PERSISTENT_SCENE']='1'
        if args.d3d9_additive:env['SFC_D3D9_SHARED_LIGHTS']='1'
        if args.light_tuning:env['SFC_LIGHT_TUNING']='1'
        if args.capture_native_lights:env['SFC_NATIVE_LIGHT_DISCOVERY']='1'
        if args.capture_ship_image:env.update(SFC_REMIX_CAPTURE_SHIP_IMAGE='1',SFC_REMIX_CAPTURE_SHIP_IMAGE_DELAY_MS='15000')
        if semantic_enabled:
            from present_calibration import Receiver
            if receiver is None:receiver=Receiver()
            if args.live_owner_timing:
                if args.experimental_parallel_assets:from progressive_scene_relay import Relay
                elif args.multi_ship:from multi_scene_relay import Relay
                else:from live_owner_timing import Relay
                mode_args={'pipeline_mode':args.pipeline_mode} if args.multi_ship else {}
                if args.experimental_parallel_assets:mode_args['experimental_live_checkout']=True
                timing_relay=Relay(work,receiver,TEST,additive=args.d3d9_additive,persistent=args.persistent_scene,buffered=args.synchronized_buffer,**mode_args)
            env['SFC_REMIX_CALIBRATION_SCENE']=receiver.name
            env.pop('SFC_REMIX_VISIBLE_SHIP',None)
            env.pop('SFC_REMIX_TEXTURED_SHIP',None)
            if args.private_ship:env['SFC_REMIX_PRIVATE_SHIP']='1'
            if args.visible_ship:env['SFC_REMIX_VISIBLE_SHIP']='1'
            if args.textured_ship:env['SFC_REMIX_TEXTURED_SHIP']='1'
            component_path=ROOT/('artifacts/remix-runtime/native-light-tests/m1_light_component.dll' if args.capture_native_lights else 'artifacts/m1/bin/m1_component.dll')
            metadata['semantic_calibration']={'probe':'REMIX-CALIBRATION-001','scene_session':receiver.name,'maximum_asset_revisions':64 if args.multi_ship else 8,'geometry_hook':False,'same_process_render_thread_required':True,'component_sha256':digest(component_path)}
            if args.multi_ship:
                from multi_scene_resources import policy
                metadata.update(probe='D3D9-MULTISHIP-001',scene='Fresh retained multi-model diagnostic;placement recorded in live-owner analysis',original_suppressed=False,tracked_set_capacity=32,asset_revisions=64,
                                image_limit_bytes=broad_capture.OVERALL,image_policy=policy())
            (work/'manifest.json').write_text(json.dumps(metadata,indent=2))
        if args.depth_snapshots:env['SFC_REMIX_DEPTH_OUTPUT']=str(work)
        env.pop('SFC_REMIX_SCENE_DEPTH',None)
        if args.scene_depth:env['SFC_REMIX_SCENE_DEPTH']='1'
        if args.broad_capture:env['SFC_REMIX_BROAD_OUTPUT']=str(work/'broad.bin')
        if compat:
            # Preserve only the already-configured visual/OS compatibility layer
            # in this child, without changing any registry/security policy.
            flags=[s for s in compat.split() if s!='~']
            if any(s.upper()=='RUNASINVOKER' for s in flags):raise RuntimeError('Existing invoker override requires explicit review; not propagated')
            env['__COMPAT_LAYER']=' '.join(flags)
        launcher=sp.Popen([str(BIN/'return_launcher.exe'),'--game',str(TEST/'StarFleetOP.exe'),str(work/'SFCRemixReturn.dll'),CLIENT,digest(work/'SFCRemixReturn.dll')],cwd=TEST,env=env,stdout=out('launcher.log'),stderr=sp.STDOUT,creationflags=sp.CREATE_NO_WINDOW)
        until=time.monotonic()+20
        while time.monotonic()<until:
            enforce();text=(work/'launcher.log').read_text(errors='replace');match=re.search(r'VERIFIED_CHILD pid=(\d+) suspended_path_match=1 disk_sha_match=1',text)
            if match:pid=int(match[1]);break
            if launcher.poll() is not None:raise RuntimeError('Verified copied client did not launch')
            time.sleep(.1)
        if not pid or Path(image_path(pid))!=TEST/'StarFleetOP.exe':raise RuntimeError('Actual process path does not match isolated test copy; no gate activated')
        if args.multi_ship:timing_relay.start_on_launch(pid)
        if args.private_ship:receiver.context(session,pid)
        # Do not enumerate/inject the gate while the translator and proxy are
        # still populating the target's loader/module list. No fixed blind sleep.
        ready_at=time.monotonic()
        wait_component_ready(channel.snapshot,pid,launcher.poll,enforce)
        metadata['graphics_ready_wait_seconds']=time.monotonic()-ready_at
        metadata['gate_build_hashes']={p.name:digest(p) for p in (ROOT/'artifacts/m1/bin/m1_controller.exe',ROOT/'artifacts/m1/bin/m1_gate.dll')}
        (work/'manifest.json').write_text(json.dumps(metadata,indent=2))
        print('Enter the usual two-ship skirmish. Ships should look normal.',flush=True)
        if args.private_ship and not args.light_tuning:print('At the first beep,hold your ship and camera still. A later single beep means a small camera change;three beeps mean gently move/turn your ship. Two beeps mean exit normally.',flush=True)
        if inspect_requested:print('Read-only visibility check: keep both ships visible briefly. No ship will be replaced.',flush=True)
        if args.broad_capture:print('Broad recording: keep both ships in view briefly and play normally. About10seconds after tactical entry, two beeps request normal exit. No visual change expected.',flush=True)
        if args.depth_snapshots:print('Keep both ships visible. At first beep hold camera still; at the next single beep make one small camera rotation, then hold still. Two beeps mean exit normally. No visual change expected.',flush=True)
        if args.textured_ship and not args.light_tuning:print('Look for a TEXTURED ship copy beside an original,not magenta. It stays ON throughout this observation;stop only at the two-beep exit request. Small bounded delay,not frame-exact replacement.',flush=True)
        if args.capture_native_lights and not args.light_tuning and not args.scene_depth and not args.d3d9_additive:print('Light discovery:play normally,move the camera and ship briefly,and fire when convenient. We record the game lights without changing them. Exit only at the two-beep request.',flush=True)
        if args.scene_depth:print('Depth test: originals remain ON. The extra textured ship is visible only when pose/camera match;it may disappear while moving. Hold still between small camera changes. Grid behavior is being observed,not changed by a guessed rule.',flush=True)
        if args.light_wiring and not args.light_tuning:print('LIGHT WIRING:extra ship uses two observed native directional lights with ratio controls. Native game unchanged. Normal90s test,not extended tuning;exit at two-beep cue.',flush=True)
        if args.capture_ship_image:print('One prepared-image snapshot will be saved automatically. Focus the extra ship and hold the camera briefly once it appears;no manual screenshot or timestamp needed.',flush=True)
        elif args.d3d9_additive:print('Look for a fully textured extra ship beside one original. Original ships stay visible. Your existing light/material/image settings are frozen for this short test;no magenta or on/off cycle.',flush=True)
        elif not args.textured_ship:print('Look for a MAGENTA ship copy BESIDE the selected original ship,usually to its left at the starting view;it may flash. This is NOT a corner window. Original ships stay normal.' if args.visible_ship else ('No visible change expected;fresh ship output is tested privately,originals stay normal.' if args.private_ship else ('No triangle or ship changes expected; this is a read-only check.' if args.observation_only else 'A small green animated triangle will appear in a black square at upper right. It turns off/on/off automatically.')),flush=True)
        print('Tune the textured extra ship;exit SFC normally whenever finished.' if args.light_tuning else 'Play normally. Please exit only after the two-beep exit request.',flush=True)
        controller_exe=ROOT/'artifacts/m1/bin/m1_controller.exe';gate=ROOT/'artifacts/m1/bin/m1_gate.dll'
        gate_dir=work/'gate';gate_dir.mkdir();config=gate_dir/'component.ini'
        config.write_text('[m1]\nOutputDirectory='+str(gate_dir)+'\nControllerPath='+str(controller_exe)+'\nMaxSeconds=90\nStopOnBurst=1\nMaxFrames=1\nMaxEvents=1\nMaxOwners=1\nWarningBytes=16777216\nHardBytes=33554432\n',encoding='ascii')
        if semantic_enabled:
            gate=ROOT/'artifacts/m1/bin/m1_component.dll'
            if args.capture_native_lights:
                gate=ROOT/'artifacts/remix-runtime/native-light-tests/m1_light_component.dll'
                metadata['native_lights']={'probe':'NATIVE-LIGHTS-001','qualification':light_qualification,'hypothesis':'three lights and/or global illumination;UNCONFIRMED'}
                (work/'manifest.json').write_text(json.dumps(metadata,indent=2))
            config.write_text('[m1]\nOutputDirectory='+str(gate_dir)+'\nControllerPath='+str(controller_exe)+
                '\nMaxSeconds='+('1800' if args.light_tuning else '120' if args.d3d9_additive else '90' if args.private_ship or args.source_timing else '24')+'\nStopOnBurst=0\nMaxFrames=120\nMaxEvents=10000\nMaxOwners=32\nWarningBytes=16777216\nHardBytes=33554432'+
                '\nEnableGeometryHook=0\nEnableWrapperObservation=1\nEnableMeshExport=1\nEnableTextureReferences=1\nEnablePrivateCopy=0\nLiveChannel='+receiver.name+'\n',encoding='ascii')
        controller_args=[str(controller_exe),'--pid',str(pid),'--dll',str(gate),'--config',str(config),'--max-seconds','24' if args.calibration else '90','--stop-on-burst','0' if semantic_enabled else '1','--already-loaded','0','--unload-after-stop','1']
        if args.light_tuning:controller_args[controller_args.index('--max-seconds')+1]='1800'
        if args.d3d9_additive:controller_args[controller_args.index('--max-seconds')+1]='120'
        gate_timeout=tactical_gate_timeout(args.multi_ship)
        if semantic_enabled:
            controller_args+=['--gate-timeout-seconds',str(gate_timeout)]
            metadata['gate_timeout_seconds']=gate_timeout
            (work/'manifest.json').write_text(json.dumps(metadata,indent=2))
            print(f'Enter the skirmish within {gate_timeout} seconds. The90second recording starts automatically in the tactical scene,not during ship selection.',flush=True)
        controller=sp.Popen(controller_args,cwd=ROOT,stdout=out('gate-controller.log'),stderr=sp.STDOUT,creationflags=sp.CREATE_NO_WINDOW)
        if semantic_enabled:
            wait_live_gate(pid,controller,enforce,timeout=gate_timeout);controller_gate_observed=time.monotonic()
            if args.offscreen_position:
                from offscreen_position import Capture
                offscreen=Capture(work,pid,TEST/'StarFleetOP.exe')
        else:
            while controller.poll() is None:enforce();time.sleep(.1)
            gate_text=(work/'gate-controller.log').read_text(errors='replace')
            summary=json.loads((gate_dir/'M1-A-summary.json').read_text(encoding='utf-8-sig')) if (gate_dir/'M1-A-summary.json').exists() else {}
            gate_clean=controller.returncode==0 and summary.get('gate_activated') is True and all(s in gate_text for s in ('component_state=removed','hook_bytes_restored=true','component_unloaded=true'))
            if not gate_clean:raise RuntimeError('Tactical gate did not complete/restored/unload cleanly; image left disabled')
        if args.search_depth:
            search=depth_search_channel.snapshot(channel.address)
            if search['status']!=2 or search['installedMask']!=15 or search['error']:raise RuntimeError('Expanded engine search installation not qualified')
        state=channel.snapshot()
        if args.broad_capture:
            broad=broad_capture.header_at(channel.address)
            if broad['status']!=2 or broad['error']:raise RuntimeError('Broad writer not active at tactical gate; prelude may have saturated; preserve partial evidence')
        if state['gamePid']!=pid or not state['startupRestored'] or not state['startupVerified'] or not state['ready']:raise RuntimeError('Image component startup/device not qualified; original game remains normal')
        channel.set('armed',1);channel.set('enabled',int(args.d3d9_additive or not args.observation_only));winsound.Beep(880,200);active=time.monotonic();phase=-1
        if args.d3d9_additive:
            print('Preparing the extra textured ship;original game stays normal. Keep both ships visible and alive. Timed instructions start when the first matching ship image is ready.',flush=True)
            preparing=active
            while time.monotonic()-preparing<30:
                enforce()
                if channel.snapshot()['drawCount']>0:break
                if launcher.poll() is not None:raise RuntimeError('Game exited during additive preparation')
                time.sleep(.05)
            else:raise RuntimeError('No qualified offset image within30s preparation;preserve evidence')
            metadata.update(additive_preparation_seconds=time.monotonic()-preparing,formal_capture_seconds=90,semantic_watchdog_seconds=120)
            (work/'manifest.json').write_text(json.dumps(metadata,indent=2));active=time.monotonic()
        if args.capture_ship_image:image_reader=sp.Popen([str(live_bin/'ship_image_reader.exe'),session,str(work)],cwd=work,stdout=out('ship-image-reader.log'),stderr=sp.STDOUT,creationflags=sp.CREATE_NO_WINDOW)
        camera_cued=False;motion_cued=False
        source_cues=set()
        if args.multi_ship:print('MULTI-SHIP OFFSET TEST:use different ship models. Returned copies sit to CAMERA LEFT of the originals at the previous test distance. Original ships stay visible. Keep both alive and briefly visible together,then move/turn and switch cameras normally. Watch the copies for flicker,missing/wrong models or placement problems. TWO LOW beeps=exit normally after restoration.',flush=True)
        elif args.synchronized_buffer:print('BUFFERED SHIP TEST:one complete game frame and matching extra ship are displayed together. Play normally and swap cameras freely;keep both ships alive. Check return flicker and whether controls/HUD feel normal. No movement cues;TWO LOW beeps=exit normally after restoration.',flush=True)
        elif args.persistent_scene:print('PERSISTENT SHIP TEST:keep both ships alive. At the timed single cue accelerate your ship and leave it moving. TWO HIGH=enemy camera;THREE HIGH=return to your ship. The extra ship should follow current motion without reloading. Follow the gentle-turn cue for the second pass. TWO LOW=exit only after restoration.',flush=True)
        elif args.offscreen_position:print('OFFSCREEN POSITION TEST:keep both ships alive. At the first single cue accelerate your ship and LEAVE IT MOVING. TWO HIGH=look at the enemy,leaving your own ship out of view. THREE HIGH=return to your ship. Follow the turn/setup cue for the second pass. TWO LOW=exit only after restoration. No new visual effect is expected.',flush=True)
        elif args.camera_recovery:print('CAMERA RETURN TEST:keep both ships alive;do NOT destroy your ship. ONE beep=hold;TWO HIGH=enemy camera;THREE HIGH=return to own ship. This repeats twice. The extra ship should return beside your own. TWO LOW=exit normally;restoration may take a short wait after recording.',flush=True)
        elif args.lifecycle_capture:print('LIFECYCLE TEST:First15seconds settle the view. ONE beep=hold alive;TWO HIGH=enemy camera;THREE HIGH=return to own ship;FOUR HIGH=destroy OWN ship. Stay in mission after destruction. TWO LOW=exit normally.',flush=True)
        elif args.source_timing:print(('OFFSET SHIP TEST:extra textured ship,original stays visible. Keep both ships alive. ' if args.d3d9_additive else 'TIMING CHECK:no visual change. ')+ 'Do not pause;keep both ships visible. First15seconds:find a comfortable view. LOW single beep=hold. TWO HIGH beeps=small camera moves. THREE HIGH=accelerate/turn your ship. TWO LOW=exit normally.',flush=True)
        if args.light_tuning:print('TUNING:edit tools/remix_runtime/config/lights.toml, materials.toml or image.toml and SAVE. Image adjustments need enabled=true. Changes apply live. Exit SFC normally when finished;30minute safety ceiling. No timed motion instructions.',flush=True)
        tuning_exited=False
        while time.monotonic()-active<(1800 if args.light_tuning else 10.1 if args.broad_capture else (20 if args.depth_snapshots else 90)):
            enforce();elapsed=time.monotonic()-active;state=channel.snapshot()
            if args.light_tuning and launcher.poll() is not None:
                tuning_exited=True;break
            if args.source_timing and not args.multi_ship:
                cues=PHASES if args.lifecycle_capture else ((15,1,'Hold your ship and camera still for10seconds.'),(25,1,'Prepare a freely movable camera;keep both ships visible.'),(35,2,'Make small camera movements for15seconds.'),(50,1,'Hold the camera still;prepare to move your ship.'),(60,3,'Accelerate and gently turn your ship for20seconds;keep both ships visible.'),(80,1,'Hold a steady view until the exit request.'))
                for second,count,message in cues:
                    if elapsed>=second and second not in source_cues:
                        source_cues.add(second)
                        for _ in range(count):winsound.Beep(1100 if count>1 else 880,150)
                        print(message,flush=True)
                        if args.lifecycle_capture:phase_results.setdefault('lifecycle_cues',[]).append(dict(requested_second=second,issued_second=elapsed,message=message))
            if args.depth_snapshots and elapsed>=5 and not camera_cued:
                winsound.Beep(1000,200);print('Small camera rotation now, then hold still; keep both ships visible.',flush=True);camera_cued=True
            if args.private_ship and not args.light_tuning and not args.capture_ship_image and elapsed>=10 and not camera_cued:
                winsound.Beep(1000,200);print('Make one small camera change now,then hold it.',flush=True);camera_cued=True
            if args.private_ship and not args.light_tuning and not args.capture_ship_image and elapsed>=20 and not motion_cued:
                for _ in range(3):winsound.Beep(1100,150)
                print('Gently accelerate and turn your ship;keep playing until the two-beep exit cue.',flush=True);motion_cued=True
            next_phase=observation_phase(elapsed,continuous=args.textured_ship or args.source_timing)
            if phase!=next_phase:
                phase=next_phase;phase_results[str(phase)]={'seconds':elapsed,'start':state};channel.set('enabled',int(args.d3d9_additive or (not args.observation_only and phase in (0,2))))
                print('Offset ship remains enabled;keep playing until the exit request.' if args.d3d9_additive else ('Private receiver ON','Private receiver OFF','Private receiver ON again','Private renderer disconnect;original game unchanged')[phase] if args.private_ship else ('Read-only check; keep playing normally.' if args.observation_only else ('Image ON','Image OFF; keep playing','Image ON again','Renderer disconnect; image OFF; keep playing')[phase]),flush=True)
                if phase==3 and not args.search_depth:channel.set('stop',1);host_shutdown_expected=True
            if state['error']:raise RuntimeError('Image component reported an error; original rendering retained')
            if launcher.poll() is not None:raise RuntimeError('Game exited before the requested tactical observation completed')
            if host.poll() is not None and not host_shutdown_expected:raise RuntimeError('Renderer exited unexpectedly; original rendering retained')
            if elapsed-last>(5 if args.light_tuning or (args.multi_ship and args.pipeline_mode=='performance') else .25):
                item={'seconds':elapsed,'phase':phase,**state}
                if args.private_ship:
                    from live_return import telemetry
                    item['private_return']=telemetry(channel.address)
                    if args.scene_depth:
                        from live_return import depth_telemetry
                        item['scene_depth']=depth_telemetry(channel.address)
                    if args.textured_ship:
                        sampled=C.c_longlong();C.windll.kernel32.QueryPerformanceCounter(C.byref(sampled));item['sample_qpc']=sampled.value
                        item['last_display_request_age_ms']=(sampled.value-state['renderedAt'])*1000/state['qpcFrequency'] if state['renderedAt'] else None
                history.append(item);last=elapsed
            time.sleep(.05)
        if args.search_depth:
            channel.set('stop',1);host_shutdown_expected=True
            until=min(deadline,time.monotonic()+8)
            while time.monotonic()<until:
                search=depth_search_channel.snapshot(channel.address)
                if search['status'] in (4,5):break
                time.sleep(.05)
            if search['status']!=4 or search['restoredMask']!=15 or search['error']:raise RuntimeError('Expanded-search hooks not confirmed restored; exit normally, do not unload DLL')
        if args.broad_capture:
            until=min(deadline,time.monotonic()+8)
            while time.monotonic()<until:
                broad=broad_capture.header_at(channel.address)
                if broad['status'] in (3,4):break
                time.sleep(.02)
            if broad['status']!=3 or broad['error']:raise RuntimeError('Broad writer did not close successfully; exit normally')
            channel.set('stop',1);host_shutdown_expected=True
        if args.depth_snapshots or args.textured_ship or args.source_timing:
            channel.set('enabled',0);channel.set('stop',1);host_shutdown_expected=True
        if semantic_enabled:
            # Stop the renderer before waiting for semantic removal. Otherwise
            # enforce() can mistake its orderly exit for an unexpected death.
            if offscreen:offscreen.close()
            if timing_relay:timing_relay.stop()
            from controller_shutdown import wait_removed
            print('Recording finished; restoring the test component. Keep SFC open until the exit cue.',flush=True)
            wait_removed(controller,enforce,controller_gate_observed,int(controller_args[controller_args.index('--max-seconds')+1]),deadline)
            gate_text=(work/'gate-controller.log').read_text(errors='replace')
            summary=json.loads((gate_dir/'M1-A-summary.json').read_text(encoding='utf-8-sig')) if (gate_dir/'M1-A-summary.json').exists() else {}
            gate_clean=controller.poll()==0 and summary.get('gate_activated') is True and all(s in gate_text for s in ('component_state=removed','hook_bytes_restored=true','component_unloaded=true'))
            # On normal process exit Windows reclaims target memory. This is NOT
            # evidence of a controlled live-hook restoration/unload.
            if not gate_clean and not (args.light_tuning and tuning_exited and controller.poll()==8):raise RuntimeError('Semantic component removal/unload not confirmed; exit normally')
        print('Depth capture window finished — please exit SFC normally now; validation follows after exit.' if args.depth_snapshots else 'TEST COMPLETE — please exit SFC normally now.',flush=True);winsound.Beep(660,200);winsound.Beep(660,200)
        until=min(deadline,time.monotonic()+30)
        while launcher.poll() is None and time.monotonic()<until:enforce();time.sleep(.1)
        normal=launcher.poll()==0 and 'CHILD_EXIT code=0' in (work/'launcher.log').read_text(errors='replace')
        if not normal:raise RuntimeError('Normal game exit not yet confirmed; do not kill SFC')
        if host.poll() is None:host.wait(timeout=8)
        if host.returncode:raise RuntimeError('Renderer shutdown did not complete normally')
        if not args.observation_only and not args.private_ship and (not history or max(v['drawCount'] for v in history)<30 or max(v['copyCount'] for v in history)<10):raise RuntimeError('Insufficient actual image/presentation evidence')
        if inspect_requested and (channel.state.visibilitySamples!=8 or channel.state.visibilityScope!=(2 if args.inspect_early_depth else 1)):raise RuntimeError('Read-only visibility observations incomplete or wrong scope')
        if args.capture_ship_image:
            image_reader.wait(timeout=8)
            if image_reader.returncode:raise RuntimeError('Requested prepared ship image missing/reader failed;runtime evidence retained')
            from ship_image_snapshot import convert
            image_result=convert(work)
    except Exception as exc:
        error=str(exc);print('Test stopped safely: '+error,flush=True)
        if pid and not normal:print('Please exit the copied SFC game normally. No original drawing is suppressed.',flush=True)
    finally:
        if offscreen:
            try:offscreen.close()
            except Exception as exc:error=(error+'; ' if error else '')+'Offscreen reader shutdown: '+str(exc)
        if channel:channel.set('enabled',0);channel.set('stop',1)
        if image_reader and image_reader.poll() is None:
            try:image_reader.wait(timeout=5)
            except sp.TimeoutExpired:image_reader.terminate();image_reader.wait(timeout=5)
        if error and launcher and pid and launcher.poll() is None:
            print('Waiting briefly for normal game exit before restoring the test setup.',flush=True)
            until=min(deadline,time.monotonic()+30)
            while launcher.poll() is None and time.monotonic()<until:time.sleep(.1)
            normal=launcher.poll()==0 and 'CHILD_EXIT code=0' in (work/'launcher.log').read_text(errors='replace')
        # Never terminate SFC or a controller still responsible for live gate hooks.
        if host and host.poll() is None:
            try:host.wait(timeout=8)
            except sp.TimeoutExpired:host.terminate();host.wait(timeout=5)
        if launcher and launcher.poll() is None:launcher.terminate();launcher.wait(timeout=5) # parent only, not game; no game job kill flag
        if full_support and rollback.exists():
            if game_running():
                proxy_restored=False;error=(error+'; ' if error else '')+'Game still running: proxy rollback deferred; exit normally then restore verified backup'
            else:
                try:
                    if (TEST/'ReShade.log').exists() and (TEST/'ReShade.log').stat().st_size<=16*1024*1024:shutil.copyfile(TEST/'ReShade.log',work/'ReShade.full-support.log')
                    broad_capture.restore_test_proxy(TEST/'dxgi.dll',rollback);proxy_restored=True
                    if digest(config_backup)!=metadata['copied_critical_before']['ReShade.ini']:raise ValueError('Copied configuration rollback hash mismatch')
                    shutil.copyfile(TEST/'ReShade.ini',work/'ReShade.after-test.ini')
                    shutil.copyfile(config_backup,TEST/'ReShade.ini')
                except Exception as exc:proxy_restored=False;error=(error+'; ' if error else '')+str(exc)
        final=channel.snapshot() if channel else None
        # Early sponsor exit is a partial-duration test,not automatically a crash.
        # Process-exit reclamation still does NOT prove controlled hook unload.
        if launcher and launcher.poll()==0 and 'CHILD_EXIT code=0' in (work/'launcher.log').read_text(errors='replace'):normal=True
        visibility=visibility_result(channel.state) if channel else 'NO_CHANNEL'
        search=None
        if channel and args.search_depth:
            try:search=depth_search_channel.snapshot(channel.address)
            except ValueError as exc:error=(error+'; ' if error else '')+str(exc)
        private_stats=None
        if args.private_ship and channel:
            from live_return import telemetry
            private_stats=telemetry(channel.address)
        source_timing_result=None
        if timing_relay:
            try:live_timing_result=timing_relay.finish(pid)
            except Exception as exc:error=(error+'; ' if error else '')+'Live owner timing: '+str(exc)
        if args.source_timing and receiver:
            try:
                from source_timing import save
                source_timing_result=save(receiver.channel,work,pid)
            except Exception as exc:error=(error+'; ' if error else '')+'Source timing analysis: '+str(exc)
        if channel:channel.close()
        if receiver:
            if timing_relay and timing_relay.servicing and timing_relay.service.thread.is_alive():
                error=(error+'; ' if error else '')+'Recovery service still owns mapping;close deferred'
            else:receiver.close()
        for f in streams:f.close()
        after=critical_hashes(SOURCE);paths_after=launcher_paths();copy_after=critical_hashes(TEST)
        if after!=original or paths_after!=paths:error=(error+'; ' if error else '')+'Accepted installation or launcher settings changed'
        if copy_after['StarFleetOP.exe']!=CLIENT:error=(error+'; ' if error else '')+'Copied client hash changed'
        if full_support and copy_after!=metadata['copied_critical_before']:error=(error+'; ' if error else '')+'Copied critical baseline not fully restored'
        result={'probe':'REMIX-RETURN-001','error':error,'seconds':time.monotonic()-start,'target_pid':pid,'normal_game_exit':normal,'gate_clean_unloaded':gate_clean,'gate_controller_pid':controller.pid if controller else None,'gate_controller_exit':controller.poll() if controller else None,'gate_controller_left_running':controller is not None and controller.poll() is None,'renderer_exit':host.returncode if host else None,'original_critical_unchanged':after==original,'launcher_settings_unchanged':paths_after==paths,'accepted_critical_after':after,'copied_critical_after':copy_after,'history':history,'phases':phase_results,'final':final,'sponsor_visible_behavior':'PENDING sponsor report','result':'RUNTIME_REVIEW_REQUIRED' if not error else 'PARTIAL'}
        if args.private_ship:
            result.update(probe='REMIX-LIVE-RETURN-001',private_return=private_stats,fresh_asset=receiver.selected if receiver else None,
                  backbuffer_ship_drawing=bool(args.visible_ship),original_ship_suppressed=False)
            if args.textured_ship:result.update(display_policy='v4 delayed-additive,request age<=100ms at enqueue;captured pose/camera NOT current-frame replacement',output_size=[1920,1080],original_textures=True)
            if not error:result['result']='FRESH_PRIVATE_LEASE_ACCEPTED_REVIEW_REQUIRED' if private_stats and private_stats['drawn'] else 'NO_CURRENT_FRAME_RETURN_ADDITIONAL_BOUNDED_EVIDENCE_REQUIRED'
            if not error and args.visible_ship:result['result']='VISIBLE_SHIP_SUBMITTED_SPONSOR_REVIEW_REQUIRED' if final and final['drawCount'] else 'NO_VISIBLE_SHIP_SUBMISSIONS_PARTIAL'
        result['visibility_observation']=visibility
        if args.source_timing:
            result.update(probe='D3D9-SOURCE-TIMING-001',source_timing=source_timing_result,remix_loaded=False,backbuffer_ship_drawing=False,original_ship_suppressed=False)
            result['result']='SOURCE_TIMING_EVIDENCE_READY_ADJUDICATION_REQUIRED' if not error and source_timing_result and source_timing_result['result']=='SOURCE_TIMING_OBSERVATION_COMPLETE_ADJUDICATION_REQUIRED' else 'PARTIAL'
        if args.live_owner_timing:
            result.update(probe='D3D9-LIVE-TIMING-001',live_owner_timing=live_timing_result,remix_loaded=bool(timing_relay and timing_relay.process),remix_in_sfc_process=False)
            result['result']='LIVE_TIMING_EVIDENCE_READY_ADJUDICATION_REQUIRED' if not error and live_timing_result and live_timing_result['result']=='LIVE_TIMING_OBSERVED_ADJUDICATION_REQUIRED' else 'PARTIAL'
        if args.d3d9_additive:
            result.update(probe='D3D9-ADDITIVE-001',backbuffer_ship_drawing=True,original_ship_suppressed=False,legacy_host_observation_only=True,observation_only=False)
            result['result']='OFFSET_SHIP_SUBMITTED_SPONSOR_REVIEW_REQUIRED' if not error and live_timing_result and live_timing_result['result']=='OFFSET_SHIP_SUBMITTED_REVIEW_REQUIRED' else 'PARTIAL'
        if args.multi_ship:
            result.update(probe='D3D9-MULTISHIP-001',aligned_overlay=bool(live_timing_result and live_timing_result.get('selected',{}).get('camera_offset')==[0,0,0]),original_ship_suppressed=False)
            result['result']='MULTISHIP_OVERLAY_SPONSOR_REVIEW_REQUIRED' if not error and live_timing_result and live_timing_result['result']=='MULTISHIP_OVERLAY_REVIEW_REQUIRED' else 'PARTIAL'
        if args.lifecycle_capture:
            from lifecycle_capture import analyze as analyze_lifecycle
            try:result['lifecycle_capture']=analyze_lifecycle(work/'gate')
            except (OSError,ValueError) as exc:result['lifecycle_capture']=dict(result='PARTIAL',error=str(exc),native_death_signal_qualified=False)
            if result['lifecycle_capture']['result']=='PARTIAL':result['result']='PARTIAL'
        if args.persistent_scene:
            try:result['persistent_scene']=json.loads((work/'gate/PERSISTENT-SCENE-001.json').read_text())
            except (OSError,ValueError) as exc:result['persistent_scene']=dict(error=str(exc));result['result']='PARTIAL'
        if args.offscreen_position:
            from offscreen_position import analyze as analyze_offscreen
            try:result['offscreen_position']=analyze_offscreen(work)
            except (OSError,ValueError,KeyError) as exc:result['offscreen_position']=dict(result='PARTIAL',error=str(exc))
            if result['offscreen_position']['result']=='PARTIAL':result['result']='PARTIAL'
        if args.light_tuning:result['cleanup_mode']='process-exit reclamation' if tuning_exited else 'controlled timed removal'
        if args.capture_ship_image:result['prepared_ship_image']=image_result
        if args.capture_native_lights and not args.light_tuning and not args.d3d9_additive:
            try:
                from light_discovery import analyze as analyze_lights
                lights=analyze_lights(work/'gate/native-lights.bin')
                expected=[int(receiver.name[-32:][i:i+8],16) for i in range(0,32,8)]
                if lights['session_words']!=expected:raise ValueError('Light discovery session mismatch')
                worker=json.loads((work/'gate/native-lights-summary.json').read_text())
                if worker['io_failed'] or worker['queued'] or worker['written']!=lights['records']:raise ValueError('Light discovery worker incomplete')
                result['native_lights']=lights
            except (ValueError,OSError) as exc:
                error=(error+'; ' if error else '')+str(exc);result['error']=error;result['result']='PARTIAL'
        if light_relay:result['light_controls']=light_relay.summary()
        result['observation_only']=args.observation_only and not args.d3d9_additive
        if args.scene_depth:
            samples=[v['scene_depth'] for v in history if 'scene_depth' in v]
            last_depth=samples[-1] if samples else {}
            passed=bool(last_depth.get('qualified') and last_depth.get('displayed') and not last_depth.get('failed') and not last_depth.get('wrong_thread'))
            result['scene_depth_test']=dict(result='DEPTH_FILTER_RUNTIME_REVIEW_REQUIRED' if passed else 'PARTIAL_NO_QUALIFIED_DEPTH_DISPLAY',telemetry=last_depth,original_suppressed=False,grid_policy='NOT_ASSUMED')
            if not passed:
                error=(error+'; ' if error else '')+'Scene depth needs review; originals were retained'
                result['error']=error;result['result']='PARTIAL'
        result['expanded_search']=search
        result['broad_proxy_restored']=proxy_restored
        if args.depth_snapshots:
            try:
                from depth_snapshot_analysis import analyze_run
                result['depth_snapshots']=analyze_run(work,images=True)
                if not result['depth_snapshots']['complete']:
                    status=result['depth_snapshots']['status']
                    raise ValueError(f"Depth capture PARTIAL: {status.get('files',0)}/3 images; stage={status.get('failure_stage_name','unrecorded')}; HRESULT={status.get('failure_hresult_hex','unrecorded')}; feature_level={status.get('feature_level','unrecorded')}. Evidence retained; no ship suppressed.")
            except (ValueError,OSError) as exc:error=(error+'; ' if error else '')+str(exc);result['error']=error;result['result']='PARTIAL'
        if args.calibration:
            try:
                from present_calibration import analyze
                result['semantic_calibration']=analyze(work,metadata['semantic_calibration']['scene_session'],pid)
            except (ValueError,OSError) as exc:error=(error+'; ' if error else '')+str(exc);result['error']=error;result['result']='PARTIAL'
        if args.broad_capture and (work/'broad.bin').exists():
            try:result['broad_capture']=broad_capture.save_analysis(work/'broad.bin')
            except ValueError as exc:error=(error+'; ' if error else '')+str(exc);result['error']=error;result['result']='PARTIAL'
        if search:result['expanded_search_verdict']=depth_search_channel.verdict(search)
        if args.multi_ship and args.pipeline_mode=='test':
            try:
                sys.path.insert(0,str(ROOT/'tools/m1_component'))
                from identity_census import analyze_summary
                result['identity_census']=analyze_summary(work/'gate/M1-A-summary.json')
                if not result['identity_census']['enabled']:raise ValueError('Full-window identity census inactive')
                if result['identity_census']['omitted_observations']:result['result']='PARTIAL'
            except (ValueError,OSError,KeyError) as exc:
                error=(error+'; ' if error else '')+'Identity census: '+str(exc);result['error']=error;result['result']='PARTIAL'
        if args.multi_ship and args.pipeline_mode=='performance':
            result['identity_census']={'enabled':False,'reason':'Performance mode;identity safeguards remain active'}
        result['pipeline_policy']=mode_policy(args.pipeline_mode)
        result['experimental_parallel_assets']=args.experimental_parallel_assets
        result['final_report_complete']=True
        run_report.save(work,result)
    print('Evidence: '+str(work),flush=True)
    if error:raise RuntimeError(error)
if __name__=='__main__':
    try:main()
    except BaseException as exc:
        run_report.failure(exc)
        raise
