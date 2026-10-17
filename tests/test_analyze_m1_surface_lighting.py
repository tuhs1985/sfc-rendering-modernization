import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('surface_analysis',Path(__file__).resolve().parents[1]/'tools/m1_component/analyze_m1_surface_lighting.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class SurfaceTests(unittest.TestCase):
    def fixture(self):
        phases=[dict(phase=i,observed=n,applied=n if i<3 else 0,parent=n if i<3 else 0,
                     received=2*n if i in (1,2) else 0,first_ms=first,last_ms=last)
                for i,n,first,last in [(0,1200,0,19990),(1,300,20010,24990),(2,900,25010,39990),(3,100,40010,50000)]]
        d=dict(enabled=True,attempted=True,started=True,failure=0,intact=True,pinned_until_exit=True,count=452,
               changed_vectors=1356,storage_bytes=332336,marker_ms=20000,normal_gap_ms=5000,altered_ms=15000,
               owner=1,thread=2,ship=3,visual=4,model=5,source=6,manager=7,original_list=8,neutral_list=9,altered_list=10,phases=phases)
        return dict(surface_lighting=d,hooks_restored=True,visual_tint=dict(restore_failed=0,active_scopes=0))
    def test_good_requires_visual_review_not_quality_pass(self):
        r=m.analyze(self.fixture());self.assertFalse(r['issues']);self.assertEqual(r['formal_m1'],'CONTINUES')
        self.assertFalse(r['quality_improvement_proven'])
    def test_guard_failures(self):
        for key,value in [('failure',9),('intact',False),('pinned_until_exit',False),('marker_ms',10000),
                          ('count',6370),('changed_vectors',0),('storage_bytes',2000000),('altered_list',9),('owner',0)]:
            with self.subTest(key=key):
                f=self.fixture();f['surface_lighting'][key]=value;self.assertTrue(m.analyze(f)['issues'])
    def test_partial_or_short_windows_rejected(self):
        for index,key,value in [(0,'last_ms',18000),(1,'applied',1),(2,'received',0),(2,'last_ms',30000),
                                (2,'parent',0),(3,'applied',1)]:
            with self.subTest(index=index,key=key):
                f=self.fixture();f['surface_lighting']['phases'][index][key]=value;self.assertTrue(m.analyze(f)['issues'])
    def test_source_lease_cleanup_required(self):
        for key in ('restore_failed','active_scopes'):
            f=self.fixture();f['visual_tint'][key]=1;self.assertTrue(m.analyze(f)['issues'])
