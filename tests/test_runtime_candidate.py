import json
from pathlib import Path
import sys
import tempfile
from unittest import TestCase, mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/remix_runtime'))
import runtime_candidate as candidate


class RuntimeCandidateTests(TestCase):
    def test_initialization_default_has_no_side_effects(self):
        environment={'DXVK_ASYNC_ASSET_LOADING':'1','RTX_ENABLE_ASYNC_COMPILATION':'kept'}
        text,receipt=candidate.configure_initialization('inherit',environment,offline=False,release=None)
        self.assertEqual(text,'')
        self.assertEqual(environment,{'DXVK_ASYNC_ASSET_LOADING':'1','RTX_ENABLE_ASYNC_COMPILATION':'kept'})
        self.assertEqual(receipt['supplied_config'],{})

    def test_synchronous_initialization_changes_only_one_option(self):
        environment={'DXVK_ASYNC_ASSET_LOADING':'1','RTX_ENABLE_ASYNC_COMPILATION':'1',
                     'DXVK_WAIT_ASYNC_TEXTURES':'0','RTX_ASYNC_SHADER_PREWARMING':'1'}
        before=environment.copy()
        text,receipt=candidate.configure_initialization('synchronous',environment,offline=True,release='1.6.1')
        self.assertEqual(text,'rtx.initializer.asyncAssetLoading = False\n')
        before['DXVK_ASYNC_ASSET_LOADING']='0'
        self.assertEqual(environment,before)
        self.assertEqual(receipt['supplied_config'],{'rtx.initializer.asyncAssetLoading':False})
        self.assertEqual(receipt['inherited_async_asset_loading'],'1')

    def test_initialization_cannot_select_production_or_unknown_policy(self):
        for policy,offline,release in [('synchronous',False,'1.6.1'),('synchronous',True,None),
                                       ('synchronous',True,'1.5.2'),('guess',True,'1.6.1')]:
            environment={'unchanged':'yes'}
            with self.assertRaises(ValueError):
                candidate.configure_initialization(policy,environment,offline=offline,release=release)
            self.assertEqual(environment,{'unchanged':'yes'})

    def test_initialization_cli_rejects_unsafe_combinations_before_launch(self):
        import subprocess
        for arguments,reason in [(['--candidate-asset-loading','synchronous'],'requires --runtime-candidate'),
                                 (['--runtime-candidate','1.6.1','--multi-ship','--prewarm',
                                   '--candidate-asset-loading','synchronous','--loading-policy','async'],
                                  'excludes --loading-policy')]:
            result=subprocess.run([sys.executable,'-B',str(ROOT/'tools/remix_runtime/run_return_fixture.py'),
                                   *arguments],capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,2)
            self.assertIn(reason,result.stderr)

    def test_pin_is_separate_and_explicit(self):
        self.assertEqual(candidate.COMMIT, '0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0')
        self.assertEqual(candidate.ARCHIVE_BYTES, 557087446)
        self.assertIn('for-x64-games-release', candidate.URL)
        self.assertNotIn('minecraft', candidate.URL)
        self.assertIn('candidate-1.6.1', str(candidate.BASE))

    def test_changed_manifest_version_and_path_rejected(self):
        for change in ({'api_version':[0,16,0]}, {'runtime':'../normal.dll'}, {'source_commit':'main'}):
            with tempfile.TemporaryDirectory() as folder:
                base=Path(folder)
                manifest=dict(source_commit=candidate.COMMIT, archive_sha256=candidate.ARCHIVE_SHA,
                              api_version=[0,6,5], runtime='runtime/d3d9_x64.dll', **{})
                manifest.update(change)
                (base/'manifest.json').write_text(json.dumps(manifest))
                with mock.patch.object(candidate, 'BASE', base), self.assertRaisesRegex(ValueError, 'pin mismatch'):
                    candidate.verify()

    def test_corrupt_existing_download_not_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'existing.zip';path.write_bytes(b'unchanged')
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                candidate.download(candidate.URL, path, 100, '0'*64)
            self.assertEqual(path.read_bytes(),b'unchanged')

    def test_changed_header_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder)
            manifest=dict(source_commit=candidate.COMMIT,archive_sha256=candidate.ARCHIVE_SHA,
                          api_version=[0,6,5],runtime='runtime/d3d9_x64.dll',header_sha256=candidate.HEADER_SHA)
            (base/'manifest.json').write_text(json.dumps(manifest));(base/'remix_c.h').write_bytes(b'wrong')
            with mock.patch.object(candidate,'BASE',base),self.assertRaisesRegex(ValueError,'header changed'):
                candidate.verify()

    def test_experiment_cannot_qualify_gameplay(self):
        from qualify_multiship import inspect
        with tempfile.TemporaryDirectory(dir=ROOT/'artifacts/remix-runtime/runs') as folder:
            (Path(folder)/'result.json').write_text(json.dumps(dict(runtime_candidate={'release':'1.6.1'})))
            with self.assertRaisesRegex(ValueError,'Experimental runtime cannot qualify'):
                inspect(folder)

    def test_no_persistent_runtime_override_in_relay(self):
        fixture=(ROOT/'tools/remix_runtime/run_return_fixture.py').read_text()
        self.assertIn('--runtime-candidate requires --multi-ship --prewarm',fixture)
        self.assertIn('--candidate-initial-replacements requires --runtime-candidate',fixture)
        production=(ROOT/'tools/remix_runtime/run_return_game.py').read_text()
        self.assertNotIn('--runtime-candidate',production)
        self.assertNotIn('candidate-1.6.1',(ROOT/'tools/remix_runtime/live_owner_timing.py').read_text())

    def test_fixture_reserves_parallel_preparation_before_start(self):
        text=(ROOT/'tools/remix_runtime/run_return_fixture.py').read_text()
        self.assertIn('reserve_mib=1024 if args.multi_ship_resources else (768 if args.multi_ship else 192)',text)
        self.assertLess(text.index('reserve_mib=1024'),text.index('work.mkdir()'))
