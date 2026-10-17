import struct
import unittest
from base_mip_diagnostic import base_only


class BaseMipTests(unittest.TestCase):
    def test_preserves_payload_and_clears_only_mip_header_fields(self):
        raw=bytearray(87556);raw[:4]=b'DDS ';raw[84:88]=b'DX10'
        for offset,value in ((12,256),(16,256),(28,9),(128,98),(140,1),(8,0xA1007),(108,0x401008)):
            struct.pack_into('<I',raw,offset,value)
        result=base_only(raw)
        self.assertEqual(len(result),65684)
        self.assertEqual(result[148:],raw[148:148+65536])
        self.assertEqual(struct.unpack_from('<I',result,28)[0],1)
        self.assertEqual(struct.unpack_from('<I',result,108)[0],0x1000)

    def test_unqualified_or_truncated_layout_refused(self):
        with self.assertRaises(ValueError):base_only(b'DDS ')
