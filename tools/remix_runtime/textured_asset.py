"""Worker-only original-image association and grouped renderer asset preparation."""
from pathlib import Path
import hashlib
import json
import struct
from live_scene import ImageStore,qualify_mesh

def fnv(raw):
    value=14695981039346656037
    for byte in raw:value=((value^byte)*1099511628211)&0xffffffffffffffff
    return value

def prepare(packet,refs,folder,game_root):
    folder=Path(folder);images=ImageStore(game_root,folder/'textures')
    mesh=qualify_mesh(packet,refs,images)
    materials=[];lookup={};assignments={};provenance=[]
    for row in mesh['assignments']:
        primary=row['primary']
        if primary is None:raise ValueError('Textured return requires proven primary for every group')
        if primary['alpha']:raise ValueError('Textured return alpha path not qualified')
        # Secondary images are preserved in provenance,not guessed to be glow.
        digest=primary['sha256']
        if digest not in lookup:
            lookup[digest]=len(materials)
            name=Path(primary['dds']).name.encode('ascii')
            if len(name)>=72:raise ValueError('DDS filename bound')
            materials.append(struct.pack('<Q72s',int(digest[:16],16) or 1,name))
        assignments[row['group']]=lookup[digest]
        provenance.append(dict(group=row['group'],primary=primary,secondary=row['secondary']))
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
    manifest=dict(version=1,geometry_sha256=mesh['geometry_sha256'],asset_sha256=mesh['asset_sha256'],
        materials=provenance,issues=mesh['issues'],image_bytes=images.bytes,image_warning=images.bytes>=64*1024*1024,
        image_memory_bytes=images.memory,group_count=len(groups),material_count=len(materials),
        material_packet_sha256=hashlib.sha256(header+payload).hexdigest(),
        treatment='Original primary images as reflected surface color only;whole-hull emission off;provisional white directional inspection light;secondary roles not inferred',
        whole_hull_emission=False,secondary_applied=False,
        renderer_adapter=dict(backend='Pinned Remix SDK/DDS',texture_origin='Host SDK vertices only: v=1-captured_v;u unchanged',
            scope='Not a shared SFC/D3D rule;future adapters must qualify their own convention',raw_uv_and_images_unchanged=True),
        geometry='Original positions/normals/UVs unchanged;indices regrouped by captured group')
    (folder/'texture-manifest.json').write_text(json.dumps(manifest,indent=2))
    return manifest
