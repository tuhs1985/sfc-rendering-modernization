"""Bounded metadata timing analysis. No reconstructed assets or inferred pixels."""
import collections
import ctypes as C
import json
from pathlib import Path
import struct
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'remix_runtime'))
from broad_capture import Header,digest
MAGIC,HARD=0x454D4131,16*1024**2
RECORD=struct.Struct('<4Q8I40I256s8I')
NAMES=('request','request_end','load','load_end','parse','parse_end','attach','first_draw','owner_born','owner_retire','visual_retire','gate','exception','statistics','stopped')
assert RECORD.size==512

def valid(h):
    if (h.magic,h.version,h.recordBytes,h.headerBytes)!=(MAGIC,1,512,128):raise ValueError('Early-model wire version/layout')
    if h.hardBytes!=HARD or h.warningBytes!=HARD//2 or not h.frequency or h.durationMs!=90000:raise ValueError('Early-model bounds/clock')
    if h.status not in (1,2,3,4) or any(getattr(h,k)<0 for k in ('attempts','dropped','written','queued')):raise ValueError('Early-model counters/status')

def header_at(address):
    h=Header.from_buffer_copy(C.string_at(address+256,128));valid(h)
    return {n:int(getattr(h,n)) for n,_ in Header._fields_ if n!='reserved'}

def analyze(path):
    path=Path(path);size=path.stat().st_size
    if not 128<=size<=HARD or (size-128)%512:raise ValueError('Early-model file size')
    issues=collections.Counter();counts=collections.Counter();begins={};stacks=collections.defaultdict(list)
    owners={};assets={};ready={};attached={};parse_returns={};joins=[];stops=[];stats=[];retired_visuals=set();owner_epochs={};asset_epochs={};previous=0;fixture=None
    with path.open('rb') as f:
        h=Header.from_buffer_copy(f.read(128));valid(h)
        if h.fileBytes!=size:raise ValueError('Early-model declared bytes')
        for raw in iter(lambda:f.read(512),b''):
            v=RECORD.unpack(raw);seq,qpc,token,parent=v[:4];kind,thread,owner,visual,mesh,flags,depth,caller=v[4:12];a=v[12:52];name=v[52]
            if seq<=previous or (seq!=previous+1 and not h.dropped) or kind not in range(80,95) or flags&~511 or depth>8 or any(v[53:]):raise ValueError('Early-model sequence/event/flags')
            if seq!=previous+1:issues['retained_sequence_gap']+=seq-previous-1
            previous=seq
            if not h.startQpc<=qpc<=h.endQpc:raise ValueError('Early-model event clock')
            profile=bool(flags&256)
            if fixture is not None and fixture!=profile:raise ValueError('Mixed fixture/game records')
            fixture=profile;label=NAMES[kind-80];counts[label]+=1
            end=name.find(b'\0')
            if end<0 or any(c<32 or c>126 for c in name[:end]):raise ValueError('Early-model filename encoding/bound')
            text=name[:end].decode('ascii')
            if flags&255:issues['flagged_metadata']+=1
            r=dict(sequence=seq,qpc=qpc,token=token,parent=parent,owner=owner,visual=visual,mesh=mesh,flags=flags,data=a,name=text,thread=thread)
            if kind in (80,82,84):
                if not token or token in begins:raise ValueError('Early-model duplicate scope')
                if parent and (not stacks[thread] or parent!=stacks[thread][-1]):issues['scope_parent_mismatch']+=1
                begins[token]=r;stacks[thread].append(token)
            elif kind in (81,83,85,92):
                if kind==92:issues['original_exception_observed']+=1
                if not stacks[thread] or stacks[thread][-1]!=token or token not in begins:issues['scope_end_mismatch']+=1;continue
                stacks[thread].pop();begin=begins[token]
                expected={81:80,83:82,85:84}.get(kind)
                if expected and begin['kind']!=expected:raise ValueError('Early-model scope kind')
                if owner!=begin['owner'] or parent!=begin['parent'] or (kind==85 and visual!=begin['visual']):raise ValueError('Early-model scope identity changed')
                if qpc<begin['qpc']:raise ValueError('Early-model scope clock reversed')
                if kind==85 and a[2]:parse_returns[(parent,visual)]=r
                if kind==83:
                    if not visual:counts['failed_load']+=1;continue
                    counts['fresh_load' if a[23] else 'cache_return']+=1
                    if not a[1]:issues['missing_asset_epoch']+=1;continue
                    key=(visual,a[1])
                    if key in retired_visuals:issues['retired_asset_epoch_reused']+=1;continue
                    if a[1] in asset_epochs and asset_epochs[a[1]]!=visual:raise ValueError('Asset epoch cross-association')
                    asset_epochs[a[1]]=visual
                    old=assets.get(key)
                    if old and old['name']!=begin['name'] and a[23]:issues['asset_name_changed_without_epoch']+=1
                    if not old:assets[key]=dict(name=begin['name'],qualified=not(flags&255),first_ready=qpc)
                    ready[(owner,a[0],visual,a[1])]=dict(begin=begin,end=r)
            elif kind==88:
                if not owner or not a[0]:issues['owner_birth_without_epoch']+=1
                if a[0] in owner_epochs:raise ValueError('Owner epoch reused')
                owner_epochs[a[0]]=owner
                if owner in owners:issues['owner_rebirth_without_retirement']+=1
                owners[owner]=a[0]
            elif kind==89:
                if owners.get(owner)!=a[0]:issues['owner_retirement_unknown']+=1
                owners.pop(owner,None)
                for key in list(attached):
                    if key[0]==owner:del attached[key]
            elif kind==90:
                retired_visuals.add((visual,a[1]))
            elif kind==86:
                if flags&255 or owners.get(owner)!=a[0] or a[23]!=visual:counts['unqualified_attachment']+=1;continue
                completion=ready.get((owner,a[0],visual,a[1]))
                if not completion or not token:issues['attachment_without_named_completion']+=1;continue
                # Walk the observed scope chain, not a guessed pointer association.
                ancestor=completion['begin']['token'];seen=set()
                while ancestor and ancestor!=token and ancestor in begins and ancestor not in seen:
                    seen.add(ancestor);ancestor=begins[ancestor]['parent']
                request=begins.get(token)
                if ancestor!=token or not request or request['kind']!=80 or request['owner']!=owner or request['data'][0]!=a[0]:issues['attachment_request_mismatch']+=1;continue
                attached[(owner,a[0])]=dict(record=r,completion=completion,request=request)
            elif kind==87:
                bound=attached.get((owner,a[0]));key=(visual,a[1]);asset=assets.get(key)
                if flags&255 or owners.get(owner)!=a[0] or key in retired_visuals or not bound or not asset or not asset['qualified']:
                    issues['first_draw_without_live_qualification']+=1;continue
                attach=bound['record'];complete=bound['completion'];b=complete['begin'];c=complete['end']
                if not fixture and caller!=0x0042FDD5:raise ValueError('First draw caller is not the pinned semantic mainline')
                if (attach['visual'],attach['data'][1])!=key or not mesh or mesh not in a[10:14]:issues['first_draw_cross_association']+=1;continue
                if not b['qpc']<=c['qpc']<=attach['qpc']<=qpc:raise ValueError('Early-model readiness chronology')
                if len(joins)>=4096:issues['join_summary_cap']+=1;continue
                ms=lambda t:(t-h.startQpc)*1000/h.frequency
                parsed=parse_returns.get((b['token'],visual))
                joins.append(dict(owner=owner,owner_epoch=a[0],visual=visual,asset_epoch=a[1],mesh=mesh,model_name=asset['name'],request_name=bound['request']['name'],request_begin_ms=ms(bound['request']['qpc']),
                    load_begin_ms=ms(b['qpc']),native_ready_ms=ms(c['qpc']),attached_ms=ms(attach['qpc']),first_draw_ms=ms(qpc),
                    native_load_ms=(c['qpc']-b['qpc'])*1000/h.frequency,ready_to_first_draw_ms=(qpc-c['qpc'])*1000/h.frequency,
                    parser_return_ms=ms(parsed['qpc']) if parsed else None,parser_position_pointer=parsed['data'][4] if parsed else None,post_parse_position_pointer_changed=parsed['data'][4]!=a[15] if parsed else None,
                    position_pointer=a[15],original_position_pointer=a[18],source_groups=a[4],primary_ids_present=a[19],secondary_groups=a[20],missing_ids=a[21],sampled_resource_ids=list(a[24:40]),caller=caller))
            elif kind==93:stats.append(dict(faults=a[0],busy=a[1],uncertain=a[2],owner_epochs=a[3],asset_epochs=a[4],scoped_ticks_including_original_calls=token))
            elif kind==94:stops.append(dict(error=a[0],active=a[1],restored=a[2],hooked=a[3]))
            # Preserve begin kind separately after it has been used as a record.
            if kind in (80,82,84):begins[token]['kind']=kind
    if h.written!=sum(counts[k] for k in NAMES):raise ValueError('Early-model written count')
    if any(stacks.values()):issues['unfinished_scope']+=1
    if h.dropped:issues['record_loss']+=h.dropped
    if h.status!=3 or h.error or not stops or any(s['error'] or s['active'] or s['restored']!=9 or s['hooked'] for s in stops):issues['cleanup_unconfirmed']+=1
    if h.reason not in (1,3):issues['limit_or_setup_failure']+=1
    if not stats or any(stats[-1][k] for k in ('faults','busy','uncertain')):issues['native_read_or_identity_failure']+=1
    if not joins:issues['no_complete_named_owner_join']+=1
    return dict(probe='EARLY-MODEL-AVAILABILITY-001',sha256=digest(path),bytes=size,records=h.written,fixture=fixture,
        result='PARTIAL' if issues else 'FIXTURE_TIMING_JOIN_PASS' if fixture else 'EARLY_NATIVE_MODEL_TIMING_OBSERVED',issues=dict(issues),counts=dict(counts),joins=joins,
        header={n:int(getattr(h,n)) for n,_ in Header._fields_ if n!='reserved'},stopped=stops,native_statistics=stats,
        limitations=['Native readiness,not Remix/GPU readiness or speedup','First selected-child entry,not a proven visible pixel','Resource IDs are same-session metadata;only first8pairs sampled','No geometry or texture image payload','Startup worker coverage begins after ready,not guaranteed process-entry coverage','Scoped ticks include original calls and nested time;not observer overhead'])

if __name__=='__main__':print(json.dumps(analyze(Path(sys.argv[1])),indent=2))
