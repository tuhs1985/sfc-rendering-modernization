"""Release integrity, separate from development source/GPU qualification receipts."""
import hashlib
import json
import os
from pathlib import Path
from runtime_context import CLIENT_SHA256, VERSION, relative_name

SCHEMA = 'sfc.alpha.package.v1'
MANIFEST = 'package.json'
REQUIRED_ROLES = frozenset({
    'coordinator', 'python', 'launcher', 'restore', 'return_launcher', 'return_host',
    'return_addon', 'startup_gate', 'semantic_component', 'semantic_controller', 'renderer',
    'output_receiver', 'job_guard', 'mesh_checksum', 'texture_hash',
    'remix_runtime', 'reshade_proxy', 'default_rendering', 'default_lights',
    'project_license', 'third_party_notices',
    'scene_placement', 'owner_selection',
    'troubleshooting_launcher',
})


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def contained(root, name):
    path = root / relative_name(name)
    resolved = path.resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError('Package path escapes its root')
    # The ZIP layout never needs links. Reject junctions as well as symlinks,
    # including parents even when they resolve to another path inside the root.
    for part in (path, *path.parents):
        if part == root.parent:
            break
        if part.is_symlink() or (hasattr(part, 'is_junction') and part.is_junction()):
            raise ValueError('Package links/reparse directories unsupported')
    return path


def load(root):
    root = Path(root)
    path = root / MANIFEST
    if path.stat().st_size > 4 * 1024 * 1024:
        raise ValueError('Release manifest exceeds bound')
    value = json.loads(path.read_text(encoding='utf-8'))
    if (value.get('schema') != SCHEMA or value.get('version') != VERSION or
            value.get('client_sha256') != CLIENT_SHA256 or value.get('platform') != 'windows-x64'):
        raise ValueError('Unsupported package identity or game build')
    files = value.get('files')
    roles = value.get('roles')
    if (not isinstance(files, dict) or not 1 <= len(files) <= 20000 or
            not isinstance(roles, dict) or not REQUIRED_ROLES <= roles.keys()):
        raise ValueError('Incomplete release file/role manifest')
    seen = set()
    for name, entry in files.items():
        path = relative_name(name)
        if path.parts[0].casefold() in ('data', 'settings') or name == MANIFEST:
            raise ValueError('Mutable data cannot be a package integrity input')
        key = name.casefold()
        if key in seen:
            raise ValueError('Duplicate case-insensitive package name')
        seen.add(key)
        if (not isinstance(entry, dict) or type(entry.get('bytes')) is not int or
                not 0 <= entry['bytes'] <= 2 * 1024**3 or
                not isinstance(entry.get('sha256'), str) or len(entry['sha256']) != 64 or
                any(c not in '0123456789abcdef' for c in entry['sha256'])):
            raise ValueError('Malformed package file receipt')
    if any(not isinstance(name, str) or name not in files for name in roles.values()):
        raise ValueError('Package role names an unlisted file')
    return value


def verify(context):
    """Read-only; neither repairs files nor changes an unrecognized game stack."""
    if not context.release:
        raise ValueError('Release manifest requires a packaged context')
    value = load(context.package_root)
    expected={name.casefold() for name in value['files']}|{MANIFEST}
    for directory, dirs, names in os.walk(context.package_root,followlinks=False):
        if Path(directory)==context.package_root:
            dirs[:]=[d for d in dirs if d.casefold() not in ('data','settings')]
        for name in (*dirs,*names):
            path=Path(directory)/name
            relative=path.relative_to(context.package_root).as_posix()
            contained(context.package_root,relative)
            if name in names and relative.casefold() not in expected:
                raise ValueError('Unlisted immutable package file: '+relative)
    for name, entry in value['files'].items():
        path = contained(context.package_root, name)
        if not path.is_file() or path.stat().st_size != entry['bytes'] or digest(path) != entry['sha256']:
            raise ValueError('Package input missing or changed: ' + name)
    exe = context.game_root / 'StarFleetOP.exe'
    if not exe.is_file() or digest(exe).upper() != CLIENT_SHA256:
        raise ValueError('Supported StarFleetOP.exe not found beside the extracted package')
    return value


def verified_role(context, manifest, role):
    return contained(context.package_root, manifest['roles'][role])


def verify_game_profile(context, manifest):
    """Recognize a graphics stack before transaction code may touch the copy.

    Package hashes alone say nothing about graphics files already in the game.
    Do not enroll an arbitrary local stack as a trusted first-launch baseline.
    """
    from copied_preferences import protected_ini_sha256
    profile = manifest.get('game_profile', {})
    hashes = profile.get('files', {})
    required = {'DDraw.dll', 'D3DImm.dll', 'dxgi.dll', 'dgVoodoo.conf', 'ReShade.ini'}
    if set(hashes) != required or not isinstance(profile.get('sfc_protected_sha256'), str):
        raise ValueError('Package lacks a qualified game graphics profile')
    for name, expected in hashes.items():
        path = context.game_root / name
        if name=='dgVoodoo.conf' and profile.get('dimension_profile'):
            continue
        if not path.is_file() or digest(path).upper() != expected.upper():
            raise ValueError('Unsupported graphics file: ' + name +
                             '. Restore the supported game-copy profile; no files were changed.')
    if profile.get('dimension_profile'):
        from game_profile import signature
        if signature((context.game_root/'sfc.ini').read_bytes(),(context.game_root/'dgVoodoo.conf').read_bytes())!=profile['dimension_profile']:
            raise ValueError('Unsupported protected game graphics settings; no files were changed')
    elif protected_ini_sha256((context.game_root / 'sfc.ini').read_bytes()) != profile['sfc_protected_sha256']:
        raise ValueError('Unsupported protected game settings; no files were changed')
    for name in ('ddraw.dll', 'd3d8.dll', 'd3d9.dll', 'winmm.dll', 'version.dll'):
        if name.casefold() not in {n.casefold() for n in hashes} and (context.game_root / name).exists():
            # This distribution also contains a pinned, unused dgVoodoo D3D8
            # component. Recognize only its independently identified bytes.
            if name=='d3d8.dll' and digest(context.game_root/name).upper()=='72BD6B84FACE40B928DFD5D1EE6D30F2CE8671919D0264B24513E25A2C647FD3':
                continue
            raise ValueError('Unrecognized proxy conflict: ' + name + '; no files were changed')
    return profile


def seed_settings(context, manifest):
    """Only explicit bootstrap calls seed profiles; updates preserve user edits."""
    for role, name in (('default_rendering', 'rendering.toml'), ('default_lights', 'lights.toml')):
        source = contained(context.package_root, manifest['roles'][role])
        target = context.setting(name)
        if target.exists():
            contained(context.package_root, 'settings/' + name)
            if not target.is_file():
                raise ValueError('Settings target is not an ordinary file')
            continue
        context.settings_root.mkdir(parents=True, exist_ok=True)
        # Refuse unexpected links/junctions before opening a settings destination.
        contained(context.package_root, 'settings/' + name)
        try:
            with target.open('xb') as stream:
                stream.write(source.read_bytes())
        except FileExistsError:
            # Another bootstrap may have seeded the same immutable default.
            # Actual play still requires the separate single-session gate.
            pass
