from pathlib import Path
import struct
import tempfile
import unittest
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/remix_runtime'))
import present_calibration as pc

class CalibrationTests(unittest.TestCase):
    def setUp(self):
        self.session='Local\\SFCBridge_'+'a'*32
        self.s=[0x31504353,1,pc.SIZE,40,41,2,9,9,123,456]+[0]*6
        self.h=[0x314c4143,1,pc.SIZE-128,9]+[0xaaaaaaaa]*4+[1,0,0,0]
        self.rows=[[0]*96 for _ in range(32)]
        self.rows[0][1:8]=[7,9,10,1,99,98,1];self.rows[0][47:49]=[456,1]
        self.depth=dict(qpc=40,present_frame=41,resource_epoch=2)
    def read(self):
        raw=struct.pack('<16Q12I',*self.s,*self.h)+b''.join(struct.pack('<96I',*r) for r in self.rows)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'semantic-0.bin';p.write_bytes(raw)
            return pc.read_semantic(p,self.depth,self.session,123)
    def test_valid(self):self.assertEqual(self.read()['owners'][0][1],7)
    def test_wrong_gpu_pair(self):
        self.s[4]+=1
        with self.assertRaises(ValueError):self.read()
    def test_stale_semantic(self):
        self.rows[0][2]-=1
        with self.assertRaises(ValueError):self.read()
    def test_wrong_thread(self):
        self.rows[0][47]+=1
        with self.assertRaises(ValueError):self.read()
    def test_session(self):
        self.h[4]=0
        with self.assertRaises(ValueError):self.read()
    def test_reserved(self):
        self.s[-1]=1
        with self.assertRaises(ValueError):self.read()
    def test_ambiguous(self):
        self.rows[0][4]=3
        with self.assertRaises(ValueError):self.read()
    def test_nonfinite(self):
        self.rows[0][8]=0x7f800000
        with self.assertRaises(ValueError):self.read()
    def test_duplicate_owner(self):
        self.rows[1]=self.rows[0].copy();self.rows[1][45]=1;self.h[8]=2
        with self.assertRaises(ValueError):self.read()

if __name__=='__main__':unittest.main()
