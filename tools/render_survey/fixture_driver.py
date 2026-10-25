# Isolated RENDER-FAMILY-SURVEY-001 driver snapshot of tools/remix_runtime/run_return_fixture.py.
# Only observation-only metadata mode is admitted; normal launcher/source unchanged.
import sys
from pathlib import Path as _Path
sys.path.insert(0,str(_Path(__file__).resolve().parents[1]/'remix_runtime'))
"""Bounded offline same-proxy image-compositor validation. NEVER launches SFC."""
from pathlib import Path
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess as sp
import time
from return_channel import Channel,valid_name
import depth_search_channel
import survey_capture as broad_capture

ROOT=Path(__file__).resolve().parents[2]
DLL=ROOT/'artifacts/remix-runtime/deps/remix-1.5.2/.trex/d3d9.dll'
BIN=ROOT/'artifacts/remix-runtime/return-bin'
TEST=Path(r'C:\Project\SFC-Remix-Return-Test')
ENV={'DXVK_LOG_LEVEL':'error','DXVK_GRAPHICS_PRESET_TYPE':'4','RTX_INTEGRATE_INDIRECT_MODE':'0','DXVK_UPSCALER_TYPE':'0','DXVK_RAY_RECONSTRUCTION':'False','RTX_DLSS_PRESET':'0','RTX_ENABLE_ASYNC_COMPILATION':'False'}
def digest(p):
    with open(p,'rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest().upper()
def capture_file_bytes(path):
    # A worker atomically renames its tiny .pending light packet while this
    # supervisor inventories output. Vanished names are not missing evidence;
    # their destination is included on this or the next bounded poll.
    try:return path.stat().st_size if path.is_file() else 0
    except FileNotFoundError:return 0

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--graceful',action='store_true',help='Signal stop instead of intentional renderer crash')
    inspect=parser.add_mutually_exclusive_group()
    inspect.add_argument('--inspect-visibility',action='store_true',help='Exercise read-only late depth-binding observation')
    inspect.add_argument('--inspect-early-depth',action='store_true',help='Exercise supported pre-effects Present observation')
    inspect.add_argument('--search-depth',action='store_true',help='Expanded six-phase engine/presentation search')
    inspect.add_argument('--broad-capture',action='store_true',help='Full-support public event capture,10seconds,2GB ceiling')
    inspect.add_argument('--depth-snapshots',action='store_true',help='Three read-only 8sample depth snapshots, no SFC')
    inspect.add_argument('--source-timing',action='store_true',help='Metadata-only offer/Present/overlay timing;no runtime rendering')
    parser.add_argument('--live-owner-timing',action='store_true',help='Standalone raw owner/proxy/ordinary-D3D9 GPU fixture,no SFC')
    parser.add_argument('--d3d9-additive',action='store_true',help='Offline actual-proxy/ordinary-D3D9 additive GPU fixture;NOT SFC')
    parser.add_argument('--rebind-owner',action='store_true',help='Standalone synthetic owner epochs through actual resident renderer;requires additive')
    parser.add_argument('--persistent-scene',action='store_true',help='Exercise version2 persistent-source wire through actual GPU return fixture')
    parser.add_argument('--synchronized-buffer',action='store_true',help='Exercise complete-game-frame/ship one-frame pairing,standalone fixture only')
    parser.add_argument('--buffer-early-ready',action='store_true',help='Use normal16ms source lead to exercise queued output before the saved scene is presented')
    parser.add_argument('--multi-ship',action='store_true',help='Two different historical fresh packets through aligned retained scene;offline only')
    parser.add_argument('--runtime-candidate',choices=('1.6.1',),help='Isolated pinned runtime/header/host experiment;never changes gameplay dependency')
    parser.add_argument('--candidate-initial-replacements',action='store_true',help='Candidate diagnosis only: enable stock replacement policy before device creation')
    parser.add_argument('--candidate-asset-loading',choices=('inherit','synchronous'),default='inherit',help='Candidate offline only: change just NVIDIA initial asset-loading policy;other async controls unchanged')
    parser.add_argument('--pipeline-mode',choices=('performance','test'),default='test')
    parser.add_argument('--prewarm',action='store_true',help='Start native renderer before discovering prepared fixture assets')
    parser.add_argument('--startup-profile',action='store_true',help='Offline only: bounded native startup phase/QPC/memory measurements')
    parser.add_argument('--loading-policy',choices=('inherit','async','blocking','rtxio'),default='inherit',help='Offline startup only: explicitly exercise pinned Remix loading/compilation settings')
    parser.add_argument('--material-library',choices=('layers','flat'),default='layers',help='Offline startup only: same materials/images without layered USD composition')
    parser.add_argument('--material-texture-loading',choices=('preload','stream'),default='preload',help='Offline only: compare existing Remix per-material preload flag with native streaming;image bytes unchanged')
    parser.add_argument('--native-log-level',choices=('inherit','error'),default='inherit',help='Offline startup only: test built-in runtime logging cost;errors remain')
    parser.add_argument('--api-texture-prefetch',action='store_true',help='Offline only: qualify public material API texture-cache reuse before first draw;not GPU-residency proof')
    parser.add_argument('--overlap-texture-prefetch',action='store_true',help='Offline only: feed finalized per-asset texture requests during remaining preparation')
    parser.add_argument('--menu-idle-seconds',type=int,choices=(0,60),default=0,help='Offline startup profile only: wait before any synthetic scene publication')
    parser.add_argument('--render-prewarm',choices=('off','empty','triangle'),default='off',help='Experimental offline startup only: render unpublished warm-up frames before scene activation')
    parser.add_argument('--isolate-initial-material-library',action='store_true',help='Offline diagnosis ONLY: retain empty master material library;not appearance/qualification evidence')
    parser.add_argument('--multi-ship-resources',action='store_true',help='Offline three captured assets plus independent shared-asset owner;not game evidence')
    parser.add_argument('--multi-ship-late-asset',action='store_true',help='Offline third distinct asset first observed after120returned frames')
    parser.add_argument('--isolate-late-material-reload',action='store_true',help='Offline diagnosis ONLY:skip late material-list rewrite;not appearance/qualification evidence')
    parser.add_argument('--slow-end-scene',action='store_true',help='Offline only: detach while simulated original COM call sleeps')
    parser.add_argument('--with-depth',action='store_true',help='Bind known synthetic D24S8 descriptor, not actual scene depth')
    parser.add_argument('--observation-only',action='store_true',help='No Remix runtime/image; control channel and depth observations only')
    args=parser.parse_args()
    if not (args.broad_capture and args.observation_only):parser.error('Isolated survey driver accepts observation-only broad mode only')
    if args.runtime_candidate and not(args.multi_ship and args.prewarm):parser.error('--runtime-candidate requires --multi-ship --prewarm')
    if args.candidate_initial_replacements and not args.runtime_candidate:parser.error('--candidate-initial-replacements requires --runtime-candidate')
    if args.candidate_asset_loading!='inherit':
        if not args.runtime_candidate:parser.error('--candidate-asset-loading requires --runtime-candidate')
        if args.loading_policy!='inherit':parser.error('--candidate-asset-loading excludes --loading-policy overrides')
    if args.startup_profile and not(args.multi_ship and args.prewarm):parser.error('--startup-profile requires --multi-ship --prewarm')
    if args.loading_policy!='inherit' and not args.startup_profile:parser.error('--loading-policy requires --startup-profile')
    if args.material_library!='layers' and not args.startup_profile:parser.error('--material-library requires --startup-profile')
    if args.material_texture_loading!='preload' and (not args.startup_profile or args.material_library!='layers' or args.api_texture_prefetch):parser.error('Texture streaming comparison requires startup profile/layers and excludes API prefetch')
    if args.native_log_level!='inherit' and not args.startup_profile:parser.error('--native-log-level requires --startup-profile')
    if args.api_texture_prefetch and not args.startup_profile:parser.error('--api-texture-prefetch requires --startup-profile')
    if args.overlap_texture_prefetch and not args.api_texture_prefetch:parser.error('--overlap-texture-prefetch requires --api-texture-prefetch')
    if args.menu_idle_seconds and not args.startup_profile:parser.error('--menu-idle-seconds requires --startup-profile')
    if args.render_prewarm!='off' and not args.startup_profile:parser.error('--render-prewarm requires --startup-profile')
    if args.isolate_initial_material_library and not args.startup_profile:parser.error('--isolate-initial-material-library requires --startup-profile')
    os.environ.pop('SFC_D3D9_RENDER_PREWARM',None)
    if args.render_prewarm!='off':os.environ['SFC_D3D9_RENDER_PREWARM']=args.render_prewarm
    # Relay workers inherit the supervisor environment; this switch exists ONLY
    # on the standalone fixture, never a normal gameplay or callback setting.
    if args.startup_profile:os.environ['SFC_D3D9_STARTUP_PROFILE']='1'
    if args.multi_ship_resources and not args.multi_ship:parser.error('--multi-ship-resources requires --multi-ship')
    if args.multi_ship_late_asset and not args.multi_ship_resources:parser.error('--multi-ship-late-asset requires --multi-ship-resources')
    if args.isolate_late_material_reload and not args.multi_ship:parser.error('--isolate-late-material-reload requires --multi-ship')
    if args.multi_ship:args.d3d9_additive=True;args.synchronized_buffer=True
    if args.buffer_early_ready and not args.synchronized_buffer:parser.error('--buffer-early-ready requires --synchronized-buffer')
    if args.rebind_owner and not args.d3d9_additive:parser.error('--rebind-owner requires --d3d9-additive')
    if args.persistent_scene and not args.d3d9_additive:parser.error('--persistent-scene requires --d3d9-additive')
    if args.synchronized_buffer:
        if not args.d3d9_additive:parser.error('--synchronized-buffer requires --d3d9-additive')
        args.persistent_scene=True
    if args.d3d9_additive:args.live_owner_timing=True;args.source_timing=True;args.observation_only=True;args.graceful=True
    inspect_requested=args.inspect_visibility or args.inspect_early_depth
    if args.with_depth and not (args.inspect_early_depth or args.search_depth or args.broad_capture or args.depth_snapshots):parser.error('--with-depth requires --inspect-early-depth or --search-depth or --broad-capture or --depth-snapshots')
    if args.observation_only and (not (args.inspect_early_depth or args.search_depth or args.broad_capture or args.depth_snapshots or args.source_timing) or not args.graceful):parser.error('--observation-only requires a read-only mode and --graceful')
    if args.source_timing and not(args.observation_only and args.graceful):parser.error('--source-timing requires --observation-only --graceful')
    if args.live_owner_timing and not args.source_timing:parser.error('--live-owner-timing requires --source-timing')
    if args.depth_snapshots and not (args.observation_only and args.graceful):parser.error('--depth-snapshots requires --observation-only and --graceful')
    if args.broad_capture and not (args.observation_only and args.graceful):parser.error('--broad-capture requires --observation-only and --graceful')
    if args.search_depth and not args.observation_only:parser.error('--search-depth requires --observation-only')
    if args.slow_end_scene and not args.search_depth:parser.error('--slow-end-scene requires --search-depth')
    if digest(DLL)!='F7C310821AA98BCDFDEC120330B0A89457B7C5EBA58D21464AF32639611C809F':raise RuntimeError('Pinned Remix changed')
    if digest(TEST/'dxgi.dll')!='E35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7':raise RuntimeError('Copied proxy changed')
    if args.d3d9_additive:
        import sys
        sys.path.insert(0,str(ROOT/'tools/d3d9_proof'))
        from run_offline import storage,AGGREGATE_BYTES
        # Include concurrent image-converter reservations, not just the eventual
        # compressed output. Otherwise a fixture can start but refuse an owner.
        reserve_mib=1024 if args.multi_ship_resources else (768 if args.multi_ship else 192)
        if storage()+reserve_mib*1024*1024>AGGREGATE_BYTES:
            raise RuntimeError(f'Additive fixture lacks{reserve_mib}MiB reservation within20GB cap;archive completed evidence first')
    backend_locks=None
    if args.multi_ship:
        from qualify_multiship import locks
        backend_locks=locks()
    candidate_receipt=None
    if args.runtime_candidate:
        from runtime_candidate import verify
        import live_owner_timing
        candidate=verify(require_host=True)
        if not candidate['exe'].is_file():raise ValueError('Build isolated candidate host first')
        # This standalone supervisor process only. No environment override or
        # persistent gameplay pin can select an experimental dependency.
        live_owner_timing.EXE=candidate['exe'];live_owner_timing.RUNTIME=candidate['runtime']
        if args.candidate_initial_replacements:
            import multi_scene_relay
            old='rtx.enableReplacementAssets = False'
            if multi_scene_relay.CONFIG.count(old)!=1:raise ValueError('Candidate startup policy no longer matches')
            multi_scene_relay.CONFIG=multi_scene_relay.CONFIG.replace(old,'rtx.enableReplacementAssets = True')
        candidate_receipt=dict(release=args.runtime_candidate,manifest=candidate['manifest'],
                               host_sha256=digest(candidate['exe']),runtime_path=str(candidate['runtime']),
                               initial_replacements_enabled=args.candidate_initial_replacements)
        candidate_receipt['asset_loading']=args.candidate_asset_loading
    work=ROOT/'artifacts/remix-runtime/runs'/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f-return-fixture');work.mkdir()
    for source,name in [(broad_capture.qualified_full() if args.broad_capture or args.depth_snapshots or args.d3d9_additive else TEST/'dxgi.dll','dxgi.dll'),(ROOT/'artifacts/render-survey/bin/d3d11_return_fixture.exe','d3d11_return_fixture.exe'),(ROOT/'artifacts/render-survey/bin/SFCRemixReturn.dll','SFCRemixReturn.dll')]:shutil.copyfile(source,work/name)
    # No existing game config changed. Disable fixture menu/input capture only.
    (work/'ReShade.ini').write_text('[GENERAL]\nEffectSearchPaths=./no-effects\nPresetPath=./fixture.ini\n[OVERLAY]\nTutorialProgress=4\nShowFPS=0\nShowFrameTime=0\n[INPUT]\nInputProcessing=0\n')
    env={**os.environ,**ENV,'DXVK_LOG_PATH':str(work)}
    env.pop('SFC_FIXTURE_SHIP_SNAPSHOT',None)
    if args.startup_profile:env['SFC_FIXTURE_SHIP_SNAPSHOT']='1'
    env.pop('SFC_FIXTURE_MENU_IDLE_MS',None)
    if args.menu_idle_seconds:env['SFC_FIXTURE_MENU_IDLE_MS']=str(args.menu_idle_seconds*1000)
    env['SFC_PIPELINE_MODE']=args.pipeline_mode if args.multi_ship else 'test'
    host=fixture=channel=None;semantic=None;timing_result=None;streams=[];start=time.monotonic();error=None;history=[];live_relay=None;live_result=None;live_manifest=None;live_rows=[]
    try:
        def output(name):
            f=open(work/name,'wb');streams.append(f);return f
        host=sp.Popen([str(BIN/'return_host.exe'),'--observe-only' if args.observation_only else str(DLL)],cwd=work,env=env,stdout=output('host.log'),stderr=sp.STDOUT,creationflags=sp.CREATE_NO_WINDOW)
        session=None
        while time.monotonic()-start<60:
            if host.poll() is not None:raise RuntimeError('Runtime host exited before session ready')
            text=(work/'host.log').read_text(errors='replace')
            session=next((line[8:] for line in text.splitlines() if line.startswith('SESSION ')),None)
            if session:break
            time.sleep(.1)
        if not session or not valid_name(session):raise RuntimeError('Runtime session startup failed')
        channel=Channel(session)
        env.update(SFC_REMIX_RETURN_SESSION=session,SFC_REMIX_EXPECTED_IMAGE=str(work/'d3d11_return_fixture.exe'),SFC_REMIX_PRELOAD_REQUIRED='1')
        env.pop('SFC_D3D9_SOURCE_TIMING',None)
        env.pop('SFC_D3D9_LIVE_TIMING',None);env.pop('SFC_D3D9_FIXTURE_ROWS',None)
        env.pop('SFC_D3D9_MULTISCENE',None)
        env.pop('SFC_MULTISCENE_LATE_ASSET',None)
        if args.source_timing:
            from present_calibration import Receiver
            semantic=Receiver();env.update(SFC_D3D9_SOURCE_TIMING='1',SFC_REMIX_CALIBRATION_SCENE=semantic.name)
        if args.live_owner_timing:
            if args.multi_ship:from multi_scene_relay import Relay
            else:from live_owner_timing import Relay
            from run_offline import CAPTURE
            from scene_bundle import snapshots
            from live_scene import decode_mesh
            mode_args={'pipeline_mode':args.pipeline_mode} if args.multi_ship else {}
            live_relay=Relay(work,semantic,TEST,additive=args.d3d9_additive,offline_fixture=args.d3d9_additive,persistent=args.persistent_scene,buffered=args.synchronized_buffer,**mode_args)
            if args.multi_ship:live_relay.isolate_late_material_reload=args.isolate_late_material_reload
            if args.multi_ship:live_relay.isolate_initial_material_library=args.isolate_initial_material_library
            if args.multi_ship:live_relay.loading_policy=args.loading_policy
            if args.runtime_candidate:
                live_relay.candidate_release=args.runtime_candidate
                live_relay.candidate_asset_loading=args.candidate_asset_loading
            if args.multi_ship:live_relay.material_library=args.material_library
            if args.multi_ship:live_relay.material_texture_loading=args.material_texture_loading
            if args.multi_ship:live_relay.native_log_level=args.native_log_level
            if args.multi_ship:live_relay.api_texture_prefetch=args.api_texture_prefetch
            if args.multi_ship:live_relay.overlap_texture_prefetch=args.overlap_texture_prefetch
            if args.multi_ship:
                from multi_scene_fixture import rows_and_packets
                live_rows=rows_and_packets(work,semantic.name,extended=args.multi_ship_resources)
                env.update(SFC_D3D9_LIVE_TIMING='1',SFC_D3D9_MULTISCENE='1',SFC_D3D9_FIXTURE_ROWS=str(work/'fixture-rows.bin'))
                if args.multi_ship_late_asset:env['SFC_MULTISCENE_LATE_ASSET']='1'
            else:
                mesh=decode_mesh((CAPTURE/'LIVE-SCENE-001-asset-3.bin').read_bytes(),(CAPTURE/'LIVE-SCENE-001-asset-3.json').read_bytes())
                selected_frames=snapshots(mesh,CAPTURE/'LIVE-SCENE-001-updates.jsonl',3)
                all_rows=(CAPTURE/'LIVE-SCENE-001-updates.jsonl').read_text().splitlines()
                live_rows=[json.loads(all_rows[f['line']-1]) for f in selected_frames]
                gate=work/'gate';gate.mkdir()
                for extension in ('bin','json'):shutil.copyfile(CAPTURE/f'LIVE-SCENE-001-asset-3.{extension}',gate/f'LIVE-SCENE-001-asset-3.{extension}')
                (gate/'LIVE-SCENE-001-updates.jsonl').write_bytes(b'')
                (work/'manifest.json').write_text(json.dumps(dict(synthetic_source=True,source_packet_sha256=digest(CAPTURE/'LIVE-SCENE-001-asset-3.bin'),semantic_calibration={'scene_session':semantic.name}),indent=2))
                (work/'fixture-rows.bin').write_bytes(b''.join(struct.pack('<96I',*r) for r in live_rows))
                env.update(SFC_D3D9_LIVE_TIMING='1',SFC_D3D9_FIXTURE_ROWS=str(work/'fixture-rows.bin'))
        env.pop('SFC_D3D9_GAME_OUTPUT',None)
        if args.d3d9_additive:env['SFC_D3D9_GAME_OUTPUT']='1'
        env.pop('SFC_D3D9_REBIND_FIXTURE',None)
        if args.rebind_owner:env['SFC_D3D9_REBIND_FIXTURE']='1'
        env.pop('SFC_REMIX_BROAD_OUTPUT',None)
        env.pop('SFC_REMIX_DEPTH_OUTPUT',None)
        if args.depth_snapshots:env['SFC_REMIX_DEPTH_OUTPUT']=str(work)
        if args.broad_capture:env['SFC_REMIX_BROAD_OUTPUT']=str(work/'broad.bin')
        env['SFC_REMIX_INSPECT_VISIBILITY']='3' if args.search_depth else ('2' if args.inspect_early_depth else ('1' if args.inspect_visibility else '0'))
        env.pop('SFC_RETURN_FIXTURE_DEPTH',None)
        env.pop('SFC_D3D9_SYNC_BUFFER',None)
        env.pop('SFC_SYNC_FIXTURE_SHORT_LEAD',None)
        if args.synchronized_buffer:
            env['SFC_D3D9_SYNC_BUFFER']='1'
            if not args.buffer_early_ready:env['SFC_SYNC_FIXTURE_SHORT_LEAD']='1'
        env.pop('SFC_RETURN_OBSERVATION_ONLY',None)
        env.pop('SFC_RETURN_EXPANDED_SEARCH',None)
        env.pop('SFC_RETURN_SLOW_END',None)
        if args.with_depth:env['SFC_RETURN_FIXTURE_DEPTH']='1'
        if args.d3d9_additive:env['SFC_RETURN_FIXTURE_DEPTH']='1'
        if args.observation_only:env['SFC_RETURN_OBSERVATION_ONLY']='1'
        if args.search_depth:env['SFC_RETURN_EXPANDED_SEARCH']='1'
        if args.slow_end_scene:env['SFC_RETURN_SLOW_END']='1'
        fixture=sp.Popen([str(ROOT/'artifacts/render-survey/bin/survey_fixture_launcher.exe'),'--fixture',str(work/'d3d11_return_fixture.exe'),str(work/'SFCRemixReturn.dll'),digest(work/'d3d11_return_fixture.exe'),digest(work/'SFCRemixReturn.dll')],cwd=work,env=env,stdout=output('fixture.log'),stderr=sp.STDOUT,creationflags=sp.CREATE_NO_WINDOW)
        disabled_at=None;reenabled=False;killed=False;last=0;rebind_requests=[]
        while fixture.poll() is None:
            elapsed=time.monotonic()-start
            size=sum(capture_file_bytes(p) for p in work.rglob('*'))
            if args.d3d9_additive:
                images=sum(capture_file_bytes(p) for p in (work/'gpu').rglob('*') if p.suffix.lower()=='.dds' or re.fullmatch(r'texture-\d+\.bin',p.name))
                if not args.multi_ship and images>128*1024*1024:raise RuntimeError('Additive original/derived image128MiB cap')
                size-=images # Separate established image budget;logs remain32MiB.
            if elapsed>100 or size>(broad_capture.HARD+32*1024*1024 if args.broad_capture else (96*1024*1024 if args.depth_snapshots else 32*1024*1024)):raise RuntimeError('Fixture time/output cap')
            text=(work/'fixture.log').read_text(errors='replace')
            if live_relay:
                verified=re.search(r'VERIFIED_CHILD pid=(\d+) suspended_path_match=1 disk_sha_match=1',text)
                raw_pid=struct.unpack_from('<I',semantic.channel.read(10*1024*1024,32),28)[0]
                if verified and raw_pid==int(verified[1]):
                    if args.prewarm and args.multi_ship:live_relay.start_on_launch(raw_pid)
                    live_relay.poll(raw_pid)
            state=channel.snapshot()
            if args.rebind_owner and live_relay and live_relay.process and len(rebind_requests)<2:
                from owner_rebind import acknowledged,request
                generation=len(rebind_requests)+2
                if acknowledged(semantic.channel)==generation-1 and state['drawCount']>=(120 if generation==2 else 300):
                    row=list(live_rows[0]);row[1]=generation+10;row[7]=generation+10;row[5]+=generation;row[6]+=generation
                    request(semantic.channel,generation,row,int(live_relay.content_signature[:16],16) or 1)
                    # Historical-light replay carries matching SYNTHETIC identity only.
                    replay=live_relay.light_replay;replay.owner=row[1]
                    replay.snapshot.update(owner_epoch=row[1],model_process_local=row[5],source_process_local=row[6])
                    rebind_requests.append(dict(generation=generation,owner=row[1],revision=row[7]))
            if args.search_depth and elapsed>8:channel.set('stop',1)
            if args.slow_end_scene and state['ready'] and depth_search_channel.snapshot(channel.address)['reserved']==1:channel.set('stop',1)
            if state['ready'] and not disabled_at:
                channel.set('armed',1);channel.set('enabled',int(args.d3d9_additive or not args.observation_only))
            if 'SAMPLE enabled ' in text and disabled_at is None:
                channel.set('enabled',0);disabled_at=time.monotonic()
            if disabled_at and 'SAMPLE disabled ' in text and time.monotonic()-disabled_at>1 and not reenabled:
                channel.set('enabled',1);reenabled=True
            if 'SAMPLE recreated ' in text and not killed and (not inspect_requested or state['visibilitySamples']>=8):
                if args.graceful:
                    channel.set('stop',1)
                else:
                    host.kill();host.wait(timeout=5) # Explicit owned-renderer crash test.
                killed=True
            if elapsed-last>.25:history.append({'seconds':elapsed,**state});last=elapsed
            time.sleep(.05)
        fixture.wait(timeout=5)
        if fixture.returncode:raise RuntimeError('Native fixture failed: '+str(fixture.returncode))
        text=(work/'fixture.log').read_text(errors='replace')
        if args.broad_capture:
            broad=broad_capture.save_analysis(work/'broad.bin')
            if 'BROAD_END ' not in text or 'state_errors=0' not in text or broad['header']['error']:raise RuntimeError('Broad fixture failed')
            if not broad['counts'].get('resource') or not broad['counts'].get('view') or not broad['counts'].get('targets'):raise RuntimeError('Full-support events not delivered')
            if args.with_depth and not broad['depth_candidates']:raise RuntimeError('Known transient depth missing')
            if not args.with_depth and broad['depth_candidates']:raise RuntimeError('Unexpected depth in negative fixture')
            channel.set('stop',1)
        elif args.search_depth:
            search=depth_search_channel.snapshot(channel.address)
            if 'SEARCH_END ' not in text or 'state_errors=0 restored=15 seen=63' not in text:raise RuntimeError('Expanded fixture restoration/state evidence incomplete')
            if search['error'] or search['status']!=4 or search['restoredMask']!=15:raise RuntimeError('Expanded search cleanup not confirmed')
            if args.with_depth and not search['resourceCount']:raise RuntimeError('Known depth missing from expanded search')
            if not args.with_depth and search['resourceCount']:raise RuntimeError('Unexpected depth in negative fixture')
            channel.set('stop',1)
        elif args.depth_snapshots:
            if 'DEPTH_SNAPSHOT_END ' not in text or 'state_errors=0' not in text:raise RuntimeError('Depth snapshot fixture state evidence incomplete')
            channel.set('stop',1)
            from depth_snapshot_analysis import analyze_run
            report=analyze_run(work,images=True)
            if bool(report['complete'])!=args.with_depth:raise RuntimeError('Depth snapshot positive/negative evidence failed')
            if not args.with_depth and report['snapshots']:raise RuntimeError('Unexpected depth without candidate')
        elif args.source_timing:
            if 'SOURCE_TIMING_END ' not in text or 'state_errors=0 resized=1 recreated=1' not in text:raise RuntimeError('Source timing fixture state evidence incomplete')
            from source_timing import save
            timing_result=save(semantic.channel,work)
            if timing_result['result']!='SOURCE_TIMING_OBSERVATION_COMPLETE_ADJUDICATION_REQUIRED' or timing_result['records']<300 or timing_result['exact_frame_owner_pairs']<150:raise RuntimeError('Source timing callbacks incomplete')
            channel.set('stop',1)
        elif args.observation_only:
            if 'OBSERVATION_END ' not in text or 'state_errors=0 samples=8 resized=1 recreated=1' not in text:raise RuntimeError('Observation fixture state evidence incomplete')
            channel.set('stop',1)
        elif 'phases=11111' not in text or 'state_errors=0' not in text or not killed:raise RuntimeError('Fixture phase/state evidence incomplete')
        if not channel.state.startupRestored or not channel.state.startupVerified:raise RuntimeError('Startup preload/path evidence incomplete')
        if args.rebind_owner:
            from owner_rebind import acknowledged
            native_log=(work/'gpu/job-console.log').read_text()
            if len(rebind_requests)!=2 or acknowledged(semantic.channel)!=3 or 'OWNER_REBOUND generation=3' not in native_log:
                raise RuntimeError('Actual resident-renderer rebind acknowledgements incomplete')
        if inspect_requested:
            s=channel.state
            if s.visibilitySamples!=8 or s.depthPresentSamples!=(8 if args.with_depth else 0) or s.visibilityScope!=(2 if args.inspect_early_depth else 1):raise RuntimeError('Unexpected fixture visibility count/scope')
            if args.with_depth:
                # Existing proxy may expose a shader-readable typeless resource
                # behind a typed D24S8 view. Compare exact independently logged
                # native descriptor, not the originally requested resource format.
                known=re.findall(r'KNOWN_FIXTURE_DEPTH width=(\d+) height=(\d+) resource_format=(\d+) view_format=(\d+) flags=(\d+)',text)
                observed=(s.depthWidth,s.depthHeight,s.depthFormat,s.depthViewFormat,s.depthBindFlags)
                if not known or observed!=tuple(map(int,known[-1])) or s.depthViewFormat!=45 or not(s.depthBindFlags&64) or s.depthMultisamples!=1:raise RuntimeError('Known fixture depth descriptor mismatch')
        if args.graceful:
            host.wait(timeout=8)
            if host.returncode:raise RuntimeError('Graceful host shutdown failed')
    except Exception as exc:error=str(exc)
    finally:
        if channel:
            channel.set('enabled',0);channel.set('stop',1)
        for p in (fixture,host):
            if p and p.poll() is None:
                p.terminate()
                try:p.wait(timeout=5)
                except sp.TimeoutExpired:p.kill();p.wait(timeout=5)
        final=channel.snapshot() if channel else None
        search=None
        if channel and args.search_depth:
            try:search=depth_search_channel.snapshot(channel.address)
            except ValueError:pass
        if channel:channel.close()
        if live_relay:
            try:
                raw_pid=struct.unpack_from('<I',semantic.channel.read(10*1024*1024,32),28)[0]
                live_result=live_relay.finish(raw_pid)
            except Exception as exc:error=(error+'; ' if error else '')+'Live fixture: '+str(exc)
        if semantic:semantic.close()
        for f in streams:f.close()
        (work/'result.json').write_text(json.dumps({'probe':'REMIX-RETURN-001-FIXTURE','expanded_search':search,'observation_only':args.observation_only,'graceful':args.graceful,'inspect_early_depth':args.inspect_early_depth,'inspect_visibility':args.inspect_visibility,'known_fixture_depth':args.with_depth,'error':error,'seconds':time.monotonic()-start,'host_exit':host.returncode if host else None,'fixture_exit':fixture.returncode if fixture else None,'history':history,'final':final,'runtime_environment':ENV,'source_files':{p.name:digest(p) for p in (BIN/'return_host.exe',ROOT/'artifacts/render-survey/bin/SFCRemixReturn.dll',ROOT/'artifacts/render-survey/bin/d3d11_return_fixture.exe',ROOT/'artifacts/render-survey/bin/survey_fixture_launcher.exe')}},indent=2))
    receipt=json.loads((work/'result.json').read_text());receipt.update(source_timing_requested=args.source_timing,source_timing=timing_result,live_owner_timing=live_result)
    receipt['persistent_wire_fixture']=args.persistent_scene
    receipt['synchronized_buffer_fixture']=args.synchronized_buffer
    receipt['buffer_early_ready_fixture']=args.buffer_early_ready
    receipt['multi_ship_fixture']=args.multi_ship
    receipt['pipeline_mode']=args.pipeline_mode
    receipt['prewarm']=args.prewarm
    receipt['runtime_candidate']=candidate_receipt
    receipt['startup_profile']=args.startup_profile
    receipt['menu_idle_seconds']=args.menu_idle_seconds
    receipt['render_prewarm']=args.render_prewarm
    receipt['loading_policy']=args.loading_policy
    receipt['material_library']=args.material_library
    receipt['material_texture_loading']=args.material_texture_loading
    receipt['native_log_level']=args.native_log_level
    receipt['api_texture_prefetch']=args.api_texture_prefetch
    receipt['overlap_texture_prefetch']=args.overlap_texture_prefetch
    receipt['diagnostic_skip_initial_material_library']=args.isolate_initial_material_library
    receipt['multi_ship_resources_fixture']=args.multi_ship_resources
    receipt['multi_ship_late_asset_fixture']=args.multi_ship_late_asset
    receipt['diagnostic_skip_late_material_reload']=args.isolate_late_material_reload
    if backend_locks:receipt['multi_ship_build_locks']=backend_locks
    if args.rebind_owner:receipt['synthetic_rebind_requests']=rebind_requests
    (work/'result.json').write_text(json.dumps(receipt,indent=2))
    print(f'Evidence: {work}')
    if timing_result:print(json.dumps(timing_result,indent=2))
    if (work/'fixture.log').exists():print((work/'fixture.log').read_text(errors='replace'))
    if error:raise RuntimeError(error)
if __name__=='__main__':main()
