import ctypes as C
import struct
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/d3d9_proof'))
from light_transport import initialize,read_native,publish_encoded,valid_header,RAW_OFFSET,RAW_MAGIC,RAW_BYTES,RAW_STRIDE,ENCODED_OFFSET,ENCODED_MAGIC,ENCODED_BYTES


class Channel:
    name='Local\\SFCBridge_00000001000000020000000300000004'
    def __init__(self):self.memory=C.create_string_buffer(16*1024*1024);self.view=C.addressof(self.memory)
    def write(self,offset,data):C.memmove(self.view+offset,data,len(data))
    def read(self,offset,size):return C.string_at(self.view+offset,size)


class SharedLightTests(unittest.TestCase):
    def test_complete_raw_snapshot_owner_time_and_collision(self):
        c=Channel();initialize(c);c.write(RAW_OFFSET+28,struct.pack('<I',77))
        cell=RAW_OFFSET+64+3*RAW_STRIDE;raw=bytearray(6156);struct.pack_into('<I',raw,32,3)
        c.write(cell,struct.pack('<2IQ',2,0,123)+raw)
        self.assertEqual(read_native(c,3,77),(bytes(raw),123))
        self.assertIsNone(read_native(c,35,77));self.assertIsNone(read_native(c,3,78))
        c.write(cell,struct.pack('<I',3));self.assertIsNone(read_native(c,3,77))

    def test_encoded_payload_preserves_capture_time_not_poll_time(self):
        c=Channel();initialize(c);publish_encoded(c,77,bytes(200),bytes(808),123)
        self.assertTrue(valid_header(c,ENCODED_OFFSET,ENCODED_MAGIC,ENCODED_BYTES,77))
        self.assertEqual(struct.unpack('<Q',c.read(ENCODED_OFFSET+72,8))[0],123)
        with self.assertRaises(ValueError):publish_encoded(c,77,bytes(201),bytes(808),123)
        c.write(ENCODED_OFFSET+32,struct.pack('<I',1))
        self.assertFalse(valid_header(c,ENCODED_OFFSET,ENCODED_MAGIC,ENCODED_BYTES,77))


if __name__=='__main__':unittest.main()
