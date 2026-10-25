"""Explicit actual-proxy evidence admission;never certifies ordinary-D3D9 rendering."""
import argparse,json,re
from pathlib import Path
from run_survey import ROOT,locks
from survey_capture import analyze,digest

def check(folder,duration):
    folder=Path(folder).resolve();folder.relative_to(ROOT/'artifacts/remix-runtime/runs')
    result=json.loads((folder/'result.json').read_text());log=(folder/'fixture.log').read_text();report=analyze(folder/'broad.bin')
    if result['error'] or result['host_exit'] or result['fixture_exit']:raise ValueError('Fixture exit failed')
    if not re.search(r'BROAD_END .*state_errors=0 status=3 drops=0 resized=1 recreated=1',log):raise ValueError('Graphics state/resize/cleanup incomplete')
    if report['result']!='METADATA_COMPLETE_SEMANTIC_CLASSIFICATION_PENDING' or report['header']['durationMs']!=duration*1000:raise ValueError('Capture bounds/drop/adjudication incomplete')
    if report['header']['pid']<=0:raise ValueError('Unknown source process')
    for key in ('resource','view','targets','descriptors','pipeline_desc','origin','origin_stats'):
        if not report['counts'].get(key):raise ValueError('Missing observed callback: '+key)
    if not report['origin_stats'].get('captured') or not report['module_ranges']:raise ValueError('No call-origin evidence')
    if report['analysis_overflow']:raise ValueError('Analysis overflow')
    cleanup=json.loads((folder/'broad.bin.native.json').read_text())
    if not cleanup.get('installed') or not cleanup.get('restored') or any(cleanup.get(k) for k in ('error','faults','busy','census_overflow')):raise ValueError('Native observation cleanup/state incomplete')
    if report['native']['lights']['stats'].get('complete_records',0)<4 or len(report['native']['effect_types'])!=2:raise ValueError('Native light/census fixture coverage missing')
    native=result['source_files']
    for name in ('SFCRemixReturn.dll','d3d11_return_fixture.exe'):
        if native[name]!=digest(ROOT/'artifacts/render-survey/bin'/name):raise ValueError('Fixture used different observer/native test')
    return dict(path=str(folder.relative_to(ROOT)),result_sha256=digest(folder/'result.json'),trace_sha256=digest(folder/'broad.bin'),records=report['header']['written'],bytes=report['bytes'],counts=report['counts'],origin_stats=report['origin_stats'],families=len(report['families']),duration_seconds=duration)

def main():
    p=argparse.ArgumentParser();p.add_argument('current_fixture',type=Path);p.add_argument('endurance_fixture',type=Path);a=p.parse_args()
    for folder in (a.current_fixture,a.endurance_fixture):
        control=json.loads((folder/'survey-control.json').read_text())
        if control['locks']!=locks():raise ValueError('Current exact-source provenance stale')
    short=check(a.current_fixture,10);long=check(a.endurance_fixture,90)
    q=dict(result='OFFLINE_SURVEY_EVENTS_STATE_CLEANUP_PASS',locks=locks(),fixtures=[short,long],limitations=['Not SFC gameplay','Origins sampled;module range is not gameplay owner','No effect type inferred from state','No resource payload','Deferred command replay/descriptor table resolution unsupported'])
    out=ROOT/'artifacts/render-survey/qualification.json';out.write_text(json.dumps(q,indent=2));print(q['result'])

if __name__=='__main__':main()
