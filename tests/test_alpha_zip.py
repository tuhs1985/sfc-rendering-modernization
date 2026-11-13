import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
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

    def test_private_checkout_is_marked_and_restore_can_share_launcher(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'artifacts/alpha') as tmp:
            root = Path(tmp)
            recipe = self.fixture(root)
            recipe.pop('commit')
            recipe['license_review'] = 'pending'
            recipe['files'] = [item for item in recipe['files'] if item['role'] != 'restore']
            with self.assertRaisesRegex(ValueError, 'Reviewed release'):
                builder.build(recipe, root, root/'release.zip')
            with self.assertRaisesRegex(ValueError, 'private-checkout'):
                builder.build(recipe, root, root/'release.zip', private_checkout=True)
            output = root/'candidate-private-checkout.zip'
            builder.build(recipe, root, output, private_checkout=True)
            with zipfile.ZipFile(output) as archive:
                manifest = json.loads(archive.read('SFCRemix/package.json'))
            self.assertTrue(manifest['private_checkout'])
            self.assertIsNone(manifest['commit'])
            self.assertEqual(manifest['license_review'], 'pending')
            self.assertEqual(manifest['roles']['restore'], manifest['roles']['launcher'])

    def test_game_capture_private_settings_and_changed_inputs_rejected(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'artifacts/alpha') as tmp:
            root=Path(tmp);recipe=self.fixture(root)
            for name in ('StarFleetOP.exe','model.mod','data/capture.bin','settings/lights.toml','captures/fresh.png','evidence.raw32','../outside',
                         'python/include/Python.h','python/Scripts/f2py.exe','runtime/remix-runtime/deps/candidate-1.6.1/runtime/d3d9_a64ec.dll',
                         'code/tools/remix_runtime/qualify_multiship.py','CODE/TOOLS/remix_runtime/qualify_multiship.py',
                         'code/tools/release/bootstrap.py','code/tools/release/build_zip.py',
                         'code/src/launcher/build_launcher.py','code/src/launcher/launcher.cpp'):
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

    def test_partial_setup_payload_is_rejected_before_build(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'artifacts/alpha') as tmp:
            root=Path(tmp)
            recipe=self.fixture(root)
            path=root/'wrapper-template.txt'
            path.write_text('fixture')
            recipe['files'].append(dict(source=path.name,target='runtime/graphics/dgVoodoo.conf',
                                        sha256=builder.digest(path),role='setup_dgvoodoo',kind='project'))
            with self.assertRaisesRegex(ValueError,'Incomplete graphics setup inputs'):
                builder.validate_recipe(recipe,root)

    def test_reshade_roles_are_distinct_and_tied_to_the_baseline(self):
        import prepare_reshade_payloads as reshade

        with tempfile.TemporaryDirectory(dir=ROOT/'artifacts/alpha') as tmp:
            root=Path(tmp)
            recipe=self.fixture(root)
            full=next(item for item in recipe['files'] if item['role']==reshade.FULL_ROLE)
            full.update(kind='vendor', target=reshade.FULL_TARGET, upstream=reshade.FULL_SOURCE, notice=reshade.NOTICE)
            baseline=root/'standard.dll'
            baseline.write_bytes(b'standard fixture')
            old=builder.digest(baseline)
            notice=root/'notice.txt'
            notice.write_bytes(b'notice fixture')
            recipe['files'].extend([
                dict(kind='vendor', source=baseline.name, target=reshade.STANDARD_TARGET, role=reshade.BASELINE_ROLE,
                     upstream=reshade.STANDARD_SOURCE, notice=reshade.NOTICE, sha256=old),
                dict(kind='vendor', source=notice.name, target=reshade.NOTICE, upstream=reshade.NOTICE_SOURCE,
                     notice=reshade.NOTICE, sha256=builder.digest(notice)),
            ])
            recipe['game_profile']={'files':{'dxgi.dll':old}}
            with patch.multiple(reshade, OLD_SHA=old, FULL_SHA=full['sha256'], NOTICE_SHA=builder.digest(notice)):
                output=root/'reshade-inputs.zip'
                builder.build(recipe,root,output,check_commit=False)
                with zipfile.ZipFile(output) as archive:
                    manifest=json.loads(archive.read('SFCRemix/package.json'))
                    self.assertEqual(archive.read('SFCRemix/'+manifest['roles'][reshade.BASELINE_ROLE]), baseline.read_bytes())
                    self.assertEqual(archive.read('SFCRemix/'+manifest['roles'][reshade.FULL_ROLE]), (root/full['source']).read_bytes())
                    self.assertEqual(archive.read('SFCRemix/'+reshade.NOTICE), notice.read_bytes())
                    self.assertNotIn('dxgi.dll', archive.namelist())
                recipe['game_profile']['files']['dxgi.dll']=full['sha256']
                with self.assertRaisesRegex(ValueError,'differs from the qualified game profile'):
                    builder.validate_recipe(recipe,root)


if __name__=='__main__':unittest.main()
