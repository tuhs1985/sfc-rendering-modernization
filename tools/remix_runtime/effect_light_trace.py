"""Opt-in worker evidence from successful Remix submissions;no game-thread IO."""
import ctypes as C
import json
import math
from pathlib import Path
import struct
import threading
from effect_lights import SOURCE_OFFSET
OFFSET=SOURCE_OFFSET+65536
MAGIC=0x31544c45
FRAMES,CELL_BYTES,FRAME_BYTES,STORE_BYTES=16,6976,6944,111680
LIMIT=4*1024*1024

def initialize(channel,pid):
    if not pid:raise ValueError('Effect trace requires game identity')
    session=[int(channel.name[-32:][i:i+8],16) for i in range(0,32,8)]
    raw=bytearray(STORE_BYTES);struct.pack_into('<8I',raw,0,MAGIC,1,STORE_BYTES,*session,pid)
    struct.pack_into('<I',raw,40,1);channel.write(OFFSET,bytes(raw))

def decode(raw,pid):
    if len(raw)!=FRAME_BYTES:raise ValueError('Effect trace frame size')
    frame,owner,generation,usable,source,submitted=struct.unpack_from('<4I2Q',raw)
    if not frame or owner!=pid or usable not in (0,1) or not submitted:raise ValueError('Effect trace frame identity')
    native_frame,manager,thread,gate,captured=struct.unpack_from('<4IQ',raw,32)
    if usable and (not generation or frame!=native_frame or captured!=source or not source):raise ValueError('Effect trace source association')
    entries=[]
    for i,status in enumerate(struct.unpack_from('<62i',raw,4216)):
        if status not in (-1,0,1):raise ValueError('Effect trace status')
        slot=i+2;words=struct.unpack_from('<16I',raw,56+slot*64);values=struct.unpack_from('<2I8f',raw,4464+i*40)
        if status==1:
            if not usable:raise ValueError('Effect trace active light without qualified source')
            if values[0]!=slot or values[1] not in (1,5) or not all(math.isfinite(x) for x in values[2:]):raise ValueError('Effect trace submitted values')
            if any(x<0 for x in values[5:8]) or values[8]<=0 or values[9]<=0 or words[0]!=values[1]:raise ValueError('Effect trace radiance/range/type')
        entries.append(dict(slot=slot,status=status,native_words=list(words),
            submitted=dict(type=values[1],position=list(values[2:5]),radiance=list(values[5:8]),native_range=values[8],radius=values[9]) if status==1 else None))
    return dict(frame=frame,pid=pid,generation=generation,usable=usable,source_qpc=source,submitted_qpc=submitted,
                manager=manager,thread=thread,gate=gate,enables=raw[4152:4216].hex(),slots=entries)

class Recorder:
    def __init__(self,channel,folder,pid):
        self.channel=channel;self.folder=Path(folder);self.pid=pid;initialize(channel,pid)
        self.stop_event=threading.Event();self.last_frame=0;self.previous={};self.context=None
        self.summary=dict(records=0,bytes=0,frames_observed=0,active_slot_observations=0,omitted_records=0,
            invalid_reads=0,unstable_reads=0,unobserved_frame_numbers=0,error=None,limit_bytes=LIMIT,
            scope='Successful Remix DrawLightInstance parameters;not final-pixel or SFC presentation proof')
        self.file=(self.folder/'effect-light-submissions.jsonl').open('wb')
        self.thread=threading.Thread(target=self.run,name='effect-light-evidence',daemon=True);self.thread.start()
    def drain(self):
        h=struct.unpack('<8I',self.channel.read(OFFSET,32))
        expected=tuple(int(self.channel.name[-32:][i:i+8],16) for i in range(0,32,8))
        if h!=(MAGIC,1,STORE_BYTES,*expected,self.pid):raise ValueError('Effect trace session/PID changed')
        samples=[]
        for i in range(FRAMES):
            at=OFFSET+64+i*CELL_BYTES;guard=struct.unpack('<I',self.channel.read(at,4))[0]
            if not guard or guard&1:continue
            if struct.unpack('<I',self.channel.read(at+16,4))[0]<=self.last_frame:continue
            raw=self.channel.read(at+16,FRAME_BYTES)
            if self.channel.read(at,4)!=struct.pack('<I',guard):self.summary['unstable_reads']+=1;continue
            try:value=decode(raw,self.pid)
            except ValueError:self.summary['invalid_reads']+=1;continue
            if value['frame']>self.last_frame:samples.append(value)
        for value in sorted(samples,key=lambda x:x['frame']):self.accept(value)
    def accept(self,value):
        frame=value['frame']
        if frame<=self.last_frame:return
        if self.last_frame:self.summary['unobserved_frame_numbers']+=max(0,frame-self.last_frame-1)
        self.last_frame=frame;self.summary['frames_observed']+=1
        self.summary['active_slot_observations']+=sum(x['status']==1 for x in value['slots']);changed=[]
        for item in value['slots']:
            words=item['native_words'];key=(item['status'],words[0],tuple(words[4:11]),json.dumps(item['submitted'],sort_keys=True))
            if self.previous.get(item['slot'])!=key:changed.append(item);self.previous[item['slot']]=key
        context=(value['generation'],value['usable'],value['gate'],value['enables'])
        if not changed and context==self.context:return
        self.context=context;raw=(json.dumps({**value,'slots':changed},separators=(',',':'),allow_nan=False)+'\n').encode()
        if self.summary['bytes']+len(raw)>LIMIT:self.summary['omitted_records']+=1;return
        self.file.write(raw);self.summary['bytes']+=len(raw);self.summary['records']+=1
    def run(self):
        try:
            while not self.stop_event.is_set():self.drain();self.stop_event.wait(.01)
            self.drain()
        except Exception as exc:self.summary['error']=str(exc)[:1024]
        finally:self.file.close()
    def close(self):
        self.stop_event.set();self.thread.join(5)
        if self.thread.is_alive():raise RuntimeError('Effect evidence worker still owns channel')
        C.c_uint32.from_address(self.channel.view+OFFSET+40).value=0
        (self.folder/'effect-light-submissions-summary.json').write_text(json.dumps(self.summary,indent=2));return self.summary
