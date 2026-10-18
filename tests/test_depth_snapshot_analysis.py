from pathlib import Path
import json
import struct
import sys
import tempfile
import unittest
from unittest import mock
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
import depth_snapshot_analysis as d

class DepthPacketTests(unittest.TestCase):
    def qualification(self,root,**overrides):
        folder=root/'artifacts/remix-runtime/deps';folder.mkdir(parents=True,exist_ok=True)
        record=dict(result='OFFLINE_DEPTH_SNAPSHOT_PASS',source_hashes={},addon_sha256='ABC',tested_feature_level=0xA100,reader='ps_4_1')
        record.update(overrides);(folder/'depth-snapshot-qualification.json').write_text(json.dumps(record))
        with mock.patch.object(d,'ROOT',root),mock.patch.object(d,'digest',return_value='ABC'),mock.patch('prepare_full_reshade.source_hashes',return_value={}):return d.require_qualification()
    def packet(self,path,**changes):
        h=[0]*96
        h[:18]=[0x44535031,1,768,2,2,4,4,4,4,8,2,1,1,1,64,64,87,1]
        h[32:36]=[257,2,0,1]
        for key,value in changes.items():h[int(key)]=value
        z=np.tile(np.array([.5,.25,.75,.5],dtype='<f4'),(2,2,1)).tobytes()
        path.write_bytes(struct.pack('<96Q',*h)+z+bytes([1,2,3,255])*16)
    def test_valid_color_and_channels(self):
        with tempfile.TemporaryDirectory() as f:
            p=Path(f)/'depth-0.bin';self.packet(p);row,z,c=d.read_packet(p)
            self.assertTrue(row['valid']);self.assertEqual(c[0,0].tolist(),[3,2,1,255]);self.assertEqual(z[0,0].tolist(),[.5,.25,.75,.5])
    def test_reject_invalid_header(self):
        with tempfile.TemporaryDirectory() as f:
            p=Path(f)/'depth-0.bin'
            for field,value in ((0,0),(1,2),(3,5000),(9,1),(14,0),(16,39),(17,17),(18,1),(33,0)):
                self.packet(p,**{str(field):value})
                with self.assertRaises(ValueError):d.read_packet(p)
    def test_truncation(self):
        with tempfile.TemporaryDirectory() as f:
            p=Path(f)/'depth-0.bin';self.packet(p);p.write_bytes(p.read_bytes()[:-1])
            with self.assertRaises(ValueError):d.read_packet(p)
    def test_nonfinite_and_sample_order_not_silently_fixed(self):
        with tempfile.TemporaryDirectory() as f:
            p=Path(f)/'depth-0.bin';self.packet(p);raw=bytearray(p.read_bytes());struct.pack_into('<4f',raw,768,float('nan'),.9,.1,2);p.write_bytes(raw)
            row,_,_=d.read_packet(p);self.assertFalse(row['valid']);self.assertEqual(row['nonfinite_values'],1);self.assertEqual(row['out_of_range_values'],1)
    def test_incomplete_status_is_partial(self):
        with tempfile.TemporaryDirectory() as f:
            p=Path(f);self.packet(p/'depth-0.bin');(p/'depth-status.json').write_text(json.dumps(dict(files=1,issued=1,io_errors=0,gpu_failures=0,ambiguous=False,pending_abandoned=False)))
            result=d.analyze_run(p,images=True);self.assertFalse(result['complete']);self.assertTrue((p/'depth-0-color.png').exists())
    def test_too_many_packets(self):
        with tempfile.TemporaryDirectory() as f:
            p=Path(f)
            for i in range(4):self.packet(p/f'depth-{i}.bin')
            with self.assertRaises(ValueError):d.analyze_run(p)
    def test_failure_stage_and_hresult_are_named(self):
        with tempfile.TemporaryDirectory() as f:
            p=Path(f);(p/'depth-status.json').write_text(json.dumps(dict(files=0,issued=0,io_errors=0,gpu_failures=1,ambiguous=False,pending_abandoned=False,failure_stage=5,failure_hresult=0x80070057,feature_level=0xA100,reader='ps_4_1')))
            report=d.analyze_run(p);self.assertFalse(report['complete']);self.assertEqual(report['status']['failure_stage_name'],'create_ps');self.assertEqual(report['status']['failure_hresult_hex'],'0x80070057')
    def test_qualification_requires_exact_sfc_feature_mode(self):
        with tempfile.TemporaryDirectory() as f:
            for level in (None,0xB000,0xA000):
                with self.assertRaisesRegex(ValueError,'SFC10_1'):self.qualification(Path(f),tested_feature_level=level)
            with self.assertRaisesRegex(ValueError,'SFC10_1'):self.qualification(Path(f),reader='cs_5_0')
    def test_explicit_101_pixel_qualification_accepted(self):
        with tempfile.TemporaryDirectory() as f:self.assertEqual(self.qualification(Path(f))['tested_feature_level'],0xA100)

if __name__=='__main__':unittest.main()
