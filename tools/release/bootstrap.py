"""Installed-package entry point. Never builds, downloads, or searches a dev tree."""
import argparse
import json
import os
from pathlib import Path
import sys
import subprocess
from contextlib import redirect_stdout,redirect_stderr

CODE = Path(__file__).resolve().parents[2]
for directory in ('release', 'remix_runtime', 'd3d9_proof', 'scene_bridge', 'remix_ingest', 'm1_component'):
    sys.path.insert(0, str(CODE / 'tools' / directory))
from runtime_context import CONTEXT
from release_manifest import contained, verify, verify_game_profile, seed_settings
from release_manifest import verified_role,digest
from session_recording import finish


def check_native_launcher(context,manifest):
    launcher=verified_role(context,manifest,'return_launcher')
    addon=verified_role(context,manifest,'return_addon')
    command=[str(launcher),'--check-game',str(context.game_root/'StarFleetOP.exe'),str(addon),
             manifest['client_sha256'],digest(addon).upper()]
    result=subprocess.run(command,cwd=context.game_root,env={**os.environ,**context.child_environment()},
                          capture_output=True,text=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode or 'LAUNCH_PREFLIGHT_PASS no_process_created=1' not in result.stdout:
        raise ValueError('Native launcher preflight failed: '+(result.stdout+result.stderr).strip())


def check_scene_profiles(context,manifest):
    """Exercise the non-Python startup inputs before launching or switching files."""
    from multi_scene import camera_offset
    from owner_selection import selected_model
    for role,name,parse in (
        ('scene_placement','multi_ship.toml',camera_offset),
        ('owner_selection','offset_ship.toml',selected_model),
    ):
        path=verified_role(context,manifest,role)
        if path != context.code_root/'tools/d3d9_proof'/name:
            raise ValueError('Unexpected installed scene profile: '+role)
        parse(path.read_bytes())


def prepare(context, manifest):
    """Explicit first-launch writes only after package/game/profile validation."""
    seed_settings(context, manifest)
    for name in ('runs', 'baseline', 'cache', 'tmp'):
        contained(context.package_root, 'data/' + name).mkdir(parents=True, exist_ok=True)
    baseline = context.artifact('remix-runtime/test-install/sfc-baseline.ini')
    if not baseline.exists():
        with baseline.open('xb') as stream:
            stream.write((context.game_root / 'sfc.ini').read_bytes())
    os.environ['TEMP'] = str(context.data_root / 'tmp')
    os.environ['TMP'] = str(context.data_root / 'tmp')
    # Child processes inherit the explicit package context and application-local
    # runtime. No dependency comes from the developer user's PATH or home.
    os.environ.update(context.child_environment())


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--preflight', action='store_true')
    mode.add_argument('--restore', action='store_true')
    mode.add_argument('--troubleshoot', action='store_true')
    args = parser.parse_args()
    if not CONTEXT.release or CONTEXT.code_root != CODE:
        raise ValueError('Use the launcher from the extracted SFCRemix package')
    manifest = verify(CONTEXT)
    check_scene_profiles(CONTEXT,manifest)
    if manifest.get('fixture_only') and not args.preflight:
        raise ValueError('This private preflight fixture cannot launch SFC or restore a real installation')
    from windows_processes import game_running
    if not args.preflight and game_running():
        raise ValueError('Exit SFC normally before starting or restoring this copy')
    from recover_broad_session import recover_pending
    if args.restore:
        recovered = recover_pending(game_running)
        verify_game_profile(CONTEXT, manifest)
        finish(CONTEXT,game_running)
        print('Graphics restored.' if recovered else 'No interrupted graphics transaction to restore.')
        return
    if not args.preflight:
        recovered = recover_pending(game_running)
        if recovered:
            print('Previous session restored.')
        finish(CONTEXT,game_running)
    verify_game_profile(CONTEXT, manifest)
    check_native_launcher(CONTEXT,manifest)
    if args.preflight:
        print(json.dumps(dict(result='READ_ONLY_PACKAGE_PREFLIGHT_PASS', version=manifest['version'],
                              game=str(CONTEXT.game_root), files=len(manifest['files']))))
        return
    prepare(CONTEXT, manifest)
    os.environ['SFC_RELEASE_RECORDING']='minimal' if args.troubleshoot else 'off'
    os.environ['SFC_PLAY_SESSION']='1'
    # Reuse the current native coordinator, source tracking, retained meshes,
    # materials and graphics transaction. No separate release renderer.
    sys.argv = [str(CODE / 'tools/remix_runtime/run_return_game.py'), '--execute',
                '--play-session', '--native-insertion-policy', 'ExtraFrame',
                '--native-all-ships', '--break-models', '--damage-textures']
    from run_return_game import main as play
    print('Starting SFC. Exit the game normally when finished.',flush=True)
    print('Troubleshooting on: keeps up to 5 short reports, 320 KiB total.' if args.troubleshoot
          else 'Troubleshooting off. No run history will be saved.',flush=True)
    failed=None
    try:
        with open(os.devnull,'w') as sink,redirect_stdout(sink),redirect_stderr(sink):
            play()
    except Exception as exc:
        failed=exc
    finally:
        # Restoration must be verified before deleting any recovery/working data.
        if not game_running():
            verify_game_profile(CONTEXT,manifest)
            finish(CONTEXT,game_running)
    if failed:
        print('SFCRemix stopped: '+str(failed).split(';')[0][:400],flush=True)
        if game_running():print('Close SFC normally, then launch again to restore its files.')
        elif args.troubleshoot:print('A short report is in SFCRemix/data/troubleshooting.')
        else:print('Use Troubleshoot.cmd if you want to save a short report.')
        raise SystemExit(1)
    print('SFC closed. Cleanup complete.',flush=True)


if __name__ == '__main__':
    try:main()
    except Exception as exc:
        print('SFCRemix could not start: '+str(exc)[:300],flush=True)
        raise SystemExit(1)
