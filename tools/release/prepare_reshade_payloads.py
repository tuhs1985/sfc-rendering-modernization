"""Build-time preparation for the two independent ReShade ZIP inputs."""
from hashlib import sha256
import json
from pathlib import Path
import sys
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/remix_runtime'))
sys.path.insert(0, str(ROOT/'src/session'))
from graphics_transaction import OLD_SHA, FULL_SHA
from release_manifest import digest

STANDARD_SOURCE = 'https://www.reshade.me/downloads/ReShade_Setup_6.7.1.exe'
FULL_SOURCE = 'https://reshade.me/downloads/ReShade_Setup_6.7.1_Addon.exe'
STANDARD_ARCHIVE_SHA = '4d7c19a5c08849e3a83c2824cf93636349a4a605c009812adb682720d984fa4d'
NOTICE = 'notices/ReShade-LICENSE.txt'
NOTICE_SOURCE = 'https://raw.githubusercontent.com/crosire/reshade/v6.7.1/LICENSE.md'
NOTICE_SHA = '237ded5b8344f820113efab1e65e91e1f159d9202c5b4856606a0590d3ffdab0'
BASELINE_ROLE = 'reshade_baseline_proxy'
FULL_ROLE = 'reshade_proxy'
STANDARD_TARGET = 'runtime/graphics/standard-reshade/ReShade32.dll'
FULL_TARGET = 'runtime/remix-runtime/deps/reshade-full-6.7.1/extracted/ReShade32.dll'


def verify_roles(items, roles, profile):
    if BASELINE_ROLE not in roles:
        return
    records = {target: item for item, _, target in items}
    for role, target, expected, upstream in (
            (BASELINE_ROLE, STANDARD_TARGET, OLD_SHA.lower(), STANDARD_SOURCE),
            (FULL_ROLE, FULL_TARGET, FULL_SHA.lower(), FULL_SOURCE)):
        item = records[roles[role]]
        if (roles[role], item['kind'], item['sha256'], item.get('upstream'), item.get('notice')) != (
                target, 'vendor', expected, upstream, NOTICE):
            raise ValueError('Unqualified ReShade ZIP input: ' + role)
    if records[NOTICE]['sha256'] != NOTICE_SHA:
        raise ValueError('ReShade ZIP notice differs from the verified license')
    if profile.get('files', {}).get('dxgi.dll', '').lower() != OLD_SHA.lower():
        raise ValueError('Packaged standard ReShade differs from the qualified game profile')


def prepare(root=ROOT):
    dependencies = root/'artifacts/alpha/dependencies'
    installer = dependencies/'ReShade_Setup_6.7.1.exe'
    if digest(installer) != STANDARD_ARCHIVE_SHA:
        raise ValueError('Standard ReShade installer hash mismatch')
    stage = dependencies/'reshade-standard-x86-verified'
    stage.mkdir(exist_ok=True)
    standard = stage/'ReShade32.dll'
    if not standard.exists():
        with ZipFile(installer) as archive:
            entry = archive.getinfo('ReShade32.dll')
            if not 0 < entry.file_size <= 16*1024*1024:
                raise ValueError('Unexpected ReShade x86 entry size')
            data = archive.read(entry)
        if sha256(data).hexdigest() != OLD_SHA.lower():
            raise ValueError('Standard ReShade embedded DLL hash mismatch')
        with standard.open('xb') as out:
            out.write(data)
    full = root/'artifacts/remix-runtime/deps/reshade-full-6.7.1/extracted/ReShade32.dll'
    notice = root/'artifacts/alpha'/NOTICE
    if digest(standard) != OLD_SHA.lower() or digest(full) != FULL_SHA.lower():
        raise ValueError('Qualified ReShade DLL hash mismatch')
    if digest(notice) != NOTICE_SHA:
        raise ValueError('Qualified ReShade notice hash mismatch')
    return [
        dict(kind='vendor', role=BASELINE_ROLE, target=STANDARD_TARGET,
             source=standard.relative_to(root).as_posix(), sha256=OLD_SHA.lower(), upstream=STANDARD_SOURCE, notice=NOTICE),
        dict(kind='vendor', role=FULL_ROLE, target=FULL_TARGET,
             source=full.relative_to(root).as_posix(), sha256=FULL_SHA.lower(), upstream=FULL_SOURCE, notice=NOTICE),
        dict(kind='vendor', target=NOTICE, source=notice.relative_to(root).as_posix(),
             sha256=NOTICE_SHA, upstream=NOTICE_SOURCE, notice=NOTICE),
    ]


if __name__ == '__main__':
    print(json.dumps(prepare(), indent=2))
