import importlib.util
from pathlib import Path
import unittest
from PIL import Image

p=Path(__file__).resolve().parents[1]/'tools/d3d9_proof/damage_materials.py'
spec=importlib.util.spec_from_file_location('damage_materials',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class DamageMaterialTests(unittest.TestCase):
    def test_exact_black_only_and_rgb_preserved(self):
        source=Image.new('RGB',(4,1));source.putdata([(0,0,0),(1,0,0),(0,0,1),(255,0,0)])
        before=source.tobytes();out=m.black_cutout(source)
        self.assertEqual(list(out.getdata()),[(0,0,0,0),(1,0,0,255),(0,0,1,255),(255,0,0,255)])
        self.assertEqual(source.tobytes(),before)
    def test_all_three_families(self):
        self.assertEqual(len(m.PAIRS),9);self.assertEqual(len({n.casefold() for pair in m.PAIRS for n in pair}),18)

if __name__=='__main__':unittest.main()
