"""Validate one-use or bounded fresh-copy evidence; gameplay attestation required."""
import argparse
import json
from pathlib import Path

def analyze(summary):
    d=summary['private_copy']
    if d['enabled'] is not True:raise ValueError('Private-copy test not enabled')
    issues=[]
    if d['applied']!=1 or not d['attempted'] or d['failure']:issues.append('single_handoff_not_confirmed')
    if d['consumed']<1:issues.append('copied_list_not_observed_in_preparation')
    if d['parent_return']!=1:issues.append('parent_return_not_observed')
    if not d['intact'] or d['before_hash']!=d['after_hash']:issues.append('copied_payload_or_canary_changed')
    if not d['pinned_until_exit']:issues.append('pinning_policy_missing')
    if not 20000<=d['elapsed_ms']<=90000:issues.append('handoff_outside_capture_window')
    if not 1<=d['count']<=1024 or not 1<=d['copied_polygons']<=64 or not 0<d['payload_bytes']<=20224:
        issues.append('copy_budget_or_count_invalid')
    if not 0<d['slot_bytes']<=22528:issues.append('slot_budget_exceeded')
    if any(not d[key] for key in ('owner','thread','ship','visual','model','source','manager','original_list','copy_list')):
        issues.append('missing_identity')
    if d['copy_list']==d['original_list']:issues.append('no_private_list')
    if not summary['hooks_restored']:issues.append('hooks_not_restored')
    repeated=summary.get('repeated_private_copy',{})
    repeat_enabled=repeated.get('enabled') is True
    epoch_enabled=repeated.get('epoch_requalification_enabled') is True
    if epoch_enabled and not repeat_enabled:issues.append('epoch_mode_without_repeated_mode')
    if repeat_enabled:
        records=repeated['records']
        if (repeated['limit']!=32 or repeated['interval_ms']!=1000 or
            repeated['attempts']!=len(records) or len(records)!=32):
            issues.append('repeat_count_or_limits_not_confirmed')
        if not 0<repeated['storage_bytes']<=716800:issues.append('copy_bank_budget_exceeded')
        if repeated['halted'] or repeated['receipt_mismatch']:issues.append('repeat_halted_or_receipt_mismatch')
        pointers=set()
        previous=None
        previous_frame=0
        for i,r in enumerate(records):
            if r['slot']!=i or r['applied']!=1 or r['consumed']<1 or r['parent_return']!=1 or r['failure']:
                issues.append(f'slot_{i}_handoff_incomplete')
            if not r['intact'] or r['before_hash']!=r['after_hash']:issues.append(f'slot_{i}_changed')
            if not 20000<=r['elapsed_ms']<=90000 or (previous is not None and r['elapsed_ms']-previous<1000):
                issues.append(f'slot_{i}_timing_invalid')
            previous=r['elapsed_ms']
            if r['frame']<=previous_frame:issues.append(f'slot_{i}_not_a_new_frame')
            previous_frame=r['frame']
            if not r['copy_list'] or r['copy_list']==d['original_list'] or r['copy_list'] in pointers:
                issues.append(f'slot_{i}_not_fresh')
            pointers.add(r['copy_list'])
            if (r['count']!=d['count'] or r['copied_polygons']!=min(64,r['count']) or
                not 0<r['payload_bytes']<=20224):issues.append(f'slot_{i}_budget_or_shape_invalid')
        if records and any(records[0][k]!=d[k] for k in ('elapsed_ms','copy_list','count','before_hash','after_hash')):
            issues.append('first_slot_summary_mismatch')
        if epoch_enabled:
            transitions=0;previous_owner=d['owner'];seen_owners={previous_owner}
            for i,r in enumerate(records):
                changed=r['owner']!=previous_owner
                if not r['owner']:issues.append(f'slot_{i}_missing_owner')
                if changed:
                    transitions+=1
                    if not i or r['owner'] in seen_owners or r['requalified_from']!=previous_owner:
                        issues.append(f'slot_{i}_invalid_epoch_transition')
                    if (not r['retired_ms'] or not r['retired_frame'] or
                        (i and (r['retired_ms']<records[i-1]['elapsed_ms'] or r['retired_frame']<=records[i-1]['frame'])) or
                        not r['retired_ms']<=r['qualification_ms']<=r['elapsed_ms']-250 or
                        not r['retired_frame']<=r['qualification_frame']<r['frame'] or
                        not 3<=r['qualification_frames']<=r['frame']-r['qualification_frame']+1):
                        issues.append(f'slot_{i}_epoch_qualification_not_proven')
                    seen_owners.add(r['owner'])
                elif any(r[k] for k in ('requalified_from','retired_ms','retired_frame',
                                        'qualification_ms','qualification_frame','qualification_frames')):
                    issues.append(f'slot_{i}_spurious_requalification')
                previous_owner=r['owner']
            if (not 1<=transitions<=2 or repeated['epoch_requalifications']!=transitions or
                repeated['epoch_limit']!=2):issues.append('fresh_epoch_not_demonstrated_within_limit')
    return dict(probe_id='M1-C01-RT-009' if epoch_enabled else ('M1-C01-RT-008' if repeat_enabled else 'M1-C01-RT-007'),status='LEAD_REVIEW_REQUIRED' if not issues else 'ADDITIONAL_BOUNDED_EVIDENCE_REQUIRED',
                issues=issues,private_copy=d,visible_behavior='SPONSOR_ATTESTATION_REQUIRED',
                repeated_private_copy=repeated if repeat_enabled else None,
                reusable_buffer_lifetime_qualified=False,formal_m1='CONTINUES')

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('run_dir',type=Path)
    args=parser.parse_args();path=args.run_dir/'M1-A-summary.json'
    if path.stat().st_size>1024*1024:parser.error('Summary exceeds 1 MiB')
    try:result=analyze(json.loads(path.read_text(encoding='utf-8-sig')))
    except (KeyError,TypeError,ValueError) as error:parser.error(str(error))
    (args.run_dir/'M1-private-copy-analysis.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','issues')}))

if __name__=='__main__':main()
