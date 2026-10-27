"""Remix-only type overrides. Never change native SFC light records."""
import hashlib
import io
import math
from pathlib import Path
import struct

TYPES={'directional':0,'dome':1,'sphere':2,'rectangle':3,'disk':4,'cylinder':5,'spot':6}
FIELDS={'type','position','space','radius','width','height','length','axis','roll_degrees',
        'cone_angle_degrees','cone_softness','focus_exponent','environment_image','environment_rotation_degrees'}

def validate_shape(row,number,vector):
    kind=row.get('type','directional')
    if kind not in TYPES:raise ValueError('Unknown Remix light type')
    space=row.get('space','ship')
    if space not in ('ship','world'):raise ValueError('Light space must be ship or world')
    axis=vector(row.get('axis',[0,1,0]),-1e6,1e6);norm=math.hypot(*axis)
    if norm<1e-8:raise ValueError('Light axis must be nonzero')
    image=row.get('environment_image','')
    if not isinstance(image,str) or len(image)>1024:raise ValueError('Environment image path bound')
    return dict(type=kind,space=space,position=vector(row.get('position',[0,0,0]),-1e6,1e6),
        radius=number(row.get('radius',1),1e-5,1e5),width=number(row.get('width',2),1e-5,1e5),
        height=number(row.get('height',2),1e-5,1e5),length=number(row.get('length',2),1e-5,1e5),
        axis=[x/norm for x in axis],roll_degrees=number(row.get('roll_degrees',0),-360,360),
        cone_angle_degrees=number(row.get('cone_angle_degrees',45),0,180),
        cone_softness=number(row.get('cone_softness',.2),0,1),focus_exponent=number(row.get('focus_exponent',0),0,1000),
        environment_image=image,environment_rotation_degrees=number(row.get('environment_rotation_degrees',0),-360,360))

def environment(row,folder,base):
    from PIL import Image
    if row['type']!='dome':return '',None
    name=row['environment_image'];source=None
    if name:
        source=Path(name)
        if not source.is_absolute():source=Path(base)/source
        if source.stat().st_size>32*1024*1024:raise ValueError('Environment source32MiB cap')
        raw=source.read_bytes()
        with Image.open(io.BytesIO(raw)) as image:
            if max(image.size)>4096:raise ValueError('Environment4096dimension cap')
            image.load();rgba=image.convert('RGBA')
    else:raw=b'UNIFORM_WHITE_DOME_V1';rgba=Image.new('RGBA',(4,2),(255,255,255,255))
    encoded=io.BytesIO();rgba.save(encoded,format='DDS');dds=encoded.getvalue()
    digest=hashlib.sha256(dds).hexdigest();directory=Path(folder)/'textures';directory.mkdir(exist_ok=True)
    target=directory/(digest+'.dds')
    if not target.exists():
        if sum(p.stat().st_size for p in directory.iterdir() if p.is_file())+len(dds)+len(raw)>128*1024*1024:
            raise ValueError('Combined texture128MiB cap')
        if len(list(directory.glob('*.dds')))>=256:raise ValueError('Texture resource256cap')
        target.write_bytes(dds)
    return digest+'.dds',dict(source=str(source) if source else 'generated uniform white environment',
        source_sha256=hashlib.sha256(raw).hexdigest(),dds_sha256=digest,
        dimensions=list(rgba.size),dds_bytes=len(dds),source_unchanged=True,encoding='8bit RGBA DDS;not HDR')

def build(controls,revision,folder,base):
    from live_lights import fnv
    rows=[];manifest=[]
    for i in range(3):
        row=controls.get('project_fill',dict(id='project_fill',enabled=False,intensity_multiplier=0,
            color_multiplier=[1,1,1],volumetric_multiplier=1)) if i==2 else controls[f'native_directional_{i}']
        shape=row.get('shape')
        if shape is None:shape=validate_shape({},lambda v,l,h:v,lambda v,l,h:v)
        texture,provenance=environment(shape,folder,base)
        values=[shape['radius'],shape['width'],shape['height'],shape['length'],shape['cone_angle_degrees'],
                shape['cone_softness'],shape['focus_exponent'],shape['roll_degrees'],*shape['position'],*shape['axis'],
                shape['environment_rotation_degrees']]+[0]*13
        if i==2:
            values[15:18]=[row['intensity_multiplier']*c for c in row['color_multiplier']]
            from light_controls import angled_direction
            values[18:21]=angled_direction(row.get('direction_override',[0,-1,0]),row)
            values[21]=row.get('angular_diameter_degrees',.53);values[22]=row['volumetric_multiplier']
        rows.append(struct.pack('<4I28f128s',i,TYPES[shape['type']],int(shape['space']=='ship'),int(row['enabled']) if i==2 else 0,
                    *values,texture.encode('ascii')))
        manifest.append(dict(id=row['id'],origin='project' if i==2 else 'native',
            angle_mode=row.get('angle_mode','offset'),azimuth_degrees=row.get('azimuth_degrees',0),
            elevation_degrees=row.get('elevation_degrees',0),
            intensity_multiplier=row['intensity_multiplier'],color_multiplier=row['color_multiplier'],
            strength_basis='direct project radiance;not SFC conversion/master' if i==2 else 'captured native strength times conversion/master',
            **shape,prepared_environment=texture,environment_provenance=provenance,
            prepared_environment_sha256=texture[:-4] if texture else None))
    data=struct.pack('<4I2Q',0x50414853,2,808,3,revision,0)+b''.join(rows)
    return data+struct.pack('<Q',fnv(data)),manifest
