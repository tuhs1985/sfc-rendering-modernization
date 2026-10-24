import sys
from pathlib import Path
import unittest
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/remix_runtime'))
from multi_scene_resources import require_capacity,policy,EVIDENCE_RESERVE,AGGREGATE_BYTES


class MultiSceneResourceTests(unittest.TestCase):
    def test_scene_above_old128mib_is_not_rejected(self):
        require_capacity(500*1024*1024,inventory=1024*1024*1024,free=AGGREGATE_BYTES)
        self.assertTrue(policy()['legacy_scene_image_cap_removed'])

    def test_disk_and_authorized_aggregate_still_bound_preparation(self):
        for inventory,free in ((AGGREGATE_BYTES,AGGREGATE_BYTES),(0,EVIDENCE_RESERVE-1)):
            with self.assertRaises(ValueError):require_capacity(0,inventory=inventory,free=free)
        with self.assertRaises(ValueError):require_capacity(-1,inventory=0,free=AGGREGATE_BYTES)

    def test_reservation_boundary(self):
        require_capacity(10,inventory=AGGREGATE_BYTES-EVIDENCE_RESERVE-10,free=EVIDENCE_RESERVE+10)
        with self.assertRaises(ValueError):require_capacity(11,inventory=AGGREGATE_BYTES-EVIDENCE_RESERVE-10,free=EVIDENCE_RESERVE+10)

    def test_all_multiship_callers_remove_scene_cap_not_legacy_guards(self):
        source=(ROOT/'tools/remix_runtime/run_return_game.py').read_text()
        self.assertIn('if not args.multi_ship and images>128*1024*1024',source)
        source=(ROOT/'tools/remix_runtime/run_return_fixture.py').read_text()
        self.assertIn('if not args.multi_ship and images>128*1024*1024',source)
        source=(ROOT/'tools/remix_runtime/live_owner_timing.py').read_text()
        self.assertIn('scratch_limit=AGGREGATE_BYTES if self.multi_scene',source)
        source=(ROOT/'tools/remix_runtime/multi_scene_relay.py').read_text()
        self.assertNotIn('self.image_bytes+estimate>128',source)
        self.assertNotIn('len(self.original_images|original.keys())>256',source)

    def test_shared_fixture_changes_identity_not_geometry_or_textures(self):
        sys.path[:0]=[str(ROOT/'tools/d3d9_proof'),str(ROOT/'tools/scene_bridge'),str(ROOT/'tools/remix_ingest')]
        from multi_scene_fixture import CAPTURES,synthetic_instance
        from live_scene import decode_mesh
        path=CAPTURES[0];packet=path.read_bytes();references=path.with_suffix('.json').read_bytes()
        before=decode_mesh(packet,references);raw,refs=synthetic_instance(packet,references,31);after=decode_mesh(raw,refs)
        self.assertEqual(after['header'][4],31)
        self.assertEqual(before['geometry_sha256'],after['geometry_sha256'])
        self.assertEqual(before['refs']['resources'],after['refs']['resources'])
        self.assertEqual(before['corners'],after['corners'])

    def test_gameplay_worker_excludes_inherited_fixture_switches(self):
        source=(ROOT/'tools/remix_runtime/live_owner_timing.py').read_text()
        self.assertIn('if not self.offline_fixture:',source)
        for key in ('SFC_DIRECT64_BACKBUFFER_DIAGNOSTIC','SFC_D3D9_REBIND_FIXTURE','SFC_D3D9_FIXTURE_ROWS','SFC_SYNC_FIXTURE_SHORT_LEAD'):
            self.assertIn(key,source)
