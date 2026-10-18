from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
import inspect_broad_depth as inspect
import test_broad_capture as fixture

class DepthInspectionTests(unittest.TestCase):
    def analyze(self,events):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'broad.bin'
            path.write_bytes(fixture.BroadTests().trace(events))
            return inspect.inspect(path)
    def events(self):
        return [(3,100,1,[3,0x30,0,0,0,1920,1080,1,1,39,8]),
                (5,201,1,[100,192,6,41]),(5,200,1,[100,48,6,40]),
                (10,10,1,[1,200,300]),(12,10,1,[300,1]),
                (10,10,1,[1,0,300]),(22,10,1,[20]),(18,20,1,[99,400])]
    def test_transient_depth_and_related_read_view(self):
        r=self.analyze(self.events());row=r['depth_paths'][0]
        self.assertEqual(row['resource_descriptor']['samples'],8)
        self.assertEqual({x['format'] for x in row['related_views']},{40,41})
        self.assertEqual(r['present']['depth_unbound'],1)
        self.assertEqual(r['present']['latest_depth_draw_then_unbind_before_present'],1)
        self.assertEqual(row['dynamic_depth_states'][0]['enable_write_compare'],(None,None,None))
    def test_stale_draw_not_counted_in_next_frame(self):
        r=self.analyze(self.events()+[(22,10,1,[20]),(18,20,1,[99,400])])
        self.assertEqual(r['present']['depth_unbound'],2)
        self.assertEqual(r['present']['latest_depth_draw_then_unbind_before_present'],1)
        self.assertIsNone(r['sample_presentations'][1]['last_depth_draw'])
    def test_queue_not_guessed(self):
        r=self.analyze(self.events()[:-2]+[(18,20,1,[99,400])])
        self.assertEqual(r['present']['unmapped_context'],1)
    def test_copy_to_implicit_backbuffer_stays_unknown_descriptor(self):
        r=self.analyze(self.events()[:-1]+[(15,10,1,[100,400]),self.events()[-1]])
        self.assertTrue(r['transfers'][0]['dest_is_presented_backbuffer'])
        self.assertIsNone(r['transfers'][0]['dest_descriptor'])
    def test_explicit_states_distinguished_from_unobserved(self):
        events=self.events();events[4:4]=[(21,10,1,[7,1]),(21,10,1,[14,0]),(21,10,1,[23,4])]
        row=self.analyze(events)['depth_paths'][0]
        self.assertEqual(row['dynamic_depth_states'][0]['enable_write_compare'],(1,0,4))
    def test_device_end_cannot_reuse_prior_frame_depth(self):
        events=self.events()[:5]+[(2,1,1,[]),(1,1,1,[]),(10,10,1,[1,0,300]),(22,10,1,[20]),(18,20,1,[99,400])]
        r=self.analyze(events)
        self.assertNotIn('latest_depth_draw_then_unbind_before_present',r['present'])

if __name__=='__main__':unittest.main()
