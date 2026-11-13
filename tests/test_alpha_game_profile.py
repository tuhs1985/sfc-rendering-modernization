import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
from game_profile import signature,SIZES
from tools.release.qualify_graphics_adapter import matching_setting, wrapper_config


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


class GraphicsAdapterMatchTests(unittest.TestCase):
    def probe(self, observations):
        attempted = []

        def run(setting):
            attempted.append(setting)
            luids = observations[setting]
            return dict(policy=setting, process_exit=0, directdraw_draw=True,
                        actual_gpu_names=['Same GPU name'], actual_gpu_luids=luids,
                        d3d11_observed=True, dxgi_inventory=[
                            'DXGI index=0 flags=0 luid=0:11 name=Same GPU name',
                            'DXGI index=1 flags=0 luid=0:22 name=Same GPU name',
                            'DXGI index=2 flags=2 luid=0:33 name=Software',
                        ])
        return attempted, run

    def test_existing_verified_setting_needs_one_probe(self):
        attempted, probe = self.probe({'1': ['0:22']})
        setting, _ = matching_setting('0:22', '1', probe)
        self.assertEqual(setting, '1')
        self.assertEqual(attempted, ['1'])

    def test_reordered_ordinals_and_identical_names_are_resolved_by_actual_luid(self):
        attempted, probe = self.probe({'1': ['0:11'], 'all': ['0:11'], '2': ['0:22']})
        setting, _ = matching_setting('0:22', '1', probe)
        self.assertEqual(setting, '2')
        self.assertEqual(attempted, ['1', 'all', '2'])

    def test_ambiguous_and_wrong_devices_produce_no_setting(self):
        attempted, probe = self.probe({'1': ['0:11'], 'all': ['0:11', '0:22'], '2': ['0:11']})
        setting, results = matching_setting('0:22', '1', probe)
        self.assertIsNone(setting)
        self.assertEqual(attempted, ['1', 'all', '2'])
        self.assertEqual(len(results), 3)

    def test_config_preserves_other_bytes_and_rejects_ambiguous_input(self):
        original = b'; Adapters=1\r\n[General]\r\nAdapters=1\r\nOutputAPI=d3d11_fl10_1\r\n'
        self.assertEqual(wrapper_config(original, '2'), original.replace(b'\nAdapters=1', b'\nAdapters=2'))
        with self.assertRaisesRegex(ValueError, 'Ambiguous'):
            wrapper_config(original + b'Adapters=all\r\n', '2')


if __name__=='__main__':unittest.main()
