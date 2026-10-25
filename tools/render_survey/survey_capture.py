"""Versioned metadata survey parser. No geometry/image reads or semantic guesses."""
import collections
import ctypes as C
import json
import bisect
import math,struct
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'remix_runtime'))
import broad_capture as legacy
from broad_capture import Header,RECORD,FULL,FULL_SHA,OVERALL,digest,qualified_full,install_test_proxy,restore_test_proxy
ROOT=Path(__file__).resolve().parents[2]
HARD=(2048-32)*1024*1024
NAMES=legacy.NAMES+('descriptors','vertex_buffers','index_buffer','scissor','sampler','pipeline_desc','pipeline_end','origin','origin_stats','tables','constants','native_light_part','native_light_control','native_effect_census','native_status')
assert len(NAMES)==39

def reserve_capture_budget():
    sys.path.insert(0,str(ROOT/'tools/d3d9_proof'))
    from run_offline import storage
    extra=sum(p.stat().st_size for name in ('render-survey','remix-api-proof','effect-probe') for p in (ROOT/'artifacts'/name).rglob('*') if p.is_file())
    reserve=2*(HARD+32*1024*1024)+16*1024*1024
    if storage()+extra+reserve>OVERALL:raise ValueError('Survey source/archive reservation exceeds20GB output cap')
    if legacy.shutil.disk_usage(ROOT).free<reserve:raise ValueError('Insufficient disk space for bounded survey')
    return reserve

def validate(h):
    if (h.magic,h.recordBytes,h.headerBytes)!=(0x53525631,128,128) or h.version not in (1,2):raise ValueError('Survey header/version mismatch')
    if not 256<=h.hardBytes<=HARD or not 0<h.durationMs<=90000 or not h.frequency:raise ValueError('Survey bounds invalid')

def header_at(address):
    h=Header.from_buffer_copy(C.string_at(address+256,128));validate(h)
    return {n:int(getattr(h,n)) for n,_ in Header._fields_ if n!='reserved'}

def analyze(path):
    path=Path(path);size=path.stat().st_size
    if size<128 or size>HARD or (size-128)%128:raise ValueError('Survey file size/alignment')
    counts=collections.Counter();resources={};views={};contexts={};pipes={};families={};origins={};stats=collections.Counter();recent_draws={}
    lifecycle=collections.Counter();windows=collections.defaultdict(collections.Counter);over=0;previous=0;summary_origins=0
    light_pending={};light_latest={};light_controls={};light_history=[];light_stats=collections.Counter();native_types={};native_objects=set();native_stats={}
    module_path=Path(str(path)+'.modules.jsonl');modules={}
    if module_path.exists():
        if module_path.stat().st_size>4*1024*1024:raise ValueError('Module metadata bound exceeded')
        for line in module_path.read_text(encoding='utf-8').splitlines():
            item=json.loads(line)
            if not (isinstance(item['qpc'],int) and isinstance(item['base'],int) and 0<item['bytes']<=2**32 and len(item['path'])<=4096):raise ValueError('Module metadata invalid')
            if item['base'] not in modules and len(modules)>=4096:raise ValueError('Module range capacity')
            modules.setdefault(item['base'],[]).append(item)
        for values in modules.values():values.sort(key=lambda x:x['qpc'])
    def locate(address,qpc):
        for base,values in modules.items():
            i=bisect.bisect_right(values,qpc,key=lambda x:x['qpc'])-1
            if i>=0 and base<=address<base+values[i]['bytes']:
                value=values[i]
                return dict(address=address,module=value['path'],offset=address-base,
                    confidence='MODULE_RANGE_OBSERVED_NOT_EXACT_UNLOAD_TIME',engine=Path(value['path']).name.lower()=='starfleetop.exe')
        return dict(address=address,module=None,offset=None,confidence='UNKNOWN',engine=False)
    cap=65536
    def put(table,key,value,limit=cap):
        nonlocal over
        if key in table or len(table)<limit:table[key]=value
        else:over+=1
    def reference(dev,label):
        row=views.get((dev,label));res=resources.get((dev,row['resource'])) if row else None
        matched=res and row.get('resource_epoch')==res['epoch']
        return (label,row['epoch'] if row else 0,row['resource'] if row else 0,res['epoch'] if matched else 0)
    with path.open('rb') as f:
        h=Header.from_buffer_copy(f.read(128));validate(h)
        if h.fileBytes!=size or h.written!=(size-128)//128:raise ValueError('Survey final count mismatch')
        while raw:=f.read(128):
            seq,qpc,event,thread,obj,dev,*a=RECORD.unpack(raw)
            if seq<=previous or not 1<=event<(35 if h.version==1 else len(NAMES)):raise ValueError('Survey sequence/event')
            previous=seq;counts[NAMES[event]]+=1
            if event==35:
                key=(thread,obj,a[0]);row=light_pending.get(key)
                if a[1]>=64 or a[2] not in (0,8) or any(v>0xffffffff for v in a[3:]):raise ValueError('Native light fragment bounds')
                if row is None:
                    row=dict(slot=a[1],parts={},manager=obj,caller=dev,qpc=qpc);put(light_pending,key,row,4096)
                if row['slot']!=a[1] or a[2] in row['parts']:raise ValueError('Native light fragments disagree')
                row['parts'][a[2]]=a[3:]
                if len(row['parts'])==2:
                    raw=row['parts'][0]+row['parts'][8];values=struct.unpack('<15f',struct.pack('<15I',*raw[1:]))
                    value=dict(sequence=a[0],qpc=qpc,manager=obj,slot=a[1],caller=dev,native_type=raw[0],raw_words=raw,values=list(values) if all(map(math.isfinite,values)) else None)
                    put(light_latest,(obj,a[1]),value,512);light_stats['complete_records']+=1
                    light_stats['nonfinite_records']+=int(value['values'] is None)
                    if len(light_history)<256:light_history.append(value)
                    else:light_stats['history_examples_omitted']+=1
                    light_pending.pop(key,None)
            elif event==36:
                if a[4] not in (1,2,3,4) or a[5] not in (0,1):raise ValueError('Native light control schema')
                light_stats['control_calls']+=1;light_stats['invalid_snapshots']+=int(not a[5])
                put(light_controls,(obj,a[1]),dict(sequence=a[0],qpc=qpc,manager=obj,slot=a[1],enabled=a[2],global_gate=a[3],kind=a[4],valid=a[5],caller=dev),520)
                light_stats[{1:'set_calls',2:'enable_calls',3:'gate_calls',4:'initial_slot_snapshots'}[a[4]]]+=1
                # Preserve transitions/examples without retaining an unbounded timeline in RAM.
                if len(light_history)<256:light_history.append(dict(sequence=a[0],qpc=qpc,manager=obj,slot=a[1],enabled=a[2],global_gate=a[3],kind=a[4],valid=a[5],caller=dev))
                else:light_stats['history_examples_omitted']+=1
            elif event==37:
                key=(a[2],a[3]);row=native_types.get(key)
                if row is None:
                    row=dict(vtable=a[2],draw_target=a[3],observations=0,first_qpc=qpc,last_qpc=qpc,object_examples=[]);put(native_types,key,row,4096)
                row['observations']+=1;row['last_qpc']=qpc
                if obj not in row['object_examples'] and len(row['object_examples'])<16:row['object_examples'].append(obj)
                if len(native_objects)<65536:native_objects.add(obj)
                elif obj not in native_objects:over+=1
            elif event==38:
                native_stats=dict(last_list_size=a[1],read_faults=a[2],busy=a[3],list_overflow=a[4]);
            elif event==2:
                for table in (resources,views,contexts,pipes):
                    for key in [k for k in table if k[0]==dev]:del table[key]
            elif event==3:
                put(resources,(dev,obj),dict(epoch=seq,type=a[0],usage=a[1],size=a[5],height=a[6],format=a[9],samples=a[10]));lifecycle['resource_created']+=1
            elif event==4:resources.pop((dev,obj),None);lifecycle['resource_retired']+=1
            elif event==5:put(views,(dev,obj),dict(epoch=seq,resource=a[0],resource_epoch=resources.get((dev,a[0]),{}).get('epoch',0),format=a[3],usage=a[1]));lifecycle['view_created']+=1
            elif event==6:
                views.pop((dev,obj),None);lifecycle['view_retired']+=1
                for (device,_),c in contexts.items():
                    if device==dev:
                        if c['depth']==obj:c['depth']=0
                        c['textures']={k:v for k,v in c['textures'].items() if not(k[3] in (1,2,3) and v==obj)}
            elif event in (8,9):contexts.pop((dev,obj),None)
            elif event==29:
                put(pipes,(dev,obj,a[0]),tuple(a));lifecycle['pipeline_descriptors']+=1
            elif event==30:
                for key in [k for k in pipes if k[:2]==(dev,obj)]:del pipes[key]
                for (device,_),c in contexts.items():
                    if device==dev:c['pipeline']={k:v for k,v in c['pipeline'].items() if v!=obj}
                lifecycle['pipeline_retired']+=1
            elif event==31:
                # Sample tied to one exact draw sequence; no assumption of every draw.
                row=origins.get(a[0])
                if row is None:
                    row=dict(draw_sequence=a[0],thread=thread,qpc=qpc,expected=a[2],addresses={});put(origins,a[0],row,4096)
                    family=recent_draws.get(a[0])
                    if family is None:stats['origin_parent_unresolved']+=1
                    elif len(family['origin_samples'])<4 and summary_origins<512:family['origin_samples'].append(row);summary_origins+=1
                    else:stats['family_origin_summary_truncated']+=1
                for i,address in enumerate(a[3:]):
                    if a[1]+i<a[2]:row['addresses'][a[1]+i]=address
                if len(row['addresses'])==row['expected']:
                    stats['complete_origin_samples']+=1;origins.pop(a[0],None)
            elif event==32:
                for k,v in zip(('eligible','captured','empty','budget_skipped','stack_qpc_ticks'),a):stats[k]+=v
            elif event in (10,11,12,19,20,21,24,25,26,27,33,34):
                c=contexts.get((dev,obj))
                if c is None:
                    c=dict(depth=0,pipeline={},textures={},states={},vertex={},index=None,last_signature=None);put(contexts,(dev,obj),c,4096)
                if event==10:c['depth']=a[1]
                elif event==20:put(c['pipeline'],a[0],a[1],64)
                elif event==21:put(c['states'],a[0],a[1],256)
                elif event==24:
                    put(c['textures'],(a[0],a[2],a[3]+a[4],a[5]),a[6],256)
                    if a[9]>a[10]:stats['descriptor_ranges_truncated']+=1
                    if a[5] not in (0,1,2,3,6):stats['uninterpreted_descriptor_type']+=1
                elif event==25:
                    put(c['vertex'],a[0],tuple(a[1:4]),32)
                    if a[4]>32:stats['vertex_ranges_truncated']+=1
                elif event==26:c['index']=tuple(a[:3])
                elif event==33:stats['descriptor_table_bindings_unresolved']+=1
                elif event==34:stats['constant_ranges_no_payload']+=1
                elif event in (11,12):
                    if not a[0] or not a[1]:stats['zero_work_draws']+=1;continue
                    pipeline=tuple(sorted(c['pipeline'].items()));texture=tuple((k,reference(dev,v)) for k,v in sorted(c['textures'].items()) if k[3] in (1,2,3))
                    signature=(event,pipeline,reference(dev,c['depth']),texture,tuple(sorted(c['states'].items())),tuple((k,v[2]) for k,v in sorted(c['vertex'].items())),c['index'][2] if c['index'] else None)
                    row=families.get(signature)
                    if row is None:
                        row=dict(id=len(families)+1,draw_kind=NAMES[event],pipelines=pipeline,depth=reference(dev,c['depth']),texture_views=texture,
                            dynamic_states=sorted(c['states'].items()),vertex_binding_example=sorted(c['vertex'].items()),index_binding_example=c['index'],pipeline_descriptors=[pipes[k] for k in pipes if k[0]==dev and k[1] in dict(pipeline).values()],draws=0,first_qpc=qpc,last_qpc=qpc,min_count=a[0],max_count=a[0],transitions=0,
                            classification='DEPTH_BOUND_FAMILY_UNCLASSIFIED' if c['depth'] else 'NO_DEPTH_BINDING_FAMILY_UNCLASSIFIED',owner='UNKNOWN',origin_samples=[])
                        put(families,signature,row,4096)
                    row['draws']+=1;row['last_qpc']=qpc;row['min_count']=min(row['min_count'],a[0]);row['max_count']=max(row['max_count'],a[0])
                    if signature!=c['last_signature']:row['transitions']+=1;c['last_signature']=signature
                    recent_draws[seq]=row
                    if len(recent_draws)>128:del recent_draws[next(iter(recent_draws))]
                    if h.gateQpc and qpc>=h.gateQpc:windows[int((qpc-h.gateQpc)//(h.frequency*5))][row['id']]+=1
    # Origin-to-family association is exact only for retained sampled draw IDs.
    for row in families.values():
        for item in row['origin_samples']:
            item['complete']=len(item['addresses'])==item['expected'];item['addresses']=[v for _,v in sorted(item['addresses'].items())]
            item['modules']=[locate(address,item['qpc']) for address in item['addresses']]
            item['upstream_engine_owner']='UNRESOLVED' # A native call address is not a gameplay object identity.
    header={n:int(getattr(h,n)) for n,_ in Header._fields_ if n!='reserved'}
    partial=h.status!=3 or h.error or h.dropped or h.reason!=1 or over or light_pending or light_stats['invalid_snapshots'] or any(native_stats.get(k) for k in ('read_faults','busy','list_overflow'))
    summary=sorted(families.values(),key=lambda r:r['draws'],reverse=True)[:512]
    for row in summary:
        for key in ('texture_views','dynamic_states','pipeline_descriptors'):
            row[key+'_summary_truncated']=len(row[key])>16;row[key]=row[key][:16]
    return dict(probe='RENDER-FAMILY-SURVEY-001',header=header,counts=dict(counts),bytes=size,analysis_overflow=over,
        native=dict(lights=dict(stats=dict(light_stats),incomplete_fragments=len(light_pending),latest=list(light_latest.values()),latest_controls=list(light_controls.values()),history_examples=light_history),effect_types=list(native_types.values()),distinct_process_local_object_addresses=len(native_objects),census=native_stats,limitations='List membership before dispatch is not a rendered primitive or owner epoch;light timing is a native setter observation,not a D3D11 draw attribution'),
        depth_candidates=[r['id'] for r in summary if r['depth'][0]],
        family_count=len(families),families_summary_truncated=len(families)>512,
        families=summary,lifecycle=dict(lifecycle),origin_stats=dict(stats),windows=[dict(window=k,draws=dict(v)) for k,v in sorted(windows.items())],
        module_sidecar=str(path)+'.modules.jsonl',module_ranges=len(modules),origin_coverage='SAMPLED' if stats['captured'] else 'UNRESOLVED_NO_STACKS',result='PARTIAL' if partial else 'METADATA_COMPLETE_SEMANTIC_CLASSIFICATION_PENDING',
        limits='No geometry/images/shader or constant payloads;sampled call origins;no owner guessed from graphics state;deferred execution not replayed')

def save_analysis(path):
    result=analyze(path);encoded=json.dumps(result,indent=2)
    if len(encoded.encode('utf-8'))>16*1024*1024:raise ValueError('Analysis summary exceeds16MiB;raw evidence preserved')
    Path(path).with_suffix('.survey.json').write_text(encoded);return result

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('trace',type=Path);a=p.parse_args();r=save_analysis(a.trace)
    print(json.dumps({k:v for k,v in r.items() if k not in ('families','depth_candidates','windows')},indent=2))
