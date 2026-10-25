"""Bounded read-only second-pass survey review; no rendering or runtime changes.

Produces derived evidence beside each explicit survey. Shader/geometry/image
payloads never exist in this wire. Caller stacks identify flush contexts, not
automatically the producer/owner of previously queued geometry.
"""
import argparse,collections,ctypes as C,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/render_survey'))
from survey_capture import Header,RECORD,validate

def enum_values(name):
    text=(ROOT/'artifacts/remix-runtime/deps/reshade/include/reshade_api_pipeline.hpp').read_text(encoding='utf-8-sig')
    block=re.search(r'enum class '+name+r'[^\{]*\{(.*?)\n\s*\};',text,re.S)[1]
    block=re.sub(r'//[^\n]*','',block);result={};value=-1
    for part in block.split(','):
        part=part.strip()
        if not part:continue
        pair=part.split('=',1);key=pair[0].strip()
        if len(pair)==2:
            expression=pair[1].strip();value=result[expression] if expression in result else int(expression,0)
        else:value+=1
        result[key]=value
    return result

def effective_state(context,pipes,types):
    depth=pipes.get((context['device'],context['pipeline'].get(512,0),types['depth_stencil_state']))
    blend=pipes.get((context['device'],context['pipeline'].get(1024,0),types['blend_state']))
    dynamic=context['dynamic']
    return tuple([int(bool(context['depth'])),dynamic.get(7,depth[4] if depth else None),
        dynamic.get(14,depth[5] if depth else None),dynamic.get(27,blend[4] if blend else None),
        dynamic.get(19,blend[5] if blend else None),dynamic.get(20,blend[6] if blend else None),dynamic.get(1000)])

def state_label(state):
    keys=('depth_bound','depth_test','depth_write','blend','src','dst','topology')
    return ' '.join(f'{k}={v}' for k,v in zip(keys,state))

def caller_kind(chain):
    if chain and chain[0] in (0x006A88E7,0x006A88A2):return 'TEXTURE_BIND_FLUSH_CONTEXT_NOT_PRODUCER'
    if chain and chain[0] in (0x0069E6F2,0x0069E61B,0x0069EC3E,0x0069ECB2):return 'RENDER_STATE_FLUSH_CONTEXT_NOT_PRODUCER'
    if chain and chain[0] in (0x006A6F88,0x006A84DF):return 'SURFACE_LOCK_OR_FLIP_CONTEXT'
    return 'OTHER_SAMPLED_CALL_CONTEXT_OWNER_UNRESOLVED'

def retire_pipeline(device,handle,pipes,contexts):
    for key in [key for key in pipes if key[:2]==(device,handle)]:del pipes[key]
    for (dev,_),context in contexts.items():
        if dev==device:
            context['pipeline']={stage:value for stage,value in context['pipeline'].items() if value!=handle}

def file_sha256(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest().upper()

def analyze(folder):
    folder=Path(folder).resolve();folder.relative_to(ROOT/'artifacts/remix-runtime/runs')
    path=folder/'broad.bin';result=json.loads((folder/'result.json').read_text())
    control=json.loads((folder/'survey-control.json').read_text());types=enum_values('pipeline_subobject_type')
    modules=[json.loads(line) for line in (folder/'broad.bin.modules.jsonl').read_text(encoding='utf-8').splitlines()]
    engines={(m['base'],m['bytes']) for m in modules if Path(m['path']).name.lower()=='starfleetop.exe'}
    if len(engines)!=1:raise ValueError('One observed engine module range required')
    engine_base,engine_bytes=next(iter(engines))
    contexts={};pipes={};views={};resources={};resource_history=[];recent={};pending={}
    counts=collections.Counter();states={};chains={};seconds=collections.defaultdict(collections.Counter)
    unresolved=collections.Counter();previous=0;first_qpc=None;last_qpc=None
    def context(dev,obj):
        key=(dev,obj)
        if key not in contexts:
            if len(contexts)>=4096:raise ValueError('Context analysis bound')
            contexts[key]=dict(device=dev,depth=0,pipeline={},dynamic={},textures={},texture_cache=None)
        return contexts[key]
    with path.open('rb') as stream:
        h=Header.from_buffer_copy(stream.read(128));validate(h)
        if h.fileBytes!=path.stat().st_size:raise ValueError('Final file size mismatch')
        def moment(qpc):return (qpc-h.gateQpc)/h.frequency
        def view_resource(dev,view):
            v=views.get((dev,view));r=resources.get((dev,v['resource'])) if v else None
            return r if r and v['resource_epoch']==r['creation_sequence'] else None
        def complete(parent):
            p=pending.pop(parent)
            if len(p['addresses'])!=p['expected']:unresolved['incomplete_origin']+=1;return
            draw=p['draw'];addresses=[v for _,v in sorted(p['addresses'].items())]
            chain=tuple(address for address in addresses if engine_base<=address<engine_base+engine_bytes)
            if not chain:unresolved['origin_without_engine_frame']+=1;return
            row=chains.get(chain)
            if row is None:
                if len(chains)>=4096:raise ValueError('Call-chain analysis bound')
                row=dict(engine_return_addresses=[f'0x{x:08X}' for x in chain],kind=caller_kind(chain),samples=0,first_seconds=draw['seconds'],last_seconds=draw['seconds'],states=collections.Counter(),seconds=collections.Counter(),texture_resources=collections.Counter(),min_count=draw['count'],max_count=draw['count']);chains[chain]=row
            row['samples']+=1;row['last_seconds']=draw['seconds'];row['states'][draw['state']]+=1;row['seconds'][int(draw['seconds'])]+=1
            row['texture_resources'].update(draw['textures']);row['min_count']=min(row['min_count'],draw['count']);row['max_count']=max(row['max_count'],draw['count'])
        while raw:=stream.read(128):
            seq,qpc,event,thread,obj,dev,*a=RECORD.unpack(raw)
            if seq<=previous:raise ValueError('Nonmonotonic sequence')
            previous=seq;counts[event]+=1;t=moment(qpc)
            if event==2:
                for table in (contexts,views,resources,pipes):
                    for key in [k for k in table if k[0]==dev]:del table[key]
            elif event in (8,9):contexts.pop((dev,obj),None)
            elif event==3:
                if len(resource_history)>=65536:raise ValueError('Resource history bound')
                r=dict(device=dev,label=obj,creation_sequence=seq,type=a[0],usage=a[1],width_or_bytes=a[5],height_or_stride=a[6],format=a[9],samples=a[10],created_seconds=t,retired_seconds=None,draws=0,first_draw_seconds=None,last_draw_seconds=None,draw_seconds=collections.Counter(),states=collections.Counter())
                resources[dev,obj]=r;resource_history.append(r)
                if t>=0:seconds[int(t)]['resource_created']+=1
            elif event==4:
                r=resources.pop((dev,obj),None)
                if r:r['retired_seconds']=t
                if t>=0:seconds[int(t)]['resource_retired']+=1
            elif event==5:
                views[dev,obj]=dict(resource=a[0],resource_epoch=resources.get((dev,a[0]),{}).get('creation_sequence',0))
            elif event==6:
                views.pop((dev,obj),None)
                for (d,_),c in contexts.items():
                    if d==dev:
                        if c['depth']==obj:c['depth']=0
                        c['textures']={k:v for k,v in c['textures'].items() if v!=obj};c['texture_cache']=None
            elif event==29:pipes[dev,obj,a[0]]=tuple(a)
            elif event==30:retire_pipeline(dev,obj,pipes,contexts)
            elif event in (10,20,21,24):
                c=context(dev,obj)
                if event==10:c['depth']=a[1]
                elif event==20:c['pipeline'][a[0]]=a[1]
                elif event==21:c['dynamic'][a[0]]=a[1]
                elif a[5] in (1,2,3):c['textures'][a[0],a[2],a[3],a[4]]=a[6];c['texture_cache']=None
            elif event in (11,12):
                if not a[0] or not a[1]:unresolved['zero_work_draws']+=1;continue
                if first_qpc is None:first_qpc=qpc
                last_qpc=qpc;c=context(dev,obj);state=state_label(effective_state(c,pipes,types));row=states.get(state)
                if row is None:row=dict(draws=0,indexed=0,nonindexed=0,first_seconds=t,last_seconds=t,min_count=a[0],max_count=a[0],seconds=collections.Counter());states[state]=row
                row['draws']+=1;row['indexed' if event==12 else 'nonindexed']+=1;row['last_seconds']=t;row['min_count']=min(row['min_count'],a[0]);row['max_count']=max(row['max_count'],a[0]);row['seconds'][int(t)]+=1
                seconds[int(t)]['draws']+=1
                if c['texture_cache'] is None:c['texture_cache']=tuple(sorted(set(c['textures'].values())-{0}))
                textures=[]
                for label in c['texture_cache']:
                    r=view_resource(dev,label)
                    if r:
                        r['draws']+=1;r['first_draw_seconds']=t if r['first_draw_seconds'] is None else r['first_draw_seconds'];r['last_draw_seconds']=t;r['draw_seconds'][int(t)]+=1;r['states'][state]+=1;textures.append(r['creation_sequence'])
                    else:unresolved['unresolved_view_draw_references']+=1
                recent[seq]=dict(seconds=t,count=a[0],state=state,textures=textures,thread=thread)
                if len(recent)>128:del recent[next(iter(recent))]
            elif event==31:
                parent,first,expected=a[:3]
                if parent not in recent:unresolved['origin_parent_unresolved']+=1;continue
                if not 0<expected<=32 or first>=expected:raise ValueError('Invalid stack fragment')
                if parent not in pending:pending[parent]=dict(draw=recent[parent],expected=expected,addresses={})
                p=pending[parent]
                for i,address in enumerate(a[3:]):
                    if first+i<expected:p['addresses'][first+i]=address
                if len(p['addresses'])==expected:complete(parent)
            elif event==18:seconds[int(t)]['presents']+=1
        unresolved['incomplete_origin']+=len(pending)
    if previous!=h.written:raise ValueError('Record count mismatch')
    def plain(value):
        if isinstance(value,collections.Counter):return dict(value)
        if isinstance(value,dict):return {k:plain(v) for k,v in value.items()}
        if isinstance(value,list):return [plain(v) for v in value]
        return value
    payload=dict(probe='RENDER-FAMILY-SURVEY-001-REVIEW',run=folder.name,trace_sha256=file_sha256(path),
        record_count=h.written,capture_reason=h.reason,dropped=h.dropped,trace_bytes=h.fileBytes,
        retained_tactical_seconds=(h.endQpc-h.gateQpc)/h.frequency,
        first_last_draw_seconds=[moment(first_qpc),moment(last_qpc)],
        mechanical={k:result[k] for k in ('normal_game_exit','gate_clean_unloaded','renderer_exit','original_critical_unchanged','launcher_settings_unchanged','broad_proxy_restored')},
        payload_exclusions={k:control[k] for k in ('geometry_payload','image_payload')},
        state_fields=['depth_bound','depth_test','depth_write','blend','src','dst','topology'],
        states=plain(states),call_chains=plain(sorted(chains.values(),key=lambda x:x['samples'],reverse=True)),
        resources=plain(resource_history),seconds=plain(dict(seconds)),unknowns=dict(unresolved),
        limitations=['Cap/drop means partial coverage','All resource labels session-local;no cross-run pointer matching','Stack indicates observed submission/flush context,not guaranteed geometry producer','No event timestamp assigned to sponsor destruction report','No shader/geometry/image/constant payload or owner object pointer'])
    target=folder/'render-families.review.json';encoded=json.dumps(payload,indent=2)
    if len(encoded.encode())>16*1024*1024:raise ValueError('Review output16MiB cap')
    target.write_text(encoded,encoding='utf-8');return payload

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('runs',nargs='+',type=Path);args=parser.parse_args()
    for folder in args.runs:
        r=analyze(folder);print(r['run'],'seconds',round(r['retained_tactical_seconds'],3),'states',len(r['states']),'chains',len(r['call_chains']),'samples',sum(x['samples'] for x in r['call_chains']),'output',str(folder/'render-families.review.json'))
