import ctypes as C
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
import broad_capture as b
import archive_broad_evidence as archive

class BroadTests(unittest.TestCase):
    def trace(self,events,**values):
        h=b.Header();h.magic=0x42524431;h.version=1;h.recordBytes=h.headerBytes=128
        h.frequency=1000;h.durationMs=10000;h.hardBytes=b.HARD;h.warningBytes=b.HARD//2
        h.status=3;h.reason=1;h.written=len(events);h.fileBytes=128*(len(events)+1)
        for k,v in values.items():setattr(h,k,v)
        records=[]
        for i,(kind,obj,dev,args) in enumerate(events,1):records.append(b.RECORD.pack(i,i*10,kind,1,obj,dev,*(args+[0]*(11-len(args)))))
        return bytes(h)+b''.join(records)
    def analyze(self,data):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'trace.bin';p.write_bytes(data);return b.analyze(p)
    def test_positive_lifetime_and_depth_draw(self):
        events=[(3,100,1,[3,0x30,0,0,0,1920,1080,1,1,44,1]),(5,200,1,[100,0x30,3,45]),(10,10,1,[1,200]),(12,10,1,[30,1]),(10,10,1,[1,0]),(18,10,1,[1])]
        r=self.analyze(self.trace(events));self.assertEqual(r['depth_candidates'][0]['draws'],1)
        self.assertEqual(r['depth_candidates'][0]['resource_desc']['height_or_stride'],1080)
        self.assertIn('COMPLETE',r['result'])
    def test_recycled_view_not_reused(self):
        events=[(5,200,1,[100,0x30,3,45]),(10,10,1,[1,200]),(6,200,1,[]),(5,200,1,[101,0x30,3,45]),(10,10,1,[1,200])]
        rows=self.analyze(self.trace(events))['depth_candidates']
        self.assertEqual(len(rows),2);self.assertEqual({x['resource'] for x in rows},{100,101})
    def test_recycled_device_cannot_keep_old_view(self):
        events=[(5,200,1,[100,0x30,3,45]),(10,10,1,[1,200]),(2,1,1,[]),(1,1,1,[]),(10,10,1,[1,200])]
        rows=self.analyze(self.trace(events))['depth_candidates']
        self.assertEqual(len(rows),2)
        self.assertTrue(any(r['resource'] is None and r['view_creation_sequence']==0 for r in rows))
    def test_devices_and_command_reset_separate(self):
        events=[(5,200,1,[100,0x30,3,45]),(10,10,1,[1,200]),(9,10,1,[]),(12,10,1,[3]),(12,10,2,[3])]
        self.assertEqual(self.analyze(self.trace(events))['depth_candidates'][0]['draws'],0)
    def test_loss_and_non_duration_stop_partial(self):
        for kwargs in ({'dropped':1},{'reason':2},{'error':1},{'status':4}):
            self.assertIn('PARTIAL',self.analyze(self.trace([],**kwargs))['result'])
    def test_invalid_header_and_incomplete_file(self):
        for data in (b'',self.trace([])[:-1],self.trace([],recordBytes=64),self.trace([],hardBytes=b.HARD+1),self.trace([],written=1)):
            with self.assertRaises(ValueError):self.analyze(data)
    def test_unknown_bind_is_not_invented_resource(self):
        row=self.analyze(self.trace([(10,10,1,[1,999])]))['depth_candidates'][0]
        self.assertIsNone(row['resource']);self.assertEqual(row['view_creation_sequence'],0)
    def test_proxy_rollback_and_independent_change(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);target=root/'dxgi.dll';full=root/'full.dll';backup=root/'rollback'
            target.write_bytes(b'original');full.write_bytes(b'full')
            with mock.patch.multiple(b,FULL=full,FULL_SHA=b.digest(full),OLD_SHA=b.digest(target)):
                b.install_test_proxy(target,backup);self.assertEqual(target.read_bytes(),b'full')
                b.restore_test_proxy(target,backup);self.assertEqual(target.read_bytes(),b'original')
                target.write_bytes(b'independent')
                with self.assertRaises(ValueError):b.restore_test_proxy(target,backup)
                self.assertEqual(target.read_bytes(),b'independent')
    def test_atomic_stage_conflict_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);target=root/'dxgi.dll';src=root/'new.dll'
            target.write_bytes(b'original');src.write_bytes(b'new')
            target.with_name(target.name+'.sfc-broad-stage').write_bytes(b'interrupted')
            with self.assertRaises(ValueError):b.atomic_copy(src,target,b.digest(src))
            self.assertEqual(target.read_bytes(),b'original')
    def test_archive_crc_and_raw_preservation(self):
        import zipfile
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);run=root/'artifacts/remix-runtime/runs/test';run.mkdir(parents=True)
            output=root/'artifacts/remix-runtime/archives/test.zip'
            (run/'broad.bin').write_bytes(self.trace([]));(run/'result.json').write_text('{}')
            (run/'excluded.dll').write_bytes(b'not evidence')
            (run/'depth-0.bin').write_bytes(b'raw depth evidence');(run/'depth-0-min.png').write_bytes(b'derivative')
            (run/'depth-99.bin').write_bytes(b'outside bounded whitelist')
            with mock.patch.object(archive,'ROOT',root),mock.patch.object(archive,'storage_bytes',return_value=0),mock.patch('builtins.print'):
                archive.archive(output,[run])
            with zipfile.ZipFile(output) as z:
                self.assertIsNone(z.testzip());self.assertEqual(len(z.namelist()),4)
            self.assertTrue((run/'broad.bin').exists())
    def test_archive_rejects_broad_directory(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            with mock.patch.object(archive,'ROOT',root),self.assertRaises(ValueError):
                archive.archive(root/'artifacts/remix-runtime/archives/test.zip',[root])
    def test_existing_outputs_count_against_overall_allowance(self):
        with mock.patch.object(b,'storage_bytes',return_value=b.OVERALL):
            with self.assertRaises(ValueError):b.reserve_capture_budget()

if __name__=='__main__':unittest.main()
