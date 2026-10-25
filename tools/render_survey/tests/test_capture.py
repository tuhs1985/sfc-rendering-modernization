import ctypes as C
import json
from pathlib import Path
import sys,tempfile,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from survey_capture import Header,RECORD,HARD,analyze,validate

class CaptureTests(unittest.TestCase):
    def trace(self,root,rows,*,dropped=0,reason=1):
        h=Header();h.magic=0x53525631;h.version=2;h.recordBytes=h.headerBytes=128
        h.status=3;h.reason=reason;h.frequency=1000;h.gateQpc=100;h.durationMs=90000;h.hardBytes=HARD;h.dropped=dropped;h.written=len(rows);h.fileBytes=128+128*len(rows)
        data=bytes(h)
        for i,(event,obj,args) in enumerate(rows,1):data+=RECORD.pack(i,100+i,event,7,obj,1,*list(args),*([0]*(11-len(args))))
        p=Path(root)/'survey.bin';p.write_bytes(data);return p
    def test_unknown_family_no_semantic_invention(self):
        with tempfile.TemporaryDirectory() as root:
            p=self.trace(root,[(11,8,[3,1,0,0])]);r=analyze(p)
            self.assertEqual(r['families'][0]['owner'],'UNKNOWN');self.assertIn('UNCLASSIFIED',r['families'][0]['classification']);self.assertEqual(r['counts']['draw'],1)
    def test_view_and_resource_reuse_are_distinct(self):
        with tempfile.TemporaryDirectory() as root:
            p=self.trace(root,[(3,20,[0]),(5,30,[20]),(10,8,[1,30]),(11,8,[3,1]),(6,30,[]),(4,20,[]),(3,20,[0]),(5,30,[20]),(11,8,[3,1])]);r=analyze(p)
            self.assertEqual(len(r['families']),2);self.assertNotEqual(r['families'][0]['depth'][1],r['families'][1]['depth'][1])
    def test_command_reset_discards_bindings(self):
        with tempfile.TemporaryDirectory() as root:
            p=self.trace(root,[(10,8,[1,30]),(11,8,[3,1]),(9,8,[]),(11,8,[3,1])]);r=analyze(p)
            self.assertEqual(len(r['families']),2);self.assertEqual(r['families'][1]['depth'][0],0)
    def test_retired_view_cannot_rebind_itself_by_pointer_reuse(self):
        with tempfile.TemporaryDirectory() as root:
            p=self.trace(root,[(3,20,[0]),(5,30,[20]),(10,8,[1,30]),(11,8,[3,1]),(6,30,[]),(5,30,[20]),(11,8,[3,1])]);r=analyze(p)
            self.assertEqual(r['families'][1]['depth'][0],0)
    def test_drop_and_cap_never_complete(self):
        with tempfile.TemporaryDirectory() as root:
            self.assertEqual(analyze(self.trace(root,[],dropped=1))['result'],'PARTIAL')
            self.assertEqual(analyze(self.trace(root,[],reason=2))['result'],'PARTIAL')
    def test_origin_join_is_exact_and_owner_unknown(self):
        with tempfile.TemporaryDirectory() as root:
            p=self.trace(root,[(11,8,[3,1]),(31,8,[1,0,1,0x401234]),(32,8,[1,1,0,0,20])])
            Path(str(p)+'.modules.jsonl').write_text(json.dumps(dict(qpc=1,base=0x400000,bytes=0x500000,path='C:/test/StarFleetOP.exe'))+'\n')
            r=analyze(p);origin=r['families'][0]['origin_samples'][0]
            self.assertTrue(origin['complete']);self.assertEqual(origin['modules'][0]['offset'],0x1234);self.assertTrue(origin['modules'][0]['engine']);self.assertEqual(origin['upstream_engine_owner'],'UNRESOLVED')
    def test_constants_do_not_read_or_require_payload(self):
        with tempfile.TemporaryDirectory() as root:
            p=self.trace(root,[(34,8,[2,0,1,0,256]),(11,8,[3,1])]);r=analyze(p)
            self.assertEqual(r['origin_stats']['constant_ranges_no_payload'],1)
    def test_schema_and_sequence_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            p=self.trace(root,[(99,8,[])])
            with self.assertRaises(ValueError):analyze(p)
            p=self.trace(root,[]);raw=bytearray(p.read_bytes());raw[0]=0;p.write_bytes(raw)
            with self.assertRaises(ValueError):analyze(p)
    def test_two_gib_total_and_old_header_supported(self):
        self.assertEqual(HARD+32*1024**2,2*1024**3)
        h=Header();h.magic=0x53525631;h.version=1;h.recordBytes=h.headerBytes=128;h.durationMs=90000;h.frequency=1000
        for value in (256*1024**2,HARD):h.hardBytes=value;validate(h)
        h.hardBytes=HARD+128
        with self.assertRaises(ValueError):validate(h)
    def test_native_light_fragments_and_census_not_owner_claim(self):
        with tempfile.TemporaryDirectory() as root:
            rows=[(36,900,[1,2,1,1,1,1]),(35,900,[1,2,0,5,0,0,0,1,2,3,4]),(35,900,[1,2,8,5,6,7,8,9,10,11,12]),(37,123,[2,900,800,700,0,0,1]),(38,900,[2,1,0,0,0])]
            r=analyze(self.trace(root,rows));lights=r['native']['lights']
            self.assertEqual(lights['stats']['complete_records'],1);self.assertEqual(lights['latest'][0]['native_type'],5)
            self.assertEqual(lights['latest_controls'][0]['enabled'],1);self.assertEqual(len(r['native']['effect_types']),1)
            self.assertEqual(r['result'],'METADATA_COMPLETE_SEMANTIC_CLASSIFICATION_PENDING')
    def test_native_missing_fragment_and_read_fault_partial(self):
        with tempfile.TemporaryDirectory() as root:
            r=analyze(self.trace(root,[(35,900,[1,2,0,0,0,0,0,0,0,0,0])]))
            self.assertEqual(r['result'],'PARTIAL');self.assertEqual(r['native']['lights']['incomplete_fragments'],1)
            r=analyze(self.trace(root,[(38,900,[1,0,1,0,0])]))
            self.assertEqual(r['result'],'PARTIAL')
    def test_native_malformed_fragment_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(ValueError):analyze(self.trace(root,[(35,900,[1,64,0,0,0,0,0,0,0,0,0])]))
    def test_completed_origin_samples_not_retained_unbounded(self):
        with tempfile.TemporaryDirectory() as root:
            rows=[]
            for _ in range(5000):
                parent=len(rows)+1;rows.extend([(11,8,[3,1]),(31,8,[parent,0,1,0x401234])])
            r=analyze(self.trace(root,rows))
            self.assertEqual(r['analysis_overflow'],0);self.assertEqual(r['origin_stats']['complete_origin_samples'],5000)

if __name__=='__main__':unittest.main()
