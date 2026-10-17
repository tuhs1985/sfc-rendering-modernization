import importlib.util
import math
import json
from pathlib import Path
import struct
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('mesh_export', Path(__file__).resolve().parents[1] / 'tools/m1_component/analyze_mesh_export.py')
mesh = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mesh)


def packet(count=3):
    header = [0] * 64
    header[0:2] = [0x314D4653, 1]
    header[4:6] = [1, 2]
    header[8:13] = [100, 200, 300, 400, 500]
    header[13] = 0x0042E55D
    header[16:21] = [count, 1, count, 1, 1]
    positions = [(0., 0., 0.), (1., 0., 0.), (0., 1., 0.), (1., 1., 0.)][:count]
    poly = [count, 255, 0, 0, 0x3F800000, 0, 0, 123, 456]
    data = bytearray(struct.pack('<64I', *header))
    data.extend(b''.join(struct.pack('<3f', *p) for p in positions))
    data.extend(struct.pack('<9I', *poly))
    for i in range(count):
        data.extend(struct.pack('<HH5fI', i, 0, 0., 0., 2., float(i), -1., 0xF1234567))
    data.extend(struct.pack('<10I', 255, *([0] * 9)))
    return seal(data)


def seal(data):
    struct.pack_into('<I', data, 8, len(data))
    struct.pack_into('<I', data, 12, 0)
    struct.pack_into('<I', data, 12, mesh.fnv(data))
    return data


class MeshAnalysisTests(unittest.TestCase):
    def analyze(self, data):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'mesh.bin'
            path.write_bytes(data)
            return mesh.analyze(path)

    def test_portable_roundtrip(self):
        result = self.analyze(packet())
        self.assertEqual(result['polygons'], 1)
        self.assertEqual(result['uv_max'], [2., -1.])  # no clamp
        self.assertEqual(result['normal_length_range'], [2., 2.])  # no normalization
        self.assertEqual(result['nonunit_corner_vectors'], 3)
        self.assertEqual(result['face_geometric_alignment_range'], [1., 1.])
        self.assertEqual(result['source_polygon_counts'], {255: 1})

    def test_no_ngon_fan_assumption(self):
        result = self.analyze(packet(4))
        self.assertIn('Nontriangle topology', result['findings'][0])

    def test_corruption_truncation_and_limits(self):
        valid = packet()
        for data in (valid[:-1], valid + b'X', bytearray(b'X' * (mesh.FILE_LIMIT + 1))):
            with self.assertRaises(ValueError):
                self.analyze(data)
        bad = valid.copy()
        bad[-1] ^= 1
        with self.assertRaisesRegex(ValueError, 'checksum'):
            self.analyze(bad)

    def test_bad_topology_source_index_and_nan(self):
        original = packet()
        cases = ((256 + 36 + 24, 1),  # corner ordinal
                 (256 + 36 + 4, 0),  # source not present
                 (256 + 36 + 36, 3),  # vertex index
                 (256 + 36 + 36 + 16, 0x7FC00000))
        for offset, value in cases:
            bad = original.copy()
            struct.pack_into('<I', bad, offset, value)
            with self.assertRaises(ValueError):
                self.analyze(seal(bad))

    def test_degenerate_and_zero_vectors_reported(self):
        data = packet()
        struct.pack_into('<3f', data, 256 + 12, 0., 0., 0.)
        struct.pack_into('<3f', data, 256 + 36 + 36 + 4, 0., 0., 0.)
        result = self.analyze(seal(data))
        self.assertEqual(result['degenerate_triangles'], 1)
        self.assertEqual(result['zero_corner_vectors'], 1)

    def test_nonfinite_unused_position_is_not_referenced(self):
        # Four declared positions, three referenced corners: unused data retained.
        data = packet()
        data[256 + 36:256 + 36] = struct.pack('<3f', math.nan, 0., 0.)
        struct.pack_into('<I', data, 16 * 4, 4)
        result = self.analyze(seal(data))
        self.assertEqual(result['unused_positions'], 1)

    def test_receipt_correlates_capture_and_cleanup(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'mesh.bin'
            receipt = Path(directory) / 'receipt.json'
            data = packet()
            path.write_bytes(data)
            record = {'schema': 'sfc.mesh.receipt.v1', 'status': 1, 'complete': True,
                      'hooks_restored': True, 'file_write_ok': True, 'attempts': 1,
                      'owner_epoch': 1, 'packet_bytes': len(data),
                      'packet_fnv1a': struct.unpack_from('<I', data, 12)[0],
                      'capture_qpc_frequency': 10000, 'capture_qpc_ticks': [25, 0]}
            receipt.write_text(json.dumps(record))
            self.assertEqual(mesh.analyze(path, receipt)['capture_attempt_ms'], [2.5])
            for key in ('complete', 'hooks_restored', 'file_write_ok'):
                bad = dict(record, **{key: False})
                receipt.write_text(json.dumps(bad))
                with self.assertRaises(ValueError):
                    mesh.analyze(path, receipt)
            receipt.write_bytes(b'x' * 65537)
            with self.assertRaises(ValueError):
                mesh.analyze(path, receipt)


if __name__ == '__main__':
    unittest.main()
