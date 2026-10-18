from pathlib import Path
import sys
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
from analyze_present_calibration import rasterize,interior,compare,native_depth_planes

class PresentProjectionTests(unittest.TestCase):
    def test_native_sampling_and_depth(self):
        tri=np.array([[0,0,.2],[8,0,.2],[0,8,.2]])
        z=rasterize(tri,(4,4))
        self.assertAlmostEqual(z[0,0],.2)
        self.assertTrue(np.isinf(z[3,3]))
        self.assertTrue(np.allclose(z[np.isfinite(z)],.2))
    def test_winding_independent_and_nearest(self):
        a=np.array([[0,0,.7],[8,0,.7],[0,8,.7]])
        b=a.copy();b[:,2]=.4
        forward=rasterize(a,(4,4));reverse=rasterize(a[::-1],(4,4))
        self.assertTrue(np.array_equal(np.isfinite(forward),np.isfinite(reverse)))
        self.assertTrue(np.allclose(forward[np.isfinite(forward)],reverse[np.isfinite(reverse)],atol=1e-14,rtol=0))
        self.assertAlmostEqual(rasterize(np.r_[a,b],(4,4))[0,0],.4)
    def test_linear_screen_z(self):
        z=rasterize([[0,0,0],[8,0,.8],[0,8,0]],(4,4))
        self.assertAlmostEqual(z[0,0],.05)
        self.assertAlmostEqual(z[0,1],.25)
    def test_bad_input(self):
        with self.assertRaises(ValueError):rasterize([[0,0,0]],(4,4))
        with self.assertRaises(ValueError):rasterize([[0,0,np.inf]]*3,(4,4))
    def test_interior_and_sample_interval(self):
        mask=interior(np.ones((5,5),bool));self.assertEqual(mask.sum(),9)
        depth=np.zeros((5,5,4));depth[:,:,1]=.2;depth[:,:,2]=.4
        good=compare(np.full((5,5),.3),depth,mask)
        self.assertEqual(good['fraction_within_2e_5'],1)
        self.assertEqual(compare(np.full((5,5),.5),depth,mask)['observed_closer'],9)
        self.assertEqual(compare(np.full((5,5),.1),depth,mask)['predicted_closer'],9)
    def test_depth_coefficients_without_pixel_fit(self):
        n,f=1.,30000.;a=-(f+n)/(f-n);b=-2*f*n/(f-n)
        p=[[1,0,0,0],[0,1,0,0],[0,0,a,b],[0,0,-1,0]]
        dn,df=native_depth_planes(p)
        self.assertAlmostEqual(dn,2*n*f/(n+f))
        for distance in (3,10,100,1000):
            self.assertAlmostEqual(-a+b/distance,df/(df-dn)-df*dn/((df-dn)*distance))
    def test_invalid_projection_rejected(self):
        with self.assertRaises(ValueError):native_depth_planes(np.eye(4))

if __name__=='__main__':unittest.main()
