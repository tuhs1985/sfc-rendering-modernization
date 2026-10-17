import ctypes
import json
import math
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest
from live_bridge import Channel, Consumer, affine, qualify, mesh_content, SIZE, WORDS

ROOT=Path(__file__).resolve().parents[2]
CAPTURE=ROOT/'artifacts/m1/runs/20261016-171830-enabled'
GAME=Path('C:/Games/Taldren Software Inc/Starfleet Command Orion Pirates')


def words(values):return list(struct.unpack('<16I',struct.pack('<16f',*values)))+[0]


class LiveTests(unittest.TestCase):
    def sample(self,seq=1,owner=7,slot=0):
        r=[0]*48;r[:7]=[seq,owner,1,34,1,8,9];r[45]=slot
        r[8:25]=words([1,0,0,2,0,1,0,3,0,0,1,4,0,0,0,1]);return r

    def test_translation_rotation_and_origin(self):
        w=words([0,-1,0,12,1,0,0,23,0,0,1,34,0,0,0,1])
        matrix,t=affine(w,(10,20,30))
        p=(1,0,0,1)
        self.assertEqual(tuple(sum(p[i]*matrix[i][j] for i in range(4)) for j in range(4)),(2,4,4,1))
        self.assertEqual(t,(12,23,34))
        self.assertEqual(affine(w)[0][3],(0,0,0,1))
        w[0]=0x7fc00000
        with self.assertRaises(ValueError):affine(w)
        with self.assertRaises(ValueError):affine(words([2,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]))

    def test_lifetime_stale_pointer_reuse_and_bad_record(self):
        c=Consumer();assets={0:{'owner':7,'model':8,'source':9},1:{'owner':10,'model':8,'source':9}}
        self.assertIsNotNone(c.update(self.sample(),assets,0));self.assertFalse(c.fresh(1))
        bad=self.sample(2);bad[8]=0x7fc00000
        self.assertIsNone(c.update(bad,assets,1));self.assertEqual(c.rejected,1)
        retired=self.sample(3);retired[4]=2;c.update(retired,assets,1)
        self.assertIsNone(c.update(self.sample(4),assets,1))
        self.assertIsNotNone(c.update(self.sample(5,10,1),assets,1))
        self.assertEqual(c.origin,(2,3,4))
        self.assertIsNone(c.update(self.sample(6),assets,1))
        self.assertIsNone(c.update([1,2],assets,1))

    def test_actual_windows_channel_torn_bounds_wrong_session_and_disconnect(self):
        creator=Channel(create=True);reader=Channel(creator.name)
        try:
            self.assertEqual(reader.validate(),0)
            creator.write(256,struct.pack('<I',1));self.assertIsNone(reader.sample())
            creator.write(260,struct.pack('<96I',*(self.sample()+[0]*48)));creator.write(256,struct.pack('<I',2))
            self.assertEqual(reader.sample()[0],1)
            with self.assertRaises(ValueError):reader.write(0,b'x')
            with self.assertRaises(ValueError):creator.read(SIZE,1)
            with self.assertRaises(ValueError):Channel(creator.name,create=True)
            creator.write(12,struct.pack('<I',2));self.assertEqual(reader.validate(),2)
            creator.write(16,b'\0'*16)
            with self.assertRaises(ValueError):reader.validate()
        finally:reader.close();creator.close()

    def test_x86_worker_through_actual_mapping(self):
        binary=ROOT/'artifacts/m1/bin/m1_live_bridge_tests.exe'
        self.assertTrue(binary.is_file(),'Run native build before transport tests')
        c=Channel(create=True)
        try:
            with tempfile.TemporaryDirectory() as tmp:
                result=subprocess.run([str(binary),c.name,tmp],capture_output=True,timeout=10)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                self.assertEqual(c.validate(),2)
                self.assertEqual(c.sample()[4],2)
                report=json.loads((Path(tmp)/'LIVE-BRIDGE-001-worker.json').read_text())
                self.assertTrue(report['stopped']);self.assertFalse(report['io_failed'])
                self.assertTrue(1<=report['records']<=2700)
        finally:c.close()

    def test_actual_content_association_and_mismatch(self):
        packet=(CAPTURE/'MESH-EXPORT-001.bin').read_bytes();refs=(CAPTURE/'TEXTURE-EXPORT-001.json').read_bytes()
        result=qualify(packet,refs,CAPTURE,GAME)
        self.assertEqual(result['model_name'],'kff.mod')
        r=json.loads(refs);r['owner_epoch']+=1
        with self.assertRaises(ValueError):qualify(packet,json.dumps(r).encode(),CAPTURE,GAME)
        r=json.loads(refs);r['groups'][0]['primary']=r['groups'][1]['primary']
        with self.assertRaises(ValueError):qualify(packet,json.dumps(r).encode(),CAPTURE,GAME)
        wrong=bytearray(packet);wrong[256]^=1
        with self.assertRaises(ValueError):mesh_content(wrong)
        with self.assertRaises((ValueError,OSError)):qualify(packet,refs,CAPTURE,GAME/'missing')


if __name__=='__main__':unittest.main()
