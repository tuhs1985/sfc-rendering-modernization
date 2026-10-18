from pathlib import Path
import ctypes as C
import json
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
import live_return as live

class LiveReturnTests(unittest.TestCase):
    def test_textured_observation_stays_on_until_shutdown(self):
        from run_return_game import observation_phase
        for t in (0,29.9,30,44.9,45,59.9,60,89.9):
            self.assertEqual(observation_phase(t,continuous=True),0)
        self.assertEqual([observation_phase(t) for t in (0,30,45,60)],[0,1,2,3])
    def test_sdk_present_window_tracks_output_resolution(self):
        source=(Path(live.__file__).parent/'ship_live_host.cpp').read_text()
        self.assertIn('WS_POPUP,0,0,outputWidth,outputHeight',source)
        self.assertIn('GetClientRect(window,&client)',source)
        self.assertIn('actual.BackBufferWidth!=outputWidth||actual.BackBufferHeight!=outputHeight',source)
        self.assertIn('SetConfigVariable("rtx.resolutionScale","1.0")',source)
    def test_visible_mask_uses_native_viewport_not_corner(self):
        import numpy as np
        from qualify_live_return import projected_display_mask
        mask=projected_display_mask(np.ones((256,256),dtype=bool),(200,30,1720,1020))
        self.assertEqual(int(mask.sum()),1720*1020)
        self.assertFalse(mask[:30].any());self.assertFalse(mask[:,:200].any())
        self.assertTrue(mask[30:1050,200:1920].all())
    def test_visible_mask_rejects_outside_frame(self):
        import numpy as np
        from qualify_live_return import projected_display_mask
        with self.assertRaisesRegex(ValueError,'viewport'):projected_display_mask(np.ones((256,256),dtype=bool),(200,30,1920,1080))
    def test_textured_footprint_rejects_shift_and_background(self):
        import numpy as np
        from qualify_live_return import textured_footprint
        mask=np.zeros((100,100),dtype=bool);mask[20:60,20:60]=True
        self.assertTrue(textured_footprint(mask,mask)['qualified'])
        self.assertFalse(textured_footprint(mask,np.roll(mask,10,axis=1))['qualified'])
        self.assertFalse(textured_footprint(mask,np.ones_like(mask))['qualified'])
    def test_known_hash(self):
        self.assertEqual(live.fnv(b''),14695981039346656037)
        self.assertEqual(live.fnv(b'a'),0xaf63dc4c8601ec8c)
    def test_telemetry_exact_native_offsets(self):
        memory=C.create_string_buffer(4096);address=C.addressof(memory)
        offsets=[512+112,512+116,512+120]+list(range(1024+560,1024+592,4))
        for i,offset in enumerate(offsets):C.c_int32.from_address(address+offset).value=i+1
        self.assertEqual(list(live.telemetry(address).values()),list(range(1,12)))
    def test_private_mode_cannot_mix_observation(self):
        result=subprocess.run([sys.executable,str(Path(live.__file__).with_name('run_return_game.py')),'--private-ship','--observation-only'],capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,2);self.assertNotIn('Traceback',result.stderr)
    def test_private_mode_cannot_mix_depth(self):
        result=subprocess.run([sys.executable,str(Path(live.__file__).with_name('run_return_game.py')),'--private-ship','--depth-snapshots'],capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,2)
    def test_visible_mode_cannot_mix_private(self):
        result=subprocess.run([sys.executable,str(Path(live.__file__).with_name('run_return_game.py')),'--visible-ship','--private-ship'],capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,2)
    def test_textured_mode_cannot_mix_visible(self):
        result=subprocess.run([sys.executable,str(Path(live.__file__).with_name('run_return_game.py')),'--textured-ship','--visible-ship'],capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,2)
    def test_textured_mode_requires_own_qualification(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'q.json';path.write_text(json.dumps({'result':'OFFLINE_PRIVATE_RETURN_QUALIFIED','source_hashes':{},'binaries':{},'visible_camera_qualified':True}))
            with mock.patch.object(live,'QUALIFICATION',path),mock.patch.object(live,'source_hashes',return_value={}),mock.patch.object(live,'binary_hashes',return_value={}):
                with self.assertRaisesRegex(ValueError,'Textured'):live.require_qualification(visible=True,textured=True)
    def test_prepared_image_requires_own_qualification(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'q.json';path.write_text(json.dumps({'result':'OFFLINE_PRIVATE_RETURN_QUALIFIED','source_hashes':{},'binaries':{},'visible_camera_qualified':True,'textured_delivery_qualified':True}))
            with mock.patch.object(live,'QUALIFICATION',path),mock.patch.object(live,'source_hashes',return_value={}),mock.patch.object(live,'binary_hashes',return_value={}):
                with self.assertRaisesRegex(ValueError,'Prepared'):live.require_qualification(visible=True,textured=True,capture_image=True)
    def test_visible_mode_needs_pixel_qualification(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'q.json';path.write_text(json.dumps({'result':'OFFLINE_PRIVATE_RETURN_QUALIFIED','source_hashes':{},'binaries':{}}))
            with mock.patch.object(live,'QUALIFICATION',path),mock.patch.object(live,'source_hashes',return_value={}),mock.patch.object(live,'binary_hashes',return_value={}):
                with self.assertRaisesRegex(ValueError,'pixel'):live.require_qualification(visible=True)
    def test_stale_source_qualification_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'q.json';path.write_text(json.dumps({'result':'OFFLINE_PRIVATE_RETURN_QUALIFIED','source_hashes':{'a':'old'},'binaries':{}}))
            with mock.patch.object(live,'QUALIFICATION',path),mock.patch.object(live,'source_hashes',return_value={'a':'new'}):
                with self.assertRaisesRegex(ValueError,'stale'):live.require_qualification()
    def test_stale_binary_qualification_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'q.json';path.write_text(json.dumps({'result':'OFFLINE_PRIVATE_RETURN_QUALIFIED','source_hashes':{},'binaries':{'a':'old'}}))
            with mock.patch.object(live,'QUALIFICATION',path),mock.patch.object(live,'source_hashes',return_value={}),mock.patch.object(live,'binary_hashes',return_value={'a':'new'}):
                with self.assertRaisesRegex(ValueError,'stale'):live.require_qualification()
    def test_unseeded_worker_has_no_template_fallback(self):
        class Empty:
            name='Local\\SFCBridge_'+'a'*32
            def asset_transfer(self,slot):return None
            def sample_owner(self,index):return None
        with tempfile.TemporaryDirectory() as folder,mock.patch('present_calibration.SceneChannel',return_value=Empty()):
            receiver=live.FreshReceiver(folder);receiver.context('return',55);receiver.drain()
            self.assertIsNone(receiver.selected);self.assertFalse((Path(folder)/'live-asset.seed').exists())

if __name__=='__main__':unittest.main()
