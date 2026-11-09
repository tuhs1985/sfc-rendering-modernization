import struct
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/d3d9_proof'))
import output_target as target
from owner_rebind import fnv


class Channel:
    name='Local\\SFCBridge_'+'00000001000000020000000300000004'
    def __init__(self):
        raw=target.NOTICE.pack(target.MAGIC,1,64,123,1,2,3,4,999,3840,2160,1,2,0)
        raw=raw[:-8]+struct.pack('<Q',fnv(raw[:-8]))
        self.raw=bytearray(struct.pack('<i',2)+bytes(60)+raw)
    def read(self,offset,size):return bytes(self.raw[offset-target.OFFSET:offset-target.OFFSET+size])


class OutputTargetTests(unittest.TestCase):
    def test_dimensions_available_without_any_asset_fields(self):
        channel=Channel();value=target.read(channel,123)
        self.assertEqual((value['width'],value['height']),(3840,2160))
        self.assertEqual(value['target_generation'],2)
        self.assertNotIn('asset',value)

    def test_partial_wrong_process_session_and_tampered_notice_not_usable(self):
        channel=Channel();self.assertIsNone(target.read(channel,124))
        channel.name=channel.name[:-1]+'5';self.assertIsNone(target.read(channel,123))
        channel=Channel();channel.raw[0]=3;self.assertIsNone(target.read(channel,123))
        channel=Channel();channel.raw[-1]^=1;self.assertIsNone(target.read(channel,123))
        channel=Channel();calls=0;original=channel.read
        def torn(offset,size):
            nonlocal calls
            calls+=1
            return struct.pack('<i',4) if calls==3 else original(offset,size)
        channel.read=torn;self.assertIsNone(target.read(channel,123))
