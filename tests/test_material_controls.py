from pathlib import Path
import json
import struct
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_ingest'))
from material_controls import encode,Relay
from textured_asset import fnv,prepare
from test_live_scene import packet_fixture
from PIL import Image

class MaterialTests(unittest.TestCase):
    def test_defaults_and_wire(self):
        # Factory defaults must not depend on the sponsor's mutable tuning file.
        raw=encode(b'[material]\n');self.assertEqual(len(raw),56)
        self.assertEqual(struct.unpack('<2I10fQ',raw)[:6],(0x3143544d,1,1.,1.,0.,0.))
        self.assertEqual(struct.unpack_from('<Q',raw,48)[0],fnv(raw[:48]))
    def test_invalid_and_optional(self):
        for text in ('roughness=2','illumination_strength=-1','roughness=nan','roughness=true','wat=1','metallic=2','anisotropy=-2','base_colour=[1,1]','base_colour=[1,1,1]','illumination_colour=[1,2,1]'):
            with self.subTest(text=text),self.assertRaises(ValueError):encode(('[material]\n'+text).encode())
        raw=encode(b'[material]\nroughness=0.4\nillumination_strength=2\nmetallic=0.3\nanisotropy=-0.5\n')
        self.assertAlmostEqual(struct.unpack_from('<f',raw,8)[0],.4)
    def test_last_good_and_bounds(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp);config=folder/'settings.toml';config.write_text('[material]\nroughness=0.5\n')
            relay=Relay(folder,config);relay.poll();good=(folder/'material-controls.bin').read_bytes()
            config.write_text('[material]\nroughness=99\n');relay.poll()
            self.assertEqual((folder/'material-controls.bin').read_bytes(),good);self.assertEqual(relay.rejected,1)
            relay.accepted=256;config.write_text('[material]\nroughness=0.1\n');relay.poll()
            self.assertEqual((folder/'material-controls.bin').read_bytes(),good)
    def test_product_not_raw_mask_and_source_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp);out=folder/'out';out.mkdir()
            Image.new('RGB',(8,8),(120,60,20)).save(folder/'ship.bmp')
            Image.new('RGB',(4,4),(128,0,255)).save(folder/'mask.bmp')
            original=(folder/'ship.bmp').read_bytes();packet,refs=packet_fixture()
            # Group flags/source layout is decoded from the real packet helper.
            from live_scene import decode_mesh
            mesh=decode_mesh(packet,refs)
            # Locate source flags and second image ID using the helper's packet layout.
            self.assertEqual(len(mesh['groups']),1)
            # Qualifier injection changes only the synthetic test association,not capture code.
            import textured_asset
            qualify=textured_asset.qualify_mesh
            def with_mask(p,r,images):
                result=qualify(p,r,images);result['assignments'][0]['secondary']=images.load('mask.bmp');return result
            from unittest.mock import patch
            with patch.object(textured_asset,'qualify_mesh',side_effect=with_mask):manifest=prepare(packet,refs,out,folder)
            self.assertTrue(manifest['secondary_applied']);self.assertFalse(manifest['whole_hull_emission'])
            emission=manifest['materials'][0]['illumination']
            self.assertEqual(emission['source_dimensions'],[[8,8],[4,4]])
            self.assertEqual(emission['derived_dimensions'],[8,8])
            with Image.open(emission['dds']) as image:self.assertEqual(image.convert('RGB').getpixel((0,0)),(60,0,20))
            self.assertEqual((folder/'ship.bmp').read_bytes(),original)
            raw=(out/'live-emissions.bin').read_bytes();self.assertEqual(len(raw),104)
            self.assertEqual(struct.unpack_from('<Q',raw,16)[0],fnv(raw[24:]))
    def test_backend_field_wiring_and_fence_order(self):
        root=Path(__file__).resolve().parents[1]/'tools/remix_runtime'
        source=(root/'ship_textured_asset.h').read_text()
        for field in ('roughnessConstant=v[0]','metallicConstant=v[2]','anisotropy=v[3]','emissionPaths[i].empty()?0:v[1]'):
            self.assertIn(field,source)
        host=(root/'ship_live_host.cpp').read_text()
        self.assertLess(host.index('live GPU completion'),host.index('auto next=materialSettings'))
        self.assertIn('load(wire.lease)!=Idle',host)
        self.assertIn('mi.hash=seed.meshHash^next.revision',host)

if __name__=='__main__':unittest.main()
