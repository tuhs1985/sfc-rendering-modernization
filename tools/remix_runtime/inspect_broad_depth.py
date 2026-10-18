"""Offline depth/binding lifetime and presentation-order inspection; no GPU calls."""
from pathlib import Path
import argparse
import collections
import ctypes as C
import json
import broad_capture as b

def inspect(path):
    path=Path(path);base=b.analyze(path)
    resources={};views={};contexts={};queues={};history=[];view_history=[]
    draws=collections.Counter();depth_rows={};edges=collections.Counter()
    present=collections.Counter();backbuffers=collections.Counter();samples=[];last_depth={};last_unbind={};last_transfer={}
    overflow=0;bound_states=collections.Counter()
    binding_window=collections.Counter();frames={};frame_totals=collections.Counter()
    with path.open('rb') as f:
        h=b.Header.from_buffer_copy(f.read(128))
        while raw:=f.read(128):
            seq,qpc,kind,thread,obj,dev,*a=b.RECORD.unpack(raw)
            if kind==3:
                r={'device':dev,'resource':obj,'creation_sequence':seq,'creation_qpc':qpc,'type':a[0],'usage':a[1],'flags':a[3],'width_or_size':a[5],'height_or_stride':a[6],'format':a[9],'samples':a[10],'end_sequence':None}
                if len(history)<65536:resources[dev,obj]=r;history.append(r)
                else:overflow+=1
            elif kind==4:
                r=resources.pop((dev,obj),None)
                if r:r['end_sequence']=seq
            elif kind==5:
                v={'device':dev,'view':obj,'creation_sequence':seq,'resource':a[0],'resource_creation_sequence':resources.get((dev,a[0]),{}).get('creation_sequence'),'usage':a[1],'type':a[2],'format':a[3],'range':a[4:8],'end_sequence':None}
                if len(view_history)<65536:views[dev,obj]=v;view_history.append(v)
                else:overflow+=1
            elif kind==6:
                v=views.pop((dev,obj),None)
                if v:v['end_sequence']=seq
            elif kind==2:
                for mapping in (resources,views,contexts,queues,last_depth,last_unbind,last_transfer,frames):
                    for key in [key for key in mapping if key[0]==dev]:del mapping[key]
            elif kind in (8,9):contexts.pop((dev,obj),None)
            elif kind in (10,20,21):
                key=(dev,obj)
                if key not in contexts:
                    if len(contexts)>=4096:overflow+=1;continue
                    contexts[key]={'dsv':0,'rtvs':[],'depth_pipeline':None,'depth_states':{}}
                c=contexts[key]
                if kind==10:
                    c['dsv']=a[1];c['rtvs']=a[2:2+min(a[0],8)]
                    if a[1]:binding_window['before_gate' if qpc<h.gateQpc else 'after_gate']+=1
                    if not a[1]:last_unbind[dev,obj]={'sequence':seq,'qpc':qpc}
                elif kind==20 and a[0]&0x200:c['depth_pipeline']=a[1]
                elif kind==21 and a[0] in (7,14,23):c['depth_states'][a[0]]=a[1]
            elif kind in (11,12) and a[0] and a[1]:
                c=contexts.get((dev,obj),{});dsv=c.get('dsv',0)
                if len(frames)<4096 or (dev,obj) in frames:
                    frame=frames.setdefault((dev,obj),{'with_depth':0,'without_depth':0,'tail_unbound':0})
                    frame['with_depth' if dsv else 'without_depth']+=1
                    if dsv:frame['tail_unbound']=0
                    elif frame['with_depth']:frame['tail_unbound']+=1
                else:overflow+=1
                draws['with_depth' if dsv else 'without_depth']+=1
                if dsv:
                    v=views.get((dev,dsv),{});creation=v.get('creation_sequence',0)
                    key=(dev,dsv,creation)
                    if len(depth_rows)>=4096 and key not in depth_rows:overflow+=1;continue
                    row=depth_rows.setdefault(key,{'device':dev,'view':dsv,'view_creation_sequence':creation,'draws':0,'indexed':0,'nonindexed':0,'first_sequence':seq,'last_sequence':seq,'pipeline_handles':collections.Counter(),'dynamic_depth_states':collections.Counter()})
                    row['draws']+=1;row['indexed' if kind==12 else 'nonindexed']+=1;row['last_sequence']=seq
                    row['pipeline_handles'][c.get('depth_pipeline')]+=1
                    state=tuple(c.get('depth_states',{}).get(n) for n in (7,14,23))
                    row['dynamic_depth_states'][state]+=1
                    last_depth[dev,obj]={'sequence':seq,'qpc':qpc,'view':dsv,'creation_sequence':creation}
                    bound_states['dynamic_complete' if all(n is not None for n in state) else 'static_pipeline_state_not_captured']+=1
            elif kind in (15,16,17):
                src,dst=a[:2];sr=resources.get((dev,src),{});dr=resources.get((dev,dst),{})
                key=(kind,dev,src,sr.get('creation_sequence'),dst,dr.get('creation_sequence'))
                if len(edges)<4096 or key in edges:edges[key]+=1
                else:overflow+=1
                last_transfer[dev,obj]={'sequence':seq,'qpc':qpc,'kind':b.NAMES[kind],'source':src,'dest':dst}
            elif kind==22:
                if len(queues)<4096 or (dev,a[0]) in queues:queues[dev,a[0]]=obj
                else:overflow+=1
            elif kind==18:
                if len(backbuffers)<4096 or (dev,a[1]) in backbuffers:backbuffers[dev,a[1]]+=1
                else:overflow+=1
                context=queues.get((dev,obj));c=contexts.get((dev,context))
                if c is None:present['unmapped_context']+=1
                elif c.get('dsv'):present['depth_bound']+=1
                else:present['depth_unbound']+=1
                d=last_depth.get((dev,context));u=last_unbind.get((dev,context));t=last_transfer.get((dev,context))
                if d and u and d['sequence']<u['sequence']<seq:present['latest_depth_draw_then_unbind_before_present']+=1
                frame=frames.pop((dev,context),None)
                if frame and frame['with_depth']:
                    frame_totals['frames_with_depth_draws']+=1
                    frame_totals['unbound_draws_after_last_depth_draw']+=frame['tail_unbound']
                    if frame['tail_unbound']==2:frame_totals['frames_with_exactly_two_unbound_tail_draws']+=1
                if len(samples)<3:samples.append({'present_sequence':seq,'present_qpc':qpc,'queue':obj,'context':context,'last_depth_draw':d,'last_depth_unbind':u,'last_transfer':t})
                # Never let an earlier frame's draw qualify a later empty frame.
                for mapping in (last_depth,last_unbind,last_transfer):mapping.pop((dev,context),None)
    rs={(r['device'],r['creation_sequence']):r for r in history}
    out=[]
    for row in depth_rows.values():
        dev=row['device'];v=next((v for v in view_history if v['device']==dev and v['creation_sequence']==row['view_creation_sequence']),None)
        r=rs.get((dev,v['resource_creation_sequence'])) if v else None
        row['view_descriptor']=v;row['resource_descriptor']=r
        row['related_views']=[x for x in view_history if r and x['device']==dev and x['resource_creation_sequence']==r['creation_sequence']]
        row['pipeline_handles']=[{'handle':handle,'draws':n} for handle,n in row['pipeline_handles'].items()]
        row['dynamic_depth_states']=[{'enable_write_compare':values,'draws':n} for values,n in row['dynamic_depth_states'].items()]
        out.append(row)
    transfers=[]
    for (kind,dev,src,sc,dst,dc),n in edges.items():transfers.append({'kind':b.NAMES[kind],'count':n,'device':dev,'source':src,'dest':dst,'dest_is_presented_backbuffer':(dev,dst) in backbuffers,'source_descriptor':rs.get((dev,sc)),'dest_descriptor':rs.get((dev,dc))})
    return {'source':str(path),'source_sha256':b.digest(path),'base_result':base['result'],'gate_qpc':h.gateQpc,'frequency':h.frequency,'tactical_seconds':(h.endQpc-h.gateQpc)/h.frequency if h.gateQpc else None,'draws':dict(draws),'present':dict(present),'frame_totals':dict(frame_totals),'depth_binding_window':dict(binding_window),'presented_backbuffers':[{'device':dev,'resource':r,'presents':n} for (dev,r),n in backbuffers.items()],'depth_state_coverage':dict(bound_states),'depth_paths':out,'transfers':transfers,'sample_presentations':samples,'analysis_overflow':overflow,'limits':'65536resource/view histories;4096contexts/queues/edge groups/depth paths; raw retained','unqualified':'Depth values,static depth-pipeline descriptors,HUD/owner identity and GPU usability not captured; deferred command replay not reconstructed'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('trace',type=Path);a=p.parse_args()
    result=inspect(a.trace);output=a.trace.with_suffix('.depth-path.json')
    output.write_text(json.dumps(result,indent=2));print(str(output))
