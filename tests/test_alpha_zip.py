import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('alpha_build',ROOT/'tools/release/build_zip.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)


class AlphaZipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (ROOT/'artifacts/alpha').mkdir(parents=True,exist_ok=True)
    def fixture(self,root):
        root=Path(root);items=[]
        for role in builder.REQUIRED_ROLES:
            path=root/(role+'.txt');path.write_text(role)
            items.append(dict(source=path.name,target='inputs/'+path.name,sha256=builder.digest(path),role=role,kind='project'))
        return dict(schema='sfc.alpha.build.v1',version=builder.VERSION,license_review='complete',
                    commit='a'*40,files=items,game_profile={},remix={})

    def test_allowlisted_zip_contains_only_launcher_package_and_checksums(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'artifacts/alpha') as tmp:
            root=Path(tmp);recipe=self.fixture(root)
            (root/'private-chat.png').write_bytes(b'NEVER SELECTED')
            output=root/'candidate.zip'
            result=builder.build(recipe,root,output,check_commit=False)
            self.assertFalse(result['published'])
            self.assertIn(result['sha256'],output.with_suffix('.zip.sha256').read_text())
            with zipfile.ZipFile(output) as archive:
                names=archive.namelist()
                self.assertTrue(all(n=='SFCRemix-Launch.cmd' or n.startswith('SFCRemix/') for n in names))
                self.assertFalse(any('private-chat' in n for n in names))
                entry=archive.read('SFCRemix-Launch.cmd').lower()
                self.assertNotIn(b'powershell',entry);self.assertNotIn(b'.ps1',entry)
                self.assertIn(b'launcher.exe',entry)
                manifest=json.loads(archive.read('SFCRemix/package.json'))
                self.assertEqual(set(manifest['roles']),builder.REQUIRED_ROLES)
            with self.assertRaisesRegex(ValueError,'already exists'):
                builder.build(recipe,root,output,check_commit=False)

    def test_game_capture_private_settings_and_changed_inputs_rejected(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'artifacts/alpha') as tmp:
            root=Path(tmp);recipe=self.fixture(root)
            for name in ('StarFleetOP.exe','model.mod','data/capture.bin','settings/lights.toml','captures/fresh.png','evidence.raw32','../outside',
                         'python/include/Python.h','python/Scripts/f2py.exe','runtime/remix-runtime/deps/candidate-1.6.1/runtime/d3d9_a64ec.dll'):
                value=json.loads(json.dumps(recipe));value['files'][0]['target']=name
                with self.subTest(name=name),self.assertRaises(ValueError):builder.validate_recipe(value,root)
            recipe['files'][0]['sha256']='0'*64
            with self.assertRaisesRegex(ValueError,'input changed'):builder.validate_recipe(recipe,root)

    def test_vendor_requires_identified_upstream_and_included_notice(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'artifacts/alpha') as tmp:
            root=Path(tmp);recipe=self.fixture(root);item=recipe['files'][0];item['kind']='vendor'
            with self.assertRaisesRegex(ValueError,'Vendor upstream'):builder.validate_recipe(recipe,root)
            item.update(upstream='https://example.test/distribution.zip',notice='LICENSE.txt')
            with self.assertRaisesRegex(ValueError,'not included'):builder.validate_recipe(recipe,root)
            item['notice']=recipe['files'][1]['target']
            self.assertEqual(len(builder.validate_recipe(recipe,root)[0]),len(recipe['files']))


if __name__=='__main__':unittest.main()
