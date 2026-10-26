"""Full-interval and material-response evidence for isolated candidate attempts."""
import hashlib
import json
from pathlib import Path
import re
import struct
import sys
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/d3d9_proof'))
from startup_profile import analyze
HERE=ROOT/'artifacts/candidate-hot-reload';RUNS=ROOT/'artifacts/remix-runtime/runs'
ROIS=dict(FCA=(200,730,570,970),RCA=(780,730,1110,970),FDD=(1140,730,1330,970))


def summarize(folder):
    result=json.loads((folder/'result.json').read_text());probe=result['candidate_hot_reload_probe']
    job=folder/'gpu/job-result.json'
    out=dict(run=folder.name,mode=probe['mode'],emission_off=probe.get('diagnostic_emission_override')==0,
        retouch=probe.get('diagnostic_final_retouch',False),retouches=probe.get('retouches',[]),
        disable_preserve=probe.get('diagnostic_disable_preserve',False),
        complete_before_device=probe.get('diagnostic_complete_before_device',False),
        late_emission_off=probe.get('diagnostic_late_emission_off',False),late_edits=probe.get('late_edits',[]),
        flat_library=probe.get('diagnostic_flat_library',False),
        late_asset=probe.get('diagnostic_late_asset',False),
        alias_correction=probe.get('diagnostic_alias_lifetime_correction',False),error=result['error'],
        native_job=json.loads(job.read_text()) if job.is_file() else None,
        fixture_exit=result['fixture_exit'],launches=probe['launches'])
    log=(folder/'gpu/job-console.log').read_text(errors='replace')
    out['effective_startup_options']=[l for l in log.splitlines() if 'rtx.initializer.asyncAssetLoading =' in l]
    out['effective_preserve_options']=[l for l in log.splitlines() if 'rtx.enablePreservePath =' in l]
    out['api_handoff_success_marker']='CANDIDATE_ASYNC_HANDOFF initial_config_sync=1 after_device=1 api_success=1' in log
    out['search_path_log']=[l for l in log.splitlines() if 'asset search path:' in l]
    live=result['live_owner_timing']
    if live:
        m=live['multi_scene'];out.update(state=m['state'],partial=m['partial'],material_master_publications=len(m['material_events']),
            material_events=m['material_events'],asset_timings=m['asset_timings'],draws=m['draws'],output_stages=m['output_stage_timings'])
        try:out['startup']=analyze(folder)
        except ValueError as e:out['startup_error']=str(e)
        fmt=struct.Struct('<8I5Q');raw=(folder/'D3D9-SYNC-BUFFER-001.bin').read_bytes()
        rows=[fmt.unpack_from(raw,i) for i in range(64,len(raw)-fmt.size+1,fmt.size)]
        first=next((i for i,r in enumerate(rows) if r[3]==1),None)
        if first is not None:
            origin=min(j['discovered_ns'] for j in m['preparation']['jobs_summary'])/1e9
            gaps=[];gap=[]
            for r in rows[first:]:
                if r[3]==2:gap.append(r)
                elif gap:gaps.append(gap);gap=[]
            if gap:gaps.append(gap)
            out.update(first_matching_s=rows[first][-1]/1e7-origin,
                post_start_omissions=sum(map(len,gaps)),max_gap_records=max(map(len,gaps),default=0),
                max_gap_span_s=max(((g[-1][-1]-g[0][-1])/1e7 for g in gaps),default=0))
    window=re.search(r'GAME_DELIVERY_WINDOW frames=(\d+) draws=(\d+)',(folder/'fixture.log').read_text())
    out['settled_window']=dict(frames=int(window[1]),draws=int(window[2])) if window else None
    return out


def compare(a,b,first=False):
    images=[RUNS/a/('fixture-ship.bmp' if first else 'fixture-ship-late.bmp'),RUNS/b/'fixture-ship-late.bmp']
    if not all(p.is_file() for p in images):return dict(a=a,b=b,missing_late_image=True)
    left,right=[np.array(Image.open(p).convert('RGB')).astype(np.float32) for p in images]
    results={}
    for name,(x,y,z,w) in ROIS.items():
        aa,bb=left[y:w,x:z],right[y:w,x:z]
        mask=(abs(aa-[8,14,79]).max(2)>3)|(abs(bb-[8,14,79]).max(2)>3)
        diff=abs(aa-bb)
        results[name]=dict(roi=[x,y,z,w],ship_pixels=int(mask.sum()),
            rgb_mean_abs_error=float(diff[mask].mean()),over10=int((diff.max(2)[mask]>10).sum()))
    return dict(a=a,b=b,first_to_late=first,per_model=results,scope='Same fixed synthetic poses;union ship-pixel mask;not a complete material correctness proof')


folders=sorted(p.parent for p in RUNS.glob('20261026-*/candidate-hot-reload-probe.json'))
rows=[summarize(p) for p in folders]
good=[r for r in rows if not r['error']]
full=next(r['run'] for r in good if r['mode']=='async' and not r['emission_off'] and not r['retouch'])
off=next(r['run'] for r in good if r['mode']=='async' and r['emission_off'])
sync=next(r['run'] for r in good if r['mode']=='sync' and not r['emission_off'])
pairs=[(full,off),(full,sync),(off,sync)]
pairs.extend((full,r['run']) for r in good if r['retouch'])
pairs.extend((sync,r['run']) for r in good if r['mode']=='handoff')
pairs.extend((sync,r['run']) for r in good if r['disable_preserve'])
pairs.extend((sync,r['run']) for r in good if r['complete_before_device'])
preserve_full=[r for r in good if r['disable_preserve'] and not r['emission_off']]
preserve_off=[r for r in good if r['disable_preserve'] and r['emission_off']]
if preserve_full and preserve_off:pairs.append((preserve_full[-1]['run'],preserve_off[-1]['run']))
initial_full=[r for r in good if r['complete_before_device'] and not r['emission_off'] and not r['late_emission_off']]
initial_off=[r for r in good if r['complete_before_device'] and r['emission_off']]
if initial_full and initial_off:pairs.append((initial_full[-1]['run'],initial_off[-1]['run']))
flat_full=[r for r in good if r['flat_library'] and not r['emission_off'] and not r['late_asset']]
flat_off=[r for r in good if r['flat_library'] and r['emission_off']]
pairs.extend((sync,r['run']) for r in good if r['flat_library'])
if flat_full and flat_off:pairs.append((flat_full[-1]['run'],flat_off[-1]['run']))
out=dict(scope='Isolated ordinary-D3D9 candidate investigation;not production qualification',runs=rows,
    image_comparisons=[compare(*p) for p in pairs]+[compare(r['run'],r['run'],True) for r in good if r['late_emission_off']],
    missing_controls='A completed handoff full-vs-emission-off comparison is required before claiming handoff material response')
reference=json.loads((ROOT/'artifacts/staging-integration/20261025-220919-119346-return-fixture-archive.json').read_text())
def selected(name):return '/assets/' in name and(name.endswith(('.dds','/mod.usda','/scene.bin')) or '/texture-' in name)
expected={k.split('/gpu/',1)[1]:v['sha256'] for k,v in reference['files'].items() if selected(k)}
content=[]
for row in rows:
    receipt=HERE/(row['run']+'-archive.json')
    if not receipt.is_file():continue
    saved=json.loads(receipt.read_text())
    got={k.split('/gpu/',1)[1]:v['sha256'] for k,v in saved['files'].items() if selected(k)}
    differences=[k for k in set(got)|set(expected) if got.get(k)!=expected.get(k)]
    content.append(dict(run=row['run'],selected_files=len(got),all_exact=got==expected,differences=sorted(differences),
        only_stage_differences=bool(differences) and all(k.endswith('/mod.usda') for k in differences)))
out['final_asset_content']=content
(HERE/'analysis.json').write_text(json.dumps(out,indent=2))
print(json.dumps(dict(runs=[{k:r.get(k) for k in ('run','mode','emission_off','retouch','error','first_matching_s','post_start_omissions','max_gap_records','max_gap_span_s','settled_window')} for r in rows],comparisons=out['image_comparisons']),indent=2))
