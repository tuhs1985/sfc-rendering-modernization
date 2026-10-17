import struct
import unittest
from live_camera import camera_state,multiply


def words(m,flag):return list(struct.unpack('<16I',struct.pack('<16f',*(v for row in m for v in row))))+[flag<<8]


def fixture():
    model=[[0,-1,0,4],[1,0,0,5],[0,0,1,0],[0,0,0,1]]
    view=[[1,0,0,0],[0,1,0,0],[0,0,1,-20],[0,0,0,1]]
    p=[[2,0,.12,0],[0,3.2,-.08,0],[0,0,-1.002002,-2.002002],[0,0,-1,0]]
    s=[[512,0,0,712],[0,-320,0,320],[0,0,1,0],[0,0,0,1]]
    r=[0]*96;r[:7]=[1,1,1,34,1,2,3]
    r[8:25]=words(model,1);r[25:42]=words(multiply(multiply(multiply(s,p),view),model),0)
    r[48]=1;r[49:66]=words(view,1);r[66:83]=words(p,0)
    r[83:89]=struct.unpack('<6I',struct.pack('<6f',200,0,1024,640,512,320))
    return r


class LiveCameraTests(unittest.TestCase):
    def test_offset_viewport_camera_origin_and_projection(self):
        s=camera_state(fixture(),(4,5,0),[(0,0,0),(1,2,3),(-2,-1,1)])
        self.assertEqual(s['viewport'],[200,0,1024,640])
        self.assertEqual(s['camera_transform'][3],(-400,-500,2000,1))
        self.assertAlmostEqual(s['horizontal_offset'],1.2,places=5)
        self.assertAlmostEqual(s['vertical_offset'],-.5,places=5)
        self.assertLess(s['native_composition_pixel_error'],.001)
        self.assertLess(s['near'],s['far'])

    def test_mismatched_camera_or_viewport_refused(self):
        for index,value in ((83,struct.unpack('<I',struct.pack('<f',100))[0]),
                            (52,struct.unpack('<I',struct.pack('<f',1))[0]),(48,0),(42,1)):
            r=fixture();r[index]=value
            with self.assertRaises(ValueError):camera_state(r,(0,0,0),[(0,0,0),(1,1,1)])

    def test_orthographic_nonfinite_and_wrong_aspect_refused(self):
        for index,value in ((80,0),(66,0x7fc00000),(70,0x3f800000),(85,0x3f800000)):
            r=fixture();r[index]=value
            with self.assertRaises(ValueError):camera_state(r,(0,0,0),[(0,0,0)])


if __name__=='__main__':unittest.main()
