import sys
import tempfile
from pathlib import Path
from unittest import TestCase

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools/remix_runtime'),str(ROOT/'tools/d3d9_proof')]
from warm_start import ACTIVATION,packet,activate
from owner_rebind import fnv

class WarmStartTests(TestCase):
    def env(self):
        return dict(SFC_D3D9_GAME_PID='123',SFC_D3D9_EXPECTED_MODEL='456',SFC_D3D9_EXPECTED_SOURCE='789',
                    SFC_D3D9_INITIAL_ASSET_MASK='f',SFC_D3D9_REBIND_COOKIE='abc',SFC_D3D9_ASSET_SHA256='12'*32,SFC_D3D9_OFFSET_X='-15.89')
    def test_layout_and_checksum(self):
        raw=packet(self.env(),'Local\\SFCBridge_'+'a'*32);fields=ACTIVATION.unpack(raw)
        self.assertEqual(len(raw),104);self.assertEqual(fields[:4],(0x31524157,1,104,123))
        self.assertEqual(fields[8:12],(456,789,15,0xabc));self.assertEqual(fields[-1],fnv(raw[:-8]))
    def test_invalid_identity_and_offset(self):
        for key,value in (('SFC_D3D9_GAME_PID','0'),('SFC_D3D9_EXPECTED_MODEL','0'),('SFC_D3D9_INITIAL_ASSET_MASK','0'),('SFC_D3D9_ASSET_SHA256','00'*32),('SFC_D3D9_OFFSET_X','nan')):
            env=self.env();env[key]=value
            with self.assertRaises(ValueError):packet(env,'Local\\SFCBridge_'+'a'*32)
        with self.assertRaises(ValueError):packet(self.env(),'wrong')
    def test_atomic_single_activation(self):
        with tempfile.TemporaryDirectory() as directory:
            activate(directory,self.env(),'Local\\SFCBridge_'+'a'*32)
            self.assertEqual((Path(directory)/'renderer-activate.bin').stat().st_size,104)
            self.assertFalse((Path(directory)/'renderer-activate.pending').exists())
            with self.assertRaises(ValueError):activate(directory,self.env(),'Local\\SFCBridge_'+'a'*32)
    def test_prewarm_is_before_game_graphics_wait(self):
        text=(ROOT/'tools/remix_runtime/run_return_game.py').read_text()
        self.assertLess(text.index('timing_relay.start_on_launch(pid)'),text.index('wait_component_ready(channel.snapshot'))
        native=(ROOT/'tools/d3d9_proof/d3d9_direct_host.cpp').read_text()
        self.assertLess(native.index('CreateDeviceEx('),native.index('warm_start::wait(root)'))
        self.assertLess(native.index('warm_start::wait(root)'),native.index('Renderer renderer('))
