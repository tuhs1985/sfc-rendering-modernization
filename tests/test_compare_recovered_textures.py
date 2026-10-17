import sys
from pathlib import Path
import unittest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools/m1_component'))
from compare_recovered_textures import difference


class PixelComparisonTests(unittest.TestCase):
    def test_exact_palette_decode(self):
        palette = Image.new('P', (2, 2))
        palette.putpalette([10, 20, 30]+[0]*765)
        a = palette.convert('RGBA')
        result = difference(a, a.copy())
        self.assertTrue(result['exact_rgb'])
        self.assertTrue(result['alpha_exact'])
        self.assertEqual(result['changed_rgb_pixels'], 0)

    def test_known_error_and_alpha_are_separate(self):
        a = Image.new('RGBA', (2, 1), (10, 20, 30, 255))
        b = a.copy(); b.putpixel((0, 0), (12, 24, 36, 128))
        result = difference(a, b)
        self.assertEqual(result['changed_rgb_pixels'], 1)
        self.assertEqual(result['mean_absolute_error_rgb'], [1, 2, 3])
        self.assertEqual(result['maximum_absolute_error_rgb'], [2, 4, 6])
        self.assertFalse(result['alpha_exact'])

    def test_resolution_change_not_silently_resized(self):
        with self.assertRaises(ValueError):
            difference(Image.new('RGB', (2, 2)), Image.new('RGB', (1, 1)))


if __name__ == '__main__': unittest.main()
