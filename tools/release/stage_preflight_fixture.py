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
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/remix_runtime'))
from runtime_context import CONTEXT,CLIENT_SHA256,VERSION
from release_manifest import digest,SCHEMA,REQUIRED_ROLES
from copied_preferences import protected_ini_sha256
from inventory_dependencies import production_files
from game_profile import signature as dimension_signature
from runtime_candidate import COMMIT,HEADER_SHA
from package_layout import copy_python,copy_remix


def stage(*,functional=False):
    if CONTEXT.release:raise ValueError('This is a development-only fixture')
    fixture=ROOT/'artifacts/alpha/preflight-fixtures'/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
    game=fixture/'Game é space';package=game/'SFCRemix';package.mkdir(parents=True)
    if functional:
        # Private gameplay checkout, never ZIP input. The tester game remains
        # outside SFCRemix, and gets independent copies rather than hard links.
        if not game.resolve().is_relative_to((ROOT/'artifacts/alpha/preflight-fixtures').resolve()):raise ValueError('Private game copy escaped fixture root')
        shutil.copytree(CONTEXT.game_root,game,dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns('SFCRemix','*.dmp','ReShade.log','*.sfc-broad-stage'))
    protected=('StarFleetOP.exe','DDraw.dll','D3DImm.dll','dxgi.dll','dgVoodoo.conf','ReShade.ini','sfc.ini')
    before={n:digest(CONTEXT.game_root/n) for n in protected}
    for name in protected:shutil.copyfile(CONTEXT.game_root/name,game/name)
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
    for role,name in (('default_lights','lights.toml'),('default_rendering','rendering.toml')):
        destination=package/'defaults'/name;destination.parent.mkdir(exist_ok=True)
        shutil.copyfile(CONTEXT.setting(name),destination);roles[role]='defaults/'+name
    assert REQUIRED_ROLES<=roles.keys()
    files={p.relative_to(package).as_posix():dict(bytes=p.stat().st_size,sha256=digest(p)) for p in package.rglob('*') if p.is_file()}
    value=dict(schema=SCHEMA,version=VERSION,client_sha256=CLIENT_SHA256,platform='windows-x64',
               roles=roles,files=files,fixture_only=not functional,private_checkout=functional,
               remix=dict(release='1.6.1',source_commit=COMMIT,api_version=[0,6,5],header_sha256=HEADER_SHA),
               game_profile=dict(files={n:before[n] for n in protected if n not in ('StarFleetOP.exe','sfc.ini')},
                                 sfc_protected_sha256=protected_ini_sha256((game/'sfc.ini').read_bytes()),
                                 dimension_profile=dimension_signature((game/'sfc.ini').read_bytes(),(game/'dgVoodoo.conf').read_bytes())))
    (package/'package.json').write_text(json.dumps(value,indent=2))
    results=[]
    for index in range(2):
        if index:
            moved=fixture/'Moved portable game é'
            if not moved.resolve().is_relative_to(fixture.resolve()):raise ValueError('Fixture move escaped its verified root')
            game.rename(moved);game=moved;package=game/'SFCRemix'
        run=subprocess.run([str(package/'launcher.exe'),'--preflight'],
                           cwd=fixture,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=180)
        results.append(dict(moved=bool(index),exit_code=run.returncode,console=run.stdout))
        if run.returncode:break
        if (package/'data').exists() or (package/'settings').exists():raise ValueError('Read-only preflight wrote mutable data')
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
from run_return_game import main
main()
"""
    check=subprocess.run([str(package/'python/python.exe'),'-I','-B','-c',code],cwd=fixture,
                         env={**os.environ,'SFC_RELEASE_ROOT':str(package)},stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=180)
    results.append(dict(prepared_native_coordinator=True,exit_code=check.returncode,console=check.stdout))
    after={n:digest(CONTEXT.game_root/n) for n in protected}
    record=dict(result='PORTABLE_READ_ONLY_PREFLIGHT_ONLY' if all(x['exit_code']==0 for x in results) else 'PARTIAL',
                no_sfc_launch=True,original_copy_unchanged=before==after,fixture_not_distributable=True,
                independent_upstream_python=True,toolkit_required=False,results=results)
    if functional:
        record.update(private_functional_checkout=str(package),not_for_distribution=True,
                      launcher=str(package/'launcher.exe'),no_gameplay_acceptance=True)
        (game/'PRIVATE-CHECKOUT-NOT-FOR-DISTRIBUTION.txt').write_text('Private functional checkout of uncommitted source. No game assets belong in a release ZIP. Vendor notice/packaging review and sponsor gameplay acceptance remain open. Do not distribute this directory.\n')
    (fixture/'result.json').write_text(json.dumps(record,indent=2))
    print(fixture);print(json.dumps(record,indent=2))
    if before!=after or any(x['exit_code'] for x in results):raise ValueError('Portable preflight fixture needs review')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--functional',action='store_true')
    stage(functional=parser.parse_args().functional)
