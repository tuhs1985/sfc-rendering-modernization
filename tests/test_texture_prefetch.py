from pathlib import Path
import json
import os
import struct
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools/remix_runtime'),str(ROOT/'tools/d3d9_proof')]
from texture_prefetch import packet,HEADER,STRIDE
from owner_rebind import fnv


class PrefetchTests(unittest.TestCase):
    def prepare(self,gpu):
        stage=gpu/'assets/1/rtx-remix/mods/sfc-policy/mod.usda'
        stage.parent.mkdir(parents=True);stage.write_text('unchanged')
        name='textures/'+'a'*64+'.dds';target=stage.parent/name;target.parent.mkdir();target.write_bytes(b'unchanged image')
        (stage.parents[3]/'material-binding.json').write_text(json.dumps(dict(images={name:{}})))
        return os.path.relpath(stage,gpu/'rtx-remix/mods/sfc-policy'),target

    def test_session_checksum_dedup_and_immutable_images(self):
        with tempfile.TemporaryDirectory() as directory:
            gpu=Path(directory);layer,image=self.prepare(gpu)
            raw=packet(gpu,[layer,layer],123,'Local\\SFCBridge_'+'a'*32)
            self.assertEqual(HEADER.unpack_from(raw)[:4],(0x31504654,1,123,1))
            self.assertEqual(len(raw),32+STRIDE+8)
            self.assertEqual(struct.unpack('<Q',raw[-8:])[0],fnv(raw[:-8]))
            self.assertEqual(image.read_bytes(),b'unchanged image')

    def test_bad_session_pid_missing_and_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            gpu=Path(directory);layer,image=self.prepare(gpu)
            for pid,session in ((0,'Local\\SFCBridge_'+'a'*32),(123,'wrong')):
                with self.assertRaises(ValueError):packet(gpu,[layer],pid,session)
            with self.assertRaises(ValueError):packet(gpu,['../../../../outside'],123,'Local\\SFCBridge_'+'a'*32)
            image.unlink()
            with self.assertRaises(ValueError):packet(gpu,[layer],123,'Local\\SFCBridge_'+'a'*32)

    def test_experiment_cannot_qualify(self):
        from qualify_multiship import inspect
        with tempfile.TemporaryDirectory(dir=ROOT/'artifacts/remix-runtime/runs') as directory:
            (Path(directory)/'result.json').write_text(json.dumps(dict(multi_ship_fixture=True,fixture_exit=0,host_exit=0,api_texture_prefetch=True)))
            with self.assertRaisesRegex(ValueError,'cannot qualify'):inspect(directory)
