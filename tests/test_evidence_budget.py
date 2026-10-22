import pathlib
import sys
import unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
from evidence_budget import AGGREGATE_BYTES
import broad_capture


class EvidenceBudget(unittest.TestCase):
    def test_sponsor_aggregate_is_decimal_twenty_gb(self):
        self.assertEqual(AGGREGATE_BYTES,20_000_000_000)
        self.assertEqual(broad_capture.OVERALL,AGGREGATE_BYTES)

    def test_per_capture_not_raised_with_aggregate(self):
        self.assertEqual(broad_capture.HARD,2_000_000_000)


if __name__=='__main__':unittest.main()
