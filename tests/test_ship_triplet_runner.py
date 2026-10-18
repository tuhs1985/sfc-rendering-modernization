import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
import run_coverage_probe as runner

class TripletRunnerTests(unittest.TestCase):
    def rejected(self,*args):
        result=subprocess.run([sys.executable,str(Path(runner.__file__)),*args],capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,2);self.assertNotIn('Traceback',result.stderr)
    def test_requires_native_depth_and_capture(self):self.rejected('--triplet','--execute')
    def test_fault_requires_triplet(self):self.rejected('--triplet-fault','slow')
    def test_offset_requires_triplet(self):self.rejected('--diagnostic-offset')
    def test_source_session_key_layout(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder);capture=p/'capture';capture.mkdir();row=[0]*96;row[1]=2;row[2]=120;row[7]=2
            (capture/'semantic.analysis.json').write_text(json.dumps({'snapshots':[{'associations':[{'owner':2,'record':row}]}]}))
            (capture/'manifest.json').write_text(json.dumps({'semantic_calibration':{'scene_session':'Local\\SFCBridge_'+'a'*32}}))
            (capture/'result.json').write_text(json.dumps({'target_pid':38852}));source=p/'mesh.bin';source.write_bytes(b'mesh fixture')
            camera={'source_capture':'capture','source_snapshot':0,'owner_epoch':2,'viewport':[200,30,1720,1020]}
            with mock.patch.object(runner,'ROOT',p):result=runner.prepare_triplet_request(camera,source,p)
            raw=(p/'ship-return-request.bin').read_bytes();self.assertEqual(len(raw),152)
            key=struct.unpack('<8I2Q8I32s6II3f',raw);self.assertEqual(key[:8],(0,0,0,0,2,2,120,29))
            self.assertEqual(key[-10:-4],(0xaaaaaaaa,)*4+(38852,0));self.assertEqual(result['engine_frame'],120)
            self.assertEqual(key[-4:],(0,0,0,0))
            camera['diagnostic_offset']={'mode':1,'world_translation':[12,-4,2]}
            with mock.patch.object(runner,'ROOT',p):runner.prepare_triplet_request(camera,source,p)
            self.assertEqual(struct.unpack('<I3f',(p/'ship-return-request.bin').read_bytes()[-16:]),(1,12,-4,2))

if __name__=='__main__':unittest.main()
