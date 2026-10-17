"""Analyze bounded raw-bit corner snapshots, without auto-qualifying normal space."""
import argparse
import json
import math
import struct
from pathlib import Path


def float_bits(value):
    if not isinstance(value, int) or not 0 <= value <= 0xFFFFFFFF:
        raise ValueError('Invalid uint32 bit pattern')
    return struct.unpack('<f', struct.pack('<I', value))[0]


def matrix_error(bits):
    if len(bits) != 17:
        raise ValueError('Expected 68-byte matrix-plus-metadata')
    values = [float_bits(x) for x in bits[:16]]
    if not all(math.isfinite(x) for x in values):
        return None
    rows = [values[i:i + 3] for i in (0, 4, 8)]
    return max(abs(sum(a * b for a, b in zip(rows[i], rows[j])) - int(i == j))
               for i in range(3) for j in range(3))


def analyze(packet):
    records = packet['records']
    schema = packet['schema']
    windows = 6 if schema == 'm1.c01.corners.v1' else 18
    epoch_aware = schema == 'm1.c01.corners.v3'
    if schema not in ('m1.c01.corners.v1', 'm1.c01.corners.v2', 'm1.c01.corners.v3') or len(records) > windows * 2:
        raise ValueError('Unsupported schema or snapshot bound')
    if packet['written'] != len(records) or packet['captured'] > windows * 2:
        raise ValueError('Invalid snapshot counts')
    issues = []
    if packet['output_truncated'] or packet['captured'] != len(records):
        issues.append('Output incomplete')
    owners = {}
    reports = []
    previous = {}
    owner_identity = {}
    if epoch_aware:
        filters = packet['filters']
        transitions = packet['transitions']
        if len(filters) != 2 or any(len(f) != 7 for f in filters) or len(transitions) > 64:
            raise ValueError('Invalid bounded filter/transition metadata')
        for transition in transitions:
            if len(transition) != 7 or transition[1] not in range(1, 6) or transition[2] not in (0, 1):
                raise ValueError('Invalid epoch transition')
        if packet['transition_dropped']:
            issues.append('Epoch transition ledger saturated')
        if any(f[5] for f in filters):
            issues.append('Render thread mismatch within epoch')
        if any(f[6] for f in filters):
            issues.append('Ship address observed with changed visual association')
    for sample in records:
        owner = sample['owner']
        window = sample['window']
        if window not in range(windows) or not window * 5000 <= sample['elapsed_ms'] < (window + 1) * 5000:
            raise ValueError('Invalid requested-action window')
        if not owner or any(not sample[x] for x in ('ship', 'visual', 'model', 'source', 'manager')):
            issues.append('Missing semantic identity')
        interest = sample['filter'] if epoch_aware else owner
        if epoch_aware and (interest not in (0, 1) or
            (sample['ship'], sample['visual']) != tuple(filters[interest][:2])):
            raise ValueError('Snapshot outside its declared address interest filter')
        slots = owners.setdefault(interest, [])
        identity_tuple = (sample['ship'], sample['visual'], sample['thread'])
        if owner in owner_identity and owner_identity[owner] != identity_tuple:
            issues.append('Owner identity/thread cross-association')
        owner_identity[owner] = identity_tuple
        if window in slots:
            raise ValueError('Duplicate owner/window')
        slots.append(window)
        if len(owners) > 2 or len(slots) > windows:
            raise ValueError('Owner/window limits exceeded')
        if sample['status'] != 0:
            issues.append(f"Owner {owner} window {window}: guarded capture status {sample['status']}")
        polygons, corners = sample['polygons'], sample['corners']
        if len(polygons) > 64 or len(corners) > 512 or len(sample['dispatch']) != 3:
            raise ValueError('Record collection bounds exceeded')
        for polygon in polygons:
            if len(polygon) != 7 or not 0 <= polygon[1] < 256 or not 1 <= polygon[2] <= 256:
                raise ValueError('Invalid sampled polygon')
        lengths, nonfinite, groups, corner_bits = [], 0, {}, []
        for corner in corners:
            if len(corner) != 8 or not 0 <= corner[0] < len(polygons) or not 0 <= corner[1] < sample['vertex_count']:
                raise ValueError('Invalid corner/index')
            vector = [float_bits(x) for x in corner[2:5]]
            position = [float_bits(x) for x in corner[5:8]]
            if all(math.isfinite(x) for x in vector + position):
                lengths.append(math.sqrt(sum(x * x for x in vector)))
            else:
                nonfinite += 1
            source_index = polygons[corner[0]][1]
            groups.setdefault(source_index, set()).add(tuple(corner[2:5]))
            corner_bits.append(tuple(corner))
        if nonfinite:
            issues.append('Non-finite sampled vector/position')
        error = matrix_error(sample['object_transform'])
        position_error = matrix_error(sample['position_transform'])
        if error is None or position_error is None:
            issues.append('Non-finite matrix')
        identity = (owner, sample['model'], sample['source'])
        last = previous.get(identity)
        action = min(2, window // (2 if windows == 6 else 3))
        report = {'owner': owner, 'window': window, 'requested_action':
                  ('observe_no_commands', 'camera_only', 'ship_turn_camera_angle_held')[action],
                  'action_performed': 'SPONSOR_ATTESTATION_REQUIRED',
                  'status': sample['status'], 'sample_truncated': sample['sample_truncated'],
                  'corners': len(corners), 'nonfinite': nonfinite,
                  'vector_length_min': min(lengths) if lengths else None,
                  'vector_length_max': max(lengths) if lengths else None,
                  'object_basis_gram_max_error': error,
                  'position_basis_gram_max_error': position_error,
                  'dispatch': [f'0x{x:08X}' for x in sample['dispatch']],
                  'source_groups_with_multiple_vector_bit_patterns': sorted(k for k, v in groups.items() if len(v) > 1),
                  'object_transform_changed': last is not None and sample['object_transform'] != last[0],
                  'position_transform_changed': last is not None and sample['position_transform'] != last[1],
                  'corner_bits_changed': last is not None and corner_bits != last[2]}
        if epoch_aware:
            report['interest_filter'] = interest
            report['comparison_within_same_epoch_only'] = True
        reports.append(report)
        previous[identity] = (sample['object_transform'], sample['position_transform'], corner_bits)
    if len(owners) != 2 or any(sorted(observed) != list(range(windows)) for observed in owners.values()):
        issues.append(f'Two-owner {windows}-window observation incomplete')
    result = {'probe_id': 'M1-C01-RT-004' if epoch_aware else 'M1-C01-RT-002' if windows == 6 else 'M1-C01-RT-003', 'status': 'INPUT_EVIDENCE_READY_FOR_LEAD_REVIEW' if not issues else
            'ADDITIONAL_BOUNDED_EVIDENCE_REQUIRED', 'issues': sorted(set(issues)), 'records': reports,
            'normal_space_qualified': False, 'formal_m1': 'CONTINUES'}
    if epoch_aware:
        result['transitions'] = transitions
        result['transition_dropped'] = packet['transition_dropped']
        result['outside_filter_calls'] = packet['outside_filter_calls']
        result['coverage'] = [{'interest_filter': index,
            'missing_snapshot_windows': sorted(set(range(windows)) - set(owners.get(index, []))),
            'no_observed_mainline_windows': [w for w in range(windows) if not filters[index][3] & (1 << w)],
            'failed_or_absent_windows': [w for w in range(windows) if not filters[index][4] & (1 << w)]}
            for index in (0, 1)]
        result['identity_continuity_across_epochs_asserted'] = False
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_dir', type=Path)
    args = parser.parse_args()
    path = args.run_dir / 'M1-C01-corners.json'
    if path.stat().st_size > 3 * 1024 * 1024:
        parser.error('Input exceeds 3 MiB safeguard')
    try:
        packet = json.loads(path.read_text(encoding='utf-8-sig'))
        if packet['schema'] == 'm1.c01.corners.v1' and path.stat().st_size > 1024 * 1024:
            raise ValueError('Legacy v1 input exceeds 1 MiB')
        result = analyze(packet)
        metadata_path = args.run_dir / 'run-metadata.json'
        if packet['schema'] == 'm1.c01.corners.v3' and metadata_path.exists():
            if metadata_path.stat().st_size > 65536:
                raise ValueError('Metadata exceeds 64 KiB safeguard')
            probe = json.loads(metadata_path.read_text(encoding='utf-8-sig')).get('probe_id')
            if probe in ('M1-C01-RT-004', 'M1-C01-RT-005','M1-C01-RT-006','M1-C01-RT-007','M1-C01-RT-008','M1-C01-RT-009','M1-C01-RT-010'):
                result['probe_id'] = probe
                if probe in ('M1-C01-RT-007','M1-C01-RT-008'):
                    for record in result['records']:
                        record['requested_action']='setup_then_neutral_play_see_cue_log'
                if probe=='M1-C01-RT-009':
                    for record in result['records']:
                        record['requested_action']='setup_neutral_play_then_brief_camera_away_return_see_cue_log'
                if probe=='M1-C01-RT-010':
                    for record in result['records']:
                        record['requested_action']='identify_twenty_seconds_then_same_ship_lighting_see_component_phases'
    except (KeyError, TypeError, ValueError) as error:
        parser.error(f'Malformed corner packet: {error}')
    (args.run_dir / 'M1-C01-corner-analysis.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': result['status'], 'issues': result['issues'], 'records': len(result['records'])}))


if __name__ == '__main__':
    main()
