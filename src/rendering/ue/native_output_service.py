"""Explicit one-player additive UE service; no default viewer behavior change."""
import math
from pathlib import Path
import sys
from source_service import SourceService

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/"tools/d3d9_proof"))
from owner_selection import choose,selected_model

def choose_player(reader,candidates,model):
    qualified=[]
    for row in candidates:
        content=reader.revisions[row[7]][0]
        qualified.append((row,{"refs":{"model_filename":reader.assets[content].model}}))
    match=choose(qualified,model)
    return match[0] if match else None

def additive_environment(original):
    env=dict(original)
    env.update(SFC_D3D9_GAME_OUTPUT="1",SFC_D3D9_SYNC_BUFFER="1",SFC_NATIVE_RESOLUTION="1",
               SFC_NATIVE_INSERTION_GATE="1",SFC_NATIVE_INSERTION_ADDITIVE="1",
               SFC_NATIVE_INSERTION_POLICY="ExtraFrame",SFC_NATIVE_INSERTION_ALL_SHIPS="0",
               SFC_D3D9_PLAYER_REPLACEMENT="0",SFC_NATIVE_INSERTION_OBSERVE="0")
    return env

class AdditiveSourceService(SourceService):
    def __init__(self,receiver,game,pid,folder,executable,*,consumer,world_offset,environment,player_model=None):
        super().__init__(receiver,game,pid,folder,executable,environment=additive_environment(environment))
        if len(world_offset)!=3 or any(not math.isfinite(float(v)) for v in world_offset):raise ValueError("Three finite native world offsets required")
        self.consumer=Path(consumer).resolve();self.world_offset=tuple(map(float,world_offset))
        if not self.consumer.is_file():raise ValueError("Qualified UE receiver missing")
        self.player_model=selected_model() if player_model is None else player_model
        self.player=None
    def choose_anchor(self,candidates):
        chosen=choose_player(self.reader,candidates,self.player_model)
        if chosen is None:return None
        identity=(chosen[1],chosen[7])
        if self.player is not None and identity!=self.player:return None
        self.player=identity
        return chosen
    def arguments(self):
        args=super().arguments()+["-SFCNativeAdditive",f"-SFCGpuConsumer={self.consumer}"]
        return args+[f"-SFCWorldOffset{axis}={value:.17g}" for axis,value in zip("XYZ",self.world_offset)]
    def summary(self):
        result=super().summary()
        result.update(native_output=True,original_suppressed=False,selected_model=self.player_model,
                      player=self.player,world_offset=list(self.world_offset),
                      selection="Unique configured player fixture; not an engine ownership flag")
        return result
