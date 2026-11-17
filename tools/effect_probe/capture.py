"""Bounded effects metadata parser; no geometry/image content or guessed owners."""
import argparse,collections,ctypes as C,json,math,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'remix_runtime'))
from broad_capture import Header,RECORD,digest
MAGIC,HARD=0x45524631,16*1024*1024
NAMES=('born','retired','enter','leave','selected','finalized','polygon','resource','name','fault','overflow','stopped','statistics','quad_corner','quad_result',
       'batch_span','batch_vertex','batch_indices','batch_flush','batch_state','batch_present')
def valid(h):
    if (h.magic,h.version,h.recordBytes,h.headerBytes)!=(MAGIC,1,128,128):raise ValueError('Effect wire header/version')
    if h.hardBytes!=HARD or not h.frequency or not 0<h.durationMs<=90000:raise ValueError('Effect wire bounds')
def header_at(address):
    h=Header.from_buffer_copy(C.string_at(address+256,128));valid(h)
    return {n:int(getattr(h,n)) for n,_ in Header._fields_ if n!='reserved'}

def hook_phase_at(address):
    return C.c_uint32.from_address(address+256+Header.reserved.offset).value
def analyze(path, *, allow_unfinalized=False):
    path=Path(path);size=path.stat().st_size
    if not 128<=size<=HARD or (size-128)%128:raise ValueError('Effect file alignment/size')
    counts=collections.Counter();issues=collections.Counter();owners={};scopes={};requests={};chunks={};images={};polygons=[];stopped=[];stats=[];last=0
    quad_samples={}
    batches={}
    with path.open('rb') as f:
        h=Header.from_buffer_copy(f.read(128));valid(h)
        unfinalized = allow_unfinalized and (h.status,h.error,h.fileBytes,h.written)==(1,0,0,0)
        if unfinalized:
            issues['unfinalized_trace']+=1
        elif h.fileBytes!=size:raise ValueError('Effect final file size')
        for raw in iter(lambda:f.read(128),b''):
            seq,qpc,kind,thread,obj,manager,*a=RECORD.unpack(raw)
            if seq<=last or not 64<=kind<64+len(NAMES):raise ValueError('Effect sequence/kind')
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
            elif kind in (77,78):
                sample,token=a[:2]
                if not 1<=sample<=16:raise ValueError('Effect quad sample bound')
                active=stack[-1] if stack else None
                if not active or not active['good'] or (active['owner'],active['manager'],active['token'])!=(obj,manager,token):
                    issues['unqualified_quad_payload']+=1;continue
                key=(sample,thread,obj,manager,token)
                target=quad_samples.setdefault(key,dict(corners={},result=None))
                if kind==77:
                    index=a[2]
                    if index>=4 or index in target['corners']:raise ValueError('Effect quad corner order')
                    target['corners'][index]=struct.unpack('<16I',struct.pack('<8Q',*a[3:]))
                elif target['result'] is not None or active['epoch']!=a[2]:raise ValueError('Effect quad result identity')
                else:target['result']=dict(sequence=seq,epoch=a[2],resource_id=a[3],flags=a[4],native_return=a[5])
            elif 79<=kind<=84:
                sample,token=a[:2]
                if sample!=1 or not token:raise ValueError('Effect batch sample identity')
                key=(sample,thread,obj,manager,token)
                batch=batches.setdefault(key,dict(span=None,flush=None,present=None,vertices={},indices={},states={}))
                if kind==79:
                    epoch,resource,first,count,corners=a[2:7]
                    if batch['span'] or not (3<=corners<=16 and count==(corners-2)*3 and first%3==0 and first+count<=216):
                        raise ValueError('Effect batch span')
                    batch['span']=(epoch,resource,first,count)
                    continue
                order=a[2]
                if not order or not batch['span'] or batch.setdefault('order',order)!=order:
                    raise ValueError('Effect batch flush identity')
                if kind in (80,81):
                    index=a[3]
                    values=batch['vertices' if kind==80 else 'indices']
                    if index>=batch['span'][3] or index in values or batch['flush']:raise ValueError('Effect batch index order')
                    values[index]=a[4:8] if kind==80 else a[4]
                elif kind==82:
                    device,vertices,triangles,topology=a[3:7]
                    if batch['flush'] or topology!=4 or not device or not 0<triangles<=72 or not 0<vertices<=216:
                        raise ValueError('Effect batch draw bounds')
                    batch['flush']=(seq,vertices,triangles)
                    batch['scene']=a[7]
                elif kind==83:
                    state=(a[3],a[4])
                    if not batch['flush'] or batch['present'] or state in batch['states'] or len(batch['states'])>=23:
                        raise ValueError('Effect batch state order')
                    batch['states'][state]=a[5:11]
                elif kind==84:
                    if not batch['flush'] or batch['present'] or not a[3] or a[5]!=batch['scene']:
                        raise ValueError('Effect batch presentation order')
                    batch['present']=a[3:5]
    records=sum(counts.values())
    if not unfinalized and h.written!=records:raise ValueError('Effect record count')
    if chunks:issues['incomplete_filename']+=len(chunks)
    if any(scopes.values()):issues['unfinished_scope']+=1
    if h.dropped:issues['record_loss']+=h.dropped
    if h.status!=3 or h.error or not stopped or any(e or active for e,active in stopped):issues['cleanup_unconfirmed']+=1
    if not unfinalized and h.reason not in (1,3):issues['capture_limit_or_setup_failure']+=1
    if stats and (stats[-1][0] or stats[-1][1] or stats[-1][4]):issues['native_fault_or_identity_uncertainty']+=1
    joined=collections.defaultdict(set)
    bindings=collections.defaultdict(set)
    for r in requests.values():
        name=images.get((r['manager'],r['resource_id'],r['signature']))
        if r['qualified'] and name:
            key=(r['owner'],r['epoch'],r['scope'],r['manager'],r['resource_id'])
            joined[key].add(name)
            bindings[key].add((name,r['signature'][-1]))
    qualified=0;assignments={}
    for p in polygons:
        names=joined[(p['owner'],p['epoch'],p['scope'],p['manager'],p['resource_id'])]
        if p['qualified'] and len(names)==1:
            qualified+=1;assignments[(p['owner'],p['epoch'],p['resource_id'],next(iter(names)))]=True
    if not qualified:issues['no_joined_native_polygon']+=1
    samples=[]
    for (sample,thread,obj,manager,token),value in sorted(quad_samples.items()):
        result=value['result']
        if not result or len(value['corners'])!=4:
            issues['incomplete_quad_payload']+=1;continue
        names=joined[(obj,result['epoch'],token,manager,result['resource_id'])]
        samples.append(dict(result,sample=sample,thread=thread,scope=token,
                            filename=next(iter(names)) if len(names)==1 else None,
                            preclip_corner_words=[value['corners'][i] for i in range(4)]))
    batch_draws=[]
    for key,batch in batches.items():
        result=quad_samples.get(key,{}).get('result')
        if not (result and batch['span'] and batch['flush'] and batch['present']):
            issues['incomplete_batch_span']+=1
            continue
        epoch,resource,first,count=batch['span']
        flush_sequence,vertex_count,triangles=batch['flush']
        if result['epoch']!=epoch or result['resource_id']!=resource or first+count>triangles*3:
            raise ValueError('Effect batch provenance mismatch')
        if len(batch['indices'])!=count or len(batch['vertices'])!=count:
            issues['incomplete_batch_payload']+=1
            continue
        indices=[batch['indices'][i] for i in range(count)]
        if any(i>=vertex_count for i in indices):raise ValueError('Effect batch index range')
        present_sequence,present_result=batch['present']
        binding=batch['states'].get((2,0))
        resource_bindings=bindings[(key[2],epoch,key[-1],key[3],resource)]
        bound_name=None
        if binding and binding[0] and not binding[1] and binding[4]==resource and len(resource_bindings)==1:
            name,surface=next(iter(resource_bindings))
            if binding[0]==surface:bound_name=name
        batch_draws.append(dict(sample=key[0],epoch=epoch,scope=key[-1],resource_id=resource,first_index=first,
          thread=key[1],manager=key[3],
          bound_filename=bound_name,
          native_scene_ordinal=batch['scene'] or None,
          indices=indices,vertex_words=[batch['vertices'][i] for i in range(count)],flush_order=batch['order'],
          flush_sequence=flush_sequence,present_sequence=present_sequence,present_result=present_result,
          native_state=[dict(kind=k,selector=s,words=words) for (k,s),words in batch['states'].items()]))
    return dict(probe='EFFECT-RESOURCE-JOIN-001',sha256=digest(path),bytes=size,records=records,counts=dict(counts),issues=dict(issues),
                result='PARTIAL' if issues else 'NATIVE_EFFECT_RESOURCE_JOIN_OBSERVED',header={n:int(getattr(h,n)) for n,_ in Header._fields_ if n!='reserved'},
                qualified_native_polygons=qualified,assignments=[dict(owner=k[0],epoch=k[1],resource_id=k[2],filename=k[3]) for k in assignments],
                native_statistics=stats,stopped=stopped,quad_samples=samples,batch_draws=batch_draws,
                limitations=['Batch records observe native draw arguments and state before flush; HRESULT and translated GPU output are not observed','Quad words are preclip samples','Resource snapshot identity,not unobserved allocation epoch','Not an effects renderer or universal effect classification'])


RENDER_STATES={
    7:'z_enable',14:'z_write_enable',15:'alpha_test_enable',19:'src_blend',
    20:'dest_blend',22:'cull_mode',23:'z_func',24:'alpha_ref',25:'alpha_func',
    27:'alpha_blend_enable',41:'color_key_enable',
}
TEXTURE_STATES={
    1:'color_op',2:'color_arg1',3:'color_arg2',4:'alpha_op',5:'alpha_arg1',
    6:'alpha_arg2',13:'address_u',14:'address_v',16:'mag_filter',17:'min_filter',18:'mip_filter',
}


def read_native_draw(path):
    """Decode the observed Device3 draw span without a graphics device."""
    report=analyze(path)
    if report['issues'] or len(report['batch_draws'])!=1:
        raise ValueError('One complete native draw observation is required')
    draw=report['batch_draws'][0]
    if not draw['bound_filename'] or draw['present_result']!=1:
        raise ValueError('Native texture binding or presentation is unverified')
    states={(row['kind'],row['selector']):row['words'] for row in draw['native_state']}
    expected={(0,k) for k in RENDER_STATES}|{(1,k) for k in TEXTURE_STATES}|{(2,0)}
    if states.keys()!=expected or any(words[1] for words in states.values()):
        raise ValueError('Native draw state readback is incomplete')
    binding=states[2,0]
    if not binding[2] or binding[3]:
        raise ValueError('Native render target readback is incomplete')

    vertices={}
    for index,words in zip(draw['indices'],draw['vertex_words']):
        packed=struct.pack('<4Q',*words)
        if index in vertices and vertices[index]!=packed:
            raise ValueError('Conflicting native vertex bytes for one index')
        vertices[index]=packed
    decoded=[]
    for index,packed in sorted(vertices.items()):
        x,y,z,rhw,diffuse,specular,u,v=struct.unpack('<4f2I2f',packed)
        if not all(math.isfinite(n) for n in (x,y,z,rhw,u,v)):
            raise ValueError('Non-finite native vertex')
        decoded.append(dict(batch_index=index,screen_xy=[x,y],depth=z,rhw=rhw,
                            diffuse_argb=diffuse,specular_argb=specular,uv=[u,v]))
    return dict(
        trace_sha256=report['sha256'],owner_epoch=draw['epoch'],scope=draw['scope'],
        flush_order=draw['flush_order'],flush_record=draw['flush_sequence'],
        native_scene_ordinal=draw['native_scene_ordinal'],
        engine_present_ordinal=draw['present_sequence'],first_batch_index=draw['first_index'],
        topology='triangle_list',coordinate_space='native_pretransformed_screen',
        indices=draw['indices'],vertices=decoded,
        texture=dict(filename=draw['bound_filename'],run_local_resource_id=draw['resource_id'],
                     native_upload_orientation=None),
        render_state={name:states[0,k][0] for k,name in RENDER_STATES.items()},
        texture_stage_0={name:states[1,k][0] for k,name in TEXTURE_STATES.items()},
        draw_hresult=None,
    )


if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Inspect one complete native effect draw offline.')
    parser.add_argument('trace',type=Path)
    print(json.dumps(read_native_draw(parser.parse_args().trace),indent=2))
