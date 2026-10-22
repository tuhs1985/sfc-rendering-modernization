import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
import synchronized_buffer as b

class BufferTests(unittest.TestCase):
    session='Local\\SFCBridge_'+'00000001'*4
    def raw(self,rows,**changes):
        h=[b.MAGIC,1,b.STORE_BYTES,123,1,1,1,1,len(rows),0,max((r[6] for r in rows),default=0),0,0,0,0,0]
        for key,value in changes.items():h[int(key)]=value
        return b.HEADER.pack(*h)+b''.join(b.RECORD.pack(*r) for r in rows)
    def row(self):return [101,100,100,1,2,3,17000,0,91,91,777,777,123456]
    def test_matched_previous_not_current(self):
        r=b.decode(self.raw([self.row()]),self.session,123);self.assertEqual(r['paired'],1);self.assertEqual(r['owners'],{'2':1})
    def test_wrong_frame_or_camera_or_sequence_rejected(self):
        for field,value in ((0,102),(2,101),(9,92),(11,778)):
            r=self.row();r[field]=value
            with self.assertRaises(ValueError):b.decode(self.raw([r]),self.session,123)
    def test_age_and_identity(self):
        for field,value in ((6,50001),(4,0),(5,0),(8,0)):
            r=self.row();r[field]=value
            with self.assertRaises(ValueError):b.decode(self.raw([r]),self.session,123)
    def test_original_only_previous_scene_is_not_false_ship(self):
        r=self.row();r[3]=2;r[2]=r[9]=r[11]=0
        self.assertEqual(b.decode(self.raw([r]),self.session,123)['without_ship'],1)
    def test_reset_and_warmup(self):
        rows=[[101,0,0,s,0,0,0,0,0,0,0,0,123456+s] for s in (3,4)]
        data=b.decode(self.raw(rows),self.session,123);self.assertEqual((data['warmup'],data['reset']),(1,1))
    def test_layout_and_bounds(self):
        for raw in (b'bad',self.raw([])+b'x',self.raw([],**{'8':b.CAPACITY+1})):
            with self.assertRaises(ValueError):b.decode(raw,self.session,123)
    def test_wrong_session_and_process(self):
        for session,pid in ((self.session,124),('Local\\SFCBridge_'+'00000002'*4,123)):
            with self.assertRaises(ValueError):b.decode(self.raw([self.row()]),session,pid)
    def test_supervisor_atomic_rename_inventory(self):
        from run_return_fixture import capture_file_bytes
        from unittest.mock import Mock
        from types import SimpleNamespace
        p=Mock();p.is_file.return_value=True;p.stat.side_effect=FileNotFoundError('renamed')
        self.assertEqual(capture_file_bytes(p),0)
        p.stat.side_effect=None;p.stat.return_value=SimpleNamespace(st_size=48)
        self.assertEqual(capture_file_bytes(p),48)
        p.stat.side_effect=PermissionError('not an atomic rename')
        with self.assertRaises(PermissionError):capture_file_bytes(p)
    def test_buffer_cannot_certify_unbuffered_mode(self):
        import additive_qualification as q
        import tempfile,json
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);fixture=root/'artifacts/remix-runtime/runs/test';fixture.mkdir(parents=True)
            (fixture/'result.json').write_text(json.dumps(dict(synchronized_buffer_fixture=True)))
            with patch.object(q,'ROOT',root):
                with self.assertRaisesRegex(ValueError,'cannot certify the unbuffered'):
                    q.qualify(fixture)

    def test_early_late_fence_qualification(self):
        from qualify_synchronized_buffer import phase_qualified
        from copy import deepcopy
        result=dict(buffer_early_ready_fixture=True,live_owner_timing=dict(game_output=dict(retain_ready=True,lease_worker_releases=599,overwritten=0)),
                    source_timing=dict(profiles=[dict(last_lead_ms=dict(p50=16))]))
        phase_qualified(result,True)
        for mutate in ('overwritten','retain_ready','lease_worker_releases'):
            bad=deepcopy(result);bad['live_owner_timing']['game_output'][mutate]=1 if mutate=='overwritten' else 0
            with self.assertRaises(ValueError):phase_qualified(bad,True)
        with self.assertRaises(ValueError):phase_qualified(result,False)
        result['source_timing']['profiles'][0]['last_lead_ms']['p50']=3
        with self.assertRaises(ValueError):phase_qualified(result,True)
        result['buffer_early_ready_fixture']=False;phase_qualified(result,False)

if __name__=='__main__':unittest.main()
