import importlib.util
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/m1_component'))
import analyze_m1_corner_math as m

class MathTests(unittest.TestCase):
    def test_rotation_and_reverse(self):
        r=[[0,-1,0],[1,0,0],[0,0,1]]
        self.assertEqual(m.mv(r,[2,3,4]),[-3,2,4])
        self.assertEqual(m.mv(m.transpose(r),[-3,2,4]),[2,3,4])
        self.assertEqual(m.determinant(r),1)
    def test_scale_not_inverse(self):
        r=[[2,0,0],[0,1,0],[0,0,1]]
        self.assertNotEqual(m.mv(m.transpose(r),m.mv(r,[1,0,0])),[1,0,0])
    def test_winding_and_degenerate(self):
        self.assertEqual(m.cosine(m.cross([1,0,0],[0,1,0]),[0,0,1]),1)
        self.assertIsNone(m.cosine([0,0,0],[1,0,0]))
    def test_layout_metadata_excluded(self):
        bits=[0x3f800000,0,0,0x40000000,0,0x3f800000,0,0x40400000,
              0,0,0x3f800000,0x40800000,0,0,0,0x3f800000,0xffffffff]
        r,t=m.matrix(bits)
        self.assertEqual(t,[2,3,4]);self.assertEqual(m.determinant(r),1)
