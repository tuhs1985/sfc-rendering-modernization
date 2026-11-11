"""Compare the accepted and cache-only profiles using the installed ReShade preparation helper."""
import configparser
import json
import os
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory


def read_profile(raw):
    profile = configparser.RawConfigParser(strict=True)
    profile.optionxform = str
    profile.read_string(raw.decode('utf-8-sig'))
    return profile


def candidate_profile(raw):
    original = read_profile(raw)
    key = 'IntermediateCachePath'
    if not Path(original['GENERAL'][key]).is_absolute():
        raise ValueError('Expected the accepted machine-specific ReShade cache path')
    candidate, count = re.subn(
        rb'(?m)^(IntermediateCachePath[ \t]*=[ \t]*)[^\r\n]+',
        lambda match: match[1] + rb'.\SFCRemix\data\cache',
        raw,
    )
    if count != 1 or read_profile(candidate)['GENERAL'][key] != r'.\SFCRemix\data\cache':
        raise ValueError('Expected exactly one ReShade cache setting in GENERAL')
    return candidate


def main():
    package = Path(sys.argv[1]).resolve()
    os.environ['SFC_RELEASE_ROOT'] = str(package)
    sys.path.insert(0, str(package/'code/src/launcher'))
    import bootstrap
    from portable_reshade import prepare
    from release_manifest import digest

    context = bootstrap.CONTEXT
    manifest = bootstrap.verify(context)
    if not manifest.get('private_checkout') or context.package_root != package:
        raise ValueError('Cache qualification requires the disposable functional checkout')
    # Refuse any installed location outside the fixture tree created by the stager.
    fixture_root = (Path(__file__).resolve().parents[2]/'artifacts/alpha/preflight-fixtures').resolve()
    if not package.is_relative_to(fixture_root):
        raise ValueError('Cache qualification requires a newly staged fixture')
    path = context.game_root/'ReShade.ini'
    candidate = path.read_bytes()
    original = sys.stdin.buffer.read(1024*1024+1)
    if len(original) > 1024*1024 or candidate != candidate_profile(original):
        raise ValueError('Fixture does not contain the exact cache-only change')
    inputs = read_profile(candidate)['GENERAL']

    def appearance_files():
        files = set()
        for name in ('EffectSearchPaths', 'TextureSearchPaths', 'PresetPath', 'StartupPresetPath'):
            for value in filter(None, (item.strip() for item in inputs.get(name, '').split(','))):
                root = (context.game_root/value.removesuffix('**').rstrip('\\/')).resolve()
                if not root.is_relative_to(context.game_root.resolve()) or not root.exists():
                    raise ValueError('Missing or nonportable appearance input: ' + name)
                if root.is_dir():
                    files.update(path for path in root.rglob('*') if path.is_file())
                else:
                    files.add(root)
        if not files:
            raise ValueError('No appearance files in fixture')
        return {path: digest(path) for path in files}

    def effective_profile(work):
        root = work/'reshade'
        if prepare(context, work) != {'RESHADE_BASE_PATH_OVERRIDE': str(root)}:
            raise ValueError('Installed ReShade path override differs')
        profile = read_profile((root/'ReShade.ini').read_bytes())
        for section, key, folder in (('GENERAL', 'IntermediateCachePath', 'cache'),
                                     ('SCREENSHOT', 'SavePath', 'screenshots'),
                                     ('ADDON', 'AddonPath', 'addons')):
            if profile[section][key] != str(root/folder) or not (root/folder).is_dir():
                raise ValueError('Generated ReShade output escaped the session: ' + key)
            profile[section][key] = folder
        return {name: dict(profile[name]) for name in profile}

    before = appearance_files()
    with TemporaryDirectory(prefix='reshade-cache-qualification-', dir=context.data_root/'tmp') as folder:
        control, test = (Path(folder)/name for name in ('control', 'candidate'))
        control.mkdir()
        test.mkdir()
        try:
            path.write_bytes(original)
            expected = effective_profile(control)
        finally:
            path.write_bytes(candidate)
        if effective_profile(test) != expected:
            raise ValueError('Cache-only change altered the effective ReShade profile')
    if path.read_bytes() != candidate or before != appearance_files():
        raise ValueError('Candidate configuration or appearance inputs changed')
    print(json.dumps(dict(result='PORTABLE_RESHADE_CACHE_PASS', appearance_files=len(before),
                          effective_profile_identical=True, appearance_hashes_unchanged=True,
                          launched_game=False, launched_renderer=False)))


if __name__ == '__main__':
    main()
