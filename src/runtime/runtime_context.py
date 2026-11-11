"""Application-local paths shared by development and packaged play.

Construction is read-only. Only the release bootstrap seeds settings/directories;
importing a module never writes into the selected game or an accepted install.
"""
from dataclasses import dataclass
import os
from pathlib import Path, PurePosixPath
from typing import Mapping

CODE_ROOT = Path(__file__).resolve().parents[2]
CLIENT_SHA256 = '4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29'
VERSION = '0.1.0-alpha.1'


def relative_name(value):
    """Manifest/artifact names are portable relative paths, never shell text."""
    if not isinstance(value, str) or not value or '\\' in value or ':' in value:
        raise ValueError('Expected a portable relative path')
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in ('', '.', '..') for part in value.split('/')):
        raise ValueError('Expected a portable relative path')
    return path


@dataclass(frozen=True)
class RuntimeContext:
    mode: str
    code_root: Path
    package_root: Path
    game_root: Path
    accepted_root: Path
    data_root: Path
    settings_root: Path
    python: Path

    @property
    def release(self):
        return self.mode == 'release'

    @property
    def artifact_root(self):
        return self.data_root if self.release else self.code_root / 'artifacts'

    def relative(self, path):
        """Portable evidence reference; never truncate an outside absolute path."""
        root = self.package_root if self.release else self.code_root
        return Path(path).resolve().relative_to(root.resolve())

    def reference(self, name):
        root = self.package_root if self.release else self.code_root
        path = root / relative_name(name.replace('\\', '/'))
        if not path.resolve().is_relative_to(root.resolve()):
            raise ValueError('Evidence reference escapes the application root')
        return path

    def artifact(self, name):
        path = relative_name(name)
        if not self.release:
            return self.code_root / 'artifacts' / path
        # Existing logical build paths remain recognizable, but immutable inputs
        # and writable session/cache data occupy distinct package subtrees.
        for prefix, destination in (
            ('remix-runtime/runs', self.data_root / 'runs'),
            ('remix-runtime/archives', self.data_root / 'archives'),
            ('remix-runtime/test-install', self.data_root / 'baseline'),
            ('d3d9-proof/runs', self.data_root / 'offline-runs'),
            ('d3d9-intercept/direct64-runs', self.data_root / 'direct64-runs'),
            ('d3d9-proof/environment-cache', self.data_root / 'cache/environment'),
        ):
            base = PurePosixPath(prefix)
            if path == base or base in path.parents:
                return destination / path.relative_to(base)
        return self.package_root / 'runtime' / path

    def setting(self, name):
        path = relative_name(name)
        if len(path.parts) != 1 or path.suffix != '.toml':
            raise ValueError('Settings must name one TOML profile')
        return self.settings_root / path

    def child_environment(self):
        return {'SFC_RELEASE_ROOT': str(self.package_root)} if self.release else {}


def development(code_root=CODE_ROOT):
    root = Path(code_root).resolve()
    return RuntimeContext(
        mode='development', code_root=root, package_root=root,
        game_root=Path(r'C:\Project\SFC-Remix-Return-Test'),
        accepted_root=Path(r'C:\Games\Taldren Software Inc\Starfleet Command Orion Pirates'),
        data_root=root / 'artifacts', settings_root=root / 'tools/remix_runtime/config',
        python=Path(r'C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'))


def packaged(package_root):
    root = Path(package_root).resolve()
    if root.name != 'SFCRemix':
        raise ValueError('Release root must be the extracted SFCRemix directory')
    game = root.parent
    # Both refer to the user-owned game copy, not this workstation's accepted
    # installation. Release baseline snapshots separately protect touched files.
    return RuntimeContext(
        mode='release', code_root=root / 'code', package_root=root,
        game_root=game, accepted_root=game, data_root=root / 'data',
        settings_root=root / 'settings', python=root / 'python/python.exe')


def load(environment: Mapping[str, str] | None = None):
    env = os.environ if environment is None else environment
    explicit = env.get('SFC_RELEASE_ROOT')
    return packaged(explicit) if explicit else development()


CONTEXT = load()
