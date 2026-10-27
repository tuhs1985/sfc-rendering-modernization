import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools/remix_runtime'),str(ROOT/'tools/d3d9_proof')]
from material_library import publish_remix_revision


class MaterialRevisionTests(unittest.TestCase):
    def test_fast_revisions_remain_distinct_at_usd_precision_without_waits(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);target=root/'mod.usda';target.write_text('initial')
            # Simulate a clock ahead of actual writes. Every revision must still
            # differ, including the full64-asset session; no pacing/sleep needed.
            initial=(target.stat().st_mtime_ns//1_000_000_000+120)*1_000_000_000
            os.utime(target,ns=(initial,initial));last=initial
            for i in range(64):
                text=f'#usda 1.0\n# revision {i}\n'
                with patch('time.sleep',side_effect=AssertionError('No wait permitted')):
                    receipt=publish_remix_revision(root,text)
                actual=target.stat().st_mtime_ns
                self.assertGreater(actual//1_000_000_000,last//1_000_000_000)
                self.assertEqual(receipt['published_mtime_ns'],actual)
                self.assertEqual(target.read_bytes(),text.replace('\n',os.linesep).encode())
                self.assertFalse((root/'mod.usda.pending').exists());last=actual

    def test_busy_exchange_preserves_last_good_then_retries_same_content(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);target=root/'mod.usda';target.write_text('good')
            before=target.stat().st_mtime_ns
            with patch.object(Path,'replace',side_effect=PermissionError('Busy')):
                with self.assertRaises(PermissionError):publish_remix_revision(root,'next')
            self.assertEqual(target.read_text(),'good');self.assertEqual(target.stat().st_mtime_ns,before)
            publish_remix_revision(root,'next');self.assertEqual(target.read_text(),'next')

    def test_natural_later_time_preserved_and_metadata_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            receipt=publish_remix_revision(root,'#usda 1.0\n')
            self.assertEqual(receipt['natural_mtime_ns'],receipt['published_mtime_ns'])
            with self.assertRaisesRegex(ValueError,'cap'):publish_remix_revision(root,'x'*(16*1024*1024+1))

    def test_only_checkout_routes_publication_through_compatibility_policy(self):
        from async_material_checkout import Relay
        from progressive_scene_relay import Relay as Progressive
        from multi_scene_relay import Relay as Baseline
        self.assertIs(Progressive.commit_layers,Baseline.commit_layers)
        self.assertIsNot(Relay.commit_layers,Baseline.commit_layers)

    def test_qualification_rejects_missing_colliding_and_discontinuous_receipts(self):
        from qualify_async_material import validate_revisions
        def event(before,after):
            return dict(usd_revision=dict(policy='remix-openusd-windows-second-revision-v1',
                previous_mtime_ns=before,published_mtime_ns=after))
        validate_revisions([event(1_100_000_000,2_000_000_000),event(2_000_000_000,3_000_000_000)])
        for events in ([],[{}],[event(1_100_000_000,1_900_000_000)],
                       [event(1_100_000_000,2_000_000_000),event(2_500_000_000,3_000_000_000)]):
            with self.assertRaises(ValueError):validate_revisions(events)


if __name__=='__main__':unittest.main()
