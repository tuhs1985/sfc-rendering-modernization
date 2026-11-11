"""Remix adapter: original damage pairs, exact-black cutout and decal tagging.

Shared nine-material library prepared before gameplay. No model-file loading.
"""
from pathlib import Path
import hashlib
import json
import struct
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/remix_runtime'))
sys.path.insert(0,str(ROOT/'src/assets'))
sys.path.insert(0,str(ROOT/'src/runtime'))
from runtime_context import CONTEXT
sys.path.insert(0,str(ROOT/'tools/scene_bridge'))

PAIRS=(('light damage.bmp','light damage si.bmp'),('medium damage.bmp','medium damage si.bmp'),('heavy damage.bmp','heavy damage si.bmp'),
       ('starbase damage light.bmp','starbase damage lightSI.bmp'),('starbase damage medium.bmp','starbase damage mediumSI.bmp'),('starbase damage heavy.bmp','starbase damage heavySI.bmp'),
       ('organic damage light.bmp','organic damage lightSI.bmp'),('organic damage medium.bmp','organic damage mediumSI.bmp'),('organic damage heavy.bmp','organic damage heavySI.bmp'))

def black_cutout(image):
    import numpy as np
    from PIL import Image
    rgba=np.array(image.convert('RGBA'),copy=True)
    rgba[:,:,3]=np.where(np.all(rgba[:,:,:3]==0,axis=2),0,255).astype('uint8')
    return Image.fromarray(rgba)

def prepare(root,gpu):
    from parallel_assets import load_image,material_piece
    from material_binding import shader
    from material_controls import encode
    from remix_coordinates import bgra
    from mesh_checksum import texture_identity,asset_identity
    gpu=Path(gpu);stage=gpu/'rtx-remix/mods/sfc-damage';stage.mkdir(parents=True,exist_ok=True)
    raw=(CONTEXT.setting('rendering.toml')).read_bytes();values=struct.unpack('<2I10fQ',encode(raw))[2:12]
    entries=[];reports=[];blocks=[];hashes=[];total=0
    for i,(primary_name,secondary_name) in enumerate(PAIRS):
        primary=load_image(root,'assets/textures/'+primary_name);secondary=load_image(root,'assets/textures/'+secondary_name)
        cutout=black_cutout(primary['image']);primary={**primary,'image':cutout,'bgra':cutout.tobytes('raw','BGRA')}
        meta=primary['metadata'];w,h=meta['width'],meta['height']
        upload=bgra(primary['bgra'],w,h);payload=struct.pack('<4I',0x31544653,w,h,len(upload))+upload
        (gpu/f'damage-texture-{i}.bin').write_bytes(payload)
        hash_value=texture_identity(upload,w,h);hash_name=format(hash_value,'016X');hashes.append(hash_name)
        entries.append(struct.pack('<IIQ',w,h,asset_identity(payload)))
        piece=material_piece(primary,secondary,values)
        for name,(data,_) in piece['encoded'].items():
            target=stage/name;target.parent.mkdir(exist_ok=True);target.write_bytes(data);total+=len(data)
        block=shader(hash_name,piece['images'],values)
        block=block.replace('            bool inputs:preload_textures = true',
            '            bool inputs:use_legacy_alpha_state = true\n            bool inputs:preload_textures = true')
        blocks.append(block)
        total+=len(primary['raw'])+len(secondary['raw'])+len(payload)
        if total>128*1024**2:raise ValueError('Damage original/derived128MiB cap')
        reports.append(dict(index=i,family=i//3,severity=i%3,primary=primary_name,companion=secondary_name,
            primary_sha256=primary['sha256'],companion_sha256=secondary['sha256'],remix_hash=hash_name,
            texture_sha256=hashlib.sha256(payload).hexdigest(),width=w,height=h))
    (gpu/'damage-index.bin').write_bytes(struct.pack('<4I',0x314C4D44,1,9,total)+b''.join(entries))
    text='#usda 1.0\n(defaultPrim = "RootNode")\ndef Xform "RootNode"\n{\n def Scope "Looks"\n {\n'+''.join(blocks)+' }\n}\n'
    (stage/'mod.usda').write_text(text,encoding='utf-8')
    report=dict(version=1,images=reports,bytes=total,warning=total>=64*1024**2,
        transparency='Derived alpha0 only for exact RGB black;all other pixels alpha255;source RGB/files unchanged',
        mapping='Separate worker-generated native projection;original UVs preserved',
        adapter='Remix-only image-origin conversion and documented decalTextures/material blending',
        emission='Existing provisional primary*SI material policy;not a newly proven native lighting equation')
    (gpu/'damage-provenance.json').write_text(json.dumps(report,indent=2))
    return 'rtx.decalTextures = '+', '.join('0x'+v for v in hashes)+'\nrtx.enableDecalMaterialBlending = True\n'
