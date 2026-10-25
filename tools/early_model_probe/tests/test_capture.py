import importlib.util
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('early_capture',Path(__file__).resolve().parents[1]/'capture.py')
capture=importlib.util.module_from_spec(spec);spec.loader.exec_module(capture)

def row(kind,*,token=0,parent=0,owner=100,visual=200,mesh=0,flags=0,data=None,name=''):
    a=[0]*40;a[0]=1;a[1]=1;a[10]=300;a[15]=0x33330000;a[18]=0x11110000
    if data:
        for i,v in data.items():a[i]=v
    return dict(kind=kind,token=token,parent=parent,owner=owner,visual=visual,mesh=mesh,flags=flags,a=a,name=name)

def trace_rows():
    return [row(88),row(80,token=1,name='ship.mod'),row(82,token=2,parent=1,name='ship.mod'),
        row(84,token=3,parent=2),row(85,token=3,parent=2,data={2:1}),row(83,token=2,parent=1,data={23:1}),
        row(86,token=1,data={23:200}),row(81,token=1),row(91),row(87,mesh=300),
        row(93,data={0:0,1:0,2:0}),row(94,data={0:0,1:0,2:9,3:0})]

class EarlyCaptureTests(unittest.TestCase):
    def review(self,rows,*,dropped=0,version=1,reason=3):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'early.bin';h=capture.Header();h.magic=capture.MAGIC;h.version=version;h.recordBytes=512;h.headerBytes=128
            h.status=3;h.reason=reason;h.frequency=1000;h.startQpc=100;h.endQpc=10000;h.hardBytes=capture.HARD;h.warningBytes=capture.HARD//2;h.durationMs=90000;h.written=len(rows);h.fileBytes=128+512*len(rows);h.dropped=dropped
            with path.open('wb') as f:
                f.write(bytes(h))
                for seq,r in enumerate(rows,1):
                    f.write(capture.RECORD.pack(seq,100+seq,r['token'],r['parent'],r['kind'],7,r['owner'],r['visual'],r['mesh'],r['flags'],0,0x42FDD5,*r['a'],r['name'].encode().ljust(256,b'\0'),*([0]*8)))
            return capture.analyze(path)
    def test_named_request_completion_owner_draw_join(self):
        d=self.review(trace_rows());self.assertEqual(d['result'],'EARLY_NATIVE_MODEL_TIMING_OBSERVED');self.assertEqual(d['joins'][0]['model_name'],'ship.mod');self.assertEqual(d['joins'][0]['ready_to_first_draw_ms'],4)
        self.assertEqual(d['joins'][0]['position_pointer'],0x33330000)
    def test_retired_owner_never_joins_by_pointer(self):
        rows=trace_rows();rows.insert(9,row(89));d=self.review(rows)
        self.assertFalse(d['joins']);self.assertIn('first_draw_without_live_qualification',d['issues'])
    def test_retired_asset_never_revives(self):
        rows=trace_rows();rows.insert(9,row(90));d=self.review(rows);self.assertFalse(d['joins'])
    def test_missing_request_chain_is_partial(self):
        rows=trace_rows();rows[6]['token']=999;d=self.review(rows);self.assertFalse(d['joins']);self.assertIn('attachment_request_mismatch',d['issues'])
    def test_wrong_mesh_is_not_same_owner_draw(self):
        rows=trace_rows();rows[9]['mesh']=301;d=self.review(rows);self.assertIn('first_draw_cross_association',d['issues'])
    def test_failed_load_not_ready(self):
        rows=trace_rows();rows[5]['visual']=0;d=self.review(rows);self.assertFalse(d['joins']);self.assertEqual(d['counts']['failed_load'],1)
    def test_record_loss_never_passes(self):
        d=self.review(trace_rows(),dropped=1);self.assertEqual(d['result'],'PARTIAL');self.assertIn('record_loss',d['issues'])
    def test_missing_byte_restoration_fails(self):
        rows=trace_rows();rows[-1]['a'][2]=8;d=self.review(rows);self.assertIn('cleanup_unconfirmed',d['issues'])
    def test_version_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError,'version'):self.review(trace_rows(),version=2)
    def test_limit_is_partial(self):
        self.assertIn('limit_or_setup_failure',self.review(trace_rows(),reason=2)['issues'])
    def test_fixture_not_gameplay_success(self):
        rows=trace_rows()
        for r in rows:r['flags']=256
        d=self.review(rows);self.assertEqual(d['result'],'FIXTURE_TIMING_JOIN_PASS');self.assertTrue(d['fixture'])
    def test_unqualified_asset_cannot_pass(self):
        rows=trace_rows();rows[5]['flags']=64;d=self.review(rows);self.assertFalse(d['joins'])
    def test_retired_epoch_cannot_be_restored_by_cache_return(self):
        rows=trace_rows();rows.insert(5,row(90));d=self.review(rows)
        self.assertFalse(d['joins']);self.assertIn('retired_asset_epoch_reused',d['issues'])
    def test_changed_scope_owner_rejected(self):
        rows=trace_rows();rows[5]['owner']=999
        with self.assertRaisesRegex(ValueError,'identity'):self.review(rows)
    def test_reused_owner_epoch_rejected(self):
        rows=trace_rows();rows.insert(1,row(89));rows.insert(2,row(88))
        with self.assertRaisesRegex(ValueError,'epoch reused'):self.review(rows)

if __name__=='__main__':unittest.main()
