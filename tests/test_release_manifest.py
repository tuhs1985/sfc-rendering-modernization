import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/remix_runtime'))
import release_manifest as rm
from runtime_context import packaged, CLIENT_SHA256, VERSION
from unittest.mock import patch


class ReleaseManifestTests(unittest.TestCase):
    def stage(self, directory):
        context = packaged(Path(directory) / 'SFC é' / 'SFCRemix')
        context.package_root.mkdir(parents=True)
        (context.game_root / 'StarFleetOP.exe').write_bytes(b'synthetic game identity')
        files = {}; roles = {}
        for role in rm.REQUIRED_ROLES:
            name = 'inputs/' + role + '.txt'
            path = context.package_root / name
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(role.encode())
            files[name] = {'bytes': path.stat().st_size, 'sha256': rm.digest(path)}
            roles[role] = name
        manifest = dict(schema=rm.SCHEMA, version=VERSION, client_sha256=CLIENT_SHA256,
                        platform='windows-x64', files=files, roles=roles)
        (context.package_root / rm.MANIFEST).write_text(json.dumps(manifest))
        return context, manifest

    def test_integrity_checks_real_files_and_seed_preserves_user_settings(self):
        with tempfile.TemporaryDirectory() as tmp:
            context, value = self.stage(tmp)
            real_digest = rm.digest
            with patch.object(rm, 'digest', side_effect=lambda p: CLIENT_SHA256.lower() if Path(p).name == 'StarFleetOP.exe' else real_digest(p)):
                self.assertEqual(rm.verify(context), value)
                self.assertFalse(context.settings_root.exists(), 'Verification must be read-only')
                rm.seed_settings(context, value)
                profile = context.setting('rendering.toml')
                self.assertEqual(profile.read_bytes(), b'default_rendering')
                profile.write_bytes(b'user settings')
                rm.seed_settings(context, value)
                self.assertEqual(profile.read_bytes(), b'user settings')
                changed = context.package_root / value['roles']['renderer']
                changed.write_bytes(b'bad')
                with self.assertRaisesRegex(ValueError, 'input missing or changed'):
                    rm.verify(context)

    def test_missing_roles_unsafe_names_and_mutable_receipts_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            context, original = self.stage(tmp)
            for mutate in (
                lambda x: x['roles'].pop('renderer'),
                lambda x: x['files'].update({'../game.exe': next(iter(x['files'].values()))}),
                lambda x: x['files'].update({'settings/rendering.toml': next(iter(x['files'].values()))}),
                lambda x: x['roles'].update(renderer='unlisted.exe'),
                lambda x: x.update(client_sha256='0' * 64),
            ):
                value = json.loads(json.dumps(original)); mutate(value)
                (context.package_root / rm.MANIFEST).write_text(json.dumps(value))
                with self.assertRaises(ValueError): rm.load(context.package_root)

    def test_wrong_game_refused_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            context, _ = self.stage(tmp)
            with self.assertRaisesRegex(ValueError, 'Supported StarFleetOP'):
                rm.verify(context)
            self.assertFalse(context.data_root.exists())
            self.assertFalse(context.settings_root.exists())

    def test_case_collisions_and_invalid_hashes_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            context, value = self.stage(tmp)
            name = next(iter(value['files']))
            value['files'][name.upper()] = value['files'][name]
            (context.package_root / rm.MANIFEST).write_text(json.dumps(value))
            with self.assertRaisesRegex(ValueError, 'case-insensitive'): rm.load(context.package_root)
            del value['files'][name.upper()]
            value['files'][name]['sha256'] = 'z' * 64
            (context.package_root / rm.MANIFEST).write_text(json.dumps(value))
            with self.assertRaisesRegex(ValueError, 'receipt'): rm.load(context.package_root)

    def test_unknown_dll_cannot_hide_beside_listed_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            context, _ = self.stage(tmp)
            (context.package_root / 'inputs/extra.dll').write_bytes(b'unlisted')
            with self.assertRaisesRegex(ValueError,'Unlisted immutable'):
                rm.verify(context)

    def test_game_profile_is_checked_before_any_settings_are_seeded(self):
        from copied_preferences import protected_ini_sha256
        with tempfile.TemporaryDirectory() as tmp:
            context, value = self.stage(tmp)
            names=('DDraw.dll','D3DImm.dll','dxgi.dll','dgVoodoo.conf','ReShade.ini')
            for name in names:(context.game_root/name).write_bytes(name.encode())
            ini=b'[Network]\r\nPlayerName=before\r\n[3D]\r\nWidth=1920\r\n'
            (context.game_root/'sfc.ini').write_bytes(ini.replace(b'before',b'after'))
            value['game_profile']=dict(files={n:rm.digest(context.game_root/n) for n in names},
                                      sfc_protected_sha256=protected_ini_sha256(ini))
            rm.verify_game_profile(context,value)
            self.assertFalse(context.settings_root.exists())
            (context.game_root/'d3d9.dll').write_bytes(b'unknown')
            with self.assertRaisesRegex(ValueError,'proxy conflict'):
                rm.verify_game_profile(context,value)
            (context.game_root/'d3d9.dll').unlink()
            (context.game_root/'dxgi.dll').write_bytes(b'unknown')
            with self.assertRaisesRegex(ValueError,'Unsupported graphics file'):
                rm.verify_game_profile(context,value)
            self.assertFalse(context.data_root.exists())


if __name__ == '__main__': unittest.main()
