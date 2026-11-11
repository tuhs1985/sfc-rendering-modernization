"""Compare or select a verified dgVoodoo adapter on a synthetic DirectDraw 7 draw."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
ADAPTER_SETTING = re.compile(rb'(?im)^(Adapters[ \t]*=[ \t]*)(all|[1-9][0-9]*)(?=[ \t]*\r?$)')
LUID = r'-?\d+:\d+'


def wrapper_config(wrapper, setting):
    if not re.fullmatch(r'all|[1-9][0-9]*', setting):
        raise ValueError('Invalid dgVoodoo adapter setting')
    config, count = ADAPTER_SETTING.subn(lambda match: match[1]+setting.encode('ascii'), wrapper)
    if count != 1:
        raise ValueError('Expected exactly one dgVoodoo adapter setting')
    return config


def matching_setting(remix_luid, preferred, probe):
    """Try the current setting first. Select only a uniquely observed GPU match."""
    if not re.fullmatch(LUID, remix_luid):
        raise ValueError('Invalid Remix adapter identity')
    results = []

    def try_setting(setting):
        row = probe(setting)
        results.append(row)
        return wrapper_draw_passed(row) and row['actual_gpu_luids'] == [remix_luid]

    if try_setting(preferred):
        return preferred, results
    inventory = '\n'.join(results[0]['dxgi_inventory'])
    count = sum((int(flags) & 2) == 0 for flags in re.findall(r'\bflags=(\d+)\b', inventory))
    for setting in ('all', *(str(index) for index in range(1, min(count, 32)+1))):
        if setting != preferred and try_setting(setting):
            return setting, results
    return None, results


def wrapper_draw_passed(row):
    return (row['process_exit']==0 and row['directdraw_draw'] and row['actual_gpu_names']
            and row['actual_gpu_luids'] and row['d3d11_observed'])


def compile_probe(folder, architecture, name, include, libraries):
    vc = Path('C:/Program Files/Microsoft Visual Studio/18/Community/VC/Auxiliary/Build')/f'vcvars{architecture}.bat'
    source = ROOT/'tools/release'/f'{name}.cpp'
    command = (f'"{vc}" && cl /nologo /std:c++20 /EHsc /W4 /WX /O2 /MT /I"{include}" "{source}" '
               f'/Fe:{name}.exe /link /Brepro {libraries}')
    subprocess.run(f'"{os.environ["COMSPEC"]}" /d /s /c "{command}"', cwd=folder, check=True, timeout=120)
    return folder/f'{name}.exe'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', type=Path)
    parser.add_argument('--match', action='store_true', help='probe Remix and find a verified dgVoodoo setting')
    args = parser.parse_args()
    package = args.package.resolve()
    os.environ['SFC_RELEASE_ROOT'] = str(package)
    sys.path.insert(0, str(package/'code/src/launcher'))
    import bootstrap
    from release_manifest import verified_role, verify_game_profile

    context = bootstrap.CONTEXT
    manifest = bootstrap.verify(context)
    profile = verify_game_profile(context, manifest)
    wrapper = (context.game_root/'dgVoodoo.conf').read_bytes()
    settings = ADAPTER_SETTING.findall(wrapper)
    if len(settings) != 1:
        raise ValueError('Expected one adapter setting in the qualified profile')
    preferred = settings[0][1].decode('ascii').lower()
    folder = ROOT/'artifacts/alpha/adapter-probe'/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
    folder.mkdir(parents=True)
    sdk = ROOT/'artifacts/remix-runtime/deps/reshade/include'
    probe_executable = compile_probe(folder, 32, 'graphics_adapter_probe', sdk, 'dxgi.lib dxguid.lib user32.lib')
    env = {key: value for key, value in os.environ.items()
           if not key.upper().startswith(('SFC_', 'RESHADE_', 'DXVK_', 'RTX_'))}
    remix_luid = selected = None
    if args.match:
        sdk = ROOT/'artifacts/remix-runtime/deps/candidate-1.6.1'
        host = compile_probe(folder, 64, 'shared_layout_probe', sdk, 'd3d11.lib dxgi.lib user32.lib')
        runtime = verified_role(context, manifest, 'remix_runtime')
        log = folder/'remix-adapter.log'
        with log.open('wb') as stream:
            run = subprocess.run([str(host), str(runtime), '--adapter-only'], cwd=folder,
                                 env={**env, 'DXVK_ENABLE_RAYTRACING': '1', 'RTX_AUTOMATION_DISABLE_BLOCKING_DIALOG_BOXES': '1'},
                                 stdout=stream, stderr=subprocess.STDOUT,
                                 timeout=20, creationflags=subprocess.CREATE_NO_WINDOW)
        ids = re.findall(rf'^REMIX_D3D9_ADAPTER luid=({LUID})$', log.read_text(errors='replace'), re.M)
        if run.returncode or len(ids)!=1:
            raise ValueError('Could not verify the Remix adapter. See '+str(log))
        remix_luid = ids[0]

    deadline = time.monotonic()+30

    def probe(setting):
        name = 'all-adapters' if setting=='all' else f'ordinal-{setting}'
        case = folder/name
        case.mkdir()
        for dll in ('DDraw.dll', 'D3DImm.dll'):
            shutil.copyfile(context.game_root/dll, case/dll)
        shutil.copyfile(verified_role(context, manifest, 'reshade_proxy'), case/'dxgi.dll')
        (case/'dgVoodoo.conf').write_bytes(wrapper_config(wrapper, setting))
        (case/'ReShade.ini').write_text('[GENERAL]\nEffectSearchPaths=./no-effects\n[OVERLAY]\nTutorialProgress=4\n',
                                      encoding='ascii')
        executable = case/probe_executable.name
        shutil.copyfile(probe_executable, executable)
        remaining = deadline-time.monotonic()
        if remaining<=0:
            return dict(policy=name, process_exit=None, dxgi_inventory=[], error='Adapter probe deadline')
        try:
            run = subprocess.run([str(executable), str(case)], cwd=case, env=env,
                                 capture_output=True, timeout=min(remaining, 8),
                                 creationflags=subprocess.CREATE_NO_WINDOW)
        except subprocess.TimeoutExpired:
            return dict(policy=name, process_exit=None, dxgi_inventory=[], error='Adapter probe timed out')
        log_path = case/'ReShade.log'
        log = log_path.read_text(errors='replace') if log_path.is_file() else ''
        stdout = run.stdout.decode(errors='replace')
        stderr = run.stderr.decode(errors='replace')
        adapters = sorted(set(re.findall(r'Running on (.+?)(?: Driver |\r?\n)', log)))
        return dict(policy=name, process_exit=run.returncode, actual_gpu_names=adapters,
                    actual_gpu_luids=sorted(set(re.findall(rf'^WRAPPER_D3D11 luid=({LUID}) ', stdout, re.M))),
                    dxgi_inventory=[line for line in stdout.splitlines() if line.startswith('DXGI ')],
                    directdraw_draw='DIRECTDRAW_ADAPTER_PROBE_PASS' in stdout,
                    d3d11_observed='D3D11CreateDevice' in log, stdout=stdout, stderr=stderr)

    if args.match:
        selected, results = matching_setting(remix_luid, preferred, probe)
        if selected:
            (folder/'matched-dgVoodoo.conf').write_bytes(wrapper_config(wrapper, selected))
        result = 'ADAPTER_MATCH_VERIFIED' if selected else 'NO_VERIFIED_ADAPTER_MATCH'
    else:
        results = [probe(setting) for setting in ('1', 'all')]
        result = 'WRAPPER_ADAPTER_PROBE_PASS' if all(map(wrapper_draw_passed, results)) else 'PARTIAL'
    report = dict(result=result, remix_luid=remix_luid, selected_setting=selected,
                  game_launched=False, settings_changed=False, qualified_wrapper_hashes=profile['files'],
                  scope='Standalone native adapter comparison. Hybrid and gameplay require separate qualification.',
                  cases=results)
    (folder/'result.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(folder)
    print(json.dumps(report, indent=2))
    return 0 if result in ('WRAPPER_ADAPTER_PROBE_PASS', 'ADAPTER_MATCH_VERIFIED') else 1


if __name__ == '__main__':
    raise SystemExit(main())
