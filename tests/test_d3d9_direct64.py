from pathlib import Path
import struct
import sys
import tempfile
import unittest
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/d3d9_proof'))
from analyze_direct64 import raw32,overlap
from run_offline import oracle
from synthetic import prepare


class Direct64OutputTests(unittest.TestCase):
    def test_raw32_roundtrip_and_rejections(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'image.raw32';path.write_bytes(struct.pack('<2I',2,1)+bytes(8))
            self.assertEqual(raw32(path),(2,1,bytes(8)))
            for raw in (b'',struct.pack('<2I',0,1),struct.pack('<2I',2,1)+bytes(7),struct.pack('<2I',1921,1)+bytes(4)):
                path.write_bytes(raw)
                with self.assertRaises(ValueError):raw32(path)

    def test_known_projection_sample_centers_and_depth(self):
        with tempfile.TemporaryDirectory() as directory:
            path=prepare(Path(directory)/'known')
            legacy=oracle(path,0,960,540);ray=oracle(path,0,960,540,viewport_mode='full_frustum',pixel_center=.5)
            self.assertFalse(np.array_equal(legacy,ray))
            self.assertEqual(int(ray.sum()),5832)
            depth=oracle(path,0,960,540,viewport_mode='full_frustum',pixel_center=.5,return_depth=True)
            self.assertTrue(np.allclose(depth[ray],.9,atol=1e-6));self.assertTrue(np.isinf(depth[~ray]).all())

    def test_unknown_conventions_reject(self):
        with tempfile.TemporaryDirectory() as directory:
            path=prepare(Path(directory)/'known')
            with self.assertRaises(ValueError):oracle(path,0,960,540,viewport_mode='guessed')
            with self.assertRaises(ValueError):oracle(path,0,960,540,pixel_center=.3)

    def test_empty_coverage_cannot_match(self):
        empty=np.zeros((4,4),bool);expected=empty.copy();expected[1,1]=True
        result=overlap(empty,expected);self.assertEqual(result['iou'],0);self.assertEqual(result['missing_1px'],1)


if __name__=='__main__':unittest.main()
