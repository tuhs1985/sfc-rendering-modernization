"""Match the actual Remix and dgVoodoo devices before changing a game copy."""
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

from game_profile import canonical

ADAPTER = (b'general', b'adapters')
LUID = r'-?\d+:\d+'


def wrapper_config(wrapper, setting):
    if not re.fullmatch(r'all|[1-9][0-9]?', setting):
        raise ValueError('Invalid dgVoodoo adapter setting')
    return canonical(wrapper, {ADAPTER: setting.encode('ascii')})[0]


def current_setting(wrapper):
    setting = canonical(wrapper, {ADAPTER: b'all'})[1][ADAPTER].decode('ascii').lower()
    if not re.fullmatch(r'all|[1-9][0-9]?', setting):
        raise ValueError('Invalid dgVoodoo adapter setting')
    return setting


def matching_setting(remix_luid, preferred, probe):
    """Try the existing setting first. Require exactly one observed GPU."""
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


def probe_environment():
    return {key: value for key, value in os.environ.items()
            if not key.upper().startswith(('SFC_', 'RESHADE_', 'DXVK_', 'RTX_'))}


def remix_adapter(host, runtime, folder, env):
    log = folder/'remix-adapter.log'
    with log.open('wb') as stream:
        run = subprocess.run([str(host), str(runtime), '--adapter-only'], cwd=folder,
                             env={**env, 'DXVK_ENABLE_RAYTRACING': '1',
                                  'RTX_AUTOMATION_DISABLE_BLOCKING_DIALOG_BOXES': '1'},
                             stdout=stream, stderr=subprocess.STDOUT,
                             timeout=20, creationflags=subprocess.CREATE_NO_WINDOW)
    ids = re.findall(rf'^REMIX_D3D9_ADAPTER luid=({LUID})$', log.read_text(errors='replace'), re.M)
    if run.returncode or len(ids)!=1:
        raise ValueError('Could not verify the Remix GPU.')
    return ids[0]


def wrapper_adapter(setting, wrapper, folder, probe_executable, libraries, env, deadline):
    name = 'all-adapters' if setting=='all' else f'ordinal-{setting}'
    remaining = deadline-time.monotonic()
    if remaining<=0:
        return dict(policy=name, process_exit=None, dxgi_inventory=[], error='Adapter probe deadline')
    case = folder/name
    case.mkdir()
    for target, source in libraries.items():
        shutil.copyfile(source, case/target)
    (case/'dgVoodoo.conf').write_bytes(wrapper_config(wrapper, setting))
    (case/'ReShade.ini').write_text('[GENERAL]\nEffectSearchPaths=./no-effects\n[OVERLAY]\nTutorialProgress=4\n',
                                  encoding='ascii')
    executable = case/probe_executable.name
    shutil.copyfile(probe_executable, executable)
    try:
        run = subprocess.run([str(executable), str(case)], cwd=case, env=env,
                             capture_output=True, timeout=min(remaining, 8),
                             creationflags=subprocess.CREATE_NO_WINDOW)
    except subprocess.TimeoutExpired:
        return dict(policy=name, process_exit=None, dxgi_inventory=[], error='Adapter probe timed out')
    log_path = case/'ReShade.log'
    log = log_path.read_text(errors='replace') if log_path.is_file() else ''
    stdout = run.stdout.decode(errors='replace')
    return dict(policy=name, process_exit=run.returncode,
                actual_gpu_names=sorted(set(re.findall(r'Running on (.+?)(?: Driver |\r?\n)', log))),
                actual_gpu_luids=sorted(set(re.findall(rf'^WRAPPER_D3D11 luid=({LUID}) ', stdout, re.M))),
                dxgi_inventory=[line for line in stdout.splitlines() if line.startswith('DXGI ')],
                directdraw_draw='DIRECTDRAW_ADAPTER_PROBE_PASS' in stdout,
                d3d11_observed='D3D11CreateDevice' in log,
                stdout=stdout, stderr=run.stderr.decode(errors='replace'))


def choose(context, manifest, wrapper, preferred):
    from release_manifest import contained, verified_role

    def role(name):
        return verified_role(context, manifest, name)

    folder = contained(context.package_root, 'data/tmp/gpu-setup')
    folder.mkdir(parents=True, exist_ok=True)
    libraries = {'DDraw.dll': role('setup_ddraw'), 'D3DImm.dll': role('setup_d3dimm'),
                 'dxgi.dll': role('reshade_proxy')}
    env = probe_environment()
    def clear_probe_files():
        root = folder.resolve()
        for path in folder.rglob('*'):
            if path.is_symlink() or path.is_junction() or not path.resolve().is_relative_to(root):
                raise ValueError('Linked graphics probe data')
        for path in folder.iterdir():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()

    # Keep one empty working directory. The driver can hold the directory
    # itself after the helper exits. The launcher lock serializes its reuse.
    clear_probe_files()
    try:
        try:
            luid = remix_adapter(role('setup_remix_probe'), role('remix_runtime'), folder, env)
        except subprocess.TimeoutExpired as exc:
            raise ValueError('Remix GPU check timed out. Try again with SFC closed.') from exc
        deadline = time.monotonic()+30
        setting, results = matching_setting(luid, preferred, lambda value: wrapper_adapter(
            value, wrapper, folder, role('setup_wrapper_probe'), libraries, env, deadline))
    finally:
        # Retry transient file sharing errors without retaining probe output.
        limit = time.monotonic()+2
        while True:
            try:
                clear_probe_files()
                break
            except PermissionError as exc:
                if exc.winerror!=32 or time.monotonic()>=limit:
                    raise
                time.sleep(.05)
    if setting is None:
        observed = sorted({name for row in results for name in row.get('actual_gpu_luids', [])})
        raise ValueError(f'No matching graphics device. Remix GPU {luid}. Game wrapper GPUs: '
                         + (', '.join(observed) or 'none detected'))
    return wrapper_config(wrapper, setting), luid
