"""Independent build lock; never rewrites the ordinary-D3D9 preparation receipt."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/remix_runtime'))
from additive_qualification import sources,configs,digest
RECORD=ROOT/'artifacts/remix-api-proof/bin/build.json'
def inputs():
    code=sources()
    for p in (ROOT/'tools/remix_api_proof').rglob('*'):
        if p.is_file() and p.suffix in ('.h','.cpp','.py','.ps1'):
            code[p.relative_to(ROOT).as_posix()]=digest(p)
    header=ROOT/'artifacts/remix-runtime/deps/remix_c.h'
    return dict(sources=code,configs=configs(),header_sha256=digest(header),
        host_sha256=digest(RECORD.parent/'api_host.exe'),
        mock_sha256=digest(RECORD.parent/'api_renderer_tests.exe'),
        runtime_manifest_sha256=digest(ROOT/'artifacts/remix-runtime/deps/manifest.json'))
def verify():
    if json.loads(RECORD.read_text())!=inputs():raise ValueError('Isolated API build/source/config lock stale')
    return inputs()
if __name__=='__main__':
    if sys.argv[1:]!=['--record']:raise ValueError('Explicit --record after native build/tests only')
    RECORD.write_text(json.dumps(inputs(),indent=2));verify();print('Isolated API build lock recorded')
