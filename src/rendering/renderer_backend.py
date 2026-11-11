"""Select and verify the pinned renderer and configure its child process."""
import hashlib
import json
from pathlib import Path

from runtime_context import CONTEXT

BASE = CONTEXT.artifact('remix-runtime/deps/candidate-1.6.1')
COMMIT = '0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0'
ARCHIVE_SHA = '7dd1d44492a609050e44b0e3581cec31135d1ed88b4a91123b4faae91955716a'
HEADER_SHA = '26a5607a07e8718298c35519e53bbc71d526186a947e5a2a5b613a0d6db04f3a'


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def verify(*, require_host=False, base=None):
    base = BASE if base is None else base
    if CONTEXT.release:
        from release_manifest import load,verified_role
        manifest=load(CONTEXT.package_root)
        pin=manifest.get('remix',{})
        if pin!={'release':'1.6.1','source_commit':COMMIT,'api_version':[0,6,5],'header_sha256':HEADER_SHA}:
            raise ValueError('Release runtime/SDK pair differs from the qualified pin')
        return dict(runtime=verified_role(CONTEXT,manifest,'remix_runtime'),
                    exe=verified_role(CONTEXT,manifest,'renderer'),
                    manifest=dict(source_commit=COMMIT,api_version=[0,6,5],header_sha256=HEADER_SHA))
    manifest = json.loads((base / 'manifest.json').read_text())
    if (manifest['source_commit'] != COMMIT or manifest['archive_sha256'] != ARCHIVE_SHA
            or manifest['api_version'] != [0, 6, 5] or manifest['runtime'] != 'runtime/d3d9_x64.dll'):
        raise ValueError('Candidate manifest pin mismatch')
    if manifest['header_sha256'] != HEADER_SHA or digest(base / 'remix_c.h') != HEADER_SHA:
        raise ValueError('Candidate header changed')
    for name, receipt in manifest['files'].items():
        path = (base / name).resolve()
        path.relative_to((base / 'runtime').resolve())
        if path.stat().st_size != receipt['bytes'] or digest(path) != receipt['sha256']:
            raise ValueError('Candidate dependency changed: ' + name)
    exe = CONTEXT.artifact('remix-runtime/candidate-1.6.1-bin/d3d9_direct_host.exe')
    if require_host:
        build = json.loads((exe.parent / 'build.json').read_text())
        from source_inventory import sources
        if (build['host_sha256'] != digest(exe) or build['sources'] != sources()
                or build['header_sha256'] != HEADER_SHA):
            raise ValueError('Candidate host build/source/header qualification stale')
    return dict(runtime=base / manifest['runtime'], exe=exe, manifest=manifest)


def configure_child(backend,environment):
    if not backend or backend.get('release')!='1.6.1':
        raise ValueError('Verified async material checkout backend required')
    before=environment.get('DXVK_ASYNC_ASSET_LOADING')
    environment['DXVK_ASYNC_ASSET_LOADING']='1'
    # Exercise the existing private renderer startup once. Its completion precedes
    # shared startup readiness; afterward warm_start waits without further Presents.
    environment['SFC_D3D9_RENDER_PREWARM']='triangle'
    environment['SFC_D3D9_STARTUP_PROFILE']='0' if environment.get('SFC_RELEASE_ROOT') else '1'
    return ('rtx.initializer.asyncAssetLoading = True\n'
            'rtx.enableReplacementAssets = True\n'),dict(
        release='1.6.1',material_library='flat',complete_asset_stages=True,
        initial_material_priming=True,private_render_prewarm='triangle',
        supplied_async_asset_loading='1',inherited_async_asset_loading=before,
        host_sha256=backend['host_sha256'],runtime_sha256=backend['runtime_sha256'],
        header_sha256=backend['header_sha256'],scope='Explicit checkout child only;normal1.5.2 unchanged')


def backend_inputs():
    candidate=verify(require_host=True)
    return dict(release='1.6.1',exe=candidate['exe'],runtime=candidate['runtime'],
        host_sha256=digest(candidate['exe']),runtime_sha256=digest(candidate['runtime']),
        header_sha256=candidate['manifest']['header_sha256'],
        source_commit=candidate['manifest']['source_commit'],
        source_parity='Packaged5a7eec84/public0a6cd5b not instruction-level verified')


def receipt(backend):
    return {k:str(v) if k in ('exe','runtime') else v for k,v in backend.items()}
