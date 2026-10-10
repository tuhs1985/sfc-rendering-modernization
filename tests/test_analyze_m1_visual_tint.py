import csv
import json
import tempfile
import unittest
from pathlib import Path

from tools.m1_component.analyze_m1_visual_tint import analyze


class VisualTintAnalysisTests(unittest.TestCase):
    def test_coherent_target_and_release_do_not_claim_visible_success(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            summary = dict(
                geometry_hook_enabled=False, hooks_restored=True, log_truncated=False,
                event_log_bytes=1024, rejected_semantics=0, owner_overflow=0, thread_overflow=0,
                visual_tint=dict(enabled=True, target_owner_id=1, delay_ms=5000,
                                 duration_ms=10000, applied=1, restored=1,
                                 renderer_replaced=0, active_scopes=0, restore_failed=0, rejected=0),
            )
            base = dict(event='model0', owner_id=1, elapsed_ms=1000, tint_applied=0,
                        return_address='0x0042FDD5', model0_vtable='0x007983E8',
                        visual_vtable='0x007985A4', ship='0x1000', source='0x2000',
                        effective_source='0x3000', tint_entries=2, tint_elapsed_ms=5000,
                        tint_original_rgb='0x00FFFFFF')
            rows = [base, dict(base, elapsed_ms=5000, tint_applied=1),
                    dict(base, elapsed_ms=16000), dict(base, owner_id=2)]

            def save():
                (directory / 'M1-A-summary.json').write_text(json.dumps(summary))
                (directory / 'controller.stdout.txt').write_text('hook_bytes_restored=true\n')
                with (directory / 'M1-A-events.csv').open('w', newline='') as handle:
                    writer = csv.DictWriter(handle, fieldnames=base.keys())
                    writer.writeheader()
                    writer.writerows(rows)

            save()
            result = analyze(directory)
            self.assertEqual(result['result'], 'TARGETED_TINT_INSTRUMENTATION_COHERENT')
            self.assertIn('UNADJUDICATED', result['visible_effect'])
            rows[1]['owner_id'] = 2
            save()
            self.assertEqual(analyze(directory)['result'], 'REVIEW_REQUIRED')
            rows[1]['owner_id'] = 1
            summary['visual_tint']['active_scopes'] = 1
            save()
            self.assertEqual(analyze(directory)['result'], 'REVIEW_REQUIRED')


if __name__ == '__main__':
    unittest.main()
