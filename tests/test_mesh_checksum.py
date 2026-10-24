import concurrent.futures
import json
from pathlib import Path
import random
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
for path in ('tools/remix_ingest','tools/d3d9_proof'):sys.path.insert(0,str(ROOT/path))
import mesh_checksum
from live_scene import decode_mesh
from test_live_scene import packet_fixture


def reference(raw):
    value=2166136261
    for i,byte in enumerate(raw):value=((value^(0 if 12<=i<16 else byte))*16777619)&0xffffffff
    return value


class MeshChecksumTests(unittest.TestCase):
    def test_mutable_or_unbounded_input_rejected_before_loading(self):
        for raw in (bytearray(256),memoryview(bytes(256)),bytes(255),bytes(2*1024*1024+1)):
            with patch.object(mesh_checksum,'_load',side_effect=AssertionError('Must not load')):
                with self.assertRaises(ValueError):mesh_checksum.calculate(raw)

    def test_loader_rejects_changed_build(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder);(base/'build.json').write_text(json.dumps(dict(source_sha256='wrong',dll_sha256='wrong',architecture='x64')))
            with patch.object(mesh_checksum,'BIN',base),patch.object(mesh_checksum,'_function',None):
                with self.assertRaisesRegex(ValueError,'build/source/architecture'):mesh_checksum.calculate(bytes(256))

    @unittest.skipUnless((mesh_checksum.BIN/'mesh_checksum.dll').exists(),'Build native checksum helper first')
    def test_exact_fnv32_zeroed_checksum_field_and_binary_buffers(self):
        rng=random.Random(104)
        for length in (256,257,1024,65537,2*1024*1024):
            raw=rng.randbytes(length)
            self.assertEqual(mesh_checksum.calculate(raw),reference(raw))
            changed=raw[:12]+b'\0\xff\0\xff'+raw[16:]
            self.assertEqual(mesh_checksum.calculate(changed),mesh_checksum.calculate(raw))

    @unittest.skipUnless((mesh_checksum.BIN/'mesh_checksum.dll').exists(),'Build native checksum helper first')
    def test_decoded_content_and_rejections_identical(self):
        packet,refs=packet_fixture()
        self.assertEqual(decode_mesh(packet,refs),decode_mesh(packet,refs,checksum=mesh_checksum.calculate))
        damaged=packet[:260]+bytes([packet[260]^1])+packet[261:]
        for raw,reference_bytes in ((damaged,refs),(packet[:-1],refs),(packet,refs.replace(b'"model": 3',b'"model": 999'))):
            for backend in (None,mesh_checksum.calculate):
                with self.assertRaises(ValueError):decode_mesh(raw,reference_bytes,checksum=backend)

    @unittest.skipUnless((mesh_checksum.BIN/'mesh_checksum.dll').exists(),'Build native checksum helper first')
    def test_thread_safe_without_changing_immutable_input(self):
        packet,_=packet_fixture();original=bytes(packet)
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            values=list(executor.map(mesh_checksum.calculate,[packet]*64))
        self.assertEqual(values,[struct.unpack_from('<I',packet,12)[0]]*64)
        self.assertEqual(packet,original)
