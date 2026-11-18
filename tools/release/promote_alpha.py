"""Promote tested alpha bytes after explicit source/vendor provenance checks.

Only README and package metadata change. This never builds or alters binaries,
copies a game directory, changes a running installation, or publishes anything.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

from build_zip import write

ROOT = Path(__file__).resolve().parents[2]
LAUNCHER_SOURCE = '69a682d'
CANDIDATE_SHA256 = 'b1c992f442cf2ba178029b8e3444e2da93a0123daa4532bcc2d8eecbd61725c1'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def text(data):
    return data.decode('utf-8-sig').replace('\r\n', '\n')


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def checked_payload(archive):
    names = archive.namelist()
    if len(names) != len(set(n.casefold() for n in names)):
        raise ValueError('Duplicate ZIP names')
    manifest = json.loads(archive.read('SFCRemix/package.json'))
    expected = {'SFCRemix/' + n for n in manifest['files']}
    expected |= {'SFCRemix/package.json', 'SFCRemix-Launch.cmd'}
    if set(names) != expected:
        raise ValueError('ZIP differs from immutable allowlist')
    for name in names:
        if name.startswith('/') or '\\' in name or ':' in name or '..' in Path(name).parts:
            raise ValueError('Unsafe ZIP path')
    for name, entry in manifest['files'].items():
        raw = archive.read('SFCRemix/' + name)
        if len(raw) != entry['bytes'] or sha(raw) != entry['sha256']:
            raise ValueError('Immutable input mismatch: ' + name)
        if Path(name).suffix.lower() == '.mod' or Path(name).name.lower().startswith('starfleetop.'):
            raise ValueError('Game payload forbidden')
    return manifest


def compare_vendor(candidate, reference):
    if candidate['provenance'] != reference['provenance']:
        raise ValueError('Provenance inventory changed')
    if set(candidate['files']) != set(reference['files']):
        raise ValueError('Payload inventory changed')
    for name, provenance in candidate['provenance'].items():
        if provenance['kind'] == 'vendor' and candidate['files'][name] != reference['files'][name]:
            raise ValueError('Vendor input differs from reviewed reference: ' + name)


def promote(candidate, reference, recipe_file, commit, output):
    candidate, reference, output = map(lambda p: Path(p).resolve(), (candidate, reference, output))
    if output.exists() or not output.is_relative_to((ROOT / 'artifacts/alpha/public').resolve()):
        raise ValueError('Use a new output beneath artifacts/alpha/public')
    if not output.name.endswith('.zip'):
        raise ValueError('ZIP output required')
    for path in (candidate, reference):
        expected = path.with_suffix('.zip.sha256').read_text().split()[0]
        if sha(path.read_bytes()) != expected:
            raise ValueError('Input ZIP checksum mismatch')
    resolved = git('rev-parse', commit + '^{commit}').decode().strip()
    if sha(candidate.read_bytes()) != CANDIDATE_SHA256:
        raise ValueError('Candidate is not the qualified alpha input')
    recipe = json.loads(Path(recipe_file).read_text(encoding='utf-8-sig'))
    with zipfile.ZipFile(candidate) as source, zipfile.ZipFile(reference) as previous:
        manifest, inherited = checked_payload(source), checked_payload(previous)
        if (inherited.get('private_checkout') or not inherited.get('commit')
                or recipe.get('license_review') != 'complete'
                or recipe.get('commit') != inherited['commit']):
            raise ValueError('Complete reviewed reference and source commit required')
        reviewed = {item['target']: item['sha256'] for item in recipe['files']}
        if reviewed != {name: entry['sha256'] for name, entry in inherited['files'].items()}:
            raise ValueError('Reviewed recipe does not match reference payload')
        compare_vendor(manifest, inherited)
        if manifest['roles'] != inherited['roles'] or manifest['game_profile'] != inherited['game_profile']:
            raise ValueError('Application roles or game profile changed')
        if manifest['remix'] != inherited['remix'] or manifest['client_sha256'] != inherited['client_sha256']:
            raise ValueError('Runtime/client pin changed')
        code_count = 0
        for name, provenance in manifest['provenance'].items():
            if provenance['kind'] != 'project':
                continue
            if name.startswith('code/') and name.endswith('.py'):
                if text(source.read('SFCRemix/' + name)) != text(git('show', resolved + ':' + name[5:])):
                    raise ValueError('Packaged application differs from committed source: ' + name)
                code_count += 1
            elif name != 'launcher.exe' and manifest['files'][name] != inherited['files'][name]:
                raise ValueError('Unqualified project input changed: ' + name)
        if text(source.read('SFCRemix-Launch.cmd')) != text(git('show', resolved + ':src/launcher/SFCRemix-Launch.cmd')):
            raise ValueError('CMD launcher source differs')
        # Preserve build provenance instead of claiming binaries were rebuilt now.
        changes = set(git('diff', '--name-only', inherited['commit'], resolved, '--', '*.cpp', '*.h').decode().splitlines())
        if changes != {'src/launcher/launcher.cpp'}:
            raise ValueError('Native source lineage changed beyond the qualified launcher')
        if git('show', LAUNCHER_SOURCE + ':src/launcher/launcher.cpp') != git('show', resolved + ':src/launcher/launcher.cpp'):
            raise ValueError('Launcher source differs from qualified startup-indicator revision')
        # The candidate's sidecar and preserved gameplay/setup receipts bind its launcher.
        readme = git('show', resolved + ':tools/release/ALPHA-README.md')
        manifest['files']['README.md'] = {'bytes': len(readme), 'sha256': sha(readme)}
        manifest.update(commit=resolved, private_checkout=False, license_review='complete')
        manifest['promotion'] = dict(candidate_sha256=sha(candidate.read_bytes()),
                                     reviewed_reference_sha256=sha(reference.read_bytes()),
                                     inherited_native_source=inherited['commit'],
                                     launcher_source=git('rev-parse', LAUNCHER_SOURCE).decode().strip(),
                                     application_modules_checked=code_count,
                                     runtime_binaries_changed=False,
                                     changed_payloads=['README.md', 'package.json'])
        output.parent.mkdir(parents=True, exist_ok=True)
        pending = output.with_suffix('.zip.pending')
        if pending.exists():
            raise ValueError('Interrupted output exists')
        try:
            with zipfile.ZipFile(pending, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as target:
                for name in sorted(source.namelist()):
                    raw = (json.dumps(manifest, indent=2, sort_keys=True).encode() if name == 'SFCRemix/package.json'
                           else readme if name == 'SFCRemix/README.md' else source.read(name))
                    write(target, name, raw)
            with zipfile.ZipFile(pending) as result:
                checked_payload(result)
                for name in source.namelist():
                    if name not in ('SFCRemix/package.json', 'SFCRemix/README.md') and result.read(name) != source.read(name):
                        raise ValueError('Runtime bytes changed during promotion')
            pending.rename(output)
        except BaseException:
            pending.unlink(missing_ok=True)
            raise
    checksum = sha(output.read_bytes())
    output.with_suffix('.zip.sha256').write_text(checksum + '  ' + output.name + '\n', encoding='ascii')
    result = dict(version=manifest['version'], source_commit=resolved, bytes=output.stat().st_size,
                  sha256=checksum, files=len(manifest['files']), promotion=manifest['promotion'])
    output.with_suffix('.zip.promotion.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--reference-recipe', type=Path, required=True)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(promote(args.candidate, args.reference, args.reference_recipe, args.commit, args.output), indent=2))
