import importlib.util
import unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('copy_analysis',Path(__file__).resolve().parents[1]/
                                          'tools/m1_component/analyze_m1_private_copy.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class CopyTests(unittest.TestCase):
    def fixture(self):
        d=dict(enabled=True,attempted=True,applied=1,consumed=1,parent_return=1,failure=0,intact=True,
               before_hash=17,after_hash=17,pinned_until_exit=True,count=452,copied_polygons=64,
               payload_bytes=20224,slot_bytes=21000,owner=1,thread=2,ship=3,visual=4,model=5,manager=6,
               original_list=7,copy_list=8,source=9,elapsed_ms=20500)
        return dict(private_copy=d,hooks_restored=True)
    def test_good_not_formal_pass(self):
        a=m.analyze(self.fixture());self.assertFalse(a['issues']);self.assertEqual(a['formal_m1'],'CONTINUES')
    def test_failures(self):
        for k,v in [('applied',2),('consumed',0),('intact',False),('after_hash',0),('slot_bytes',99999),('parent_return',0)]:
            with self.subTest(key=k):
                f=self.fixture();f['private_copy'][k]=v;self.assertTrue(m.analyze(f)['issues'])
    def repeated_fixture(self):
        f=self.fixture();d=f['private_copy']
        records=[dict(slot=i,elapsed_ms=20500+1000*i,frame=1200+i*60,applied=1,consumed=2,parent_return=1,
                      failure=0,copy_list=8+32768*i,count=452,copied_polygons=64,payload_bytes=8976,
                      before_hash=17+i,after_hash=17+i,intact=True) for i in range(32)]
        f['repeated_private_copy']=dict(enabled=True,limit=32,interval_ms=1000,attempts=32,
                                       storage_bytes=657000,halted=False,receipt_mismatch=0,records=records)
        return f
    def test_repeated_fresh_copies_not_reuse_or_formal_pass(self):
        a=m.analyze(self.repeated_fixture());self.assertFalse(a['issues'])
        self.assertEqual(a['probe_id'],'M1-C01-RT-008')
        self.assertFalse(a['reusable_buffer_lifetime_qualified']);self.assertEqual(a['formal_m1'],'CONTINUES')
    def test_repeated_failures(self):
        for key,value in [('copy_list',8),('elapsed_ms',20501),('intact',False),('consumed',0),
                          ('parent_return',0),('failure',2),('payload_bytes',30000),('count',999),('slot',10),('frame',1200)]:
            with self.subTest(key=key):
                f=self.repeated_fixture();f['repeated_private_copy']['records'][1][key]=value
                self.assertTrue(m.analyze(f)['issues'])
        for key,value in [('attempts',31),('storage_bytes',1000000),('halted',True),('receipt_mismatch',1),('limit',64)]:
            with self.subTest(key=key):
                f=self.repeated_fixture();f['repeated_private_copy'][key]=value;self.assertTrue(m.analyze(f)['issues'])
    def test_short_repeat_is_additional_evidence_not_success(self):
        f=self.repeated_fixture();f['repeated_private_copy']['records'].pop();f['repeated_private_copy']['attempts']=31
        self.assertEqual(m.analyze(f)['status'],'ADDITIONAL_BOUNDED_EVIDENCE_REQUIRED')
    def epoch_fixture(self):
        f=self.repeated_fixture();repeat=f['repeated_private_copy']
        repeat.update(epoch_requalification_enabled=True,epoch_requalifications=2,epoch_limit=2)
        for i,r in enumerate(repeat['records']):
            r.update(owner=1 if i<8 else (2 if i<16 else 3),requalified_from=0,retired_ms=0,
                     retired_frame=0,qualification_ms=0,qualification_frame=0,qualification_frames=0)
            if i in (8,16):
                prev=repeat['records'][i-1]
                r.update(requalified_from=prev['owner'],retired_ms=prev['elapsed_ms']+200,
                         retired_frame=prev['frame']+1,qualification_ms=prev['elapsed_ms']+250,
                         qualification_frame=prev['frame']+2,qualification_frames=10)
        return f
    def test_independent_epochs(self):
        a=m.analyze(self.epoch_fixture());self.assertFalse(a['issues'])
        self.assertEqual(a['probe_id'],'M1-C01-RT-009');self.assertEqual(a['formal_m1'],'CONTINUES')
    def test_epoch_missing_or_fabricated_proof(self):
        for key,value in [('requalified_from',99),('retired_ms',0),('retired_frame',0),
                          ('qualification_ms',28499),('qualification_frames',2),('qualification_frames',999),
                          ('qualification_frame',1700),('owner',1)]:
            with self.subTest(key=key):
                f=self.epoch_fixture();f['repeated_private_copy']['records'][8][key]=value
                self.assertTrue(m.analyze(f)['issues'])
        f=self.epoch_fixture();f['repeated_private_copy']['epoch_requalifications']=1
        self.assertTrue(m.analyze(f)['issues'])
    def test_owner_merge_and_spurious_transition(self):
        f=self.epoch_fixture();f['repeated_private_copy']['records'][16]['owner']=1
        self.assertTrue(m.analyze(f)['issues'])
        f=self.epoch_fixture();f['repeated_private_copy']['records'][2]['requalified_from']=1
        self.assertTrue(m.analyze(f)['issues'])
    def test_requalification_mode_requires_an_actual_transition(self):
        f=self.epoch_fixture()
        for r in f['repeated_private_copy']['records']:
            r.update(owner=1,requalified_from=0,retired_ms=0,retired_frame=0,
                     qualification_ms=0,qualification_frame=0,qualification_frames=0)
        f['repeated_private_copy']['epoch_requalifications']=0
        self.assertTrue(m.analyze(f)['issues'])
