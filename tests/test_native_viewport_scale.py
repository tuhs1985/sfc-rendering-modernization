from pathlib import Path
import struct
import sys
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/d3d9_proof'))
from analyze_viewport_scale import compare


class NativeViewportScale(unittest.TestCase):
    def fixture(self):
        row=[0]*96
        model=np.eye(4);view=np.eye(4);view[2,3]=-5
        projection=np.array([[1.,0,0,0],[0,1,0,0],[0,0,-1.1,-1],[0,0,-1,0]])
        vp=np.array([[860.,0,0,1060],[0,-510,0,540],[0,0,1,0],[0,0,0,1]])
        for start,m,flags in ((8,model,256),(49,view,256),(66,projection,0),(25,vp@projection@view@model,0)):
            row[start:start+17]=[*struct.unpack('<16I',struct.pack('<16f',*m.flat)),flags]
        row[83:87]=struct.unpack('<4I',struct.pack('<4f',200,30,1720,1020))
        return row,np.array([[-1.,-1,0],[1,0,1],[0,1,-1]])

    def test_native_agreement_not_model_rescale(self):
        row,p=self.fixture();out=compare(row,p)
        self.assertLess(out['max_corrected_projection_error_pixels'],.001)
        self.assertGreater(out['max_old_placement_error_pixels'],10)
        self.assertAlmostEqual(out['old_relative_magnification'][0],1920/1720)
        self.assertEqual(out['max_camera_left_depth_change'],0)

    def test_different_native_matrix_is_not_false_pass(self):
        row,p=self.fixture();row[28]=struct.unpack('<I',struct.pack('<f',1200))[0]
        self.assertGreater(compare(row,p)['max_corrected_projection_error_pixels'],1)

    def test_invalid_viewport_rejected(self):
        row,p=self.fixture();row[85]=0
        with self.assertRaises(ValueError):compare(row,p)


if __name__=='__main__':unittest.main()
