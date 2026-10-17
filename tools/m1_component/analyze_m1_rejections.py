"""Validate bounded observer exclusions; never infer harmlessness."""
import argparse
import json
from pathlib import Path

REASONS = ('reserved','ship_unreadable','ship_vtable','ship_visual_unreadable',
           'visual_unreadable','visual_vtable','association','model_caller',
           'model_unreadable','model_vtable','model_visual_unreadable',
           'model_visual_vtable','owner_missing')

def analyze(summary):
    d = summary['rejection_diagnostics']
    if d['schema'] != 'm1.rejections.v1':
        raise ValueError('Unsupported schema')
    counts = d['counts']
    if len(counts) != 4 or any(len(phase) != 4 or any(len(row)!=13 for row in phase) for phase in counts):
        raise ValueError('Invalid phase/reason table')
    values = [d['total'],d['signature_overflow'],d['example_omitted']]
    values += [v for phase in counts for row in phase for v in row]
    if (any(type(v) is not int or v < 0 for v in values)
        or any(row[0] for phase in counts for row in phase) or any(sum(phase[0]) for phase in counts)):
        raise ValueError('Invalid counters')
    total = d['total']
    if sum(sum(row) for phase in counts for row in phase) != total or total != summary['rejected_semantics']:
        raise ValueError('Aggregate reconciliation failed')
    buckets, examples = d['buckets'],d['examples']
    if len(buckets) > 32 or len(examples) != min(64,total):
        raise ValueError('Capacity violated')
    if d['example_omitted'] != max(0,total-64):
        raise ValueError('Example omission mismatch')
    samples = examples + [s for b in buckets for s in (b['first'],b['last'])]
    for s in samples:
        if (len(s)!=16 or any(type(v) is not int or not 0<=v<=0xffffffff for v in s)
            or s[0]>3 or s[2] not in (1,2,3) or not 1<=s[3]<=12 or s[14]>3 or s[15]>3):
            raise ValueError('Invalid example')
    if any(type(b['count']) is not int or b['count']<=0 for b in buckets):
        raise ValueError('Invalid bucket count')
    if sum(b['count'] for b in buckets)+d['signature_overflow']!=total:
        raise ValueError('Signature reconciliation failed')
    issues=[]
    if d['signature_overflow']: issues.append('signature_capacity_exceeded')
    if any(s[14] or s[15] for s in samples):
        issues.append('selected_address_related_exclusion_requires_review')
    return dict(probe_id='M1-C01-RT-005',status='LEAD_REVIEW_REQUIRED',total=total,
                counts_by_requested_phase=counts,reason_names=REASONS,
                signature_overflow=d['signature_overflow'],example_omitted=d['example_omitted'],
                issues=issues,harmless_exception_confirmed=False,buckets=buckets,examples=examples)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_dir',type=Path)
    args=parser.parse_args()
    path=args.run_dir/'M1-A-summary.json'
    if path.stat().st_size>1024*1024: parser.error('Summary exceeds 1 MiB safeguard')
    try: result=analyze(json.loads(path.read_text(encoding='utf-8-sig')))
    except (KeyError,TypeError,ValueError) as error: parser.error(str(error))
    metadata=args.run_dir/'run-metadata.json'
    if metadata.exists():
        if metadata.stat().st_size>65536:parser.error('Metadata exceeds 64 KiB')
        try: probe=json.loads(metadata.read_text(encoding='utf-8-sig')).get('probe_id')
        except (TypeError,ValueError) as error:parser.error(str(error))
        if probe in ('M1-C01-RT-005','M1-C01-RT-006','M1-C01-RT-007','M1-C01-RT-008','M1-C01-RT-009','M1-C01-RT-010','M1-CLOSE-ENDURE-001'):result['probe_id']=probe
    (args.run_dir/'M1-rejection-analysis.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','total','issues')}))

if __name__=='__main__': main()
