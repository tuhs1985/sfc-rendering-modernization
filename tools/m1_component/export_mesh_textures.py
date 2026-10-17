"""Recover same-run registry-named originals; derive PNG/MTL without geometry edits.

Secondary resources are retained, NEVER guessed to be glow. A textured derivative
can therefore be useful while the overall increment remains PARTIAL.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path, PureWindowsPath
import struct
import sys

from PIL import Image
from analyze_mesh_export import analyze, FILE_LIMIT
from export_mesh_obj import export_obj

WARNING = 64 * 1024 * 1024
LIMIT = 128 * 1024 * 1024
REFERENCE_LIMIT = 512 * 1024


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_bounded(path, limit):
    with Path(path).open('rb') as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError(f'File exceeds bounded read: {Path(path).name}')
    return data


def source_path(game, filename):
    """Use registry path, not a search-by-basename or a guessed ship class."""
    path = PureWindowsPath(filename)
    if path.drive or path.root or '..' in path.parts or not path.parts or path.parts[0].lower() != 'assets':
        raise ValueError('Registry filename must be an Assets-relative path without traversal')
    # Resolve each component explicitly; also works in case-sensitive offline tests.
    actual = Path(game).resolve()
    for part in path.parts:
        matches = [p for p in actual.iterdir() if p.name.lower() == part.lower()]
        if len(matches) != 1:
            raise ValueError(f'Missing/ambiguous original image path: {filename}')
        actual = matches[0]
    assets = (Path(game)/'Assets').resolve()
    if not actual.resolve().is_relative_to(assets) or not actual.is_file():
        raise ValueError('Image escapes installed Assets directory')
    if actual.suffix.lower() not in ('.bmp', '.pcx'):
        raise ValueError('Unqualified original image format; no fallback or GPU readback')
    return actual


def recover(capture, game, output=None):
    capture, game = Path(capture), Path(game)
    output = Path(output) if output else capture/'textured'
    packet = capture/'MESH-EXPORT-001.bin'
    receipt = capture/'MESH-EXPORT-001-receipt.json'
    analysis = analyze(packet, receipt)
    raw = read_bounded(packet, FILE_LIMIT)
    if sha(raw) != analysis['packet_sha256']:
        raise ValueError('Packet changed after validation')
    h = struct.unpack_from('<64I', raw)
    refs = json.loads(read_bounded(capture/'TEXTURE-EXPORT-001.json', REFERENCE_LIMIT))
    if refs.get('schema') != 'sfc.texture.references.v1' or refs.get('status') != 1 or refs.get('hooks_restored') is not True:
        raise ValueError('Texture association incomplete; preserve raw capture as PARTIAL')
    for key, index in (('packet_fnv1a', 3), ('owner_epoch', 4), ('frame', 6), ('model', 10), ('source', 12)):
        if refs.get(key) != h[index]:
            raise ValueError('Texture references are not from the same mesh epoch')
    offset = 256 + h[16]*12 + h[17]*36 + h[18]*28
    sources = [struct.unpack_from('<10I', raw, offset+i*40) for i in range(h[19])]
    expected = [{'group': s[0], 'flags': s[1], 'primary': s[6], 'secondary': s[8],
                 'primary_name_offset': s[7], 'secondary_name_offset': s[9]} for s in sources]
    if refs.get('groups') != expected:
        raise ValueError('Source/group associations differ from packet')
    multitexture = refs.get('manager_multitexture_flag')
    if multitexture is not None and (type(multitexture) is not int or not 0 <= multitexture <= 255):
        raise ValueError('Invalid observed multitexture flag; absent historical value must remain unknown')
    path_word = refs.get('manager_secondary_path_word')
    if path_word is not None and (type(path_word) is not int or not 0 <= path_word <= 0xffffffff):
        raise ValueError('Invalid observed secondary-path word')
    fallback = refs.get('manager_fallback_validation_mask')
    previous_alpha_test = refs.get('manager_previous_alpha_test_flag')
    for value, maximum in ((fallback, 0xffffffff), (previous_alpha_test, 255)):
        if value is not None and (type(value) is not int or not 0 <= value <= maximum):
            raise ValueError('Invalid observed fallback eligibility input')
    used = {g['primary'] for g in expected if g['primary']}
    used |= {g['secondary'] for g in expected if g['flags'] & 0x20 and g['secondary']}
    resources = refs.get('resources', [])
    if len(resources) > 10 or len(used) > 10:
        raise ValueError('Ten-resource bound exceeded; PARTIAL')
    ids = [r['id'] for r in resources]
    if len(set(ids)) != len(ids) or set(ids) != used or any(type(i) is not int or not 1 <= i <= 4096 for i in ids):
        raise ValueError('Missing, duplicate or unexpected same-run resource identity')
    if output.exists() or output.resolve().is_relative_to((game/'Assets').resolve()):
        raise ValueError('Refusing to overwrite evidence or write into original assets')
    output.mkdir(parents=True, exist_ok=False)
    manifest = {'schema': 'sfc.texture.derivative.v1', 'status': 'PARTIAL',
                'packet_sha256': sha(raw), 'references_sha256': sha(read_bounded(capture/'TEXTURE-EXPORT-001.json', REFERENCE_LIMIT)),
                'owner_epoch': h[4], 'model': h[10], 'source': h[12], 'frame': h[6],
                'model_filename': refs['model_filename'], 'groups': expected, 'images': [],
                'textures_enabled': refs.get('textures_enabled'),
                'manager_multitexture_flag': multitexture,
                'manager_secondary_path_word': path_word,
                'manager_fallback_validation_mask': fallback,
                'manager_previous_alpha_test_flag': previous_alpha_test,
                'image_bytes': 0, 'warning_bytes': WARNING, 'hard_bytes': LIMIT,
                'uv_transform': 'none', 'geometry_transform': 'none',
                'normals': 'existing grey OBJ normalization only',
                'secondary_role': 'UNPROVEN_NOT_APPLIED_AS_EMISSION',
                'visual_comparison': 'PENDING_SPONSOR', 'findings': []}
    try:
        for resource in resources:
            path = source_path(game, resource['filename'])
            if not resource.get('registry_object') or not resource.get('manager_entry') or not resource.get('surface_identity'):
                raise ValueError('Missing live resource-table corroboration')
            if PureWindowsPath(resource['requested']).stem.lower() != path.stem.lower():
                raise ValueError('Requested model image name differs from live registry filename')
            original = read_bounded(path, LIMIT - manifest['image_bytes'])
            with Image.open(io.BytesIO(original)) as image:
                width, height = image.size
                if not 1 <= width <= 4096 or not 1 <= height <= 4096:
                    raise ValueError('Image dimension bound exceeded; PARTIAL')
                if image.format not in ('BMP', 'PCX'):
                    raise ValueError('Image bytes disagree with supported source formats')
                fmt, mode = image.format, image.mode
                image.load()
                alpha = 'A' in image.getbands() or 'transparency' in image.info
                derived = image.convert('RGBA' if alpha else 'RGB')
                encoded = io.BytesIO(); derived.save(encoded, format='PNG')
                png = encoded.getvalue()
                # Round-trip exact decoded colour/alpha; no UV/image flips or colour grading.
                with Image.open(io.BytesIO(png)) as check:
                    check.load()
                    if check.tobytes() != derived.tobytes():
                        raise ValueError('Lossless image conversion check failed')
            if manifest['image_bytes'] + len(original) + len(png) > LIMIT:
                raise ValueError('128 MiB original+derived image bound exceeded; PARTIAL')
            stem = f'resource_{resource["id"]:04d}'
            original_name, png_name = stem+path.suffix.lower(), stem+'.png'
            (output/original_name).write_bytes(original)
            (output/png_name).write_bytes(png)
            manifest['image_bytes'] += len(original)+len(png)
            if sha(read_bounded(path, len(original))) != sha(original):
                raise ValueError('Original image changed during recovery')
            manifest['images'].append({**resource, 'original_path': str(path.resolve()),
                'original_copy': original_name, 'original_sha256': sha(original), 'original_bytes': len(original),
                'width': width, 'height': height, 'format': fmt, 'mode': mode,
                'alpha_present': alpha, 'alpha_role': 'UNPROVEN' if alpha else 'no decoded alpha',
                'derived': png_name, 'derived_sha256': sha(png), 'derived_bytes': len(png)})
        enabled = refs.get('textures_enabled')
        if type(enabled) is not int or not 1 <= enabled <= 255 or any(not g['primary'] or not g['flags'] & 1 for g in expected):
            raise ValueError('Primary image use/intentionally-untextured status unresolved')
        export_obj(packet, output/'ship.obj', receipt)
        materials = []
        for g in expected:
            materials += [f'newmtl source_{g["group"]:03d}', 'Ka 0 0 0', 'Kd 1 1 1',
                          'Ks 0 0 0', 'd 1', 'illum 1', f'map_Kd resource_{g["primary"]:04d}.png', '']
        (output/'ship.mtl').write_text('\n'.join(materials), encoding='ascii')
        obj_manifest = json.loads((output/'ship.obj-manifest.json').read_text())
        obj_manifest['mtl'] = {'name': 'ship.mtl', 'bytes': (output/'ship.mtl').stat().st_size,
                               'sha256': sha((output/'ship.mtl').read_bytes())}
        obj_manifest['policy']['materials'] = 'registry_proven_primary_images_secondary_role_unproven'
        obj_manifest['texture_derivative'] = True
        (output/'ship.obj-manifest.json').write_text(json.dumps(obj_manifest, indent=2)+'\n')
        manifest.update(primary_images_ready=True, obj_sha256=sha((output/'ship.obj').read_bytes()),
                        mtl_sha256=sha((output/'ship.mtl').read_bytes()))
        manifest['findings'].append('Secondary image role and visual placement remain unproven; not an increment PASS.')
    except (ValueError, OSError, Image.DecompressionBombError) as exc:
        manifest['findings'].append(str(exc))
        manifest['primary_images_ready'] = False
    manifest['size_warning'] = manifest['image_bytes'] >= WARNING
    (output/'association-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture', type=Path)
    parser.add_argument('--game', type=Path, default=Path('C:/Games/Taldren Software Inc/Starfleet Command Orion Pirates'))
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        result = recover(args.capture, args.game, args.output)
        print(json.dumps(result, indent=2))
        return 0 if result['primary_images_ready'] else 2
    except (OSError, ValueError, KeyError, TypeError, struct.error) as exc:
        print(f'PARTIAL: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
