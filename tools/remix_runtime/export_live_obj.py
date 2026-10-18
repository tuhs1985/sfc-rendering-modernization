"""Export a retained fresh semantic mesh into isolated OBJ/MTL/PNG derivatives."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import struct
from run_coverage_probe import ROOT,decode_mesh

def export(folder,output):
    folder,output=Path(folder),Path(output)
    if output.exists():raise ValueError('Refusing to overwrite an existing export')
    fresh=json.loads((folder/'fresh-asset.json').read_text())
    source=ROOT/fresh['mesh']['source_packet']
    packet=source.read_bytes()
    if hashlib.sha256(packet).hexdigest()!=fresh['packet_sha256']:raise ValueError('Captured packet hash changed')
    mesh=decode_mesh(packet,source.with_suffix('.json').read_bytes())
    textures=json.loads((folder/'texture-manifest.json').read_text())
    if textures['geometry_sha256']!=mesh['geometry_sha256']:raise ValueError('Texture geometry association mismatch')
    assignments={x['group']:x for x in textures['materials']};images={};mtl=[]
    for group in mesh['groups']:
        row=assignments[group['group']];image=row['primary']
        if not image:raise ValueError('Untextured group not supported by this export')
        name=image['sha256']+'.png';src=folder/'textures'/name
        if hashlib.sha256(src.read_bytes()).hexdigest()!=image['png_sha256']:raise ValueError('Image derivative hash changed')
        images[name]=src
        mtl.extend([f"newmtl group_{group['group']}",'Ka 0 0 0','Kd 1 1 1','Ks 0 0 0','d 1','illum 1',f'map_Kd textures/{name}',''])
    lines=['# Fresh captured SFC geometry; no UV/axis/winding/normal repair',
           '# Original primary images only; no provisional runtime light or emission',
           'mtllib ship.mtl','o captured_ship']
    for index,normal,uv in mesh['corners']:
        for prefix,values in (('v',mesh['points'][index]),('vt',uv),('vn',normal)):
            lines.append(prefix+' '+' '.join(format(x,'.9g') for x in values))
    for group,start in mesh['polygons']:
        lines.extend([f'g group_{group}',f'usemtl group_{group}',
                      'f '+' '.join(f'{i}/{i}/{i}' for i in range(start+1,start+4))])
    obj='\n'.join(lines)+'\n';material='\n'.join(mtl)+'\n'
    total=len(obj.encode())+len(material.encode())+sum(p.stat().st_size for p in images.values())
    if len(obj.encode())>16*1024*1024 or total>128*1024*1024:raise ValueError('Export size cap')
    output.mkdir(parents=True);(output/'textures').mkdir()
    (output/'ship.obj').write_text(obj,encoding='utf-8');(output/'ship.mtl').write_text(material,encoding='utf-8')
    for name,src in images.items():shutil.copyfile(src,output/'textures'/name)
    result=dict(source_run=folder.name,model=fresh['model_name'],packet_sha256=fresh['packet_sha256'],
                geometry_sha256=mesh['geometry_sha256'],vertices=len(mesh['corners']),triangles=len(mesh['polygons']),
                groups=len(mesh['groups']),primary_images=len(images),bytes=total,
                conversion='Exact raw positions/per-corner normals/UVs and triangle order;no axis/UV flip;no normal normalization',
                lighting='No runtime light or emission exported;original primary images as diffuse colour only',
                limitations='Secondary-image role omitted;native shading/Blender texture convention unqualified;captured LOD only',
                obj_sha256=hashlib.sha256((output/'ship.obj').read_bytes()).hexdigest(),
                mtl_sha256=hashlib.sha256((output/'ship.mtl').read_bytes()).hexdigest(),
                image_sha256={name:hashlib.sha256((output/'textures'/name).read_bytes()).hexdigest() for name in images})
    (output/'manifest.json').write_text(json.dumps(result,indent=2))
    return result

def verify(folder,output):
    """Read back exported arrays/materials and compare to the captured packet."""
    folder,output=Path(folder),Path(output)
    fresh=json.loads((folder/'fresh-asset.json').read_text());source=ROOT/fresh['mesh']['source_packet']
    packet=source.read_bytes()
    if hashlib.sha256(packet).hexdigest()!=fresh['packet_sha256']:raise ValueError('Captured packet hash changed')
    mesh=decode_mesh(packet,source.with_suffix('.json').read_bytes())
    values={'v':[],'vt':[],'vn':[]};faces=[];current=None
    for line in (output/'ship.obj').read_text().splitlines():
        fields=line.split()
        if not fields:continue
        if fields[0] in values:values[fields[0]].append(tuple(map(float,fields[1:])))
        elif fields[0]=='usemtl':current=fields[1]
        elif fields[0]=='f':faces.append((current,fields[1:]))
    expected={'v':[mesh['points'][i] for i,_,_ in mesh['corners']],
              'vt':[uv for _,_,uv in mesh['corners']],'vn':[n for _,n,_ in mesh['corners']]}
    for name in values:
        a,b=values[name],expected[name]
        if len(a)!=len(b):raise ValueError('Exported array count mismatch')
        for x,y in zip(a,b):
            if len(x)!=len(y) or struct.pack('<%df'%len(x),*x)!=struct.pack('<%df'%len(y),*y):
                raise ValueError('Exported position/normal/UV changed')
    expected_faces=[(f'group_{g}',[f'{i}/{i}/{i}' for i in range(start+1,start+4)]) for g,start in mesh['polygons']]
    if faces!=expected_faces:raise ValueError('Exported triangle/group assignment changed')
    manifest=json.loads((output/'manifest.json').read_text())
    if manifest['packet_sha256']!=fresh['packet_sha256']:raise ValueError('Export source manifest mismatch')
    for name,key in (('ship.obj','obj_sha256'),('ship.mtl','mtl_sha256')):
        if hashlib.sha256((output/name).read_bytes()).hexdigest()!=manifest[key]:raise ValueError('Export hash mismatch')
    textures=json.loads((folder/'texture-manifest.json').read_text())
    expected_materials={f"group_{x['group']}":'textures/'+x['primary']['sha256']+'.png' for x in textures['materials']}
    actual={};name=None
    for line in (output/'ship.mtl').read_text().splitlines():
        fields=line.split()
        if fields and fields[0]=='newmtl':name=fields[1]
        elif fields and fields[0]=='map_Kd':actual[name]=fields[1]
    if actual!=expected_materials:raise ValueError('Exported texture assignment changed')
    for image in textures['materials']:
        primary=image['primary'];path=output/'textures'/(primary['sha256']+'.png')
        if hashlib.sha256(path.read_bytes()).hexdigest()!=primary['png_sha256']:raise ValueError('Exported texture pixels changed')
    return dict(result='LIVE_CAPTURE_OBJ_READBACK_PASS',vertices=len(mesh['corners']),triangles=len(faces),
                groups=len(actual),primary_images=len(manifest['image_sha256']),packet_sha256=fresh['packet_sha256'],
                geometry_source='Captured runtime packet only;installed MOD not opened')

def main():
    p=argparse.ArgumentParser();p.add_argument('capture',type=Path);p.add_argument('output',type=Path);p.add_argument('--verify',action='store_true');a=p.parse_args()
    if not a.verify:export(a.capture,a.output)
    print(json.dumps(verify(a.capture,a.output),indent=2))

if __name__=='__main__':main()
