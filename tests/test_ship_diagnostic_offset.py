import copy
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
from run_coverage_probe import diagnostic_offset

class OffsetTests(unittest.TestCase):
    def fixture(self,folder,rotated=False):
        points=[[-.5,-.5,0],[.5,-.5,0],[0,.5,0]]
        raw=struct.pack('<4I4f',0x53464347,1,3,3,0,0,0,1)
        raw+=b''.join(struct.pack('<8f',*p,0,0,1,0,0) for p in points)
        (folder/'coverage-mesh.bin').write_bytes(raw)
        model=np.eye(4);model[2,3]=10
        proj=np.array([[128,0,128,0],[0,-128,128,0],[0,0,1,0],[0,0,1,0]],dtype=float)
        if rotated:proj[0,:2]=[0,128];proj[1,:2]=[128,0]
        right=[0,1,0] if rotated else [1,0,0]
        camera={'native_model':model.tolist(),'native_composed':(proj@model).tolist(),'viewport':[0,0,256,256],
                'sdk_parameters':[0,0,0,*right,0,1,0,0,0,1,90,1,1,100]}
        return camera,raw
    def test_world_offset_and_projection_not_pixel_shift(self):
        for rotated in (False,True):
            with tempfile.TemporaryDirectory() as tmp:
                folder=Path(tmp);camera,raw=self.fixture(folder,rotated);before=copy.deepcopy(camera)
                result=diagnostic_offset(camera,folder)
                self.assertEqual(camera,before);self.assertEqual((folder/'coverage-mesh.bin').read_bytes(),raw)
                model=np.array(result['rendered_native_model']);original=np.array(result['original_native_model'])
                np.testing.assert_array_equal(model[:3,:3],original[:3,:3])
                self.assertAlmostEqual(result['world_translation'][1 if rotated else 0],-4,places=5)
                old=np.array(result['original_native_composed']);new=np.array(result['native_composed'])
                for p in ([0,0,0,1],[.3,.1,0,1],[-.2,.2,.5,1]):
                    a=old@p;b=new@p
                    self.assertAlmostEqual(b[1]/b[3],a[1]/a[3],places=6)
                    self.assertAlmostEqual(b[2]/b[3],a[2]/a[3],places=6)
                    self.assertLess(b[0]/b[3],a[0]/a[3])
                a=old@[0,0,0,1];b=new@[0,0,0,1]
                self.assertAlmostEqual((b[0]/b[3]-a[0]/a[3])/256,-.2,places=6)
    def test_bad_camera_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp);camera,_=self.fixture(folder);camera['sdk_parameters'][3]=2
            with self.assertRaisesRegex(ValueError,'basis'):diagnostic_offset(camera,folder)
    def test_clipping_is_not_silently_repaired(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp);camera,_=self.fixture(folder);camera['viewport'][2]=8
            with self.assertRaisesRegex(ValueError,'clip'):diagnostic_offset(camera,folder)

if __name__=='__main__':unittest.main()
