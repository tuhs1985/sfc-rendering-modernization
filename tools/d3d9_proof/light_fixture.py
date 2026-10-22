"""Offline light replay ONLY: historical directions,explicit synthetic identity/time.

Never used as a fallback for missing live native light observations.
"""
import ctypes as C
import json
from pathlib import Path
import struct
import threading
import time
import tomllib
from run_offline import ROOT
from native_light_state import decode
from live_lights import packet,REGISTRY
from light_controls import validate,scales
from light_shapes import build


class Replay:
    def __init__(self,folder,scene,receiver=None):
        self.folder=Path(folder);self.stop=threading.Event();self.error=None;self.receiver=receiver
        source=ROOT/'artifacts/remix-runtime/runs/20261019-211853-736917-in-game/gate/native-light-latest-1.bin'
        self.snapshot=decode(source.read_bytes())
        self.session=[int(scene['source_session'][-32:][i:i+8],16) for i in range(0,32,8)]
        self.owner=scene['frames'][0]['owner'];self.snapshot.update(session_words=self.session,owner_epoch=self.owner,
            model_process_local=scene['fresh_preparation_row'][5],source_process_local=scene['fresh_preparation_row'][6],frame=scene['frames'][0]['frame'])
        self.folder.joinpath('light-fixture-identity.bin').write_bytes(struct.pack('<6I',*self.session,self.snapshot['model_process_local'],self.snapshot['source_process_local']))
        config=ROOT/'tools/remix_runtime/config/lights.toml';raw=config.read_bytes();data=tomllib.loads(raw.decode())
        self.controls={r['id']:r for r in validate(data,REGISTRY)};self.scale,self.master=scales(data)
        shapes,manifest=build(self.controls,1,self.folder,config.parent)
        self.folder.joinpath('light-shapes.bin').write_bytes(shapes)
        self.folder.joinpath('lights-config-accepted.toml').write_bytes(raw)
        self.folder.joinpath('light-fixture.json').write_text(json.dumps(dict(source=str(source.relative_to(ROOT)),
            classification='OFFLINE_REPLAY_HISTORICAL_DIRECTIONS_SYNTHETIC_IDENTITY_TIME_NOT_LIVE_LIGHT_PROOF',shapes=manifest),indent=2))
        self.shapes=shapes
        self.publish();self.thread=threading.Thread(target=self.run,daemon=False);self.thread.start()

    def publish(self):
        if self.receiver:
            row=next((r for i in range(32) if (r:=self.receiver.channel.sample_owner(i)) and r[1]==self.owner and r[4]==1),None)
            if not row:return
            self.snapshot['frame']=row[2]
        counter=C.c_longlong();C.windll.kernel32.QueryPerformanceCounter(C.byref(counter))
        raw=packet(self.snapshot,dict(owner_epoch=self.owner),self.session,self.controls,self.scale,self.master,1,counter.value,1,shapes=True)
        if self.receiver:
            from light_transport import publish_encoded
            pid=struct.unpack('<I',self.receiver.channel.read(10*1024*1024+28,4))[0]
            if pid:publish_encoded(self.receiver.channel,pid,raw,self.shapes,counter.value)
        pending=self.folder/'live-lights.pending';pending.write_bytes(raw)
        try:pending.replace(self.folder/'live-lights.bin')
        except PermissionError:return # Keep native timestamp;next bounded poll retries.

    def run(self):
        try:
            while not self.stop.wait(.002):self.publish()
        except Exception as exc:self.error=exc

    def close(self):
        self.stop.set();self.thread.join(timeout=2)
        if self.thread.is_alive():raise ValueError('Offline light worker failed to stop')
        if self.error:raise self.error
