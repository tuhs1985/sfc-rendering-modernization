import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('rejections',Path(__file__).resolve().parents[1]/
                                          'tools/m1_component/analyze_m1_rejections.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class Rejections(unittest.TestCase):
    def test_endurance_metadata_attribution(self):
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)
            (path/'M1-A-summary.json').write_text(json.dumps(self.fixture()))
            (path/'run-metadata.json').write_text(json.dumps({'probe_id':'M1-CLOSE-ENDURE-001'}))
            subprocess.run([sys.executable,module.__file__,str(path)],check=True,capture_output=True)
            self.assertEqual(json.loads((path/'M1-rejection-analysis.json').read_text())['probe_id'],
                             'M1-CLOSE-ENDURE-001')
    def fixture(self):
        s=[0,12,2,2]+[0]*12
        counts=[[[0]*13 for _ in range(4)] for _ in range(4)];counts[0][2][2]=1
        return {'rejected_semantics':1,'rejection_diagnostics':{
            'schema':'m1.rejections.v1','total':1,'signature_overflow':0,
            'example_omitted':0,'counts':counts,'examples':[s],
            'buckets':[{'count':1,'first':s,'last':s}]}}
    def test_valid_never_exonerates(self):
        self.assertFalse(module.analyze(self.fixture())['harmless_exception_confirmed'])
    def test_selected_review(self):
        f=self.fixture();f['rejection_diagnostics']['examples'][0][14]=1
        self.assertTrue(module.analyze(f)['issues'])
    def test_invalid(self):
        for key,value in [('total',2),('example_omitted',1),('counts',[]),('examples',[]),('schema','x')]:
            with self.subTest(key=key):
                f=copy.deepcopy(self.fixture());f['rejection_diagnostics'][key]=value
                with self.assertRaises(ValueError): module.analyze(f)
    def test_overflow_reported(self):
        f=self.fixture();d=f['rejection_diagnostics'];d['buckets']=[];d['signature_overflow']=1
        self.assertIn('signature_capacity_exceeded',module.analyze(f)['issues'])
    def test_bad_sample(self):
        f=self.fixture();f['rejection_diagnostics']['examples'][0][3]=0
        with self.assertRaises(ValueError): module.analyze(f)
