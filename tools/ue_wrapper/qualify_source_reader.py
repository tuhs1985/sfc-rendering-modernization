"""Replay retained source packets through real Windows IPC into the UE reader."""
import hashlib
import json
import os
from pathlib import Path
import struct
import sys

ROOT=Path(__file__).resolve().parents[2]
for part in ('src/rendering/ue','src/transport','src/assets','src/runtime'):
    sys.path.insert(0,str(ROOT/part))
from scene_receiver import Receiver
from source_reader import SourceReader
import multi_scene as wire
from owner_rebind import fnv
from runtime_context import CONTEXT
from scene_capacity import STATE_OFFSET
from mesh_decode import decode_mesh
import numpy as np

def export_fca(reader,snapshots,run,output):
    content=reader.revisions[4][0]
    asset=reader.assets[content]
    candidates=[]
    points=np.c_[np.asarray(asset.positions),np.ones(len(asset.positions))]
    for snapshot in snapshots:
        for instance in snapshot['instances']:
            if instance['revision']!=4:continue
            view,projection,viewport=snapshot['camera']
            clip=points @ (np.asarray(projection) @ np.asarray(view) @ np.asarray(instance['model'])).T
            if np.any(clip[:,3]<=0):continue
            ndc=clip[:,:3]/clip[:,3,None]
            if np.any(ndc[:,2]<=0):continue
            low=np.maximum(-1,ndc[:,:2].min(0))
            high=np.minimum(1,ndc[:,:2].max(0))
            area=np.prod(np.maximum(0,high-low))
            if area>0:candidates.append((area,snapshot,instance))
    if not candidates:raise ValueError('No visible qualified F-CA frame')
    _,snapshot,instance=max(candidates,key=lambda item:item[0])
    output.mkdir(parents=True,exist_ok=True)
    groups=[];indices=[];images={}
    for group,flags,primary,_,secondary,_,role in asset.groups:
        first=len(indices)
        for polygon_group,start in asset.polygons:
            if polygon_group==group:indices.extend((start,start+1,start+2))
        if len(indices)==first:continue
        image=reader.images[primary]
        filename=image.decoded_sha256+'.bgra'
        (output/filename).write_bytes(image.bgra)
        images[primary]=dict(file=filename,width=image.width,height=image.height,
                             sha256=image.decoded_sha256,original_sha256=image.original_sha256)
        groups.append(dict(group=group,flags=flags,first_index=first,index_count=len(indices)-first,
            primary=dict(filename=primary),secondary_filename=secondary,secondary_role_evidence=role))
    view,projection,viewport=snapshot['camera']
    frame=dict(owner=instance['owner_epoch'],revision=instance['revision'],model=instance['model'],
               view=view,projection=projection,viewport=list(viewport[:4]),active=1,
               source_frame=snapshot['frame'],source_sequence=snapshot['sequence'])
    packet=run/'gate/LIVE-SCENE-001-asset-4.bin'
    scene=dict(proof_schema='sfc.ue5.offline-proof.v1',session=reader.session,
        owner_epoch=instance['owner_epoch'],fragment=None,
        asset=dict(content=content,revision=4,model=asset.model),frames=[frame],
        positions=asset.positions,corners=asset.corners,indices=indices,groups=groups,images=images,
        source_packet=str(packet.relative_to(ROOT)),
        source_packet_sha256=hashlib.sha256(packet.read_bytes()).hexdigest(),
        source_scope='Retained native data replayed through current Windows IPC; no live SFC run')
    (output/'scene.json').write_text(json.dumps(scene))
    return str(output/'scene.json')

def run():
    run=ROOT/'artifacts/remix-runtime/runs/20261023-205121-223108-in-game'
    legacy_bytes=40+32*384
    raw=(run/'D3D9-MULTISCENE-001.frames.bin').read_bytes()
    if not raw or len(raw)%legacy_bytes:
        raise ValueError('Known legacy source-frame fixture layout')
    receiver=Receiver(retain_assets=False)
    try:
        channel=receiver.channel
        channel.write(12,struct.pack('<I',os.getpid()))
        wire.initialize(channel)
        channel.write(wire.OFFSET+12,struct.pack('<I',os.getpid()))
        reader=SourceReader(receiver,CONTEXT.game_root,os.getpid())
        for slot,revision in enumerate((1,2,3,4)):
            mesh=(run/f'gate/LIVE-SCENE-001-asset-{revision}.bin').read_bytes()
            refs=(run/f'gate/LIVE-SCENE-001-asset-{revision}.json').read_bytes()
            owner=struct.unpack_from('<I',mesh,16)[0]
            channel.write(65536+slot*2*1024*1024,mesh+refs)
            channel.write(256+slot*64,struct.pack('<6I',1,0,len(mesh),len(refs),owner,revision))
        reader.admit()
        if receiver.assets or len(reader.revisions)!=4:
            raise ValueError('Decoded ownership was not transferred once')
        image_bytes=reader.image_bytes
        for revision in (1,2,3,4):
            packet=(run/f'gate/LIVE-SCENE-001-asset-{revision}.bin').read_bytes()
            refs=(run/f'gate/LIVE-SCENE-001-asset-{revision}.json').read_bytes()
            original=decode_mesh(packet,refs)
            asset=reader.assets[reader.revisions[revision][0]]
            if asset.positions!=tuple(original['points']) or asset.corners!=tuple(original['corners']):
                raise ValueError('Original positions, normals or UVs changed')
        snapshots=[]
        for offset in range(0,len(raw),legacy_bytes):
            old=raw[offset:offset+legacy_bytes]
            if fnv(old[:-8])!=struct.unpack_from('<Q',old,len(old)-8)[0]:
                raise ValueError('Historical source-frame checksum')
            sequence,offered,frame,anchor,revision,count=struct.unpack_from('<QQ4I',old)
            if not 1<=count<=32:
                raise ValueError('Historical owner count')
            # Explicit fixture adaptation only. Current live reads use the
            # existing protocol4 mapping without altering its layout.
            current=bytearray(wire.FRAME_BYTES)
            current[:32]=old[:32]
            current[32:32+count*384]=old[32:32+count*384]
            struct.pack_into('<Q',current,len(current)-8,fnv(current[:-8]))
            base=wire.OFFSET+64+(frame%wire.FRAMES)*wire.FRAME_SLOT
            channel.write(base,struct.pack('<II',1,0))
            channel.write(base+8,bytes(current))
            channel.write(base,struct.pack('<I',2))
            channel.write(wire.OFFSET+36,struct.pack('<I',frame))
            result=reader.snapshot()
            if result is not None:
                snapshots.append(result)
        if len(snapshots)<2 or reader.image_bytes!=image_bytes:
            raise ValueError('Source replay did not reuse image assets')
        owners={item['owner_epoch'] for frame in snapshots for item in frame['instances']}
        if len(owners)<2:
            raise ValueError('Missing independently qualified owners')
        # A second owner receives identical captured geometry, with an explicit
        # synthetic epoch. This must share the retained asset and images.
        duplicate=bytearray((run/'gate/LIVE-SCENE-001-asset-4.bin').read_bytes())
        refs=json.loads((run/'gate/LIVE-SCENE-001-asset-4.json').read_bytes())
        struct.pack_into('<I',duplicate,16,9)
        value=2166136261
        for index,byte in enumerate(duplicate):
            value=((value^(0 if 12<=index<16 else byte))*16777619)&0xffffffff
        struct.pack_into('<I',duplicate,12,value)
        refs['owner_epoch']=9
        refs['packet_fnv1a']=value
        encoded=json.dumps(refs).encode()
        channel.write(65536,bytes(duplicate)+encoded)
        channel.write(256,struct.pack('<6I',2,1,len(duplicate),len(encoded),9,100))
        reader.admit()
        if len(reader.assets)!=4 or reader.revisions[4][0]!=reader.revisions[100][0] or reader.image_bytes!=image_bytes:
            raise ValueError('Shared geometry or image reuse failed')
        # Owner retirement is explicit, independent of frame visibility.
        retired=[0]*96
        retired[0]=1;retired[1]=9;retired[2]=frame+1;retired[4]=2;retired[7]=100
        channel.write(128,struct.pack('<I',1))
        channel.write(STATE_OFFSET,struct.pack('<I96I',2,*retired))
        next_frame=frame+1
        next_raw=bytearray(current)
        struct.pack_into('<Q',next_raw,0,sequence+1)
        struct.pack_into('<I',next_raw,16,next_frame)
        for index in range(count):
            struct.pack_into('<I',next_raw,32+index*384+8,next_frame)
            owner=struct.unpack_from('<I',next_raw,32+index*384+4)[0]
            if owner==anchor:
                struct.pack_into('<Q',next_raw,32+index*384+94*4,sequence+1)
        struct.pack_into('<Q',next_raw,len(next_raw)-8,fnv(next_raw[:-8]))
        base=wire.OFFSET+64+(next_frame%wire.FRAMES)*wire.FRAME_SLOT
        channel.write(base+8,bytes(next_raw));channel.write(base,struct.pack('<I',2))
        channel.write(wire.OFFSET+36,struct.pack('<I',next_frame))
        retirement=reader.snapshot()
        if not retirement or retirement['retirements']!=[dict(session=reader.session,owner_epoch=9,revision=100,source_frame=next_frame)]:
            raise ValueError('Explicit retirement not propagated')
        name=receiver.channel.name
        receiver.channel.name='Local\\SFCBridge_'+'0'*32
        try:
            try:reader.snapshot()
            except ValueError as error:
                if 'session changed' not in str(error):raise
            else:raise ValueError('Cross-session input accepted')
        finally:receiver.channel.name=name
        for asset in reader.assets.values():
            if not asset.positions or not asset.corners:
                raise ValueError('Lost original geometry')
        result=dict(source_run=run.name,frames=len(snapshots),owners=sorted(owners),
                    assets=len(reader.assets),image_bytes=reader.image_bytes,
                    receiver_retained_decodes=len(receiver.assets),
                    shared_asset_reused=True,retirement_propagated=True,cross_session_rejected=True,
                    first_sequence=snapshots[0]['sequence'],last_sequence=snapshots[-1]['sequence'],
                    original_uvs=True,remix_submission=False)
        output=ROOT/'artifacts/ue-foundation/source-reader'
        output.mkdir(exist_ok=True)
        result['fca_input']=export_fca(reader,snapshots,run,output/'fca-input')
        (output/'result.json').write_text(json.dumps(result,indent=2))
        return result
    finally:
        receiver.close()

if __name__=='__main__':
    print(json.dumps(run(),indent=2))
