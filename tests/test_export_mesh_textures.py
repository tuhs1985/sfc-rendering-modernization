import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools/m1_component'))
from PIL import Image
import export_mesh_textures as textures
from export_mesh_obj import export_obj
from test_analyze_mesh_export import packet, seal


class TextureRecoveryTests(unittest.TestCase):
    def fixture(self, root):
        capture, game = root/'capture', root/'game'
        capture.mkdir(); directory = game/'Assets/Models/test'; directory.mkdir(parents=True)
        raw = packet()
        struct.pack_into('<10I', raw, len(raw)-40, 255, 0x23, 0xffffffff, 0, 0, 0, 1, 10, 2, 20)
        seal(raw); h = struct.unpack_from('<64I', raw)
        (capture/'MESH-EXPORT-001.bin').write_bytes(raw)
        receipt = dict(schema='sfc.mesh.receipt.v1', status=1, complete=True, hooks_restored=True,
                       file_write_ok=True, attempts=1, owner_epoch=h[4], packet_bytes=h[2], packet_fnv1a=h[3])
        (capture/'MESH-EXPORT-001-receipt.json').write_text(json.dumps(receipt))
        resources = []
        for i, name in ((1, 'test_a'), (2, 'test_ai')):
            Image.new('RGB', (4, 4), (i*60, 80, 90)).save(directory/(name+'.bmp'))
            resources.append(dict(id=i, registry_object=1000+i, manager_entry=2000+i, surface_identity=3000+i,
                                  filename=f'Assets/Models/test/{name}.bmp', requested=name))
        refs = dict(schema='sfc.texture.references.v1', status=1, hooks_restored=True, packet_fnv1a=h[3],
                    owner_epoch=h[4], frame=h[6], model=h[10], source=h[12], model_filename='Assets/Models/test/test.mod',
                    textures_enabled=1,
                    groups=[dict(group=255, flags=0x23, primary=1, secondary=2, primary_name_offset=10, secondary_name_offset=20)],
                    resources=resources)
        (capture/'TEXTURE-EXPORT-001.json').write_text(json.dumps(refs))
        return capture, game, refs

    def test_roundtrip_originals_geometry_uvs_and_no_guessed_glow(self):
        with tempfile.TemporaryDirectory() as tmp:
            capture, game, refs = self.fixture(Path(tmp))
            raw = (capture/'MESH-EXPORT-001.bin').read_bytes()
            originals = {p: p.read_bytes() for p in game.rglob('*.bmp')}
            result = textures.recover(capture, game)
            self.assertTrue(result['primary_images_ready'])
            self.assertEqual(result['status'], 'PARTIAL')
            self.assertEqual(len(result['images']), 2)
            self.assertEqual(result['secondary_role'], 'UNPROVEN_NOT_APPLIED_AS_EMISSION')
            export_obj(capture/'MESH-EXPORT-001.bin', capture/'grey.obj', capture/'MESH-EXPORT-001-receipt.json')
            fields = lambda p: [s for s in p.read_text().splitlines() if s.startswith(('v ', 'vt ', 'vn ', 'f ', 'g ', 'usemtl '))]
            self.assertEqual(fields(capture/'grey.obj'), fields(capture/'textured/ship.obj'))
            mtl = (capture/'textured/ship.mtl').read_text()
            self.assertIn('map_Kd resource_0001.png', mtl)
            self.assertNotIn('map_Ke', mtl)
            self.assertEqual(raw, (capture/'MESH-EXPORT-001.bin').read_bytes())
            self.assertTrue(all(p.read_bytes() == data for p, data in originals.items()))
            with self.assertRaises(ValueError):
                textures.recover(capture, game)

    def test_cross_epoch_groups_duplicate_and_count_rejected(self):
        for change in ('epoch', 'group', 'duplicate', 'count'):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as tmp:
                capture, game, refs = self.fixture(Path(tmp))
                if change == 'epoch': refs['packet_fnv1a'] += 1
                if change == 'group': refs['groups'][0]['primary'] = 77
                if change == 'duplicate': refs['resources'][1]['id'] = 1
                if change == 'count': refs['resources'] *= 6
                (capture/'TEXTURE-EXPORT-001.json').write_text(json.dumps(refs))
                with self.assertRaises(ValueError): textures.recover(capture, game)

    def test_path_flag_is_provenance_not_permission_to_guess_emission(self):
        for flag in (None, 0, 1):
            with self.subTest(flag=flag), tempfile.TemporaryDirectory() as tmp:
                capture, game, refs = self.fixture(Path(tmp))
                if flag is not None:
                    refs['manager_multitexture_flag'] = flag
                    refs['manager_secondary_path_word'] = flag*0xffffffff
                    refs['manager_fallback_validation_mask'] = flag*3
                    refs['manager_previous_alpha_test_flag'] = flag
                (capture/'TEXTURE-EXPORT-001.json').write_text(json.dumps(refs))
                result = textures.recover(capture, game)
                self.assertTrue(result['primary_images_ready'])
                self.assertEqual(result['manager_multitexture_flag'], flag)
                self.assertEqual(result['manager_secondary_path_word'], None if flag is None else flag*0xffffffff)
                self.assertEqual(result['manager_fallback_validation_mask'], None if flag is None else flag*3)
                self.assertEqual(result['manager_previous_alpha_test_flag'], flag)
                self.assertEqual(result['secondary_role'], 'UNPROVEN_NOT_APPLIED_AS_EMISSION')
                self.assertNotIn('map_Ke', (capture/'textured/ship.mtl').read_text())

    def test_invalid_observed_path_flag_rejected(self):
        for flag in (True, -1, 256, '1'):
            with self.subTest(flag=flag), tempfile.TemporaryDirectory() as tmp:
                capture, game, refs = self.fixture(Path(tmp))
                refs['manager_multitexture_flag'] = flag
                (capture/'TEXTURE-EXPORT-001.json').write_text(json.dumps(refs))
                with self.assertRaises(ValueError): textures.recover(capture, game)

    def test_limits_missing_path_and_role_remain_partial(self):
        for problem in ('size', 'dimension', 'missing', 'traversal', 'requested'):
            with self.subTest(problem=problem), tempfile.TemporaryDirectory() as tmp:
                capture, game, refs = self.fixture(Path(tmp))
                if problem == 'dimension':
                    Image.new('RGB', (4097, 1)).save(game/'Assets/Models/test/test_a.bmp')
                if problem == 'missing': refs['resources'][0]['filename'] = 'Assets/Models/test/absent.bmp'
                if problem == 'traversal': refs['resources'][0]['filename'] = 'Assets/../outside.bmp'
                if problem == 'requested': refs['resources'][0]['requested'] = 'wrong'
                (capture/'TEXTURE-EXPORT-001.json').write_text(json.dumps(refs))
                with patch.object(textures, 'LIMIT', 140 if problem == 'size' else textures.LIMIT):
                    result = textures.recover(capture, game)
                self.assertFalse(result['primary_images_ready'])
                self.assertEqual(result['status'], 'PARTIAL')
                self.assertTrue(result['findings'])
                self.assertLessEqual(sum(p.stat().st_size for p in (capture/'textured').glob('*.png')), textures.LIMIT)

    def test_warning_and_lossless_decoding(self):
        with tempfile.TemporaryDirectory() as tmp:
            capture, game, refs = self.fixture(Path(tmp))
            with patch.object(textures, 'WARNING', 1): result = textures.recover(capture, game)
            self.assertTrue(result['size_warning'])
            with Image.open(capture/'textured/resource_0001.png') as image:
                self.assertEqual(image.getpixel((0, 0)), (60, 80, 90))

    def test_all_five_groups_and_ten_images(self):
        with tempfile.TemporaryDirectory() as tmp:
            capture, game, refs = self.fixture(Path(tmp))
            original = (capture/'MESH-EXPORT-001.bin').read_bytes()
            h = list(struct.unpack_from('<64I', original)); h[17:20] = [5, 15, 5]
            data = bytearray(struct.pack('<64I', *h)+original[256:292])
            for g in range(5):
                poly = list(struct.unpack_from('<9I', original, 292)); poly[1]=g; poly[6]=g*3
                data.extend(struct.pack('<9I', *poly))
            data.extend(original[328:412]*5)
            refs['groups']=[]; refs['resources']=[]
            for g in range(5):
                a, b = g*2+1, g*2+2
                data.extend(struct.pack('<10I', g, 0x23, 0xffffffff, 0, 0, 0, a, g*20, b, g*20+10))
                refs['groups'].append(dict(group=g, flags=0x23, primary=a, secondary=b,
                                           primary_name_offset=g*20, secondary_name_offset=g*20+10))
                for i in (a, b):
                    Image.new('RGB', (2, 2), (i*20, 80, 90)).save(game/f'Assets/Models/test/image_{i}.bmp')
                    refs['resources'].append(dict(id=i, registry_object=i+10, manager_entry=i+20,
                        surface_identity=i+30, filename=f'Assets/Models/test/image_{i}.bmp', requested=f'image_{i}'))
            seal(data); h=struct.unpack_from('<64I', data)
            refs['packet_fnv1a']=h[3]
            (capture/'MESH-EXPORT-001.bin').write_bytes(data)
            (capture/'TEXTURE-EXPORT-001.json').write_text(json.dumps(refs))
            receipt_path=capture/'MESH-EXPORT-001-receipt.json'
            receipt=json.loads(receipt_path.read_text());receipt.update(packet_bytes=h[2], packet_fnv1a=h[3])
            receipt_path.write_text(json.dumps(receipt))
            result=textures.recover(capture, game)
            self.assertTrue(result['primary_images_ready'], result['findings'])
            self.assertEqual(len(result['images']), 10)
            mtl=(capture/'textured/ship.mtl').read_text()
            for g in range(5):
                self.assertIn(f'newmtl source_{g:03d}', mtl)
                self.assertIn(f'map_Kd resource_{g*2+1:04d}.png', mtl)


if __name__ == '__main__':
    unittest.main()
