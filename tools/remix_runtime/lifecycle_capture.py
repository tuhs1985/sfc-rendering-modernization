"""Bounded diagnostic phases and conservative owner-observation analysis."""
import json
from pathlib import Path

PHASES = (
    (15, 1, 'Hold your ship and camera still; keep your ship alive.'),
    (25, 2, 'Switch to the enemy camera now, leaving your own ship out of view. Keep it alive.'),
    (40, 3, 'Return the camera to your own ship now. Leave it alive for another20seconds.'),
    (60, 4, 'Destroy your own ship now using your usual method. Stay in this mission until the exit cue.'),
)
RECOVERY_PHASES = (
    (15, 1, 'Hold your ship and camera still. Keep both ships alive throughout.'),
    (25, 2, 'Switch to the enemy camera; leave your own ship out of view.'),
    (40, 3, 'Return to your own ship. Look for the extra ship returning beside it.'),
    (55, 2, 'Switch to the enemy camera again; keep your own ship alive.'),
    (70, 3, 'Return to your own ship again. Check that the extra ship returns.'),
    (80, 1, 'Hold the view steady. Do not exit until the two LOW exit beeps.'),
)


def analyze(directory):
    directory = Path(directory)
    rows = {}
    for line in (directory/'LIVE-SCENE-001-updates.jsonl').read_text().splitlines():
        row = json.loads(line)
        if len(row) != 96 or not all(type(v) is int and 0 <= v <= 0xffffffff for v in row):
            raise ValueError('Invalid lifecycle observation')
        owner = rows.setdefault(str(row[1]), dict(records=0, first_ms=row[3], last_ms=row[3], statuses=set(), revisions=set()))
        owner['records'] += 1
        owner['last_ms'] = row[3]
        owner['statuses'].add(row[4]); owner['revisions'].add(row[7])
    for owner in rows.values():
        for key in ('statuses', 'revisions'): owner[key] = sorted(owner[key])
    events = [json.loads(line) for line in (directory/'LIFECYCLE-001-events.jsonl').read_text().splitlines()]
    for row in events:
        if len(row) != 96 or not all(type(v) is int and 0 <= v <= 0xffffffff for v in row):
            raise ValueError('Invalid lifecycle event')
    worker = json.loads((directory/'LIVE-SCENE-001-worker.json').read_text())
    complete = (bool(events) and worker.get('lifecycle_capture') is True and worker.get('stopped') is True
                and not any(worker.get(k, 1) for k in ('io_failed','saturated','dropped','lifecycle_dropped','lifecycle_omitted','lifecycle_pending'))
                and worker.get('lifecycle_records') == len(events))
    return dict(result='OBSERVATIONS_READY_NOT_DEATH_PROOF' if complete else 'PARTIAL', owners=rows,
                transitions=[dict(owner=r[1], frame=r[2], elapsed_ms=r[3], status=r[4], revision=r[7], sequence=r[0]) for r in events],
                worker=worker, native_death_signal_qualified=False,
                interpretation='Status2 means render-observation retirement, NOT native destruction. Cues record requested actions, not confirmed completion.')
