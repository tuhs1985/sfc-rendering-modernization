"""Read-only adjudication of four bounded diagnostic fixtures."""
from pathlib import Path
import hashlib,json,re,struct,zipfile
from PIL import Image,ImageChops,ImageStat
ROOT=Path(__file__).resolve().parents[3];HERE=ROOT/"artifacts/resource-stall"
RUNS=ROOT/'artifacts/remix-runtime/runs'
NAMES=['20261025-213454-340621-return-fixture','20261025-213559-910384-return-fixture',
       '20261025-213854-971322-return-fixture','20261025-214030-845021-return-fixture']
results=[]
for name in NAMES:
 p=RUNS/name;d=json.loads((p/'result.json').read_text());m=d['live_owner_timing']['multi_scene']
 text=(p/'gpu/job-console.log').read_text();calls=[]
 for line in text.splitlines():
  if not line.startswith('RESOURCE_CALL '):continue
  r=dict(re.findall(r'(\w+)=([\w]+)',line));r={k:v if k=='op' else int(v) for k,v in r.items()}
  r['wall_ms']=(r['end_qpc']-r['begin_qpc'])*1000/r['frequency'];r['cpu_ms']=r['cpu_100ns']/10000;calls.append(r)
 (p/'resource-calls.json').write_text(json.dumps(calls,indent=2))
 t=min(j['discovered_ns'] for j in m['preparation']['jobs_summary'])/1e9
 fmt=struct.Struct('<8I5Q');raw=(p/'D3D9-SYNC-BUFFER-001.bin').read_bytes()
 rows=[fmt.unpack_from(raw,i) for i in range(64,len(raw)-fmt.size+1,fmt.size)]
 ix=next(i for i,r in enumerate(rows) if r[3]==1);gaps=[];gap=[]
 for r in rows[ix:]:
  if r[3]==2:gap.append(r)
  elif gap:gaps.append(gap);gap=[]
 if gap:gaps.append(gap)
 win=re.search(r'GAME_DELIVERY_WINDOW frames=(\d+) draws=(\d+)',(p/'fixture.log').read_text())
 results.append(dict(run=name,initial_data=d['resource_call_profile'].get('initial_data_control',False),
  error=d['error'],host_exit=d['host_exit'],fixture_exit=d['fixture_exit'],state=m['state'],partial=m['partial'],
  first_matching_s=rows[ix][-1]/1e7-t,admissions=m['asset_timings'],output_stages=m['output_stage_timings'],
  renderer_totals=[c for c in calls if c['op']=='renderer_total'],
  slow_calls=sorted([c for c in calls if c['op']!='renderer_total'],key=lambda c:c['wall_ms'],reverse=True)[:8],
  call_count=len(calls),trace_summary=next(x for x in text.splitlines() if x.startswith('RESOURCE_CALL_SUMMARY')),
  post_start_omissions=sum(map(len,gaps)),max_omission_records=max(map(len,gaps),default=0),
  max_omission_span_s=max(((g[-1][-1]-g[0][-1])/1e7 for g in gaps),default=0),
  settled_window=dict(frames=int(win[1]),draws=int(win[2]))))
archive=json.loads((HERE/'lock-controls-archive.json').read_text());comparisons=[]
alternate_archive=json.loads((HERE/'initial-data-archive.json').read_text()) if (HERE/'initial-data-archive.json').is_file() else None
for old,new in ((NAMES[0],NAMES[2]),(NAMES[1],NAMES[3])):
 def selected(name):return name.endswith(('.dds','/mod.usda','/scene.bin')) or '/texture-' in name
 a={k.split('/gpu/',1)[1]:v['sha256'] for k,v in archive['files'].items() if k.startswith(old+'/') and selected(k)}
 folder=RUNS/new/'gpu';b={p.relative_to(folder).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
  for p in (folder/'assets').rglob('*') if p.is_file() and selected('/'+p.name)}
 if not b and alternate_archive:
  b={k.split('/gpu/',1)[1]:v['sha256'] for k,v in alternate_archive['files'].items() if k.startswith(new+'/') and selected(k)}
 left=Image.open(RUNS/old/'fixture-ship-late.bmp').convert('RGB');right=Image.open(RUNS/new/'fixture-ship-late.bmp').convert('RGB')
 diff=ImageChops.difference(left,right).crop((200,730,1340,970));pixels=list(diff.getdata())
 differences=[]
 with zipfile.ZipFile(ROOT/archive['archive']) as z:
  for key in sorted(set(a)|set(b)):
   if a.get(key)==b.get(key):continue
   before=z.read(old+'/gpu/'+key)
   if (folder/key).is_file():after=(folder/key).read_bytes()
   else:
    with zipfile.ZipFile(ROOT/alternate_archive['archive']) as other:after=other.read(new+'/gpu/'+key)
   if key.endswith('/scene.bin'):
    h=struct.unpack_from('<8I',before);end=32+h[2]*32+h[3]*4+h[4]*16
    differences.append(dict(file=key,geometry_exact=before[:end]==after[:end],
     only_frame_number_differs=before[:end+8]==after[:end+8] and before[end+12:]==after[end+12:],
     before_frame=struct.unpack_from('<I',before,end+8)[0],after_frame=struct.unpack_from('<I',after,end+8)[0]))
   else:differences.append(dict(file=key,unexplained=True))
 comparisons.append(dict(base=old,alternative=new,asset_files=len(b),final_asset_hash_sets_equal=a==b,
  differences=differences,geometry_images_materials_exact=all(x.get('geometry_exact') and x.get('only_frame_number_differs') for x in differences),
  roi=[200,730,1340,970],mean_abs_error=ImageStat.Stat(diff).mean,nonzero=sum(max(v)>0 for v in pixels),
  over10=sum(max(v)>10 for v in pixels),total=len(pixels),pixel_bit_exact=diff.getbbox() is None))
out=dict(scope='Isolated diagnostic derivative;not production qualification or gameplay',runs=results,comparisons=comparisons)
(HERE/'analysis.json').write_text(json.dumps(out,indent=2))
print(json.dumps(dict(runs=[{k:r[k] for k in ('run','first_matching_s','settled_window','post_start_omissions','max_omission_records','max_omission_span_s')} for r in results],comparisons=comparisons),indent=2))
