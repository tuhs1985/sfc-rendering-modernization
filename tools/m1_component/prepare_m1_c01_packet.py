"""Bounded offline C-01 packet preparation; never attaches to a game process."""

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

CLIENT_SHA256 = '4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29'
ADDRESS = re.compile(r'^\s*([0-9A-Fa-f]{8}):')
WINDOWS = (
    ('ship_transform_handoff', 0x004162B9, 0x00416360),
    ('model0_primary_and_secondary', 0x0042E4B2, 0x0042E650),
    ('source_init_and_polygon_preparation', 0x006ABF80, 0x006AC600),
)
MAX_DISASM = 128 * 1024 * 1024
MAX_CSV = 32 * 1024 * 1024
MAX_PACKET = 2 * 1024 * 1024
MAX_ROWS = 50000


def digest(path):
    sha = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(65536), b''):
            sha.update(block)
    return sha.hexdigest().upper()


def select_windows(path):
    if path.stat().st_size > MAX_DISASM:
        raise ValueError('Disassembly input exceeds 128 MiB')
    selected = {name: [] for name, _, _ in WINDOWS}
    active = None
    size = 0
    with path.open(encoding='utf-8', errors='strict') as handle:
        for line in handle:
            if len(line) > 8192:
                raise ValueError('Unexpected oversized disassembly line')
            match = ADDRESS.match(line)
            if match:
                address = int(match[1], 16)
                active = next((name for name, lo, hi in WINDOWS
                               if lo <= address <= hi), None)
            if active:
                size += len(line.encode('utf-8'))
                if size > MAX_PACKET // 2:
                    raise ValueError('Selected disassembly exceeds 1 MiB')
                selected[active].append(line.rstrip('\r\n'))
    if any(not lines for lines in selected.values()):
        raise ValueError('Required exact-build instruction window missing')
    return selected


def owner_evidence(path):
    if path.stat().st_size > MAX_CSV:
        raise ValueError('Semantic CSV input exceeds 32 MiB')
    owners = {}
    rows = 0
    csv.field_size_limit(8192)
    with path.open(newline='', encoding='utf-8-sig') as handle:
        reader = csv.DictReader(handle)
        required = {'event', 'owner_id', 'return_address', 'ship', 'visual',
                    'model0', 'source', 'elapsed_ms'}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError('Missing semantic CSV fields')
        for row in reader:
            rows += 1
            if rows > MAX_ROWS:
                raise ValueError('Semantic CSV exceeds 50,000 rows')
            if row['event'] != 'model0' or int(row['owner_id']) == 0:
                continue
            if int(row['return_address'], 0) != 0x0042FDD5:
                raise ValueError('Assigned Model0 owner has non-mainline return')
            owner = int(row['owner_id'])
            if owner not in owners:
                if len(owners) >= 8:
                    raise ValueError('More than eight detailed owner epochs')
                owners[owner] = {
                    'observed_model0_events': 0,
                    'first_elapsed_ms': int(row['elapsed_ms']),
                    'last_elapsed_ms': int(row['elapsed_ms']),
                    'identity': {key: row[key] for key in
                                 ('ship', 'visual', 'model0', 'source')},
                    'identity_changes': 0,
                    'recorded_tint_sample_rgb': [],
                }
            item = owners[owner]
            item['observed_model0_events'] += 1
            item['last_elapsed_ms'] = int(row['elapsed_ms'])
            if item['identity'] != {key: row[key] for key in item['identity']}:
                item['identity_changes'] += 1
            if int(row.get('tint_applied', '0')):
                color = row.get('tint_original_rgb', '')
                if color not in item['recorded_tint_sample_rgb']:
                    if len(item['recorded_tint_sample_rgb']) >= 256:
                        raise ValueError('Unexpected sample RGB cardinality')
                    item['recorded_tint_sample_rgb'].append(color)
    return {'input_rows': rows, 'owners': owners,
            'limitation': 'Historical per-process identity only; RGB is a single '
                          'recorded sample per substitution, not a source distribution.'}


def prepare(client, disassembly, events=None):
    actual = digest(client)
    if actual != CLIENT_SHA256:
        raise ValueError('Client hash differs from supported exact build')
    windows = select_windows(disassembly)
    packet = {
        'schema': 'm1.c01.offline-input-packet.v1',
        'status': 'INPUT_QUALIFICATION_PENDING',
        'client': {'path': str(client.resolve()), 'sha256': actual},
        'disassembly': {'path': str(disassembly.resolve()),
                        'sha256': digest(disassembly),
                        'provenance_limitation': 'Retained dumpbin text; hash client '
                                                'and text separately. This does not '
                                                'prove every instruction matches PE bytes.'},
        'instruction_windows': windows,
        'unresolved': ['surface normal/position fields', 'coordinate space',
                       'numeric orientation transform', 'source-to-surface sharing',
                       'existing lighting response and safe output location'],
        'conclusion': 'No normal, matrix, lighting contract or shading feasibility '
                      'is confirmed automatically. Analyst must adjudicate exact '
                      'references before defining a live read-only probe.',
    }
    if events is not None:
        packet['historical_events'] = {'path': str(events.resolve()),
                                       'sha256': digest(events),
                                       **owner_evidence(events)}
    return packet


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--client', type=Path, required=True)
    parser.add_argument('--disassembly', type=Path, required=True)
    parser.add_argument('--events', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    # Outputs confined to ignored project artifacts; never overwrite evidence.
    root = Path(__file__).resolve().parents[2] / 'artifacts' / 'm1' / 'c01'
    output = args.output.resolve()
    if root.resolve() not in output.parents:
        parser.error('Output must be a new file below artifacts/m1/c01')
    if output in [p.resolve() for p in
                  (args.client, args.disassembly, args.events) if p is not None]:
        parser.error('Output cannot overwrite an input')
    packet = prepare(args.client, args.disassembly, args.events)
    encoded = (json.dumps(packet, indent=2) + '\n').encode('utf-8')
    if len(encoded) > MAX_PACKET:
        parser.error('Packet exceeds 2 MiB; no output written')
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('xb') as handle:
        handle.write(encoded)
    print(f'Packet prepared ({len(encoded)} bytes); INPUT_QUALIFICATION_PENDING')


if __name__ == '__main__':
    main()
