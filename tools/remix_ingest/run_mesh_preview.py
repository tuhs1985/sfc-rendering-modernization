"""One-click bounded preview of the accepted saved mesh; never launches SFC."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid
from run_remix_ingest import digest, write_json

ACCEPTED = Path('C:/Project/RemixJobs/20261015-231057Z-19b131ce')
USD_HASH = '59b9c57adad61bef4244f34b631b833bd6c34416791d3108ade0537a64592696'
ROOT = Path(__file__).resolve().parents[2]
PREVIEW_ENV = {'DXVK_GRAPHICS_PRESET_TYPE': '4', 'RTX_INTEGRATE_INDIRECT_MODE': '0'}
VIEWS = {'Angled': (1.4, 0.8, 1.4), 'Front': (1, 0, 0),
         'Side': (0, 0, 1), 'Above': (0, 1, 0)}
ABOVE_UP = (1, 0, 0)  # Sponsor identified +X as the captured ship's forward end.


def verify_input(job, textures=False):
    job = Path(job).resolve()
    source = job / 'output/ship.usda'
    if source.stat().st_size > 2*1024*1024 or (not textures and digest(source) != USD_HASH):
        raise ValueError('Preview requires the exact accepted mesh; no guessed replacement')
    result = json.loads((job/'result.json').read_text())
    corners = json.loads((job/'corner-comparison-numeric.json').read_text())
    if result.get('fixture') is not False or result.get('status') != 'GEOMETRY_INGESTED_PREVIEW_PENDING':
        raise ValueError('Not an accepted real ingestion result')
    expected = 452
    if textures:
        metadata = json.loads((job/'job-metadata.json').read_text())
        expected = metadata['expected_triangles']
        if metadata.get('textures') is not True or result.get('texture_preview_candidate') is not True or digest(source) != result.get('usd_sha256'):
            raise ValueError('Not a verified textured ingestion candidate')
    if corners.get('match') is not True or corners.get('expected_triangles') != expected or not 1 <= expected <= 512:
        raise ValueError('Corner comparison not qualified')
    return source


def prepare(job, toolkit, jobs, smoke=False, textures=False, fresh=False):
    source = None if fresh else verify_input(job, textures)
    toolkit, jobs = Path(toolkit).resolve(), Path(jobs).resolve()
    if any(c.isspace() for c in str(toolkit)+str(jobs)):
        raise ValueError('Toolkit and scratch roots must have no spaces')
    if toolkit == jobs or toolkit in jobs.parents or Path(job).resolve() in jobs.parents or jobs == Path(job).resolve():
        raise ValueError('Scratch must be separate from vendor and accepted evidence')
    if (toolkit/'VERSION').read_text().strip() != '1.6.0-dev+main.30229.3f23f80a.gl':
        raise ValueError('Toolkit revision changed; review required')
    work = jobs/('preview-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%SZ-')+uuid.uuid4().hex[:8])
    work.mkdir(parents=True, exist_ok=False)
    if fresh:
        source=work/'ship.usda'
        source.write_text('#usda 1.0\n(defaultPrim="ReferenceTarget"\n metersPerUnit=1\n upAxis="Y")\ndef Xform "ReferenceTarget" {}\n')
    else:shutil.copyfile(source, work/'ship.usda')
    dependencies = {}
    if textures and not fresh:
        total = 0
        for path in sorted(source.parent.rglob('*')):
            if path.is_symlink() or not path.resolve().is_relative_to(source.parent):
                raise ValueError('Unsafe preview dependency path')
            if not path.is_file() or path == source:
                continue
            total += path.stat().st_size
            if total > 128*1024*1024:
                raise ValueError('Preview dependencies exceed 128 MiB')
            relative = path.relative_to(source.parent)
            target = work/relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
            dependencies[str(relative)] = digest(path)
    here = Path(__file__).resolve().parent
    for name in ('sfc_mesh_preview.kit', 'kit_mesh_preview.py', 'preview_renderer.conf', 'preview_sampling_audit.py'):
        shutil.copyfile(here/name, work/name)
    config = {'work': work.as_posix(), 'asset': (work/'ship.usda').as_posix(),
              'source_sha256': digest(source), 'source': str(source), 'smoke': smoke,
              'expected_triangles': 0 if fresh else (json.loads((Path(job)/'job-metadata.json').read_text())['expected_triangles'] if textures else 452),
              'fresh_scene':fresh,
              'textures': textures, 'dependency_sha256': dependencies, 'ready_seconds': 120,
              'views': VIEWS, 'above_up': ABOVE_UP}
    write_json(work/'preview-config.json', config)
    command = [str(toolkit/'kit/kit.exe'), str(work/'sfc_mesh_preview.kit')]
    for folder in ('exts', 'extscache', 'kit/extscore'):
        command.extend(['--ext-folder', str(toolkit/folder)])
    command.extend(['--portable-root', str(work/'portable'), '--exec', str(work/'kit_mesh_preview.py')])
    if smoke:
        command.append('--no-window')
    write_json(work/'preview-launch.json', {'schema': 'sfc.remix.preview-launch.v1',
              'command': command, 'toolkit_version': (toolkit/'VERSION').read_text().strip(),
              'kit_sha256': digest(toolkit/'kit/kit.exe'),
              'scripts': {name: digest(here/name) for name in ('sfc_mesh_preview.kit', 'kit_mesh_preview.py', 'run_mesh_preview.py', 'preview_renderer.conf', 'preview_sampling_audit.py')},
              'process_environment': {**PREVIEW_ENV, 'DXVK_RTX_CONFIG_FILE': str(work/'preview_renderer.conf')},
              'limits': {'total_seconds': 180, 'view_seconds': 120, 'scratch_stop': 256*1024*1024,
                         'scratch_warning': 128*1024*1024, 'console_bytes': 8*1024*1024,
                         'png_count': 3 if smoke else 1, 'png_bytes_each': 8*1024*1024}})
    return work, source, command


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--job', type=Path, default=ACCEPTED)
    parser.add_argument('--toolkit', type=Path, default=Path('C:/Project/RTXRemix'))
    parser.add_argument('--jobs', type=Path, default=Path('C:/Project/RemixJobs'))
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--smoke', action='store_true', help='Bounded no-window rendering validation, then exit')
    parser.add_argument('--textures', action='store_true', help='Preview verified same-run textured ingestion; grey remains the default')
    parser.add_argument('--base-mip-only', action='store_true', help='Approved scratch-only diagnostic; requires textures and smoke')
    parser.add_argument('--sharper-mip', action='store_true', help='Scratch-only nativeMipBias=-1 candidate, preserving the full mip chain')
    parser.add_argument('--nearest-filter', action='store_true', help='Session-only material filtering diagnostic; requires textured smoke')
    parser.add_argument('--resident-textures', action='store_true', help='Offline textured preview full residency; retains all original mip chains')
    parser.add_argument('--provisional-lighting', action='store_true', help='Sponsor-authorized unverified lighting-mask reconstruction, offline only')
    parser.add_argument('--live-channel', help='Explicit session-only live connection; never enabled by default')
    parser.add_argument('--live-game-root', type=Path)
    parser.add_argument('--live-launch-record', type=Path)
    parser.add_argument('--game-camera',action='store_true',help='Live-only direct SFC camera; no fixed-camera fallback')
    parser.add_argument('--fresh-scene',action='store_true',help='Protocol3 empty scene; construct fresh received meshes, no imported job')
    parser.add_argument('--live-replay',action='store_true',help='Synthetic fresh-scene rehearsal, permits one diagnostic screenshot')
    parser.add_argument('--surface-diagnostic', choices=('left-handed', 'quarter-light', 'two-sided', 'emissive-surface'), help='Isolated smoke-only facing or synthetic-light test')
    args = parser.parse_args()
    try:
        if args.game_camera and not args.live_channel:raise ValueError('Game camera requires live channel')
        if args.fresh_scene and (not args.live_channel or not args.game_camera or args.provisional_lighting):
            raise ValueError('Fresh scene requires live game camera and no template lighting derivative')
        if args.live_replay and not args.fresh_scene:raise ValueError('Replay screenshot requires fresh-scene rehearsal')
        if args.live_channel:
            from live_bridge import NAME
            if not NAME.fullmatch(args.live_channel) or not args.live_game_root or not args.textures or not args.resident_textures or args.smoke or args.surface_diagnostic:
                raise ValueError('Live preview requires explicit channel/game root and resident textured nonsmoke mode')
        if args.surface_diagnostic and (not args.textures or not args.resident_textures or not args.smoke or args.provisional_lighting):
            raise ValueError('Surface diagnostic requires textured resident smoke without provisional emission')
        if args.provisional_lighting and (not args.textures or not args.resident_textures):
            raise ValueError('Provisional lighting requires explicit textures and full residency')
        if args.resident_textures and (args.base_mip_only or args.sharper_mip or args.nearest_filter or not args.textures):
            raise ValueError('Residency mode requires textures and no other sampling diagnostic')
        if args.nearest_filter and (args.base_mip_only or args.sharper_mip or not args.textures or not args.smoke):
            raise ValueError('Nearest-filter diagnostic requires textured smoke and no other sampling diagnostic')
        if args.sharper_mip and (args.base_mip_only or not args.textures or not args.smoke):
            raise ValueError('Sharper-mip candidate requires textured smoke and excludes base-only mode')
        if args.base_mip_only and not (args.textures and args.smoke):
            raise ValueError('Base-mip diagnostic requires explicit textured smoke mode')
        guard = ROOT/'artifacts/remix-ingest/bin/bounded_job.exe'
        if not args.prepare_only and not guard.is_file():
            raise ValueError('Build tools/remix_ingest/build_remix_job.ps1 first')
        work, source, command = prepare(args.job, args.toolkit, args.jobs, args.smoke, args.textures,args.fresh_scene)
        if args.live_channel:
            metadata={} if args.fresh_scene else json.loads((Path(args.job)/'job-metadata.json').read_text())
            config_path=work/'preview-config.json';config=json.loads(config_path.read_text())
            config['live_bridge']={'channel':args.live_channel,'game_root':str(args.live_game_root.resolve()),'game_camera':args.game_camera,
                                   'template_capture':metadata.get('capture')}
            config['ready_seconds']=280
            config['live_replay']=args.live_replay
            config_path.write_text(json.dumps(config,indent=2)+'\n')
            for name in ('live_bridge.py','kit_live_bridge.py','live_camera.py','live_scene.py','kit_live_scene.py','fresh_mesh_usd.py'):
                shutil.copyfile(Path(__file__).with_name(name),work/name)
            shutil.copyfile(ROOT/'tools/m1_component/analyze_live_camera.py',work/'analyze_live_camera.py')
            if args.live_launch_record:write_json(args.live_launch_record,{'work':str(work)})
        if args.surface_diagnostic:
            config_path = work/'preview-config.json'
            config = json.loads(config_path.read_text())
            config['surface_diagnostic'] = args.surface_diagnostic
            config_path.write_text(json.dumps(config, indent=2)+'\n')
        if args.nearest_filter:
            config_path = work/'preview-config.json'
            config = json.loads(config_path.read_text())
            config['nearest_filter_diagnostic'] = True
            config_path.write_text(json.dumps(config, indent=2)+'\n')
        if args.resident_textures:
            local = work/'preview_renderer.conf'
            before = digest(local)
            local.write_text(local.read_text()+'\n# Offline selected-mesh residency test, not a global policy\nrtx.texturemanager.neverDowngradeTextures = True\n')
            write_json(work/'texture-residency-test.json', {'requested_option': 'rtx.texturemanager.neverDowngradeTextures',
                       'requested_value': True, 'before_config_sha256': before, 'after_config_sha256': digest(local),
                       'textures_unchanged': True, 'gpu_residency_readback': 'unavailable'})
        if args.provisional_lighting:
            from provisional_lighting import prepare as prepare_lighting
            prepare_lighting(work, args.job)
            write_json(work/'provisional-lighting-tool.json', {'sha256': digest(Path(__file__).with_name('provisional_lighting.py'))})
        if args.base_mip_only:
            from base_mip_diagnostic import prepare as prepare_base_mip
            prepare_base_mip(work)
            write_json(work/'base-mip-tool.json', {'sha256': digest(Path(__file__).with_name('base_mip_diagnostic.py'))})
        if args.sharper_mip:
            local = work/'preview_renderer.conf'
            before = digest(local)
            local.write_text(local.read_text()+'\n# Explicit candidate test, not a new default\nrtx.nativeMipBias = -1\n')
            write_json(work/'mip-policy-test.json', {'requested_option': 'rtx.nativeMipBias', 'requested_value': -1,
                       'before_config_sha256': before, 'after_config_sha256': digest(local),
                       'textures_unchanged': True, 'effective_native_value_readback': 'unavailable'})
        expected_hash = digest(source)
        print(f'Preview evidence: {work}', flush=True)
        if args.prepare_only:
            return 0
        print('A SEPARATE window will show the saved ship, not the game. Use the view buttons.', flush=True)
        if args.provisional_lighting:
            print('PROVISIONAL lighting-mask reconstruction: active SFC path, color space and strength NOT VERIFIED.', flush=True)
        print(('Recovered primary textures; glow role still unproven.' if args.textures else 'Plain grey materials.')
              + ' Synthetic lights, unchanged faces. Close the preview when finished.', flush=True)
        print('Live workflow: five-minute total limit; ship hidden until fresh assets verify.' if args.live_channel else 'Automatically closes after two minutes of viewing (three-minute total limit).', flush=True)
        env = os.environ.copy()
        env.update(PREVIEW_ENV)
        env['DXVK_RTX_CONFIG_FILE'] = str(work/'preview_renderer.conf')
        env['SFC_MESH_PREVIEW_CONFIG'] = str(work/'preview-config.json')
        write_json(work/'guard.json', {'guard_sha256': digest(guard), 'python': sys.version})
        result = {'status': 'FAIL', 'source_unchanged': False}
        try:
            child = subprocess.run([str(guard), str(work), '300' if args.live_channel else '180', str(256*1024*1024),
                                    str(8*1024*1024), *command], env=env, timeout=320 if args.live_channel else 200, check=False)
            owned = json.loads((work/'job-result.json').read_text())
            ready = json.loads((work/'preview-ready.json').read_text())
            result.update(guard_exit=child.returncode, job=owned, ready=ready,
                          source_unchanged=digest(source)==expected_hash)
            if child.returncode or owned['stop_reason'] or owned['remaining_owned_processes']:
                raise ValueError('Preview job did not exit cleanly')
            if ready.get('status') != 'READY' or not result['source_unchanged']:
                raise ValueError('Preview readiness/source preservation not confirmed')
            result['status'] = 'SMOKE_RENDERED_VISUAL_REVIEW_REQUIRED' if args.smoke else 'PREVIEW_CLOSED_REVIEW_REQUIRED'
        except (OSError, ValueError, KeyError, subprocess.TimeoutExpired) as exc:
            result.update(error=str(exc), source_unchanged=digest(source)==expected_hash)
        write_json(work/'preview-result.json', result)
        print(json.dumps(result), flush=True)
        return 1 if result['status'] == 'FAIL' else 0
    except (OSError, ValueError, KeyError) as exc:
        print(f'Preview not started: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
