"""Read-only provenance/UV/material audit; no SFC launch or rendering changes."""
from pathlib import Path
import argparse
import hashlib
import json
import struct
import numpy as np
from PIL import Image
from run_coverage_probe import ROOT,decode_mesh

def audit(folder):
    folder=Path(folder)
    if not folder.resolve().is_relative_to((ROOT/'artifacts/remix-runtime/runs').resolve()):
        raise ValueError('Only retained runtime evidence may be audited')
    manifest=json.loads((folder/'fresh-asset.json').read_text())
    source=ROOT/manifest['mesh']['source_packet']
    if source.stat().st_size>2*1024*1024:raise ValueError('Packet bound')
    mesh=decode_mesh(source.read_bytes(),source.with_suffix('.json').read_bytes())
    raw=(folder/'live-mesh.bin').read_bytes()
    count=struct.unpack_from('<I',raw,8)[0]
    values=np.frombuffer(raw,dtype='<f4',offset=32).reshape(count,8)
    expected=np.asarray([(*mesh['points'][i],*normal,*uv) for i,normal,uv in mesh['corners']],dtype='<f4')
    if not np.array_equal(values,expected):raise ValueError('Native vertex/UV changed')
    textures=json.loads((folder/'texture-manifest.json').read_text())
    associations={x['group']:x for x in textures['materials']}
    resources={x['id']:x['filename'] for x in mesh['refs']['resources']}
    material=(folder/'live-materials.bin').read_bytes();h=struct.unpack_from('<8IQ',material)
    if h[:2]!=(0x31585453,1) or h[2]>256 or h[3]>256:raise ValueError('Material schema')
    names=[struct.unpack_from('<Q72s',material,40+i*80)[1].split(b'\0')[0].decode() for i in range(h[2])]
    groups=[struct.unpack_from('<4I',material,40+h[2]*80+i*16) for i in range(h[3])]
    indices=struct.unpack_from('<%dI'%h[4],material,40+h[2]*80+h[3]*16)
    checked={};saucer=[]
    for group in mesh['groups']:
        row=associations[group['group']];primary=row['primary']
        # ImageStore deduplicates byte-identical files; filename can be an alias.
        requested=ROOT.parent/'SFC-Remix-Return-Test'/resources[group['primary']]
        if hashlib.sha256(requested.read_bytes()).hexdigest()!=primary['sha256']:raise ValueError('Resource image hash mismatch')
        g=next(g for g in groups if g[0]==group['group'])
        if names[g[1]]!=primary['sha256']+'.dds':raise ValueError('Material association mismatch')
        expected_indices=[v for identity,start in mesh['polygons'] if identity==g[0] for v in (start,start+1,start+2)]
        if list(indices[g[2]:g[2]+g[3]])!=expected_indices:raise ValueError('Group/corner association mismatch')
        for image in (row['primary'],row['secondary']):
            if image is None or image['sha256'] in checked:continue
            original=folder/'textures'/(image['sha256']+'.original')
            b=original.read_bytes()
            if hashlib.sha256(b).hexdigest()!=image['sha256']:raise ValueError('Original hash mismatch')
            with Image.open(original) as im:rgba=np.asarray(im.convert('RGBA')).copy()
            with Image.open(folder/'textures'/(image['sha256']+'.dds')) as im:dds=np.asarray(im.convert('RGBA')).copy()
            with Image.open(folder/'textures'/(image['sha256']+'.png')) as im:png=np.asarray(im.convert('RGBA')).copy()
            if not np.array_equal(rgba,dds) or not np.array_equal(rgba,png):raise ValueError('Derived image pixels changed')
            item=dict(filename=image['filename'],sha256=image['sha256'],pixel_exact=True,
                      bmp_height=struct.unpack_from('<i',b,22)[0] if b[:2]==b'BM' else None)
            checked[image['sha256']]=item
        if Path(primary['filename']).name.lower()=='top.bmp':
            image=checked[primary['sha256']]
            with Image.open(folder/'textures'/(primary['sha256']+'.png')) as im:pixels=np.asarray(im.convert('RGB')).astype(float)
            saucer.append(dict(group=g[0],primary=primary['filename'],sha256=primary['sha256'],
                corner_count=g[3],bmp_height=image['bmp_height'],
                decoded_vertical_flip_mae=float(np.abs(pixels-pixels[::-1]).mean()),
                decoded_horizontal_flip_mae=float(np.abs(pixels-pixels[:,::-1]).mean()),
                source_vs_dds_mae=0.0))
    return dict(run=folder.name,vertices=count,groups=len(groups),unique_images=len(checked),
                vertex_uv_exact=True,resource_group_material_indices_exact=True,images_pixel_exact=True,
                saucer=saucer,conclusion='No saved-pixel or captured-UV flip introduced; native/GPU sampling relationship not established by byte equality')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('folder',type=Path)
    args=parser.parse_args();print(json.dumps(audit(args.folder),indent=2))

if __name__=='__main__':main()
