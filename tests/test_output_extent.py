from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
from output_extent import requirements,MAX_BYTES


class OutputExtentTests(unittest.TestCase):
    def test_checked_memory_and_unchanged_queue_depth(self):
        for width,height,total in ((1920,1080,132710400),(2560,1440,235929600),(3840,2160,530841600),(1280,360,29491200),(1031,517,34113728)):
            with self.subTest(extent=(width,height)):
                value=requirements(width,height)
                self.assertEqual(value['bytes'],total)
                self.assertEqual(value['pool_slots'],2)
                self.assertLessEqual(total,MAX_BYTES)

    def test_invalid_dimensions_do_not_overflow_or_allocate(self):
        for width,height in ((0,1080),(1920,0),(-1,1),(3841,2160),(3840,2161),(2**32-1,2**32-1),(True,1080),(1.0,1)):
            with self.assertRaises(ValueError):requirements(width,height)
