"""Receive and acknowledge qualified scene assets from the live channel."""
import hashlib

from live_scene import SceneChannel, decode_mesh, ASSETS


class Receiver:
    def __init__(self,*,break_models=False):
        self.channel=SceneChannel(create=True)
        self.break_models=break_models
        self.revisions={}
        self.assets={}
        self.retain_assets=True # Legacy single-owner recovery consumes decoded packets.

    @property
    def name(self):return self.channel.name

    def drain(self):
        for slot in range(4):
            transfer=self.channel.asset_transfer(slot)
            if transfer is None:continue
            generation,revision,owner,mesh,refs=transfer
            if not 1<=revision<=ASSETS:raise ValueError('Asset revision outside session transport budget')
            if self.break_models:
                from break_scene import decode_runtime_mesh
                data=decode_runtime_mesh(mesh,refs,allow_break=True)
            else:data=decode_mesh(mesh,refs)
            if data['header'][4]!=owner:raise ValueError('Asset transfer owner mismatch')
            identity=hashlib.sha256(mesh+refs).hexdigest()
            if revision in self.revisions and self.revisions[revision]!=identity:raise ValueError('Reused asset revision')
            self.revisions[revision]=identity
            if self.retain_assets:self.assets[revision]=data
            self.channel.acknowledge(slot,generation)

    def close(self):self.channel.close()
