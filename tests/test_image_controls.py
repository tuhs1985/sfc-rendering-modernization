from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
from image_controls import encode,Relay,DEFAULT
from material_controls import fnv

class ImageTests(unittest.TestCase):
    def test_default_disabled_and_checksum(self):
        p=encode(b'[image]\n');self.assertEqual(len(p),48)
        self.assertEqual(struct.unpack('<6I4fQ',p)[:10],(0x31474d49,1,0,1,1,50,0.,1.,1.,1.))
        self.assertEqual(struct.unpack_from('<Q',p,40)[0],fnv(p[:40]))
        # Sponsor's active file is mutable; factory tests must use restore example.
        self.assertEqual(p,encode(DEFAULT.with_name('image.example.toml').read_bytes()))
    def test_modes_and_controls(self):
        p=encode(b'[image]\nenabled=true\ntone_mapping="global"\nautomatic_exposure=false\nbrightness=25\nexposure_ev=-1.0\ncontrast=1.5\ngamma=2.0\nsaturation=0.0\n')
        self.assertEqual(struct.unpack('<6I4fQ',p)[2:10],(1,0,0,25,-1.,1.5,2.,0.))
    def test_reject_invalid(self):
        for setting in ('enabled=1','automatic_exposure="off"','tone_mapping="foo"','brightness=true','brightness=2.5','brightness=101','gamma=0','gamma=nan','contrast=inf','saturation=-1','exposure_ev=5','wat=1'):
            with self.subTest(setting=setting),self.assertRaises(ValueError):encode(('[image]\n'+setting).encode())
        with self.assertRaises(ValueError):encode(b' '*16385)
        with self.assertRaises(ValueError):encode(b'[material]\n')
    def test_last_good_bounded_restore(self):
        with tempfile.TemporaryDirectory() as root:
            d=Path(root);p=d/'image.toml';p.write_bytes(b'[image]\nenabled=true\ngamma=2\n');r=Relay(d,p)
            with patch('time.monotonic',return_value=1):r.poll()
            good=(d/'image-controls.bin').read_bytes()
            p.write_bytes(b'[image]\ngamma=0\n')
            with patch('time.monotonic',return_value=2):r.poll()
            self.assertEqual((d/'image-controls.bin').read_bytes(),good)
            p.write_bytes(b'[image]\n')
            with patch('time.monotonic',return_value=3):r.poll()
            self.assertEqual((d/'image-controls.bin').read_bytes(),encode(b'[image]\n'))
            r.accepted=256;p.write_bytes(b'[image]\ngamma=3\n')
            with patch('time.monotonic',return_value=4):r.poll()
            self.assertEqual(r.accepted,256)
    def test_worker_integration_and_no_double_grade(self):
        root=DEFAULT.parent.parent
        host=(root/'ship_live_host.cpp').read_text()
        self.assertLess(host.index('live GPU completion'),host.index('imageAdjust.draw'))
        self.assertLess(host.index('image completion'),host.index('publishCompleted'))
        self.assertIn('self.images.poll()', (root/'live_lights.py').read_text())
        self.assertIn('mode?values[1]:1.f',(root/'remix_image_controls.h').read_text())

if __name__=='__main__':unittest.main()
