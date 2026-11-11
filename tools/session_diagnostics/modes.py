"""Development-only capture modes and timed observation; never shipped."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src/session'))
sys.path.insert(0,str(ROOT/'tools/remix_runtime'))
from coordinator import (
    Session,ASSETS,OWNERS,BIN,C,CLIENT,CONTEXT,DLL,ENV,SOURCE,TEST,
    argparse,capture_file_bytes,compat_flags,critical_hashes,digest,dt,
    game_running,image_path,json,launcher_paths,os,preflight,protected_ini_sha256,re,
    run_report,shutil,sp,tactical_gate_timeout,time,wait_live_gate,winsound,
    wait_component_ready,write_native_config,
)
from return_channel import visibility_result
from exit_monitor import early_without_output,partial_live_result
import broad_capture

def observation_phase(elapsed,continuous=False):
    return 0 if continuous else (0 if elapsed<30 else 1 if elapsed<45 else 2 if elapsed<60 else 3)

class DiagnosticSession(Session):
    """Override only mode preparation/observation/analysis; inherit shared lifecycle."""

    def _prepare(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--execute', action='store_true')
        self.parser.add_argument('--budget-seconds', type=int, default=285)
        self.parser.add_argument('--play-session', action='store_true', help='Untimed native replacement until game exit;minimal bounded records')
        self.inspect = self.parser.add_mutually_exclusive_group()
        self.inspect.add_argument('--inspect-visibility', action='store_true', help='At most eight read-only late depth-binding observations; no suppression')
        self.inspect.add_argument('--inspect-early-depth', action='store_true', help='Eight read-only pre-effects Present depth-binding observations; no suppression')
        self.inspect.add_argument('--search-depth', action='store_true', help='Continuous bounded six-phase engine/presentation depth search')
        self.inspect.add_argument('--broad-capture', action='store_true', help='Approved full-support public event burst;10seconds/2GB')
        self.inspect.add_argument('--depth-snapshots', action='store_true', help='Three paired depth/color snapshots,20seconds,no rendering changes')
        self.inspect.add_argument('--source-timing', action='store_true', help='Read-only semantic-offer to presentation timing;no Remix runtime/image')
        self.parser.add_argument('--live-owner-timing', action='store_true', help='Fresh raw semantic owner to separate ordinary-D3D9 renderer;no game drawing')
        self.parser.add_argument('--d3d9-additive', action='store_true', help='Qualified ordinary-D3D9 extra ship;original rendering untouched')
        self.parser.add_argument('--player-replacement', action='store_true', help='Default-off unique player-fixture mesh suppression with complete-frame presentation')
        self.parser.add_argument('--native-foreground', action='store_true', help='Default-off player shield preservation with original native shaders')
        self.parser.add_argument('--native-insertion-observe', action='store_true', help='Read-only native model/draw/output timing;no suppression or returned image')
        self.parser.add_argument('--native-insertion-policy', choices=('Strict', 'ExtraFrame'), help='Qualified pre-effects native player insertion;explicit absolute deadline policy')
        self.parser.add_argument('--native-all-ships', action='store_true', help='Qualified native replacement for all supported retained ships;not just player fixture')
        self.parser.add_argument('--native-resolution', action='store_true', default=CONTEXT.release, help='Use actual game-target extent/generation;alpha uses the six stable SFC sizes')
        self.parser.add_argument('--break-models', action='store_true', help='Default-off fresh indexed debris through retained native insertion')
        self.parser.add_argument('--lifecycle-capture', action='store_true', help='Separate bounded camera-gap/destruction observations;no native death inference')
        self.parser.add_argument('--camera-recovery', action='store_true', help='Two alive camera-away/back checks;no destruction requested')
        self.parser.add_argument('--offscreen-position', action='store_true', help='Default-off external read-only ship position across camera gaps;not renderer input')
        self.parser.add_argument('--persistent-scene', action='store_true', help='Simulation-driven retained native instances;player-ship display first')
        self.parser.add_argument('--synchronized-buffer', action='store_true', help='One complete game-frame delay paired with same-frame ship/depth;default off')
        self.parser.add_argument('--multi-ship', action='store_true', help='Fresh retained different models,configured camera-left diagnostic;originals remain')
        self.parser.add_argument('--experimental-parallel-assets', action='store_true', help='Sponsor-authorized experimental checkout: parallel parts/progressive materials;late-update delivery gate remains unresolved')
        self.parser.add_argument('--async-material-checkout', action='store_true', help='Opt-in qualified1.6.1 single-file material checkout;normal runtime unchanged')
        self.parser.add_argument('--pipeline-mode', choices=('performance', 'test'), default='performance', help='Performance baseline;test adds diagnostic comparisons. Essential safeguards remain in both')
        self.inspect.add_argument('--private-ship', action='store_true', help='Fresh semantic SDK ship return into private game-side target;no visible change')
        self.inspect.add_argument('--visible-ship', action='store_true', help='Fresh matching magenta ship at world-offset position in original camera viewport;original ships unchanged')
        self.inspect.add_argument('--textured-ship', action='store_true', help='Original textures,screen-resolution output,bounded delayed additive display;no suppression')
        self.parser.add_argument('--observation-only', action='store_true', help='Use control-only host; do not start Remix or display triangle')
        self.parser.add_argument('--calibration', action='store_true', help='Opt-in current-frame semantic records paired with three depth snapshots')
        self.parser.add_argument('--capture-ship-image', action='store_true', help='One exact prepared textured ship-layer image;external readback only')
        self.parser.add_argument('--capture-native-lights', action='store_true', help='Read-only bounded native light bank discovery;no lighting changes')
        self.parser.add_argument('--light-wiring', action='store_true', help='Normal90s two-native-directional-light/config wiring check;not long tuning mode')
        self.parser.add_argument('--light-tuning', action='store_true', help='Low-recording live controls until normal game exit;30minute tactical ceiling')
        self.parser.add_argument('--scene-depth', action='store_true', help='Default-off depth-filtered additive ship;original drawing/UI path unchanged')
        self.parser.add_argument('--legacy-startup-warmup', action='store_true', help='Opt-in old24Present startup workaround;default is one Present')
        self.parser.add_argument('--completion-diagnostics', action='store_true', help='Default-off bounded slow renderer-completion records')
        self.parser.add_argument('--light-diagnostics', action='store_true', help='Optional bounded native-to-Remix transient light submission evidence')
        self.damage = self.parser.add_mutually_exclusive_group()
        self.damage.add_argument('--damage-textures', action='store_true', default=None, help='Enable damage layers (default for native multi-ship replacement)')
        self.damage.add_argument('--no-damage-textures', dest='damage_textures', action='store_false', default=None, help='Disable damage layers for a diagnostic comparison')
        self.args = self.parser.parse_args(self.argv)
        if self.args.damage_textures is None:
            self.args.damage_textures = self.args.native_all_ships
        if self.args.play_session and (not self.args.native_all_ships or self.args.pipeline_mode != 'performance' or any((self.args.completion_diagnostics, self.args.light_diagnostics, self.args.light_tuning, self.args.lifecycle_capture, self.args.offscreen_position, self.args.camera_recovery, self.args.calibration, self.args.capture_ship_image, self.args.native_insertion_observe, self.args.broad_capture, self.args.depth_snapshots, self.args.capture_native_lights, self.args.inspect_early_depth, self.args.search_depth, self.args.observation_only, self.args.source_timing))):
            self.parser.error('Play session requires native multi-ship/performance without diagnostic captures or tuning')
        if self.args.search_depth:
            global depth_search_channel
            import depth_search_channel
            self.depth_search_channel = depth_search_channel
        if self.args.native_resolution and (not self.args.native_all_ships):
            self.parser.error('--native-resolution requires --native-all-ships')
        os.environ['SFC_NATIVE_RESOLUTION'] = '1' if self.args.native_resolution else '0'
        if self.args.damage_textures and (not self.args.native_all_ships):
            self.parser.error('Damage textures requires native multi-ship insertion')
        if self.args.break_models and (not self.args.native_all_ships):
            self.parser.error('Break models requires native multi-ship insertion')
        if self.args.native_all_ships and (not self.args.native_insertion_policy):
            self.parser.error('Native multi-ship replacement requires explicit timing policy')
        if self.args.light_diagnostics and (not self.args.native_all_ships):
            self.parser.error('Light diagnostics requires native multi-ship replacement')
        if self.args.native_insertion_policy:
            if self.args.native_insertion_observe or self.args.native_foreground or self.args.light_tuning:
                self.parser.error('Native gate excludes observation,shield replay and tuning')
            self.args.player_replacement = not self.args.native_all_ships
            self.args.multi_ship = True
            self.args.async_material_checkout = True
        if self.args.native_insertion_observe:
            if self.args.native_foreground or self.args.light_tuning or self.args.player_replacement:
                self.parser.error('Native insertion observation excludes replacement,shield replay and tuning')
            self.args.player_replacement = True
            self.args.multi_ship = True
            self.args.async_material_checkout = True
        if self.args.player_replacement and (not self.args.multi_ship or not self.args.async_material_checkout or self.args.light_tuning):
            self.parser.error('Player replacement requires current multi-ship async baseline and excludes tuning')
        if self.args.native_foreground and (not self.args.player_replacement):
            self.parser.error('Native foreground requires player replacement')
        self.d3d9_tuning = self.args.light_tuning and self.args.multi_ship
        if self.d3d9_tuning and (not self.args.async_material_checkout):
            self.parser.error('D3D9 tuning requires the current --async-material-checkout baseline')
        if self.args.async_material_checkout and (not self.args.multi_ship or self.args.pipeline_mode != 'performance' or self.args.experimental_parallel_assets):
            self.parser.error('--async-material-checkout requires performance multi-ship and excludes the older experimental checkout')
        if self.args.experimental_parallel_assets and (not self.args.multi_ship or self.args.pipeline_mode != 'performance'):
            self.parser.error('--experimental-parallel-assets requires --multi-ship --pipeline-mode performance')
        if self.args.experimental_parallel_assets:
            print('EXPERIMENTAL PARALLEL ASSETS ENABLED: within-ship tasks and progressive materials. Late material updates may interrupt the extra ships;original SFC drawing stays enabled.', flush=True)
        if self.args.multi_ship:
            self.args.d3d9_additive = True
            self.args.synchronized_buffer = True
        if self.args.synchronized_buffer:
            if not self.args.d3d9_additive:
                self.parser.error('--synchronized-buffer requires --d3d9-additive')
            self.args.persistent_scene = True
            if not self.args.multi_ship:
                from qualify_synchronized_buffer import require_qualification as buffer_qualified
                self.buffer_qualified = buffer_qualified
                self.buffer_qualified()
        if self.args.persistent_scene:
            if not self.args.d3d9_additive or self.args.offscreen_position:
                self.parser.error('--persistent-scene requires additive and excludes diagnostic external reader')
            self.args.camera_recovery = True
            if not self.args.multi_ship:
                from qualify_persistent_scene import require_qualification as persistent_qualified
                self.persistent_qualified = persistent_qualified
                self.persistent_qualified()
        if self.args.scene_depth:
            if self.args.light_tuning or self.args.capture_ship_image:
                self.parser.error('--scene-depth is a bounded standalone test,not tuning/image capture')
            self.args.light_wiring = True
        if self.args.light_tuning and (not self.d3d9_tuning):
            self.args.light_wiring = True
        if self.args.light_wiring:
            self.args.capture_native_lights = True
        if self.args.capture_native_lights:
            self.args.textured_ship = True
        if self.args.capture_ship_image:
            self.args.textured_ship = True
        if self.args.textured_ship:
            self.args.visible_ship = True
        if self.args.visible_ship:
            self.args.private_ship = True
        if self.args.offscreen_position:
            if not self.args.d3d9_additive:
                self.parser.error('--offscreen-position requires --d3d9-additive')
            self.args.camera_recovery = True
            from offscreen_position import verify_client
            self.verify_client = verify_client
            self.verify_client(TEST / 'StarFleetOP.exe')
            from qualify_offscreen_position import require_qualification as offscreen_qualified
            self.offscreen_qualified = offscreen_qualified
            self.offscreen_qualified()
        if self.args.camera_recovery:
            self.args.lifecycle_capture = True
        if self.args.multi_ship and self.args.pipeline_mode == 'performance':
            self.args.lifecycle_capture = False
        if self.args.lifecycle_capture and (not self.args.d3d9_additive):
            self.parser.error('--lifecycle-capture requires --d3d9-additive')
        if self.args.lifecycle_capture:
            from qualify_lifecycle_capture import require_qualification as lifecycle_qualified
            self.lifecycle_qualified = lifecycle_qualified
            if not self.args.multi_ship:
                self.lifecycle_qualified()
        if self.args.d3d9_additive:
            if self.args.private_ship or self.args.calibration or (self.args.light_tuning and (not self.d3d9_tuning)) or self.args.broad_capture or self.args.depth_snapshots or self.args.search_depth:
                self.parser.error('--d3d9-additive is separate from SDK/private/capture modes')
            self.args.source_timing = True
            self.args.live_owner_timing = True
            self.args.observation_only = True
            self.args.capture_native_lights = True
        if self.args.private_ship and (self.args.calibration or self.args.observation_only):
            self.parser.error('--private-ship is separate from calibration/observation-only')
        self.semantic_enabled = self.args.calibration or self.args.private_ship or self.args.source_timing
        if self.args.live_owner_timing and (not (self.args.source_timing and self.args.observation_only)):
            self.parser.error('--live-owner-timing requires --source-timing --observation-only')
        self.live_bin = CONTEXT.artifact('remix-runtime/live-return-bin')
        if self.args.calibration and (not (self.args.depth_snapshots and self.args.observation_only)):
            self.parser.error('--calibration requires --depth-snapshots --observation-only')
        if self.args.observation_only and (not (self.args.inspect_early_depth or self.args.search_depth or self.args.broad_capture or self.args.depth_snapshots or self.args.source_timing)):
            self.parser.error('--observation-only requires --inspect-early-depth or --search-depth or --broad-capture or --depth-snapshots or --source-timing')
        if self.args.source_timing and (not self.args.observation_only or self.args.private_ship or self.args.calibration):
            self.parser.error('--source-timing requires observation-only and excludes private/calibration render modes')
        if self.args.depth_snapshots and (not self.args.observation_only):
            self.parser.error('--depth-snapshots requires --observation-only')
        self.full_support = self.args.broad_capture or self.args.depth_snapshots or self.args.scene_depth or self.args.d3d9_additive
        if self.args.broad_capture and (not self.args.observation_only):
            self.parser.error('--broad-capture requires --observation-only')
        if self.args.search_depth and (not self.args.observation_only):
            self.parser.error('--search-depth requires --observation-only')
        if self.args.execute:
            if not C.windll.shell32.IsUserAnAdmin():
                raise RuntimeError('Use the established elevated testing parent. No automatic UAC requested.')
            if game_running():
                raise RuntimeError('Exit the existing SFC game normally before starting or recovering the isolated test.')
            if self.full_support:
                from recover_broad_session import recover_pending
                self.recover_pending = recover_pending
                self.recovered = self.recover_pending(game_running)
                if self.recovered:
                    print('Recovered prior interrupted test: ' + self.recovered, flush=True)
        preflight()
        self.checkout_backend = None
        if self.args.source_timing:
            if self.args.native_insertion_policy:
                if self.args.native_all_ships:
                    from native_cohort import require_qualification as gate_qualified
                    self.gate_qualified = gate_qualified
                else:
                    from native_gate import require_qualification as gate_qualified
                    self.gate_qualified = gate_qualified
                self.require_qualification = lambda: self.gate_qualified(self.args.native_insertion_policy)
            elif self.args.native_insertion_observe:
                from native_insertion_probe import require_qualification
                self.require_qualification = require_qualification
            elif self.args.player_replacement:
                from player_replacement import require_qualification
                self.require_qualification = require_qualification
            elif self.d3d9_tuning:
                from qualify_d3d9_tuning import require_qualification_tuning as require_qualification
                self.require_qualification = require_qualification
            elif self.args.async_material_checkout:
                from qualify_async_material import require_qualification
                self.require_qualification = require_qualification
            elif self.args.multi_ship:
                from qualify_multiship import require_qualification
                self.require_qualification = require_qualification
            elif self.args.d3d9_additive:
                from additive_qualification import require_qualification
                self.require_qualification = require_qualification
            elif self.args.live_owner_timing:
                from live_owner_timing import require_qualification
                self.require_qualification = require_qualification
            else:
                from source_timing import require_qualification
                self.require_qualification = require_qualification
            self.q = self.require_qualification()
            if self.args.native_foreground:
                from native_foreground_qualification import require_qualification as require_foreground
                self.require_foreground = require_foreground
                self.require_foreground()
            if self.args.async_material_checkout:
                self.checkout_backend = self.q['backend_inputs']
            json.dumps(self.q)
            import sys
            sys.path.insert(0, str(ROOT / 'tools/d3d9_proof'))
            if not (CONTEXT.release and self.args.play_session):
                from run_offline import storage, AGGREGATE_BYTES
                self.storage = storage
                self.AGGREGATE_BYTES = AGGREGATE_BYTES
                self.reserve = (544 if self.args.native_all_ships else 288 if self.args.native_insertion_policy else 192 if self.args.d3d9_additive else 128 if self.args.live_owner_timing else 64) * 1024 * 1024
                if self.storage() + self.reserve > self.AGGREGATE_BYTES:
                    raise RuntimeError('Source timing reservation exceeds20GB evidence allowance')
        if self.args.capture_native_lights:
            if CONTEXT.release:
                from release_manifest import load, verified_role
                self.load = load
                self.verified_role = verified_role
                self.light_manifest = self.load(CONTEXT.package_root)
                self.light_qualification = dict(result='RELEASE_MANIFEST_INPUTS', component_sha256=digest(self.verified_role(CONTEXT, self.light_manifest, 'semantic_component')))
            else:
                from light_discovery import require_qualification as require_light_qualification
                self.require_light_qualification = require_light_qualification
                self.light_qualification = self.require_light_qualification()
        if self.args.private_ship:
            from live_return import require_qualification as require_private_qualification
            self.require_private_qualification = require_private_qualification
            self.require_private_qualification(visible=self.args.visible_ship, textured=self.args.textured_ship, capture_image=self.args.capture_ship_image, light_wiring=self.args.light_wiring)
            for self.path in (self.live_bin / 'ship_live_host.exe', self.live_bin / 'SFCRemixReturn.dll'):
                if not self.path.is_file():
                    raise RuntimeError('Private return build missing: ' + str(self.path))
            self.q = json.loads(CONTEXT.artifact('remix-runtime/deps/present-calibration-qualification.json').read_text())
            if self.q['component_sha256'] != digest(CONTEXT.artifact('m1/bin/m1_component.dll')):
                raise RuntimeError('Accepted semantic component changed; requalify ABI before private test')
        if self.args.calibration and (not CONTEXT.artifact('m1/bin/m1_component.dll').is_file()):
            raise RuntimeError('Full semantic component build required')
        if self.args.calibration:
            from present_calibration import require_qualification as require_calibration
            self.require_calibration = require_calibration
            self.require_calibration()
        if self.args.scene_depth:
            from scene_depth import require_qualification as require_depth_test
            self.require_depth_test = require_depth_test
            self.require_depth_test()
        if self.full_support and (not self.args.scene_depth) and (not self.args.d3d9_additive):
            broad_capture.qualified_full()
            broad_capture.reserve_capture_budget()
            self.qualification = CONTEXT.artifact('remix-runtime/deps/reshade-full-6.7.1/qualification.json')
            self.q = json.loads(self.qualification.read_text())
            if self.q.get('proxy_sha256') != broad_capture.FULL_SHA or self.q.get('result') != 'OFFLINE_EVENT_AND_STATE_PASS':
                raise RuntimeError('Full-support offline qualification missing')
            from prepare_full_reshade import source_hashes
            self.source_hashes = source_hashes
            if self.q.get('source_hashes') != self.source_hashes():
                raise RuntimeError('Broad collector sources changed since offline qualification; requalify first')
            if self.args.depth_snapshots:
                from depth_snapshot_analysis import require_qualification
                self.require_qualification = require_qualification
                self.require_qualification()
        self.inspect_requested = self.args.inspect_visibility or self.args.inspect_early_depth
        if not self.args.execute:
            print('Read-only preflight PASS. No game/renderer started.')
            print('Damage textures: ' + ('ON' if self.args.damage_textures else 'OFF'))
            if self.args.play_session:
                print('Play session: untimed until game exit;minimal bounded recording')
            return False
        self.untimed=self.args.play_session
        self.output_enabled=bool(self.args.d3d9_additive or not self.args.observation_only)
        return True

    def _initialize(self):
        if not C.windll.shell32.IsUserAnAdmin():
            raise RuntimeError('Use the established elevated testing parent. No automatic UAC requested.')
        if game_running():
            raise RuntimeError('Exit the existing SFC game normally before starting the isolated test.')
        if not 120 <= self.args.budget_seconds <= 285:
            raise RuntimeError('Prepared workflow budget must be120..285seconds')
        if self.args.textured_ship:
            self.reserve = 384 * 1024 * 1024
            if broad_capture.storage_bytes() + self.reserve > broad_capture.OVERALL or shutil.disk_usage(ROOT).free < self.reserve:
                raise RuntimeError('Textured run/archive exceeds available20GB allowance or disk space')
        self.work = CONTEXT.artifact('remix-runtime/runs') / dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f-in-game')
        self.work.mkdir()
        if CONTEXT.release and self.args.play_session:
            from session_recording import mark
            self.mark = mark
            self.mark(self.work, os.environ.get('SFC_RELEASE_RECORDING', 'off'))
        run_report.save(self.work, dict(result='IN_PROGRESS', probe='REMIX-RETURN-001', stage='prepared', light_wiring=self.args.light_wiring, final_report_complete=False))
        self.start = time.monotonic()
        self.deadline = float('inf') if self.args.play_session else self.start + (1980 if self.args.light_tuning else self.args.budget_seconds)
        self.original = critical_hashes(SOURCE)
        self.paths = launcher_paths()
        self.compat = compat_flags()
        self.host_exe = self.live_bin / 'ship_live_host.exe' if self.args.private_ship else BIN / 'return_host.exe'
        self.addon = self.live_bin / 'SFCRemixReturn.dll' if self.args.private_ship else BIN / 'SFCRemixReturn.dll'
        for src, name in [(self.host_exe, 'renderer-host.bin'), (BIN / 'return_launcher.exe', 'startup-launcher.bin'), (self.addon, 'SFCRemixReturn.dll')]:
            shutil.copyfile(src, self.work / name)
        self.build_files = (BIN / 'return_host.exe', BIN / 'return_launcher.exe', BIN / 'SFCRemixReturn.dll')
        if not (CONTEXT.release and self.args.observation_only):
            self.build_files += (DLL,)
        self.metadata = {'probe': 'REMIX-RETURN-001', 'utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'accepted_critical_before': self.original, 'copied_critical_before': critical_hashes(TEST), 'launcher_settings_before': self.paths, 'source_compatibility': self.compat, 'scene': 'SDK default-material triangle with green sphere light; no SFC draw suppression', 'output_resources_bytes': 2 * 256 * 256 * 4, 'capture_seconds': 90, 'workflow_seconds': self.args.budget_seconds, 'limits_bytes': 32 * 1024 * 1024, 'build_hashes': {p.name: digest(p) for p in self.build_files}}
        self.metadata['visibility_probe'] = {'enabled': self.inspect_requested, 'scope': 'early-present' if self.args.inspect_early_depth else 'late-overlay', 'max_samples': 8, 'minimum_interval_ms': 1000, 'read_only': True, 'qualified_scene_depth': False}
        self.metadata['observation_only'] = self.args.observation_only
        self.metadata['scene_depth_test'] = self.args.scene_depth
        if self.args.source_timing:
            self.metadata.update(probe='D3D9-SOURCE-TIMING-001', scene='Metadata-only semantic offer to Present/overlay;no image or Remix runtime', output_resources_bytes=0, source_timing={'geometry_hook': False, 'record_capacity': 32768, 'record_bytes': 80, 'max_detailed_owners_per_callback': 8, 'storage_bytes': 2621568, 'stages': ['present', 'overlay'], 'source_qpc_extension_words': [89, 90, 91, 92, 93]})
        self.metadata['light_tuning'] = self.args.light_tuning
        self.metadata['play_session'] = self.args.play_session
        self.metadata['copied_sfc_protected_sha256'] = protected_ini_sha256((TEST / 'sfc.ini').read_bytes())
        if self.args.play_session:
            self.metadata.update(capture_seconds=None, workflow_seconds=None, detail_policy='No frame trace or images;120 recent5second status samples;bounded console;functional assets cached once')
        from pipeline_mode import policy as mode_policy
        self.mode_policy = mode_policy
        self.metadata['pipeline_policy'] = self.mode_policy(self.args.pipeline_mode)
        self.metadata['experimental_parallel_assets'] = self.args.experimental_parallel_assets
        if self.args.async_material_checkout:
            from async_material_checkout import receipt
            self.receipt = receipt
            self.metadata['async_material_checkout'] = self.receipt(self.checkout_backend)
        if self.args.light_tuning:
            self.metadata.update(capture_seconds=1800, workflow_seconds=1980, detail_policy='100 scene rows per owner;latest-only native bank;5second presentation samples')
        if self.args.private_ship:
            self.metadata.update(probe='REMIX-LIVE-RETURN-001', scene='Fresh selected ship rendered by SDK to PRIVATE game-side target;no backbuffer changes', output_resources_bytes=4 * 256 * 256 * 4)
            self.metadata['private_ship'] = {'strict_current_frame': True, 'saved_template': False, 'expected_visible_change': bool(self.args.visible_ship), 'host_sha256': digest(self.host_exe), 'addon_sha256': digest(self.addon)}
            if self.args.visible_ship:
                self.metadata['scene'] = 'Fresh SDK magenta ship at diagnostic WORLD offset in original camera viewport;transparent background,original ships ON,no scene-depth or replacement claim'
            if self.args.textured_ship:
                self.metadata.update(scene='Fresh original primary textures,1920x1080 output,100ms delayed additive copy;NOT synchronized replacement', output_resources_bytes=4 * 1920 * 1080 * 4, image_limit_bytes=128 * 1024 * 1024, display_policy='v4 source request age<=100ms;captured pose/camera retained')
            if self.args.textured_ship:
                self.metadata['private_ship'].update(strict_current_frame=False, identity_checked=True, source_provenance_retained=True, maximum_request_age_ms=100)
            self.metadata['build_hashes'] = {p.name: digest(p) for p in (self.host_exe, BIN / 'return_launcher.exe', self.addon, DLL)}
            if self.args.capture_ship_image:
                self.metadata['prepared_ship_image'] = {'probe': 'REMIX-PREPARED-IMAGE-001', 'shots': 1, 'delay_after_first_display_ms': 15000, 'reader_sha256': digest(self.live_bin / 'ship_image_reader.exe'), 'extra_gpu_bytes': 2 * 1920 * 1080 * 4, 'max_raw_bytes': 256 + 1920 * 1080 * 4, 'render_thread_readback': False, 'camera_motion_cues': False}
        self.metadata['depth_snapshots'] = {'enabled': self.args.depth_snapshots, 'probe': 'REMIX-DEPTH-001', 'maximum_pairs': 3, 'tactical_seconds': 20, 'image_limit_bytes': 64 * 1024 * 1024, 'expected_source_samples': 8}
        if self.args.calibration:
            self.metadata['probe'] = 'REMIX-CALIBRATION-001'
        self.metadata['broad_capture'] = {'enabled': self.args.broad_capture, 'proxy_sha256': broad_capture.FULL_SHA, 'tactical_detail_seconds': 10, 'trace_hard_bytes': broad_capture.HARD, 'trace_warning_bytes': 1000000000, 'overall_ceiling_bytes': broad_capture.OVERALL, 'prelude': 'resource/view/device/command lifecycle plus target bindings/reset before tactical gate', 'coverage': 'enumerated public events, not exhaustive GPU/geometry capture'}
        if self.args.broad_capture:
            self.metadata['capture_seconds'] = 10.1
        if self.args.depth_snapshots:
            self.metadata['capture_seconds'] = 20
            self.metadata['limits_bytes'] = 96 * 1024 * 1024
        if self.args.broad_capture:
            self.metadata['limits_bytes'] = broad_capture.HARD + 32 * 1024 * 1024
            self.metadata['ancillary_limit_bytes'] = 32 * 1024 * 1024
        self.metadata['expanded_search'] = {'enabled': self.args.search_depth, 'phases': self.depth_search_channel.PHASES if self.args.search_depth else [], 'resource_limit': 32, 'duration_seconds': 90, 'mapping_extension_bytes': 2304}
        if self.args.observation_only:
            self.metadata['scene'] = 'No Remix runtime started; read-only early depth-binding observation'
        if self.args.source_timing:
            self.metadata['scene'] = 'Semantic source/Present timing,no game drawing'
        if self.args.live_owner_timing:
            self.metadata['scene'] = 'Fresh semantic owner to separate ordinary-D3D9/Remix GPU receiver;current Present audit only,no game drawing'
        if self.args.d3d9_additive:
            self.metadata.update(probe='D3D9-ADDITIVE-001', scene='Fresh ordinary-D3D9/Remix textured ship at fixed world offset;exact-current-frame GPU return;original drawing ON', output_resources_bytes=82944000, image_limit_bytes=128 * 1024 * 1024, display_policy='Exact source identity/frame only;no stale hold;resize hides until fresh session')
        if self.args.persistent_scene:
            self.metadata['persistent_scene'] = dict(protocol=2, registry_owners=OWNERS, pose_source='SHIP_SIMULATION_FIELDS', renderer='Existing ordinary D3D9 retained assets', initial_display='Configured player fixture', visibility_does_not_retire=True)
        if self.args.synchronized_buffer:
            self.metadata['synchronized_buffer'] = dict(frames=1, max_age_ms=50, complete_native_HUD_delayed=True, prediction=False, stale_overlay_hold=False)
            self.metadata.update(output_resources_bytes=1920 * 1080 * 4 * 14, display_policy='One adjacent complete game frame with matching output/depth;50ms bound;no stale overlay on a newer scene')
        if self.args.lifecycle_capture:
            from lifecycle_capture import PHASES, RECOVERY_PHASES
            self.PHASES = PHASES
            self.RECOVERY_PHASES = RECOVERY_PHASES
            if self.args.camera_recovery:
                self.PHASES = self.RECOVERY_PHASES
            if self.args.persistent_scene:
                from offscreen_position import PHASES
                self.PHASES = PHASES
            if self.args.synchronized_buffer:
                self.PHASES = ()
            if self.args.offscreen_position:
                from offscreen_position import PHASES
                self.PHASES = PHASES
                self.metadata['offscreen_position'] = dict(probe='OFFSCREEN-POSITION-001', owners=2, hz_max=20, seconds_max=120, records_per_ship=2700, bytes_max=8 * 1024 * 1024, external_read_only=True, renderer_input=False, lifetime_proven=False)
            self.metadata['lifecycle_capture'] = dict(probe='D3D9-LIFECYCLE-001', detail_hz_max=20, detail_records_per_slot=2700, detail_bytes=16 * 1024 * 1024, event_queue_records=256, event_bytes=1024 * 1024, phases=self.PHASES, native_death_signal_qualified=False)
            self.metadata['lifecycle_capture']['mode'] = 'camera_return_alive' if self.args.camera_recovery else 'camera_gap_then_destruction'
            if self.args.synchronized_buffer:
                self.metadata['lifecycle_capture']['mode'] = 'freeform_buffered_comparison_alive'
        if self.args.broad_capture:
            self.metadata['scene'] = 'No Remix renderer; full-support read-only resource/binding/draw metadata'
        if self.args.depth_snapshots:
            self.metadata['scene'] = 'No Remix renderer; three paired read-only depth/color snapshots; no original draws suppressed'
        (self.work / 'manifest.json').write_text(json.dumps(self.metadata, indent=2))
        self.host = self.launcher = self.controller = self.channel = None
        self.receiver = None
        self.streams = []
        self.pid = None
        self.error = None
        self.normal = False
        self.gate_clean = False
        self.history = []
        self.phase_results = {}
        self.last = 0
        self.host_shutdown_expected = False
        self.proxy_restored = None
        self.image_reader = None
        self.image_result = None
        self.light_relay = None
        self.tuning_exited = False
        self.timing_relay = None
        self.live_timing_result = None
        self.offscreen = None
        self.insertion_capture = None
        self.insertion_result = None
        self.native_capture = None
        self.native_result = None
        self.exit_monitor = None
        self.user_exited = False
        self.capture_complete = False
        self.controller_retired = False
        self.session_stage = 'startup'
        self.rollback = self.work / 'dxgi-original.rollback'
        self.config_backup = self.work / 'ReShade.original.ini'
        self.last_output_check = 0

    def enforce(self):
        if self.exit_monitor:
            self.exit_monitor.check()
        if self.insertion_capture and self.insertion_capture.error:
            raise RuntimeError('Native insertion observation: ' + self.insertion_capture.error)
        if self.offscreen and self.offscreen.error:
            raise RuntimeError('Offscreen position reader: ' + self.offscreen.error)
        if self.timing_relay and self.timing_relay.servicing:
            self.timing_relay.check_service()
        elif self.receiver:
            self.receiver.drain()
        if self.timing_relay and self.pid:
            self.timing_relay.poll(self.pid)
        if self.light_relay:
            self.light_relay.poll()
        if self.args.multi_ship and self.args.pipeline_mode == 'performance':
            self.now = time.monotonic()
            if self.now > self.deadline:
                raise RuntimeError('Prepared workflow time limit')
            if self.now - self.last_output_check < (5 if self.args.play_session else 1):
                return
            self.last_output_check = self.now
        if self.args.play_session:
            if CONTEXT.release:
                return
            self.logs = sum((capture_file_bytes(p) for p in self.work.rglob('*') if p.suffix.lower() in ('.log', '.csv', '.jsonl')))
            if self.logs > 32 * 1024 * 1024:
                raise RuntimeError('Play-session logs exceed32MiB')
            return
        self.size = sum((p.stat().st_size for p in self.work.rglob('*') if p.is_file()))
        self.other = sum((p.stat().st_size for p in self.work.rglob('*') if p.is_file() and p.name != 'broad.bin'))
        if self.args.d3d9_additive:
            self.images = sum((p.stat().st_size for p in (self.work / 'gpu').rglob('*') if p.is_file() and (p.suffix.lower() == '.dds' or re.fullmatch('(?:texture-\\d+|damage-texture-\\d+)\\.bin', p.name))))
            if not self.args.multi_ship and self.images > 128 * 1024 * 1024:
                raise RuntimeError('Additive image128MiB cap;original rendering retained')
            self.size -= self.images
            self.other -= self.images
        if self.args.textured_ship:
            self.textures = sum((p.stat().st_size for p in (self.work / 'textures').glob('*') if p.is_file()))
            if self.textures > 128 * 1024 * 1024:
                raise RuntimeError('Original/derived image128MiB cap')
            if self.textures > 64 * 1024 * 1024 and (not self.phase_results.get('texture_warned')):
                print('Image output64MiB warning;128MiB cap remains.', flush=True)
                self.phase_results['texture_warned'] = True
            self.size -= self.textures
            self.other -= self.textures
        if self.full_support and (TEST / 'ReShade.log').exists():
            self.other += (TEST / 'ReShade.log').stat().st_size
        self.image_bytes = sum((p.stat().st_size for p in self.work.glob('depth-*.bin')))
        if self.args.depth_snapshots:
            self.other -= self.image_bytes
        if self.args.source_timing:
            self.size += 2621568
            self.other += 2621568
        if self.args.live_owner_timing:
            self.size += 1154688
            self.other += 1154688
        if self.args.broad_capture and (self.work / 'broad.bin').exists() and ((self.work / 'broad.bin').stat().st_size >= 1000000000) and (not self.phase_results.get('broad_warned')):
            print('Broad trace warning1GB; strict2GB writer cap remains active.', flush=True)
            self.phase_results['broad_warned'] = True
        if self.args.depth_snapshots and self.image_bytes > 64 * 1024 * 1024:
            raise RuntimeError('Depth image64MiB cap; original rendering retained')
        if self.args.depth_snapshots and self.image_bytes > 32 * 1024 * 1024 and (not self.phase_results.get('image_warned')):
            print('Depth images exceed32MiB warning; three-pair64MiB cap remains.', flush=True)
            self.phase_results['image_warned'] = True
        if time.monotonic() > self.deadline or self.other > 32 * 1024 * 1024 or self.size > (broad_capture.HARD + 32 * 1024 * 1024 if self.args.broad_capture else 96 * 1024 * 1024 if self.args.depth_snapshots else 32 * 1024 * 1024):
            raise RuntimeError('Prepared workflow time/output cap; original rendering retained')
        if self.other > 16 * 1024 * 1024 and (not self.phase_results.get('warned')):
            print('Evidence warning16MiB; still bounded.', flush=True)
            self.phase_results['warned'] = True

    def _start_host(self):
        self.host_env = {**os.environ, **ENV, 'DXVK_LOG_PATH': str(self.work)}
        self.host_env.update(SFC_PLAY_SESSION='1' if self.args.play_session else '0', SFC_PLAY_PARENT_PID=str(os.getpid()) if self.args.play_session else '0')
        if self.args.private_ship:
            from live_return import FreshReceiver
            self.FreshReceiver = FreshReceiver
            self.receiver = self.FreshReceiver(self.work, textured=self.args.textured_ship)
            self.host_env['SFC_REMIX_CALIBRATION_SCENE'] = self.receiver.name
        self.host_env.pop('SFC_REMIX_TEXTURED_SHIP', None)
        self.host_env.pop('SFC_REMIX_LIGHT_WIRING', None)
        self.host_env.pop('SFC_LIGHT_TUNING', None)
        if self.args.light_tuning:
            self.host_env['SFC_LIGHT_TUNING'] = '1'
        if self.args.light_wiring:
            from live_lights import Relay
            self.Relay = Relay
            self.light_relay = self.Relay(self.work, self.receiver, tuning=self.args.light_tuning)
            self.host_env['SFC_REMIX_LIGHT_WIRING'] = '1'
        if self.args.textured_ship:
            self.host_env['SFC_REMIX_TEXTURED_SHIP'] = '1'
        self.host = sp.Popen([str(self.host_exe), '--observe-only' if self.args.observation_only else str(DLL)], cwd=self.work, env=self.host_env, stdout=self.out('host.log'), stderr=sp.STDOUT, creationflags=sp.CREATE_NO_WINDOW)

    def _prepare_game(self):
        self.env = {**os.environ, 'SFC_REMIX_RETURN_SESSION': self.session, 'SFC_REMIX_EXPECTED_IMAGE': str(TEST / 'StarFleetOP.exe'), 'SFC_REMIX_PRELOAD_REQUIRED': '1'}
        self.env['SFC_PLAY_SESSION'] = '1' if self.args.play_session else '0'
        self.env['SFC_REMIX_INSPECT_VISIBILITY'] = '3' if self.args.search_depth else '2' if self.args.inspect_early_depth else '1' if self.args.inspect_visibility else '0'
        self.env.pop('SFC_REMIX_BROAD_OUTPUT', None)
        self.env.pop('SFC_REMIX_DEPTH_OUTPUT', None)
        self.env.pop('SFC_REMIX_CALIBRATION_SCENE', None)
        self.env.pop('SFC_REMIX_CAPTURE_SHIP_IMAGE', None)
        self.env.pop('SFC_REMIX_CAPTURE_SHIP_IMAGE_DELAY_MS', None)
        self.env.pop('SFC_NATIVE_LIGHT_DISCOVERY', None)
        self.env.pop('SFC_LIGHT_TUNING', None)
        self.env.pop('SFC_D3D9_SOURCE_TIMING', None)
        self.env.pop('SFC_D3D9_LIVE_TIMING', None)
        if self.args.source_timing:
            self.env['SFC_D3D9_SOURCE_TIMING'] = '1'
        if self.args.live_owner_timing:
            self.env['SFC_D3D9_LIVE_TIMING'] = '1'
        self.env.pop('SFC_D3D9_GAME_OUTPUT', None)
        self.env.pop('SFC_LIFECYCLE_CAPTURE', None)
        if self.args.lifecycle_capture:
            self.env['SFC_LIFECYCLE_CAPTURE'] = '1'
        if self.args.d3d9_additive:
            self.env.update(SFC_D3D9_GAME_OUTPUT='1', SFC_LIGHT_TUNING='1')
        self.env.pop('SFC_D3D9_SHARED_LIGHTS', None)
        self.env.pop('SFC_PERSISTENT_SCENE', None)
        self.env.pop('SFC_D3D9_SYNC_BUFFER', None)
        self.env.pop('SFC_D3D9_MULTISCENE', None)
        if self.args.multi_ship:
            self.env['SFC_D3D9_MULTISCENE'] = '1'
        self.env['SFC_D3D9_PLAYER_REPLACEMENT'] = '1' if self.args.player_replacement or self.args.native_all_ships else '0'
        self.env['SFC_NATIVE_INSERTION_ALL_SHIPS'] = '1' if self.args.native_all_ships else '0'
        self.env['SFC_DAMAGE_TEXTURES'] = '1' if self.args.damage_textures else '0'
        self.env['SFC_BREAK_SCENE'] = '1' if self.args.break_models else '0'
        self.env['SFC_D3D9_NATIVE_FOREGROUND'] = '1' if self.args.native_foreground else '0'
        self.env['SFC_NATIVE_INSERTION_OBSERVE'] = '1' if self.args.native_insertion_observe else '0'
        self.env['SFC_NATIVE_INSERTION_GATE'] = '1' if self.args.native_insertion_policy else '0'
        if CONTEXT.release:
            from portable_reshade import prepare as prepare_portable_reshade
            self.prepare_portable_reshade = prepare_portable_reshade
            self.env.update(self.prepare_portable_reshade(CONTEXT, self.work))
        self.env.pop('SFC_NATIVE_GATE_BASELINE', None)
        self.env.pop('SFC_NATIVE_GATE_FIXTURE_DELAYS', None)
        if self.args.native_insertion_policy:
            self.env['SFC_NATIVE_INSERTION_POLICY'] = self.args.native_insertion_policy
        self.env.pop('SFC_REPLACEMENT_FIXTURE_FAULTS', None)
        self.env['SFC_PIPELINE_MODE'] = self.args.pipeline_mode if self.args.multi_ship else 'test'
        if self.args.synchronized_buffer:
            self.env['SFC_D3D9_SYNC_BUFFER'] = '1'
        if self.args.persistent_scene:
            self.env['SFC_PERSISTENT_SCENE'] = '1'
        if self.args.d3d9_additive:
            self.env['SFC_D3D9_SHARED_LIGHTS'] = '1'
        if self.args.light_tuning:
            self.env['SFC_LIGHT_TUNING'] = '1'
        if self.args.capture_native_lights:
            self.env['SFC_NATIVE_LIGHT_DISCOVERY'] = '1'
        if self.args.capture_ship_image:
            self.env.update(SFC_REMIX_CAPTURE_SHIP_IMAGE='1', SFC_REMIX_CAPTURE_SHIP_IMAGE_DELAY_MS='15000')
        if self.semantic_enabled:
            from present_calibration import Receiver
            self.Receiver = Receiver
            if self.receiver is None:
                self.receiver = self.Receiver(break_models=self.args.break_models)
            if self.args.native_insertion_policy and (not self.args.play_session):
                from native_gate import Capture
                self.Capture = Capture
                self.native_capture = self.Capture(self.receiver.channel, self.work, session=[int(self.receiver.name[-32:][i:i + 8], 16) for i in range(0, 32, 8)])
            if self.args.native_insertion_observe:
                from native_insertion_probe import Capture
                self.Capture = Capture
                self.insertion_capture = self.Capture(self.receiver.channel, self.work, session=[int(self.receiver.name[-32:][i:i + 8], 16) for i in range(0, 32, 8)])
            if self.args.live_owner_timing:
                if self.args.async_material_checkout:
                    from async_material_checkout import Relay
                    self.Relay = Relay
                elif self.args.experimental_parallel_assets:
                    from progressive_scene_relay import Relay
                    self.Relay = Relay
                elif self.args.multi_ship:
                    from multi_scene_relay import Relay
                    self.Relay = Relay
                else:
                    from live_owner_timing import Relay
                    self.Relay = Relay
                self.mode_args = {'pipeline_mode': self.args.pipeline_mode} if self.args.multi_ship else {}
                if self.args.player_replacement:
                    self.mode_args['player_replacement'] = True
                if self.args.experimental_parallel_assets:
                    self.mode_args['experimental_live_checkout'] = True
                if self.args.async_material_checkout:
                    self.mode_args['checkout_backend'] = self.checkout_backend
                self.timing_relay = self.Relay(self.work, self.receiver, TEST, additive=self.args.d3d9_additive, persistent=self.args.persistent_scene, buffered=self.args.synchronized_buffer, **self.mode_args)
                self.timing_relay.light_diagnostics = self.args.light_diagnostics
                self.timing_relay.damage_textures = self.args.damage_textures
                self.timing_relay.completion_diagnostics = self.args.completion_diagnostics
                self.timing_relay.play_session = self.args.play_session
                self.timing_relay.live_tuning = self.d3d9_tuning
                if self.args.native_insertion_policy:
                    self.timing_relay.native_gate_policy = self.args.native_insertion_policy
                self.timing_relay.native_all_ships = self.args.native_all_ships
                self.timing_relay.break_models = self.args.break_models
                self.timing_relay.legacy_startup_warmup = self.args.legacy_startup_warmup
            self.env['SFC_REMIX_CALIBRATION_SCENE'] = self.receiver.name
            self.env.pop('SFC_REMIX_VISIBLE_SHIP', None)
            self.env.pop('SFC_REMIX_TEXTURED_SHIP', None)
            if self.args.private_ship:
                self.env['SFC_REMIX_PRIVATE_SHIP'] = '1'
            if self.args.visible_ship:
                self.env['SFC_REMIX_VISIBLE_SHIP'] = '1'
            if self.args.textured_ship:
                self.env['SFC_REMIX_TEXTURED_SHIP'] = '1'
            self.component_path = CONTEXT.artifact('remix-runtime/native-light-tests/m1_light_component.dll' if self.args.capture_native_lights else 'm1/bin/m1_component.dll')
            self.metadata['semantic_calibration'] = {'probe': 'REMIX-CALIBRATION-001', 'scene_session': self.receiver.name, 'maximum_asset_revisions': ASSETS if self.args.multi_ship else 8, 'geometry_hook': False, 'same_process_render_thread_required': True, 'component_sha256': digest(self.component_path)}
            if self.args.multi_ship:
                from multi_scene_resources import policy
                self.policy = policy
                self.metadata.update(probe='D3D9-MULTISHIP-001', scene='Fresh retained multi-model diagnostic;placement recorded in live-owner analysis', original_suppressed=False, tracked_set_capacity=OWNERS, asset_revisions=ASSETS, image_limit_bytes=broad_capture.OVERALL, image_policy=self.policy())
                if self.args.player_replacement:
                    self.metadata.update(probe='PLAYER-REPLACEMENT-001', scene='Capture-first player-fixture suppression;transactional whole-frame presentation', replacement_requested=True, original_suppressed='See final native receipts', fallback='Two additional complete-picture presentations,then latched native rendering')
                if self.args.native_insertion_observe:
                    self.metadata.update(probe='NATIVE-INSERTION-001', scene='Read-only native draw order and private output readiness;no visible returned image', replacement_requested=False, original_suppressed=False, shield_replay=False, detail_bytes=8 * 1024 * 1024)
                if self.args.native_insertion_policy:
                    self.metadata.update(probe='NATIVE-GATE-001', scene='Exact-ticket native colour/depth insertion before subsequent engine effects/text', timing_policy=self.args.native_insertion_policy, reference_hz=60, shield_replay=False, late_composition=False, fallback='Original selected lists remain intact for an uncommitted owner/frame', detail_bytes=8 * 1024 * 1024, display_policy='Current native source frame;absolute deadline;commit colour/depth before zero-count suppression', synchronized_buffer=dict(frames=0, complete_native_HUD_delayed=False, prediction=False, stale_overlay_hold=False, coordinator='Absolute source-frame deadline;immutable completed-output lease'))
                if self.args.native_all_ships:
                    self.metadata.update(probe='NATIVE-COHORT-001', scope='Supported retained ships;per-owner native suppression and physical owner coverage;one shared frame lease', native_all_ships=True, break_models=self.args.break_models)
            (self.work / 'manifest.json').write_text(json.dumps(self.metadata, indent=2))
        if self.args.depth_snapshots:
            self.env['SFC_REMIX_DEPTH_OUTPUT'] = str(self.work)
        self.env.pop('SFC_REMIX_SCENE_DEPTH', None)
        if self.args.scene_depth:
            self.env['SFC_REMIX_SCENE_DEPTH'] = '1'
        if self.args.broad_capture:
            self.env['SFC_REMIX_BROAD_OUTPUT'] = str(self.work / 'broad.bin')

    def _after_launch(self):
        if self.args.multi_ship:
            self.timing_relay.start_on_launch(self.pid)
        if self.args.private_ship:
            self.receiver.context(self.session, self.pid)

    def _instructions(self):
        print('Start your campaign or skirmish when ready. No session or battle-selection timer.' if self.args.play_session else 'Enter the usual two-ship skirmish. Ships should look normal.', flush=True)
        if self.args.break_models:
            print('DEBRIS CHECK:use an F-CA with a surviving wingman. Destroy one enhanced ship in view;watch its pieces,briefly switch cameras and return. Native debris remains until matching replacement output is ready. Exit normally at the usual cue.', flush=True)
        if self.args.private_ship and (not self.args.light_tuning):
            print('At the first beep,hold your ship and camera still. A later single beep means a small camera change;three beeps mean gently move/turn your ship. Two beeps mean exit normally.', flush=True)
        if self.inspect_requested:
            print('Read-only visibility check: keep both ships visible briefly. No ship will be replaced.', flush=True)
        if self.args.broad_capture:
            print('Broad recording: keep both ships in view briefly and play normally. About10seconds after tactical entry, two beeps request normal exit. No visual change expected.', flush=True)
        if self.args.depth_snapshots:
            print('Keep both ships visible. At first beep hold camera still; at the next single beep make one small camera rotation, then hold still. Two beeps mean exit normally. No visual change expected.', flush=True)
        if self.args.textured_ship and (not self.args.light_tuning):
            print('Look for a TEXTURED ship copy beside an original,not magenta. It stays ON throughout this observation;stop only at the two-beep exit request. Small bounded delay,not frame-exact replacement.', flush=True)
        if self.args.capture_native_lights and (not self.args.light_tuning) and (not self.args.scene_depth) and (not self.args.d3d9_additive):
            print('Light discovery:play normally,move the camera and ship briefly,and fire when convenient. We record the game lights without changing them. Exit only at the two-beep request.', flush=True)
        if self.args.scene_depth:
            print('Depth test: originals remain ON. The extra textured ship is visible only when pose/camera match;it may disappear while moving. Hold still between small camera changes. Grid behavior is being observed,not changed by a guessed rule.', flush=True)
        if self.args.light_wiring and (not self.args.light_tuning):
            print('LIGHT WIRING:extra ship uses two observed native directional lights with ratio controls. Native game unchanged. Normal90s test,not extended tuning;exit at two-beep cue.', flush=True)
        if self.args.play_session:
            print('UNTIMED MULTI-SHIP REPLACEMENT:current appearance,weapon lights and damage enabled. Leave and enter battles normally;exit SFC when finished.', flush=True)
        elif self.args.native_insertion_observe:
            print('NATIVE DRAW ORDER CHECK:use your usual F-CA and a different enemy. The game picture stays original;no extra ship. Play normally,rotate camera,fire weapons and briefly pause/unpause. Wait for the exit request.', flush=True)
        elif self.args.native_all_ships:
            print('MULTI-SHIP REPLACEMENT:use different ship models. Supported ships should be replaced at their normal positions. Start still,then rotate/move/turn,switch cameras and expose shields. Originals remain until each replacement is ready. Exit normally at the two low beeps.', flush=True)
        elif self.args.player_replacement:
            print('PLAYER REPLACEMENT: use your usual F-CA and a different enemy model. Expect one player ship at its original position,not an extra copy. Original drawing stays during preparation. Start still,then rotate camera,move/turn and switch away/back. Exit normally when requested.', flush=True)
        elif self.args.capture_ship_image:
            print('One prepared-image snapshot will be saved automatically. Focus the extra ship and hold the camera briefly once it appears;no manual screenshot or timestamp needed.', flush=True)
        elif self.args.d3d9_additive:
            print('Live D3D9 tuning: textured copies use your current settings. Save rendering.toml or lights.toml to update them. Exit SFC normally when finished.' if self.d3d9_tuning else 'Look for a fully textured extra ship beside one original. Original ships stay visible. Your existing light/material/image settings are frozen for this short test;no magenta or on/off cycle.', flush=True)
        elif not self.args.textured_ship:
            print('Look for a MAGENTA ship copy BESIDE the selected original ship,usually to its left at the starting view;it may flash. This is NOT a corner window. Original ships stay normal.' if self.args.visible_ship else 'No visible change expected;fresh ship output is tested privately,originals stay normal.' if self.args.private_ship else 'No triangle or ship changes expected; this is a read-only check.' if self.args.observation_only else 'A small green animated triangle will appear in a black square at upper right. It turns off/on/off automatically.', flush=True)
        if not self.args.play_session:
            print('Exit SFC normally whenever finished. An early exit immediately starts cleanup and saves a shortened run;the two-beep cue marks the planned full test.', flush=True)

    def _configure_controller(self):
        self.controller_exe = CONTEXT.artifact('m1/bin/m1_controller.exe')
        self.gate = CONTEXT.artifact('m1/bin/m1_gate.dll')
        self.gate_dir = self.work / 'gate'
        self.gate_dir.mkdir()
        self.config = self.gate_dir / 'component.ini'
        write_native_config(self.config, '[m1]\nOutputDirectory=' + str(self.gate_dir) + '\nControllerPath=' + str(self.controller_exe) + '\nMaxSeconds=90\nStopOnBurst=1\nMaxFrames=1\nMaxEvents=1\nMaxOwners=1\nWarningBytes=16777216\nHardBytes=33554432\n')
        if self.semantic_enabled:
            self.gate = CONTEXT.artifact('m1/bin/m1_component.dll')
            if self.args.capture_native_lights:
                self.gate = CONTEXT.artifact('remix-runtime/native-light-tests/m1_light_component.dll')
                self.metadata['native_lights'] = {'probe': 'NATIVE-LIGHTS-001', 'qualification': self.light_qualification, 'hypothesis': 'three lights and/or global illumination;UNCONFIRMED'}
                (self.work / 'manifest.json').write_text(json.dumps(self.metadata, indent=2))
            write_native_config(self.config, '[m1]\nOutputDirectory=' + str(self.gate_dir) + '\nControllerPath=' + str(self.controller_exe) + '\nMaxSeconds=' + ('0' if self.args.play_session else '1800' if self.args.light_tuning else '120' if self.args.d3d9_additive else '90' if self.args.private_ship or self.args.source_timing else '24') + '\nStopOnBurst=0\nMaxFrames=120\nMaxEvents=10000\nMaxOwners=' + str(OWNERS) + '\nWarningBytes=16777216\nHardBytes=33554432' + '\nEnableGeometryHook=0\nEnableWrapperObservation=1\nEnableMeshExport=1\nEnableTextureReferences=1\nEnablePrivateCopy=0\nLiveChannel=' + self.receiver.name + '\n')
        self.controller_args = [str(self.controller_exe), '--pid', str(self.pid), '--dll', str(self.gate), '--config', str(self.config), '--max-seconds', '24' if self.args.calibration else '90', '--stop-on-burst', '0' if self.semantic_enabled else '1', '--already-loaded', '0', '--unload-after-stop', '1']
        if self.args.light_tuning:
            self.controller_args[self.controller_args.index('--max-seconds') + 1] = '1800'
        if self.args.d3d9_additive and (not self.d3d9_tuning):
            self.controller_args[self.controller_args.index('--max-seconds') + 1] = '120'
        if self.args.play_session:
            self.controller_args[self.controller_args.index('--max-seconds') + 1] = '0'
        self.gate_timeout = tactical_gate_timeout(self.args.multi_ship)
        if self.semantic_enabled:
            self.controller_args += ['--gate-timeout-seconds', str(0 if self.args.play_session else self.gate_timeout)]
            self.metadata['gate_timeout_seconds'] = None if self.args.play_session else self.gate_timeout
            (self.work / 'manifest.json').write_text(json.dumps(self.metadata, indent=2))
            print('UNTIMED PLAY:enter battles when ready;exit SFC normally when finished. No recording deadline or timed cues.' if self.args.play_session else f'Enter the skirmish within {self.gate_timeout} seconds. The90second recording starts automatically in the tactical scene,not during ship selection.', flush=True)

    def _start_controller(self):
        self._launch_controller()
        if self.semantic_enabled:
            wait_live_gate(self.pid,self.controller,self.enforce,timeout=None if self.untimed else self.gate_timeout)
            self.controller_gate_observed=time.monotonic();self.session_stage='tactical'
            self._after_tactical_gate()
        else:
            while self.controller.poll() is None:self.enforce();time.sleep(.1)
            self.gate_text=(self.work/'gate-controller.log').read_text(errors='replace')
            self.summary=json.loads((self.gate_dir/'M1-A-summary.json').read_text(encoding='utf-8-sig')) if (self.gate_dir/'M1-A-summary.json').exists() else {}
            self.gate_clean=self.controller.returncode==0 and self.summary.get('gate_activated') is True and all(
                marker in self.gate_text for marker in ('component_state=removed','hook_bytes_restored=true','component_unloaded=true'))
            if not self.gate_clean:raise RuntimeError('Tactical gate did not complete/restored/unload cleanly; image left disabled')

    def _stop_extensions(self):
        if self.offscreen:
            try:self.offscreen.close()
            except Exception as exc:
                self.error=(self.error+'; ' if self.error else '')+'Offscreen reader shutdown: '+str(exc)
        if self.image_reader and self.image_reader.poll() is None:
            try:
                self.image_reader.wait(timeout=5)
            except sp.TimeoutExpired:
                self.image_reader.terminate()
                self.image_reader.wait(timeout=5)

    def _after_tactical_gate(self):
        if self.args.offscreen_position:
            from offscreen_position import Capture
            self.offscreen=Capture(self.work,self.pid,TEST/'StarFleetOP.exe')

    def _check_observers(self):
        if self.args.search_depth:
            self.search = self.depth_search_channel.snapshot(self.channel.address)
            if self.search['status'] != 2 or self.search['installedMask'] != 15 or self.search['error']:
                raise RuntimeError('Expanded engine search installation not qualified')
        self.state = self.channel.snapshot()
        if self.args.broad_capture:
            self.broad = broad_capture.header_at(self.channel.address)
            if self.broad['status'] != 2 or self.broad['error']:
                raise RuntimeError('Broad writer not active at tactical gate; prelude may have saturated; preserve partial evidence')

    def _begin_observation(self):
        if self.args.d3d9_additive and (not (self.args.native_insertion_observe or self.args.native_insertion_policy)):
            print('Preparing current D3D9 tuning;edit settings after the copies appear. No timed motion instructions.' if self.d3d9_tuning else 'Preparing the extra textured ship;original game stays normal. Keep both ships visible and alive. Timed instructions start when the first matching ship image is ready.', flush=True)
            self.preparing = self.active
            while time.monotonic() - self.preparing < 30:
                self.enforce()
                if self.channel.snapshot()['drawCount'] > 0:
                    break
                if self.launcher.poll() is not None:
                    raise RuntimeError('Game exited during additive preparation')
                time.sleep(0.05)
            else:
                raise RuntimeError('No qualified offset image within30s preparation;preserve evidence')
            self.metadata.update(additive_preparation_seconds=time.monotonic() - self.preparing, formal_capture_seconds=1800 if self.d3d9_tuning else 90, semantic_watchdog_seconds=1800 if self.d3d9_tuning else 120)
            (self.work / 'manifest.json').write_text(json.dumps(self.metadata, indent=2))
            self.active = time.monotonic()
        if self.args.capture_ship_image:
            self.image_reader = sp.Popen([str(self.live_bin / 'ship_image_reader.exe'), self.session, str(self.work)], cwd=self.work, stdout=self.out('ship-image-reader.log'), stderr=sp.STDOUT, creationflags=sp.CREATE_NO_WINDOW)
        self.camera_cued = False
        self.motion_cued = False
        self.source_cues = set()
        if self.args.play_session:
            print('UNTIMED PLAY:replacement and damage stay enabled across menus/battles. Exit SFC normally to clean up. No timed exit cue.', flush=True)
        elif self.args.light_tuning:
            pass
        elif self.args.native_insertion_observe:
            print('READ-ONLY CHECK:play normally;include camera changes,weapon fire and a brief pause/unpause. Wait for TWO LOW beeps before exiting so hooks can be removed first.', flush=True)
        elif self.args.player_replacement:
            print('PLAYER REPLACEMENT:one player ship at the normal position. Briefly hold still,then move/turn,rotate camera and switch away/back. No timed movement cues. Two low beeps=request normal exit.', flush=True)
        elif self.args.native_all_ships:
            print('NATIVE MULTI-SHIP REPLACEMENT:look for normal-position ships,not extra copies. Briefly keep different ships visible,rotate/move/turn,switch cameras and expose shields. Brief pause/unpause is fine. TWO LOW beeps=exit normally after restoration.', flush=True)
        elif self.args.multi_ship:
            print('MULTI-SHIP OFFSET TEST:use different ship models. Returned copies sit to CAMERA LEFT of the originals at the previous test distance. Original ships stay visible. Keep both alive and briefly visible together,then move/turn and switch cameras normally. Watch the copies for flicker,missing/wrong models or placement problems. TWO LOW beeps=exit normally after restoration.', flush=True)
        elif self.args.synchronized_buffer:
            print('BUFFERED SHIP TEST:one complete game frame and matching extra ship are displayed together. Play normally and swap cameras freely;keep both ships alive. Check return flicker and whether controls/HUD feel normal. No movement cues;TWO LOW beeps=exit normally after restoration.', flush=True)
        elif self.args.persistent_scene:
            print('PERSISTENT SHIP TEST:keep both ships alive. At the timed single cue accelerate your ship and leave it moving. TWO HIGH=enemy camera;THREE HIGH=return to your ship. The extra ship should follow current motion without reloading. Follow the gentle-turn cue for the second pass. TWO LOW=exit only after restoration.', flush=True)
        elif self.args.offscreen_position:
            print('OFFSCREEN POSITION TEST:keep both ships alive. At the first single cue accelerate your ship and LEAVE IT MOVING. TWO HIGH=look at the enemy,leaving your own ship out of view. THREE HIGH=return to your ship. Follow the turn/setup cue for the second pass. TWO LOW=exit only after restoration. No new visual effect is expected.', flush=True)
        elif self.args.camera_recovery:
            print('CAMERA RETURN TEST:keep both ships alive;do NOT destroy your ship. ONE beep=hold;TWO HIGH=enemy camera;THREE HIGH=return to own ship. This repeats twice. The extra ship should return beside your own. TWO LOW=exit normally;restoration may take a short wait after recording.', flush=True)
        elif self.args.lifecycle_capture:
            print('LIFECYCLE TEST:First15seconds settle the view. ONE beep=hold alive;TWO HIGH=enemy camera;THREE HIGH=return to own ship;FOUR HIGH=destroy OWN ship. Stay in mission after destruction. TWO LOW=exit normally.', flush=True)
        elif self.args.source_timing:
            print(('OFFSET SHIP TEST:extra textured ship,original stays visible. Keep both ships alive. ' if self.args.d3d9_additive else 'TIMING CHECK:no visual change. ') + 'Do not pause;keep both ships visible. First15seconds:find a comfortable view. LOW single beep=hold. TWO HIGH beeps=small camera moves. THREE HIGH=accelerate/turn your ship. TWO LOW=exit normally.', flush=True)
        if self.args.light_tuning:
            print('TUNING:edit tools/remix_runtime/config/rendering.toml (materials,image,quality,bloom) or lights.toml and SAVE. Image adjustments need enabled=true. Changes apply live. Exit SFC normally when finished;30minute safety ceiling. No timed motion instructions.', flush=True)
        self.tuning_exited = False

    def _observe(self):
        while self.args.play_session or time.monotonic() - self.active < (1800 if self.args.light_tuning else 10.1 if self.args.broad_capture else 20 if self.args.depth_snapshots else 90):
            self.enforce()
            self.elapsed = time.monotonic() - self.active
            self.state = self.channel.snapshot()
            if self.args.source_timing and (not self.args.multi_ship):
                self.cues = self.PHASES if self.args.lifecycle_capture else ((15, 1, 'Hold your ship and camera still for10seconds.'), (25, 1, 'Prepare a freely movable camera;keep both ships visible.'), (35, 2, 'Make small camera movements for15seconds.'), (50, 1, 'Hold the camera still;prepare to move your ship.'), (60, 3, 'Accelerate and gently turn your ship for20seconds;keep both ships visible.'), (80, 1, 'Hold a steady view until the exit request.'))
                for second, count, message in self.cues:
                    if self.elapsed >= second and second not in self.source_cues:
                        self.source_cues.add(second)
                        for self._ in range(count):
                            winsound.Beep(1100 if count > 1 else 880, 150)
                        print(message, flush=True)
                        if self.args.lifecycle_capture:
                            self.phase_results.setdefault('lifecycle_cues', []).append(dict(requested_second=second, issued_second=self.elapsed, message=message))
            if self.args.depth_snapshots and self.elapsed >= 5 and (not self.camera_cued):
                winsound.Beep(1000, 200)
                print('Small camera rotation now, then hold still; keep both ships visible.', flush=True)
                self.camera_cued = True
            if self.args.private_ship and (not self.args.light_tuning) and (not self.args.capture_ship_image) and (self.elapsed >= 10) and (not self.camera_cued):
                winsound.Beep(1000, 200)
                print('Make one small camera change now,then hold it.', flush=True)
                self.camera_cued = True
            if self.args.private_ship and (not self.args.light_tuning) and (not self.args.capture_ship_image) and (self.elapsed >= 20) and (not self.motion_cued):
                for self._ in range(3):
                    winsound.Beep(1100, 150)
                print('Gently accelerate and turn your ship;keep playing until the two-beep exit cue.', flush=True)
                self.motion_cued = True
            self.next_phase = observation_phase(self.elapsed, continuous=self.args.textured_ship or self.args.source_timing)
            if self.phase != self.next_phase:
                self.phase = self.next_phase
                self.phase_results[str(self.phase)] = {'seconds': self.elapsed, 'start': self.state}
                self.channel.set('enabled', int(self.args.d3d9_additive or (not self.args.observation_only and self.phase in (0, 2))))
                if not self.args.play_session:
                    print('Supported-ship replacement remains enabled;keep playing until the exit request.' if self.args.native_all_ships else 'Read-only draw-order check;keep playing until the exit request.' if self.args.native_insertion_observe else 'Player replacement remains enabled;keep playing until the exit request.' if self.args.player_replacement else 'Offset ship remains enabled;keep playing until the exit request.' if self.args.d3d9_additive else ('Private receiver ON', 'Private receiver OFF', 'Private receiver ON again', 'Private renderer disconnect;original game unchanged')[self.phase] if self.args.private_ship else 'Read-only check; keep playing normally.' if self.args.observation_only else ('Image ON', 'Image OFF; keep playing', 'Image ON again', 'Renderer disconnect; image OFF; keep playing')[self.phase], flush=True)
                if self.phase == 3 and (not self.args.search_depth):
                    self.channel.set('stop', 1)
                    self.host_shutdown_expected = True
            if self.state['error']:
                raise RuntimeError('Image component reported an error; original rendering retained')
            self.exit_monitor.check()
            if self.host.poll() is not None and (not self.host_shutdown_expected):
                raise RuntimeError('Renderer exited unexpectedly; original rendering retained')
            if self.elapsed - self.last > (5 if self.args.light_tuning or (self.args.multi_ship and self.args.pipeline_mode == 'performance') else 0.25):
                self.item = {'seconds': self.elapsed, 'phase': self.phase, **self.state}
                if self.args.player_replacement:
                    from player_replacement import summary as replacement_summary
                    self.replacement_summary = replacement_summary
                    self.item['replacement'] = self.replacement_summary(self.receiver.channel)
                if self.args.private_ship:
                    from live_return import telemetry
                    self.telemetry = telemetry
                    self.item['private_return'] = self.telemetry(self.channel.address)
                    if self.args.scene_depth:
                        from live_return import depth_telemetry
                        self.depth_telemetry = depth_telemetry
                        self.item['scene_depth'] = self.depth_telemetry(self.channel.address)
                    if self.args.textured_ship:
                        self.sampled = C.c_longlong()
                        C.windll.kernel32.QueryPerformanceCounter(C.byref(self.sampled))
                        self.item['sample_qpc'] = self.sampled.value
                        self.item['last_display_request_age_ms'] = (self.sampled.value - self.state['renderedAt']) * 1000 / self.state['qpcFrequency'] if self.state['renderedAt'] else None
                self.history.append(self.item)
                self.last = self.elapsed
                if self.args.play_session and len(self.history) > 120:
                    del self.history[0]
            time.sleep(0.05)

    def _end_observation(self):
        self.capture_complete = True
        self.session_stage = 'cleanup'
        if self.args.search_depth:
            self.channel.set('stop', 1)
            self.host_shutdown_expected = True
            self.until = min(self.deadline, time.monotonic() + 8)
            while time.monotonic() < self.until:
                self.search = self.depth_search_channel.snapshot(self.channel.address)
                if self.search['status'] in (4, 5):
                    break
                time.sleep(0.05)
            if self.search['status'] != 4 or self.search['restoredMask'] != 15 or self.search['error']:
                raise RuntimeError('Expanded-search hooks not confirmed restored; exit normally, do not unload DLL')
        if self.args.broad_capture:
            self.until = min(self.deadline, time.monotonic() + 8)
            while time.monotonic() < self.until:
                self.broad = broad_capture.header_at(self.channel.address)
                if self.broad['status'] in (3, 4):
                    break
                time.sleep(0.02)
            if self.broad['status'] != 3 or self.broad['error']:
                raise RuntimeError('Broad writer did not close successfully; exit normally')
            self.channel.set('stop', 1)
            self.host_shutdown_expected = True
        if self.args.depth_snapshots or self.args.textured_ship or self.args.source_timing:
            self.channel.set('enabled', 0)
            self.channel.set('stop', 1)
            self.host_shutdown_expected = True
        if self.semantic_enabled:
            if self.offscreen:
                self.offscreen.close()
            if self.timing_relay:
                self.timing_relay.stop()
            from controller_shutdown import wait_removed
            self.wait_removed = wait_removed
            print('Recording finished; restoring the test component. Keep SFC open until the exit cue.', flush=True)
            self.wait_removed(self.controller, self.enforce, self.controller_gate_observed, int(self.controller_args[self.controller_args.index('--max-seconds') + 1]), self.deadline)
            self.gate_text = (self.work / 'gate-controller.log').read_text(errors='replace')
            self.summary = json.loads((self.gate_dir / 'M1-A-summary.json').read_text(encoding='utf-8-sig')) if (self.gate_dir / 'M1-A-summary.json').exists() else {}
            self.gate_clean = self.controller.poll() == 0 and self.summary.get('gate_activated') is True and all((s in self.gate_text for s in ('component_state=removed', 'hook_bytes_restored=true', 'component_unloaded=true')))
            if not self.gate_clean:
                self.enforce()
                raise RuntimeError('Semantic component removal/unload not confirmed; exit normally')
        print('Depth capture window finished — please exit SFC normally now; validation follows after exit.' if self.args.depth_snapshots else 'TEST COMPLETE — please exit SFC normally now.', flush=True)
        winsound.Beep(660, 200)
        winsound.Beep(660, 200)
        self.until = min(self.deadline, time.monotonic() + 30)
        while self.launcher.poll() is None and time.monotonic() < self.until:
            self.enforce()
            time.sleep(0.1)
        self.normal = self.launcher.poll() == 0 and 'CHILD_EXIT code=0' in (self.work / 'launcher.log').read_text(errors='replace')
        if not self.normal:
            raise RuntimeError('Normal game exit not yet confirmed; do not kill SFC')
        if self.host.poll() is None:
            self.host.wait(timeout=8)
        if self.host.returncode:
            raise RuntimeError('Renderer shutdown did not complete normally')
        if not self.args.observation_only and (not self.args.private_ship) and (not self.history or max((v['drawCount'] for v in self.history)) < 30 or max((v['copyCount'] for v in self.history)) < 10):
            raise RuntimeError('Insufficient actual image/presentation evidence')
        if self.inspect_requested and (self.channel.state.visibilitySamples != 8 or self.channel.state.visibilityScope != (2 if self.args.inspect_early_depth else 1)):
            raise RuntimeError('Read-only visibility observations incomplete or wrong scope')
        if self.args.capture_ship_image:
            self.image_reader.wait(timeout=8)
            if self.image_reader.returncode:
                raise RuntimeError('Requested prepared ship image missing/reader failed;runtime evidence retained')
            from ship_image_snapshot import convert
            self.convert = convert
            self.image_result = self.convert(self.work)

    def _normal_exit(self):
        self.normal = True
        self.user_exited = True
        self.tuning_exited = bool(self.args.light_tuning)
        if self.args.play_session:
            self.capture_complete = True
        print('SFC exited normally. Cleaning up the renderer,workers and test setup now.', flush=True)

    def _failure(self, exc):
        self.error = str(exc)
        print('Test stopped safely: ' + self.error, flush=True)
        if self.pid and (not self.normal):
            print('Please exit the copied SFC game normally. ' + ('Replacement is being revoked; recovery evidence will be checked.' if self.args.player_replacement else 'No original drawing is suppressed.'), flush=True)

    def _collect(self):
        self.visibility = visibility_result(self.channel.state) if self.channel else 'NO_CHANNEL'
        self.search = None
        if self.channel and self.args.search_depth:
            try:
                self.search = self.depth_search_channel.snapshot(self.channel.address)
            except ValueError as exc:
                self.error = (self.error + '; ' if self.error else '') + str(exc)
        self.private_stats = None
        if self.args.private_ship and self.channel:
            from live_return import telemetry
            self.telemetry = telemetry
            self.private_stats = self.telemetry(self.channel.address)
        self.source_timing_result = None
        if self.timing_relay:
            try:
                self.live_timing_result = self.timing_relay.finish_play(self.pid) if self.args.play_session else partial_live_result(self.timing_relay) if self.user_exited and early_without_output(self.timing_relay) else self.timing_relay.finish(self.pid)
                if self.args.native_foreground and self.live_timing_result.get('result') != 'PARTIAL_NORMAL_EXIT_BEFORE_OUTPUT':
                    from native_foreground_qualification import save as save_foreground
                    self.save_foreground = save_foreground
                    self.live_timing_result['native_foreground'] = self.save_foreground(self.receiver.channel, self.work)
            except Exception as exc:
                self.error = (self.error + '; ' if self.error else '') + 'Live owner timing: ' + str(exc)
        if self.args.source_timing and (not self.args.play_session) and self.receiver and (not (self.user_exited and self.session_stage in ('startup', 'mission_selection'))):
            try:
                from source_timing import save
                self.save = save
                self.source_timing_result = self.save(self.receiver.channel, self.work, self.pid)
            except Exception as exc:
                self.error = (self.error + '; ' if self.error else '') + 'Source timing analysis: ' + str(exc)
        if self.insertion_capture:
            try:
                self.insertion_result = self.insertion_capture.finish()
                if self.insertion_result['error']:
                    raise RuntimeError(self.insertion_result['error'])
            except Exception as exc:
                self.error = (self.error + '; ' if self.error else '') + 'Insertion evidence: ' + str(exc)
        if self.native_capture:
            try:
                self.native_result = self.native_capture.finish()
                if self.native_result.get('error'):
                    raise RuntimeError(self.native_result['error'])
            except Exception as exc:
                self.error = (self.error + '; ' if self.error else '') + 'Native gate evidence: ' + str(exc)

    def _report(self):
        if self.args.private_ship:
            self.result.update(probe='REMIX-LIVE-RETURN-001', private_return=self.private_stats, fresh_asset=self.receiver.selected if self.receiver else None, backbuffer_ship_drawing=bool(self.args.visible_ship), original_ship_suppressed=False)
            if self.args.textured_ship:
                self.result.update(display_policy='v4 delayed-additive,request age<=100ms at enqueue;captured pose/camera NOT current-frame replacement', output_size=[1920, 1080], original_textures=True)
            if not self.error:
                self.result['result'] = 'FRESH_PRIVATE_LEASE_ACCEPTED_REVIEW_REQUIRED' if self.private_stats and self.private_stats['drawn'] else 'NO_CURRENT_FRAME_RETURN_ADDITIONAL_BOUNDED_EVIDENCE_REQUIRED'
            if not self.error and self.args.visible_ship:
                self.result['result'] = 'VISIBLE_SHIP_SUBMITTED_SPONSOR_REVIEW_REQUIRED' if self.final and self.final['drawCount'] else 'NO_VISIBLE_SHIP_SUBMISSIONS_PARTIAL'
        self.result['visibility_observation'] = self.visibility
        if self.args.source_timing:
            self.result.update(probe='D3D9-SOURCE-TIMING-001', source_timing=self.source_timing_result, remix_loaded=False, backbuffer_ship_drawing=False, original_ship_suppressed=False)
            self.result['result'] = 'SOURCE_TIMING_EVIDENCE_READY_ADJUDICATION_REQUIRED' if not self.error and self.source_timing_result and (self.source_timing_result['result'] == 'SOURCE_TIMING_OBSERVATION_COMPLETE_ADJUDICATION_REQUIRED') else 'PARTIAL'
        if self.args.live_owner_timing:
            self.result.update(probe='D3D9-LIVE-TIMING-001', live_owner_timing=self.live_timing_result, remix_loaded=bool(self.timing_relay and self.timing_relay.process), remix_in_sfc_process=False)
            self.result['result'] = 'LIVE_TIMING_EVIDENCE_READY_ADJUDICATION_REQUIRED' if not self.error and self.live_timing_result and (self.live_timing_result['result'] == 'LIVE_TIMING_OBSERVED_ADJUDICATION_REQUIRED') else 'PARTIAL'
        if self.args.d3d9_additive:
            self.result.update(probe='D3D9-ADDITIVE-001', backbuffer_ship_drawing=True, original_ship_suppressed=False, legacy_host_observation_only=True, observation_only=False)
            self.result['result'] = 'OFFSET_SHIP_SUBMITTED_SPONSOR_REVIEW_REQUIRED' if not self.error and self.live_timing_result and (self.live_timing_result['result'] == 'OFFSET_SHIP_SUBMITTED_REVIEW_REQUIRED') else 'PARTIAL'
        if self.args.multi_ship:
            self.result.update(probe='D3D9-MULTISHIP-001', aligned_overlay=bool(self.live_timing_result and self.live_timing_result.get('selected', {}).get('camera_offset') == [0, 0, 0]), original_ship_suppressed=False)
            self.result['result'] = 'MULTISHIP_OVERLAY_SPONSOR_REVIEW_REQUIRED' if not self.error and self.live_timing_result and (self.live_timing_result['result'] == 'MULTISHIP_OVERLAY_REVIEW_REQUIRED') else 'PARTIAL'
        if self.args.player_replacement:
            self.replacement = (self.live_timing_result or {}).get('replacement', {})
            self.result.update(probe='PLAYER-REPLACEMENT-001', original_ship_suppressed=bool(self.replacement.get('suppressed')), replacement=self.replacement, result='PLAYER_REPLACEMENT_SPONSOR_REVIEW_REQUIRED' if not self.error and self.replacement.get('committed') else 'PARTIAL')
        if self.args.native_foreground:
            self.result['native_foreground'] = (self.live_timing_result or {}).get('native_foreground')
        if self.args.native_insertion_policy:
            self.result.update(probe='NATIVE-GATE-001', timing_policy=self.args.native_insertion_policy, native_gate=self.native_result, shield_replay=False, late_composition=False, legacy_startup_warmup=self.args.legacy_startup_warmup, result='NATIVE_GATE_SPONSOR_COMPARISON_REQUIRED' if not self.error and self.native_result and self.native_result.get('commits') else 'PARTIAL')
            if self.args.native_all_ships:
                self.result.update(probe='NATIVE-COHORT-001', native_all_ships=True, break_models=self.args.break_models, native_cohort=(self.live_timing_result or {}).get('native_cohort'), original_ship_suppressed=bool(((self.live_timing_result or {}).get('native_cohort') or {}).get('suppressed')), result='NATIVE_COHORT_SPONSOR_REVIEW_REQUIRED' if not self.error and (self.live_timing_result or {}).get('result') == 'NATIVE_COHORT_REVIEW_REQUIRED' else 'PARTIAL')
            if ((self.native_result or {}).get('header') or {}).get('partial'):
                self.result['result'] = 'PARTIAL_TERMINAL_REPLACEMENT_STOP'
        if self.args.native_insertion_observe:
            self.result.update(probe='NATIVE-INSERTION-001', native_insertion=self.insertion_result, backbuffer_ship_drawing=False, original_ship_suppressed=False, observation_only=True, result='NATIVE_INSERTION_OBSERVATION_REQUIRES_ANALYSIS' if not self.error else 'PARTIAL')
            if (self.result.get('replacement') or {}).get('suppressed') or (self.result.get('replacement') or {}).get('committed') or (self.final and self.final['drawCount']):
                self.error = (self.error + '; ' if self.error else '') + 'Observation unexpectedly altered drawing'
                self.result.update(error=self.error, result='PARTIAL')
        if self.args.lifecycle_capture:
            from lifecycle_capture import analyze as analyze_lifecycle
            self.analyze_lifecycle = analyze_lifecycle
            try:
                self.result['lifecycle_capture'] = self.analyze_lifecycle(self.work / 'gate')
            except (OSError, ValueError) as exc:
                self.result['lifecycle_capture'] = dict(result='PARTIAL', error=str(exc), native_death_signal_qualified=False)
            if self.result['lifecycle_capture']['result'] == 'PARTIAL':
                self.result['result'] = 'PARTIAL'
        if self.args.persistent_scene and (not self.args.play_session):
            try:
                self.result['persistent_scene'] = json.loads((self.work / 'gate/PERSISTENT-SCENE-001.json').read_text())
            except (OSError, ValueError) as exc:
                self.result['persistent_scene'] = dict(error=str(exc))
                self.result['result'] = 'PARTIAL'
        if self.args.offscreen_position:
            from offscreen_position import analyze as analyze_offscreen
            self.analyze_offscreen = analyze_offscreen
            try:
                self.result['offscreen_position'] = self.analyze_offscreen(self.work)
            except (OSError, ValueError, KeyError) as exc:
                self.result['offscreen_position'] = dict(result='PARTIAL', error=str(exc))
            if self.result['offscreen_position']['result'] == 'PARTIAL':
                self.result['result'] = 'PARTIAL'
        if self.args.light_tuning:
            self.result['cleanup_mode'] = 'process-exit reclamation' if self.tuning_exited else 'controlled timed removal'
        if self.args.capture_ship_image:
            self.result['prepared_ship_image'] = self.image_result
        if self.args.capture_native_lights and (not self.args.light_tuning) and (not self.args.d3d9_additive) and (not (self.user_exited and (not self.capture_complete))):
            try:
                from light_discovery import analyze as analyze_lights
                self.analyze_lights = analyze_lights
                self.lights = self.analyze_lights(self.work / 'gate/native-lights.bin')
                self.expected = [int(self.receiver.name[-32:][i:i + 8], 16) for i in range(0, 32, 8)]
                if self.lights['session_words'] != self.expected:
                    raise ValueError('Light discovery session mismatch')
                self.worker = json.loads((self.work / 'gate/native-lights-summary.json').read_text())
                if self.worker['io_failed'] or self.worker['queued'] or self.worker['written'] != self.lights['records']:
                    raise ValueError('Light discovery worker incomplete')
                self.result['native_lights'] = self.lights
            except (ValueError, OSError) as exc:
                self.error = (self.error + '; ' if self.error else '') + str(exc)
                self.result['error'] = self.error
                self.result['result'] = 'PARTIAL'
        if self.light_relay:
            self.result['light_controls'] = self.light_relay.summary()
        self.result['observation_only'] = self.args.observation_only and (not self.args.d3d9_additive)
        if self.args.scene_depth:
            self.samples = [v['scene_depth'] for v in self.history if 'scene_depth' in v]
            self.last_depth = self.samples[-1] if self.samples else {}
            self.passed = bool(self.last_depth.get('qualified') and self.last_depth.get('displayed') and (not self.last_depth.get('failed')) and (not self.last_depth.get('wrong_thread')))
            self.result['scene_depth_test'] = dict(result='DEPTH_FILTER_RUNTIME_REVIEW_REQUIRED' if self.passed else 'PARTIAL_NO_QUALIFIED_DEPTH_DISPLAY', telemetry=self.last_depth, original_suppressed=False, grid_policy='NOT_ASSUMED')
            if not self.passed:
                self.error = (self.error + '; ' if self.error else '') + 'Scene depth needs review; originals were retained'
                self.result['error'] = self.error
                self.result['result'] = 'PARTIAL'
        self.result['expanded_search'] = self.search
        self.result['damage_textures'] = self.args.damage_textures
        self.result['copied_player_preferences_changed'] = self.copy_after['sfc.ini'] != self.metadata['copied_critical_before']['sfc.ini'] and 'sfc.ini' not in self.copy_protected_changes
        self.result['broad_proxy_restored'] = self.proxy_restored
        if self.args.depth_snapshots and (not (self.user_exited and (not self.capture_complete))):
            try:
                from depth_snapshot_analysis import analyze_run
                self.analyze_run = analyze_run
                self.result['depth_snapshots'] = self.analyze_run(self.work, images=True)
                if not self.result['depth_snapshots']['complete']:
                    self.status = self.result['depth_snapshots']['status']
                    raise ValueError(f"Depth capture PARTIAL: {self.status.get('files', 0)}/3 images; stage={self.status.get('failure_stage_name', 'unrecorded')}; HRESULT={self.status.get('failure_hresult_hex', 'unrecorded')}; feature_level={self.status.get('feature_level', 'unrecorded')}. Evidence retained; no ship suppressed.")
            except (ValueError, OSError) as exc:
                self.error = (self.error + '; ' if self.error else '') + str(exc)
                self.result['error'] = self.error
                self.result['result'] = 'PARTIAL'
        if self.args.calibration and (not (self.user_exited and (not self.capture_complete))):
            try:
                from present_calibration import analyze
                self.analyze = analyze
                self.result['semantic_calibration'] = self.analyze(self.work, self.metadata['semantic_calibration']['scene_session'], self.pid)
            except (ValueError, OSError) as exc:
                self.error = (self.error + '; ' if self.error else '') + str(exc)
                self.result['error'] = self.error
                self.result['result'] = 'PARTIAL'
        if self.args.broad_capture and (self.work / 'broad.bin').exists():
            try:
                self.result['broad_capture'] = broad_capture.save_analysis(self.work / 'broad.bin')
            except ValueError as exc:
                self.error = (self.error + '; ' if self.error else '') + str(exc)
                self.result['error'] = self.error
                self.result['result'] = 'PARTIAL'
        if self.search:
            self.result['expanded_search_verdict'] = self.depth_search_channel.verdict(self.search)
        if self.args.multi_ship and self.args.pipeline_mode == 'test' and (not (self.user_exited and (not self.capture_complete))):
            try:
                sys.path.insert(0, str(ROOT / 'tools/m1_component'))
                from identity_census import analyze_summary
                self.analyze_summary = analyze_summary
                self.result['identity_census'] = self.analyze_summary(self.work / 'gate/M1-A-summary.json')
                if not self.result['identity_census']['enabled']:
                    raise ValueError('Full-window identity census inactive')
                if self.result['identity_census']['omitted_observations']:
                    self.result['result'] = 'PARTIAL'
            except (ValueError, OSError, KeyError) as exc:
                self.error = (self.error + '; ' if self.error else '') + 'Identity census: ' + str(exc)
                self.result['error'] = self.error
                self.result['result'] = 'PARTIAL'
        if self.args.multi_ship and self.args.pipeline_mode == 'performance':
            self.result['identity_census'] = {'enabled': False, 'reason': 'Performance mode;identity safeguards remain active'}
        self.result['pipeline_policy'] = self.mode_policy(self.args.pipeline_mode)
        self.result['experimental_parallel_assets'] = self.args.experimental_parallel_assets
        self.result['async_material_checkout'] = self.metadata.get('async_material_checkout')
        self.result['final_report_complete'] = True
        self.result.update(early_game_exit=self.user_exited and (not self.capture_complete) and (not self.args.light_tuning), observation_complete=self.capture_complete, exit_stage=self.session_stage, controller_retired_after_game_exit=self.controller_retired)
        if self.user_exited:
            self.result['cleanup_mode'] = 'controlled live unload' if self.gate_clean else 'process-exit reclamation'
            if not self.error and (self.args.light_tuning or not self.capture_complete):
                self.result['result'] = 'TUNING_FINISHED_NORMAL_EXIT' if self.args.light_tuning else 'PARTIAL_DURATION_NORMAL_EXIT'
        if self.args.play_session:
            self.gate_status = (self.live_timing_result or {}).get('native_gate_summary') or {}
            self.healthy = not (self.error or self.gate_status.get('error') or self.gate_status.get('partial'))
            self.result.update(probe='NATIVE-PLAY-SESSION-001', play_session=True, workflow_seconds=None, capture_seconds=None, early_game_exit=False, result='PLAY_SESSION_FINISHED_NORMAL_EXIT' if self.normal and self.healthy else 'PARTIAL_PLAY_SESSION', diagnostic_capture=False)
        run_report.save(self.work, self.result)


def main(argv=None):
    DiagnosticSession(argv).run()

def cli():
    try:main()
    except BaseException as exc:
        run_report.failure(exc)
        raise

if __name__=='__main__':cli()
