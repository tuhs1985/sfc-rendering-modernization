"""Private, non-distributable portable entry-point fixture. Does not launch SFC.

Copies only critical game files into a fresh ignored fixture for read-only
preflight. This is NOT the release builder and cannot establish gameplay/dependency
closure or permission to distribute vendor files. No ZIP is produced.
"""
import datetime as dt
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/remix_runtime'))
from runtime_context import CONTEXT,CLIENT_SHA256,VERSION
from release_manifest import digest,SCHEMA,REQUIRED_ROLES,PROFILE_FILES
from copied_preferences import protected_ini_sha256
from inventory_dependencies import production_files
from game_profile import signature as dimension_signature
from runtime_candidate import COMMIT,HEADER_SHA
from package_layout import copy_python,copy_remix


def launcher_preflight(game, cwd):
    return subprocess.run([str(game/'SFCRemix/launcher.exe'),'--preflight'],
                          cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=180)


def check_profile_mismatches(game, fixture):
    """Exercise the packaged failure path in the freshly staged, minimal copy."""
    def snapshot():
        return {path.relative_to(game).as_posix(): digest(path)
                for path in game.rglob('*') if path.is_file()}

    original = snapshot()
    files = {name: (game/name).read_bytes()
             for name in ('DDraw.dll', 'dxgi.dll', 'sfc.ini', 'dgVoodoo.conf')}
    conflict = game/'d3d9.dll'
    if conflict.exists():
        raise ValueError('Mismatch fixture already contains a D3D9 proxy')
    wrong_dimensions, count = re.subn(
        rb'(?im)^(DesktopResolution[ \t]*=[ \t]*)([0-9]+x[0-9]+)',
        lambda match: match[1] + (b'1600x900' if match[2] != b'1600x900' else b'1280x720'),
        files['dgVoodoo.conf'],
    )
    if count != 1:
        raise ValueError('Cannot set a mismatched desktop resolution in the fixture')
    try:
        (game/'DDraw.dll').unlink()
        (game/'dxgi.dll').write_bytes(b'fixture wrong baseline')
        (game/'sfc.ini').write_bytes(files['sfc.ini'] + b'\r\n; fixture customized setting\r\n')
        (game/'dgVoodoo.conf').write_bytes(wrong_dimensions)
        conflict.write_bytes(b'fixture conflicting proxy')
        broken = snapshot()
        run = launcher_preflight(game, fixture)
        expected = (
            'Missing graphics file: DDraw.dll',
            'Unsupported graphics file: dxgi.dll',
            'resolution does not match sfc.ini',
            'Unrecognized proxy conflict: d3d9.dll',
            'No game or package files were changed.',
        )
        if run.returncode != 1 or any(message not in run.stdout for message in expected):
            raise ValueError('Packaged mismatch report failed\n' + run.stdout)
        if broken != snapshot() or any((game/'SFCRemix'/name).exists() for name in ('data', 'settings')):
            raise ValueError('Packaged mismatch check wrote to the fixture')
    finally:
        for name, raw in files.items():
            (game/name).write_bytes(raw)
        conflict.unlink(missing_ok=True)

    restored = launcher_preflight(game, fixture)
    if restored.returncode or 'READ_ONLY_PACKAGE_PREFLIGHT_PASS' not in restored.stdout or original != snapshot():
        raise ValueError('Restored fixture did not pass unchanged\n' + restored.stdout)
    return dict(profile_mismatch_test=True, exit_code=0, checker_exit_code=run.returncode,
                files_unchanged=True, restored_fixture_passed=True, console=run.stdout)


def stage_setup_inputs(fixture, game, package, roles, baseline):
    from qualify_graphics_adapter import compile_probe

    stage=package/'runtime/graphics'
    stage.mkdir(exist_ok=True)
    archive=ROOT/'artifacts/alpha/dependencies/dgVoodoo2_86_5-preserved.zip'
    if digest(archive)!='76b6893a0be81e3905a03f30f25202d6dc6128c3b8f7a21f2c33bcfabfa75ddf':
        raise ValueError('Unqualified dgVoodoo setup archive')
    with ZipFile(archive) as source:
        for name, role in (('DDraw.dll','setup_ddraw'),('D3DImm.dll','setup_d3dimm')):
            entry=next(item for item in source.infolist() if item.filename.lower().endswith('/x86/'+name.lower()))
            path=stage/name
            path.write_bytes(source.read(entry))
            if digest(path)!=baseline[name]:
                raise ValueError('Setup DLL differs from the qualified game profile: '+name)
            roles[role]=path.relative_to(package).as_posix()
    compiled=fixture/'setup-probes'
    compiled.mkdir()
    deps=ROOT/'artifacts/remix-runtime/deps'
    for name, arch, sdk, libraries, role in (
        ('graphics_adapter_probe',32,'reshade/include','dxgi.lib dxguid.lib user32.lib','setup_wrapper_probe'),
        ('shared_layout_probe',64,'candidate-1.6.1','d3d11.lib dxgi.lib user32.lib','setup_remix_probe'),
    ):
        source=compile_probe(compiled,arch,name,deps/sdk,libraries)
        path=stage/source.name
        shutil.copyfile(source,path)
        roles[role]=path.relative_to(package).as_posix()


GAME_FOLDERS = ('Game é space', 'Moved portable game é')


def remove_staged_game(fixture):
    for name in GAME_FOLDERS:
        game = fixture / name
        if game.is_symlink() or game.is_junction() or game.resolve().parent != fixture:
            raise ValueError(f'Refusing to clean an unexpected fixture path: {game}')
        if game.exists():
            shutil.rmtree(game)


def stage(*,functional=False,portable_cache=False,setup=False,keep_game=False):
    if CONTEXT.release:raise ValueError('This is a development-only fixture')
    if portable_cache and not functional:
        raise ValueError('Portable cache qualification requires the private functional fixture')
    if setup and not portable_cache:
        raise ValueError('Setup qualification requires the portable cache fixture')
    if keep_game and not functional:
        raise ValueError('--keep-game requires --functional')
    root = ROOT/'artifacts/alpha/preflight-fixtures'
    if root.resolve() != root:
        raise ValueError('Fixture root must be in its expected project location')
    fixture = root / dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
    fixture.mkdir(parents=True)
    complete = False
    try:
        stage_fixture(fixture, functional=functional, portable_cache=portable_cache,
                      setup=setup, keep_game=keep_game)
        complete = True
    finally:
        if not (complete and keep_game):
            remove_staged_game(fixture)


def stage_fixture(fixture, *, functional, portable_cache, setup, keep_game):
    game=fixture/GAME_FOLDERS[0];package=game/'SFCRemix';package.mkdir(parents=True)
    if functional:
        # Private gameplay checkout, never ZIP input. The tester game remains
        # outside SFCRemix, and gets independent copies rather than hard links.
        if not game.resolve().is_relative_to((ROOT/'artifacts/alpha/preflight-fixtures').resolve()):raise ValueError('Private game copy escaped fixture root')
        shutil.copytree(CONTEXT.game_root,game,dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns('SFCRemix','*.dmp','ReShade.log','*.sfc-broad-stage'))
    protected=('StarFleetOP.exe','DDraw.dll','D3DImm.dll','dxgi.dll','dgVoodoo.conf','ReShade.ini','sfc.ini')
    before={n:digest(CONTEXT.game_root/n) for n in protected}
    for name in protected:shutil.copyfile(CONTEXT.game_root/name,game/name)
    if portable_cache:
        from qualify_reshade_cache import candidate_profile
        original_reshade=(game/'ReShade.ini').read_bytes()
        (game/'ReShade.ini').write_bytes(candidate_profile(original_reshade))
    if functional:
        shutil.copyfile(ROOT/'src/launcher/SFCRemix-Launch.cmd',game/'SFCRemix-Launch.cmd')
    # This runtime was obtained from the identified upstream distribution,
    # never from Codex. Ignore compiled caches so -B imports create no mutable
    # writes outside data and immutable manifests remain stable across moves.
    copy_python(ROOT/'artifacts/alpha/python-3.12.14',package/'python')
    for name in production_files():
        target=package/'code'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
    shutil.copyfile(ROOT/'artifacts/alpha/launcher-bin/launcher.exe',package/'launcher.exe')
    shutil.copyfile(ROOT/'src/launcher/Troubleshoot.cmd',package/'Troubleshoot.cmd')
    roles=dict(coordinator='code/src/launcher/bootstrap.py',python='python/python.exe',launcher='launcher.exe',restore='launcher.exe',
               project_license='LICENSE',third_party_notices='FIXTURE-NOT-FOR-DISTRIBUTION.txt',troubleshooting_launcher='Troubleshoot.cmd')
    shutil.copyfile(ROOT/'LICENSE',package/'LICENSE')
    (package/roles['third_party_notices']).write_text('Private entry-point fixture only. Vendor notices/complete dependency closure still under review. Do not distribute this directory.')
    binaries={
        'return_launcher':'remix-runtime/return-bin/return_launcher.exe',
        'return_host':'remix-runtime/return-bin/return_host.exe',
        'return_addon':'remix-runtime/return-bin/SFCRemixReturn.dll',
        'startup_gate':'m1/bin/m1_gate.dll',
        'semantic_component':'remix-runtime/native-light-tests/m1_light_component.dll',
        'semantic_controller':'m1/bin/m1_controller.exe',
        'renderer':'remix-runtime/candidate-1.6.1-bin/d3d9_direct_host.exe',
        'output_receiver':'d3d9-proof/receiver-bin/output_receiver.exe',
        'job_guard':'remix-ingest/bin/bounded_job.exe',
        'mesh_checksum':'d3d9-proof/mesh-checksum/mesh_checksum.dll',
        'remix_runtime':'remix-runtime/deps/candidate-1.6.1/runtime/d3d9_x64.dll',
        'reshade_proxy':'remix-runtime/deps/reshade-full-6.7.1/extracted/ReShade32.dll',
    }
    for role,name in binaries.items():
        destination=package/'runtime'/name;destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'artifacts'/name,destination);roles[role]='runtime/'+name
    if functional:
        source=ROOT/'artifacts/remix-runtime/deps/candidate-1.6.1/runtime'
        destination=package/'runtime/remix-runtime/deps/candidate-1.6.1/runtime'
        copy_remix(source,destination)
        from prepare_notices import prepare as prepare_notices
        shutil.copytree(prepare_notices(),package/'notices')
        from prepare_reshade_payloads import BASELINE_ROLE, prepare as prepare_reshade_payloads
        baseline=next(item for item in prepare_reshade_payloads() if item.get('role')==BASELINE_ROLE)
        destination=package/baseline['target']
        destination.parent.mkdir(parents=True)
        shutil.copyfile(ROOT/baseline['source'],destination)
        if digest(destination)!=baseline['sha256']:
            raise ValueError('Staged standard ReShade DLL changed')
        roles[BASELINE_ROLE]=baseline['target']
    if setup:
        stage_setup_inputs(fixture,game,package,roles,before)
    for role,name in (('default_lights','lights.toml'),('default_rendering','rendering.toml')):
        destination=package/'defaults'/name;destination.parent.mkdir(exist_ok=True)
        shutil.copyfile(CONTEXT.setting(name),destination);roles[role]='defaults/'+name
    assert REQUIRED_ROLES<=roles.keys()
    files={p.relative_to(package).as_posix():dict(bytes=p.stat().st_size,sha256=digest(p)) for p in package.rglob('*') if p.is_file()}
    value=dict(schema=SCHEMA,version=VERSION,client_sha256=CLIENT_SHA256,platform='windows-x64',
               roles=roles,files=files,fixture_only=not functional,private_checkout=functional,
               remix=dict(release='1.6.1',source_commit=COMMIT,api_version=[0,6,5],header_sha256=HEADER_SHA),
               game_profile=dict(files={n:digest(game/n) for n in sorted(PROFILE_FILES)},
                                 sfc_protected_sha256=protected_ini_sha256((game/'sfc.ini').read_bytes()),
                                 dimension_profile=dimension_signature((game/'sfc.ini').read_bytes(),(game/'dgVoodoo.conf').read_bytes())))
    (package/'package.json').write_text(json.dumps(value,indent=2))
    results=[]
    for index in range(2):
        if index:
            moved=fixture/GAME_FOLDERS[1]
            if not moved.resolve().is_relative_to(fixture.resolve()):raise ValueError('Fixture move escaped its verified root')
            game.rename(moved);game=moved;package=game/'SFCRemix'
        run=launcher_preflight(game,fixture)
        results.append(dict(moved=bool(index),exit_code=run.returncode,console=run.stdout))
        if run.returncode:break
        if (package/'data').exists() or (package/'settings').exists():raise ValueError('Read-only preflight wrote mutable data')
    if not functional and all(result['exit_code']==0 for result in results):
        results.append(check_profile_mismatches(game,fixture))
    # Exercise the actual installed normal coordinator's non-executing preflight,
    # after explicit preparation in this disposable fixture. The old1.5.2 DLL,
    # test receipts and developer source tree are deliberately absent.
    code="""import os,sys
from pathlib import Path
p=Path(os.environ['SFC_RELEASE_ROOT'])
sys.path.insert(0,str(p/'code/src/launcher'))
import bootstrap
m=bootstrap.verify(bootstrap.CONTEXT)
bootstrap.prepare(bootstrap.CONTEXT,m)
sys.argv=['installed-preflight','--play-session','--native-insertion-policy','ExtraFrame','--native-all-ships','--break-models','--damage-textures']
from coordinator import main
main()
"""
    check=subprocess.run([str(package/'python/python.exe'),'-I','-B','-c',code],cwd=fixture,
                         env={**os.environ,'SFC_RELEASE_ROOT':str(package)},stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=180)
    results.append(dict(prepared_native_coordinator=True,exit_code=check.returncode,console=check.stdout))
    if portable_cache and all(result['exit_code']==0 for result in results):
        check=subprocess.run([str(package/'python/python.exe'),'-I','-B',
                              str(ROOT/'tools/release/qualify_reshade_cache.py'),str(package)],
                             input=original_reshade,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
        results.append(dict(portable_cache_profile=True,exit_code=check.returncode,
                            console=check.stdout.decode('utf-8',errors='replace')))
    after={n:digest(CONTEXT.game_root/n) for n in protected}
    record=dict(result='PORTABLE_READ_ONLY_PREFLIGHT_ONLY' if all(x['exit_code']==0 for x in results) else 'PARTIAL',
                no_sfc_launch=True,original_copy_unchanged=before==after,fixture_not_distributable=True,
                independent_upstream_python=True,toolkit_required=False,results=results,
                retained_game=keep_game and before==after and all(x['exit_code']==0 for x in results))
    if functional:
        record.update(not_for_distribution=True,no_gameplay_acceptance=True,
                      portable_cache=portable_cache,setup=setup)
    if record['retained_game']:
        record.update(private_functional_checkout=str(package),
                      launcher=str(game/'SFCRemix-Launch.cmd'),native_launcher=str(package/'launcher.exe'))
        (game/'PRIVATE-CHECKOUT-NOT-FOR-DISTRIBUTION.txt').write_text('Private functional checkout of uncommitted source. No game assets belong in a release ZIP. Vendor notice/packaging review and sponsor gameplay acceptance remain open. Do not distribute this directory.\n')
    (fixture/'result.json').write_text(json.dumps(record,indent=2))
    print(fixture);print(json.dumps(record,indent=2))
    if before!=after or any(x['exit_code'] for x in results):raise ValueError('Portable preflight fixture needs review')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--functional',action='store_true')
    parser.add_argument('--portable-cache',action='store_true',help='qualify a cache-only ReShade change in the private game copy')
    parser.add_argument('--setup',action='store_true',help='stage verified setup inputs in the private fixture')
    parser.add_argument('--keep-game',action='store_true',help='keep a successful functional copy for a separate checkout')
    args=parser.parse_args()
    stage(functional=args.functional,portable_cache=args.portable_cache,setup=args.setup,keep_game=args.keep_game)
