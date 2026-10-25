import struct,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from analyze_native_survey import known_light_fields,class_name

class Fake:
    def __init__(self):
        self.data={0x1004:struct.pack('<I',0x2000),0xffc:struct.pack('<I',0x3000),0x3000:struct.pack('<5I',0,0,0,0x4000,0x5000),0x4008:b'.?AVtFx_Test@@\0'+b'\0'*114}
    def read(self,a,n):return self.data[a][:n]

class NativeReviewTests(unittest.TestCase):
    def test_qualified_rtti(self):self.assertEqual(class_name(Fake(),0x1000,0x2000)['native_class'],'tFx_Test')
    def test_target_mismatch(self):
        with self.assertRaises(ValueError):class_name(Fake(),0x1000,0x2222)
    def test_unknown_tail_is_not_decoded_as_float(self):
        r=known_light_fields([5]+[0]*10+[0xffffffff]*5)
        self.assertIsNotNone(r);self.assertEqual(r['unknown_tail_words'],[0xffffffff]*5)
    def test_nonfinite_known_field(self):self.assertIsNone(known_light_fields([5,0x7fc00000]+[0]*14))

if __name__=='__main__':unittest.main()
