"""Development-only capture review and pixel/source comparisons; never shipped."""
import hashlib,io,json,math,os,struct,time
from pathlib import Path
from mesh_decode import decode_mesh,_decode_mesh
from live_bridge import affine
from live_scene import IMAGE_LIMIT,MEMORY_LIMIT
from scene_bundle import camera_state,native_matrix,resolve_image,texture

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


class ImageStore:
    """Worker-only immutable original+PNG copies with decoded/mipmap accounting."""
    def __init__(self,game_root,output):
        self.root=Path(game_root).resolve();self.output=Path(output);self.output.mkdir(exist_ok=True)
        self.images={};self.bytes=0;self.memory=0

    def load(self,filename):
        from PIL import Image
        name=filename.replace('\\','/');candidate=self.root/name;path=candidate.resolve()
        if not name or not path.is_relative_to(self.root) or any(p.is_symlink() for p in [candidate,*candidate.parents] if p!=self.root):raise ValueError('Unsafe image path')
        if not path.is_file() or path.stat().st_size>16*1024*1024:raise ValueError('Image file bound')
        raw=path.read_bytes();digest=hashlib.sha256(raw).hexdigest()
        if digest in self.images:return self.images[digest]
        if len(self.images)>=256:raise ValueError('Unique image cap')
        with Image.open(io.BytesIO(raw)) as image:
            if not 1<=image.width<=4096 or not 1<=image.height<=4096:raise ValueError('Image dimension bound')
            image.load();rgba=image.convert('RGBA');encoded=io.BytesIO();rgba.save(encoded,format='PNG');png=encoded.getvalue()
            encoded=io.BytesIO();rgba.save(encoded,format='DDS');dds=encoded.getvalue()
            memory=rgba.width*rgba.height*4*2  # decoded+GPU/mips conservative reservation
            if self.bytes+len(raw)+len(png)+len(dds)>IMAGE_LIMIT or self.memory+memory>MEMORY_LIMIT:raise ValueError('Image output/memory cap')
            with Image.open(io.BytesIO(png)) as check:
                if check.convert('RGBA').tobytes()!=rgba.tobytes():raise ValueError('PNG pixel mismatch')
            with Image.open(io.BytesIO(dds)) as check:
                if check.convert('RGBA').tobytes()!=rgba.tobytes():raise ValueError('DDS pixel mismatch')
            row=dict(sha256=digest,filename=name,format=image.format,width=image.width,height=image.height,
                alpha=rgba.getextrema()[3]!=(255,255),png=(self.output/(digest+'.png')).as_posix(),
                png_sha256=hashlib.sha256(png).hexdigest(),dds=(self.output/(digest+'.dds')).as_posix(),
                dds_sha256=hashlib.sha256(dds).hexdigest(),memory_bytes=memory)
        (self.output/(digest+'.original')).write_bytes(raw);Path(row['png']).write_bytes(png)
        Path(row['dds']).write_bytes(dds)
        self.bytes+=len(raw)+len(png)+len(dds);self.memory+=memory;self.images[digest]=row;return row


def qualify_mesh(packet,refs,images):
    data=decode_mesh(packet,refs);resources={r['id']:r for r in data['refs']['resources']};assignments=[];issues=[]
    for group in data['groups']:
        row=dict(group=group['group'],flags=group['flags'],primary=None,secondary=None)
        if data['refs'].get('textures_enabled')!=1:raise ValueError('Texture-disabled path not qualified')
        if group['flags']&1:
            if not group['primary'] or group['primary'] not in resources:raise ValueError('Unresolved primary image')
            row['primary']=images.load(resources[group['primary']]['filename'])
            if row['primary']['alpha']:issues.append(f"group {group['group']}: alpha image retained, native blend/alpha-test mapping unqualified")
        else:issues.append(f"group {group['group']}: untextured flag path not visually qualified")
        if group['flags']&0x20 and group['secondary']:
            if group['secondary'] not in resources:raise ValueError('Unresolved secondary association')
            row['secondary']=images.load(resources[group['secondary']]['filename'])
            issues.append(f"group {group['group']}: secondary role not applied; primary-only provisional material")
        assignments.append(row)
    identity=dict(geometry=data['geometry_sha256'],groups=[(x['group'],x['flags'],
        x['primary']['sha256'] if x['primary'] else None,x['secondary']['sha256'] if x['secondary'] else None) for x in assignments])
    data.update(assignments=assignments,issues=issues,asset_sha256=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest())
    return data


class SceneConsumer:
    def __init__(self):self.last={};self.retired=set();self.origin=None;self.seen={};self.revisions={};self.owners={};self.rejected=0
    def update(self,r,assets,now=None):
        now=time.monotonic() if now is None else now
        if r is None:return None
        if len(r)!=96 or not all(type(x)is int and 0<=x<=0xffffffff for x in r):self.rejected+=1;return None
        slot,owner=r[45],r[1]
        if not 0<=slot<32 or not owner:self.rejected+=1;return None
        if r[0]<=self.last.get(slot,0):return None
        self.last[slot]=r[0]
        key=(slot,owner)
        previous=self.owners.get(slot)
        if previous is not None and previous!=owner:
            if owner<previous:self.rejected+=1;return None
            self.retired.add((slot,previous));self.seen.pop(slot,None)
        self.owners[slot]=owner
        if r[4]==2:self.retired.add(key);self.seen.pop(slot,None);return None
        asset=assets.get(r[7])
        if (r[4]!=1 or key in self.retired or not asset or asset['header'][4]!=owner or
            tuple(asset['header'][i] for i in (10,12))!=(r[5],r[6]) or r[7]<self.revisions.get(slot,0) or any(r[42:45])):
            self.seen.pop(slot,None);self.rejected+=1;return None
        try:matrix,t=affine(r[8:25],self.origin)
        except ValueError:self.seen.pop(slot,None);self.rejected+=1;return None
        if self.origin is None:self.origin=t
        self.revisions[slot]=r[7];self.seen[slot]=(owner,now);return matrix
    def fresh(self,slot,now=None):
        now=time.monotonic() if now is None else now
        return slot in self.seen and now-self.seen[slot][1]<1


def decode_piece(packet, references, handoff, observation):
    """Preserve native arrays and qualify the separate indexed-draw origin."""
    data = _decode_mesh(packet, references, checksum=None, origin=0x0042EA92)
    h = data['header']
    if (not handoff.get('owner_epoch') or not handoff.get('asset_epoch')
            or not handoff.get('owner') or not observation.get('child')
            or observation.get('mesh_status') != 1
            or observation.get('references_status') != 1
            or not isinstance(observation.get('index'), int)
            or not 0 <= observation['index'] < observation.get('piece_count', 0)
            or observation.get('count') != h[17]
            or h[4] != handoff['owner_epoch'] or h[8] != observation['child']
            or h[9] != handoff.get('visual') or h[20:24] != (1, 0, 0, 0)):
        raise ValueError('Break-piece observation identity')
    name = data['refs'].get('model_filename', '').replace('\\', '/')
    if (name.lower() != handoff.get('model', '').replace('\\', '/').lower()
            or not name.lower().endswith('_brk.mod')):
        raise ValueError('Break visual resource identity')
    data['piece'] = dict(index=observation['index'], first=observation['first'],
                         count=observation['count'], child=observation['child'],
                         parent_owner_epoch=handoff['owner_epoch'],
                         visual_epoch=handoff['asset_epoch'])
    data['source_kind']='break_piece'
    return data


def decode_capture(folder):
    """Offline handoff to scene preparation, without changing normal admission."""
    folder = Path(folder)
    result = json.loads((folder / 'result.json').read_text())
    report = result['report']
    if (report.get('issues') or not report.get('finalized')
            or report.get('restored') not in ([0, 0, 14, 0], [0, 0, 16, 0])):
        raise ValueError('Break capture integrity is incomplete')
    observations = report['geometry']
    if not 1 <= len(observations) <= 4:
        raise ValueError('Diagnostic break snapshot capacity')
    pieces, slots, children = {}, set(), set()
    for observation in observations:
        slot = observation['slot']
        if (type(slot) is not int or not 0 <= slot < 4 or slot in slots
                or observation['index'] in pieces or observation['child'] in children):
            raise ValueError('Duplicate break capture identity')
        packet = (folder / f'break-piece-{slot}.bin').read_bytes()
        refs = (folder / f'break-piece-{slot}.json').read_bytes()
        pieces[observation['index']] = decode_piece(packet, refs, report['handoff'], observation)
        slots.add(slot)
        children.add(observation['child'])
    total = len(pieces)
    if set(pieces) != set(range(total)) or any(row['piece_count'] != total for row in observations):
        raise ValueError('Incomplete break model')
    first = 0
    points = pieces[0]['points']
    for index in range(total):
        piece = pieces[index]
        if piece['piece']['first'] != first or piece['points'] != points:
            raise ValueError('Break partition continuity or shared positions')
        first += piece['piece']['count']
    return dict(handoff=report['handoff'], pieces=pieces, triangles=first,
                points=points, poses=report['pieces'])


def streamed_layers(root,layers):
    """Offline-only derivative selecting Remix's existing texture-streaming path.

    Keep each original generated stage and every image unchanged. The sibling
    stage keeps relative texture paths valid; only the preload boolean differs.
    """
    root=Path(root).resolve();gpu=root.parents[2]
    if not 1<=len(layers)<=64:raise ValueError('Material library layer bound')
    outputs=[];count=0
    for layer in layers:
        stage=(root/layer).resolve();stage.relative_to(gpu)
        parts=stage.relative_to(gpu).parts
        if not(len(parts)==6 and parts[0]=='assets' and parts[1].isdigit()
               and parts[2:]==('rtx-remix','mods','sfc-policy','mod.usda')):
            raise ValueError('Unexpected generated material stage')
        if stage.stat().st_size>16*1024*1024:raise ValueError('Material stage metadata cap')
        text=stage.read_text(encoding='utf-8')
        old='bool inputs:preload_textures = true'
        n=text.count(old)
        if not 1<=n<=256 or text.count('inputs:preload_textures')!=n:
            raise ValueError('Unqualified texture preload declarations')
        target=stage.with_name('streamed.usda')
        if target.is_symlink():raise ValueError('Streaming derivative symlink')
        pending=stage.with_name('streamed.pending')
        if pending.is_symlink():raise ValueError('Streaming pending symlink')
        pending.write_text(text.replace(old,'bool inputs:preload_textures = false'),encoding='utf-8')
        pending.replace(target)
        path=os.path.relpath(target,root).replace('\\','/')
        if '@' in path or '\n' in path:raise ValueError('Unsafe streaming stage path')
        outputs.append(path);count+=n
    return outputs,count



def verify_material_source(source,scene):
    if (hashlib.sha256(source.read_bytes()).hexdigest()!=scene['source_packet_sha256']
            or hashlib.sha256(source.with_suffix('.json').read_bytes()).hexdigest()!=scene['source_references_sha256']):
        raise ValueError('Fresh source association changed')


def verify_material_upload(folder,index,game_root,filename,original_sha,decoded):
    if original_sha!=decoded['original_sha256']:raise ValueError('Primary image mismatch')
    packed=folder/f'texture-{index}.bin';metadata,bgra=texture(resolve_image(game_root,filename).read_bytes())
    if packed.read_bytes()!=struct.pack('<4I',0x31544653,metadata['width'],metadata['height'],len(bgra))+bgra:
        raise ValueError('Ordinary texture upload differs from source')
