import ctypes as C
import json
from pathlib import Path
import struct
import subprocess as sp
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
from offscreen_position import ProcessReader,sample,decode_fields,Capture,PHASES,RANGES,analyze


class PositionTests(unittest.TestCase):
    def setUp(self):
        self.child=sp.Popen([sys.executable,str(Path(__file__).with_name('offscreen_position_child.py'))],
            stdin=sp.PIPE,stdout=sp.PIPE,stderr=sp.PIPE,text=True,creationflags=sp.CREATE_NO_WINDOW)
        self.seed=json.loads(self.child.stdout.readline())
        self.reader=ProcessReader(self.child.pid,sys.executable)
    def command(self,name):
        self.child.stdin.write(name+'\n');self.child.stdin.flush();self.assertEqual(self.child.stdout.readline().strip(),'OK')
    def tearDown(self):
        self.reader.close()
        try:self.child.stdin.write('exit\n');self.child.stdin.flush();self.child.wait(2)
        except (OSError,sp.TimeoutExpired):self.child.kill();self.child.wait(2)
        self.child.stdin.close();self.child.stdout.close();self.child.stderr.close()
    def test_actual_read_process_memory_sees_motion_without_cache_updates(self):
        a=sample(self.reader.read,self.seed);self.command('move');b=sample(self.reader.read,self.seed)
        self.assertEqual(a['status'],'stable_read');self.assertEqual(b['position'],[1,200,0])
        self.assertEqual(a['cache_words'],b['cache_words']);self.assertGreater(b['native_tick_before'],a['native_tick_before'])
        self.command('render');c=sample(self.reader.read,self.seed);self.assertEqual(c['cache_translation'][0],1)
    def test_identity_loss_never_becomes_valid_position(self):
        self.command('reuse');self.assertEqual(sample(self.reader.read,self.seed)['status'],'identity_mismatch')
    def test_nan_or_unreadable_is_rejected_without_target_crash(self):
        self.command('nan');self.assertEqual(sample(self.reader.read,self.seed)['status'],'unreadable_or_nonfinite')
        self.assertIsNone(self.child.poll())
    def test_wrong_process_path_and_read_bounds(self):
        with self.assertRaisesRegex(ValueError,'path mismatch'):ProcessReader(self.child.pid,'C:/not-the-fixture.exe')
        for address,size in ((0,4),(0x80000000,4),(self.seed['ship'],69)):
            with self.assertRaises(ValueError):self.reader.read(address,size)
    def test_double_read_change_is_not_a_fresh_coherent_pose(self):
        count=0
        def changing(address,size):
            nonlocal count
            if address==self.seed['ship']+0xE6:
                count+=1
                if count==2:self.command('move')
            return self.reader.read(address,size)
        self.assertEqual(sample(changing,self.seed)['status'],'changing_during_read')
    def test_actual_capture_worker_joins_and_quarantines_identity_loss(self):
        with tempfile.TemporaryDirectory() as raw:
            seed={**self.seed,'source':123,'model_name':'synthetic','initial_observer_epoch':1,
                'observed_epochs':[[1,1,1,1,1]],'records':0,'quarantined':False,'source_packet':'synthetic'}
            def discover(c):
                if not c.tracks:c.tracks[seed['ship']]=seed
            with patch.object(Capture,'discover',discover):
                c=Capture(raw,self.child.pid,sys.executable)
                try:
                    self.command('move');time.sleep(.12);self.command('reuse');time.sleep(.12)
                finally:receipt=c.close()
            self.assertTrue(receipt['joined']);self.assertTrue(receipt['process_handle_closed'])
            self.assertTrue(receipt['tracks'][0]['quarantined']);self.assertIsNone(c.reader.handle)
            rows=[json.loads(l) for l in (Path(raw)/'OFFSCREEN-POSITION-001.jsonl').read_text().splitlines()]
            self.assertEqual(rows[-1]['status'],'identity_mismatch');self.assertLess(len(rows),10)
    def test_output_byte_limit_stops_collection_not_game_or_process(self):
        with tempfile.TemporaryDirectory() as raw:
            seed={**self.seed,'model_name':'synthetic','initial_observer_epoch':1,
                'observed_epochs':[[1,1,1,1,1]],'records':0,'quarantined':False}
            def discover(c):
                if not c.tracks:c.tracks[seed['ship']]=seed
            with patch.object(Capture,'discover',discover),patch('offscreen_position.MAX_BYTES',32):
                c=Capture(raw,self.child.pid,sys.executable)
                try:c.thread.join(2)
                finally:receipt=c.close()
            self.assertTrue(receipt['saturated']);self.assertEqual(receipt['bytes'],0)
            self.assertIsNone(self.child.poll())


class AnalysisTests(unittest.TestCase):
    def fixture(self,folder,moving=True):
        from source_timing import HEADER,RECORD,MAGIC,STORE_BYTES,CAPACITY
        header=[MAGIC,1,STORE_BYTES,CAPACITY,77,9,3,0,3,0,0,0,1000,1,2,3,4,0,0,0,0,bytes(40)]
        source=[]
        for count,(frame,owner,qpc) in enumerate(((10,2,100),(11,9,200),(20,3,900)),1):
            source.append(RECORD.pack(1,frame,count,owner,owner,1,9,0,qpc,qpc,qpc+1,123,234,99,98))
        (folder/'D3D9-SOURCE-TIMING-001.bin').write_bytes(HEADER.pack(*header)+b''.join(source))
        (folder/'manifest.json').write_text(json.dumps(dict(semantic_calibration=dict(scene_session='Local\\SFCBridge_00000001000000020000000300000004'))))
        worker=dict(pid=77,error=None,saturated=False,joined=True,process_handle_closed=True,
            tracks=[dict(ship=100,model_name='synthetic',quarantined=False,observed_epochs=[[2,10,0,99,98],[3,20,0,99,98]])])
        (folder/'offscreen-position-worker.json').write_text(json.dumps(worker));(folder/'gate').mkdir()
        event=[0]*96;event[1]=2;event[2]=11;event[4]=2
        (folder/'gate/LIFECYCLE-001-events.jsonl').write_text(json.dumps(event)+'\n')
        rows=[dict(pid=77,ship=100,status='stable_read',qpc_before=300+i*100,qpc_after=301+i*100,frequency=1000,
            position=[i if moving else 0,0,0],cache_words=[0]*17,native_tick_before=i) for i in range(3)]
        (folder/'OFFSCREEN-POSITION-001.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    def test_fresh_movement_inside_verified_render_gap_not_lifetime_proof(self):
        with tempfile.TemporaryDirectory() as raw:
            folder=Path(raw);self.fixture(folder);result=analyze(folder)
            self.assertEqual(result['result'],'OFFSCREEN_POSITION_UPDATES_OBSERVED_NOT_LIFETIME_PROOF')
            gap=result['tracks'][0]['gaps'][0];self.assertEqual(gap['samples'],3)
            self.assertTrue(gap['position_changed']);self.assertEqual(gap['missing_owner_render_offers'],0)
    def test_stationary_readable_data_is_not_claimed_as_continued_updates(self):
        with tempfile.TemporaryDirectory() as raw:
            folder=Path(raw);self.fixture(folder,moving=False);self.assertEqual(analyze(folder)['result'],'PARTIAL')
    def test_source_session_mismatch_cannot_prove_offscreen_updates(self):
        with tempfile.TemporaryDirectory() as raw:
            folder=Path(raw);self.fixture(folder)
            (folder/'manifest.json').write_text(json.dumps(dict(semantic_calibration=dict(scene_session='Local\\SFCBridge_'+'0'*32))))
            with self.assertRaises(ValueError):analyze(folder)
    def test_base_movement_is_not_hidden_by_zero_added_translation(self):
        with tempfile.TemporaryDirectory() as raw:
            folder=Path(raw);self.fixture(folder)
            path=folder/'OFFSCREEN-POSITION-001.jsonl';rows=[json.loads(l) for l in path.read_text().splitlines()]
            for r in rows:r['base_position']=r['position'];r['position']=[0,0,0]
            path.write_text(''.join(json.dumps(r)+'\n' for r in rows))
            result=analyze(folder);self.assertEqual(result['result'],'OFFSCREEN_POSITION_UPDATES_OBSERVED_NOT_LIFETIME_PROOF')
            self.assertEqual(result['tracks'][0]['gaps'][0]['movement_source'],'base_simulation_translation')
    def test_cues_request_actual_offscreen_movement_without_destruction(self):
        self.assertEqual([p[0] for p in PHASES],[15,25,40,50,60,75,80])
        self.assertIn('moving',PHASES[1][2]);self.assertFalse(any('destroy' in p[2] for p in PHASES))
    def test_bad_field_length(self):
        with self.assertRaises(ValueError):decode_fields(b'\0'*10)


if __name__=='__main__':unittest.main()
