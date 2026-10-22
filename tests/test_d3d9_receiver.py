from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/d3d9_proof'))
from run_direct64 import verify_receiver,resize_output,limit_to_first,qualified_extent
from scene_bundle import read_replay
from synthetic import prepare
import json
import struct


class ReceiverEvidenceTests(unittest.TestCase):
    def test_unqualified_extent_is_not_silently_admitted(self):
        self.assertTrue(qualified_extent(1920,1080));self.assertTrue(qualified_extent(640,960));self.assertTrue(qualified_extent(960,540))
        self.assertFalse(qualified_extent(1280,360));self.assertFalse(qualified_extent(1280,720));self.assertFalse(qualified_extent(1921,1080))
    def test_extent_changes_only_output_dimensions(self):
        with tempfile.TemporaryDirectory() as d:
            p=prepare(Path(d)/'scene');before=(p/'scene.bin').read_bytes();manifest=json.loads((p/'scene.json').read_text())
            frames=manifest['frames'].copy();resize_output(p,(640,960),manifest);after=(p/'scene.bin').read_bytes()
            self.assertEqual(before[:24]+before[32:],after[:24]+after[32:]);self.assertEqual(struct.unpack_from('<2I',after,24),(640,960));self.assertEqual(frames,manifest['frames'])
            with self.assertRaises(ValueError):resize_output(p,(1921,1080),manifest)

    def test_first_snapshot_preserves_geometry_and_exact_first_frame(self):
        with tempfile.TemporaryDirectory() as d:
            p=prepare(Path(d)/'scene');before=read_replay(p/'scene.bin');manifest=json.loads((p/'scene.json').read_text());limit_to_first(p,manifest);after=read_replay(p/'scene.bin')
            for key in ('vertices','indices','groups','width','height'):self.assertEqual(before[key],after[key])
            self.assertEqual(after['frames'],before['frames'][:1]);self.assertEqual(len(manifest['frames']),1)

    def fixture(self,root,mode='normal',frames=2):
        root=Path(root)
        (root/'job-console.log').write_text('OUTPUT_PEER_RETIRED\n'+''.join(f'OUTPUT_ACK sequence={i+1} held_ms=210\n' for i in range(frames)))
        (root/'receiver.log').write_text(''.join(f'RECEIVED sequence={i+1}\n' for i in range(frames)))
        for i in range(frames):
            for j in range(3):
                raw=bytes([i,j,7]);(root/f'receiver-{i}-{j}.raw32').write_bytes(raw);(root/f'returned-{i}-{j}.raw32').write_bytes(raw)
        return root

    def test_exact_images_and_slow_ack(self):
        with tempfile.TemporaryDirectory() as d:
            p=self.fixture(d)
            self.assertEqual(len(verify_receiver(p,'normal',2)['matching_images']),6)
            self.assertEqual(verify_receiver(p,'slow',2)['mode'],'slow')

    def test_changed_missing_and_unretired_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=self.fixture(d);target=p/'receiver-1-2.raw32';target.write_bytes(b'bad')
            with self.assertRaises(ValueError):verify_receiver(p,'normal',2)
            target.unlink()
            with self.assertRaises(ValueError):verify_receiver(p,'normal',2)
            (p/'job-console.log').write_text('')
            with self.assertRaises(ValueError):verify_receiver(p,'normal',2)

    def test_negative_receipts_are_not_normal_delivery(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'job-console.log').write_text('OUTPUT_PEER_RETIRED\nOUTPUT_INVALID_REJECTED\n');(p/'receiver.log').write_text('RECEIVER_REJECTED malformed/session/sequence packet\n')
            self.assertEqual(verify_receiver(p,'invalid',3)['matching_images'],[])
            with self.assertRaises(ValueError):verify_receiver(p,'normal',3)

    def test_timing_only_receipts_cannot_claim_images(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'job-console.log').write_text('OUTPUT_PEER_RETIRED\nOUTPUT_ACK sequence=1 held_ms=1\n');(p/'receiver.log').write_text('RECEIVED sequence=1\n')
            r=verify_receiver(p,'normal',1,verify_images=False);self.assertFalse(r['image_verification']);self.assertEqual(r['matching_images'],[])
            with self.assertRaises(ValueError):verify_receiver(p,'normal',1)


if __name__=='__main__':unittest.main()
