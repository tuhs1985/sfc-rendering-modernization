"""Read-only build audit. Import closure is a superset, not a load-time claim."""
import ast
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
# Non-Python inputs are invisible to the import walk. Keep this allowlist
# explicit: never copy arbitrary neighboring files (including game assets).
RUNTIME_RESOURCES={
    'scene_placement':'tools/d3d9_proof/multi_ship.toml',
    'owner_selection':'tools/d3d9_proof/offset_ship.toml',
}
sys.path.insert(0,str(ROOT/'tools/recon'))
from inspect_pe import inspect


def python_closure(entry):
    modules={};ambiguous=set()
    for path in (ROOT/'tools').rglob('*.py'):
        if path.stem in modules and modules[path.stem]!=path:ambiguous.add(path.stem)
        modules[path.stem]=path
    queue=[Path(entry)];seen=set();external=set()
    while queue:
        path=queue.pop()
        if path in seen:continue
        seen.add(path)
        for node in ast.walk(ast.parse(path.read_text(encoding='utf-8-sig'))):
            names=([a.name.split('.')[0] for a in node.names] if isinstance(node,ast.Import)
                   else [node.module.split('.')[0]] if isinstance(node,ast.ImportFrom) and node.module else [])
            for name in names:
                if name in ambiguous:raise ValueError('Ambiguous local import; qualify actual search order: '+name)
                if name in modules:queue.append(modules[name])
                else:external.add(name)
    return dict(scope='Static superset includes inactive development/diagnostic branches;verify actual release imports before packaging',
                files=[str(p.relative_to(ROOT)).replace('\\','/') for p in sorted(seen)],
                resources=dict(RUNTIME_RESOURCES),external_modules=sorted(external))


def native_inventory(paths):
    result=[]
    for path in paths:
        path=Path(path);value=inspect(path)
        result.append(dict(path=str(path.relative_to(ROOT)).replace('\\','/'),
                           sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                           machine=value['machine'],imports=[i['dll'] for i in value['imports']]))
    return result


if __name__=='__main__':
    binaries=[ROOT/name for name in (
        'artifacts/remix-runtime/return-bin/return_launcher.exe',
        'artifacts/remix-runtime/return-bin/return_host.exe',
        'artifacts/remix-runtime/return-bin/SFCRemixReturn.dll',
        'artifacts/m1/bin/m1_gate.dll','artifacts/m1/bin/m1_controller.exe',
        'artifacts/remix-runtime/native-light-tests/m1_light_component.dll',
        'artifacts/remix-runtime/candidate-1.6.1-bin/d3d9_direct_host.exe',
        'artifacts/d3d9-proof/receiver-bin/output_receiver.exe',
        'artifacts/remix-ingest/bin/bounded_job.exe',
        'artifacts/d3d9-proof/mesh-checksum/mesh_checksum.dll',
        'artifacts/alpha/python-3.12.14/python.exe',
        'artifacts/alpha/launcher-bin/launcher.exe')]
    output=ROOT/'artifacts/alpha/dependency-inventory.json'
    output.write_text(json.dumps(dict(python=python_closure(ROOT/'tools/release/bootstrap.py'),
                                     native=native_inventory(binaries)),indent=2))
    print(output)
