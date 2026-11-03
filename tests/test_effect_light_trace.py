import copy,json,struct,sys,tempfile,time
from pathlib import Path
from unittest.mock import patch
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools/remix_runtime'),str(ROOT/'tools/d3d9_proof')]
import effect_light_trace as t
from test_fast_light_transport import Channel

def frame(number=1,pid=123):
    raw=bytearray(t.FRAME_BYTES)
    struct.pack_into('<4I2Q',raw,0,number,pid,1,1,1000,2000)
    struct.pack_into('<4IQ',raw,32,number,0,7,1,1000)
    struct.pack_into('<I',raw,56+2*64,5)
    raw[4152:4156]=b'\1'*4
    struct.pack_into('<i',raw,4216,1)
    struct.pack_into('<2I8f',raw,4464,2,5,1,2,3,.5,.25,0,100,1)
    return raw

def publish(channel,raw):
    number=struct.unpack_from('<I',raw)[0];at=t.OFFSET+64+number%t.FRAMES*t.CELL_BYTES
    channel.write(at,struct.pack('<IIQ',2,0,2000)+raw)

class EffectTraceTests(unittest.TestCase):
    def test_decode_preserves_native_words_and_actual_submission(self):
        v=t.decode(frame(),123);self.assertEqual(v['slots'][0]['native_words'][0],5)
        self.assertEqual(v['slots'][0]['submitted']['position'],[1,2,3]);self.assertEqual(v['source_qpc'],1000)

    def test_malformed_identity_nonfinite_and_status(self):
        for at,packing,value in ((4,'I',999),(32,'I',2),(4216,'i',2),(4472,'f',float('nan'))):
            with self.subTest(at=at):
                raw=frame();struct.pack_into('<'+packing,raw,at,value)
                with self.assertRaises(ValueError):t.decode(raw,123)
        with self.assertRaises(ValueError):t.decode(b'',123)

    def test_actual_native_layout_both_architectures(self):
        for arch in (32,64):
            path=ROOT/f'artifacts/player-replacement/effect-light-tests/trace{arch}.bin'
            if not path.exists():self.skipTest('Build effect-light tests first')
            raw=path.read_bytes();pid=struct.unpack_from('<I',raw,4)[0];v=t.decode(raw,pid)
            self.assertEqual(v['frame'],10);self.assertEqual(v['slots'][1]['submitted']['radiance'][0],1.5)

    def test_record_changes_bound_and_shutdown_without_disabling_lights(self):
        c=Channel()
        with tempfile.TemporaryDirectory() as folder:
            recorder=t.Recorder(c,folder,123)
            try:
                publish(c,frame());deadline=time.monotonic()+2
                while recorder.last_frame<1 and time.monotonic()<deadline:time.sleep(.005)
                self.assertEqual(recorder.last_frame,1)
                # Submit unchanged state on a new frame:counts increase but no log event.
                publish(c,frame(2));deadline=time.monotonic()+2
                while recorder.last_frame<2 and time.monotonic()<deadline:time.sleep(.005)
                self.assertEqual(recorder.summary['records'],1)
                with patch.object(t,'LIMIT',1):
                    v=t.decode(frame(3),123);v['gate']=0;recorder.accept(v)
                self.assertEqual(recorder.summary['omitted_records'],1)
            finally:summary=recorder.close()
            self.assertIsNone(summary['error']);self.assertFalse(recorder.thread.is_alive())
            self.assertEqual(struct.unpack('<I',c.read(t.OFFSET+40,4))[0],0)
            self.assertLessEqual(summary['bytes'],4*1024**2)

    def test_session_mismatch_is_reported_not_relabelled(self):
        c=Channel()
        with tempfile.TemporaryDirectory() as folder:
            recorder=t.Recorder(c,folder,123)
            c.write(t.OFFSET+12,bytes(16));recorder.thread.join(2);summary=recorder.close()
            self.assertIn('session',summary['error'])

if __name__=='__main__':unittest.main()
