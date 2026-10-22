"""Independent-source replay deadlines. No SFC GPU contention or frame-seal claim."""
import csv
import json
import re
from pathlib import Path
import numpy as np


def assess(rows, lag_sequence=0):
    if not 1 <= len(rows) <= 300:
        raise ValueError('Input row bound')
    previous = 0
    missed = []
    costs = []
    for row in rows:
        sequence = row['sequence']
        offered, deadline, completed, frequency = (row[k] for k in ('offered_qpc', 'deadline_qpc', 'completed_qpc', 'frequency'))
        if (not previous < sequence <= 300 or not row['source_frame'] or
            not 0 < offered < deadline or completed < offered or
            not 0 < frequency < 10**12 or frequency != rows[0]['frequency']):
            raise ValueError('Input sequence/clock')
        if row['on_time'] not in (0, 1) or row['on_time'] != int(completed < deadline):
            raise ValueError('Input deadline flag')
        previous = sequence
        costs.append((completed - offered) * 1000 / frequency)
        if not row['on_time']:
            missed.append(sequence)
    recovery = next((r['sequence'] for r in rows if r['sequence'] > lag_sequence and r['on_time']), None) if lag_sequence else None
    return dict(consumed=len(rows), omitted_source_sequences=300-len(rows), last_sequence=previous,
        late_completions=len(missed), late_sequences=missed,
        source_to_receiver_ack_ms=dict(zip(('p50', 'p95', 'max'), map(float, np.quantile(costs, [.5, .95, 1])))),
        injected_lag_sequence=lag_sequence, first_on_time_after_injected_lag=recovery,
        scope='Independent synthetic60Hz source cycling captured states;all completed costs retained. '
              'Late packets were copied into an offline receiver cache,NOT displayed. '
              'No source-frame seal,current SFC expectation,simultaneous SFC GPU load or live presentation claim.')


def analyze(folder, injected_ms):
    folder = Path(folder)
    path = folder / 'input-timing.csv'
    if path.stat().st_size > 128*1024:
        raise ValueError('Input timing cap')
    with path.open() as f:
        rows = [{k: int(v) for k, v in r.items()} for r in csv.DictReader(f)]
    text = (folder / 'job-console.log').read_text()
    matches = re.findall(r'INPUT_REPLAY_COMPLETE source_late=(\d+) obsolete=(\d+) expired=(\d+) invalid=(\d+) lag_used=(\d+) lag_sequence=(\d+) mapping_bytes=1344', text)
    if len(matches) != 1:
        raise ValueError('Input source completion receipt')
    late, obsolete, expired, invalid, lag_used, lag_sequence = map(int, matches[0])
    if invalid or bool(lag_used) != bool(injected_ms):
        raise ValueError('Invalid input or missing injected stall')
    result = assess(rows, lag_sequence)
    if injected_ms and (lag_sequence not in result['late_sequences'] or not result['first_on_time_after_injected_lag']):
        raise ValueError('Injected stall/recovery not demonstrated')
    result['counters'] = dict(source_late=late, obsolete=obsolete, expired=expired, invalid=invalid)
    (folder / 'input-analysis.json').write_text(json.dumps(result, indent=2))
    return result
