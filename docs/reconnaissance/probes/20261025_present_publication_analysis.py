"""Run190 read-only attribution and full-interval delivery comparison."""
import hashlib
import json
from pathlib import Path
import re
import struct
import sys
import zipfile
from PIL import Image, ImageChops, ImageStat

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'tools/d3d9_proof'))
from startup_profile import analyze
RUNS = ROOT/'artifacts/remix-runtime/runs'
HERE = ROOT/'artifacts/present-stall'
OLD = '20261025-220919-119346-return-fixture'
NEW = '20261025-224552-119514-return-fixture'
FAILED = '20261025-224644-859442-return-fixture'


def summarize(name):
    folder=RUNS/name
    result=json.loads((folder/'result.json').read_text())
    job=json.loads((folder/'gpu/job-result.json').read_text())
    data=dict(run=name,error=result['error'],native_job=job,
              total_bytes=sum(p.stat().st_size for p in folder.rglob('*') if p.is_file()))
    if not result['live_owner_timing']:
        data['startup_records_lost_on_native_crash']=True
        return data
    multi=result['live_owner_timing']['multi_scene']
    profile=analyze(folder)
    origin=min(j['discovered_ns'] for j in multi['preparation']['jobs_summary'])
    fmt=struct.Struct('<8I5Q')
    raw=(folder/'D3D9-SYNC-BUFFER-001.bin').read_bytes()
    rows=[fmt.unpack_from(raw,i) for i in range(64,len(raw)-fmt.size+1,fmt.size)]
    first=next(i for i,r in enumerate(rows) if r[3]==1)
    gaps=[];gap=[]
    for row in rows[first:]:
        if row[3]==2:gap.append(row)
        elif gap:gaps.append(gap);gap=[]
    if gap:gaps.append(gap)
    windows=re.search(r'GAME_DELIVERY_WINDOW frames=(\d+) draws=(\d+)',(folder/'fixture.log').read_text())
    boot=[r for r in profile['bootstrap']]
    data.update(bootstrap_wall_s=profile['bootstrap_total_wall_seconds'],
                draw_issue_s=sum(r['draw_seconds'] for r in boot),
                present_plus_service_s=sum(r['present_seconds'] for r in boot),
                largest_present_plus_service=max(boot,key=lambda r:r['present_seconds']),
                startup_profile=profile,
                first_matching_s=rows[first][-1]/1e7-origin/1e9,
                post_start_omissions=sum(map(len,gaps)),
                max_gap_records=max(map(len,gaps),default=0),
                max_gap_span_s=max(((g[-1][-1]-g[0][-1])/1e7 for g in gaps),default=0),
                omission_gaps=[dict(records=len(g),start_qpc=g[0][-1],end_qpc=g[-1][-1]) for g in gaps],
                material_master_publications=len(multi['material_events']),
                material_publication_first_ns=multi['material_events'][0]['supervisor_monotonic_ns'],
                material_publication_last_ns=multi['material_events'][-1]['supervisor_monotonic_ns'],
                state=multi['state'],partial=multi['partial'],draws=multi['draws'],
                output_stages=multi['output_stage_timings'],
                settled_window=dict(frames=int(windows[1]),draws=int(windows[2])),
                probe=result.get('present_publication_probe'),
                source_input_unchanged=result.get('present_publication_probe',{}).get('unchanged_production'))
    return data


def selected(name):
    return '/assets/' in name and (name.endswith(('.dds','/mod.usda','/scene.bin')) or '/texture-' in name)


archive=json.loads((ROOT/'artifacts/staging-integration'/f'{OLD}-archive.json').read_text())
before={}
with zipfile.ZipFile(ROOT/archive['archive']) as source:
    for name in source.namelist():
        if selected(name):before[name.split('/gpu/',1)[1]]=source.read(name)
after={p.relative_to(RUNS/NEW/'gpu').as_posix():p.read_bytes()
       for p in (RUNS/NEW/'gpu/assets').rglob('*') if p.is_file() and selected('/assets/'+p.name)}
if not after:
    new_archive=json.loads((HERE/f'{NEW}-archive.json').read_text())
    with zipfile.ZipFile(ROOT/new_archive['archive']) as source:
        after={name.split('/gpu/',1)[1]:source.read(name) for name in source.namelist() if selected(name)}
differences=[]
for name in sorted(set(before)|set(after)):
    if before.get(name)==after.get(name):continue
    a,b=before.get(name,b''),after.get(name,b'')
    if name.endswith('/scene.bin') and len(a)>32 and len(b)>32:
        h=struct.unpack_from('<8I',a);end=32+h[2]*32+h[3]*4+h[4]*16
        differences.append(dict(file=name,geometry_exact=a[:end]==b[:end],
            only_frame_number_differs=a[:end+8]==b[:end+8] and a[end+12:]==b[end+12:]))
    else:differences.append(dict(file=name,unexplained=True))
roi=(200,730,1340,970)
left=Image.open(RUNS/OLD/'fixture-ship-late.bmp').convert('RGB')
right=Image.open(RUNS/NEW/'fixture-ship-late.bmp').convert('RGB')
diff=ImageChops.difference(left,right).crop(roi)
comparison=dict(base=OLD,alternative=NEW,asset_files=len(after),
    all_final_geometry_images_materials_exact=all(d.get('geometry_exact') and d.get('only_frame_number_differs') for d in differences),
    differences=differences,late_pixel_roi=roi,late_pixel_mean_abs_error=ImageStat.Stat(diff).mean,
    late_pixel_bit_exact=diff.getbbox() is None,
    interpretation='Same final bytes does not establish when runtime consumed them;late view is only one bounded sample')
out=dict(scope='Isolated standalone attribution;not speedup/default/gameplay qualification',
    runs=[summarize(n) for n in (OLD,NEW,FAILED)],comparison=comparison)
(HERE/'analysis.json').write_text(json.dumps(out,indent=2))
print(json.dumps(dict(runs=[{k:r[k] for k in ('run','error','bootstrap_wall_s','first_matching_s','post_start_omissions','max_gap_records','max_gap_span_s','material_master_publications','settled_window') if k in r} for r in out['runs']],comparison=comparison),indent=2))
