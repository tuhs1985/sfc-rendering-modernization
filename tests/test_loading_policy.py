from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/remix_runtime'))
from loading_policy import configure,KEYS


class LoadingPolicyTests(unittest.TestCase):
    def test_inherited_inputs_not_assumed_to_be_wrapper_environment(self):
        environment={'unrelated':'preserved'}
        text,receipt=configure('inherit',environment,offline=False)
        self.assertEqual(text,'');self.assertEqual(environment,{'unrelated':'preserved'})
        self.assertTrue(all(value is None for value in receipt['supplied_environment'].values()))

    def test_async_and_blocking_override_native_inputs_not_images(self):
        for mode,value in (('async','1'),('blocking','0')):
            environment={key:'inherited-conflict' for key in KEYS}
            text,receipt=configure(mode,environment,offline=True)
            self.assertEqual(environment['RTX_ENABLE_ASYNC_COMPILATION'],value)
            self.assertEqual(environment['DXVK_ASYNC_ASSET_LOADING'],value)
            self.assertEqual(environment['RTX_ASYNC_SHADER_PREWARMING'],'1')
            self.assertEqual(environment['DXVK_WAIT_ASYNC_TEXTURES'],'0')
            self.assertEqual(len(receipt['supplied_config']),5)
            self.assertNotIn('enableReplacement',text)
            self.assertNotIn('preload_textures',text)

    def test_experiments_refused_for_game(self):
        for mode in ('async','blocking','rtxio','unknown'):
            with self.assertRaises(ValueError):configure(mode,{},offline=False)

    def test_rtxio_uses_vendor_path_without_changing_other_loading_controls(self):
        environment={'DXVK_WAIT_ASYNC_TEXTURES':'0','unrelated':'kept'}
        text,receipt=configure('rtxio',environment,offline=True)
        self.assertEqual(environment,{'DXVK_WAIT_ASYNC_TEXTURES':'0','unrelated':'kept','DXVK_USE_RTXIO':'1'})
        self.assertEqual(receipt['supplied_config'],{'rtx.io.enabled':True,'rtx.io.useAsyncQueue':True})
        self.assertNotIn('shader',text)

    def test_snapshot_is_one_existing_readback_not_render_thread_work(self):
        source=(ROOT/'tools/remix_runtime/return_fixture.cpp').read_text()
        self.assertEqual(source.count('"fixture-ship.bmp"'),1)
        self.assertIn('if(!imageSample&&cohortSettled',source)
