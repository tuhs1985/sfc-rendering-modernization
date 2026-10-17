import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1] / 'tools/m1_component'
sys.path.insert(0, str(TOOLS))
import export_mesh_obj as exporter
from test_analyze_mesh_export import packet, seal


class ObjExportTests(unittest.TestCase):
    def test_attributes_face_order_material_and_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, target = root / 'input.bin', root / 'ship.obj'
            original = packet()
            source.write_bytes(original)
            result = exporter.export_obj(source, target)
            lines = target.read_text().splitlines()
            self.assertEqual([s for s in lines if s.startswith('v ')], ['v 0 0 0', 'v 1 0 0', 'v 0 1 0'])
            self.assertEqual([s for s in lines if s.startswith('vn ')], ['vn 0 0 1'] * 3)
            self.assertIn('vt 2 -1', lines)  # neither clamp nor V flip
            self.assertIn('f 1/1/1 2/2/2 3/3/3', lines)
            self.assertIn('g source_255', lines)
            self.assertIn('usemtl source_255', lines)
            self.assertIn('newmtl source_255', target.with_suffix('.mtl').read_text())
            self.assertEqual(source.read_bytes(), original)
            manifest = json.loads(target.with_suffix('.obj-manifest.json').read_text())
            self.assertEqual(manifest, result)
            self.assertEqual(result['polygon_mapping'], [[0, 255, 1, 0]])
            self.assertEqual(result['consumer_status'], 'REMIX_NOT_TESTED')
            self.assertFalse(result['cleanup_receipt_validated'])

    def test_uv_and_vector_seams_not_welded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = packet()
            # Repeat position zero but give its corner another UV and vector;
            # other vertices keep triangle nondegenerate for both polygons.
            header = list(struct.unpack_from('<64I', data))
            original_poly = bytes(data[292:328])
            original_corners = bytes(data[328:412])
            poly = bytearray(original_poly)
            struct.pack_into('<I', poly, 24, 3)
            more = bytearray(original_corners)
            struct.pack_into('<f', more, 16, 5.)
            struct.pack_into('<f', more, 12, -2.)
            header[17:19] = [2, 6]
            data = bytearray(struct.pack('<64I', *header)) + data[256:292] + original_poly + poly + original_corners + more + data[412:]
            source, target = root / 'input.bin', root / 'ship.obj'
            source.write_bytes(seal(data))
            result = exporter.export_obj(source, target)
            lines = target.read_text().splitlines()
            self.assertEqual(result['vertices'], 6)
            self.assertEqual([s for s in lines if s.startswith('v ')].count('v 0 0 0'), 2)
            self.assertIn('vt 5 -1', lines)
            self.assertIn('vn 0 0 -1', lines)
            self.assertIn('f 4/4/4 5/5/5 6/6/6', lines)

    def test_refuses_unqualified_or_invalid_inputs_before_output(self):
        for bad in (packet(4), packet()[:-1]):
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                source, target = root / 'input.bin', root / 'ship.obj'
                source.write_bytes(bad)
                with self.assertRaises(ValueError):
                    exporter.export_obj(source, target)
                self.assertFalse(target.exists())

    def test_refuses_overwrite_and_size_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, target = root / 'input.bin', root / 'ship.obj'
            source.write_bytes(packet())
            with patch.object(exporter, 'OBJ_LIMIT', 1):
                with self.assertRaisesRegex(ValueError, 'size limit'):
                    exporter.export_obj(source, target)
            self.assertFalse(target.exists())
            with patch.object(exporter, 'SIDECAR_LIMIT', 1):
                with self.assertRaisesRegex(ValueError, 'size limit'):
                    exporter.export_obj(source, target)
            target.with_suffix('.mtl').write_text('preserve')
            with self.assertRaisesRegex(ValueError, 'overwrite'):
                exporter.export_obj(source, target)
            self.assertEqual(target.with_suffix('.mtl').read_text(), 'preserve')
            self.assertFalse(target.exists())

    def test_zero_vectors_not_silently_repaired(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, target = root / 'input.bin', root / 'ship.obj'
            data = packet()
            struct.pack_into('<3f', data, 332, 0., 0., 0.)
            source.write_bytes(seal(data))
            with self.assertRaisesRegex(ValueError, 'Zero vectors'):
                exporter.export_obj(source, target)
            self.assertFalse(target.exists())

    def test_maximum_triangles_and_source_groups_remain_bounded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = packet()
            header = list(struct.unpack_from('<64I', original))
            header[17:20] = [512, 1536, 256]
            polygons = bytearray()
            for p in range(512):
                poly = bytearray(original[292:328])
                struct.pack_into('<I', poly, 4, p % 256)
                struct.pack_into('<I', poly, 24, p * 3)
                polygons.extend(poly)
            data = bytearray(struct.pack('<64I', *header)) + original[256:292] + polygons
            data.extend(original[328:412] * 512)
            for group in range(256):
                data.extend(struct.pack('<10I', group, *([0] * 9)))
            source, target = root / 'input.bin', root / 'ship.obj'
            source.write_bytes(seal(data))
            result = exporter.export_obj(source, target)
            self.assertEqual(result['triangles'], 512)
            self.assertEqual(result['vertices'], 1536)
            self.assertLess(target.stat().st_size, exporter.OBJ_LIMIT)
            self.assertLess(target.with_suffix('.mtl').stat().st_size, exporter.SIDECAR_LIMIT)
            self.assertLess(target.with_suffix('.obj-manifest.json').stat().st_size, exporter.SIDECAR_LIMIT)


if __name__ == '__main__':
    unittest.main()
