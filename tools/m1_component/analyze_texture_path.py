"""Adjudicate recorded texture-path inputs without inventing missing GPU state."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
from analyze_mesh_export import analyze, FILE_LIMIT


def classify(path_word, multitexture):
    for value, maximum in ((path_word, 0xffffffff), (multitexture, 255)):
        if value is not None and (type(value) is not int or not 0 <= value <= maximum):
            raise ValueError('Invalid recorded texture-path input')
    if path_word is None or multitexture is None:
        return 'UNOBSERVED'
    if path_word == 0:
        return 'PRIMARY_ONLY_GATE'
    if multitexture:
        return 'MULTITEXTURE_MODE0'
    return 'FALLBACK_FAMILY_EXACT_MODE_UNOBSERVED'


def inspect(capture):
    capture = Path(capture)
    packet = capture/'MESH-EXPORT-001.bin'
    checked = analyze(packet, capture/'MESH-EXPORT-001-receipt.json')
    refs_path = capture/'TEXTURE-EXPORT-001.json'
    if packet.stat().st_size > FILE_LIMIT or refs_path.stat().st_size > 512*1024:
        raise ValueError('Evidence size bound exceeded')
    raw = packet.read_bytes()
    if hashlib.sha256(raw).hexdigest() != checked['packet_sha256']:
        raise ValueError('Packet changed during review')
    h = struct.unpack_from('<64I', raw)
    refs = json.loads(refs_path.read_text(encoding='utf-8-sig'))
    if (refs.get('schema') != 'sfc.texture.references.v1' or refs.get('status') != 1
            or refs.get('hooks_restored') is not True):
        raise ValueError('Incomplete or unrestored texture capture')
    for key, index in (('packet_fnv1a', 3), ('owner_epoch', 4), ('frame', 6), ('model', 10), ('source', 12)):
        if refs.get(key) != h[index]:
            raise ValueError('Cross-epoch texture association')
    offset = 256+h[16]*12+h[17]*36+h[18]*28
    sources = [struct.unpack_from('<10I', raw, offset+i*40) for i in range(h[19])]
    groups = [{'group': s[0], 'flags': s[1], 'primary': s[6], 'secondary': s[8],
               'primary_name_offset': s[7], 'secondary_name_offset': s[9]} for s in sources]
    if refs.get('groups') != groups:
        raise ValueError('Captured source/group data mismatch')
    path_word, multi = refs.get('manager_secondary_path_word'), refs.get('manager_multitexture_flag')
    branch = classify(path_word, multi)
    mask, previous = refs.get('manager_fallback_validation_mask'), refs.get('manager_previous_alpha_test_flag')
    # Same widths as path-word/byte; missing historical values stay unknown.
    classify(mask, previous)
    prediction = 'N/A'
    if branch == 'FALLBACK_FAMILY_EXACT_MODE_UNOBSERVED':
        prediction = 'UNOBSERVED_INPUTS'
        if mask is not None and previous is not None:
            prediction = 'MODES_2_THEN_1_REQUESTED' if mask & (2 if previous else 1) else 'MODE_1_ONLY_REQUESTED'
    return {'schema': 'sfc.texture.path-analysis.v1', 'packet_sha256': checked['packet_sha256'],
            'references_sha256': hashlib.sha256(refs_path.read_bytes()).hexdigest(),
            'owner_epoch': h[4], 'frame': h[6], 'model': h[10], 'source': h[12],
            'model_filename': refs['model_filename'], 'groups': groups,
            'textures_enabled': refs.get('textures_enabled'),
            'manager_secondary_path_word': path_word, 'manager_multitexture_flag': multi,
            'manager_fallback_validation_mask': mask, 'manager_previous_alpha_test_flag': previous,
            'static_fallback_request_prediction': prediction,
            'branch_family': branch, 'confidence': 'CONFIRMED' if branch != 'UNOBSERVED' else None,
            'confidence_scope': 'Recorded inputs plus exact-build static branch; not direct executed-pass or GPU-state observation',
            'exact_fallback_passes': 'UNOBSERVED' if branch == 'FALLBACK_FAMILY_EXACT_MODE_UNOBSERVED' else 'N/A',
            'missing_for_fallback_eligibility': ([name for name, value in
               (('manager+0x800C validation mask', mask), ('manager+0x3F54 previous alpha-test state', previous)) if value is None]
               if branch == 'FALLBACK_FAMILY_EXACT_MODE_UNOBSERVED' else []),
            'not_proven': ['executed pass count', 'GPU texture-stage/blend values', 'physical emission strength', 'legacy color space'],
            'provisional_preview_disposition': 'Keep labelled hypothesis; no automatic promotion or asset changes'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture', type=Path)
    parser.add_argument('--output', type=Path, help='New report path; existing evidence is never overwritten')
    args = parser.parse_args()
    result = inspect(args.capture)
    raw = (json.dumps(result, indent=2, allow_nan=False)+'\n').encode()
    if len(raw) > 65536:
        raise ValueError('Path analysis exceeds 64 KiB')
    with (args.output or args.capture/'TEXTURE-EXPORT-001-path-analysis.json').open('xb') as stream:
        stream.write(raw)
    print(result['branch_family'])


if __name__ == '__main__': main()
