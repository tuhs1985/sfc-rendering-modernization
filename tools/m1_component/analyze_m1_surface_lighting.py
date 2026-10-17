"""Adjudicate bounded sustained surface diagnostic; visual attestation still required."""
import argparse
import json
from pathlib import Path

def analyze(summary):
    d=summary['surface_lighting'];issues=[]
    if not d['enabled'] or not d['attempted'] or not d['started'] or d['failure']:
        issues.append('surface_test_not_activated_or_aborted')
    if not d['intact'] or not d['pinned_until_exit']:issues.append('immutable_graph_integrity_or_lifetime_missing')
    if not 1<=d['count']<=512 or d['changed_vectors']<1 or not 0<d['storage_bytes']<=1048576:
        issues.append('full_mesh_or_budget_not_qualified')
    if (d['marker_ms'],d['normal_gap_ms'],d['altered_ms'])!=(20000,5000,15000):
        issues.append('approved_schedule_changed')
    if any(not d[k] for k in ('owner','thread','ship','visual','model','source','manager','original_list')):
        issues.append('selected_identity_missing')
    if not d['neutral_list'] or not d['altered_list'] or len({d[k] for k in ('original_list','neutral_list','altered_list')})!=3:
        issues.append('private_graphs_not_distinct')
    phases=d['phases']
    if len(phases)!=4:issues.append('phase_records_missing')
    else:
        for i,p in enumerate(phases):
            if p['phase']!=i or not p['observed']:issues.append(f'phase_{i}_not_observed')
            low,high=((0,20000),(20000,25000),(25000,40000),(40000,90000))[i]
            if not low<=p['first_ms']<=p['last_ms']<high:issues.append(f'phase_{i}_timing_invalid')
            if i<3 and (not p['applied'] or p['parent']!=p['applied']):issues.append(f'phase_{i}_application_or_parent_missing')
            if i in (1,2) and (p['applied']<2 or p['received']<p['applied']):issues.append(f'phase_{i}_repeated_receipt_missing')
        if phases[0]['last_ms']<19500:issues.append('marker_not_sustained_for_twenty_seconds')
        if phases[1]['last_ms']-phases[1]['first_ms']<4000 or phases[2]['last_ms']-phases[2]['first_ms']<14000:
            issues.append('continuous_windows_not_sustained')
        if abs(sum(p['applied'] for p in phases[1:3])-sum(p['observed'] for p in phases[1:3]))>2:
            issues.append('eligible_calls_not_continuously_overridden')
        if phases[3]['applied']:issues.append('override_persisted_after_restore')
    if not summary['hooks_restored']:issues.append('hooks_not_restored')
    tint=summary['visual_tint']
    if tint['restore_failed'] or tint['active_scopes']:issues.append('source_marker_lease_not_clean')
    return dict(probe_id='M1-C01-RT-010',issues=issues,
                status='LEAD_REVIEW_REQUIRED' if not issues else 'ADDITIONAL_BOUNDED_EVIDENCE_REQUIRED',
                surface_lighting=d,visual_effect='SPONSOR_ATTESTATION_REQUIRED',formal_m1='CONTINUES',
                quality_improvement_proven=False,recyclable_buffer_lifetime_proven=False)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('run_dir',type=Path)
    args=parser.parse_args();path=args.run_dir/'M1-A-summary.json'
    if path.stat().st_size>1048576:parser.error('Summary exceeds1MiB')
    try:result=analyze(json.loads(path.read_text(encoding='utf-8-sig')))
    except (KeyError,TypeError,ValueError) as error:parser.error(str(error))
    (args.run_dir/'M1-surface-lighting-analysis.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','issues')}))
if __name__=='__main__':main()
