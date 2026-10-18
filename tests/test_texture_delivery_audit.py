from pathlib import Path
import json
import struct
import sys
import tempfile
import unittest
from unittest import mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
import live_return
import audit_texture_delivery as target
from textured_asset import prepare
from run_coverage_probe import prepare_mesh
from test_live_scene import packet_fixture
from PIL import Image

class TextureDeliveryAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        base=Path(self.temp.name);root=base/'project';root.mkdir()
        self.folder=root/'artifacts/remix-runtime/runs/test';self.folder.mkdir(parents=True)
        game=base/'SFC-Remix-Return-Test';game.mkdir()
        image=Image.new('RGB',(8,8),(60,20,30));image.putpixel((0,0),(0,255,0));image.save(game/'ship.bmp')
        packet,refs=packet_fixture();source=self.folder/'asset.bin';source.write_bytes(packet);source.with_suffix('.json').write_bytes(refs)
        with mock.patch('run_coverage_probe.ROOT',root):mesh=prepare_mesh(source,self.folder/'live-mesh.bin')
        prepare(packet,refs,self.folder,game)
        (self.folder/'fresh-asset.json').write_text(json.dumps({'mesh':mesh}))
        patch=mock.patch.object(target,'ROOT',root);patch.start();self.addCleanup(patch.stop)
    def test_intact_delivery(self):
        report=target.audit(self.folder)
        self.assertTrue(report['vertex_uv_exact']);self.assertTrue(report['images_pixel_exact'])
    def test_changed_uv_rejected(self):
        p=self.folder/'live-mesh.bin';raw=bytearray(p.read_bytes());struct.pack_into('<f',raw,32+24,.123);p.write_bytes(raw)
        with self.assertRaisesRegex(ValueError,'vertex/UV'):target.audit(self.folder)
    def test_changed_derived_pixels_rejected(self):
        image=next((self.folder/'textures').glob('*.dds'));Image.new('RGB',(8,8),(0,0,0)).save(image)
        with self.assertRaisesRegex(ValueError,'pixels changed'):target.audit(self.folder)
