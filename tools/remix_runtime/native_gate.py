"""Version1 native pre-suppression gate evidence;renderer-independent frame timing."""
import hashlib,json,struct,threading,math
from pathlib import Path
from player_replacement import ROOT,OFFSET as BASE
OFFSET=BASE+50176
CAPACITY=64
SIZE=8576
LIMIT=8*1024*1024
MAGIC=0x3147544e
RECEIPT=ROOT/'artifacts/player-replacement/native-gate-tests/qualification.json'

def header(raw):
    if len(raw)!=256:raise ValueError('Gate header length')
    v=struct.unpack('<10I16i2I6Q96s',raw)
    if v[:3]!=(MAGIC,1,SIZE) or not v[3] or v[8] not in (1,2) or not v[9] or not v[29]:raise ValueError('Gate header identity/layout')
    names=('stop','error','frame','thread','written','read','dropped','requests','commits','misses','stale','invalid','stop_wakes','active','max_active','partial')
    result=dict(zip(names,v[10:26]));result.update(pid=v[3],session=list(v[4:8]),policy=v[8],generation=v[9],frequency=v[29])
    if not 0<=result['written']-result['read']<=CAPACITY:raise ValueError('Gate ring cursors')
    return result

def record(raw):
    if len(raw)!=128:raise ValueError('Gate record length')
    v=struct.unpack('<12IQ2I8Q',raw)
    names=('frame','owner','revision','policy','outcome','queue','generation','resource_epoch','reason','primary','secondary','flags','offered','pending_source_slots','pool_busy_total','start','entered','ready','inserted','ended','presented','sequence','hash')
    result=dict(zip(names,v))
    if not result['frame'] or result['policy'] not in (1,2) or not result['start'] or result['presented']<result['start']:raise ValueError('Gate record clock/frame')
    if result['outcome']==2 and (not result['owner'] or not result['sequence'] or not result['hash'] or not result['inserted'] or not result['ready']):raise ValueError('Gate commit missing identity/completion')
    return result

def stats(values):
    v=sorted(values)
    return dict(samples=len(v),median=v[len(v)//2],p95=v[min(len(v)-1,math.ceil(len(v)*.95)-1)],p99=v[min(len(v)-1,math.ceil(len(v)*.99)-1)],maximum=v[-1]) if v else dict(samples=0)

class Capture:
    def __init__(self,channel,folder,session):
        self.channel=channel;self.folder=Path(folder);self.session=session;self.stop=threading.Event();self.error=None;self.latest=None;self.omitted=0
        self.thread=threading.Thread(target=self.run,name='native-gate-evidence',daemon=True);self.thread.start()
    def drain(self,out):
        raw=self.channel.read(OFFSET,256)
        if struct.unpack_from('<I',raw)[0]==0:return
        h=header(raw)
        if h['session']!=self.session:raise ValueError('Gate evidence session')
        for n in range(h['read'],h['written']):
            b=self.channel.read(OFFSET+384+(n%CAPACITY)*128,128);record(b)
            if out.tell()+128<=LIMIT:out.write(b)
            else:self.omitted+=1
        self.channel.write(OFFSET+60,struct.pack('<i',h['written']));self.latest=h
    def run(self):
        try:
            with (self.folder/'NATIVE-GATE-001.bin').open('wb') as out:
                while not self.stop.is_set():self.drain(out);self.stop.wait(.01)
                self.drain(out)
        except Exception as exc:self.error=str(exc)
    def finish(self):
        self.stop.set();self.thread.join(5)
        if self.thread.is_alive():raise RuntimeError('Gate evidence worker still owns mapping')
        result=analyze(self.folder,self.latest);result.update(error=self.error,detail_omitted=self.omitted)
        (self.folder/'NATIVE-GATE-001.json').write_text(json.dumps(result,indent=2));return result

def analyze(folder,h):
    rows=[]
    with (Path(folder)/'NATIVE-GATE-001.bin').open('rb') as f:
        while b:=f.read(128):rows.append(record(b))
    if not h:return dict(result='PARTIAL',records=0,header=None)
    frequency=h['frequency'];scale=1000/frequency
    # Diagnostic fixture pixel readbacks are marked and excluded from clean
    # timing distributions,not deleted from the evidence or correctness totals.
    measured=[r for r in rows if r['flags']&16] or rows
    clean=[r for r in measured if not r['flags']&2 and r['entered']]
    pairs=[(a,b) for a,b in zip(measured,measured[1:]) if not (a['flags']|b['flags'])&2]
    waits=[(r['ended']-r['entered'])*scale for r in clean if r['ended']>=r['entered']]
    periods=[(b['presented']-a['presented'])*scale for a,b in pairs if b['presented']>=a['presented']]
    ages=[(r['presented']-r['offered'])*scale for r in clean if r['offered']]
    longest=current=0
    for r in clean:
        current=current+1 if r['outcome']!=2 else 0;longest=max(longest,current)
    rolling=[]
    reference_drift=[]
    if measured:
        base=measured[0]['presented']
        origin=measured[0]
        reference_drift=[(r['start']-origin['start'])*scale-(r['frame']-origin['frame'])*1000/60 for r in measured]
        bins={}
        for r in measured:bins.setdefault(int((r['presented']-base)/frequency/5),[]).append(r)
        for bucket,v in sorted(bins.items()):
            samples=[(r['presented']-r['offered'])*scale for r in v if r['offered'] and not r['flags']&2]
            drift=(v[-1]['start']-origin['start'])*scale-(v[-1]['frame']-origin['frame'])*1000/60
            rolling.append(dict(second=bucket*5,frames=len(v),commits=sum(r['outcome']==2 for r in v),max_queue=max(r['queue'] for r in v),max_pending_source_slots=max(r['pending_source_slots'] for r in v),source_age_ms=stats(samples),reference_schedule_drift_ms=drift))
    return dict(result='COMPARISON_REQUIRES_REVIEW',records=len(rows),measurement_frames=len(measured),header=h,policy='Strict' if h['policy']==1 else 'ExtraFrame',
        commits=sum(r['outcome']==2 for r in rows),original_frames=sum(r['outcome']!=2 for r in rows),
        measured_commits=sum(r['outcome']==2 for r in measured),measured_fallbacks=sum(r['outcome']!=2 for r in measured),
        injected_overruns=sum(bool(r['flags']&4) for r in measured),injected_representative_delays=sum(bool(r['flags']&8) for r in measured),
        longest_requested_fallback=longest,gate_wait_ms=stats(waits),frame_period_ms=stats(periods),
        actual_game_pool_ready_ms=stats([(r['ready']-r['start'])*scale for r in clean if r['ready']]),
        continuation_after_insertion_ms=stats([(r['presented']-r['inserted'])*scale for r in clean if r['inserted']]),
        source_to_display_ms=stats(ages),native_frame_elapsed_ms=stats([(r['presented']-r['start'])*scale for r in measured if not r['flags']&2]),
        maximum_slot_occupancy=max((r['queue'] for r in rows),default=0),rolling=rolling,
        maximum_pending_source_slots=max((r['pending_source_slots'] for r in rows),default=0),maximum_pending_gate_requests=h['max_active'],
        reference_schedule_drift_ms=stats(reference_drift),final_reference_schedule_drift_ms=reference_drift[-1] if reference_drift else None,
        timing_note='Present callback timestamps;actual display scanout/input latency not measured. Cold preparation and fixture readbacks are retained and identified.')

def require_qualification(policy):
    q=json.loads(RECEIPT.read_text())
    if q['result']!='NATIVE_GATE_COMPARISON_PREPARED' or policy not in q['policies']:raise ValueError('Native gate comparison not qualified')
    for name,sha in q['files'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest().upper()!=sha:raise ValueError('Native gate input changed: '+name)
    from async_material_checkout import backend_inputs,receipt
    return dict(q,backend_inputs=receipt(backend_inputs()))
