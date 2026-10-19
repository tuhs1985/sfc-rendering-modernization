from pathlib import Path
import hashlib
import json
import struct
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
import live_return
from textured_asset import prepare,fnv
from test_live_scene import packet_fixture
from PIL import Image

class TexturedAssetTests(unittest.TestCase):
    def test_origin_conversion_is_pinned_and_remix_only(self):
        root=Path(__file__).resolve().parents[1]
        host=(root/'tools/remix_runtime/ship_live_host.cpp').read_text()
        self.assertIn('if(textured){for(auto& vertex:vertices)vertex.texcoord[1]=sfc_remix_adapter::textureV(vertex.texcoord[1])',host)
        self.assertEqual(host.count('sfc_remix_adapter::textureV('),1)
        self.assertIn('remix_texture_coordinates.h',live_return.LIVE_SOURCES)
        for name in ('run_coverage_probe.py','export_live_obj.py','textured_asset.py'):
            source=(root/'tools/remix_runtime'/name).read_text()
            self.assertNotIn('sfc_remix_adapter',source)
        self.assertNotIn('remix_texture_coordinates', (root/'tools/m1_component/m1_live_scene.h').read_text())
    def test_hull_material_does_not_emit_primary_texture(self):
        source=(Path(__file__).resolve().parents[1]/'tools/remix_runtime/ship_textured_asset.h').read_text()
        self.assertIn('info.albedoTexture=paths[i].c_str()',source)
        self.assertIn('emissionPaths[i].empty()?nullptr:emissionPaths[i].c_str()',source)
        self.assertIn('emissionPaths[i].empty()?0:v[1]',source)
        self.assertIn('info.emissiveColorConstant={0,0,0}',source)
        self.assertNotIn('info.emissiveTexture=paths[i].c_str()',source)
    def test_textured_inspection_light_is_directional_not_world_origin_point(self):
        source=(Path(__file__).resolve().parents[1]/'tools/remix_runtime/ship_live_host.cpp').read_text()
        self.assertIn('distant.direction={0,-.70710678f,-.70710678f}',source)
        self.assertIn('textured?static_cast<void*>(&distant):static_cast<void*>(&sphere)',source)
        self.assertIn('remixapi_Float3D{1,1,1}',source)
    def test_primary_provenance_group_indices_and_original_pixels(self):
        with tempfile.TemporaryDirectory() as root:
            root=Path(root);game=root/'game';game.mkdir();out=root/'out';out.mkdir()
            image=Image.new('RGB',(8,8),(120,35,60));image.putpixel((0,0),(20,200,40));image.save(game/'ship.bmp')
            original=(game/'ship.bmp').read_bytes();packet,refs=packet_fixture();manifest=prepare(packet,refs,out,game)
            self.assertFalse(manifest['whole_hull_emission']);self.assertFalse(manifest['secondary_applied'])
            self.assertTrue(manifest['renderer_adapter']['raw_uv_and_images_unchanged'])
            self.assertEqual(manifest['renderer_adapter']['backend'],'Pinned Remix SDK/DDS')
            self.assertEqual(manifest['materials'][0]['primary']['sha256'],hashlib.sha256(original).hexdigest())
            with Image.open(manifest['materials'][0]['primary']['dds']) as decoded:self.assertEqual(decoded.convert('RGB').tobytes(),image.tobytes())
            raw=(out/'live-materials.bin').read_bytes();h=struct.unpack_from('<8IQ',raw)
            self.assertEqual(h[:6],(0x31585453,1,1,1,3,3));self.assertEqual(h[8],fnv(raw[40:]))
            self.assertEqual(struct.unpack_from('<4I',raw,120),(0,0,0,3));self.assertEqual(struct.unpack_from('<3I',raw,136),(0,1,2))
            self.assertEqual((game/'ship.bmp').read_bytes(),original)
    def test_missing_image_has_no_fallback(self):
        with tempfile.TemporaryDirectory() as root:
            root=Path(root);out=root/'out';out.mkdir();packet,refs=packet_fixture()
            with self.assertRaisesRegex(ValueError,'Image file'):prepare(packet,refs,out,root)
            self.assertFalse((out/'live-materials.bin').exists())
    def test_unqualified_alpha_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            root=Path(root);out=root/'out';out.mkdir();Image.new('RGBA',(8,8),(10,20,30,100)).save(root/'alpha.png')
            packet,refs=packet_fixture();refs=json.loads(refs);refs['resources'][0]['filename']='alpha.png'
            with self.assertRaisesRegex(ValueError,'alpha path'):prepare(packet,json.dumps(refs).encode(),out,root)

if __name__=='__main__':unittest.main()
