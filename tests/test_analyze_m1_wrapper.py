import importlib.util
import unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('wrapper',Path(__file__).resolve().parents[1]/
                                          'tools/m1_component/analyze_m1_wrapper.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class WrapperTests(unittest.TestCase):
    def fixture(self):
        return {'wrapper_observation':{'schema':'m1.wrapper.v1','enabled':True,'total':1,
            'outcomes':[0,1,0,0,0,0,0,0],'parent_closed':1,'example_omitted':0,
            'samples':[[0,1,1,2,0x0042e55d,1,2,3,4,5,452,1234,1,452,1234]]}}
    def test_valid_not_lifetime_proof(self):
        a=m.analyze(self.fixture());self.assertEqual(a['primary'],1)
        self.assertFalse(a['pointer_nonretention_proven'])
    def test_mismatch(self):
        f=self.fixture();f['wrapper_observation']['samples'][0][11]=0
        with self.assertRaises(ValueError):m.analyze(f)
    def test_count_mismatch(self):
        f=self.fixture();f['wrapper_observation']['total']=2
        with self.assertRaises(ValueError):m.analyze(f)
    def test_unclosed_parent(self):
        f=self.fixture();f['wrapper_observation']['parent_closed']=0
        self.assertIn('some_parent_returns_unobserved',m.analyze(f)['issues'])
