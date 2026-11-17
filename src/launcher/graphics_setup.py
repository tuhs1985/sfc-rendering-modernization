"""First-run graphics setup for the user's separate game copy."""
from contextlib import contextmanager
from hashlib import sha256
import json
import msvcrt
import os
import re

from release_manifest import contained, digest, game_profile_issues, verified_role, verify_game_profile
from setup_adapter import choose, current_setting
from game_profile import prepare_wrapper, sfc_profile

TARGETS = {'DDraw.dll': 'setup_ddraw', 'D3DImm.dll': 'setup_d3dimm',
           'dxgi.dll': 'reshade_baseline_proxy'}
JOURNAL_FILES = {*TARGETS, 'ReShade.ini', 'dgVoodoo.conf'}  # Older setup journals can still be undone.


@contextmanager
def launch_lock(context):
    path = contained(context.package_root, 'data/graphics-setup.lock')
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a+b') as lock:
        lock.seek(0)
        try:
            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError as exc:
            raise ValueError('This copy already has an active SFCRemix launcher.') from exc
        yield


def setup_root(context):
    return contained(context.package_root, 'data/graphics-setup')


def file_hash(path):
    if not path.exists():
        return None
    if not path.is_file() or path.stat().st_size>32*1024*1024:
        raise ValueError('Expected a regular graphics file: ' + path.name)
    return digest(path)


def valid_hash(value):
    return isinstance(value, str) and re.fullmatch(r'[0-9a-f]{64}', value) is not None


def write_synced(path, data):
    with path.open('xb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def replace_file(root, target, data):
    pending = contained(root, 'pending')
    pending.unlink(missing_ok=True)
    write_synced(pending, data)
    os.replace(pending, target)


def clear(root):
    for name in (*JOURNAL_FILES, 'journal.json', 'complete', 'pending'):
        contained(root, name).unlink(missing_ok=True)
    root.rmdir()


def restore(context, game_running):
    root = setup_root(context)
    if not root.exists():
        return False
    if game_running():
        raise ValueError('Close SFC before restoring graphics files.')
    journal = contained(root, 'journal.json')
    if not journal.exists():
        # Game writes begin only after the journal is published.
        clear(root)
        return True
    if journal.stat().st_size > 4096:
        raise ValueError('Invalid graphics setup journal')
    entries = json.loads(journal.read_bytes())
    if not isinstance(entries, dict) or not entries.keys() <= JOURNAL_FILES:
        raise ValueError('Invalid graphics setup journal')
    originals = {}
    for name, hashes in entries.items():
        if not isinstance(hashes, list) or len(hashes)!=2:
            raise ValueError('Invalid graphics setup journal')
        before, after = hashes
        if not valid_hash(after) or (before is not None and not valid_hash(before)):
            raise ValueError('Invalid graphics setup journal')
        target = contained(context.game_root, name)
        backup = contained(root, name)
        if file_hash(target) not in (before, after) or file_hash(backup) != before:
            raise ValueError('Graphics file changed after setup: ' + name + '. Backup retained.')
        originals[name] = backup.read_bytes() if before is not None else None
    for name, original in originals.items():
        target = contained(context.game_root, name)
        current = file_hash(target)
        if current == entries[name][0]:
            continue
        if current != entries[name][1]:
            raise ValueError('Graphics file changed during restore: ' + name)
        if original is None:
            target.unlink()
        else:
            replace_file(root, target, original)
        if file_hash(target) != entries[name][0]:
            raise ValueError('Graphics restore verification failed: ' + name)
    # Once all originals are back, retire the journal before deleting backups.
    journal.unlink()
    clear(root)
    return True


def candidates(context, manifest):
    profile = manifest['game_profile']
    for issue in game_profile_issues(context, manifest):
        if issue.startswith(('Unrecognized proxy conflict:', 'sfc.ini:')):
            raise ValueError(issue)
    result = {}
    for name, role in TARGETS.items():
        source = verified_role(context, manifest, role)
        if source.stat().st_size>32*1024*1024:
            raise ValueError('Packaged graphics input exceeds the size limit: ' + name)
        raw = source.read_bytes()
        if sha256(raw).hexdigest() != profile['files'][name].lower():
            raise ValueError('Packaged graphics input differs from the qualified profile: ' + name)
        result[name] = raw
    wrapper_path = contained(context.game_root, 'dgVoodoo.conf')
    original = b''
    if wrapper_path.exists():
        with wrapper_path.open('rb') as stream:
            original = stream.read(1024*1024+1)
    with contained(context.game_root, 'sfc.ini').open('rb') as stream:
        _, size = sfc_profile(stream.read(1024*1024+1))
    wrapper = prepare_wrapper(original, size)
    preferred = current_setting(wrapper)
    verified, luid = choose(context, manifest, wrapper, preferred)
    result['dgVoodoo.conf'] = verified
    return result, luid


def prepare_graphics(context, manifest, game_running, confirm=input):
    root = setup_root(context)
    if contained(root, 'complete').is_file() and contained(root, 'journal.json').is_file():
        try:
            verify_game_profile(context, manifest)
        except ValueError as exc:
            if not str(exc).startswith('dgVoodoo.conf:'):
                raise
        else:
            return
    if game_running():
        raise ValueError('Close SFC before preparing graphics files.')
    if restore(context, game_running):
        print('Interrupted graphics setup restored.')
    sources, luid = candidates(context, manifest)
    entries = {}
    for name, data in sources.items():
        before = file_hash(contained(context.game_root, name))
        after = sha256(data).hexdigest()
        if before!=after:
            entries[name] = (before, after)
    if entries:
        print('Prepare graphics in this game copy?')
        print(context.game_root)
        for name, (before, _) in entries.items():
            print(f'- {"Replace" if before else "Add"} {name}')
        if 'dgVoodoo.conf' in entries:
            print('dgVoodoo will use SFC\'s resolution, 8x antialiasing and the verified graphics adapter.')
            print('Run SFCRemix-Launch.cmd --restore to recover your original graphics files.')
        if confirm('Type Y to continue: ').strip().casefold() != 'y':
            raise ValueError('Graphics setup cancelled. Game files were kept.')
    if game_running():
        raise ValueError('Close SFC before preparing graphics files.')
    root.mkdir()
    for name, (before, _) in entries.items():
        target = contained(context.game_root, name)
        if file_hash(target)!=before:
            raise ValueError('Graphics file changed during setup: ' + name)
        if before is not None:
            backup = root/name
            write_synced(backup, target.read_bytes())
            if digest(backup)!=before:
                raise ValueError('Graphics backup verification failed: ' + name)
    replace_file(root, root/'journal.json', json.dumps(entries).encode('ascii'))
    try:
        for name, (before, after) in entries.items():
            target = contained(context.game_root, name)
            if file_hash(target)!=before:
                raise ValueError('Graphics file changed during setup: ' + name)
            replace_file(root, target, sources[name])
            if digest(target)!=after:
                raise ValueError('Graphics setup verification failed: ' + name)
        verify_game_profile(context, manifest)
        write_synced(root/'complete', luid.encode('ascii'))
    except Exception:
        restore(context, game_running)
        raise
    print('Graphics setup complete.')
