import sys
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest import TestCase,mock

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools/remix_runtime'),str(ROOT/'tools/d3d9_proof')]
from pipeline_mode import policy,validate
from multi_scene_resources import Reservations,AGGREGATE_BYTES,EVIDENCE_RESERVE

class PipelineModeTests(TestCase):
    def test_modes_do_not_disable_safety(self):
        for mode in ('performance','test'):
            self.assertTrue(policy(mode)['safety_checks'])
            self.assertFalse(policy(mode)['continuous_image_readback'])
        self.assertFalse(policy('performance')['detailed_evidence'])
        self.assertTrue(policy('test')['detailed_evidence'])
        with self.assertRaises(ValueError):validate('unsafe')

    def test_inventory_scanned_once_before_workers(self):
        with mock.patch('run_offline.storage',return_value=0) as inventory:
            ledger=Reservations()
            for _ in range(5):
                with ledger.asset():pass
            inventory.assert_called_once_with()
        self.assertEqual(ledger.bytes,0)

    def test_failed_partial_output_is_accounted(self):
        ledger=Reservations(inventory=0)
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)
            with self.assertRaisesRegex(ValueError,'partial'):
                with ledger.asset(folder):
                    (folder/'partial.bin').write_bytes(b'12345')
                    raise ValueError('partial')
            self.assertEqual(ledger.bytes,0)
            self.assertEqual(ledger.committed,5)

    def test_concurrent_writers_commit_without_global_scans(self):
        ledger=Reservations(inventory=0);barrier=threading.Barrier(4)
        with tempfile.TemporaryDirectory() as temp:
            def write(i):
                folder=Path(temp)/str(i);folder.mkdir()
                with ledger.asset(folder):
                    barrier.wait(timeout=3)
                    (folder/'image.bin').write_bytes(b'123')
            with mock.patch('run_offline.storage',side_effect=AssertionError('No runtime scan')):
                with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(write,range(4)))
        self.assertEqual(ledger.committed,12);self.assertEqual(ledger.bytes,0)

    def test_aggregate_exhaustion_still_fails_closed(self):
        ledger=Reservations(inventory=AGGREGATE_BYTES-EVIDENCE_RESERVE)
        with self.assertRaises(ValueError):
            with ledger.asset():self.fail('Must not admit')
        self.assertEqual(ledger.bytes,0)

    def test_launcher_exposes_both_and_defaults_to_performance(self):
        source=(ROOT/'tools/d3d9_proof/start_d3d9_multiship_session.ps1').read_text()
        self.assertIn("[ValidateSet('Performance','Test')]",source)
        self.assertIn("$Mode='Performance'",source)
        self.assertIn('--pipeline-mode',source)

    def test_functional_state_precedes_optional_native_logging(self):
        source=(ROOT/'tools/m1_component/m1_live_scene.h').read_text()
        self.assertIn('if(b.performance)continue; // Latest state is functional',source)
        self.assertIn('if(b.performance)continue; // Shared light transport remains',source)
        source=(ROOT/'tools/m1_component/m1_component.cpp').read_text()
        self.assertIn('if(g_performance_mode)return;',source)
