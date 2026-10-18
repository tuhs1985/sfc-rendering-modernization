from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/m1_component'))
import verify_light_state_bytes as lights

class LightAnchorTests(unittest.TestCase):
    def test_restores_normal_anchor_set(self):
        original=lights.engine.ANCHORS
        def verify(_):
            self.assertIs(lights.engine.ANCHORS,lights.ANCHORS)
            return {'result':'STATIC_PREFIXES_MATCH'}
        with mock.patch.object(lights.engine,'verify',side_effect=verify):
            result=lights.verify('unused')
        self.assertIs(lights.engine.ANCHORS,original)
        self.assertIn('not sampled',result['scope'])
    def test_restores_on_failure(self):
        original=lights.engine.ANCHORS
        with mock.patch.object(lights.engine,'verify',side_effect=ValueError('mismatch')):
            with self.assertRaises(ValueError):lights.verify('unused')
        self.assertIs(lights.engine.ANCHORS,original)
    def test_wrong_build_rejected_without_writing(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'client.bin';p.write_bytes(b'wrong build')
            with self.assertRaisesRegex(ValueError,'Unsupported client hash'):lights.verify(p)
            self.assertEqual(p.read_bytes(),b'wrong build')

if __name__=='__main__':unittest.main()
