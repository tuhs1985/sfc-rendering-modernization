"""Offline deadline attribution;no runtime changes or physical-display claims."""
import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/remix_runtime'))
from live_owner_timing import parse_audits
from source_timing import HEADER,RECORD,decode
from analyze_source_lead import distribution


def assess(audits,inputs,timings,sources,frequency):
    by_sequence={r['sequence']:r for r in inputs}
    # CSV sequence is loop index,not output sequence:light omissions skip outputs.
    # Join on source frame;repeated frames remain explicitly unjoined.
    by_output={}
    for r in timings:by_output.setdefault(r['source_frame'],[]).append(r)
    camera={};previous={}
    for r in sorted((r for r in sources if r[0]==1),key=lambda r:r[10]):
        key=(r[3],r[4]);prior=previous.get(key)
        camera[(r[1],*key)]=None if prior is None or prior[1]+1!=r[1] else r[12]!=prior[12]
        previous[key]=r
    groups={};causes=Counter();gpu_bounds=Counter();camera_groups=Counter();streaks=[];streak=0;last_frame=None
    first_match=next((a['frame'] for a in audits if a['status']==1),None)
    steady=Counter()
    for a in audits:
        if a['status'] not in (1,2,3,4,6):continue
        matched=a['status']==1
        if first_match is not None and a['frame']>=first_match:steady['matched' if matched else 'missed']+=1
        if not matched:
            if last_frame is None or a['frame']==last_frame+1:streak+=1
            else:
                if streak:streaks.append(streak)
                streak=1
        else:
            if streak:streaks.append(streak)
            streak=0
        last_frame=a['frame']
        c=camera.get((a['frame'],a['owner'],a['revision']))
        camera_groups[(str(c),'matched' if matched else 'missed')]+=1
        r=by_sequence.get(a['input_sequence'])
        if r is None:
            if not matched:causes['no_retained_output_for_expected_source']+=1
            continue
        if (r['source_frame'],r['owner'],r['revision'])!=(a['frame'],a['owner'],a['revision']):
            raise ValueError('Expected source identity differs')
        if not 0<r['offered_qpc']<=r['taken_qpc']<=r['light_ready_qpc']<=r['completed_qpc']:
            raise ValueError('Invalid timing order')
        if r['frequency']!=frequency:raise ValueError('Mixed QPC frequency')
        if not matched:
            if r['completed_qpc']<=a['present']:
                causes['completed_by_observer_but_not_matched']+=1
            elif r['taken_qpc']>=a['present']:
                causes['not_taken_until_after_observer']+=1
            elif r['light_ready_qpc']>=a['present']:
                causes['light_stage_crossed_observer']+=1
            else:causes['render_or_transfer_crossed_observer']+=1
        label='matched' if matched else 'missed'
        g=groups.setdefault(label,{})
        def add(name,value):g.setdefault(name,[]).append(value)
        ms=lambda value:value*1000/frequency
        add('source_to_observer_ms',ms(a['present']-r['offered_qpc']))
        add('queue_ms',ms(r['taken_qpc']-r['offered_qpc']))
        add('light_ms',ms(r['light_ready_qpc']-r['taken_qpc']))
        add('end_to_end_ms',ms(r['completed_qpc']-r['offered_qpc']))
        add('completion_margin_ms',ms(a['present']-r['completed_qpc']))
        candidates=by_output.get(a['frame'],[])
        t=candidates[0] if len(candidates)==1 else None
        if t:
            if t['source_frame']!=a['frame']:raise ValueError('Output identity differs')
            if not matched:
                # peer_us is floored to microseconds. One-us upper bound avoids
                # falsely attributing a final ACK delay to unfinished rendering.
                peer_start_lower=r['completed_qpc']-(t['peer_us']+1)*frequency/1_000_000
                gpu_bounds['pre_peer_work_definitely_late' if peer_start_lower>a['present']
                           else 'transfer_publication_or_ack_boundary_unresolved']+=1
            for name in ('draw_present_us','output_gpu_us','peer_us','copy_submit_us','render_ready_wait_us','postprocess_us'):
                add(name.replace('_us','_ms'),t[name]/1000)
    if streak:streaks.append(streak)
    return dict(result='OFFLINE_DELIVERY_ATTRIBUTION',audit_status_counts=dict(Counter(str(a['status']) for a in audits)),
                miss_attribution=dict(causes),camera_hash_change_counts={f'{k[0]}_{k[1]}':v for k,v in camera_groups.items()},
                missed_output_deadline_bounds=dict(gpu_bounds),first_matched_frame=first_match,
                after_first_match_counts=dict(steady),
                missed_frame_streaks=dict(Counter(str(n) for n in streaks)),
                timing={label:{name:distribution(values) for name,values in g.items()} for label,g in groups.items()},
                caveats=['Observer receipts and compositor draws occur at different callbacks;not interchangeable counts.',
                         'Completion timestamp is after peer acknowledgement;GPU pool may become ready slightly earlier.',
                         'Camera hashes reveal changed state,not rotation speed or user input.',
                         'No stale-image hold,buffering,renderer change or physical-display measurement.'])


def analyze(folder):
    folder=Path(folder).resolve();folder.relative_to(ROOT/'artifacts/remix-runtime/runs')
    m=json.loads((folder/'manifest.json').read_text());result=json.loads((folder/'result.json').read_text())
    session=m['semantic_calibration']['scene_session'];pid=result['target_pid']
    raw=(folder/'D3D9-SOURCE-TIMING-001.bin').read_bytes();validation=decode(raw,session,pid)
    _,audits=parse_audits((folder/'D3D9-LIVE-TIMING-001.bin').read_bytes(),session,pid)
    def rows(name):
        with (folder/'gpu'/name).open(newline='') as f:
            return [{k:int(v) for k,v in row.items()} for row in csv.DictReader(f)]
    report=assess(audits,rows('live-input.csv'),rows('frame-timing.csv'),list(RECORD.iter_unpack(raw[HEADER.size:])),validation['frequency'])
    report['source']=str(folder.relative_to(ROOT));return report


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('folder',type=Path);args=parser.parse_args()
    print(json.dumps(analyze(args.folder),indent=2))
