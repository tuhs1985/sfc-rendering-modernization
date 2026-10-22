"""Read-only semantic-offer to presentation lead. Not a renderer/frame-seal PASS."""
from pathlib import Path
import hashlib
import json
import struct
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
OFFSET=12*1024*1024
CAPACITY=32768
HEADER=struct.Struct('<12IQ8I40s')
RECORD=struct.Struct('<8I5Q2I')
MAGIC=0x31545344
STORE_BYTES=HEADER.size+CAPACITY*RECORD.size
QUALIFICATION=ROOT/'artifacts/d3d9-proof/source-timing-qualification.json'
BINARIES=('artifacts/remix-runtime/return-bin/SFCRemixReturn.dll','artifacts/m1/bin/m1_component.dll',
    'artifacts/m1/bin/m1_controller.exe','artifacts/remix-runtime/return-bin/return_launcher.exe',
    'artifacts/remix-runtime/return-bin/d3d11_return_fixture.exe','artifacts/remix-runtime/return-bin/return_host.exe',
    'artifacts/m1/bin/m1_live_scene_tests.exe','artifacts/d3d9-proof/receiver-bin/source_timing_tests.exe')


def digest(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest().upper()


def source_hashes():
    from prepare_full_reshade import source_hashes as base
    result=base()
    names=('tools/d3d9_proof/source_timing.h','tools/remix_runtime/source_timing.py','tools/remix_runtime/source_timing_addon.h',
        'tools/remix_runtime/source_timing_fixture.h','tools/remix_runtime/qualify_source_timing.py',
        'tests/d3d9_source_timing_tests.cpp','tests/test_d3d9_source_timing.py',
        'tools/d3d9_proof/start_source_timing_session.ps1','tools/d3d9_proof/build_receiver.ps1')
    result.update({p:digest(ROOT/p) for p in names});return result


def require_qualification():
    q=json.loads(QUALIFICATION.read_text())
    if q.get('result')!='OFFLINE_SOURCE_TIMING_PREPARED' or q.get('sources')!=source_hashes():raise ValueError('Source timing offline/source qualification required')
    if q.get('binaries')!={p:digest(ROOT/p) for p in BINARIES}:raise ValueError('Source timing qualified binaries changed;requalify,do not rebuild during gameplay setup')
    return q


def decode(raw,session,pid=None):
    if not HEADER.size<=len(raw)<=STORE_BYTES:raise ValueError('Source timing byte cap')
    h=HEADER.unpack_from(raw)
    expected=tuple(int(session[-32:][i:i+8],16) for i in range(0,32,8))
    if (h[:4]!=(MAGIC,1,STORE_BYTES,CAPACITY) or not h[4] or not h[5] or not 0<h[12]<10**12 or
        h[13:17]!=expected or h[20] or any(h[21]) or h[6]>CAPACITY or len(raw)!=HEADER.size+h[6]*RECORD.size):raise ValueError('Source timing header/session')
    if pid is not None and h[4]!=pid:raise ValueError('Source timing wrong process')
    rows=[];previous=0;groups={};pairs={}
    for r in RECORD.iter_unpack(raw[HEADER.size:]):
        stage,frame,callback,owner,revision,status,thread,reserved,first,last,now,pose,camera,model,source=r
        if (stage not in (1,2) or not all((frame,callback,owner,revision,pose,camera,model,source)) or status!=1 or thread!=h[5] or reserved or
            callback<previous or callback>h[8] or not 0<first<=last<=now):raise ValueError('Source timing malformed row/order')
        previous=callback
        row=dict(stage=stage,frame=frame,callback=callback,owner=owner,revision=revision,source_thread=thread,
            first_qpc=first,last_qpc=last,observed_qpc=now,pose_hash=pose,camera_hash=camera,model=model,source=source,
            first_lead_ms=(now-first)*1000/h[12],last_lead_ms=(now-last)*1000/h[12])
        rows.append(row);groups.setdefault((stage,owner,revision),[]).append(row);pairs.setdefault((frame,owner,revision),{}).setdefault(stage,[]).append(row)
    def summary(values):
        return dict(zip(('min','p05','p50','p95','max'),(float(x) for x in np.quantile(values,[0,.05,.5,.95,1]))))
    profiles=[dict(stage=k[0],owner=k[1],revision=k[2],records=len(v),first_lead_ms=summary([r['first_lead_ms'] for r in v]),
        last_lead_ms=summary([r['last_lead_ms'] for r in v])) for k,v in sorted(groups.items())]
    exact=changed=repeated=0;orders=[]
    for stages in pairs.values():
        if len(stages.get(1,[]))!=1 or len(stages.get(2,[]))!=1:repeated+=1;continue
        a,b=stages[1][0],stages[2][0];exact+=1
        changed+=int((a['pose_hash'],a['camera_hash'])!=(b['pose_hash'],b['camera_hash']))
        orders.append((b['observed_qpc']-a['observed_qpc'])*1000/h[12])
    counters=dict(zip(('dropped','callbacks','wrong_thread','invalid','snapshot_miss'),h[7:12]))
    counters.update(missing_stamp=h[17],ambiguous=h[18],owner_limit=h[19])
    complete=bool(rows) and not any(counters[k] for k in ('dropped','wrong_thread','invalid','missing_stamp','owner_limit'))
    return dict(result='SOURCE_TIMING_OBSERVATION_COMPLETE_ADJUDICATION_REQUIRED' if complete else 'SOURCE_TIMING_PARTIAL',
        pid=h[4],thread=h[5],frequency=h[12],records=len(rows),counters=counters,profiles=profiles,
        exact_frame_owner_pairs=exact,pose_camera_changed_between_stages=changed,unpaired_or_repeated_frame_groups=repeated,
        overlay_minus_present_ms=summary(orders) if orders else None,sha256=hashlib.sha256(raw).hexdigest(),
        scope='Direct first/last semantic offer to callbacks;not physical display timing,complete frame sealing,renderer delivery or milestone PASS')


def save(channel,folder,pid=None):
    folder=Path(folder);folder.relative_to(ROOT/'artifacts')
    head=channel.read(OFFSET,HEADER.size);h=HEADER.unpack(head)
    if h[6]>CAPACITY:raise ValueError('Source timing record cap')
    raw=channel.read(OFFSET,HEADER.size+h[6]*RECORD.size)
    if channel.read(OFFSET,HEADER.size)!=head or raw[:HEADER.size]!=head:raise ValueError('Source timing still changing;do not claim final snapshot')
    (folder/'D3D9-SOURCE-TIMING-001.bin').write_bytes(raw)
    result=decode(raw,channel.name,pid)
    (folder/'source-timing.analysis.json').write_text(json.dumps(result,indent=2));return result
