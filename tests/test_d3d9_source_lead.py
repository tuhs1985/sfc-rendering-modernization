from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools/d3d9_proof'))
from analyze_source_lead import assess, HEADER, RECORD
import test_d3d9_source_timing as timing

SESSION = timing.SESSION


class SourceLeadTests(unittest.TestCase):
    def records(self, rows):
        h, _, _ = timing.SourceTimingTests().packet()
        h[6] = len(rows)
        h[8] = max(r[2] for r in rows)
        return HEADER.pack(*h) + b''.join(RECORD.pack(*r) for r in rows)

    def test_exact_pair_only(self):
        _, a, b = timing.SourceTimingTests().packet()
        report = assess(self.records([a, b]), SESSION, 77)
        self.assertEqual(report['observed_frames'], 1)
        self.assertEqual(report['owners'][0]['last_offer_to_present_ms']['min'], 40)
        b[1] += 1
        self.assertEqual(assess(self.records([a, b]), SESSION, 77)['qualified_exact_pairs'], 0)

    def test_changed_state_not_qualified(self):
        _, a, b = timing.SourceTimingTests().packet()
        b[12] += 1
        report = assess(self.records([a, b]), SESSION, 77)
        self.assertEqual(report['qualified_exact_pairs'], 0)
        self.assertEqual(report['source_validation']['pose_camera_changed_between_stages'], 1)

    def test_latest_observed_owner_and_camera_disagreement(self):
        _, a, b = timing.SourceTimingTests().packet()
        c, d = a.copy(), b.copy()
        c[3] = d[3] = 5
        c[8] = d[8] = 120
        c[9] = d[9] = 140
        c[12] = d[12] = 999
        report = assess(self.records([a, c, b, d]), SESSION, 77)
        self.assertEqual(report['latest_observed_owner_to_first_present_ms']['min'], 10)
        self.assertEqual(report['frames_with_multiple_camera_hashes'], 1)
        self.assertEqual(report['observed_owner_counts'], {'2': 1})

    def test_repeated_frame_not_counted_as_fresh(self):
        _, a, b = timing.SourceTimingTests().packet()
        c = a.copy()
        c[2] = 3
        self.assertEqual(assess(self.records([a, b, c]), SESSION, 77)['qualified_exact_pairs'], 0)


if __name__ == '__main__':
    unittest.main()
