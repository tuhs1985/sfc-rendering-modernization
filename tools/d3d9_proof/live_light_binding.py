"""Bounded worker-only current native lights -> existing Remix light policy.

No historical-light fallback. Configuration is frozen for the90s insertion proof.
"""
import ctypes as C
import hashlib
import json
from pathlib import Path
import time
import tomllib
from light_controls import validate,scales
from light_shapes import build
from live_lights import REGISTRY,read_latest,packet
from native_light_state import decode

def world_light_context(snapshot,row):
    if any(snapshot['slots'][i]['native_type']!=0 for i in range(2)):
        raise ValueError('Only qualified world directional bank can be shared')
    # New adapter context;the original native observation remains unchanged.
    return dict(snapshot,owner_epoch=row[1],model_process_local=row[5],source_process_local=row[6])

class Binding:
    def __init__(self,folder,gpu,receiver,row,persistent=False):
        self.folder=Path(folder);self.gpu=Path(gpu);self.receiver=receiver;self.row=list(row)
        self.last=0;self.ready=False;self.generation=0;self.busy=0;self.invalid=0;self.latest=None
        config=Path(__file__).resolve().parents[1]/'remix_runtime/config/lights.toml'
        raw=config.read_bytes()
        if len(raw)>65536:raise ValueError('Light config64KiB cap')
        data=tomllib.loads(raw.decode());self.controls={r['id']:r for r in validate(data,REGISTRY)}
        self.scale,self.master=scales(data)
        self.session=[int(receiver.name[-32:][i:i+8],16) for i in range(0,32,8)]
        shapes,manifest=build(self.controls,1,self.gpu,config.parent)
        self.shapes=shapes;self.last_native=None
        (self.gpu/'light-shapes.bin').write_bytes(shapes)
        (self.gpu/'lights-config-accepted.toml').write_bytes(raw)
        (self.gpu/'light-shapes-manifest.json').write_text(json.dumps(manifest,indent=2))
        self.config_hash=hashlib.sha256(raw).hexdigest()
        self.persistent=persistent;self.native_cache={};self.bank_publication=None

    def poll(self):
        self.ready=False
        row=next((r for i in range(32) if (r:=self.receiver.channel.sample_owner(i)) and r[1]==self.row[1] and r[7]==self.row[7] and r[4]==1),None)
        if not row:return False
        try:
            from light_transport import read_native,publish_encoded
            import struct
            pid=struct.unpack('<I',self.receiver.channel.read(10*1024*1024+28,4))[0]
            from light_transport import RAW_OFFSET
            publication=struct.unpack('<I',self.receiver.channel.read(RAW_OFFSET+36,4))[0]
            if self.persistent and publication==self.bank_publication and self.last_native and self.last_native[0]==row[1] and self.latest and 0<=row[3]-self.latest['native_elapsed_ms']<=400:
                self.ready=True;return True
            source_row=row
            observed=read_native(self.receiver.channel,row[1],pid)
            if self.persistent:
                # Only the original WORLD-space directional records are consumed
                # by packet();owner-local diagnostic vectors never enter this join.
                candidates=[]
                for i in range(32):
                    candidate=self.receiver.channel.sample_owner(i)
                    if not candidate or candidate[4]!=1 or candidate[3]>row[3] or row[3]-candidate[3]>200:continue
                    value=read_native(self.receiver.channel,candidate[1],pid)
                    if value:candidates.append((value[1],candidate,value))
                if candidates:_,source_row,observed=max(candidates,key=lambda v:v[0])
            if observed is None:return False
            original,captured=observed
            cached=self.native_cache.get(source_row[1])
            native=cached[1] if cached and cached[0]==captured else decode(original)
            if len(self.native_cache)>=32 and source_row[1] not in self.native_cache:self.native_cache.clear()
            self.native_cache[source_row[1]]=(captured,native)
            if (native['session_words']!=self.session or native['owner_epoch']!=source_row[1] or
                native['model_process_local']!=source_row[5] or native['source_process_local']!=source_row[6] or
                native['elapsed_ms']>row[3] or row[3]-native['elapsed_ms']>400):return False
            identity=(row[1],native['sequence'],captured,source_row[1])
            if identity==self.last_native:self.ready=True;return True
            self.generation+=1
            normalized=world_light_context(native,row) if self.persistent else native
            raw=packet(normalized,dict(owner_epoch=row[1]),self.session,self.controls,self.scale,self.master,self.generation,captured,1,shapes=True)
            publish_encoded(self.receiver.channel,pid,raw,self.shapes,captured)
            self.last_native=identity
            self.bank_publication=publication
            self.latest=dict(sequence=native['sequence'],frame=native['frame'],source_age_ms=row[3]-native['elapsed_ms'],
                native_elapsed_ms=native['elapsed_ms'],
                native_bank_owner=source_row[1],native_bank_model=source_row[5],target_owner=row[1],
                normalization='WORLD_DIRECTIONAL_BANK_TO_PERSISTENT_INSTANCE' if self.persistent else 'SAME_OWNER')
            self.ready=True;return True
        except (PermissionError,FileNotFoundError):self.busy+=1;return False
        except ValueError:self.invalid+=1;return False

    def prepare_owner(self,row):
        self.row=list(row);self.ready=False
        return self.poll()

    def summary(self):return dict(config_sha256=self.config_hash,packets=self.generation,busy=self.busy,invalid=self.invalid,latest=self.latest,
                                 policy='Frozen config;fresh same-session/owner/model/source native lights only;no replay fallback')
