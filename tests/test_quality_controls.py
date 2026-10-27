from pathlib import Path
import sys
import struct
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
from quality_controls import encode,Relay,DEFAULT
from material_controls import fnv

class QualityTests(unittest.TestCase):
    def test_wire_and_restoration(self):
        p=encode(b'[quality]\n');self.assertEqual(len(p),48);self.assertEqual(struct.unpack('<8I2fQ',p)[:10],(0x31544c51,1,0,1,8,0,1,0,0.,1.))
        self.assertEqual(struct.unpack_from('<Q',p,40)[0],fnv(p[:40]))
        self.assertEqual(p,encode(DEFAULT.with_name('rendering.example.toml').read_bytes()))
    def test_options_and_limits(self):
        p=encode(b'[quality]\nenabled=true\nmax_anisotropy=16\nanti_aliasing="temporal"\ndenoising=false\nmip_bias=-0.5\n')
        self.assertEqual(struct.unpack('<8I2fQ',p)[2:10],(1,1,16,3,0,0,-.5,1.))
        for s in ('supersampling=2.0','supersampling=true','mip_bias=nan','max_anisotropy=3','max_anisotropy=true','anti_aliasing="msaa8"','texture_filtering="point"','enabled=1','denoising=1','wat=0'):
            with self.subTest(s=s),self.assertRaises(ValueError):encode(('[quality]\n'+s).encode())
        with self.assertRaises(ValueError):encode(b' '*16385)
    def test_last_good_and_default_file_not_mutable_test_input(self):
        with tempfile.TemporaryDirectory() as root:
            d=Path(root);p=d/'q.toml';p.write_bytes(b'[quality]\nenabled=true\nmax_anisotropy=16\n');r=Relay(d,p)
            with patch('time.monotonic',return_value=1):r.poll()
            good=(d/'quality-controls.bin').read_bytes();p.write_bytes(b'[quality]\nsupersampling=2\n')
            with patch('time.monotonic',return_value=2):r.poll()
            self.assertEqual((d/'quality-controls.bin').read_bytes(),good)
            p.write_bytes(b'[quality]\n')
            with patch('time.monotonic',return_value=3):r.poll()
            self.assertEqual((d/'quality-controls.bin').read_bytes(),encode(b'[quality]\n'))
    def test_sdk_sampler_applied_and_recreated_outside_sfc(self):
        root=DEFAULT.parent.parent
        self.assertIn('info.filterMode=filter',(root/'ship_textured_asset.h').read_text())
        host=(root/'ship_live_host.cpp').read_text()
        self.assertIn('candidate.create(api,next,samplerRevision,qualitySettings.enabled?1:0)',host)
        self.assertLess(host.index('live GPU completion'),host.index('candidate.create(api,next,samplerRevision'))
