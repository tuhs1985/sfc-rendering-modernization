"""Prepare or execute one isolated, bounded Toolkit ingestion; never launches SFC."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'm1_component'))
from analyze_mesh_export import analyze
from export_mesh_obj import export_obj

SCHEMA = 'exts/lightspeed.trex.app.resources/data/validation_schema/model_ingestion.json'
SCHEMA_HASH = '1860e98cfa28a3d0d0686a96e2ddafab92cc9b84bcdb29b29783028cd910c878'
CLIENT_HASH = '4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    data = (json.dumps(value, indent=2, allow_nan=False) + '\n').encode()
    if len(data) > 65536:
        raise ValueError('Job metadata exceeds 64 KiB')
    with Path(path).open('xb') as stream:
        stream.write(data)


def configure_schema(template, obj, output):
    schema = json.loads(json.dumps(template))
    if schema['context_plugin']['name'] != 'AssetImporter':
        raise ValueError('Unexpected vendor schema context')
    context = schema['context_plugin']['data']
    context.update(input_files=[Path(obj).as_posix()], output_directory=Path(output).as_posix(),
                   output_usd_extension='usda', allow_empty_input_files_list=False)
    return schema


def prepare(capture, toolkit, jobs, fixture=False, textures=False):
    capture, toolkit, jobs = (Path(p).resolve() for p in (capture, toolkit, jobs))
    # Vendor --exec/CLI schema parsing is space-sensitive. Separate short scratch
    # root also avoids writing generated metadata alongside original evidence.
    if any(c.isspace() for c in str(jobs)) or any(c.isspace() for c in str(toolkit)):
        raise ValueError('Use short Toolkit/jobs paths without spaces')
    if digest(toolkit / SCHEMA) != SCHEMA_HASH:
        raise ValueError('Vendor schema revision changed; review before proceeding')
    if 'version = "1.6.0-dev"' not in (toolkit / 'apps/lightspeed.app.trex.kit').read_text():
        raise ValueError('Unexpected Toolkit version')
    packet, receipt = capture / 'MESH-EXPORT-001.bin', capture / 'MESH-EXPORT-001-receipt.json'
    analysis = analyze(packet, receipt)
    if not fixture:
        result = json.loads((capture / 'run-result.json').read_text(encoding='utf-8-sig'))
        if result.get('normal_exit_observed') is not True or result.get('client_unchanged') is not True or result.get('client_sha256_after') != CLIENT_HASH:
            raise ValueError('Capture exit/client baseline not verified')
        if result.get('mesh_export_pipeline_failed') or result.get('mesh_packet_validation_failed'):
            raise ValueError('Capture mesh pipeline reported failure')
    work = jobs / (datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%SZ-') + uuid.uuid4().hex[:8])
    work.mkdir(parents=True, exist_ok=False)
    source, output = work / 'input', work / 'output'
    source.mkdir();output.mkdir()
    shutil.copyfile(packet, source / packet.name);shutil.copyfile(receipt, source / receipt.name)
    export_obj(source / packet.name, source / 'ship.obj', source / receipt.name)
    if textures:
        from export_mesh_textures import read_bounded, LIMIT
        derivative = capture/'textured'
        associations = json.loads(read_bounded(derivative/'association-manifest.json', 512*1024))
        if associations.get('primary_images_ready') is not True or associations['packet_sha256'] != analysis['packet_sha256']:
            raise ValueError('Textured derivative not qualified for this packet')
        if len(associations['images']) > 10 or associations['image_bytes'] > LIMIT:
            raise ValueError('Textured derivative exceeds image envelope')
        for name, expected in (('ship.obj', associations['obj_sha256']), ('ship.mtl', associations['mtl_sha256'])):
            if digest(derivative/name) != expected:
                raise ValueError('Textured derivative changed')
            if name == 'ship.obj':
                fields = lambda p: [s for s in p.read_text().splitlines() if s.startswith(('v ', 'vt ', 'vn ', 'f ', 'g ', 'usemtl '))]
                if fields(derivative/name) != fields(source/name):
                    raise ValueError('Textured derivative changed geometry/UVs/groups')
            shutil.copyfile(derivative/name, source/name)
        total = 0
        for image in associations['images']:
            name = image['derived']
            if Path(name).name != name or not name.endswith('.png') or not 1 <= image['width'] <= 4096 or not 1 <= image['height'] <= 4096:
                raise ValueError('Unsafe derived image path/dimensions')
            total += (derivative/name).stat().st_size
            if total > LIMIT or digest(derivative/name) != image['derived_sha256']:
                raise ValueError('Derived image limit/hash failure')
            shutil.copyfile(derivative/name, source/name)
        shutil.copyfile(derivative/'association-manifest.json', source/'association-manifest.json')
    schema = configure_schema(json.loads((toolkit / SCHEMA).read_text()), source / 'ship.obj', output)
    write_json(work / 'schema.json', schema)
    script = Path(__file__).with_name('kit_ingest.py')
    shutil.copyfile(script, work / 'kit_ingest.py')
    config = {'schema': (work / 'schema.json').as_posix(), 'work': work.as_posix(),
              'output': output.as_posix(), 'fixture': fixture}
    write_json(work / 'config.json', config)
    command = [str(toolkit / 'kit/kit.exe'),
               str(toolkit / 'exts/omni.flux.validator.mass.core/apps/omni.flux.app.validator.mass_cli.kit'),
               '--merge-config=' + str(toolkit / 'apps/lightspeed.app.trex.validation_cli.kit'),
               '--/app/tokens/app=' + str(toolkit / 'apps'), '--no-window',
               '--portable-root', str(work / 'portable'),
               '--/app/settings/persistent=false', '--/app/settings/loadUserConfig=false',
               '--/app/extensions/registryEnabled=false']
    # merge-config applies settings, not the merged app's extension dependency
    # startup. Explicitly enable its declared plugins, as vendor CLI's -e permits.
    for extension in ('lightspeed.trex.app.resources', 'omni.flux.validator.plugin.check.usd',
                      'omni.flux.validator.plugin.context.usd_stage',
                      'omni.flux.validator.plugin.resultor.file', 'omni.flux.validator.plugin.selector.usd'):
        command.extend(['--enable', extension])
    command.extend(['--exec', str(work / 'kit_ingest.py')])
    metadata = {'schema': 'sfc.remix.job.v1', 'fixture': fixture, 'textures': textures, 'capture': str(capture),
                'packet_sha256': analysis['packet_sha256'], 'toolkit': str(toolkit),
                'vendor_schema_sha256': digest(toolkit / SCHEMA), 'script_sha256': digest(script),
                'runner_sha256': digest(__file__), 'kit_executable_sha256': digest(toolkit / 'kit/kit.exe'),
                'toolkit_version': (toolkit / 'VERSION').read_text().strip(),
                'command': command, 'limits': {'wall_seconds': 180, 'conversion_seconds': 120,
                                               'scratch_warning': 128*1024*1024, 'scratch_stop': 256*1024*1024,
                                               'console_bytes': 8*1024*1024},
                'expected_triangles': analysis['polygons'], 'owner_epoch': analysis['owner_epoch']}
    write_json(work / 'job-metadata.json', metadata)
    return work, metadata


def cyclic_triangle(vertices):
    # Relative precision is adjudicated separately; this exact quantization is
    # suitable for the first native-unit qualification, not an axis/scale repair.
    points = [tuple(round(float(x), 5) for x in p) for p in vertices]
    if not all(math.isfinite(x) for p in points for x in p):
        raise ValueError('Nonfinite converted geometry')
    return min(tuple(points[i:] + points[:i]) for i in range(3))


def compare_geometry(obj, geometry):
    positions, expected = [], Counter()
    for line in Path(obj).read_text().splitlines():
        if line.startswith('v '):
            positions.append([float(x) for x in line.split()[1:]])
        elif line.startswith('f '):
            indices = [int(x.split('/')[0])-1 for x in line.split()[1:]]
            expected[cyclic_triangle([positions[i] for i in indices])] += 1
    observed = Counter()
    for mesh in geometry['meshes']:
        if any(n != 3 for n in mesh['counts']):
            raise ValueError('Consumer produced nontriangle topology')
        indices = mesh['indices']
        for start in range(0, len(indices), 3):
            observed[cyclic_triangle([mesh['points'][i] for i in indices[start:start+3]])] += 1
    return {'triangles_match_native_coordinates_and_winding': expected == observed,
            'expected_triangles': sum(expected.values()), 'observed_triangles': sum(observed.values()),
            'missing_triangles': sum((expected-observed).values()), 'extra_triangles': sum((observed-expected).values()),
            'comparison': 'local position triples rounded to 5 decimals, cyclic order allowed, no axes/scale/reversal fix',
            'transforms_attributes': 'recorded in geometry.json; not silently applied or declared qualified'}


def execute(work, metadata, guard):
    env = os.environ.copy();env['SFC_REMIX_JOB_CONFIG'] = str(work / 'config.json')
    command = [str(guard), str(work), '180', str(256*1024*1024), str(8*1024*1024), *metadata['command']]
    write_json(work / 'execution.json', {'guard': str(guard.resolve()), 'guard_sha256': digest(guard),
                                       'command': command, 'python': sys.version})
    # Guard owns a Job Object before child startup; never kill by executable name.
    result = {'schema': 'sfc.remix.result.v1', 'fixture': metadata['fixture'], 'status': 'FAIL',
              'guard_exit': None}
    try:
        child = subprocess.run(command, env=env, timeout=200, check=False)
        result['guard_exit'] = child.returncode
        job = json.loads((work / 'job-result.json').read_text())
        result['job'] = job
        if child.returncode or job['stop_reason'] or job['exit_code'] or job['remaining_owned_processes']:
            raise ValueError(f'Owned job did not complete cleanly (stop_reason={job["stop_reason"]}, exit_code={job["exit_code"]})')
        inspect = json.loads((work / 'inspection.json').read_text())
        if inspect.get('status') != 'INSPECTED' or inspect.get('vendor_validation_passed') is not True:
            raise ValueError('Vendor pipeline/geometry inspection did not succeed')
        geometry = json.loads((work / 'geometry.json').read_text())
        comparison = compare_geometry(work / 'input/ship.obj', geometry)
        result.update(comparison)
        if not comparison['triangles_match_native_coordinates_and_winding']:
            raise ValueError('Geometry changed; bounded offline adjudication required')
        if metadata.get('textures'):
            from compare_obj_attributes import compare
            corners = compare((work/'input/ship.obj').read_text(), geometry)
            write_json(work/'corner-comparison-numeric.json', corners)
            if not corners.get('match'):
                raise ValueError('Textured import changed UVs/normals/groups')
            result['texture_preview_candidate'] = True
            result['usd_sha256'] = digest(work/'output/ship.usda')
            result['texture_fidelity'] = 'PENDING_VISUAL_REVIEW_SECONDARY_ROLE_UNPROVEN'
        result['status'] = 'SYNTHETIC_PREFLIGHT_PASS' if metadata['fixture'] else 'GEOMETRY_INGESTED_PREVIEW_PENDING'
    except (OSError, ValueError, KeyError, subprocess.TimeoutExpired) as exc:
        result['error'] = str(exc)
    write_json(work / 'result.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture', type=Path)
    parser.add_argument('--toolkit', type=Path, default=Path('C:/Project/RTXRemix'))
    parser.add_argument('--jobs', type=Path, default=Path('C:/Project/RemixJobs'))
    parser.add_argument('--fixture', action='store_true')
    parser.add_argument('--textures', action='store_true', help='Opt-in same-run primary-image derivative; secondary role remains unproven')
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--guard', type=Path, default=Path(__file__).resolve().parents[2] / 'artifacts/remix-ingest/bin/bounded_job.exe')
    args = parser.parse_args()
    try:
        if args.execute and not args.guard.is_file():
            raise ValueError('Build bounded_job.exe before execution')
        work, metadata = prepare(args.capture, args.toolkit, args.jobs, args.fixture, args.textures)
        print(f'Job directory: {work}', flush=True)
        if args.execute:
            result = execute(work, metadata, args.guard)
            print(json.dumps(result))
            if result['status'] == 'FAIL':
                return 1
    except (OSError, ValueError, KeyError, subprocess.TimeoutExpired) as exc:
        parser.exit(1, f'Remix job failed: {exc}\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
