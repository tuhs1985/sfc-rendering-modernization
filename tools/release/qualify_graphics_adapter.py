"""Compare dgVoodoo adapter policies on a synthetic DirectDraw 7 draw."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', type=Path)
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
    broadened, count = re.subn(rb'(?im)^(Adapters[ \t]*=[ \t]*)1(?=\r?$)',
                                lambda match: match[1]+b'all', wrapper)
    if count != 1:
        raise ValueError('Expected one Adapters=1 setting in the qualified profile')
    folder = ROOT/'artifacts/alpha/adapter-probe'/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
    folder.mkdir(parents=True)
    vc = Path('C:/Program Files/Microsoft Visual Studio/18/Community/VC/Auxiliary/Build/vcvars32.bat')
    source = ROOT/'tools/release/graphics_adapter_probe.cpp'
    sdk = ROOT/'artifacts/remix-runtime/deps/reshade/include'
    command = (f'"{vc}" && cl /nologo /std:c++20 /EHsc /W4 /WX /O2 /MT /I"{sdk}" "{source}" '
               '/Fe:graphics_adapter_probe.exe /link /Brepro dxgi.lib dxguid.lib user32.lib')
    subprocess.run(f'"{os.environ["COMSPEC"]}" /d /s /c "{command}"', cwd=folder, check=True, timeout=120)
    results = []
    env = {key: value for key, value in os.environ.items() if not key.startswith(('SFC_', 'RESHADE_'))}
    for name, config in (('ordinal-1', wrapper), ('all-adapters', broadened)):
        case = folder/name
        case.mkdir()
        for dll in ('DDraw.dll', 'D3DImm.dll'):
            shutil.copyfile(context.game_root/dll, case/dll)
        shutil.copyfile(verified_role(context, manifest, 'reshade_proxy'), case/'dxgi.dll')
        (case/'dgVoodoo.conf').write_bytes(config)
        (case/'ReShade.ini').write_text('[GENERAL]\nEffectSearchPaths=./no-effects\n[OVERLAY]\nTutorialProgress=4\n',
                                      encoding='ascii')
        executable = case/'graphics_adapter_probe.exe'
        shutil.copyfile(folder/executable.name, executable)
        run = subprocess.run([str(executable), str(case)], cwd=case, env=env,
                             capture_output=True, timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
        log_path = case/'ReShade.log'
        log = log_path.read_text(errors='replace') if log_path.is_file() else ''
        stdout = run.stdout.decode(errors='replace')
        stderr = run.stderr.decode(errors='replace')
        adapters = sorted(set(re.findall(r'Running on (.+?)(?: Driver |\r?\n)', log)))
        results.append(dict(policy=name, process_exit=run.returncode, actual_gpu_names=adapters,
                            actual_gpu_luids=sorted(set(re.findall(r'^WRAPPER_D3D11 luid=([^ ]+)', stdout, re.M))),
                            dxgi_inventory=[line for line in stdout.splitlines() if line.startswith('DXGI ')],
                            directdraw_draw='DIRECTDRAW_ADAPTER_PROBE_PASS' in stdout,
                            d3d11_observed='D3D11CreateDevice' in log, stdout=stdout, stderr=stderr))
    passed = all(row['process_exit']==0 and row['directdraw_draw'] and row['actual_gpu_names']
                 and row['actual_gpu_luids'] and row['d3d11_observed'] for row in results)
    report = dict(result='WRAPPER_ADAPTER_PROBE_PASS' if passed else 'PARTIAL',
                  game_launched=False, settings_changed=False, qualified_wrapper_hashes=profile['files'],
                  scope='Standalone native adapter comparison. Hybrid and gameplay require separate qualification.',
                  cases=results)
    (folder/'result.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(folder)
    print(json.dumps(report, indent=2))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
