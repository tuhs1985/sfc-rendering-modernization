"""Prepare the pinned application-local VC runtime for the Remix ZIP recipe."""

import argparse
import json
from pathlib import Path
import shutil

from inventory_dependencies import native_inventory
from prepare_reshade_payloads import ROOT, digest


REDIST_VERSION = '14.51.36231'
REDIST_URL = 'https://learn.microsoft.com/en-us/visualstudio/releases/2026/redistribution'
REMIX_TARGET = 'runtime/remix-runtime/deps/candidate-1.6.1/runtime'
NOTICE_TARGET = 'notices/Microsoft-Visual-Cpp-Redistribution.txt'
PINS = {
    'msvcp140.dll': '7c26614e1d733892c2deac7e245ce115504b1d80592dd0a01b08e3e5a55f89ca',
    'vcruntime140.dll': 'd1f4225df2cd877dbf130d5668a021dce3f94118455ff5ec952061c30afc9ce7',
    'vcruntime140_1.dll': 'a7146c08f89fe5b04541ab507cdb59ff7b44534d4ba3c668a426c6450a03434e',
}


def prepare(redist):
    crt = Path(redist) / REDIST_VERSION / 'x64/Microsoft.VC145.CRT'
    sources = {name: crt / name for name in PINS}
    for name, path in sources.items():
        if not path.is_file() or digest(path) != PINS[name]:
            raise ValueError(f'Expected the pinned VS 2026 x64 Redistributable file: {path}')

    output = ROOT / 'artifacts/alpha/remix-crt'
    output.mkdir(parents=True, exist_ok=True)
    for name, path in sources.items():
        target = output / name
        shutil.copyfile(path, target)
        if digest(target) != PINS[name]:
            raise ValueError(f'Redistributable changed during staging: {name}')

    notice = output / Path(NOTICE_TARGET).name
    notice.write_text(
        'Microsoft Visual C++ Runtime, copyright Microsoft Corporation.\n'
        f'Unmodified Visual Studio 2026 VC145 x64 application-local files ({REDIST_VERSION}).\n'
        'Separate Microsoft license terms apply. Redistribution is subject to the\n'
        'Visual Studio Software License Terms and the corresponding REDIST list.\n'
        f'{REDIST_URL}\n',
        encoding='ascii',
    )
    native = native_inventory(output / name for name in PINS)
    if any(entry['machine'] != 'x64' for entry in native):
        raise ValueError('Expected x64 Visual C++ runtime')
    entries = [
        dict(kind='vendor', source=entry['path'], sha256=entry['sha256'],
             target=f"{REMIX_TARGET}/{Path(entry['path']).name}",
             upstream=REDIST_URL, notice=NOTICE_TARGET)
        for entry in native
    ]
    entries.append(dict(kind='vendor', source=notice.relative_to(ROOT).as_posix(),
                        sha256=digest(notice), target=NOTICE_TARGET,
                        upstream=REDIST_URL, notice=NOTICE_TARGET))
    return dict(files=entries, native_imports=native)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('redist_root', type=Path, help='Visual Studio VC/Redist/MSVC directory')
    args = parser.parse_args()
    print(json.dumps(prepare(args.redist_root), indent=2))
