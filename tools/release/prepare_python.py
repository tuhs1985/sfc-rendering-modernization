"""Prepare pinned app-local Python; never copy the developer/Codex interpreter."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
LOCK = Path(__file__).with_name('python-dependencies.json')


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def obtain(entry, downloads):
    name = entry['filename']
    if Path(name).name != name or any(x in name for x in ('\\', ':')):
        raise ValueError('Dependency filename')
    target = downloads / name
    if not target.exists():
        temporary = target.with_suffix(target.suffix + '.pending')
        request = urllib.request.Request(entry['url'], headers={'User-Agent': 'SFC-Modernize-release-build'})
        count = 0
        try:
            with urllib.request.urlopen(request, timeout=45) as response, temporary.open('xb') as stream:
                while block := response.read(1024 * 1024):
                    count += len(block)
                    if count > entry['bytes']:
                        raise ValueError('Dependency download size exceeded')
                    stream.write(block)
            if count != entry['bytes'] or digest(temporary) != entry['sha256']:
                raise ValueError('Downloaded dependency checksum/size mismatch')
            temporary.replace(target)
        finally:
            if temporary.exists():
                temporary.unlink()
    if target.stat().st_size != entry['bytes'] or digest(target) != entry['sha256']:
        raise ValueError('Cached dependency checksum/size mismatch: ' + name)
    return target


def prepare(destination):
    lock = json.loads(LOCK.read_text())
    destination = Path(destination).resolve()
    destination.relative_to(ROOT / 'artifacts')
    if destination.exists():
        raise ValueError('Python destination already exists; preserve it and choose a fresh build folder')
    downloads = ROOT / 'artifacts/alpha/dependencies'
    downloads.mkdir(parents=True, exist_ok=True)
    archive = obtain(lock['python'], downloads)
    wheels = [obtain(entry, downloads) for entry in lock['wheels']]
    with tarfile.open(archive, 'r:gz') as package:
        entries = package.getmembers()
        if len(entries) > 20000 or sum(v.size for v in entries) > 512 * 1024**2:
            raise ValueError('Python extraction bound')
        for entry in entries:
            path = PurePosixPath(entry.name)
            if (path.is_absolute() or '..' in path.parts or '\\' in entry.name or ':' in entry.name or
                    not path.parts or path.parts[0] != 'python' or
                    not (entry.isfile() or entry.isdir())):
                raise ValueError('Python archive path/type unsupported')
        destination.parent.mkdir(parents=True, exist_ok=True)
        stage = destination.with_name(destination.name + '.extracting')
        if stage.exists():
            raise ValueError('Interrupted Python extraction exists; review before retry')
        stage.mkdir()
        package.extractall(stage, members=entries, filter='data')
    shutil.move(str(stage / 'python'), str(destination))
    stage.rmdir()
    executable = destination / 'python.exe'
    subprocess.run([str(executable), '-I', '-m', 'pip', 'install', '--no-index', '--no-deps',
                    '--disable-pip-version-check', *map(str, wheels)], check=True)
    script = ("import sys,json,numpy,PIL;assert sys.version_info[:3]==(3,12,14);"
              "assert numpy.__version__=='2.3.5';assert PIL.__version__=='12.3.0';"
              "print(json.dumps(dict(python=sys.version.split()[0],prefix=sys.prefix,"
              "numpy=numpy.__version__,pillow=PIL.__version__)))")
    result = subprocess.check_output([str(executable), '-I', '-c', script], text=True)
    receipt = dict(result='APP_LOCAL_PYTHON_PREPARED', lock_sha256=digest(LOCK),
                   runtime=json.loads(result), downloaded_from_upstream=True, copied_codex_runtime=False,
                   dependencies=[lock['python'], *lock['wheels']])
    (destination.parent / (destination.name + '-receipt.json')).write_text(json.dumps(receipt, indent=2))
    print(result, end='')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--destination', type=Path, required=True)
    prepare(parser.parse_args().destination)
