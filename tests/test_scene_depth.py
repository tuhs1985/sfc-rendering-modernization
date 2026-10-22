import ctypes as C
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
import scene_depth
from live_return import depth_telemetry

class SceneDepthTests(unittest.TestCase):
    def test_fixed_extension_and_reserved_guard(self):
        block=C.create_string_buffer(4096)
        raw=struct.pack('<32I',0x31504453,1,128,0,*range(16),*([0]*12))
        C.memmove(C.addressof(block)+2048,raw,128)
        row=depth_telemetry(C.addressof(block))
        self.assertEqual(row['engine_frame'],15)
        self.assertEqual(row['displayed'],9)
        block[2048+127]=b'\1'
        with self.assertRaises(ValueError):depth_telemetry(C.addressof(block))

    def test_receipt_requires_exact_sources_binaries_and_proxy(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt=Path(tmp)/'qualification.json'
            good=dict(result='OFFLINE_SCENE_DEPTH_CALLBACK_PASS',sources={'a':'1'},binaries={'b':'2'},proxy_sha256=scene_depth.FULL_SHA)
            with patch.object(scene_depth,'RECEIPT',receipt),patch.object(scene_depth,'qualified_full'),patch.object(scene_depth,'source_hashes',return_value={'a':'1'}),patch.object(scene_depth,'binary_hashes',return_value={'b':'2'}):
                receipt.write_text(json.dumps(good))
                self.assertEqual(scene_depth.require_qualification(),good)
                for key in ('result','sources','binaries','proxy_sha256'):
                    bad={**good,key:None};receipt.write_text(json.dumps(bad))
                    with self.assertRaises(ValueError):scene_depth.require_qualification()

    def test_missing_receipt_is_not_approval(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(scene_depth,'RECEIPT',Path(tmp)/'missing.json'),patch.object(scene_depth,'qualified_full'):
            with self.assertRaises(FileNotFoundError):scene_depth.require_qualification()

if __name__=='__main__':unittest.main()
