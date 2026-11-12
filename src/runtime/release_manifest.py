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
    'output_receiver', 'job_guard', 'mesh_checksum',
    'remix_runtime', 'reshade_proxy', 'default_rendering', 'default_lights',
    'project_license', 'third_party_notices',
    'troubleshooting_launcher',
})
SETUP_ROLES = frozenset({'setup_ddraw', 'setup_d3dimm',
                         'setup_remix_probe', 'setup_wrapper_probe', 'reshade_baseline_proxy'})
SETUP_INPUT_ROLES = SETUP_ROLES - {'reshade_baseline_proxy'} | {'setup_dgvoodoo', 'setup_reshade'}
PROFILE_FILES = frozenset({'DDraw.dll', 'D3DImm.dll', 'dxgi.dll'})


def setup_enabled(manifest):
    return SETUP_ROLES <= manifest.get('roles', {}).keys()


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
    if SETUP_INPUT_ROLES & roles.keys() and not setup_enabled(value):
        raise ValueError('Incomplete graphics setup inputs')
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


def game_profile_issues(context, manifest):
    """Read-only checks shared by launch admission and the tester report."""
    from copied_preferences import protected_ini_sha256

    profile = manifest.get('game_profile', {})
    hashes = profile.get('files', {})
    # Older packages included a ReShade.ini hash. It is user configuration.
    if set(hashes) - {'ReShade.ini', 'dgVoodoo.conf'} != PROFILE_FILES:
        raise ValueError('Package lacks a qualified game graphics profile')
    versions = {
        'DDraw.dll': 'the qualified dgVoodoo 2.86.5 x86 DDraw.dll',
        'D3DImm.dll': 'the qualified dgVoodoo 2.86.5 x86 D3DImm.dll',
        'dxgi.dll': 'the qualified baseline ReShade 6.7.1.2133 x86 dxgi.dll',
    }
    dimensions = profile.get('dimension_profile')
    for name, expected in hashes.items():
        if name == 'ReShade.ini':
            continue
        if name == 'dgVoodoo.conf' and dimensions:
            continue
        path = context.game_root / name
        if not path.is_file():
            yield f'Missing graphics file: {name}. The game copy needs {versions.get(name, "the qualified " + name)}.'
        elif digest(path).upper() != expected.upper():
            yield f'Unsupported graphics file: {name}. The game copy needs {versions.get(name, "the qualified " + name)}.'

    def inspect(name, parser):
        path = context.game_root / name
        if not path.is_file():
            raise ValueError('Missing file')
        with path.open('rb') as stream:
            return parser(stream.read(1024 * 1024 + 1))

    if dimensions:
        from game_profile import SIZES, matching_dimensions, sfc_profile, wrapper_profile, wrapper_requirements

        if (set(dimensions) != {'schema', 'sfc_sha256', 'dg_sha256'} or
                dimensions['schema'] != 'sfc.alpha.graphics-dimensions.v1'):
            raise ValueError('Package lacks a qualified resolution profile')
        supported = ', '.join(f'{w}x{h}' for w, h in SIZES)
        native = wrapper = None
        try:
            native = inspect('sfc.ini', sfc_profile)
        except ValueError as exc:
            yield f'sfc.ini: {exc}. Use one supported [3D] Width/Height pair: {supported}.'
        def inspect_wrapper(raw):
            wrapper_requirements(raw)
            if setup_enabled(manifest):
                from setup_adapter import current_setting
                current_setting(raw)
            return wrapper_profile(raw)

        try:
            wrapper = inspect('dgVoodoo.conf', inspect_wrapper)
        except ValueError as exc:
            yield f'dgVoodoo.conf: {exc}. The qualified profile requires DesktopResolution and Resolution.'
        if native and wrapper and not matching_dimensions(native[1], *wrapper[1:]):
            w, h = native[1]
            yield (f'dgVoodoo.conf: resolution does not match sfc.ini ({w}x{h}). '
                   f'Set DesktopResolution={w}x{h} and Resolution=h:{w}, v:{h}.')
    else:
        try:
            actual = inspect('sfc.ini', protected_ini_sha256)
        except ValueError as exc:
            yield f'sfc.ini: {exc}. The game copy needs the qualified settings.'
        else:
            if actual != profile['sfc_protected_sha256']:
                yield 'sfc.ini: settings outside the player name differ from the qualified profile.'

    for name in ('ddraw.dll', 'd3d8.dll', 'd3d9.dll', 'winmm.dll', 'version.dll'):
        if name.casefold() not in {n.casefold() for n in hashes} and (context.game_root / name).exists():
            # This distribution also contains a pinned, unused dgVoodoo D3D8
            # component. Recognize only its independently identified bytes.
            if name=='d3d8.dll' and digest(context.game_root/name).upper()=='72BD6B84FACE40B928DFD5D1EE6D30F2CE8671919D0264B24513E25A2C647FD3':
                continue
            yield f'Unrecognized proxy conflict: {name}. Use a separate game copy with the qualified graphics stack.'


def verify_game_profile(context, manifest):
    """Require the qualified profile before touching graphics files."""
    issue = next(game_profile_issues(context, manifest), None)
    if issue:
        raise ValueError(issue + ' No files were changed.')
    return manifest['game_profile']


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
