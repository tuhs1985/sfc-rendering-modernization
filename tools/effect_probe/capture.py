"""Bounded effects metadata parser; no geometry/image content or guessed owners."""
import collections,ctypes as C,json,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'remix_runtime'))
from broad_capture import Header,RECORD,digest
MAGIC,HARD=0x45524631,16*1024*1024
NAMES=('born','retired','enter','leave','selected','finalized','polygon','resource','name','fault','overflow','stopped','statistics')
def valid(h):
    if (h.magic,h.version,h.recordBytes,h.headerBytes)!=(MAGIC,1,128,128):raise ValueError('Effect wire header/version')
    if h.hardBytes!=HARD or not h.frequency or not 0<h.durationMs<=90000:raise ValueError('Effect wire bounds')
def header_at(address):
    h=Header.from_buffer_copy(C.string_at(address+256,128));valid(h)
    return {n:int(getattr(h,n)) for n,_ in Header._fields_ if n!='reserved'}
def analyze(path):
    path=Path(path);size=path.stat().st_size
    if not 128<=size<=HARD or (size-128)%128:raise ValueError('Effect file alignment/size')
    counts=collections.Counter();issues=collections.Counter();owners={};scopes={};requests={};chunks={};images={};polygons=[];stopped=[];stats=[];last=0
    with path.open('rb') as f:
        h=Header.from_buffer_copy(f.read(128));valid(h)
        if h.fileBytes!=size:raise ValueError('Effect final file size')
        for raw in iter(lambda:f.read(128),b''):
            seq,qpc,kind,thread,obj,manager,*a=RECORD.unpack(raw)
            if seq<=last or not 64<=kind<=76:raise ValueError('Effect sequence/kind')
            last=seq;counts[NAMES[kind-64]]+=1
            stack=scopes.setdefault(thread,[])
            if kind==64:
                if not a[0]:issues['unknown_birth_epoch']+=1
                owners[obj]=a[0]
            elif kind==65:
                if owners.get(obj)!=a[0]:issues['unmatched_retire']+=1
                owners.pop(obj,None)
            elif kind==66:
                if len(stack)>=8:issues['scope_overflow']+=1;continue
                good=bool(a[0] and owners.get(obj)==a[0] and not a[2] and a[3])
                if not good:issues['unqualified_scope']+=1
                stack.append(dict(owner=obj,epoch=a[0],token=a[1],manager=manager,good=good))
            elif kind==67 or (kind==73 and a[2]==2):
                if not stack or (stack[-1]['owner'],stack[-1]['epoch'],stack[-1]['token'])!=(obj,a[0],a[1]):issues['unbalanced_scope']+=1
                else:stack.pop()
                if kind==73:issues['native_exception_observed']+=1
            elif kind in (68,69,70,71):
                s=stack[-1] if stack else None
                matched=bool(s and s['good'] and (s['owner'],s['epoch'],s['token'],s['manager'])==(obj,a[0],a[1],manager))
                if kind==70:
                    qualified=matched and bool(a[5]) and 0<a[2]<=4096 and 0<a[3]<=65536
                    if not qualified:issues['unqualified_polygon']+=1
                    if len(polygons)<32768:polygons.append(dict(sequence=seq,owner=obj,epoch=a[0],scope=a[1],manager=manager,resource_id=a[2],corners=a[3],flags=a[4],qualified=qualified))
                    else:issues['polygon_summary_cap']+=1
                elif kind==71:
                    if len(requests)<32768:requests[seq]=dict(owner=obj,manager=manager,epoch=a[0],scope=a[1],resource_id=a[2],signature=tuple(a[3:7]),qualified=matched)
                    else:issues['resource_summary_cap']+=1
            elif kind==72:
                parent,resource,chunk=a[:3]
                if chunk>=4 or parent not in requests:issues['unmatched_filename']+=1;continue
                key=(parent,resource);parts=chunks.setdefault(key,{})
                if chunk in parts:raise ValueError('Duplicate filename chunk')
                parts[chunk]=struct.pack('<8Q',*a[3:])
                if len(parts)==4:
                    rawname=b''.join(parts[i] for i in range(4));end=rawname.find(b'\0')
                    if end<=0 or any(c<32 or c>126 for c in rawname[:end]):raise ValueError('Invalid bounded resource filename')
                    r=requests[parent];images[(r['manager'],resource,r['signature'])]=rawname[:end].decode('ascii')
                    del chunks[key]
            elif kind==73:issues['resource_snapshot_changed']+=1
            elif kind==74:issues['native_scope_overflow']+=1
            elif kind==75:stopped.append(a[:2])
            elif kind==76:stats.append(a[:5])
    if h.written!=sum(counts.values()):raise ValueError('Effect record count')
    if chunks:issues['incomplete_filename']+=len(chunks)
    if any(scopes.values()):issues['unfinished_scope']+=1
    if h.dropped:issues['record_loss']+=h.dropped
    if h.status!=3 or h.error or not stopped or any(e or active for e,active in stopped):issues['cleanup_unconfirmed']+=1
    if h.reason not in (1,3):issues['capture_limit_or_setup_failure']+=1
    if stats and (stats[-1][0] or stats[-1][1] or stats[-1][4]):issues['native_fault_or_identity_uncertainty']+=1
    joined=collections.defaultdict(set)
    for r in requests.values():
        name=images.get((r['manager'],r['resource_id'],r['signature']))
        if r['qualified'] and name:joined[(r['owner'],r['epoch'],r['scope'],r['manager'],r['resource_id'])].add(name)
    qualified=0;assignments={}
    for p in polygons:
        names=joined[(p['owner'],p['epoch'],p['scope'],p['manager'],p['resource_id'])]
        if p['qualified'] and len(names)==1:
            qualified+=1;assignments[(p['owner'],p['epoch'],p['resource_id'],next(iter(names)))]=True
    if not qualified:issues['no_joined_native_polygon']+=1
    return dict(probe='EFFECT-RESOURCE-JOIN-001',sha256=digest(path),bytes=size,records=h.written,counts=dict(counts),issues=dict(issues),
                result='PARTIAL' if issues else 'NATIVE_EFFECT_RESOURCE_JOIN_OBSERVED',header={n:int(getattr(h,n)) for n,_ in Header._fields_ if n!='reserved'},
                qualified_native_polygons=qualified,assignments=[dict(owner=k[0],epoch=k[1],resource_id=k[2],filename=k[3]) for k in assignments],
                native_statistics=stats,stopped=stopped,limitations=['Not a one-to-one D3D11 draw/producer mapping','No geometry or image payload','Resource snapshot identity,not unobserved allocation epoch','Not an effects renderer or universal effect classification'])
