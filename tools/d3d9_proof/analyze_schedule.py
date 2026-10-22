"""Offline helper schedule costs,not game frame times or a CDD performance claim."""
import argparse
import csv
import json
from pathlib import Path
import numpy as np
from run_offline import ROOT,digest


def assess(rows,count):
    if count not in (120,300) or len(rows)!=count:raise ValueError('Schedule row bound')
    for i,r in enumerate(rows):
        if r['sequence']!=i+1 or r['presents']!=(24 if i==0 else 1) or not r['source_frame']:raise ValueError('Schedule sequence/presents')
        if any(r[k]<0 for k in ('draw_present_us','output_gpu_us','local_readback_us','peer_us')):raise ValueError('Negative stage time')
        if i and (r['scheduled_us']!=(i-1)*1000000//60 or r['completed_us']<r['scheduled_us']):raise ValueError('Schedule clock')
    steady=rows[1:]
    def quantile(values):return {k:float(x) for k,x in zip(('p50','p95','max'),np.quantile(values,[.5,.95,1]))}
    costs=[r['completed_us']-r['scheduled_us'] for r in steady]
    return dict(frames=count,steady_frames=count-1,demand_hz=60,deadline_us=1000000/60,
        deadline_misses=sum(x>1000000/60 for x in costs),completion_from_due_us=quantile(costs),
        stages_us={k:quantile([r[k] for r in steady]) for k in ('draw_present_us','output_gpu_us','local_readback_us','peer_us')},
        scope='synthetic60Hz demand cycling actual captured snapshots;includes diagnostic stalls;not original-rate replay,live SFC latency or CDD KPP3 qualification')


def analyze(folder):
    folder=Path(folder).resolve();folder.relative_to(ROOT/'artifacts/d3d9-intercept/direct64-runs')
    meta=json.loads((folder/'result.json').read_text())
    path=folder/'frame-timing.csv'
    if path.stat().st_size>128*1024:raise ValueError('Timing byte cap')
    with path.open() as f:rows=[{k:int(v) for k,v in r.items()} for r in csv.DictReader(f)]
    report=assess(rows,meta.get('paced_frames',0));report['timing_sha256']=digest(path)
    report['result']='OFFLINE_SCHEDULE_MET' if not report['deadline_misses'] else 'OFFLINE_SCHEDULE_MISSES_REVIEW'
    (folder/'schedule-analysis.json').write_text(json.dumps(report,indent=2));return report


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('folder',type=Path);args=parser.parse_args();print(json.dumps(analyze(args.folder),indent=2))
