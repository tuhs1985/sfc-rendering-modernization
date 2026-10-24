import importlib
from pathlib import Path
import struct
import sys
import unittest
from unittest.mock import Mock
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[1]
for name in ('d3d9_proof','remix_runtime','remix_ingest','scene_bridge','m1_component'):
    sys.path.insert(0,str(ROOT/'tools'/name))
import multi_scene as wire
from multi_scene_relay import Relay


class MultiSceneTests(unittest.TestCase):
    def test_material_reload_isolation_cannot_qualify_normal_workflow(self):
        source=(ROOT/'tools/remix_runtime/qualify_multiship.py').read_text()
        self.assertIn("if result.get('diagnostic_skip_late_material_reload')",source)
        source=(ROOT/'tools/remix_runtime/multi_scene_relay.py').read_text()
        self.assertIn("if not self.offline_fixture:raise ValueError('Material-reload isolation is offline diagnosis only')",source)

    def test_previous_diagnostic_distance_and_aligned_option(self):
        self.assertEqual(wire.camera_offset(),[-15.897722721099854,0,0])
        self.assertEqual(wire.camera_offset(b'camera_left_distance = 0'),[0,0,0])

    def test_placement_rejects_invalid_or_extra_settings(self):
        for raw in (b'camera_left_distance = -1',b'camera_left_distance = nan',
                    b'camera_left_distance = true',b'camera_left_distance = 1000001',
                    b'camera_left_distance = 1\nz_height = 2'):
            with self.assertRaises(ValueError):wire.camera_offset(raw)

    def row(self):
        r=[0]*96;r[1]=7;r[4]=1;r[5]=70;r[6]=71;r[7]=3
        return r

    def test_cross_abi_layout_and_no_overlap(self):
        self.assertEqual(wire.STORE_BYTES,107072)
        self.assertGreater(wire.OFFSET,12*1024*1024+2621568)
        self.assertLess(wire.OFFSET+wire.STORE_BYTES,15*1024*1024)
        self.assertEqual(wire.ASSET.size,88)

    def test_catalog_content_and_bytes(self):
        raw=wire.asset_packet(1,1,self.row(),'ab'*32,b'geometry',[b'texture'])
        fields=wire.ASSET.unpack(raw)
        self.assertEqual(fields[:8],(1,1,7,3,70,71,8,7))
        self.assertEqual(fields[8],bytes.fromhex('ab'*32))
        self.assertEqual(fields[-1],wire.fnv(raw[:-8]))

    def test_invalid_identity_caps(self):
        for identity in (0,65):
            with self.assertRaises(ValueError):wire.asset_packet(identity,1,self.row(),'ab'*32,b'a',[])
        with self.assertRaises(ValueError):wire.asset_packet(1,1,self.row(),'00'*32,b'a',[])
        with self.assertRaises(ValueError):wire.asset_packet(1,1,self.row(),'ab'*32,bytes(2*1024*1024+1),[])

    def test_corrupt_or_overwritten_catalog_rejected(self):
        channel=Mock();channel.read.return_value=bytes(8)
        raw=wire.asset_packet(1,1,self.row(),'ab'*32,b'g',[b't'])
        with self.assertRaises(ValueError):wire.publish(channel,1,raw[:-1]+bytes([raw[-1]^1]))
        channel.read.return_value=struct.pack('<2i',2,1)
        with self.assertRaises(ValueError):wire.publish(channel,1,raw)

    def test_shared_asset_distinct_owner_epoch_no_rebuild(self):
        relay=object.__new__(Relay);relay.content=Mock();relay.content.signature.return_value='ab'*32
        raw=wire.asset_packet(1,1,self.row(),'ab'*32,b'g',[b't'])
        relay.resident={'ab'*32:(1,Path('owned-gpu'),{'model_name':'test'},raw)}
        row=self.row();row[1]=8;row[7]=4
        canonical=dict(id=1,phase='ready',wire=raw,gpu=Path('owned-gpu'),manifest={'model_name':'test'})
        duplicate=dict(id=2,phase='alias',canonical=1,row=row,signature='ab'*32)
        relay.preparer=SimpleNamespace(pump=lambda:[],jobs={1:canonical,2:duplicate})
        relay.collect_prepared();alias=duplicate['wire'];path=wire.ASSET.unpack(alias)[1];new=duplicate['new']
        fields=wire.ASSET.unpack(alias)
        self.assertFalse(new);self.assertEqual(path,1)
        self.assertEqual(fields[:6],(2,1,8,4,70,71))
        self.assertEqual(fields[8:],wire.ASSET.unpack(raw)[8:11]+(wire.fnv(alias[:-8]),))

    def test_live_workflow_is_explicit_and_preserves_legacy(self):
        source=(ROOT/'tools/remix_runtime/run_return_game.py').read_text()
        self.assertIn("if args.multi_ship:from multi_scene_relay import Relay",source)
        self.assertIn("if not args.multi_ship:buffer_qualified()",source)
        self.assertIn('original_ship_suppressed=False',source)
        self.assertIn("if self.additive and not self.multi_scene:",(ROOT/'tools/remix_runtime/live_owner_timing.py').read_text())


if __name__=='__main__':unittest.main()
