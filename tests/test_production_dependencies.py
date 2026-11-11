import hashlib
from pathlib import Path
import sys
import tempfile
import time
from unittest.mock import patch
import unittest

ROOT=Path(__file__).resolve().parents[1]
for name in ('release','remix_runtime','d3d9_proof','scene_bridge','remix_ingest'):
    sys.path.insert(0,str(ROOT/'tools'/name))
from inventory_dependencies import production_files
from parallel_assets import Tasks
import runtime_files


class ProductionDependencyTests(unittest.TestCase):
    def test_runtime_file_helpers_preserve_existing_digest_case_and_missing_packet_behavior(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'packet';p.write_bytes(b'known packet')
            self.assertEqual(runtime_files.digest(p),hashlib.sha256(b'known packet').hexdigest().upper())
            self.assertEqual(runtime_files.capture_file_bytes(p),12)
            p.unlink();self.assertEqual(runtime_files.capture_file_bytes(p),0)

    def test_tasks_still_complete_and_propagate_errors_without_collecting_timing(self):
        tasks=Tasks(workers=2,record_timings=False)
        def fail():raise ValueError('expected task failure')
        try:
            tasks.add(('base',1),lambda:42)
            tasks.add(('bad',1),fail)
            with patch('parallel_assets.time.perf_counter_ns',side_effect=AssertionError('diagnostic clock called')):
                until=time.monotonic()+2
                while time.monotonic()<until:
                    tasks.pump()
                    if all(t['state'] in ('done','failed') for t in tasks.tasks.values()):break
                    time.sleep(.001)
            self.assertEqual(tasks.tasks[('base',1)]['value'],42)
            self.assertEqual(tasks.tasks[('bad',1)]['error'],'expected task failure')
            self.assertEqual(tasks.spans,[])
            self.assertNotIn('begin_ns',tasks.tasks[('base',1)])
        finally:tasks.close()

    def test_production_list_keeps_wire_camera_settings_and_excludes_standalone_toolchains(self):
        files=set(production_files())
        self.assertEqual({p for p in files if p.startswith('src/')},
                         {'src/launcher/bootstrap.py','src/launcher/session_recording.py',
                          'src/session/coordinator.py','src/session/exit_monitor.py','src/session/reports.py',
                          'src/session/graphics_transaction.py','src/session/component_qualification.py',
                          'src/runtime/runtime_context.py','src/runtime/release_manifest.py','src/runtime/windows_processes.py','src/runtime/runtime_files.py','src/runtime/copied_preferences.py','src/runtime/session_recovery.py',
                          'src/assets/parallel_assets.py','src/assets/scene_bundle.py','src/assets/material_binding.py','src/assets/material_library.py','src/assets/roughness_maps.py','src/assets/mesh_checksum.py','src/assets/damage_materials.py','src/assets/damage_mapping.py','src/assets/break_scene.py','src/assets/mesh_decode.py',
    'src/transport/live_bridge.py',
    'src/transport/live_scene.py',
    'src/transport/scene_capacity.py',
    'src/transport/texture_memory.py',
    'src/transport/warm_start.py',
    'src/transport/multi_scene.py',
    'src/transport/owner_rebind.py',
    'src/transport/recovery_service.py',
    'src/transport/light_transport.py',
    'src/transport/scene_receiver.py',
    'src/assets/asset_content.py',
    'src/rendering/live_owner_timing.py',
    'src/rendering/multi_scene_relay.py',
    'src/rendering/progressive_scene_relay.py',
    'src/rendering/async_material_checkout.py',
    'src/rendering/renderer_backend.py'})
        self.assertFalse(any(p.startswith('tools/release/') for p in files))
        names={Path(p).stem for p in production_files()}
        self.assertTrue({'native_gate','native_cohort','live_camera','break_scene','effect_lights',
            'release_manifest','session_recovery','session_recording','runtime_files',
            'coordinator','exit_monitor','reports'}<=names)
        self.assertFalse(names.intersection({'run_return_game','session_exit','run_report','broad_capture','modes'}))
        self.assertFalse(names.intersection({'run_offline','run_direct64','run_intercept','run_return_fixture',
            'asset_preparation','owner_selection','synchronized_buffer','light_discovery','player_replacement',
            'loading_policy','evidence_budget','qualify_multiship','qualify_persistent_scene','depth_search_channel'}))
