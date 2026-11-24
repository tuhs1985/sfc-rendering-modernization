"""One-time UE base definitions from admitted neutral assets, never templates.

Frame updates stay on existing shared memory. This is the existing local proof
input schema, not a replacement source protocol or a public plugin API.
"""
import json
import os
from pathlib import Path


class DefinitionPublisher:
    def __init__(self,folder):
        self.folder=Path(folder)
        self.published={}
        self.images=set()
        self.session=None
        self.asset_definitions={}

    def publish(self,reader,snapshot,instance):
        revision=instance['revision']
        if self.session is not None and reader.session!=self.session:
            raise ValueError('Source publisher belongs to another session; create a fresh working directory')
        if (snapshot['session']!=reader.session or instance['session']!=reader.session
                or snapshot['source_pid']!=reader.source_pid or instance not in snapshot['instances']
                or revision not in reader.revisions):
            raise ValueError('Source definition session/revision association')
        content,owner,model,source=reader.revisions[revision]
        if instance['owner_epoch']!=owner or instance['asset']!=content:
            raise ValueError('Source definition owner/asset association')
        if len(content)!=64 or any(c not in '0123456789abcdef' for c in content):
            raise ValueError('Invalid source content identity')
        key=(reader.session,owner,revision)
        if key in self.published:
            previous,path=self.published[key]
            if previous!=content:raise ValueError('Source revision changed content')
            return path
        asset=reader.assets[content];origin=reader.origins[revision]
        if snapshot['camera'] is None:raise ValueError('Missing coherent source camera')
        view,projection,viewport=snapshot['camera']
        frame=dict(owner=owner,revision=revision,model=instance['model'],view=view,projection=projection,
            viewport=list(viewport[:4]),active=1,source_frame=snapshot['frame'],source_sequence=snapshot['sequence'])
        definition=dict(proof_schema='sfc.ue5.offline-proof.v1',session=reader.session,owner_epoch=owner,
            fragment=origin.get('fragment'),asset=dict(content=content,revision=revision,model=asset.model,
                geometry_content=getattr(asset,'geometry_content','') or content),
            source_packet=f'ipc:{reader.session}/asset/{revision}',source_packet_sha256=origin['packet_sha256'],
            source_binding=dict(pid=reader.source_pid,model=model,source=source),
            source_scope='Definition assembled from supplied neutral snapshot; caller controls live/replay admission',frames=[frame])
        payloads={}
        if content in self.asset_definitions:
            definition['asset_reference']=self.asset_definitions[content]
        else:
            groups=[];indices=[];images={};payloads={}
            for group,flags,primary,_,secondary,secondary_hash,role in asset.groups:
                first=len(indices)
                for polygon_group,start in asset.polygons:
                    if polygon_group==group:indices.extend((start,start+1,start+2))
                if len(indices)==first:continue
                image=reader.images[primary];filename=image.decoded_sha256+'.bgra'
                if len(image.decoded_sha256)!=64 or any(c not in '0123456789abcdef' for c in image.decoded_sha256):
                    raise ValueError('Invalid original image identity')
                images[primary]=dict(file=filename,width=image.width,height=image.height,
                    sha256=image.decoded_sha256,original_sha256=image.original_sha256)
                payloads[filename]=image.bgra
                groups.append(dict(group=group,flags=flags,first_index=first,index_count=len(indices)-first,
                    primary=dict(filename=primary),secondary_filename=secondary,secondary_sha256=secondary_hash,
                    secondary_role_evidence=role))
            if not groups:raise ValueError('Missing source groups')
            definition.update(positions=asset.positions,corners=asset.corners,indices=indices,groups=groups,images=images)
        self.folder.mkdir(parents=True,exist_ok=True)
        for filename,pixels in payloads.items():
            if filename in self.images:continue
            path=self.folder/filename
            # The session parent owns this fresh working directory. Publish the
            # definition only after every required base image is completely written.
            with path.open('xb') as stream:stream.write(pixels)
            self.images.add(filename)
        path=self.folder/f'{content}-{owner}-{revision}.json'
        pending=path.with_suffix('.pending');pending.write_text(json.dumps(definition,separators=(',',':')),encoding='utf-8')
        os.replace(pending,path)
        self.published[key]=(content,path)
        self.asset_definitions.setdefault(content,path.name)
        self.session=reader.session
        return path
