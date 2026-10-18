import json
from pathlib import Path
import sys
import tempfile
import unittest

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
from analyze_blender_uv import imported_uvs, corners, label


class BlenderUvCompareTests(unittest.TestCase):
    def test_exact_import_and_v_flip_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'quad.obj'
            path.write_text('v 0 1 2\nvt .25 .125\nusemtl group_45\nf 1/1/1 1/1/1 1/1/1\n')
            row = ['group_45', [0, 1, 2], [.25, .125]]
            self.assertEqual(imported_uvs(path, [row]*3), 3)
            for bad in (['group_45', [0, 1, 2], [.25, .875]],
                        ['group_46', [0, 1, 2], [.25, .125]],
                        ['group_45', [0, 2, 1], [.25, .125]]):
                with self.assertRaises(ValueError):
                    imported_uvs(path, [row, row, bad])

    def test_corner_origin_labels(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'corners.png'
            image = Image.new('RGB', (4, 4))
            colors = [(128, 5, 5), (5, 128, 5), (5, 5, 128), (128, 128, 5)]
            for y in range(4):
                for x in range(4):
                    image.putpixel((x, y), colors[2*(y>=2)+(x>=2)])
            image.save(path)
            self.assertEqual(label(corners(path)), ['red', 'green', 'blue', 'yellow'])


if __name__ == '__main__':
    unittest.main()
