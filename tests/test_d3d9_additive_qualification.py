from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
from additive_qualification import delivery_window

class DeliveryGuardTests(unittest.TestCase):
    def test_fixed_window_passes_only_at_guard(self):
        self.assertEqual(delivery_window('GAME_DELIVERY_WINDOW frames=600 draws=540'),(600,540))
    def test_old_success_count_alone_is_not_ready(self):
        with self.assertRaises(ValueError):delivery_window('GAME_IMAGE_PIXELS changed=18596 border_untouched=1')
    def test_low_delivery_short_window_and_impossible_counts_reject(self):
        for value in ('frames=600 draws=539','frames=180 draws=175','frames=600 draws=601'):
            with self.assertRaises(ValueError):delivery_window('GAME_DELIVERY_WINDOW '+value)
