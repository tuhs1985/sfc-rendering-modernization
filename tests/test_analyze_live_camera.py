import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/m1_component'))
from analyze_live_camera import multiply, inverse, project, recover, inspect, native_matrix


def bits(matrix,flag):
    return list(struct.unpack('<16I',struct.pack('<16f',*(x for row in matrix for x in row))))+[flag<<8]


def fixture():
    view=[[0,1,0,-3],[-1,0,0,2],[0,0,1,-20],[0,0,0,1]]
    pixel_projection=[[900,0,-500,0],[0,-900,-320,0],[0,0,-1.1,-2],[0,0,-1,0]]
    model=[[0,-1,0,4],[1,0,0,5],[0,0,1,1],[0,0,0,1]]
    composed=multiply(multiply(pixel_projection,view),model)
    row=[0]*48;row[:7]=[1,2,3,34,1,4,5];row[8:25]=bits(model,1);row[25:42]=bits(composed,0)
    return row,model,view,pixel_projection


class CameraTests(unittest.TestCase):
    def test_known_camera_and_object_separation(self):
        row,model,view,projection=fixture();r=recover(row)
        expected=multiply(projection,view)
        self.assertLess(max(abs(r['combined_world_to_screen_homogeneous'][i][j]-expected[i][j]) for i in range(4) for j in range(4)),1e-5)
        for p in ([0,0,0],[1,2,3],[-3,-2,1]):
            world=[sum(model[i][j]*p[j] for j in range(3))+model[i][3] for i in range(3)]
            a=project(native_matrix(row[25:42]),p);b=project(r['combined_world_to_screen_homogeneous'],world)
            self.assertLess(max(abs(x-y) for x,y in zip(a,b)),1e-5)
        self.assertEqual(r['principal_point_pixels'],[500,320])
        self.assertEqual(r['focal_magnitudes_pixels'],[900,900])
        self.assertLess(r['factorization_max_error'],1e-5)
        for a,b in zip(r['camera_center_native'],[2,3,20]):self.assertAlmostEqual(a,b)

    def test_native_affine_metadata_overrides_stored_fourth_row(self):
        r,_,_,_=fixture();r[20:24]=bits([[2,3,4,5]]*4,0)[:4]
        self.assertEqual(native_matrix(r[8:25])[3],[0,0,0,1])
        self.assertEqual(recover(r)['principal_point_pixels'],[500,320])

    def test_invalid_inputs_and_projection_plane(self):
        r,_,_,_=fixture()
        for index,value in ((42,1),(8,0x7fc00000),(24,0x200)):
            bad=r.copy();bad[index]=value
            with self.assertRaises(ValueError):recover(bad)
        with self.assertRaises(ValueError):inverse([[1,1],[1,1]])
        with self.assertRaises(ValueError):project([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,0]],[1,2,3])

    def test_bounded_read_only_report_and_exclusions(self):
        r,_,_,_=fixture()
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'updates.jsonl';bad=r.copy();bad[0]=2;bad[42]=1
            data=(json.dumps(r)+'\n'+json.dumps(bad)+'\n').encode();p.write_bytes(data)
            out=inspect(p);self.assertEqual(out['records'],1);self.assertEqual(len(out['excluded']),1)
            self.assertEqual(p.read_bytes(),data)
            p.write_text(json.dumps(r)+'\n'+json.dumps(r))
            with self.assertRaises(ValueError):inspect(p)


if __name__=='__main__':unittest.main()
