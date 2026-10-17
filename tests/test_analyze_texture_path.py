import json
from pathlib import Path
import tempfile
import unittest
import test_export_mesh_textures as recovery_tests
from analyze_texture_path import classify, inspect


class TexturePathTests(unittest.TestCase):
    def test_classifies_branch_without_claiming_pass_count(self):
        self.assertEqual(classify(511, 0), 'FALLBACK_FAMILY_EXACT_MODE_UNOBSERVED')
        self.assertEqual(classify(511, 1), 'MULTITEXTURE_MODE0')
        self.assertEqual(classify(0, 1), 'PRIMARY_ONLY_GATE')

    def test_missing_old_fields_remain_unknown(self):
        self.assertEqual(classify(None, None), 'UNOBSERVED')
        self.assertEqual(classify(511, None), 'UNOBSERVED')

    def test_invalid_flags_rejected(self):
        for pair in ((True, 0), (511, False), (-1, 0), (511, 256)):
            with self.assertRaises(ValueError): classify(*pair)

    def test_same_epoch_review_is_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            capture, _, refs = recovery_tests.TextureRecoveryTests().fixture(Path(tmp))
            refs.update(manager_secondary_path_word=511, manager_multitexture_flag=0)
            path = capture/'TEXTURE-EXPORT-001.json'; path.write_text(json.dumps(refs))
            before = {p: p.read_bytes() for p in capture.iterdir() if p.is_file()}
            report = inspect(capture)
            self.assertEqual(report['branch_family'], 'FALLBACK_FAMILY_EXACT_MODE_UNOBSERVED')
            self.assertEqual(report['exact_fallback_passes'], 'UNOBSERVED')
            self.assertTrue(all(p.read_bytes() == b for p, b in before.items()))

    def test_cross_epoch_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            capture, _, refs = recovery_tests.TextureRecoveryTests().fixture(Path(tmp))
            refs['frame'] += 1
            (capture/'TEXTURE-EXPORT-001.json').write_text(json.dumps(refs))
            with self.assertRaises(ValueError): inspect(capture)

    def test_fallback_prediction_uses_both_eligibility_inputs(self):
        for mask, previous, expected in ((1, 0, 'MODES_2_THEN_1_REQUESTED'),
                                         (1, 1, 'MODE_1_ONLY_REQUESTED'),
                                         (2, 1, 'MODES_2_THEN_1_REQUESTED'),
                                         (0, 0, 'MODE_1_ONLY_REQUESTED')):
            with self.subTest(mask=mask, previous=previous), tempfile.TemporaryDirectory() as tmp:
                capture, _, refs = recovery_tests.TextureRecoveryTests().fixture(Path(tmp))
                refs.update(manager_secondary_path_word=511, manager_multitexture_flag=0,
                            manager_fallback_validation_mask=mask, manager_previous_alpha_test_flag=previous)
                (capture/'TEXTURE-EXPORT-001.json').write_text(json.dumps(refs))
                result = inspect(capture)
                self.assertEqual(result['static_fallback_request_prediction'], expected)
                self.assertEqual(result['exact_fallback_passes'], 'UNOBSERVED')
