"""Functional component qualification; no observation workers or analysis imports."""
from pathlib import Path
import hashlib
import json
from runtime_context import CONTEXT
ROOT=CONTEXT.code_root
BIN=CONTEXT.artifact('remix-runtime/native-light-tests')
RECEIPT=BIN/'qualification.json'
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def sources():
    base=ROOT/'tools/m1_component'
    paths=list(base.glob('*.h'))+list(base.glob('*.cpp'))
    paths += [base/'build_light_discovery.ps1',base/'build_native_light_tests.ps1',base/'native_light_component.def',ROOT/'tests/m1_live_scene_tests.cpp',ROOT/'tests/m1_mesh_export_tests.cpp',ROOT/'tests/native_light_snapshot_tests.cpp',
              ROOT/'tests/native_light_observer_tests.cpp',ROOT/'tools/remix_runtime/light_discovery.py',
              ROOT/'tools/remix_runtime/native_light_state.py',
              ROOT/'tools/remix_runtime/run_return_game.py',
              ROOT/'tools/remix_runtime/start_return_image_session.ps1',
              ROOT/'tools/remix_runtime/start_light_discovery_session.ps1']
    paths += list((ROOT/'src/session').glob('*.py'))
    paths += list((ROOT/'src/runtime').glob('*.py'))
    paths += list((ROOT/'tools/session_diagnostics').glob('*.py'))
    return {str(p.relative_to(ROOT)):digest(p) for p in sorted(set(paths))}

def require_qualification():
    if CONTEXT.release:
        from release_manifest import load
        manifest=load(CONTEXT.package_root)
        return dict(result='RELEASE_MANIFEST_INPUTS',version=manifest['version'])
    q=json.loads(RECEIPT.read_text())
    if q.get('result')!='OFFLINE_NATIVE_LIGHT_DISCOVERY_QUALIFIED' or q.get('sources')!=sources() or q.get('component_sha256')!=digest(BIN/'m1_light_component.dll'):
        raise ValueError('Native light discovery qualification stale/missing')
    return q
