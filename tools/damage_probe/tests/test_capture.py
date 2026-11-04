import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('damage_capture',Path(__file__).resolve().parents[1]/'damage_capture.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)

def mesh():
    h=[0]*32;h[:3]=[0x444D5031,1,128+36+28+84];h[4:13]=[200,1,300,400,100,1,3,1,3];h[15:17]=[99,100]
    raw=bytearray(struct.pack('<32I',*h)+struct.pack('<9f',0,0,0,1,0,0,0,1,0)+struct.pack('<7I',3,0,0,0,0,0,0))
    for i in range(3):raw+=struct.pack('<I5fI',i,0,0,1,.25,.75,0)
    struct.pack_into('<I',raw,12,c.fnv(raw));return raw

class DamageCaptureTests(unittest.TestCase):
    def mapping(self,raw):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'map.bin';p.write_bytes(raw);return c.mapping(p)
    def test_exact_secondary_mapping(self):
        r=self.mapping(mesh());self.assertEqual((r['positions'],r['polygons'],r['corners']),(3,1,3));self.assertEqual((r['primary_id'],r['companion_id']),(99,100));self.assertFalse(r['uv_modified'])
    def test_corrupt_checksum(self):
        raw=mesh();raw[-1]^=1
        with self.assertRaisesRegex(ValueError,'checksum'):self.mapping(raw)
    def altered(self,offset,value):
        raw=mesh();struct.pack_into('<I',raw,offset,value);struct.pack_into('<I',raw,12,0);struct.pack_into('<I',raw,12,c.fnv(raw));return raw
    def test_bad_index(self):
        with self.assertRaisesRegex(ValueError,'index'):self.mapping(self.altered(128+36+28,3))
    def test_nonfinite_uv(self):
        with self.assertRaisesRegex(ValueError,'finite'):self.mapping(self.altered(128+36+28+16,0x7FC00000))
    def test_material_group_not_assumed(self):
        with self.assertRaisesRegex(ValueError,'group'):self.mapping(self.altered(128+36+4,1))
    def test_native_corner_pointer_not_portable(self):
        with self.assertRaisesRegex(ValueError,'ordinal'):self.mapping(self.altered(128+36+24,0x12340000))
    def test_limit(self):
        with self.assertRaisesRegex(ValueError,'counts'):self.mapping(self.altered(10*4,65537))
    def test_short_file(self):
        with self.assertRaisesRegex(ValueError,'size'):self.mapping(b'abc')
    def test_reserved(self):
        with self.assertRaisesRegex(ValueError,'reserved'):self.mapping(self.altered(20*4,1))
    def trace(self,rows,mapping=False):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'damage.bin';h=c.Header();h.magic=0x454D4131;h.version=1;h.recordBytes=512;h.headerBytes=128;h.frequency=1000;h.startQpc=100;h.endQpc=10000;h.fileBytes=128+len(rows)*512;h.hardBytes=c.HARD;h.warningBytes=c.HARD//2;h.durationMs=90000;h.status=3;h.reason=3;h.written=len(rows)
            with path.open('wb') as f:
                f.write(bytes(h))
                for seq,(kind,owner,a) in enumerate(rows,1):f.write(c.RECORD.pack(seq,100+seq,1,0,kind,7,owner,200,300,256,0,0x42E626,*a,b'\0'*256,*([0]*8)))
            if mapping:(path.parent/(path.name+'.mapping-1.bin')).write_bytes(mesh())
            return c.analyze(path)
    def rows(self):
        identity=[1,1]+[0]*38;passed=identity.copy();passed[5]=400;passed[13]=99;passed[15]=100
        receipt=identity.copy();receipt[2:4]=[1,1]
        stopped=[0,0,10,0]+[0]*36
        return [(88,100,identity),(101,100,passed),(102,100,receipt),(93,0,[0]*40),(94,0,stopped)]
    def test_complete_fixture_join(self):
        self.assertFalse(self.trace(self.rows(),True)['issues'])
    def test_missing_mapping_partial(self):
        self.assertIn('mapping_file_receipt_mismatch',self.trace(self.rows())['issues'])
    def test_recycled_owner_rejected(self):
        rows=self.rows();rows.insert(1,(89,100,[1,1]+[0]*38));self.assertIn('damage_identity',self.trace(rows,True)['issues'])
    def test_resource_mismatch_partial(self):
        rows=self.rows();rows[1][2][13]=77;self.assertIn('mapping_material_join',self.trace(rows,True)['issues'])
    def test_cleanup_required(self):
        rows=self.rows();rows[-1][2][2]=9;self.assertIn('cleanup_unconfirmed',self.trace(rows,True)['issues'])

if __name__=='__main__':unittest.main()
