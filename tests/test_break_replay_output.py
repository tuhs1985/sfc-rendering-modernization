"""Returned-image qualification must not confuse API success with shaded debris."""
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('break_replay',ROOT/'tools/remix_ingest/run_break_replay.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ReturnedDebrisTests(unittest.TestCase):
    def output(self,folder,colors,depth):
        prefix=struct.pack('<2I',2,1)
        (folder/'returned-0-0.raw32').write_bytes(prefix+bytes(colors))
        (folder/'returned-0-1.raw32').write_bytes(prefix+struct.pack('<2f',*depth))

    def test_flat_background_with_valid_hull_is_not_shaded(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);self.output(p,[5,5,5,255]*2,[-1234,.5])
            self.assertEqual(module.inspect_output(p,0)['shaded_hull_pixels'],0)

    def test_colour_outside_hull_is_not_debris(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);self.output(p,[5,5,5,255,100,100,100,255],[.5,-1234])
            result=module.inspect_output(p,0)
            self.assertTrue(result['varied_colour'])
            self.assertEqual(result['shaded_hull_pixels'],0)

    def test_shaded_hull_is_observed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);self.output(p,[5,5,5,255,100,80,60,255],[-1234,.5])
            self.assertEqual(module.inspect_output(p,0)['shaded_hull_pixels'],1)

    def test_mismatched_output_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);self.output(p,[5,5,5,255]*2,[-1234,.5])
            (p/'returned-0-1.raw32').write_bytes(struct.pack('<2I',1,2)+b'\0'*8)
            with self.assertRaises(ValueError):module.inspect_output(p,0)


if __name__=='__main__':unittest.main()
