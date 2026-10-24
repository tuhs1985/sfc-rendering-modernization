"""Pinned, isolated stock-runtime experiment; never changes the gameplay pin."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'artifacts/remix-runtime/deps/candidate-1.6.1'
COMMIT = '0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0'
NAME = 'rtx-remix-for-x64-games-release-remix-1.6.1.zip'
ARCHIVE_BYTES = 557087446
ARCHIVE_SHA = '7dd1d44492a609050e44b0e3581cec31135d1ed88b4a91123b4faae91955716a'
URL = 'https://github.com/NVIDIAGameWorks/rtx-remix/releases/download/remix-1.6.1/' + NAME
HEADER_URL = f'https://raw.githubusercontent.com/NVIDIAGameWorks/dxvk-remix/{COMMIT}/public/include/remix/remix_c.h'
HEADER_SHA = '26a5607a07e8718298c35519e53bbc71d526186a947e5a2a5b613a0d6db04f3a'


def configure_initialization(policy, environment, *, offline, release):
    """One candidate-only input; never a shader/texture readiness assertion."""
    if policy not in ('inherit', 'synchronous'):
        raise ValueError('Unknown candidate asset initialization policy')
    before = environment.get('DXVK_ASYNC_ASSET_LOADING')
    options = {}
    if policy != 'inherit':
        if not offline or release != '1.6.1':
            raise ValueError('Candidate initialization requires isolated offline runtime1.6.1')
        environment['DXVK_ASYNC_ASSET_LOADING'] = '0'
        options['rtx.initializer.asyncAssetLoading'] = False
    return ''.join(f'{key} = {value}\n' for key, value in options.items()), dict(
        policy=policy, release=release, inherited_async_asset_loading=before,
        supplied_async_asset_loading=environment.get('DXVK_ASYNC_ASSET_LOADING'),
        supplied_config=options, scope='Candidate child only;not GPU residency or runtime promotion')


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def download(url, path, limit, expected=None):
    if path.exists():
        if expected and digest(path) != expected:
            raise ValueError('Existing candidate download hash mismatch')
        return
    temporary = path.with_suffix(path.suffix + '.partial')
    count = 0
    with urllib.request.urlopen(url, timeout=60) as source, temporary.open('xb') as target:
        while block := source.read(1024 * 1024):
            count += len(block)
            if count > limit:
                raise ValueError('Dependency download size bound')
            target.write(block)
    if expected and digest(temporary) != expected:
        raise ValueError('Candidate download hash mismatch')
    temporary.rename(path)


def fetch():
    BASE.mkdir(parents=True, exist_ok=True)
    archive = BASE / NAME
    download(URL, archive, ARCHIVE_BYTES, ARCHIVE_SHA)
    if archive.stat().st_size != ARCHIVE_BYTES:
        raise ValueError('Candidate archive size mismatch')
    header = BASE / 'remix_c.h'
    download(HEADER_URL, header, 256 * 1024, HEADER_SHA)
    text = header.read_text()
    version = tuple(int(re.search(r'#define REMIXAPI_VERSION_' + key + r'\s+(\d+)', text)[1])
                    for key in ('MAJOR', 'MINOR', 'PATCH'))
    if version != (0, 6, 5):
        raise ValueError('Release-source API version mismatch')
    extracted = BASE / 'runtime'
    existing = extracted.exists()
    with zipfile.ZipFile(archive) as package:
        infos = package.infolist()
        if len(infos) > 5000 or sum(x.file_size for x in infos) > 3 * 1024**3:
            raise ValueError('Dependency extraction bound')
        for entry in infos:
            p = PurePosixPath(entry.filename)
            if p.is_absolute() or '..' in p.parts or '\\' in entry.filename or ':' in entry.filename:
                raise ValueError('Unsafe dependency archive path')
            if (entry.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError('Symlink in dependency archive')
        if existing:
            # A failed layout check may leave a complete extraction. Resume only
            # after matching every entry to the independently pinned archive.
            for entry in infos:
                if entry.is_dir():continue
                target = extracted / entry.filename
                if target.is_symlink() or not target.is_file() or target.stat().st_size != entry.file_size:
                    raise ValueError('Existing extraction incomplete/changed')
                with package.open(entry) as stream:
                    if hashlib.file_digest(stream, 'sha256').hexdigest() != digest(target):
                        raise ValueError('Existing extraction changed')
        else:
            package.extractall(extracted)  # ZipFile validates each decompressed CRC.
    files = {p.relative_to(BASE).as_posix(): dict(bytes=p.stat().st_size, sha256=digest(p))
             for p in extracted.rglob('*') if p.is_file()}
    # New stock x64 package uses an architecture dispatcher plus explicit real
    # x64/ARM64EC renderer DLLs, unlike the old x86-package .trex layout.
    dll = extracted / 'd3d9_x64.dll'
    if not dll.is_file():
        raise ValueError('Expected standalone x64 runtime missing')
    manifest = dict(release='remix-1.6.1', source_commit=COMMIT, api_version=list(version),
                    archive_url=URL, archive_bytes=ARCHIVE_BYTES, archive_sha256=ARCHIVE_SHA,
                    header_url=HEADER_URL, header_sha256=digest(header), files=files,
                    runtime='runtime/d3d9_x64.dll', scope='Offline experiment only;not production qualification')
    (BASE / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    return verify()


def verify(*, require_host=False):
    manifest = json.loads((BASE / 'manifest.json').read_text())
    if (manifest['source_commit'] != COMMIT or manifest['archive_sha256'] != ARCHIVE_SHA
            or manifest['api_version'] != [0, 6, 5] or manifest['runtime'] != 'runtime/d3d9_x64.dll'):
        raise ValueError('Candidate manifest pin mismatch')
    if manifest['header_sha256'] != HEADER_SHA or digest(BASE / 'remix_c.h') != HEADER_SHA:
        raise ValueError('Candidate header changed')
    for name, receipt in manifest['files'].items():
        path = (BASE / name).resolve()
        path.relative_to((BASE / 'runtime').resolve())
        if path.stat().st_size != receipt['bytes'] or digest(path) != receipt['sha256']:
            raise ValueError('Candidate dependency changed: ' + name)
    exe = ROOT / 'artifacts/remix-runtime/candidate-1.6.1-bin/d3d9_direct_host.exe'
    if require_host:
        build = json.loads((exe.parent / 'build.json').read_text())
        from additive_qualification import sources
        if (build['host_sha256'] != digest(exe) or build['sources'] != sources()
                or build['header_sha256'] != HEADER_SHA):
            raise ValueError('Candidate host build/source/header qualification stale')
    return dict(runtime=BASE / manifest['runtime'], exe=exe, manifest=manifest)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--fetch', action='store_true')
    parser.add_argument('--record-build', action='store_true')
    args = parser.parse_args()
    result = fetch() if args.fetch else verify()
    if args.record_build:
        from additive_qualification import sources
        (result['exe'].parent / 'build.json').write_text(json.dumps(dict(
            host_sha256=digest(result['exe']), header_sha256=HEADER_SHA, sources=sources(),
            architecture='x64', flags='/O2 /fp:precise /W4 /WX',
            scope='Isolated host built from unchanged adapter sources with candidate header'), indent=2))
    print(json.dumps(dict(runtime=str(result['runtime']), files=len(result['manifest']['files']),
                         api_version=result['manifest']['api_version'], exe=str(result['exe'])), indent=2))
