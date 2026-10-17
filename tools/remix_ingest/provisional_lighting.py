"""Explicit offline hypothesis derivative; NEVER establishes an SFC runtime role."""
import io
import json
from pathlib import Path
from PIL import Image
from run_remix_ingest import digest, write_json

LIMIT = 8*1024*1024


def multiply_encoded(primary, secondary):
    if primary.size != secondary.size or primary.size != (256, 256):
        raise ValueError('Only matching captured 256-square images are qualified')
    p, s = primary.convert('RGB').tobytes(), secondary.convert('RGB').tobytes()
    return Image.frombytes('RGB', primary.size, bytes((a*b+127)//255 for a, b in zip(p, s)))


def prepare(work, job):
    work, job = Path(work).resolve(), Path(job).resolve()
    config_path = work/'preview-config.json'
    config = json.loads(config_path.read_text())
    if Path(config['work']).resolve() != work or not config.get('textures'):
        raise ValueError('Requires freshly prepared textured preview scratch')
    metadata = json.loads((job/'job-metadata.json').read_text())
    capture = Path(metadata['capture']).resolve()
    folder = capture/'textured'
    manifest_path = folder/'association-manifest.json'
    manifest = json.loads(manifest_path.read_text())
    refs_path = capture/'TEXTURE-EXPORT-001.json'
    refs = json.loads(refs_path.read_text())
    if (digest(capture/'MESH-EXPORT-001.bin') != metadata['packet_sha256']
            or manifest['packet_sha256'] != metadata['packet_sha256']
            or manifest['references_sha256'] != digest(refs_path)
            or not manifest.get('primary_images_ready')
            or manifest['groups'] != refs['groups'] or refs.get('status') != 1
            or refs.get('hooks_restored') is not True):
        raise ValueError('Provisional images require verified same-capture associations')
    groups, images = manifest['groups'], manifest['images']
    if len(groups) != 5 or len(images) != 10 or len({g['group'] for g in groups}) != 5:
        raise ValueError('Only the five captured groups / ten resources are qualified')
    resources = {r['id']: r for r in images}
    if len(resources) != 10:
        raise ValueError('Duplicate resource identity')
    # Validate all inputs before creating any derivative. IDs are offline labels,
    # never dereferenced and never reused against a new running process.
    decoded = {}
    for ident, row in resources.items():
        path = folder/row['derived']
        if (path.is_symlink() or path.resolve().parent != folder.resolve()
                or path.stat().st_size > 1024*1024 or digest(path) != row['derived_sha256']):
            raise ValueError('Image provenance/path/bound mismatch')
        with Image.open(path) as image:
            if image.size != (256, 256) or row.get('alpha_present'):
                raise ValueError('Only captured opaque 256-square images are qualified')
            decoded[ident] = image.convert('RGB')
    for group in groups:
        if group['flags'] & 0x21 != 0x21 or group['primary'] not in decoded or group['secondary'] not in decoded:
            raise ValueError('Missing qualified primary/secondary pair')
    output = work/'provisional-lighting'
    output.mkdir(exist_ok=False)
    rows, total = [], 0
    for group in groups:
        product = multiply_encoded(decoded[group['primary']], decoded[group['secondary']]).convert('RGBA')
        stem = f'group_{group["group"]:03d}'
        paths = []
        for suffix, fmt in (('.png', 'PNG'), ('.dds', 'DDS')):
            stream = io.BytesIO(); product.save(stream, format=fmt)
            raw = stream.getvalue(); total += len(raw)
            if total > LIMIT:
                raise ValueError('Provisional image output exceeds 8 MiB')
            with Image.open(io.BytesIO(raw)) as check:
                if check.convert('RGBA').tobytes() != product.tobytes():
                    raise ValueError('Derived image round-trip changed pixels')
            path = output/(stem+suffix)
            with path.open('xb') as file:
                file.write(raw)
            paths.append({'path': path.relative_to(work).as_posix(), 'sha256': digest(path), 'bytes': len(raw)})
        rows.append({'group': group['group'], 'primary': group['primary'], 'secondary': group['secondary'],
                     'primary_png_sha256': resources[group['primary']]['derived_sha256'],
                     'secondary_png_sha256': resources[group['secondary']]['derived_sha256'],
                     'dds': paths[1]['path'], 'files': paths})
        config['dependency_sha256'].update({p['path']: p['sha256'] for p in paths})
    report = {'schema': 'sfc.provisional-lighting.v1', 'status': 'PROVISIONAL_RUNTIME_UNVERIFIED',
              'packet_sha256': metadata['packet_sha256'], 'association_manifest_sha256': digest(manifest_path),
              'references_sha256': digest(refs_path), 'groups': rows, 'image_bytes': total,
              'formula': 'per-channel floor((primary_encoded * secondary_encoded + 127)/255)',
              'intensity_assumption': 1.0, 'color_space_assumption': 'encoded product, emitted as sRGB texture',
              'not_proven': ['active SFC branch', 'legacy color space', 'physical strength', 'intermediate saturation equivalence'],
              'source_changes': False, 'geometry_or_uv_changes': False}
    write_json(work/'provisional-lighting.json', report)
    config['provisional_lighting'] = report
    config_path.write_text(json.dumps(config, indent=2)+'\n')
    return report
