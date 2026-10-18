import json
from pathlib import Path
import sys
import tempfile
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
import run_coverage_probe as c

class CoverageTests(unittest.TestCase):
    def fixture(self,folder,mode='bits'):
        lines=[]
        for phase,owners in enumerate(((7,11),(7,11),(11,),(13,11),(23,))):
            ids=np.zeros((256,256),dtype='<u4');z=np.full((256,256),-1234,dtype='<f4')
            for n,owner in enumerate(owners):
                area=np.s_[20:30,20+n*30:30+n*30];ids[area]=owner
                view_z=9 if owner==11 else (8 if phase==1 else 6)
                z[area]=100/99.9-(.1*100/99.9)/view_z
            if mode=='numeric':ids=ids.astype('<f4').view('<u4')
            (folder/f'coverage-{phase}-picking.bin').write_bytes(ids.tobytes())
            (folder/f'coverage-{phase}-depth.bin').write_bytes(z.tobytes())
            (folder/f'coverage-{phase}-color.bin').write_bytes(bytes(256*256*4))
            lines.extend(f'COVERAGE_NATIVE_GPU_EXACT phase={phase} output={name}' for name in ('color','depth','picking'))
            lines.append(f'COVERAGE_SHADER_ID_EXACT phase={phase}')
        (folder/'stdout.log').write_text('\n'.join(lines))
    def test_bit_ids_and_normalized_depth(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);self.fixture(p);r=c.analyze(p)
            self.assertTrue(all(r[k] for k in c.CORE_QUALIFIED));self.assertFalse(r['historical_camera_projection_qualified']);self.assertEqual(r['phases'][0]['qualified_id_mode'],'raw_uint32')
    def test_numeric_id_conversion_distinguished(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);self.fixture(p,'numeric');self.assertEqual(c.analyze(p)['phases'][0]['qualified_id_mode'],'numeric_float32')
    def test_stale_retired_id_not_qualified(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);self.fixture(p);(p/'coverage-2-picking.bin').write_bytes((p/'coverage-0-picking.bin').read_bytes());self.assertFalse(c.analyze(p)['owner_coverage_qualified'])
    def test_depth_range_and_background_corruption(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);self.fixture(p);z=np.fromfile(p/'coverage-0-depth.bin',dtype='<f4');z[0]=0;z[20*256+20]=100;z.tofile(p/'coverage-0-depth.bin');r=c.analyze(p);self.assertFalse(r['normalized_depth_qualified']);self.assertFalse(r['background_sentinel_qualified'])
    def test_no_log_is_not_gpu_transfer_proof(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);self.fixture(p);(p/'stdout.log').write_text('');r=c.analyze(p);self.assertFalse(r['native_gpu_transfer_exact']);self.assertFalse(r['native_shader_id_decode_exact'])
    def test_truncated_plane_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);self.fixture(p);(p/'coverage-0-depth.bin').write_bytes(b'bad')
            with self.assertRaises(ValueError):c.analyze(p)
    def test_archive_rejects_repository_root(self):
        with self.assertRaises(ValueError):c.archive([c.ROOT])
    def test_native_composed_raster_reference(self):
        import struct
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'manifest.json').write_text(json.dumps({'replay_camera':{'viewport':[0,0,256,256],'native_composed':np.eye(4).tolist()}}))
            data=struct.pack('<4I4f',0x53464347,1,3,3,0,0,0,1)
            for x,y in ((10,10),(20,10),(10,20)):data+=struct.pack('<8f',x,y,0,0,0,1,0,0)
            (p/'coverage-mesh.bin').write_bytes(data);z=c.expected_replay(p)
            self.assertEqual(z[11,11],.5);self.assertFalse(np.isfinite(z[21,21]));self.assertGreater(np.isfinite(z).sum(),10)
    def test_native_z_reference_does_not_remap(self):
        import struct
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'manifest.json').write_text(json.dumps({'replay_camera':{'viewport':[0,0,256,256],'native_composed':np.eye(4).tolist(),'depth_reference':'native_z','native_depth_conversion':False}}))
            data=struct.pack('<4I4f',0x53464347,1,3,3,0,0,0,1)
            for x,y in ((10,10),(20,10),(10,20)):data+=struct.pack('<8f',x,y,.2,0,0,1,0,0)
            (p/'coverage-mesh.bin').write_bytes(data)
            self.assertAlmostEqual(c.expected_replay(p)[11,11],.2,places=6)
            manifest=json.loads((p/'manifest.json').read_text());manifest['replay_camera']['native_depth_conversion']=True
            (p/'manifest.json').write_text(json.dumps(manifest))
            self.assertAlmostEqual(c.expected_replay(p)[11,11],.2,places=6)

if __name__=='__main__':unittest.main()
