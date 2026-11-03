"""Bounded, offline analysis of opt-in native startup measurements."""
from pathlib import Path
import re

ROW=re.compile(r'^STARTUP_PROFILE stage=(\w+) index=(\d+) qpc=(\d+) frequency=(\d+) private_bytes=(\d+) working_set=(\d+) system_commit=(\d+) commit_limit=(\d+)$',re.M)
COST=re.compile(r'^STARTUP_PROFILE_COST stage=(\w+) index=(\d+) process_query_ticks=(\d+) system_query_ticks=(\d+) frequency=(\d+)$',re.M)

def analyze_text(text):
    rows=[dict(stage=m[0],index=int(m[1]),qpc=int(m[2]),frequency=int(m[3]),private_bytes=int(m[4]),working_set=int(m[5]),system_commit=int(m[6]),commit_limit=int(m[7])) for m in ROW.findall(text)]
    if not rows or len(rows)>128:raise ValueError('Missing or unbounded startup profile')
    frequency=rows[0]['frequency']
    if not frequency or any(r['frequency']!=frequency for r in rows) or any(b['qpc']<a['qpc'] for a,b in zip(rows,rows[1:])):raise ValueError('Startup profile clock')
    def point(stage,index=0):
        found=[r for r in rows if (r['stage'],r['index'])==(stage,index)]
        if len(found)!=1:raise ValueError('Missing/duplicate startup phase: '+stage)
        return found[0]
    def seconds(a,b):return (b['qpc']-a['qpc'])/frequency
    early=any(r['stage']=='receiver_activated' for r in rows)
    stages=('activated','receiver_activated','scene_loaded','materials_enabled','renderer_assets_started','frame_begin') if early else ('activated','scene_loaded','materials_enabled','receiver_started','renderer_assets_started','frame_begin')
    phases=[dict(begin=a,end=b,seconds=seconds(point(a),point(b))) for a,b in zip(stages,stages[1:])]
    boot=[]
    for r in rows:
        if r['stage']!='bootstrap_begin':continue
        i=r['index'];draw=point('bootstrap_drawn',i);end=point('bootstrap_presented',i)
        boot.append(dict(index=i,draw_seconds=seconds(r,draw),present_seconds=seconds(draw,end)))
    if not boot or [r['index'] for r in boot]!=list(range(len(boot))):raise ValueError('Bootstrap sequence')
    warm=any(r['stage']=='render_warm_begin' for r in rows)
    cohort=any(r['stage']=='cohort_draw_begin' for r in rows)
    costs=[]
    for label,index,process,system,freq in COST.findall(text):
        if int(freq)!=frequency:raise ValueError('Startup cost clock')
        point(label,int(index))
        costs.append(dict(stage=label,index=int(index),process_query_seconds=int(process)/frequency,system_query_seconds=int(system)/frequency))
    if costs and (len(costs)!=len(rows) or len({(c['stage'],c['index']) for c in costs})!=len(rows)):raise ValueError('Startup cost coverage')
    narrow=('peer_start_begin','peer_guid_ready','peer_security_ready','peer_mapping_created','peer_events_created','peer_mapping_initialized','peer_process_begin','peer_process_created','peer_passive_ready','peer_start_complete','receiver_started') if early else ('materials_enabled','scene_packet_read_begin','scene_packet_read_complete','scene_packet_hash_complete','peer_start_begin','peer_guid_ready','peer_security_ready','peer_mapping_created','peer_events_created','peer_mapping_initialized','peer_process_begin','peer_process_created','peer_start_complete','receiver_started')
    receiver_phases=[]
    if any(r['stage']=='peer_start_begin' for r in rows):
        receiver_phases=[dict(begin=a,end=b,seconds=seconds(point(a),point(b))) for a,b in zip(narrow,narrow[1:])]
    return dict(points=len(rows),frequency=frequency,phases=phases,bootstrap=boot,
                experimental_render_warm_seconds=seconds(point('render_warm_begin'),point('render_warm_complete')) if warm else None,
                first_cohort_draw_present_seconds=seconds(point('cohort_draw_begin'),point('cohort_draw_end')) if cohort else None,
                first_cohort_copy_seconds=seconds(point('cohort_draw_end'),point('cohort_output_complete')) if cohort else None,
                first_cohort_ack_seconds=seconds(point('cohort_output_complete'),point('cohort_receiver_ack')) if cohort else None,
                activation_to_bootstrap_output_seconds=seconds(point('activated'),point('output_complete')),
                bootstrap_total_wall_seconds=seconds(point('bootstrap_begin'),point('bootstrap_presented',len(boot)-1)),
                first_receiver_ack_seconds=seconds(point('output_complete'),point('receiver_ack')),
                memory_samples=[r for r in rows if r['private_bytes']],diagnostic_costs=costs,receiver_phases=receiver_phases,
                early_passive_receiver=early,
                receiver_creation_seconds=seconds(point('peer_process_begin'),point('peer_process_created')) if any(r['stage']=='peer_process_begin' for r in rows) else None,
                receiver_ready_before_activation_seconds=seconds(point('receiver_started'),point('activated')) if early else None,
                scope='External host startup only;not first matching game composition or physical display latency')

def analyze(folder):
    path=Path(folder)/'gpu/job-console.log'
    if path.stat().st_size>2*1024*1024:raise ValueError('Startup analysis console cap')
    return analyze_text(path.read_text(errors='replace'))
