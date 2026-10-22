"""Observed source windows, not frame sealing or a live-render deadline proof."""
import argparse
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/remix_runtime'))
from source_timing import HEADER, RECORD, STORE_BYTES, decode


def distribution(values):
    if not values:
        return None
    return dict(zip(('min', 'p05', 'p50', 'p95', 'max'),
                    map(float, np.quantile(values, [0, .05, .5, .95, 1]))))


def assess(raw, session, pid):
    validation = decode(raw, session, pid)
    frequency = validation['frequency']
    grouped = {}
    for r in RECORD.iter_unpack(raw[HEADER.size:]):
        grouped.setdefault((r[1], r[3], r[4]), {}).setdefault(r[0], []).append(r)
    exact = []
    for key, stages in grouped.items():
        if len(stages.get(1, [])) == len(stages.get(2, [])) == 1:
            a, b = stages[1][0], stages[2][0]
            if a[11:13] == b[11:13] and a[8:10] == b[8:10]:
                exact.append(a)
    frames = {}
    owners = {}
    for r in sorted(exact, key=lambda r: r[10]):
        frames.setdefault(r[1], []).append(r)
        owners.setdefault((r[3], r[4]), []).append(r)
    profiles = []
    for (owner, revision), rows in sorted(owners.items()):
        leads = [(r[10] - r[9]) * 1000 / frequency for r in rows]
        intervals = [(b[8] - a[8]) * 1000 / frequency for a, b in zip(rows, rows[1:])
                     if b[1] == a[1] + 1]
        profiles.append(dict(owner=owner, revision=revision, frames=len(rows),
            first_frame=rows[0][1], last_frame=rows[-1][1],
            last_offer_to_present_ms=distribution(leads),
            adjacent_frame_offer_interval_ms=distribution(intervals),
            pose_transitions=sum(a[11] != b[11] for a, b in zip(rows, rows[1:])),
            camera_transitions=sum(a[12] != b[12] for a, b in zip(rows, rows[1:])),
            windows_shorter_than_ms={str(x): sum(v < x for v in leads) for x in (8, 12, 14)}))
    # Latest offer of the owners actually observed in each frame. This does NOT
    # establish that no later owner/submodel could appear, or a publication seal.
    windows = [(min(r[10] for r in rows) - max(r[9] for r in rows)) * 1000 / frequency
               for rows in frames.values()]
    return dict(result='SOURCE_WINDOWS_ADJUDICATION_ONLY', source_validation=validation,
        observed_frames=len(frames), qualified_exact_pairs=len(exact), owners=profiles,
        latest_observed_owner_to_first_present_ms=distribution(windows),
        frames_with_multiple_camera_hashes=sum(len({r[12] for r in rows}) > 1 for rows in frames.values()),
        observed_owner_counts={str(n): sum(len(rows) == n for rows in frames.values())
                               for n in sorted({len(rows) for rows in frames.values()})},
        scope='Exact frame/owner/revision only. Thresholds are descriptive, not predicted success rates. '
              'Separate offline renderer costs are not simultaneous GPU contention evidence. '
              'First/last offers and matching callbacks do not prove complete frame sealing.')


def analyze(folder):
    folder = Path(folder).resolve()
    folder.relative_to(ROOT / 'artifacts/remix-runtime/runs')
    path = folder / 'D3D9-SOURCE-TIMING-001.bin'
    if path.stat().st_size > STORE_BYTES:
        raise ValueError('Source timing byte cap')
    manifest = json.loads((folder / 'manifest.json').read_text())
    result = json.loads((folder / 'result.json').read_text())
    if manifest.get('probe') != 'D3D9-SOURCE-TIMING-001' or result.get('probe') != manifest['probe']:
        raise ValueError('Source timing probe required')
    report = assess(path.read_bytes(), manifest['semantic_calibration']['scene_session'], result['target_pid'])
    (folder / 'source-lead.adjudication.json').write_text(json.dumps(report, indent=2))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('folder', type=Path)
    args = parser.parse_args()
    print(json.dumps(analyze(args.folder), indent=2))
