import io,json,struct,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
import native_insertion_probe as n
tempfile.tempdir=str(n.ROOT/'artifacts/player-replacement/native-insertion-tests')
Path(tempfile.tempdir).mkdir(parents=True,exist_ok=True)

class Channel:
    def __init__(self):self.data=bytearray(n.SIZE)
    def read(self,offset,length):return bytes(self.data[offset-n.OFFSET:offset-n.OFFSET+length])
    def write(self,offset,data):self.data[offset-n.OFFSET:offset-n.OFFSET+len(data)]=data

def setup():
    c=Channel();h=[0]*32;h[:8]=[n.MAGIC,1,n.SIZE,42,1,2,3,4];h[14]=9
    c.data[:128]=struct.pack('<32I',*h);struct.pack_into('<Q',c.data,104,1000000)
    return c

def put(c,kind,phase,qpc,output=0):
    w=struct.unpack_from('<I',c.data,32)[0];a=[0]*27;a[:8]=[kind,22,7,4,phase,100,200,300]
    a[8]=qpc;a[22]=output;a[24]=int(output!=0);a[26]=w+1
    c.data[128+(w%n.CAPACITY)*128:256+(w%n.CAPACITY)*128]=struct.pack('<8I5Q14I',*a)
    struct.pack_into('<I',c.data,32,w+1)

class ProbeTests(unittest.TestCase):
    def test_header(self):
        c=setup();self.assertEqual(n.header(c.data[:128])['frequency'],1000000)
        c.data[0]=0
        with self.assertRaises(ValueError):n.header(c.data[:128])
    def test_commit_and_identity(self):
        c=setup();put(c,5,2,12345,22);e=n.event(c.data[128:256],1)
        self.assertEqual(e['output_frame'],22);self.assertEqual(e['qpc'],12345)
        with self.assertRaises(ValueError):n.event(c.data[128:256],2)
        c.data[128]=99
        with self.assertRaises(ValueError):n.event(c.data[128:256],1)
    def test_external_drain(self):
        with tempfile.TemporaryDirectory() as d:
            c=setup();cap=n.Capture(c,d,session=[1,2,3,4]);cap.stop_event.set();cap.thread.join(5)
            put(c,3,2,10000);put(c,5,2,11000,22);put(c,6,2,12000,22)
            stream=io.BytesIO();cap.drain(stream);cap.drain(stream)
            self.assertEqual(cap.count,3);self.assertEqual(len(stream.getvalue()),384)
            self.assertEqual(struct.unpack_from('<I',c.data,36)[0],3)
            self.assertEqual(cap.source_leads,[2.0]);self.assertEqual(cap.readiness[('after_selected',5,0)],1)
            result=cap.finish();self.assertFalse(result['shield_replay']);self.assertTrue(result['original_drawing_unchanged'])
    def test_stale_session_not_acknowledged(self):
        with tempfile.TemporaryDirectory() as d:
            c=setup();cap=n.Capture(c,d,session=[4,3,2,1]);cap.stop_event.set();cap.thread.join(5)
            self.assertIn('session',cap.error)
            self.assertEqual(struct.unpack_from('<I',c.data,36)[0],0)
    def test_cursor_bounds(self):
        c=setup();struct.pack_into('<I',c.data,32,257)
        with self.assertRaises(ValueError):n.header(c.data[:128])
    def test_observer_is_separate(self):
        root=Path(__file__).resolve().parents[1]
        code=(root/'tools/remix_runtime/d3d9_game_receiver.h').read_text()
        self.assertIn('replacementMode=replacement::requested()&&!native_insertion::requested()',code)
        self.assertIn('if(insertionProbe)',code)
        producer=(root/'tools/m1_component/m1_component.cpp').read_text()
        self.assertIn('if(g_replacement&&state&&!g_insertion_probe)',producer)

if __name__=='__main__':unittest.main()
