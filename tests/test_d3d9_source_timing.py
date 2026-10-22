from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
from source_timing import HEADER,RECORD,MAGIC,STORE_BYTES,CAPACITY,decode

SESSION='Local\\SFCBridge_00000001000000020000000300000004'


class SourceTimingTests(unittest.TestCase):
    def packet(self):
        h=[MAGIC,1,STORE_BYTES,CAPACITY,77,9,2,0,2,0,0,0,1000,1,2,3,4,0,0,0,0,bytes(40)]
        a=[1,11,1,4,1,1,9,0,100,110,150,123,234,99,98]
        b=a.copy();b[0]=2;b[2]=2;b[10]=160
        return h,a,b

    def raw(self,h,a,b):return HEADER.pack(*h)+RECORD.pack(*a)+RECORD.pack(*b)

    def test_same_frame_pair_and_signed_callback_order(self):
        h,a,b=self.packet();r=decode(self.raw(h,a,b),SESSION,77)
        self.assertEqual(r['exact_frame_owner_pairs'],1);self.assertEqual(r['pose_camera_changed_between_stages'],0)
        self.assertEqual(r['overlay_minus_present_ms']['p50'],10)
        a[10]=170;r=decode(self.raw(h,a,b),SESSION,77);self.assertEqual(r['overlay_minus_present_ms']['p50'],-10)

    def test_frame_change_not_joined_by_nearest_time(self):
        h,a,b=self.packet();b[1]=12;r=decode(self.raw(h,a,b),SESSION,77)
        self.assertEqual(r['exact_frame_owner_pairs'],0);self.assertEqual(r['unpaired_or_repeated_frame_groups'],2)

    def test_changed_camera_is_explicit(self):
        h,a,b=self.packet();b[12]+=1;r=decode(self.raw(h,a,b),SESSION,77)
        self.assertEqual(r['pose_camera_changed_between_stages'],1)

    def test_reject_bad_identity_clock_count(self):
        h,a,b=self.packet()
        with self.assertRaises(ValueError):decode(self.raw(h,a,b),SESSION,78)
        a[9]=151
        with self.assertRaises(ValueError):decode(self.raw(h,a,b),SESSION,77)
        h,a,b=self.packet();h[6]=CAPACITY+1
        with self.assertRaises(ValueError):decode(self.raw(h,a,b),SESSION,77)
        h,a,b=self.packet();h[13]=5
        with self.assertRaises(ValueError):decode(self.raw(h,a,b),SESSION,77)

    def test_saturation_is_partial_not_silently_passed(self):
        h,a,b=self.packet();h[7]=1;r=decode(self.raw(h,a,b),SESSION,77)
        self.assertEqual(r['result'],'SOURCE_TIMING_PARTIAL')


if __name__=='__main__':unittest.main()
