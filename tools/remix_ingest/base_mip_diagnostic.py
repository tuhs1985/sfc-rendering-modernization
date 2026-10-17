"""Approved scratch-only DDS mip-chain experiment; no pixel recompression."""
import hashlib
import json
from pathlib import Path
import struct
from PIL import Image


def base_only(raw):
    if len(raw)<148 or raw[:4]!=b'DDS ' or raw[84:88]!=b'DX10' or struct.unpack_from('<I',raw,128)[0]!=98:
        raise ValueError('Only the observed BC7 DX10 DDS layout is qualified')
    height,width=struct.unpack_from('<2I',raw,12)
    if (width,height)!=(256,256) or struct.unpack_from('<I',raw,140)[0]!=1:
        raise ValueError('Only selected 256-square, single-image texture is qualified')
    size=((width+3)//4)*((height+3)//4)*16
    if len(raw)<148+size: raise ValueError('Truncated base image')
    out=bytearray(raw[:148+size])
    struct.pack_into('<I',out,28,1)
    struct.pack_into('<I',out,8,struct.unpack_from('<I',out,8)[0]&~0x20000)
    struct.pack_into('<I',out,108,struct.unpack_from('<I',out,108)[0]&~(8|0x400000))
    return bytes(out)


def prepare(work):
    work=Path(work).resolve()
    config_path=work/'preview-config.json'
    config=json.loads(config_path.read_text())
    if Path(config['work']).resolve()!=work or not config.get('textures') or not config.get('smoke'):
        raise ValueError('Requires freshly prepared textured smoke scratch job')
    paths=sorted((work/'textures').glob('*.dds'))
    if len(paths)!=5: raise ValueError('Expected five primary textures')
    rows=[]
    for path in paths:
        if path.is_symlink() or not path.resolve().is_relative_to(work): raise ValueError('Unsafe scratch path')
        raw=path.read_bytes(); converted=base_only(raw)
        from io import BytesIO
        with Image.open(BytesIO(raw)) as a, Image.open(BytesIO(converted)) as b:
            if a.convert('RGBA').tobytes()!=b.convert('RGBA').tobytes(): raise ValueError('Base decoded pixels changed')
        before=hashlib.sha256(raw).hexdigest();after=hashlib.sha256(converted).hexdigest()
        relative=str(path.relative_to(work))
        if config['dependency_sha256'].get(relative)!=before: raise ValueError('Unexpected dependency before mutation')
        path.write_bytes(converted) # owned new scratch derivative, never original/import output
        config['dependency_sha256'][relative]=after
        rows.append(dict(path=relative,before_sha256=before,after_sha256=after,
                         before_bytes=len(raw),after_bytes=len(converted),base_payload_unchanged=raw[148:148+65536]==converted[148:],mips_after=1))
    config['base_mip_diagnostic']=True
    config_path.write_text(json.dumps(config,indent=2)+'\n')
    (work/'base-mip-diagnostic.json').write_text(json.dumps(dict(schema='sfc.base-mip.diagnostic.v1',textures=rows,
        scope='scratch textures only; no recompression or change of base pixels, geometry, UV, lights, camera'),indent=2)+'\n')
