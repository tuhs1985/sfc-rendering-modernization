from pathlib import Path
import json
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/remix_runtime'))
from rendering_config import DEFAULT,EXAMPLE,parse,scoped
import image_controls
import material_controls
import quality_controls


class RenderingConfigTests(unittest.TestCase):
    def test_single_authority_and_known_sections(self):
        self.assertEqual(DEFAULT,material_controls.DEFAULT)
        self.assertEqual(DEFAULT,image_controls.DEFAULT)
        self.assertEqual(DEFAULT,quality_controls.DEFAULT)
        self.assertEqual(set(parse(DEFAULT.read_bytes())),{'material','image','quality','remix'})
        for raw in (b'[wrong]\n',b'image=1\n',b' '*16385):
            with self.assertRaises(ValueError):parse(raw)

    def test_combined_profile_preserves_each_parser_value(self):
        material=b'[material]\nroughness=0.4\nemissive_intensity=5\n'
        image=b'[image]\nenabled=true\ngamma=0.7\n'
        quality=b'[quality]\nenabled=true\nmax_anisotropy=16\n'
        native=b'[remix]\n"rtx.bloom.enable"=false\n'
        raw=material+image+quality+native
        self.assertEqual(material_controls.encode(raw),material_controls.encode(material))
        self.assertEqual(image_controls.encode(raw),image_controls.encode(image,native))
        self.assertEqual(quality_controls.encode(raw),quality_controls.encode(quality))

    def test_unrelated_edits_and_spacing_do_not_invalidate_materials(self):
        first=b'[material]\nroughness=.4\n[image]\ncontrast=1\n[remix]\n"rtx.bloom.enable"=true\n'
        first=first.replace(b'roughness=.4',b'roughness=0.4')
        second=first.replace(b'contrast=1',b'contrast=1.2').replace(b'enable"=true',b'enable"=false')
        self.assertEqual(scoped(first,'material'),scoped(second,'material'))
        self.assertEqual(scoped(first,'material'),scoped(b'# formatted\n[material]\n roughness = 0.4\n','material'))
        self.assertNotEqual(scoped(first,'image','remix'),scoped(second,'image','remix'))

    def test_factory_restore_and_exact_native_names(self):
        raw=EXAMPLE.read_bytes()
        self.assertEqual(material_controls.encode(raw),material_controls.encode(b'[material]\n'))
        self.assertEqual(quality_controls.encode(raw),quality_controls.encode(b'[quality]\n'))
        self.assertEqual(image_controls.encode(raw),image_controls.encode(b'[image]\n',b'[remix]\n'))
        self.assertEqual(set(parse(raw)['remix']),set(image_controls.REMIX_DEFAULTS))


if __name__=='__main__':unittest.main()
