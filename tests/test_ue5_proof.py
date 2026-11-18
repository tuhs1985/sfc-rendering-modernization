import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
from PIL import Image


PATH = Path(__file__).resolve().parents[1] / 'tools/ue5_proof/verify.py'
SPEC = importlib.util.spec_from_file_location('ue_proof_verify', PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class UEProofReferenceTests(unittest.TestCase):
    def fixture(self, folder):
        pixels = np.array([[[0, 0, 255, 255], [0, 255, 0, 255]],
                           [[255, 0, 0, 255], [255, 255, 255, 255]]], dtype='uint8')
        (folder / 'source.bgra').write_bytes(pixels.tobytes())
        return dict(frames=[dict(model=np.eye(4).tolist(), view=np.eye(4).tolist(),
                                projection=np.eye(4).tolist(), viewport=[3, 2, 8, 8])],
                    positions=[[-1, -1, .5], [1, -1, .5], [-1, 1, .5], [1, 1, .5]],
                    corners=[[i, [0, 0, 1], uv] for i, uv in enumerate([[0, 1], [1, 1], [0, 0], [1, 0]])],
                    indices=[0, 1, 2, 2, 1, 3],
                    groups=[dict(first_index=0, index_count=6, primary=dict(filename='source'))],
                    images=dict(source=dict(file='source.bgra', width=2, height=2)))

    def test_asymmetric_source_has_original_top_row_and_colour_channels(self):
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            pixels, coverage, interior = MODULE.reference(self.fixture(folder), folder)
            self.assertEqual(pixels[1, 1].tolist(), [255, 0, 0])
            self.assertEqual(pixels[1, 6].tolist(), [0, 255, 0])
            self.assertEqual(pixels[6, 1].tolist(), [0, 0, 255])
            self.assertEqual(pixels[6, 6].tolist(), [255, 255, 255])
            self.assertTrue(coverage.all())
            self.assertGreater(interior.sum(), 20)

    def test_actual_file_boundary_detects_vertical_flip(self):
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            scene = self.fixture(folder)
            path = folder / 'scene.json'
            path.write_text(json.dumps(scene), encoding='utf-8')
            pixels, _, _ = MODULE.reference(scene, folder)
            image = folder / 'rendered.bmp'
            Image.fromarray(pixels).save(image)
            self.assertEqual(MODULE.verify(path, image, folder)['within_three_levels'], 1)
            Image.fromarray(pixels[::-1]).save(image)
            self.assertLess(MODULE.verify(path, image, folder)['within_three_levels'], .1)

    def test_output_extent_must_match_capture(self):
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            path = folder / 'scene.json'
            path.write_text(json.dumps(self.fixture(folder)), encoding='utf-8')
            Image.new('RGB', (9, 8)).save(folder / 'wrong.bmp')
            with self.assertRaisesRegex(ValueError, 'dimensions'):
                MODULE.verify(path, folder / 'wrong.bmp', folder)


if __name__ == '__main__':
    unittest.main()
