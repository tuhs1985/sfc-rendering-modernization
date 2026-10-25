"""Offline review helpers; no game, GPU or capture source changes."""
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('review',Path(__file__).resolve().parents[1]/'analyze_render_families.py')
review=importlib.util.module_from_spec(spec);spec.loader.exec_module(review)

class ReviewTests(unittest.TestCase):
    def context(self):
        return dict(device=1,depth=8,pipeline={512:11,1024:12},dynamic={1000:4})

    def test_static_state_and_dynamic_override(self):
        types={'depth_stencil_state':11,'blend_state':9}
        pipes={(1,11,11):(0,0,0,0,1,0),(1,12,9):(0,0,0,0,1,1,1)}
        c=self.context()
        self.assertEqual(review.effective_state(c,pipes,types),(1,1,0,1,1,1,4))
        c['dynamic']={7:0,14:1,27:0,19:6,20:7,1000:2}
        self.assertEqual(review.effective_state(c,pipes,types),(1,0,1,0,6,7,2))

    def test_retired_pipeline_cannot_rebind_recycled_handle(self):
        c=self.context();other=self.context();other['device']=2
        contexts={(1,100):c,(2,100):other}
        pipes={(1,11,11):(),(2,11,11):()}
        review.retire_pipeline(1,11,pipes,contexts)
        self.assertNotIn(512,c['pipeline']);self.assertEqual(other['pipeline'][512],11)
        self.assertNotIn((1,11,11),pipes);self.assertIn((2,11,11),pipes)
        pipes[1,11,11]=(0,0,0,0,1,1)
        self.assertIsNone(review.effective_state(c,pipes,{'depth_stencil_state':11,'blend_state':9})[1])

    def test_unknown_state_not_assumed_enabled(self):
        self.assertEqual(review.effective_state(self.context(),{}, {'depth_stencil_state':11,'blend_state':9}),(1,None,None,None,None,None,4))

    def test_origins_are_not_owner_names(self):
        self.assertIn('NOT_PRODUCER',review.caller_kind((0x006A88E7,)))
        self.assertIn('NOT_PRODUCER',review.caller_kind((0x0069EC3E,)))
        self.assertEqual(review.caller_kind((0x006A84DF,)),'SURFACE_LOCK_OR_FLIP_CONTEXT')
        self.assertIn('UNRESOLVED',review.caller_kind((0x0041043B,)))

if __name__=='__main__':unittest.main()
