"""Offline neutral scene view of existing SFC captures. No renderer/SDK imports.

The little-endian replay files are local consumer fixtures,NOT a new live protocol.
Raw game capture,images and native17word arithmetic remain authoritative.
"""
from pathlib import Path
import hashlib
import io
import json
import math
import re
import struct
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/remix_ingest'))
sys.path.insert(0,str(ROOT/'tools/m1_component'))
from live_scene import decode_mesh
from live_camera import camera_state
from analyze_live_camera import native_matrix

MAGIC=0x31534653
TEXTURE_MAGIC=0x31544653
MAX_BYTES=128*1024*1024
FRAME=struct.Struct('<4I52f')


def sha(raw):return hashlib.sha256(raw).hexdigest()


def finite_matrix(values):
    return len(values)==16 and all(math.isfinite(x) for x in values)


def flatten(matrix):return [x for row in matrix for x in row]


def snapshots(mesh,updates,revision):
    """Keep camera/pose from one validated row,never independently sample them."""
    if updates.stat().st_size>32*1024*1024:raise ValueError('Update input cap')
    import numpy as np
    candidates=[]
    points=np.c_[np.asarray(mesh['points']),np.ones(len(mesh['points']))]
    with updates.open(encoding='utf-8') as stream:
        for line_number,line in enumerate(stream,1):
            if len(line)>8192:raise ValueError('Update line cap')
            r=json.loads(line)
            if not isinstance(r,list) or len(r)!=96:raise ValueError('Update row size')
            if not all(type(v)is int and 0<=v<=0xffffffff for v in r):raise ValueError('Update word')
            if (r[4]!=1 or r[1]!=mesh['header'][4] or r[7]!=revision or
                r[5]!=mesh['header'][10] or r[6]!=mesh['header'][12] or
                r[2]<mesh['header'][6] or any(r[42:45])):continue
            state=camera_state(r,[0,0,0],mesh['used_points'])
            composed=native_matrix(r[25:42]);clip=points@np.asarray(composed).T
            if np.any(clip[:,3]<=0):continue
            xy=clip[:,:2]/clip[:,3,None];x,y,w,h=state['viewport']
            # Select an already captured useful view;NEVER refit/alter the camera.
            if (xy[:,0].min()<x or xy[:,0].max()>x+w or xy[:,1].min()<y or xy[:,1].max()>y+h or
                np.ptp(xy[:,0])*np.ptp(xy[:,1])<1024):continue
            model=native_matrix(r[8:25]);view=native_matrix(r[49:66]);projection=native_matrix(r[66:83])
            candidates.append(dict(line=line_number,owner=r[1],revision=r[7],frame=r[2],active=1,
                model=model,view=view,projection=projection,viewport=state['viewport'],
                native_composed=composed,composition_error_pixels=state['native_composition_pixel_error']))
    if not candidates:raise ValueError('No coherent same-owner/revision camera snapshot')
    return [candidates[i] for i in sorted({0,len(candidates)//2,len(candidates)-1})]


def resolve_image(root,filename):
    name=filename.replace('\\','/');root=Path(root).resolve();candidate=root/name
    path=candidate.resolve()
    if not name or not path.is_relative_to(root) or any(p.is_symlink() for p in [candidate,*candidate.parents] if p!=root):
        raise ValueError('Unsafe original image path')
    if not path.is_file() or path.stat().st_size>16*1024*1024:raise ValueError('Original image missing/bound')
    return path


def texture(raw):
    from PIL import Image
    with Image.open(io.BytesIO(raw)) as image:
        if not 1<=image.width<=4096 or not 1<=image.height<=4096:raise ValueError('Texture dimensions')
        image.load();rgba=image.convert('RGBA')
        if rgba.getextrema()[3]!=(255,255):raise ValueError('Transparency unsupported by first opaque proof')
        pixels=rgba.tobytes('raw','BGRA')
        return dict(width=image.width,height=image.height,format=image.format),pixels


def prepare(source,output,game_root,*,live_record=None,evidence_mode='test',qualified_mesh=None):
    """Read original runtime mesh;resolve original IMAGE files only,never MOD geometry."""
    if evidence_mode not in ('performance','test'):raise ValueError('Scene evidence mode')
    if evidence_mode=='performance' and live_record is None:raise ValueError('Performance preparation requires fresh live row')
    source=Path(source).resolve();source.relative_to(ROOT/'artifacts')
    output=Path(output).resolve();output.relative_to(ROOT/'artifacts')
    if output.exists():raise ValueError('Refuse to overwrite replay evidence')
    if source.stat().st_size>2*1024*1024 or source.with_suffix('.json').stat().st_size>256*1024:raise ValueError('Source packet/reference cap')
    raw=source.read_bytes();refs=source.with_suffix('.json').read_bytes()
    if qualified_mesh is None:mesh=decode_mesh(raw,refs)
    else:
        # Reuse this worker's fully validated immutable decode. Cheap byte hashes
        # still bind it to the current packet AND associations;never trust IDs.
        if (sha(raw)!=qualified_mesh.get('packet_sha256') or
                sha(refs)!=qualified_mesh.get('_capture_refs_sha256')):
            raise ValueError('Qualified mesh packet/reference changed')
        mesh=qualified_mesh
    revision=int(source.stem.rsplit('-',1)[1])
    updates=source.parent/'LIVE-SCENE-001-updates.jsonl'
    capture_metadata_path=source.parent/'run-metadata.json'
    if capture_metadata_path.is_file():
        source_session=json.loads(capture_metadata_path.read_text(encoding='utf-8-sig')).get('live_channel')
    else:
        capture_metadata_path=source.parent.parent/'manifest.json'
        source_session=json.loads(capture_metadata_path.read_text(encoding='utf-8-sig')).get('semantic_calibration',{}).get('scene_session')
    if not isinstance(source_session,str) or not re.fullmatch(r'Local\\SFCBridge_[a-f0-9]{32}',source_session):raise ValueError('Source capture session missing/unqualified')
    if live_record is None:frames=snapshots(mesh,updates,revision)
    else:
        r=live_record
        if (len(r)!=96 or not r[2] or r[4]!=1 or (r[1],r[5],r[6],r[7])!=(mesh['header'][4],mesh['header'][10],mesh['header'][12],revision) or r[2]<mesh['header'][6]):raise ValueError('Fresh live asset/row mismatch')
        state=camera_state(r,[0,0,0],mesh['used_points'])
        frames=[dict(line=None,owner=r[1],revision=r[7],frame=r[2],active=1,model=native_matrix(r[8:25]),view=native_matrix(r[49:66]),projection=native_matrix(r[66:83]),viewport=state['viewport'],native_composed=native_matrix(r[25:42]),composition_error_pixels=state['native_composition_pixel_error'])]
    resources={r['id']:r for r in mesh['refs']['resources']}
    textures=[];lookup={};groups=[];indices=[];total=0
    output.mkdir(parents=True)
    for group in mesh['groups']:
        if not group['flags']&1 or group['primary'] not in resources:raise ValueError('Unqualified primary association')
        resource=resources[group['primary']];path=resolve_image(game_root,resource['filename'])
        original=path.read_bytes();digest=sha(original)
        if digest not in lookup:
            if len(textures)>=256:raise ValueError('Unique image cap')
            metadata,bgra=texture(original);total+=len(original)+len(bgra)+16
            if total>MAX_BYTES:raise ValueError('Combined image cap')
            index=len(textures);lookup[digest]=index
            payload=struct.pack('<4I',TEXTURE_MAGIC,metadata['width'],metadata['height'],len(bgra))+bgra
            (output/f'texture-{index}.bin').write_bytes(payload)
            textures.append(dict(**metadata,filename=resource['filename'],original_sha256=digest,
                decoded_bgra_sha256=sha(bgra),replay_sha256=sha(payload),bytes=len(payload)))
        selected=[start for identity,start in mesh['polygons'] if identity==group['group']]
        if not selected:continue
        first=len(indices)
        for start in selected:indices.extend((start,start+1,start+2))
        groups.append((group['group'],lookup[digest],first,len(indices)-first))
    if sorted(indices)!=list(range(len(mesh['corners']))):raise ValueError('Group coverage')
    vertices=[(*mesh['points'][i],*normal,*uv) for i,normal,uv in mesh['corners']]
    payload=struct.pack('<8I',MAGIC,1,len(vertices),len(indices),len(groups),len(frames),960,540)
    payload+=b''.join(struct.pack('<8f',*v) for v in vertices)
    payload+=struct.pack('<%dI'%len(indices),*indices)
    payload+=b''.join(struct.pack('<4I',*g) for g in groups)
    for f in frames:
        payload+=FRAME.pack(f['owner'],f['revision'],f['frame'],f['active'],
            *flatten(f['model']),*flatten(f['view']),*flatten(f['projection']),*f['viewport'])
    if len(payload)>2*1024*1024:raise ValueError('Replay mesh/frames byte cap')
    (output/'scene.bin').write_bytes(payload)
    # Content identity contains no renderer handles or native pointer IDs.
    identity=dict(geometry=mesh['geometry_sha256'],groups=[(g[0],textures[g[1]]['original_sha256'],g[2],g[3]) for g in groups])
    result=dict(schema='SFC-neutral-offline-scene-1',source_packet=str(source.relative_to(ROOT)),
        source_session=source_session,source_metadata=str(capture_metadata_path.relative_to(ROOT)),source_metadata_sha256=sha(capture_metadata_path.read_bytes()),
        source_packet_sha256=sha(raw),source_references_sha256=sha(refs),updates=str(updates.relative_to(ROOT)),
        updates_sha256=sha(updates.read_bytes()) if evidence_mode=='test' else None,
        evidence_mode=evidence_mode,model_name=mesh['refs']['model_filename'],
        geometry_sha256=mesh['geometry_sha256'],asset_sha256=sha(json.dumps(identity,sort_keys=True).encode()),
        replay_sha256=sha(payload),vertices=len(vertices),triangles=len(vertices)//3,groups=groups,
        textures=textures,frames=frames,image_bytes=total,image_warning=total>=64*1024*1024,
        conventions=dict(position='captured native units;no fit/origin shift',normal='captured corner normal',
            uv='captured UV unchanged;no Remix-specific V flip',matrix='column vectors;p_out=R*p_in+t;native affine dispatch decoded',
            projection='native RH perspective;native normalized depth;no OpenGL remap',
            image='original encoded color decoded top-row-first BGRA8;no gamma baking'),
        unsupported=['in-place deformation','native alpha/blend parity','secondary contribution not rendered',
            'lighting parity','live timing/presentation','full scene/frame sealing'],
        lights=dict(available=False,reason='not joined in this first replay;unlit primary-image qualification only'))
    if live_record is not None:
        result.update(preparation='fresh contemporaneous owner table;no saved ship template',fresh_preparation_row=list(live_record),fresh_preparation_row_sha256=sha(struct.pack('<96I',*live_record)))
    (output/'scene.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result


def read_replay(path):
    raw=Path(path).read_bytes()
    if not 32<=len(raw)<=2*1024*1024:raise ValueError('Replay byte cap')
    magic,version,nv,ni,ng,nf,w,h=struct.unpack_from('<8I',raw)
    if (magic!=MAGIC or version!=1 or not 3<=nv<=32768 or nv%3 or ni!=nv or not 1<=ng<=256 or
        not 1<=nf<=16 or not 1<=w<=1920 or not 1<=h<=1080 or
        len(raw)!=32+nv*32+ni*4+ng*16+nf*FRAME.size):raise ValueError('Replay schema')
    offset=32;vertices=[struct.unpack_from('<8f',raw,offset+i*32) for i in range(nv)]
    if not all(math.isfinite(x) for v in vertices for x in v):raise ValueError('Replay finite vertices')
    offset+=nv*32;indices=list(struct.unpack_from('<%dI'%ni,raw,offset));offset+=ni*4
    if sorted(indices)!=list(range(nv)):raise ValueError('Replay index coverage')
    groups=[struct.unpack_from('<4I',raw,offset+i*16) for i in range(ng)];offset+=ng*16
    cursor=0;identities=set()
    for identity,material,first,count in groups:
        if identity in identities or material>=256 or first!=cursor or not count or count%3 or count>ni-cursor:raise ValueError('Replay group')
        identities.add(identity)
        cursor+=count
    if cursor!=ni:raise ValueError('Replay group coverage')
    frames=[FRAME.unpack_from(raw,offset+i*FRAME.size) for i in range(nf)]
    for f in frames:
        if not all(f[i] for i in (0,1,2)) or f[3] not in (0,1) or not all(math.isfinite(x) for x in f[4:]):raise ValueError('Replay frame')
        x,y,vw,vh=f[-4:]
        if x<0 or y<0 or vw<=0 or vh<=0 or x+vw>1920 or y+vh>1080:raise ValueError('Replay viewport')
    return dict(vertices=vertices,indices=indices,groups=groups,frames=frames,width=w,height=h)
