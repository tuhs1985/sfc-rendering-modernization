"""Explicit read-only UE backend service; no Remix preparation or game output."""
import ctypes as C
import os
from pathlib import Path
import struct
import subprocess
from source_reader import SourceReader
from scene_definition import DefinitionPublisher
import multi_scene as wire
from owner_rebind import fnv


def source_environment(inherited,session,source,game):
    prefixes=('SFC_REMIX_','SFC_D3D9_','SFC_NATIVE_','SFC_LIGHT_','SFC_REPLACEMENT_','SFC_DAMAGE_','SFC_BREAK_','SFC_PERSISTENT_','SFC_LIFECYCLE_')
    env={key:value for key,value in inherited.items() if not key.startswith(prefixes)}
    env.update(SFC_REMIX_RETURN_SESSION=session,SFC_REMIX_EXPECTED_IMAGE=str(game),SFC_REMIX_PRELOAD_REQUIRED='1',
        SFC_REMIX_CALIBRATION_SCENE=source,SFC_PLAY_SESSION='1',SFC_PIPELINE_MODE='performance',
        SFC_D3D9_SOURCE_TIMING='1',SFC_D3D9_LIVE_TIMING='1',SFC_PERSISTENT_SCENE='1',SFC_D3D9_MULTISCENE='1',
        SFC_D3D9_PLAYER_REPLACEMENT='0',SFC_NATIVE_INSERTION_ALL_SHIPS='0',SFC_NATIVE_INSERTION_GATE='0',
        SFC_D3D9_GAME_OUTPUT='0',SFC_DAMAGE_TEXTURES='0',SFC_BREAK_SCENE='0')
    return env


class SourceService:
    def __init__(self,receiver,game,pid,folder,executable,*,environment=None):
        self.receiver=receiver;self.reader=SourceReader(receiver,game,pid)
        self.folder=Path(folder);self.folder.mkdir(exist_ok=True)
        self.publisher=DefinitionPublisher(self.folder/'definitions')
        self.process=None;self.executable=Path(executable);self.published=set();self.last=None
        self.frames=0;self.anchor=None;self.environment=environment

    def arguments(self):
        return [str(self.executable),'-windowed','-ResX=1280','-ResY=800','-nosound','-nolog',
            f'-SFCSourceMap={self.reader.session}',f'-SFCSourcePID={self.reader.source_pid}',
            f'-SFCParentPID={os.getpid()}',f'-SFCDefinitionDirectory={self.publisher.folder}']
    def start(self):
        self.process=subprocess.Popen(self.arguments(),env=self.environment,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

    def choose_anchor(self,candidates):
        return next((r for r in candidates if (r[1],r[7])==self.anchor),candidates[0] if candidates else None)

    def poll(self):
        if self.process is not None and self.process.poll() is not None:
            raise RuntimeError('UE inspection window closed; SFC drawing is unchanged')
        self.reader.admit()
        # Existing native cohort publication needs one scheduling anchor. This
        # never selects a player for suppression: all native drawing stays on.
        rows=[self.receiver.channel.sample_owner(i) for i in self.receiver.channel.owner_indices()]
        candidates=[r for r in rows if r and r[4]==1 and r[7] in self.reader.revisions and
            self.reader.revisions[r[7]][1:]==(r[1],r[5],r[6])]
        chosen=self.choose_anchor(candidates)
        if chosen is not None and self.anchor!=(chosen[1],chosen[7]):
            self.anchor=chosen[1],chosen[7]
            # Same aligned x64 supervisor store used by the existing native host.
            C.c_uint64.from_address(self.receiver.channel.view+10*1024*1024+32).value=chosen[1]|(chosen[7]<<32)
        snapshot=self.reader.snapshot()
        if snapshot is None:return
        self.frames+=1;self.last=snapshot
        for instance in snapshot['instances']:
            revision=instance['revision']
            if revision in self.published:continue
            self.publisher.publish(self.reader,snapshot,instance)
            content,owner,model,source=self.reader.revisions[revision]
            origin=self.reader.origins[revision];asset=self.reader.assets[content]
            images={g[2] for g in asset.groups}
            image_bytes=sum(len(self.reader.images[name].bgra) for name in images)
            # UE-selected private catalogue fingerprints are original SHA-256
            # prefixes. They are not ordinary-D3D9 prepared-file FNV identities.
            image_identity=fnv(b''.join(bytes.fromhex(self.reader.images[name].decoded_sha256) for name in sorted(images)))
            raw=wire.ASSET.pack(revision,revision,owner,revision,model,source,origin['packet_bytes'],image_bytes,
                bytes.fromhex(content),int.from_bytes(bytes.fromhex(origin['packet_sha256'])[:8],'little') or 1,image_identity or 1,0)
            wire.publish(self.receiver.channel,revision,raw[:-8]+struct.pack('<Q',fnv(raw[:-8])))
            self.published.add(revision)

    def stop(self):
        self.receiver.channel.write(wire.OFFSET+32,struct.pack('<I',1))
        if self.process is not None and self.process.poll() is None:
            try:self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:self.process.terminate();self.process.wait(timeout=5)

    def summary(self):
        return dict(source_frames=self.frames,definitions=len(self.published),assets=len(self.reader.assets),
            original_images=len(self.reader.images),image_bytes=self.reader.image_bytes,asset_bytes=self.reader.asset_bytes,
            last_frame=self.last['frame'] if self.last else None,last_sequence=self.last['sequence'] if self.last else None,
            original_suppressed=False,native_output=False,diagnostic_images=False,
            ue_exit=self.process.poll() if self.process else None)
