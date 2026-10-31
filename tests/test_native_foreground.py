import sys,struct,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
import native_foreground_qualification as wire


class NativeForegroundReceipt(unittest.TestCase):
    def packet(self,*,ack=1,bytes_used=1015808):
        raw=bytearray(wire.BYTES)
        struct.pack_into('<8I',raw,0,0x31464753,1,wire.BYTES,42,1,2,3,4)
        struct.pack_into('<8I',raw,32,9,100,2,120,110,bytes_used,0,ack)
        return bytes(raw)

    def save(self,raw,folder):
        class Channel:
            def read(self,offset,size):
                assert offset==wire.OFFSET and size==wire.BYTES
                return raw
        return wire.save(Channel(),folder)

    def test_worker_ack_newer_than_last_presentation_preserves_raw_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            raw=self.packet();result=self.save(raw,folder)
            self.assertEqual(result['last_presentation_flags'],9)
            self.assertEqual(result['flags'],24)
            self.assertEqual((Path(folder)/'NATIVE-FOREGROUND-001.bin').read_bytes(),raw)

    def test_failed_teardown_is_not_hidden_by_old_render_stamp(self):
        with tempfile.TemporaryDirectory() as folder:
            result=self.save(self.packet(ack=2),folder)
            self.assertTrue(result['flags']&2)
            self.assertNotEqual(result['hooks_restored'],1)

    def test_retained_byte_cap(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):self.save(self.packet(bytes_used=32*1024*1024+1),folder)

    def test_uninitialized_source_is_not_success(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):self.save(bytes(wire.BYTES),folder)


if __name__=='__main__':unittest.main()
