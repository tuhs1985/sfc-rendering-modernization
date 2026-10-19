"""Worker-only light relay and ratio controls. No SFC writes or render callback IO."""
import ctypes as C
import hashlib
import json
from pathlib import Path
import struct
import time
import tomllib
from light_controls import validate,scales
from native_light_state import decode,SIZE

REGISTRY={f'native_directional_{i}':dict(kind='directional') for i in range(2)}
REGISTRY['project_fill']=dict(kind='directional',origin='project')
DEFAULT=Path(__file__).parent/'config/lights.toml'


def read_latest(path):
    """Bounded Windows snapshot read sharing delete/rename with the producer."""
    from ctypes import wintypes as W
    kernel=C.WinDLL('kernel32',use_last_error=True)
    kernel.CreateFileW.argtypes=[W.LPCWSTR,W.DWORD,W.DWORD,C.c_void_p,W.DWORD,W.DWORD,W.HANDLE]
    kernel.CreateFileW.restype=W.HANDLE
    kernel.ReadFile.argtypes=[W.HANDLE,C.c_void_p,W.DWORD,C.POINTER(W.DWORD),C.c_void_p]
    kernel.ReadFile.restype=W.BOOL
    kernel.CloseHandle.argtypes=[W.HANDLE];kernel.CloseHandle.restype=W.BOOL
    handle=kernel.CreateFileW(str(path),0x80000000,7,None,3,0x80,None)
    if handle==C.c_void_p(-1).value:raise C.WinError(C.get_last_error())
    try:
        data=C.create_string_buffer(SIZE+1);count=W.DWORD()
        if not kernel.ReadFile(handle,data,SIZE+1,C.byref(count),None):raise C.WinError(C.get_last_error())
        if count.value!=SIZE:raise ValueError('Latest native light snapshot size')
        return data.raw[:SIZE]
    finally:kernel.CloseHandle(handle)


def fnv(raw):
    value=14695981039346656037
    for b in raw:value=((value^b)*1099511628211)&0xffffffffffffffff
    return value


def packet(snapshot,selected,session,controls,scale,master,generation,observed,revision,shapes=False):
    if snapshot['session_words']!=session or snapshot['owner_epoch']!=selected['owner_epoch']:
        raise ValueError('Light session/owner mismatch')
    if not snapshot['global_gate_raw'] or snapshot['consumed_prefix']<2:
        raise ValueError('Native steady lighting not qualified')
    h=struct.pack('<12I2Q',0x3154474c,1,200,generation,*session,
                  snapshot['owner_epoch'],snapshot['model_process_local'],snapshot['source_process_local'],snapshot['frame'],observed,revision)
    rows=[]
    for i in range(2):
        slot=snapshot['slots'][i];control=controls[f'native_directional_{i}']
        v=slot['values']
        if slot['native_type']!=0 or not slot['consumed_by_native_response'] or v is None:
            raise ValueError('Unqualified native light type/state')
        import math
        direction=control.get('direction_override',v['direction_input'])
        length=math.hypot(*direction)
        scalar=v['type_dependent_scalar']
        if length<1e-8 or not 0<=scalar<=1000:raise ValueError('Invalid directional light')
        direction=[x/length for x in direction]
        multiplier=scale*master*control['intensity_multiplier']
        radiance=[v['contribution_channels'][j]*control['color_multiplier'][j]*scalar*multiplier for j in range(3)]
        if not all(math.isfinite(x) and 0<=x<=1e6 for x in radiance):raise ValueError('Mapped radiance bound')
        rows.append(struct.pack('<4I12f',i,int(control['enabled']),0,0,*direction,*radiance,
                    control.get('angular_diameter_degrees',.53),control['volumetric_multiplier'],scalar,multiplier,int(shapes),0))
    raw=h+b''.join(rows)
    return raw+struct.pack('<Q',fnv(raw))


class Relay:
    def __init__(self,folder,receiver,config=DEFAULT,tuning=False):
        self.folder=Path(folder);self.receiver=receiver;self.path=Path(config)
        self.offset=0;self.last_poll=0;self.last_config=0;self.last_digest=None;self.controls=None
        self.tuning=tuning
        from material_controls import Relay as MaterialRelay
        self.materials=MaterialRelay(folder)
        self.scale=self.master=1;self.revision=0;self.generation=0;self.messages=0
        self.accepted=0;self.rejected=0;self.last_native=None;self.observed=0
        self.publish_busy=0
        self.read_busy=0;self.read_recoveries=0;self.read_pending=False
        self.session=[int(receiver.name[-32:][i:i+8],16) for i in range(0,32,8)]

    def report(self,text):
        if self.messages<100:print('LIGHTS '+text,flush=True);self.messages+=1

    def reload(self):
        try:
            if self.path.stat().st_size>65536:raise ValueError('Config64KiB cap')
            raw=self.path.read_bytes();digest=hashlib.sha256(raw).hexdigest()
            if digest!=self.last_digest:
                data=tomllib.loads(raw.decode('utf-8'));rows=validate(data,REGISTRY)
                if not {'native_directional_0','native_directional_1'}.issubset({r['id'] for r in rows}):raise ValueError('Configure both native directional IDs')
                scale,master=scales(data)
                controls={r['id']:r for r in rows}
                from light_shapes import build
                shape_packet,manifest=build(controls,self.revision+1,self.folder,self.path.parent)
                pending=self.folder/'light-shapes.pending';pending.write_bytes(shape_packet)
                pending.replace(self.folder/'light-shapes.bin')
                (self.folder/'light-shapes-manifest.json').write_text(json.dumps(manifest,indent=2))
                self.controls={r['id']:r for r in rows};self.scale,self.master=scale,master
                self.last_digest=digest;self.revision+=1;self.accepted+=1
                self.report(f'CONFIG_ACCEPTED revision={self.revision} master={master}')
                (self.folder/'lights-config-accepted.toml').write_bytes(raw)
                if self.revision<=16:(self.folder/f'lights-config-{self.revision:04d}.toml').write_bytes(raw)
        except (ValueError,OSError) as exc:
            self.rejected+=1;self.report('CONFIG_REJECTED keeping last valid: '+str(exc))

    def records(self,source):
        if self.tuning:
            try:raw=read_latest(source)
            except OSError as exc:
                if not isinstance(exc,(PermissionError,FileNotFoundError)) and getattr(exc,'winerror',None) not in (2,3,5,32,33):raise
                self.read_busy+=1
                if not self.read_pending:self.report('SOURCE_BUSY retry next poll;native freshness unchanged')
                self.read_pending=True
                return
            if self.read_pending:
                self.read_recoveries+=1;self.read_pending=False;self.report('SOURCE_READ_RECOVERED')
            self.offset=SIZE;yield raw
        elif source.exists():
            with source.open('rb') as file:
                file.seek(self.offset)
                while True:
                    raw=file.read(SIZE)
                    if len(raw)!=SIZE:break
                    self.offset+=SIZE
                    if self.offset>900*SIZE:raise ValueError('Native light capture cap')
                    yield raw

    def poll(self):
        now=time.monotonic()
        if now-self.last_poll<.1:return
        self.last_poll=now
        if now-self.last_config>=.5:
            self.last_config=now;self.reload();self.materials.poll()
        selected=self.receiver.selected
        source=self.folder/'gate/native-lights.bin'
        if self.tuning and selected:
            source=self.folder/f"gate/native-light-latest-{selected['owner_epoch']}.bin"
            self.offset=0
        if selected:
            for raw in self.records(source):
                row=decode(raw)
                if self.tuning and self.last_native and row['sequence']<=self.last_native['sequence']:continue
                if row['owner_epoch']==selected['owner_epoch'] and row['session_words']==self.session:
                    current=next((r for i in range(32) if (r:=self.receiver.channel.sample_owner(i)) is not None and r[1]==selected['owner_epoch'] and r[4]==1),None)
                    if current is None or row['elapsed_ms']>current[3] or current[3]-row['elapsed_ms']>500:continue
                    self.last_native=row;counter=C.c_longlong();frequency=C.c_longlong()
                    C.windll.kernel32.QueryPerformanceCounter(C.byref(counter));C.windll.kernel32.QueryPerformanceFrequency(C.byref(frequency))
                    # Conservatively retain native age,not file-read/config-save time.
                    self.observed=counter.value-int((current[3]-row['elapsed_ms']+34)*frequency.value/1000)
        if self.controls and self.last_native:
            self.generation+=1
            try:
                raw=packet(self.last_native,selected,self.session,self.controls,self.scale,self.master,self.generation,self.observed,self.revision,shapes=True)
            except ValueError as exc:self.report('STATE_REJECTED '+str(exc));return
            pending=self.folder/'live-lights.pending';pending.write_bytes(raw)
            try:pending.replace(self.folder/'live-lights.bin')
            except PermissionError:
                # Windows reader briefly denies delete/replace. Keep last packet,
                # retry on next poll, never wait or invent a newer observation.
                self.publish_busy+=1

    def summary(self):
        return dict(config=str(self.path),accepted=self.accepted,rejected=self.rejected,
                    material_config=dict(path=str(self.materials.path),accepted=self.materials.accepted,rejected=self.materials.rejected,sha256=self.materials.digest),
                    revisions=self.revision,packets=self.generation,source_bytes=self.offset,
                    config_sha256=self.last_digest,publish_busy=self.publish_busy,read_busy=self.read_busy,
                    read_recoveries=self.read_recoveries,read_pending=self.read_pending,
                    project_fill=self.controls.get('project_fill') if self.controls else None,
                    mode='two native type0 sources plus optional independent project fill;configurable Remix types')
