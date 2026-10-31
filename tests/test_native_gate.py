import io,json,struct,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
import native_gate as n

class Channel:
    def __init__(self):self.data=bytearray(n.SIZE)
    def read(self,o,size):return bytes(self.data[o-n.OFFSET:o-n.OFFSET+size])
    def write(self,o,b):self.data[o-n.OFFSET:o-n.OFFSET+len(b)]=b

def setup(policy=1):
    c=Channel();v=[0]*34
    v[:10]=[n.MAGIC,1,n.SIZE,42,1,2,3,4,policy,1];v[29]=1000000
    c.data[:256]=struct.pack('<10I16i2I6Q96s',*v,b'\0'*96)
    return c

def row(frame,outcome=2,flags=0):
    start=frame*16667
    return struct.pack('<12IQ2I8Q',frame,7,3,1,outcome,1,1,1,0,1,1,flags,
        start+100,0,0,start,start+200,start+8000,start+8500 if outcome==2 else 0,
        start+8600,start+16000,frame,123)

class GateTests(unittest.TestCase):
    def test_policy_and_layout(self):
        for p in (1,2):self.assertEqual(n.header(setup(p).data[:256])['policy'],p)
        with self.assertRaises(ValueError):n.header(setup(3).data[:256])
    def test_partial_and_recycled_ticket_evidence(self):
        b=bytearray(row(1));struct.pack_into('<Q',b,120,0)
        with self.assertRaisesRegex(ValueError,'identity'):n.record(b)
        with self.assertRaises(ValueError):n.record(b[:100])
    def test_ring_backpressure_not_overwritten(self):
        c=setup();struct.pack_into('<i',c.data,56,65)
        with self.assertRaisesRegex(ValueError,'cursors'):n.header(c.data[:256])
    def test_external_worker_drains_before_close(self):
        with tempfile.TemporaryDirectory(dir=n.ROOT/'artifacts/player-replacement/native-gate-tests') as d:
            c=setup();cap=n.Capture(c,d,[1,2,3,4]);cap.stop.set();cap.thread.join(5)
            c.data[384:512]=row(1);struct.pack_into('<i',c.data,56,1)
            out=io.BytesIO();cap.drain(out);cap.drain(out)
            self.assertEqual(len(out.getvalue()),128);self.assertEqual(struct.unpack_from('<i',c.data,60)[0],1)
            self.assertFalse(cap.finish()['error'])
    def test_wrong_session_does_not_ack(self):
        with tempfile.TemporaryDirectory(dir=n.ROOT/'artifacts/player-replacement/native-gate-tests') as d:
            c=setup();cap=n.Capture(c,d,[4,3,2,1]);result=cap.finish()
            self.assertIn('session',result['error']);self.assertEqual(struct.unpack_from('<i',c.data,60)[0],0)
    def test_timing_and_fallback_sequences(self):
        with tempfile.TemporaryDirectory(dir=n.ROOT/'artifacts/player-replacement/native-gate-tests') as d:
            Path(d,'NATIVE-GATE-001.bin').write_bytes(row(1)+row(2,3)+row(3,3)+row(4)+row(5,flags=2))
            r=n.analyze(d,n.header(setup().data[:256]))
            self.assertEqual(r['longest_requested_fallback'],2)
            self.assertEqual(r['commits'],3)
            self.assertAlmostEqual(r['frame_period_ms']['median'],16.667)
            self.assertEqual(r['gate_wait_ms']['samples'],4)
            self.assertEqual(r['maximum_slot_occupancy'],1)
    def test_unready_cold_run_is_partial(self):
        with tempfile.TemporaryDirectory(dir=n.ROOT/'artifacts/player-replacement/native-gate-tests') as d:
            Path(d,'NATIVE-GATE-001.bin').write_bytes(b'')
            self.assertEqual(n.analyze(d,None)['result'],'PARTIAL')

if __name__=='__main__':unittest.main()
