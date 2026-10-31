import struct,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
import native_cohort as n

class CohortTests(unittest.TestCase):
    def raw(self):
        b=bytearray(n.SIZE);struct.pack_into('<16I',b,0,n.MAGIC,1,n.SIZE,42,1,2,3,4,200,400,5,0,0,0,0,0)
        struct.pack_into('<8I',b,5440,7,3,11,12,100,200,2,99)
        struct.pack_into('<8I',b,5472,8,4,11,12,100,200,3,99)
        return b
    def test_distinct_owners_shared_geometry(self):
        r=n.decode(self.raw());self.assertEqual(len(r['owners']),2);self.assertEqual(r['owners'][0]['model'],r['owners'][1]['model']);self.assertNotEqual(r['owners'][0]['owner'],r['owners'][1]['owner'])
    def test_malformed(self):
        with self.assertRaises(ValueError):n.decode(self.raw()[:-1])
        b=self.raw();b[0]=0
        with self.assertRaises(ValueError):n.decode(b)
    def test_scope_and_counts(self):
        r=n.decode(self.raw());self.assertEqual(r['session'],[1,2,3,4]);self.assertEqual(r['inserted'],200);self.assertEqual(r['suppressed'],400)

if __name__=='__main__':unittest.main()
