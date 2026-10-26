"""Worker-only normal-Remix material replacements;never registers SDK geometry.

Policy is shared; each binding retains that asset's own original image pair.
Pinned BGRA8 single-mip upload uses4-byte row alignment(already width*4).
Unsupported upload layouts fail explicitly rather than assigning another material.
"""
from pathlib import Path
import hashlib
import io
import json
import struct
import subprocess
import sys
from collections import OrderedDict

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/remix_runtime'))
sys.path.insert(0,str(ROOT/'tools/scene_bridge'))
from material_controls import encode
from roughness_maps import pixels
from scene_bundle import resolve_image,texture
LIMIT=128*1024*1024
HASHER=ROOT/'artifacts/d3d9-proof/material-bin/texture_hash.exe'
DECODE_CACHE_BYTES=32*1024*1024  # Per preparation worker; no session-long image cache.


def validate_generated_dds(data,size):
    """Cheap bounds/layout checks, NOT a second image decode or pixel comparison."""
    width,height=size
    if not 1<=width<=4096 or not 1<=height<=4096:
        raise ValueError('Material dimension cap')
    if len(data)!=128+width*height*4:
        raise ValueError('Generated DDS byte count')
    header=struct.unpack_from('<32I',data)
    if (header[:8]!=(0x20534444,124,0x100F,height,width,width*4,0,0)
            or any(header[8:19])
            or header[19:28]!=(32,0x41,0,32,0x00FF0000,0x0000FF00,0x000000FF,0xFF000000,0x1000)
            or any(header[28:])):
        raise ValueError('Unsupported generated DDS layout')


def encode_generated_dds(image):
    if image.mode!='RGBA':raise ValueError('Generated DDS requires RGBA')
    if not 1<=image.width<=4096 or not 1<=image.height<=4096:
        raise ValueError('Material dimension cap')
    b=io.BytesIO();image.save(b,format='DDS');data=b.getvalue()
    validate_generated_dds(data,image.size)
    return data


def encode_remix_material_dds(image):
    # Remix replacement-material/DDS boundary ONLY. Captured UVs and ordinary
    # D3D9 uploads keep their original bits. Equivalent to old SDK v=1-v,once.
    # All generated color/emission/roughness maps share the same origin policy.
    from PIL import Image
    return encode_generated_dds(image.transpose(Image.Transpose.FLIP_TOP_BOTTOM))


def shader(name,images,values):
    if len(name)!=16 or any(c not in '0123456789ABCDEF' for c in name):
        raise ValueError('Material identity')
    # Only generated relative names are interpolated into USD,never asset paths.
    for path in images.values():
        if not path or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-./' for c in path) or '..' in path:
            raise ValueError('Unsafe generated texture path')
    inputs=[f'            asset inputs:diffuse_texture = @{images["color"]}@ (colorSpace = "sRGB")',
            f'            float inputs:reflection_roughness_constant = {values[0]:.9g}',
            f'            float inputs:metallic_constant = {values[2]:.9g}',
            f'            float inputs:anisotropy = {values[3]:.9g}',
            '            color3f inputs:diffuse_color_constant = (1, 1, 1)',
            '            float inputs:opacity_constant = 1',
            '            bool inputs:preload_textures = true',
            '            uchar inputs:filter_mode = 1',
            '            uchar inputs:wrap_mode_u = 1',
            '            uchar inputs:wrap_mode_v = 1']
    if 'roughness' in images:
        inputs.append(f'            asset inputs:reflectionroughness_texture = @{images["roughness"]}@ (colorSpace = "raw")')
    if 'emission' in images:
        inputs.extend([f'            asset inputs:emissive_mask_texture = @{images["emission"]}@ (colorSpace = "sRGB")',
                       '            bool inputs:enable_emission = true',
                       '            color3f inputs:emissive_color_constant = (1, 1, 1)',
                       f'            float inputs:emissive_intensity = {values[1]:.9g}'])
    else:inputs.append('            bool inputs:enable_emission = false')
    return (f'    def Material "mat_{name}"\n    {{\n'
            f'        token outputs:mdl:surface.connect = </RootNode/Looks/mat_{name}/Shader.outputs:out>\n'
            '        def Shader "Shader"\n        {\n'
            '            uniform token info:implementationSource = "sourceAsset"\n'
            '            uniform asset info:mdl:sourceAsset = @AperturePBR_Opacity.mdl@\n'
            '            token outputs:out\n'+'\n'.join(inputs)+'\n        }\n    }\n')


def prepare(folder,game_root,config=None,*,evidence_mode='test'):
    if evidence_mode not in ('performance','test'):raise ValueError('Material evidence mode')
    from PIL import Image
    import numpy as np
    folder=Path(folder);scene=json.loads((folder/'scene.json').read_text())
    source=ROOT/scene['source_packet']
    refs=json.loads(source.with_suffix('.json').read_text())
    if refs.get('textures_enabled')!=1:raise ValueError('Native textured path not enabled;no guessed appearance')
    if evidence_mode=='test' and (hashlib.sha256(source.read_bytes()).hexdigest()!=scene['source_packet_sha256'] or hashlib.sha256(source.with_suffix('.json').read_bytes()).hexdigest()!=scene['source_references_sha256']):
        raise ValueError('Fresh source association changed')
    raw=(config or (ROOT/'tools/remix_runtime/config/materials.toml').read_bytes())
    packet=encode(raw);values=struct.unpack('<2I10fQ',packet)[2:12]
    if not 1<=len(scene['textures'])<=256:raise ValueError('Ordinary material image count')
    hashes=subprocess.run([str(HASHER),'--batch',str(folder),str(len(scene['textures']))],capture_output=True,text=True,timeout=10,check=True,
                          creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)).stdout.splitlines()
    if len(hashes)!=len(scene['textures']) or any(not 1<=len(h)<=16 or any(c not in '0123456789abcdef' for c in h) for h in hashes):raise ValueError('Native material hash count/format')
    if values[3]<0:raise ValueError('Pinned normal USD material clamps negative anisotropy;unsupported baseline')
    output=folder/'rtx-remix/mods/sfc-policy';output.mkdir(parents=True,exist_ok=False)
    resource={r['id']:r for r in refs['resources']};groups={r['group']:r for r in refs['groups']}
    rows=[];bindings={};total=0;image_records={};original_seen=set()
    # SFC's fresh resource associations are authoritative. Within this immutable
    # preparation, reuse decoded originals and role-specific derivatives. Hashes
    # below identify/share content and name required Remix resources, not repeated
    # comparisons against an external model/texture baseline.
    decoded_cache=OrderedDict();decoded_bytes=0;derived={}
    def original(filename):
        nonlocal total,decoded_bytes
        key_name=filename.replace('\\','/').casefold()
        if evidence_mode=='performance' and key_name in decoded_cache:
            decoded_cache.move_to_end(key_name)
            return decoded_cache[key_name]
        path=resolve_image(game_root,filename);data=path.read_bytes()
        key=hashlib.sha256(data).hexdigest()
        if key not in original_seen:total+=len(data);original_seen.add(key)
        if len(original_seen)>256:raise ValueError('Material original image resource cap')
        if total>LIMIT:raise ValueError('Material original/derived image cap')
        with Image.open(io.BytesIO(data)) as image:
            if not 1<=image.width<=4096 or not 1<=image.height<=4096:raise ValueError('Material dimension cap')
            result=image.convert('RGBA'),key
        if evidence_mode=='performance':
            size=result[0].width*result[0].height*4
            if size<=DECODE_CACHE_BYTES:
                while decoded_bytes+size>DECODE_CACHE_BYTES:
                    _,(old,_)=decoded_cache.popitem(last=False)
                    decoded_bytes-=old.width*old.height*4
                decoded_cache[key_name]=result;decoded_bytes+=size
        return result
    def save(image):
        nonlocal total
        data=encode_remix_material_dds(image);digest=hashlib.sha256(data).hexdigest()
        name='textures/'+digest+'.dds';p=output/name
        if name not in image_records:
            total+=len(data)
            if total>LIMIT:raise ValueError('Material original/derived image cap')
            p.parent.mkdir(exist_ok=True);p.write_bytes(data)
            # SFC already uses these source images. Conversion correctness belongs
            # in offline regressions,not a per-load DDS pixel readback (~16s FCA).
            # Keep cheap layout/size checks above,provenance hashes and byte caps.
            image_records[name]=dict(sha256=digest,dimensions=list(image.size),bytes=len(data))
        return name
    def generated(key,make):
        # Check before conversion/encoding. Values are output names, not pixels;
        # at most three per captured group. Test mode retains full recomputation.
        if evidence_mode=='performance' and key in derived:return derived[key]
        name=save(make())
        if evidence_mode=='performance':derived[key]=name
        return name
    for identity,index,_,_ in scene['groups']:
        group=groups[identity];primary=resource[group['primary']]
        color,original_sha=original(primary['filename']);decoded=scene['textures'][index]
        if evidence_mode=='test' and original_sha!=decoded['original_sha256']:raise ValueError('Primary image mismatch')
        if evidence_mode=='test':
            packed=folder/f'texture-{index}.bin';metadata,bgra=texture(resolve_image(game_root,primary['filename']).read_bytes())
            if packed.read_bytes()!=struct.pack('<4I',0x31544653,metadata['width'],metadata['height'],len(bgra))+bgra:
                raise ValueError('Ordinary texture upload differs from source')
        name=hashes[index].upper().zfill(16)
        images=dict(color=generated(('color',original_sha),lambda:color));secondary_sha=None
        if group.get('flags',0)&0x20 and group.get('secondary') in resource:
            second,secondary_sha=original(resource[group['secondary']]['filename'])
            def emission():
                size=(max(color.width,second.width),max(color.height,second.height))
                a=color.convert('RGB').resize(size,Image.Resampling.BILINEAR)
                b=second.convert('RGB').resize(size,Image.Resampling.BILINEAR)
                return Image.fromarray(((np.asarray(a,dtype=np.uint16)*np.asarray(b,dtype=np.uint16)+127)//255).astype(np.uint8)).convert('RGBA')
            images['emission']=generated(('emission',original_sha,secondary_sha),emission)
        if values[4]:images['roughness']=generated(('roughness',original_sha,*values),lambda:pixels(color,values[0],values[5],values[6],values[7],bool(values[8]),values[9]))
        block=shader(name,images,values)
        if name in bindings and bindings[name]!=block:raise ValueError('Same primary hash has conflicting image pairs;requires distinct material identity')
        bindings[name]=block
        rows.append(dict(group=identity,ordinary_texture=index,remix_hash=name,primary_sha256=original_sha,secondary_sha256=secondary_sha,images=images))
    stage='#usda 1.0\n(defaultPrim = "RootNode")\ndef Xform "RootNode"\n{\n def Scope "Looks"\n {\n'+''.join(bindings.values())+' }\n}\n'
    (output/'mod.usda').write_text(stage,encoding='utf-8')
    # Runtime parses material tokens itself; no Toolkit,USD geometry,or mesh replacement.
    report=dict(schema='sfc.normal-remix.material-policy.v1',sdk_mesh_calls=0,geometry_modified=False,
                evidence_mode=evidence_mode,upload_pixel_comparison=evidence_mode=='test',
                source_recomparison=evidence_mode=='test',decoded_cache_limit=DECODE_CACHE_BYTES if evidence_mode=='performance' else 0,
                config_sha256=hashlib.sha256(raw).hexdigest(),values=list(values),groups=rows,images=image_records,
                image_bytes=total,image_warning=total>=64*1024*1024,
                generated_image_validation='Header/layout/dimensions/byte bounds only;pixel roundtrip tested offline',
                texture_origin='Remix replacement DDS rows vertically inverted once;captured UVs/original images/ordinary D3D9 uploads unchanged',
                emission='Provisional primary*secondary encoded-color product;existing Remix policy,not native fidelity',
                hash_scope='Pinned XXH3 BGRA8 single-mip;GetMipSize aligns width*4 to4bytes,so all supported widths are tightly packed',
                mod_sha256=hashlib.sha256(stage.encode()).hexdigest())
    (folder/'material-binding.json').write_text(json.dumps(report,indent=2))
    (folder/'materials-config-accepted.toml').write_bytes(raw)
    return report
