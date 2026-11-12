"""Compare or select a verified dgVoodoo adapter on a synthetic DirectDraw 7 draw."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/remix_runtime'))
sys.path.insert(0, str(ROOT/'src/runtime'))
from setup_adapter import (current_setting, matching_setting, probe_environment,
                           remix_adapter, wrapper_adapter, wrapper_config, wrapper_draw_passed)


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
    preferred = current_setting(wrapper)
    folder = ROOT/'artifacts/alpha/adapter-probe'/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
    folder.mkdir(parents=True)
    sdk = ROOT/'artifacts/remix-runtime/deps/reshade/include'
    probe_executable = compile_probe(folder, 32, 'graphics_adapter_probe', sdk, 'dxgi.lib dxguid.lib user32.lib')
    env = probe_environment()
    remix_luid = selected = None
    if args.match:
        sdk = ROOT/'artifacts/remix-runtime/deps/candidate-1.6.1'
        host = compile_probe(folder, 64, 'shared_layout_probe', sdk, 'd3d11.lib dxgi.lib user32.lib')
        remix_luid = remix_adapter(host, verified_role(context, manifest, 'remix_runtime'), folder, env)

    deadline = time.monotonic()+30
    libraries = {name: context.game_root/name for name in ('DDraw.dll', 'D3DImm.dll')}
    libraries['dxgi.dll'] = verified_role(context, manifest, 'reshade_proxy')

    def probe(setting):
        return wrapper_adapter(setting, wrapper, folder, probe_executable, libraries, env, deadline)

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
