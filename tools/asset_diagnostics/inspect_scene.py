"""Read the existing SFC replay and its source provenance without a renderer."""

import argparse
import json
from pathlib import Path
import re
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/d3d9_proof'))
sys.path.insert(0, str(ROOT / 'src/assets'))
from scene_bundle import FRAME, MAX_BYTES, TEXTURE_MAGIC, flatten, read_replay, resolve_image, sha, texture
from asset_capture_review import decode_capture
from mesh_decode import decode_mesh
from live_camera import camera_state
from analyze_live_camera import native_matrix
from remix_coordinates import POLICY, bgra


def read_checked(path, expected_hash, limit):
    with path.open('rb') as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit or sha(raw) != expected_hash:
        raise ValueError(f'Invalid evidence size or hash for {path.name}')
    return raw


def source_path(root, name):
    relative = Path(name.replace('\\', '/'))
    if relative.is_absolute() or relative.anchor or '..' in relative.parts:
        raise ValueError('Source provenance path must be relative')
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError('Source provenance path escapes evidence root')
    return path


def read_frames(manifest, replay, mesh, fragment_poses):
    frames = manifest['frames']
    if len(frames) != len(replay['frames']):
        raise ValueError('Replay and manifest frame counts differ')
    live = manifest.get('fresh_preparation_row')
    sequence = None
    if live is not None:
        raw = struct.pack('<96I', *live)
        if sha(raw) != manifest.get('fresh_preparation_row_sha256') or len(frames) != 1:
            raise ValueError('Fresh source row provenance')
        if (live[1], live[7], live[2], live[5], live[6]) != (
                frames[0]['owner'], frames[0]['revision'], frames[0]['frame'],
                mesh['header'][10], mesh['header'][12]):
            raise ValueError('Fresh source row identity')
        # Reuse the native row decoder for the metadata fields it actually provides.
        for key, offset in (('model', 8), ('view', 49), ('projection', 66)):
            if frames[0][key] != native_matrix(live[offset:offset + 17]):
                raise ValueError(f'Fresh source {key} differs from replay')
        camera = camera_state(live, [0, 0, 0], mesh['used_points'])
        if frames[0]['viewport'] != camera['viewport']:
            raise ValueError('Fresh source viewport differs from replay')
        # Production asset preparation can occur before a source sequence exists.
        sequence = live[94] | (live[95] << 32)

    result = []
    previous = 0
    revision = frames[0]['revision']
    for frame, binary in zip(frames, replay['frames'], strict=True):
        if (frame['owner'] != mesh['header'][4] or frame['revision'] != revision
                or frame['frame'] <= previous):
            raise ValueError('Replay frame order or instance identity')
        serialized = FRAME.pack(frame['owner'], revision, frame['frame'], frame['active'],
                                *(word for key in ('model', 'view', 'projection')
                                  for word in flatten(frame[key])), *frame['viewport'])
        if serialized != FRAME.pack(*binary):
            raise ValueError('Manifest pose or camera differs from replay')
        if fragment_poses is not None:
            draws, cameras = fragment_poses
            sample = frame['frame']
            if sample > len(draws) or sample not in cameras:
                raise ValueError('Missing captured fragment pose or camera')
            draw, camera = draws[sample - 1], cameras[sample]
            row = [0] * 96
            row[8:25], row[25:42], row[48], row[49:89] = draw['supplied'], draw['composed'], 1, camera
            if (frame['model'] != native_matrix(draw['supplied'])
                    or frame['view'] != native_matrix(camera[:17])
                    or frame['projection'] != native_matrix(camera[17:34])
                    or frame['viewport'] != camera_state(row, [0, 0, 0], mesh['used_points'])['viewport']):
                raise ValueError('Fragment pose or camera differs from capture')
        previous = frame['frame']
        result.append(dict(frame, source_frame=frame['frame'] if fragment_poses is None else None,
                           source_sequence=sequence or None))
    return result


def image_bindings(folder, manifest, replay, mesh, game_root):
    images = manifest['textures']
    upload_origin = manifest.get('remix_texture_origin')
    if upload_origin not in (None, POLICY):
        raise ValueError('Unknown replay texture origin')
    if not 1 <= len(images) <= 256:
        raise ValueError('Replay image count')
    remaining = MAX_BYTES
    for index, image in enumerate(images):
        width, height = image['width'], image['height']
        if not 1 <= width <= 4096 or not 1 <= height <= 4096:
            raise ValueError('Replay image extent')
        size = width * height * 4
        packed = read_checked(folder / f'texture-{index}.bin', image['replay_sha256'], min(remaining, size + 16))
        if (len(packed) != size + 16 or len(packed) != image['bytes']
                or struct.unpack_from('<4I', packed) != (TEXTURE_MAGIC, width, height, size)
                or sha(packed[16:]) != image['decoded_bgra_sha256']
                or not re.fullmatch(r'[0-9a-f]{64}', image['original_sha256'])):
            raise ValueError('Replay image descriptor or provenance')
        remaining -= len(packed)

    resources = {item['id']: item['filename'] for item in mesh['refs']['resources']}
    captured = {group['group']: group for group in mesh['groups']}
    corners_by_group = {}
    for group, first in mesh['polygons']:
        corners_by_group.setdefault(group, []).extend((first, first + 1, first + 2))
    if [list(group) for group in replay['groups']] != manifest['groups']:
        raise ValueError('Replay group descriptors differ from manifest')
    bindings = []
    originals = {}
    for group, material, first, count in replay['groups']:
        captured_group = captured.get(group)
        if (captured_group is None or material >= len(images)
                or replay['indices'][first:first + count] != corners_by_group.get(group)):
            raise ValueError('Replay group differs from capture')
        filename = resources[captured_group['primary']]
        image = images[material]
        if game_root is not None:
            if filename not in originals:
                raw = resolve_image(game_root, filename).read_bytes()
                metadata, pixels = texture(raw)
                width, height = metadata['width'], metadata['height']
                upload = bgra(pixels, width, height) if upload_origin else pixels
                originals[filename] = (sha(raw), sha(upload), width, height, sha(pixels))
            if originals[filename][:4] != (image['original_sha256'], image['decoded_bgra_sha256'],
                                          image['width'], image['height']):
                raise ValueError('Primary image content differs from capture binding')
        elif filename != image['filename']:
            raise ValueError('Texture alias requires --game-root to verify original content')
        secondary = captured_group['secondary']
        primary = {'filename': filename, 'original_sha256': image['original_sha256'],
                   'source_bgra_sha256': originals[filename][4] if game_root is not None else None,
                   'width': image['width'], 'height': image['height']}
        bindings.append({'group': group, 'first_index': first, 'index_count': count,
                         'primary': primary, 'secondary_filename': resources.get(secondary),
                         'secondary_id': secondary or None,
                         'secondary_role_evidence': mesh['refs'].get('secondary_role')})
    if len(bindings) != len(corners_by_group):
        raise ValueError('Capture group coverage')
    return bindings


def read_scene(folder, evidence_root=ROOT, *, game_root=None):
    """Return arrays and source identities, using the current replay schema."""
    folder, root = Path(folder), Path(evidence_root).resolve()
    with (folder / 'scene.json').open('rb') as stream:
        raw = stream.read(512 * 1024 + 1)
    if len(raw) > 512 * 1024:
        raise ValueError('Scene manifest byte cap')
    manifest = json.loads(raw)
    if manifest.get('schema') != 'SFC-neutral-offline-scene-1':
        raise ValueError('Scene manifest schema')
    replay_hash = manifest['replay_sha256']
    read_checked(folder / 'scene.bin', replay_hash, 2 * 1024 * 1024)
    replay = read_replay(folder / 'scene.bin')
    packet = source_path(root, manifest['source_packet'])
    raw = read_checked(packet, manifest['source_packet_sha256'], 2 * 1024 * 1024)
    refs = read_checked(packet.with_suffix('.json'), manifest['source_references_sha256'], 256 * 1024)
    metadata = json.loads(read_checked(source_path(root, manifest['source_metadata']),
                                       manifest['source_metadata_sha256'], 4 * 1024 * 1024))
    session = manifest['source_session']
    fragment = bool(re.fullmatch(r'break-piece-[0-3]\.bin', packet.name))
    fragment_poses = None
    if fragment:
        if metadata.get('session') != session:
            raise ValueError('Break capture session mismatch')
        capture = decode_capture(packet.parent)
        mesh = next((item for item in capture['pieces'].values()
                     if item['packet_sha256'] == sha(raw) and item['refs'] == json.loads(refs)), None)
        if mesh is None:
            raise ValueError('Replay has no matching captured fragment')
        pose = next((item for item in capture['poses'] if item['child'] == mesh['piece']['child']), None)
        if pose is None:
            raise ValueError('Missing captured fragment pose')
        fragment_poses = pose['draws'], {item['sample']: item['words'] for item in pose['cameras']}
    else:
        actual = metadata.get('live_channel') or metadata.get('semantic_calibration', {}).get('scene_session')
        if actual != session or not isinstance(session, str) or not session:
            raise ValueError('Ship capture session mismatch')
        mesh = decode_mesh(raw, refs)
    expected = [(*mesh['points'][index], *normal, *uv) for index, normal, uv in mesh['corners']]
    if (expected != [vertex[:8] for vertex in replay['vertices']]
            or mesh['geometry_sha256'] != manifest['geometry_sha256']
            or mesh['refs']['model_filename'] != manifest['model_name']):
        raise ValueError('Replay geometry or model differs from source')
    bindings = image_bindings(folder, manifest, replay, mesh, game_root)
    identity = {'geometry': mesh['geometry_sha256'], 'groups': [
        (row['group'], row['primary']['original_sha256'], row['first_index'], row['index_count'])
        for row in bindings]}
    if sha(json.dumps(identity, sort_keys=True).encode()) != manifest['asset_sha256']:
        raise ValueError('Replay asset content identity differs')
    frames = read_frames(manifest, replay, mesh, fragment_poses)
    unavailable = {'damage': 'no matching per-owner damage state in this replay',
                   'lights': 'no matching native light record in this replay',
                   'retirement': 'replay records samples only',
                   'secondary_image_role': 'source bindings only, material interpretation varies'}
    if fragment:
        unavailable['source_frame'] = 'legacy debris replay uses per-piece sample ordinals'
        unavailable['child_owner_epoch'] = 'legacy capture identifies parent and piece index'
    if not frames[0]['source_sequence']:
        unavailable['source_sequence'] = 'no renderer-ingress sequence in source evidence'
    return {'session': session, 'owner_epoch': mesh['header'][4],
            'fragment': ({key: mesh['piece'][key] for key in ('index', 'parent_owner_epoch', 'visual_epoch')}
                         if fragment else None),
            'asset': {'content': manifest['asset_sha256'], 'revision': frames[0]['revision'],
                      'model': manifest['model_name']}, 'frames': frames,
            'positions': mesh['points'], 'corners': mesh['corners'], 'indices': replay['indices'],
            'groups': bindings, 'source_packet': manifest['source_packet'],
            'source_packet_sha256': manifest['source_packet_sha256'],
            'conventions': dict(manifest['conventions'], image='source BGRA, top row first when verified'),
            'replay_image_origin': manifest.get('remix_texture_origin'), 'unavailable': unavailable}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('replay', type=Path, nargs='+', help='Existing scene.json and scene.bin directory')
    parser.add_argument('--evidence-root', type=Path, default=ROOT)
    parser.add_argument('--game-root', type=Path, help='Read original images to verify hashes and aliases')
    parser.add_argument('--arrays', action='store_true', help='Include positions, corner normals/UVs and indices')
    args = parser.parse_args()
    try:
        scenes = [read_scene(folder, args.evidence_root, game_root=args.game_root) for folder in args.replay]
    except (OSError, ValueError, KeyError, TypeError, struct.error) as error:
        parser.exit(1, f'Scene inspection failed: {error}\n')
    sessions = {}
    for scene in scenes:
        if not args.arrays:
            for field in ('positions', 'corners', 'indices'):
                scene[field + '_count'] = len(scene.pop(field))
        sessions.setdefault(scene['session'], []).append(scene)
    print(json.dumps(sessions, indent=2))


if __name__ == '__main__':
    main()
