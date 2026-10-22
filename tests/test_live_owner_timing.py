from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
import live_owner_timing as live

SESSION='Local\\SFCBridge_00000001000000020000000300000004'


class LiveOwnerTimingTests(unittest.TestCase):
    def raw(self,status=1):
        header=live.HEADER.pack(live.MAGIC,1,live.STORE_BYTES,1,2,3,4,77,7|(1<<32),1,5,0,9,1,0,0,1,0,0,bytes(48))
        a=[5,7,1,status,150,100,140,1,1,11,11,5,7,1,0,bytes(8)]
        return header+bytes(2688-live.HEADER.size)+live.AUDIT.pack(*a),a

    def test_layout_and_exact_identity(self):
        raw,_=self.raw();h,rows=live.parse_audits(raw,SESSION,77)
        self.assertEqual(live.HEADER.size,128);self.assertEqual(live.AUDIT.size,96)
        self.assertEqual(rows[0]['status'],1)

    def test_wrong_frame_hash_sequence_not_claimed_match(self):
        raw,a=self.raw()
        for index in (7,9,11,12,13):
            bad=a.copy();bad[index]+=1
            with self.assertRaises(ValueError):live.parse_audits(raw[:-96]+live.AUDIT.pack(*bad),SESSION,77)

    def test_late_and_ineligible_are_preserved(self):
        for status in (2,3,4,5,6):
            raw,_=self.raw(status);self.assertEqual(live.parse_audits(raw,SESSION,77)[1][0]['status'],status)

    def test_wrong_process_session_and_future_match(self):
        raw,a=self.raw()
        with self.assertRaises(ValueError):live.parse_audits(raw,SESSION,78)
        with self.assertRaises(ValueError):live.parse_audits(raw,SESSION[:-1]+'5',77)
        a[6]=151
        with self.assertRaises(ValueError):live.parse_audits(raw[:-96]+live.AUDIT.pack(*a),SESSION,77)

    def test_initialization_before_hooks(self):
        class Fake:
            name=SESSION
            def write(self,offset,data):self.offset=offset;self.data=data
        channel=Fake();live.initialize(channel)
        self.assertEqual(channel.offset,10*1024*1024);self.assertEqual(len(channel.data),live.STORE_BYTES)
        self.assertEqual(live.HEADER.unpack_from(channel.data)[3:7],(1,2,3,4))

    def test_startup_frame_zero_is_not_prepared_or_rendered(self):
        class Channel:
            name=SESSION
            def write(self,offset,data):pass
            def sample_owner(self,index):
                row=[0]*96;row[1]=7;row[4]=1;row[7]=1;row[48]=1;return row
        class Receiver:
            channel=Channel()
        relay=live.Relay(Path('artifacts'),Receiver(),Path('.'))
        relay.poll(77)
        self.assertFalse(relay.attempted);self.assertIsNone(relay.process)


if __name__=='__main__':unittest.main()
