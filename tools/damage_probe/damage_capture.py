"""Damage-only evidence decoder; original black-key semantics are established."""
import collections
import hashlib
import math
from pathlib import Path
import struct
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'remix_runtime'))
from broad_capture import Header

RECORD=struct.Struct('<4Q8I40I256s8I')
HARD=16*1024**2
KINDS={100:'model_state',101:'polygon_pass',102:'mapping_result',103:'lazy_mapping_created',104:'resource_table'}

def digest(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest().upper()

def fnv(data):
    value=2166136261
    for b in data:value=((value^b)*16777619)&0xFFFFFFFF
    return value

def mapping(path):
    raw=Path(path).read_bytes()
    if not 128<=len(raw)<=2*1024**2:raise ValueError('Damage mapping size')
    h=list(struct.unpack_from('<32I',raw));n,p,c=h[10:13]
    if h[:2]!=[0x444D5031,1] or h[2]!=len(raw) or not 0<n<=65536 or not 0<p<=8192 or not 3*p<=c<=32768:raise ValueError('Damage mapping layout/counts')
    if len(raw)!=128+n*12+p*28+c*28 or any(h[20:]):raise ValueError('Damage mapping arrays/reserved')
    checksum=h[3];copy=bytearray(raw);struct.pack_into('<I',copy,12,0)
    if fnv(copy)!=checksum:raise ValueError('Damage mapping checksum')
    pos=128;poly=pos+n*12;corner=poly+p*28;expected=0
    for i in range(n):
        if not all(math.isfinite(v) for v in struct.unpack_from('<3f',raw,pos+i*12)):raise ValueError('Damage nonfinite position')
    for i in range(p):
        words=struct.unpack_from('<7I',raw,poly+i*28)
        if not 3<=words[0]<=8 or words[1] or words[6]!=expected:raise ValueError('Damage polygon/group/corner ordinal')
        expected+=words[0]
    if expected!=c:raise ValueError('Damage corner total')
    for i in range(c):
        words=struct.unpack_from('<7I',raw,corner+i*28)
        if words[0]&65535>=n or not all(math.isfinite(v) for v in struct.unpack_from('<5f',raw,corner+i*28+4)):raise ValueError('Damage corner index/finite')
    return dict(file=Path(path).name,sha256=digest(path),bytes=len(raw),visual=h[4],asset_epoch=h[5],model=h[6],list=h[7],owner=h[8],owner_epoch=h[9],positions=n,polygons=p,corners=c,scalar_bits=h[13],family=h[14],primary_id=h[15],companion_id=h[16],geometry_modified=False,uv_modified=False)

def analyze(path):
    path=Path(path);size=path.stat().st_size
    if not 128<=size<=HARD or (size-128)%512:raise ValueError('Damage trace size')
    counts=collections.Counter();issues=collections.Counter();events=[];tables=[];stops=[];statistics=[];names={};owners={};previous=0;fixture=None
    with path.open('rb') as f:
        h=Header.from_buffer_copy(f.read(128))
        if (h.magic,h.version,h.recordBytes,h.headerBytes)!=(0x454D4131,1,512,128) or h.fileBytes!=size or h.hardBytes!=HARD or h.warningBytes!=HARD//2 or h.durationMs!=90000 or not h.frequency:raise ValueError('Damage envelope version/bounds')
        for raw in iter(lambda:f.read(512),b''):
            v=RECORD.unpack(raw);seq,qpc,token,parent=v[:4];kind,thread,owner,visual,mesh,flags,depth,caller=v[4:12];a=list(v[12:52]);text=v[52]
            if seq<=previous or not h.startQpc<=qpc<=h.endQpc or kind not in (*range(80,95),*KINDS) or flags&~511 or depth>8 or any(v[53:]):raise ValueError('Damage record identity/clock/flags')
            if previous and seq!=previous+1:issues['sequence_gap']+=1
            previous=seq;counts[KINDS.get(kind,str(kind))]+=1
            current_fixture=bool(flags&256)
            if fixture is not None and fixture!=current_fixture:raise ValueError('Mixed fixture/game records')
            fixture=current_fixture
            if flags&255:issues['flagged_record']+=1
            if kind==88:
                if not owner or not a[0] or owner in owners:issues['owner_birth_identity']+=1
                owners[owner]=a[0]
            if kind==89:
                if owners.get(owner)!=a[0]:issues['owner_retirement_identity']+=1
                owners.pop(owner,None)
            # Names live on Load-begin records, joined by scope token below.
            if kind==82:names[('load',token)]=text.split(b'\0',1)[0].decode('ascii')
            if kind==83 and visual:names[(visual,a[1])]=names.get(('load',token),'')
            if kind==93:statistics.append(a)
            if kind==94:stops.append(a)
            if kind in KINDS:
                if not owner or owners.get(owner)!=a[0] or not visual or not a[1] or not mesh:issues['damage_identity']+=1
                r=dict(kind=KINDS[kind],sequence=seq,qpc=qpc,call=token,owner=owner,owner_epoch=a[0],visual=visual,asset_epoch=a[1],model=mesh,model_name=names.get((visual,a[1]),''),caller=caller,data=a)
                if kind==104:tables.append(r)
                events.append(r)
    if h.written!=sum(counts.values()):raise ValueError('Damage record count')
    if h.dropped:issues['record_loss']=h.dropped
    if h.status!=3 or h.error or not stops or any(a[:4]!=[0,0,10,0] for a in stops):issues['cleanup_unconfirmed']+=1
    if h.reason not in (1,3):issues['limit_or_setup_failure']+=1
    if not statistics or any(statistics[-1][:3]):issues['native_read_or_identity_failure']+=1
    if statistics and (statistics[-1][5] or statistics[-1][6]):issues['damage_busy_or_capacity_omission']+=statistics[-1][5]+statistics[-1][6]
    snapshots=[mapping(p) for p in sorted(path.parent.glob(path.name+'.mapping-*.bin'))]
    secondary=[e for e in events if e['kind']=='polygon_pass' and e['caller']==0x0042E626]
    if not secondary:issues['damage_pass_not_observed']+=1
    receipts=[e for e in events if e['kind']=='mapping_result']
    if any(not r['data'][3] for r in receipts):issues['mapping_capture_failed']+=1
    if len(snapshots)!=sum(bool(r['data'][3]) for r in receipts):issues['mapping_file_receipt_mismatch']+=1
    for s in snapshots:
        if not any(e['visual']==s['visual'] and e['asset_epoch']==s['asset_epoch'] and e['model']==s['model'] and e['data'][5]==s['list'] and e['data'][13]==s['primary_id'] and e['data'][15]==s['companion_id'] for e in secondary):issues['mapping_material_join']+=1
    inventory_path=Path(__file__).resolve().parents[2]/'docs/reconnaissance/evidence/20261103-damage-texture-path.json'
    import json
    inventory=json.loads(inventory_path.read_text(encoding='utf-8'))['textures']
    resolved=[]
    for e in secondary:
        candidates=[t for t in tables if (t['owner'],t['owner_epoch'],t['visual'],t['asset_epoch'],t['model'])==(e['owner'],e['owner_epoch'],e['visual'],e['asset_epoch'],e['model'])]
        if not candidates:
            if not fixture:issues['missing_resource_table']+=1
            continue
        same_call=[t for t in candidates if t['call']==e['call']]
        prior=[t for t in candidates if t['qpc']<=e['qpc']]
        if not same_call and not prior:
            issues['missing_contemporaneous_resource_table']+=1
            continue
        table=(same_call[0] if same_call else max(prior,key=lambda t:t['qpc']))['data'][2:20]
        images=[]
        for role,resource in (('primary',e['data'][13]),('companion',e['data'][15])):
            matches=[r for r in inventory if table[(int(r['resource_slot'],16)-0x008F57F8)//4]==resource and resource]
            if len(matches)!=1:issues['unresolved_damage_image']+=1
            images.append(dict(role=role,resource_id=resource,matches=matches))
        resolved.append(dict(sequence=e['sequence'],owner=e['owner'],owner_epoch=e['owner_epoch'],model=e['model'],images=images))
    return dict(probe='DAMAGE-LAYER-001',result='PARTIAL' if issues else 'FIXTURE_DAMAGE_OBSERVED' if fixture else 'DAMAGE_LAYER_OBSERVED',fixture=fixture,sha256=digest(path),bytes=size,counts=dict(counts),issues=dict(issues),events=events,mappings=snapshots,resource_tables=tables,resolved_images=resolved,statistics=statistics,stopped=stops,
                limits=dict(metadata_bytes=HARD,mappings=4,mapping_bytes_each=2*1024**2),
                limitations=['No damage display implemented','Pure black transparency is established by sponsor; opaque manager words do not prove exact downstream blend equation','Per-model invocation token/QPC is not a presentation frame ID','One mapping per observed visual epoch/model/list, at most four; no image bytes or repeated base hull dumps'])
