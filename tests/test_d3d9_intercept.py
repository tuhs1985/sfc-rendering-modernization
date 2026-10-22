from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/d3d9_proof'))
from inspect_intercept import match_corners


class InterceptComparisonTests(unittest.TestCase):
    def face(self):
        return [[(0,0,0,0,0,1,0,.079149998),(1,0,0,0,0,1,1,1),(0,1,0,0,0,1,0,0)]]

    def test_raw_uv_and_cyclic_winding(self):
        f=self.face();actual=[[f[0][2],f[0][0],f[0][1]]]
        flip,error=match_corners(actual,f)
        self.assertFalse(flip);self.assertEqual(error,0)

    def test_export_flip_with_float_boundary(self):
        f=self.face();actual=[[(*v[:7],1-v[7]) for v in reversed(f[0])]]
        actual[0][2]=(*actual[0][2][:7],.92085)
        flip,error=match_corners(actual,f)
        self.assertTrue(flip);self.assertLess(error,1e-6)

    def test_missing_and_duplicate_faces_reject(self):
        f=self.face();self.assertIsNone(match_corners([],f));self.assertIsNone(match_corners(f+f,f))

    def test_changed_geometry_normal_uv_reject(self):
        for index in (0,3,6):
            f=self.face();actual=[[list(v) for v in f[0]]];actual[0][0][index]+=.01
            with self.subTest(index=index):self.assertIsNone(match_corners(actual,f))


if __name__=='__main__':unittest.main()
