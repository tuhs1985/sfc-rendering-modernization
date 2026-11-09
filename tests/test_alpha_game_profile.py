import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
from game_profile import signature,SIZES


class AlphaGraphicsProfileTests(unittest.TestCase):
    def inputs(self,w=1920,h=1080):
        return (f'[3D]\r\nWidth={w}\r\nHeight={h}\r\nzbuffer=1\r\n[Network]\r\nPlayerName=test\r\n'.encode(),
                f'[GeneralExt]\r\nDesktopResolution={w}x{h}\r\n[DirectX]\r\nResolution=h:{w}, v:{h}\r\nAntialiasing=8x\r\n'.encode())

    def test_supported_dimensions_same_other_bytes_protected(self):
        expected=signature(*self.inputs())
        for w,h in SIZES:
            a,b=self.inputs(w,h)
            self.assertEqual(signature(a.replace(b'PlayerName=test',b'PlayerName=changed'),b),expected)
            self.assertNotEqual(signature(a.replace(b'zbuffer=1',b'zbuffer=0'),b),expected)
            self.assertNotEqual(signature(a,b.replace(b'8x',b'4x')),expected)

    def test_unsupported_mismatched_missing_and_duplicate_fields(self):
        a,b=self.inputs()
        for x,y in (self.inputs(2560,1440),self.inputs(1280,360),(a,b.replace(b'h:1920',b'h:1600')),
                    (a+b'Width=1920\r\n',b.replace(b'Antialiasing=8x',b'Resolution=h:1920, v:1080')),
                    (a.replace(b'Height=1080\r\n',b''),b)):
            with self.assertRaises(ValueError):signature(x,y)


if __name__=='__main__':unittest.main()
