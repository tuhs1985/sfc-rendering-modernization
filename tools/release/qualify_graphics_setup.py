"""Exercise installed setup and restore in a newly staged private checkout."""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('fixture', type=Path)
    args = parser.parse_args()
    fixture = args.fixture.resolve()
    if fixture.parent != (ROOT/'artifacts/alpha/preflight-fixtures').resolve():
        raise ValueError('Use a new fixture from stage_preflight_fixture.py --functional --portable-cache --setup')
    receipt = json.loads((fixture/'result.json').read_bytes())
    package = Path(receipt['private_functional_checkout']).resolve()
    if (not receipt.get('setup') or not receipt.get('no_gameplay_acceptance')
            or package.parent.parent != fixture):
        raise ValueError('Invalid private setup fixture')
    game = package.parent
    backup_dir = package/'data/graphics-setup'
    if backup_dir.exists():
        raise ValueError('Use a fresh fixture with no previous setup')
    env = {**os.environ, 'SFC_RELEASE_ROOT': str(package)}
    original = {name: (game/name).read_bytes() for name in ('DDraw.dll', 'dxgi.dll', 'ReShade.ini')}
    protected = {name: sha256((game/name).read_bytes()).hexdigest()
                 for name in ('StarFleetOP.exe', 'sfc.ini', 'D3DImm.dll', 'SFCOP_1_Preset.ini', 'dgVoodoo.conf')}
    results = []

    def run(mode, answer='', status=0, marker=''):
        # Exercise the installed entry point without opening an elevation
        # dialog. The native launcher's --preflight already ran in staging.
        command = [str(package/'python/python.exe'), '-I', '-B',
                   str(package/'code/src/launcher/bootstrap.py'), mode]
        check = subprocess.run(command, cwd=game, env=env, input=answer,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                               errors='replace', timeout=100)
        results.append(dict(mode=mode, exit_code=check.returncode, console=check.stdout))
        if check.returncode!=status or marker not in check.stdout:
            raise ValueError(f'Installed {mode} failed: {check.stdout}')

    try:
        (game/'DDraw.dll').unlink()
        (game/'dxgi.dll').write_bytes(b'fixture mismatched proxy')
        (game/'ReShade.ini').write_bytes(original['ReShade.ini']+b'\n; fixture prior preference\n')
        before = {name: (game/name).read_bytes() for name in ('dxgi.dll', 'ReShade.ini')}
        run('--preflight', status=1, marker='Missing graphics file: DDraw.dll')
        run('--prepare', 'n\n', status=1, marker='Graphics setup cancelled')
        if backup_dir.exists() or (game/'DDraw.dll').exists() or any(
                (game/name).read_bytes()!=data for name,data in before.items()):
            raise ValueError('Cancelled setup changed the game files')
        run('--prepare', 'y\n', marker='Graphics setup complete.')
        if (game/'ReShade.ini').read_bytes() != before['ReShade.ini']:
            raise ValueError('Setup changed the tester ReShade configuration')
        run('--preflight', marker='READ_ONLY_PACKAGE_PREFLIGHT_PASS')
        run('--prepare')  # Reuses the applied setup without requiring input.
        run('--restore', marker='Graphics restored.')
        if (backup_dir.exists() or (game/'DDraw.dll').exists()
                or any((game/name).read_bytes()!=data for name,data in before.items())):
            raise ValueError('Restore did not recover the prior file state')
        if any(sha256((game/name).read_bytes()).hexdigest()!=value for name,value in protected.items()):
            raise ValueError('An unrelated game file changed')
    finally:
        if not backup_dir.exists():
            for name, data in original.items():
                (game/name).write_bytes(data)
        (fixture/'setup-qualification.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    run('--preflight', marker='READ_ONLY_PACKAGE_PREFLIGHT_PASS')
    print(json.dumps(dict(result='INSTALLED_GRAPHICS_SETUP_PASS', cases=results, game_launched=False), indent=2))


if __name__ == '__main__':
    main()
