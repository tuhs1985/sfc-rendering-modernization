import json
from pathlib import Path
import tempfile
import unittest
from PIL import Image
from provisional_lighting import multiply_encoded, prepare
from run_remix_ingest import digest


class LightingTests(unittest.TestCase):
    def fixture(self, root):
        capture, job, work = root/'capture', root/'job', root/'work'
        folder = capture/'textured'; folder.mkdir(parents=True)
        job.mkdir(); work.mkdir()
        packet = capture/'MESH-EXPORT-001.bin'; packet.write_bytes(b'synthetic fixture')
        groups, images = [], []
        for g in range(5):
            groups.append({'group': g, 'flags': 35, 'primary': 2*g+1, 'secondary': 2*g+2})
            for r in (2*g+1, 2*g+2):
                image = folder/f'{r}.png'
                Image.new('RGB', (256, 256), (100, 150, 200)).save(image)
                images.append({'id': r, 'derived': image.name, 'derived_sha256': digest(image), 'alpha_present': False})
        refs = capture/'TEXTURE-EXPORT-001.json'
        refs.write_text(json.dumps({'groups': groups, 'status': 1, 'hooks_restored': True}))
        manifest = {'groups': groups, 'images': images, 'primary_images_ready': True,
                    'packet_sha256': digest(packet), 'references_sha256': digest(refs)}
        (folder/'association-manifest.json').write_text(json.dumps(manifest))
        (job/'job-metadata.json').write_text(json.dumps({'capture': str(capture), 'packet_sha256': digest(packet)}))
        (work/'preview-config.json').write_text(json.dumps({'work': str(work), 'textures': True, 'dependency_sha256': {}}))
        return work, job, capture

    def test_product_uses_both_images_not_raw_mask(self):
        p = Image.new('RGB', (256, 256), (128, 255, 0))
        s = Image.new('RGB', (256, 256), (128, 128, 255))
        result = multiply_encoded(p, s)
        self.assertEqual(result.getpixel((0, 0)), (64, 128, 0))
        self.assertEqual(p.getpixel((0, 0)), (128, 255, 0))

    def test_unqualified_size_refused(self):
        with self.assertRaises(ValueError): multiply_encoded(Image.new('RGB', (1, 1)), Image.new('RGB', (1, 1)))

    def test_full_derivative_roundtrips_and_preserves_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            work, job, capture = self.fixture(Path(tmp))
            before = {p: digest(p) for p in capture.rglob('*') if p.is_file()}
            report = prepare(work, job)
            self.assertEqual(report['status'], 'PROVISIONAL_RUNTIME_UNVERIFIED')
            self.assertEqual(len(report['groups']), 5)
            self.assertLess(report['image_bytes'], 8*1024*1024)
            self.assertTrue(all(digest(p) == h for p, h in before.items()))
            config = json.loads((work/'preview-config.json').read_text())
            self.assertEqual(len(config['dependency_sha256']), 10)
            for row in report['groups']:
                with Image.open(work/row['dds']) as image:
                    self.assertEqual(image.convert('RGB').getpixel((0, 0)), (39, 88, 157))
            with self.assertRaises(FileExistsError): prepare(work, job)

    def test_changed_image_or_cross_capture_refused(self):
        for problem in ('image', 'packet', 'reference'):
            with self.subTest(problem=problem), tempfile.TemporaryDirectory() as tmp:
                work, job, capture = self.fixture(Path(tmp))
                target = {'image': capture/'textured/1.png', 'packet': capture/'MESH-EXPORT-001.bin',
                          'reference': capture/'TEXTURE-EXPORT-001.json'}[problem]
                target.write_bytes(target.read_bytes()+b' ')
                with self.assertRaises(ValueError): prepare(work, job)
                self.assertFalse((work/'provisional-lighting').exists())

    def test_shader_override_remains_session_only_and_labelled(self):
        script = Path(__file__).with_name('kit_mesh_preview.py').read_text()
        self.assertLess(script.index('SetEditTarget(stage.GetSessionLayer())'), script.index("CreateInput('emissive_mask_texture'"))
        self.assertIn('Group/primary material association mismatch', script)
        self.assertIn('PROVISIONAL lighting masks', script)
        self.assertNotIn('.Save(', script)
