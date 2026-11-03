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
    def channel(self):
        import ctypes as C
        class Memory:
            name='Local\\SFCBridge_'+'a'*32
            buffer=C.create_string_buffer(65536)
            view=C.addressof(buffer)
            def read(self,o,n):return C.string_at(self.view+o,n)
            def write(self,o,b):C.memmove(self.view+o,b,len(b))
        return Memory()
    def test_atomic_single_activation(self):
        from warm_start import initialize,OFFSET
        c=self.channel();initialize(c,123)
        activate(c,self.env(),c.name)
        import struct
        self.assertEqual(struct.unpack('<i',c.read(OFFSET+36,4))[0],2)
        self.assertEqual(c.read(OFFSET+64,104),packet(self.env(),c.name))
        with self.assertRaises(ValueError):activate(c,self.env(),c.name)
        with self.assertRaises(ValueError):initialize(c,123)
    def test_cancel_and_identity(self):
        from warm_start import initialize,cancel,ready,OFFSET
        import struct
        c=self.channel();initialize(c,123);self.assertIsNone(ready(c))
        c.write(OFFSET+44,struct.pack('<i',-1));self.assertIsNone(ready(c))
        c.write(OFFSET+40,struct.pack('<IIQ',456,1,789));self.assertEqual(ready(c),(789,456))
        wrong=self.env();wrong['SFC_D3D9_GAME_PID']='124'
        with self.assertRaises(ValueError):activate(c,wrong,c.name)
        with self.assertRaises(ValueError):activate(c,self.env(),'Local\\SFCBridge_'+'b'*32)
        cancel(c)
        with self.assertRaises(ValueError):activate(c,self.env(),c.name)
    def test_bootstrap_and_no_file_ticket(self):
        text=(ROOT/'tools/remix_runtime/run_return_game.py').read_text()
        self.assertLess(text.index('timing_relay.start_on_launch(pid)'),text.index('wait_component_ready(channel.snapshot'))
        native=(ROOT/'tools/d3d9_proof/d3d9_direct_host.cpp').read_text()
        self.assertLess(native.index('CreateDeviceEx('),native.index('warm_start::wait(root'))
        self.assertLess(native.index('warm_start::wait(root'),native.index('Renderer renderer('))
        source=(ROOT/'tools/m1_component/m1_component.cpp').read_text()
        start=source.index('extern "C" DWORD WINAPI M1StartW')
        self.assertLess(source.index('load_config(',start),source.index('g_live_scene.start(',start))
        self.assertIn('GetPrivateProfileStringW(L"m1",L"LiveChannel"',source)
        warm=(ROOT/'tools/d3d9_proof/warm_start.h').read_text()
        self.assertNotIn('renderer-activate.bin',warm)
        self.assertNotIn('renderer-ready.bin',warm)
        self.assertNotIn('renderer-cancel',warm)
