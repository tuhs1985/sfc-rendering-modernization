import importlib.util
from pathlib import Path
import struct
import unittest

p=Path(__file__).resolve().parents[1]/'tools/scene_bridge/damage_mapping.py'
spec=importlib.util.spec_from_file_location('damage_mapping',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class DamageMappingTests(unittest.TestCase):
    def test_native_axis_selection_and_ties(self):
        point=(1,2,3)
        self.assertEqual(m.projected_uv(point,(1,0,0),.1875),(.875,1.0625))
        self.assertEqual(m.projected_uv(point,(0,-1,0),.1875),(.6875,1.0625))
        self.assertEqual(m.projected_uv(point,(0,0,1),.1875),(.6875,.875))
        self.assertEqual(m.projected_uv(point,(1,1,0),.1875),(.6875,.875))
    def test_span_branch(self):
        self.assertEqual(m.scale(7.5,0),.1875);self.assertAlmostEqual(m.scale(7.5001,0),.028125)
    def test_nonfinite_rejected(self):
        with self.assertRaises(ValueError):m.projected_uv((float('nan'),0,0),(0,0,1),1)
    def test_source_uv_and_normals_unchanged(self):
        source=[[i,0,0,0x3F800000,0,0,7] for i in range(3)];copy=[r[:] for r in source]
        out=m.corners([(0,0,0),(1,0,0),(0,1,0)],[(3,0,(0,0,1))],source,1,0)
        self.assertEqual(source,copy);self.assertEqual(out[1][:4],source[1][:4]);self.assertEqual(out[1][6],7)
        self.assertEqual(struct.unpack('<2f',struct.pack('<2I',*out[1][4:6])),(.6875,.5))
    def test_missing_corner_rejected(self):
        with self.assertRaises(ValueError):m.corners([(0,0,0)],[(3,1,(0,0,1))],[[0]*7]*3,1,0)

if __name__=='__main__':unittest.main()
