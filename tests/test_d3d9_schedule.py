from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/d3d9_proof'))
from analyze_schedule import assess


class ScheduleTests(unittest.TestCase):
    def rows(self):
        return [dict(sequence=i+1,source_frame=(1,2,3)[i%3],presents=24 if not i else 1,
            draw_present_us=300,output_gpu_us=3000,local_readback_us=0,peer_us=1000,
            scheduled_us=(i-1)*1000000//60 if i else -1,
            completed_us=(i-1)*1000000//60+5000 if i else -1) for i in range(120)]

    def test_known_deadline_counts(self):
        rows=self.rows();r=assess(rows,120);self.assertEqual(r['deadline_misses'],0);self.assertEqual(r['steady_frames'],119)
        rows[4]['completed_us']+=20000;r=assess(rows,120);self.assertEqual(r['deadline_misses'],1)

    def test_reject_sequence_missing_rows_and_wrong_clock(self):
        rows=self.rows()
        with self.assertRaises(ValueError):assess(rows[:-1],120)
        rows[1]['sequence']=3
        with self.assertRaises(ValueError):assess(rows,120)
        rows=self.rows();rows[1]['scheduled_us']=1
        with self.assertRaises(ValueError):assess(rows,120)

    def test_negative_cost_or_warm_present_cannot_be_steady_pass(self):
        rows=self.rows();rows[1]['peer_us']=-1
        with self.assertRaises(ValueError):assess(rows,120)
        rows=self.rows();rows[1]['presents']=24
        with self.assertRaises(ValueError):assess(rows,120)


if __name__=='__main__':unittest.main()
