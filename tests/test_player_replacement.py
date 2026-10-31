import struct,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/remix_runtime'))
from player_replacement import summary,OFFSET

class ReplacementSummaryTests(unittest.TestCase):
    def channel(self,raw):
        class Channel:
            def read(self,offset,size):
                assert offset==OFFSET and size==4416
                return raw
        return Channel()

    def packet(self):
        raw=bytearray(4416)
        struct.pack_into('<8I',raw,0,0x31525053,1,4416,42,1,2,3,4)
        struct.pack_into('<10IQ',raw,72,1,8,9,10,11,12,13,14,15,16,1000)
        struct.pack_into('<11I',raw,4352,1,1,300,0,295,2,0,0,0,1,400)
        return raw

    def test_exact_native_layout_and_counters(self):
        result=summary(self.channel(self.packet()))
        self.assertEqual((result['owner'],result['revision'],result['epoch']),(9,10,14))
        self.assertEqual((result['suppressed'],result['committed'],result['native_frame']),(300,295,400))
        self.assertEqual(result['session'],[1,2,3,4])

    def test_wrong_version_or_shape_is_rejected(self):
        for offset,value in ((0,0),(4,3),(8,4400)):
            raw=self.packet();struct.pack_into('<I',raw,offset,value)
            with self.assertRaises(ValueError):summary(self.channel(raw))

    def test_incomplete_transfer_is_not_a_summary(self):
        with self.assertRaises(ValueError):summary(self.channel(self.packet()[:-1]))

    def test_v2_recovery_statistics_and_legacy_reading(self):
        raw=self.packet();struct.pack_into('<I',raw,4,2)
        struct.pack_into('<3I',raw,4396,4,9,2)
        result=summary(self.channel(raw))
        self.assertEqual((result['protocol'],result['rearmed'],result['native_presentations'],result['recovery_reason']),(2,4,9,2))
        self.assertEqual(summary(self.channel(self.packet()))['protocol'],1)

if __name__=='__main__':unittest.main()
