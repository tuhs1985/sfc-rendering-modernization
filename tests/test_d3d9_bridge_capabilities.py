from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/d3d9_proof'))
from probe_bridge_api import classify
import run_intercept


def fixture(copy=0,external=0):
    return ('INITIALIZE result=0 version=0.6.4\n'
        f'CAPABILITIES copy_output={copy} external_swapchain={external} vk_image=0 set_default_output=0 request_picking=0 setup_camera=0 create_mesh=1 present=0\n'
        'PROBE_DONE device_refs=0 api_refs=0 sdk_mesh_calls=0\n')


class BridgeCapabilitiesTests(unittest.TestCase):
    def test_missing_outputs_is_specific_blocker(self):
        result=classify(fixture());self.assertEqual(result['status'],'BLOCKED_NORMAL_BRIDGE_OUTPUT_ENTRYPOINTS_ABSENT')
        self.assertEqual(result['sdk_mesh_calls'],0)

    def test_entrypoints_not_transfer_success(self):
        for copy,external in ((1,0),(0,1),(1,1)):
            with self.subTest(copy=copy,external=external):self.assertEqual(classify(fixture(copy,external))['status'],'OUTPUT_ENTRYPOINT_PRESENT_NOT_TRANSFER_QUALIFIED')

    def test_disabled_interface_not_missing_output_proof(self):
        with self.assertRaises(ValueError):classify(fixture().replace('result=0','result=11'))

    def test_version_and_ambiguous_initialization_reject(self):
        for text in (fixture().replace('0.6.4','0.7.0'),fixture()+'INITIALIZE result=0 version=0.6.4\n'):
            with self.assertRaises(ValueError):classify(text)

    def test_incomplete_duplicate_or_invalid_table_reject(self):
        for text in (fixture().replace(' vk_image=0',''),fixture().replace('vk_image=0','vk_image=2'),
                     fixture().replace('vk_image=0','vk_image=0 vk_image=0'),fixture()+fixture().splitlines()[1]+'\n'):
            with self.subTest(text=text),self.assertRaises(ValueError):classify(text)

    def test_incomplete_lifecycle_or_mesh_calls_reject(self):
        for text in (fixture().replace('api_refs=0','api_refs=1'),fixture().replace('sdk_mesh_calls=0','sdk_mesh_calls=1')):
            with self.assertRaises(ValueError):classify(text)

    def test_private_config_uses_confirmed_trex_path(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'.trex').mkdir();case=root/'case';case.mkdir()
            with patch.object(run_intercept,'RUNTIME',root):run_intercept.config(case)
            self.assertTrue((root/'.trex/bridge.conf').is_file());self.assertFalse((root/'bridge.conf').exists())
            self.assertIn('client.enableDpiAwareness = False',(root/'.trex/bridge.conf').read_text())
            self.assertIn('rtx.enableReplacementAssets = False',(case/'rtx.conf').read_text())


if __name__=='__main__':unittest.main()
