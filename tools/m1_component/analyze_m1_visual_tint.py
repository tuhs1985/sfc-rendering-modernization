"""Adjudicate instrumentation only; visible tint requires sponsor evidence."""

import argparse
import csv
import json
from pathlib import Path


def analyze(run_dir: Path) -> dict:
    summary = json.loads((run_dir / 'M1-A-summary.json').read_text(encoding='utf-8-sig'))
    with (run_dir / 'M1-A-events.csv').open(newline='', encoding='utf-8-sig') as handle:
        rows = list(csv.DictReader(handle))
    tint = summary['visual_tint']
    target = tint['target_owner_id']
    applied = [r for r in rows if int(r.get('tint_applied', '0'))]
    model_rows = [r for r in rows if r['event'] == 'model0' and int(r['owner_id'])]
    owners = sorted({int(r['owner_id']) for r in model_rows})
    reasons = []
    if not tint['enabled'] or summary['geometry_hook_enabled']:
        reasons.append('Wrong component configuration')
    if not target or not applied or tint['applied'] != len(applied):
        reasons.append('Applied substitutions are absent or not fully recorded')
    if any(r['event'] != 'model0' or int(r['owner_id']) != target or
           int(r['return_address'], 0) != 0x0042FDD5 or
           int(r['model0_vtable'], 0) != 0x007983E8 or
           int(r['visual_vtable'], 0) != 0x007985A4 or
           not int(r['ship'], 0) or not int(r['source'], 0) or
           not int(r['effective_source'], 0) or
           int(r['effective_source'], 0) == int(r['source'], 0) or
           not 1 <= int(r['tint_entries']) <= 256 or
           not tint['delay_ms'] <= int(r['tint_elapsed_ms']) <
               tint['delay_ms'] + tint['duration_ms'] for r in applied):
        reasons.append('Substitution targeting, source bounds, or phase is invalid')
    if tint['applied'] != tint['restored'] + tint['renderer_replaced'] or \
            tint['active_scopes'] or tint['restore_failed'] or tint['rejected'] or \
            tint.get('thread_mismatch', 0):
        reasons.append('Source release or fail-open rejection requires review')
    if len(owners) < 2:
        reasons.append('Two distinguishable mainline owners were not retained')
    end = tint['delay_ms'] + tint['duration_ms']
    baseline = sum(int(r['owner_id']) == target and
                   int(r['elapsed_ms']) < tint['delay_ms'] and
                   not int(r.get('tint_applied', '0')) for r in model_rows)
    returned = sum(int(r['owner_id']) == target and int(r['elapsed_ms']) >= end and
                   not int(r.get('tint_applied', '0')) for r in model_rows)
    if not baseline or not returned:
        reasons.append('Same target owner lacks before/after original-source evidence')
    controller = (run_dir / 'controller.stdout.txt').read_text(encoding='utf-8-sig')
    if not summary['hooks_restored'] or 'hook_bytes_restored=true' not in controller:
        reasons.append('Hook restoration was not verified')
    if summary['log_truncated'] or summary['event_log_bytes'] > 32 * 1024 * 1024:
        reasons.append('Capture bound failed')
    if summary['rejected_semantics'] or summary['owner_overflow'] or summary['thread_overflow']:
        reasons.append('Semantic identity or capacity failure')
    return {
        'result': 'TARGETED_TINT_INSTRUMENTATION_COHERENT' if not reasons else 'REVIEW_REQUIRED',
        'review_reasons': reasons,
        'target_owner_id': target,
        'observed_owner_ids': owners,
        'substitutions': tint['applied'],
        'restored': tint['restored'],
        'renderer_replaced': tint['renderer_replaced'],
        'baseline_target_events': baseline,
        'returned_target_events': returned,
        'original_sample_rgb': sorted({r['tint_original_rgb'] for r in applied}),
        'visible_effect': 'UNADJUDICATED — requires sponsor on/off and other-owner observation',
        'milestone': 'M1 CONTINUES; no formal TRL 4 determination',
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('run_dir', type=Path)
    directory = parser.parse_args().run_dir
    result = analyze(directory)
    (directory / 'M1-B-tint-analysis.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
