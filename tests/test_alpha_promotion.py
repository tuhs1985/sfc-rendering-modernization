import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/release'))
spec = importlib.util.spec_from_file_location('alpha_promotion', ROOT / 'tools/release/promote_alpha.py')
promotion = importlib.util.module_from_spec(spec)
spec.loader.exec_module(promotion)


class AlphaPromotionTests(unittest.TestCase):
    def fixture(self, *, extra=False, damaged=False):
        raw = b'fixture'
        manifest = dict(files={'README.md': dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())})
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, 'w') as z:
            z.writestr('SFCRemix/README.md', b'changed' if damaged else raw)
            z.writestr('SFCRemix/package.json', json.dumps(manifest))
            z.writestr('SFCRemix-Launch.cmd', b'fixture')
            if extra:
                z.writestr('SFCRemix/data/private.txt', b'private')
        stream.seek(0)
        return stream

    def test_exact_payload_file_boundary(self):
        with zipfile.ZipFile(self.fixture()) as z:
            self.assertEqual(len(promotion.checked_payload(z)['files']), 1)

    def test_unlisted_private_file_is_rejected(self):
        with zipfile.ZipFile(self.fixture(extra=True)) as z:
            with self.assertRaisesRegex(ValueError, 'allowlist'):
                promotion.checked_payload(z)

    def test_changed_immutable_bytes_are_rejected(self):
        with zipfile.ZipFile(self.fixture(damaged=True)) as z:
            with self.assertRaisesRegex(ValueError, 'mismatch'):
                promotion.checked_payload(z)

    def test_vendor_inventory_or_bytes_cannot_be_promoted(self):
        original = dict(files={'vendor.dll': dict(sha256='a')},
                        provenance={'vendor.dll': dict(kind='vendor')})
        promotion.compare_vendor(original, original)
        changed = dict(original, files={'vendor.dll': dict(sha256='b')})
        with self.assertRaisesRegex(ValueError, 'Vendor'):
            promotion.compare_vendor(changed, original)
        changed = dict(original, provenance={'vendor.dll': dict(kind='project')})
        with self.assertRaisesRegex(ValueError, 'Provenance'):
            promotion.compare_vendor(changed, original)

    def test_source_normalization_only_handles_encoding_and_line_endings(self):
        self.assertEqual(promotion.text(b'print(1)\r\n'), promotion.text(b'print(1)\n'))
        self.assertNotEqual(promotion.text(b'print(1)\r\n'), promotion.text(b'print(2)\n'))


if __name__ == '__main__':
    unittest.main()
