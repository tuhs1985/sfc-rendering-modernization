import pathlib
import sys
import unittest

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'tools/d3d9_proof'))
from analyze_delivery import assess


class DeliveryAnalysis(unittest.TestCase):
    def data(self):
        audit=dict(frame=10,owner=2,revision=3,status=2,input_sequence=7,present=20)
        row=dict(sequence=7,source_frame=10,owner=2,revision=3,offered_qpc=5,taken_qpc=8,
                 light_ready_qpc=9,completed_qpc=25,frequency=1000,output_sequence=1)
        return audit,row

    def test_late_render(self):
        a,r=self.data();out=assess([a],[r],[],[],1000)
        self.assertEqual(out['miss_attribution'],{'render_or_transfer_crossed_observer':1})
        self.assertEqual(out['timing']['missed']['completion_margin_ms']['p50'],-5)

    def test_queue_and_observer_receipt_race_distinct(self):
        a,r=self.data();r.update(taken_qpc=21,light_ready_qpc=22)
        self.assertIn('not_taken_until_after_observer',assess([a],[r],[],[],1000)['miss_attribution'])
        r.update(taken_qpc=8,light_ready_qpc=9,completed_qpc=19)
        self.assertIn('completed_by_observer_but_not_matched',assess([a],[r],[],[],1000)['miss_attribution'])

    def test_missing_and_invalid_identity(self):
        a,r=self.data()
        self.assertIn('no_retained_output_for_expected_source',assess([a],[],[],[],1000)['miss_attribution'])
        r['owner']=9
        with self.assertRaises(ValueError):assess([a],[r],[],[],1000)

    def test_status_five_excluded_and_gap_splits_streak(self):
        a,_=self.data();b={**a,'frame':12};c={**a,'frame':13,'status':5}
        out=assess([a,b,c],[],[],[],1000)
        self.assertEqual(out['missed_frame_streaks'],{'1':2})
        self.assertEqual(sum(out['miss_attribution'].values()),2)

    def test_render_bound_distinguishes_ack_ambiguity(self):
        a,r=self.data()
        t=dict(sequence=1,source_frame=10,draw_present_us=100,output_gpu_us=100,
               peer_us=100,copy_submit_us=1,render_ready_wait_us=99,postprocess_us=1)
        out=assess([a],[r],[t],[],1000)
        self.assertEqual(out['missed_output_deadline_bounds'],{'pre_peer_work_definitely_late':1})
        t['peer_us']=6000
        out=assess([a],[r],[t],[],1000)
        self.assertEqual(out['missed_output_deadline_bounds'],{'transfer_publication_or_ack_boundary_unresolved':1})

    def test_camera_hash_change_not_speed(self):
        a,r=self.data();a['status']=1
        b={**a,'frame':11,'input_sequence':8,'status':2}
        s1=(1,10,1,2,3,1,1,0,1,2,3,4,5,6,7)
        s2=(1,11,2,2,3,1,1,0,2,3,4,4,9,6,7)
        out=assess([a,b],[r],[],[s1,s2],1000)
        self.assertEqual(out['camera_hash_change_counts'],{'None_matched':1,'True_missed':1})
        self.assertEqual(out['after_first_match_counts'],{'matched':1,'missed':1})


if __name__=='__main__':unittest.main()
