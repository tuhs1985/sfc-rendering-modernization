"""Review bounded polygon-wrapper provenance; never qualify pointer lifetime automatically."""
import argparse
import json
from pathlib import Path

def analyze(summary):
    d=summary['wrapper_observation']
    if d['schema']!='m1.wrapper.v1' or d['enabled'] is not True:
        raise ValueError('Wrapper observation unavailable')
    total,counts,samples=d['total'],d['outcomes'],d['samples']
    if len(counts)!=8 or any(type(v) is not int or v<0 for v in counts) or counts[0]:
        raise ValueError('Invalid outcome counters')
    if (type(total) is not int or total<0 or sum(counts)!=total or len(samples)!=min(64,total)
        or d['example_omitted']!=max(0,total-64)):
        raise ValueError('Wrapper count/capacity mismatch')
    if type(d['parent_closed']) is not int or not 0<=d['parent_closed']<=counts[1]+counts[2]:
        raise ValueError('Invalid parent-return counters')
    for s in samples:
        if (len(s)!=15 or any(type(v) is not int or not 0<=v<=0xffffffff for v in s)
            or s[1] not in (0,1) or s[2] not in range(1,8)):
            raise ValueError('Invalid wrapper sample')
        if s[2] in (1,2) and (not s[5] or not s[8] or s[10]!=s[13] or s[11]!=s[14] or s[12]!=1
                              or s[4]!=(0x0042e55d if s[2]==1 else 0x0042e626)):
            raise ValueError('Invalid accepted provenance')
    issues=[]
    if not counts[1]:issues.append('no_primary_provenance')
    if d['parent_closed']!=counts[1]+counts[2]:issues.append('some_parent_returns_unobserved')
    if any(counts[4:]):issues.append('manager_or_call_provenance_requires_review')
    return dict(probe_id='M1-C01-RT-006',status='LEAD_REVIEW_REQUIRED',issues=issues,
        primary=counts[1],secondary=counts[2],unscoped=counts[3],outcomes=counts,
        samples=samples,parent_closed=d['parent_closed'],example_omitted=d['example_omitted'],
        substitution_enabled=bool(summary.get('private_copy',{}).get('enabled',False)),wrapper_return_directly_observed=False,
        pointer_nonretention_proven=False)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('run_dir',type=Path)
    args=parser.parse_args();path=args.run_dir/'M1-A-summary.json'
    if path.stat().st_size>1024*1024:parser.error('Summary exceeds 1 MiB')
    try: result=analyze(json.loads(path.read_text(encoding='utf-8-sig')))
    except (KeyError,TypeError,ValueError) as error:parser.error(str(error))
    if summary_path := (args.run_dir/'run-metadata.json'):
        if summary_path.exists():
            if summary_path.stat().st_size>65536:parser.error('Metadata exceeds 64 KiB')
            probe=json.loads(summary_path.read_text(encoding='utf-8-sig')).get('probe_id')
            if probe in ('M1-C01-RT-006','M1-C01-RT-007','M1-C01-RT-008','M1-C01-RT-009','M1-C01-RT-010'):result['probe_id']=probe
    (args.run_dir/'M1-wrapper-analysis.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','primary','secondary','issues')}))

if __name__=='__main__':main()
