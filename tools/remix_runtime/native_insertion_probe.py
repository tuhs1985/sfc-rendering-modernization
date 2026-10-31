"""Metadata-only native scene boundary observation; never replacement authority."""
from pathlib import Path
from collections import Counter
import hashlib,json,struct,threading
from player_replacement import OFFSET as BASE,ROOT

OFFSET=BASE+16384
CAPACITY=256
RECORD=128
SIZE=128+CAPACITY*RECORD
LIMIT=8*1024*1024
MAGIC=0x3142494e
KINDS={1:'frame_begin',2:'model_begin',3:'model_end',4:'source_published',5:'native_draw',6:'present',7:'output_discarded'}
PHASES={0:'before_selected',1:'inside_selected',2:'after_selected',3:'other_model'}
RECEIPT=ROOT/'artifacts/player-replacement/native-insertion-tests/qualification.json'

def header(raw):
    if len(raw)!=128:raise ValueError('Insertion header length')
    h=struct.unpack('<32I',raw)
    if h[:3]!=(MAGIC,1,SIZE) or not h[3] or not struct.unpack_from('<Q',raw,104)[0]:
        raise ValueError('Insertion schema/pid/frequency')
    if h[8]<h[9] or h[8]-h[9]>CAPACITY:raise ValueError('Insertion ring cursors')
    return dict(pid=h[3],session=list(h[4:8]),written=h[8],read=h[9],dropped=h[10],wrong_thread=h[11],
                stopped=h[12],error=h[13],thread=h[14],frame=h[16],owner=h[17],revision=h[18],
                frequency=struct.unpack_from('<Q',raw,104)[0],outputs=h[28])

def event(raw,ordinal):
    if len(raw)!=128 or struct.unpack_from('<I',raw,124)[0]!=ordinal:raise ValueError('Insertion event commit')
    a=struct.unpack_from('<8I5Q14I',raw)
    if a[0] not in KINDS or a[4] not in PHASES or not all(a[i] for i in (1,2,3,8)):
        raise ValueError('Insertion event identity')
    names=('kind','frame','owner','revision','phase','model','source','manager','qpc','target','depth','output_qpc','source_qpc',
           'width','height','target_format','depth_format','view_format','samples','depth_enabled','depth_write','depth_func',
           'output_frame','output_sequence','flags','caller','committed')
    return dict(zip(names,a))

class Capture:
    """Single external consumer. Stops before the shared channel is closed."""
    def __init__(self,channel,folder,session=None):
        self.channel=channel;self.folder=Path(folder);self.expected=session
        self.stop_event=threading.Event();self.error=None;self.count=0;self.discarded_detail=0;self.latest=None
        self.kinds=Counter();self.targets=Counter();self.readiness=Counter();self.ends={};self.source_leads=[]
        self.thread=threading.Thread(target=self._run,name='native-boundary-evidence',daemon=True)
        self.thread.start()

    def drain(self,stream):
        raw=self.channel.read(OFFSET,128)
        if struct.unpack_from('<I',raw)[0]==0:return
        h=header(raw)
        if self.expected is None:self.expected=h['session']
        if h['session']!=self.expected:raise ValueError('Insertion session changed')
        if self.latest and (h['pid']!=self.latest['pid'] or (self.latest['thread'] and h['thread']!=self.latest['thread'])):raise ValueError('Insertion producer changed')
        for index in range(h['read'],h['written']):
            b=self.channel.read(OFFSET+128+(index%CAPACITY)*RECORD,RECORD);e=event(b,index+1)
            self.count+=1;self.kinds[KINDS[e['kind']]]+=1
            if e['kind']==5:
                key=tuple(e[n] for n in ('phase','width','height','target_format','depth_format','view_format','samples','depth_enabled','depth_write','depth_func','caller'))
                self.targets[key]+=1
            if e['flags']&1:
                self.readiness[(PHASES[e['phase']],e['kind'],e['frame']-e['output_frame'])]+=1
            if e['kind']==3:self.ends[e['frame']]=e['qpc']
            if e['kind']==6:
                end=self.ends.pop(e['frame'],None)
                if end and len(self.source_leads)<8192:self.source_leads.append((e['qpc']-end)*1000/h['frequency'])
            # Bounded current-frame bookkeeping even if Present is absent.
            if len(self.ends)>256:self.ends.pop(next(iter(self.ends)))
            if stream.tell()+RECORD<=LIMIT:stream.write(b)
            else:self.discarded_detail+=1
        # Acknowledge only copied records. Producer uses an Interlocked read.
        self.channel.write(OFFSET+36,struct.pack('<I',h['written']))
        self.latest=h

    def _run(self):
        try:
            with (self.folder/'NATIVE-INSERTION-001.events.bin').open('wb') as stream:
                while not self.stop_event.is_set():self.drain(stream);self.stop_event.wait(.01)
                self.drain(stream)
        except Exception as exc:self.error=str(exc)

    def finish(self):
        self.stop_event.set();self.thread.join(5)
        if self.thread.is_alive():raise RuntimeError('Insertion evidence worker still owns channel')
        values=sorted(self.source_leads)
        result=dict(probe='NATIVE-INSERTION-001',result='OBSERVATION_REQUIRES_ANALYSIS',error=self.error,header=self.latest,
            events=self.count,detail_limit=LIMIT,detail_omitted=self.discarded_detail,kinds=dict(self.kinds),
            draw_states=[dict(state=list(k),count=v) for k,v in self.targets.items()],
            draw_state_fields=['phase','width','height','resource_format','depth_view_format','colour_view_format','samples','depth_enabled','depth_write','depth_func','native_caller'],
            output_readiness=[dict(phase=k[0],kind=KINDS[k[1]],source_frame_lag=k[2],count=v) for k,v in self.readiness.items()],
            model_end_to_present_ms=dict(samples=len(values),median=values[len(values)//2] if values else None,max=max(values) if values else None),
            interpretation='Output metadata availability is not a pose/camera/hash match or permission to suppress. Shared flushes are not owner-exclusive.',
            original_drawing_unchanged=True,shield_replay=False)
        (self.folder/'NATIVE-INSERTION-001.json').write_text(json.dumps(result,indent=2))
        return result

def require_qualification():
    q=json.loads(RECEIPT.read_text())
    if q['result']!='METADATA_ONLY_PROBE_TESTED':raise ValueError('Insertion probe qualification missing')
    for name,sha in q['files'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest().upper()!=sha:raise ValueError('Insertion observation input changed: '+name)
    from async_material_checkout import backend_inputs,receipt
    return dict(q,backend_inputs=receipt(backend_inputs()))
