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


class Binding:
    def __init__(self,folder,gpu,receiver,row):
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

    def poll(self):
        self.ready=False
        row=next((r for i in range(32) if (r:=self.receiver.channel.sample_owner(i)) and r[1]==self.row[1] and r[7]==self.row[7] and r[4]==1),None)
        if not row:return False
        try:
            from light_transport import read_native,publish_encoded
            import struct
            pid=struct.unpack('<I',self.receiver.channel.read(10*1024*1024+28,4))[0]
            observed=read_native(self.receiver.channel,row[1],pid)
            if observed is None:return False
            original,captured=observed;native=decode(original)
            if (native['session_words']!=self.session or native['owner_epoch']!=row[1] or
                native['model_process_local']!=row[5] or native['source_process_local']!=row[6] or
                native['elapsed_ms']>row[3] or row[3]-native['elapsed_ms']>400):return False
            identity=(row[1],native['sequence'],captured)
            if identity==self.last_native:self.ready=True;return True
            self.generation+=1
            raw=packet(native,dict(owner_epoch=row[1]),self.session,self.controls,self.scale,self.master,self.generation,captured,1,shapes=True)
            publish_encoded(self.receiver.channel,pid,raw,self.shapes,captured)
            self.last_native=identity
            self.latest=dict(sequence=native['sequence'],frame=native['frame'],source_age_ms=row[3]-native['elapsed_ms'])
            self.ready=True;return True
        except (PermissionError,FileNotFoundError):self.busy+=1;return False
        except ValueError:self.invalid+=1;return False

    def prepare_owner(self,row):
        self.row=list(row);self.ready=False
        return self.poll()

    def summary(self):return dict(config_sha256=self.config_hash,packets=self.generation,busy=self.busy,invalid=self.invalid,latest=self.latest,
                                 policy='Frozen config;fresh same-session/owner/model/source native lights only;no replay fallback')
