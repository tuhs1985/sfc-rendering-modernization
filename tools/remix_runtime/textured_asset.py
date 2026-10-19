"""Worker-only original-image association and grouped renderer asset preparation."""
from pathlib import Path
import hashlib
import json
import struct
import io
import numpy as np
from PIL import Image
from live_scene import ImageStore,qualify_mesh

def fnv(raw):
    value=14695981039346656037
    for byte in raw:value=((value^byte)*1099511628211)&0xffffffffffffffff
    return value

def prepare(packet,refs,folder,game_root):
    folder=Path(folder);images=ImageStore(game_root,folder/'textures')
    mesh=qualify_mesh(packet,refs,images)
    materials=[];emissions=[];lookup={};assignments={};provenance=[];derived={}
    for row in mesh['assignments']:
        primary=row['primary']
        if primary is None:raise ValueError('Textured return requires proven primary for every group')
        if primary['alpha']:raise ValueError('Textured return alpha path not qualified')
        secondary=row['secondary'];emission=None
        # Native ADD-then-MODULATE yields primary*secondary as its unlit term.
        # Modern emission is an approximation,not an exact legacy clamp/space match.
        if secondary is not None:
            if secondary['alpha']:raise ValueError('Secondary alpha mapping unqualified')
            pair=(primary['sha256'],secondary['sha256'])
            if pair not in derived:
                with Image.open(primary['dds']) as p,Image.open(secondary['dds']) as s:
                    size=(max(p.width,s.width),max(p.height,s.height))
                    if images.memory+size[0]*size[1]*32>256*1024*1024:raise ValueError('Illumination preparation working-memory cap')
                    # Both native stages use the captured UV domain,not pixel IDs.
                    # Bake at the larger resolution using explicit modern bilinear
                    # sampling;source pixels/UVs stay untouched. Not native fidelity.
                    a=p.convert('RGB');b=s.convert('RGB')
                    if a.size!=size:a=a.resize(size,Image.Resampling.BILINEAR)
                    if b.size!=size:b=b.resize(size,Image.Resampling.BILINEAR)
                    pixels=((np.asarray(a,dtype=np.uint16)*np.asarray(b,dtype=np.uint16)+127)//255).astype(np.uint8)
                    image=Image.fromarray(pixels).convert('RGBA');stream=io.BytesIO();image.save(stream,format='DDS');raw=stream.getvalue()
                if images.bytes+len(raw)>128*1024*1024 or images.memory+image.width*image.height*8>256*1024*1024:raise ValueError('Illumination output/memory cap')
                digest=hashlib.sha256(raw).hexdigest();path=folder/'textures'/(digest+'.dds')
                path.write_bytes(raw);images.bytes+=len(raw);images.memory+=image.width*image.height*8
                with Image.open(path) as check:
                    if check.convert('RGBA').tobytes()!=image.tobytes():raise ValueError('Illumination DDS pixel mismatch')
                derived[pair]=dict(sha256=digest,dds=str(path),bytes=len(raw),formula='floor((primary_encoded*secondary_encoded+127)/255)',
                    source_dimensions=[list(p.size),list(s.size)],derived_dimensions=list(size),sampling='shared normalized UV domain;bilinear upsample to componentwise maximum dimensions;Remix-only approximation',
                    primary_sha256=pair[0],secondary_sha256=pair[1],status='PROVISIONAL_MODERN_EMISSION_NOT_NATIVE_FIDELITY')
            emission=derived[pair]
        digest=hashlib.sha256((primary['sha256']+(emission['sha256'] if emission else '')).encode()).hexdigest()
        if digest not in lookup:
            lookup[digest]=len(materials)
            name=Path(primary['dds']).name.encode('ascii')
            if len(name)>=72:raise ValueError('DDS filename bound')
            materials.append(struct.pack('<Q72s',int(digest[:16],16) or 1,name))
            emissions.append(struct.pack('<Q72s',int(emission['sha256'][:16],16) or 1,Path(emission['dds']).name.encode('ascii')) if emission else bytes(80))
        assignments[row['group']]=lookup[digest]
        provenance.append(dict(group=row['group'],primary=primary,secondary=secondary,illumination=emission))
    indices=[];groups=[]
    for group in mesh['groups']:
        selected=[start for identity,start in mesh['polygons'] if identity==group['group']]
        if not selected:continue
        first=len(indices)
        for start in selected:indices.extend((start,start+1,start+2))
        groups.append(struct.pack('<4I',group['group'],assignments[group['group']],first,len(indices)-first))
    if sorted(indices)!=list(range(len(mesh['corners']))):raise ValueError('Group index coverage')
    payload=b''.join(materials)+b''.join(groups)+struct.pack('<%dI'%len(indices),*indices)
    header=struct.pack('<8IQ',0x31585453,1,len(materials),len(groups),len(indices),len(mesh['corners']),len(payload),0,fnv(payload))
    if len(payload)>2*1024*1024:raise ValueError('Material payload bound')
    (folder/'live-materials.bin').write_bytes(header+payload)
    emission_payload=b''.join(emissions)
    emission_packet=struct.pack('<4IQ',0x314d4553,1,len(emissions),len(emission_payload),fnv(emission_payload))+emission_payload
    (folder/'live-emissions.bin').write_bytes(emission_packet)
    from material_controls import Relay
    Relay(folder).poll()
    manifest=dict(version=1,geometry_sha256=mesh['geometry_sha256'],asset_sha256=mesh['asset_sha256'],
        materials=provenance,issues=mesh['issues'],image_bytes=images.bytes,image_warning=images.bytes>=64*1024*1024,
        image_memory_bytes=images.memory,group_count=len(groups),material_count=len(materials),
        material_packet_sha256=hashlib.sha256(header+payload).hexdigest(),
        emission_packet_sha256=hashlib.sha256(emission_packet).hexdigest(),
        treatment='Original primary reflected colour plus provisional primary*secondary emission;not exact native saturation/colour-space fidelity',
        whole_hull_emission=False,secondary_applied=bool(derived),illumination_derivatives=list(derived.values()),
        unresolved_native_fidelity=['legacy branch/pass completion','colour space and saturation','physical intensity calibration'],
        renderer_adapter=dict(backend='Pinned Remix SDK/DDS',texture_origin='Host SDK vertices only: v=1-captured_v;u unchanged',
            scope='Not a shared SFC/D3D rule;future adapters must qualify their own convention',raw_uv_and_images_unchanged=True),
        geometry='Original positions/normals/UVs unchanged;indices regrouped by captured group')
    (folder/'texture-manifest.json').write_text(json.dumps(manifest,indent=2))
    return manifest
