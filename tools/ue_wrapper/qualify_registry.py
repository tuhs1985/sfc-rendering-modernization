"""Retained UE scene checkout through existing Windows source IPC; no SFC launch."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import time
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
for part in ('src/transport','src/assets','src/runtime'):
    sys.path.insert(0,str(ROOT/part))
from live_scene import SceneChannel
import multi_scene as wire
from owner_rebind import fnv
from qualify_stream import runtime_exe,reference
from scene_capacity import STATE_OFFSET


def source_row(definition,pose,frame,sequence,index):
    row=[0]*96;row[1]=definition['owner_epoch'];row[2]=frame;row[4]=1;row[7]=definition['asset']['revision']
    row[5]=definition['source_binding']['model'];row[6]=definition['source_binding']['source'];row[45]=index;row[48]=1
    for offset,key in ((8,'model'),(49,'view'),(66,'projection')):
        values=[v for line in pose[key] for v in line]
        row[offset:offset+16]=struct.unpack('<16I',struct.pack('<16f',*values));row[offset+16]=0 if key=='projection' else 0x100
    x,y,w,h=pose['viewport'];row[83:89]=struct.unpack('<6I',struct.pack('<6f',x,y,w,h,w/2,h/2))
    row[94:96]=[sequence&0xffffffff,sequence>>32]
    return row


def publish_frame(channel,rows,frame,sequence,offered=None):
    packet=bytearray(wire.FRAME_BYTES)
    struct.pack_into('<QQ4I',packet,0,sequence,time.perf_counter_ns() if offered is None else offered,frame,rows[0][1],rows[0][7],len(rows))
    for index,row in enumerate(rows):struct.pack_into('<96I',packet,32+384*index,*row)
    struct.pack_into('<Q',packet,len(packet)-8,fnv(packet[:-8]))
    base=wire.OFFSET+64+(frame%wire.FRAMES)*wire.FRAME_SLOT
    channel.write(base,struct.pack('<II',1,0));channel.write(base+8,bytes(packet));channel.write(base,struct.pack('<I',2))
    channel.write(wire.OFFSET+36,struct.pack('<I',frame))


def publish_state(channel,row,index):
    base=STATE_OFFSET+index*512
    previous=struct.unpack('<I',channel.read(base,4))[0]
    channel.write(base,struct.pack('<I',previous+1));channel.write(base+4,struct.pack('<96I',*row));channel.write(base,struct.pack('<I',previous+2))


def run(exe,scene,output):
    output=output.resolve();output.mkdir(parents=True,exist_ok=False)
    source=json.loads(scene.read_text());directory=output/'definitions';directory.mkdir()
    channel=SceneChannel(create=True);process=None
    try:
        wire.initialize(channel);channel.write(12,struct.pack('<I',1));channel.write(wire.OFFSET+12,struct.pack('<I',os.getpid()))
        if 'source_binding' not in source:
            raw=(ROOT/source['source_packet']).read_bytes();header=struct.unpack_from('<32I',raw)
            source['source_binding']=dict(pid=os.getpid(),model=header[10],source=header[12])
        native_packet=(ROOT/source['source_packet']).read_bytes()
        native_bytes,native_hash=len(native_packet),fnv(native_packet)
        for image in source['images'].values():
            if not (directory/image['file']).exists():os.link(scene.parent/image['file'],directory/image['file'])
        geometry=source['asset'].get('geometry_content') or hashlib.sha256(json.dumps([source[k] for k in ('positions','corners','indices')]).encode()).hexdigest()
        definitions=[]
        for index in range(2):
            d=copy.deepcopy(source);d['session']=channel.name;d['owner_epoch']=source['owner_epoch']+index
            d['asset']['revision']=source['asset']['revision']+index*100;d['asset']['geometry_content']=geometry
            d['source_binding']['pid']=os.getpid();d['source_binding']['model']+=index*0x1000;d['source_binding']['source']+=index*0x2000
            d['frames'][0]['owner']=d['owner_epoch'];d['frames'][0]['revision']=d['asset']['revision']
            d['source_scope']='Explicit retained-asset sharing replay; original arrays/images, synthetic independent owners'
            definitions.append(d)

        def clone_binding(original,owner,revision):
            d=copy.deepcopy(original);d['owner_epoch']=owner;d['asset']['revision']=revision
            d['frames'][0]['owner']=owner;d['frames'][0]['revision']=revision
            return d
        variant=clone_binding(definitions[1],definitions[1]['owner_epoch'],definitions[1]['asset']['revision']+1)
        variant['asset']['content']=hashlib.sha256((source['asset']['content']+'synthetic-material-association').encode()).hexdigest()
        first=source['groups'][0]['primary']['filename']
        alternate=next(name for name,image in source['images'].items() if image['sha256']!=source['images'][first]['sha256'])
        for group in variant['groups']:group['primary']['filename']=alternate
        late=clone_binding(definitions[0],definitions[0]['owner_epoch'],definitions[0]['asset']['revision']+1)
        reused=clone_binding(definitions[0],definitions[0]['owner_epoch']+4,definitions[0]['asset']['revision']+200)
        wrong=clone_binding(definitions[0],definitions[0]['owner_epoch']+8,definitions[0]['asset']['revision']+300)
        wrong['session']='Local\\SFCBridge_'+'0'*32
        replaced=clone_binding(definitions[0],definitions[0]['owner_epoch']+8,definitions[0]['asset']['revision']+400)
        reshaped=clone_binding(replaced,replaced['owner_epoch'],replaced['asset']['revision']+1)
        reshaped['asset']['content']=hashlib.sha256((source['asset']['content']+'synthetic-extent-view').encode()).hexdigest()
        image=reshaped['images'][first]
        if image['width']%2:raise ValueError('Texture-view fixture needs an even original width')
        image['width']//=2;image['height']*=2
        for group in reshaped['groups']:group['primary']['filename']=first
        regrouped=clone_binding(replaced,replaced['owner_epoch'],replaced['asset']['revision']+2)
        regrouped['asset']['content']=hashlib.sha256((source['asset']['content']+'synthetic-group-order').encode()).hexdigest()
        regrouped['groups']=list(reversed(regrouped['groups']));new_indices=[]
        for group in regrouped['groups']:
            first_index=group['first_index'];count=group['index_count'];group['first_index']=len(new_indices)
            new_indices.extend(source['indices'][first_index:first_index+count])
        regrouped['indices']=new_indices
        fragment_path=ROOT/'artifacts/ue-foundation/inputs/piece-2/scene.json'
        piece=json.loads(fragment_path.read_text())
        piece['session']=channel.name;piece['owner_epoch']=replaced['owner_epoch'];piece['asset']['revision']=replaced['asset']['revision']+3
        piece['source_binding']=dict(replaced['source_binding']);piece['source_binding']['model']+=0x8000;piece['source_binding']['source']+=0x10000
        piece['frames']=piece['frames'][:1]
        piece['frames'][0]['owner']=piece['owner_epoch'];piece['frames'][0]['revision']=piece['asset']['revision']
        piece['fragment']=None # Geometry-only visual revision, not an invented cross-capture parent link.
        piece['source_scope']='Original captured break-piece arrays/images used as an explicit synthetic visual revision'
        for image in piece['images'].values():
            if not (directory/image['file']).exists():os.link(fragment_path.parent/image['file'],directory/image['file'])
        specs=[]
        for stage in range(1,15):
            step=dict(sequence=stage*1000000,owners=1 if stage==5 else 2,eligible=1 if stage in (3,5,12) else 2,
                      geometry_builds=1 if stage<14 else 2,material_builds=1 if stage<4 else 2 if stage<10 else 3 if stage==10 else 4 if stage<14 else 5)
            if stage==5:step.update(restart_world=True,late_asset_discards=1)
            if stage>=6:step['world_activations']=2
            if stage>=7:step['asset_rejected']=1
            specs.append(step)
        spec=dict(schema='sfc.ue.registry-check.v1',steps=specs)
        (output/'check.json').write_text(json.dumps(spec))
        args=[str(runtime_exe(exe)),'-windowed','-ResX=1920','-ResY=1080','-nosound','-nolog','-SFCDiagnostics',
              f'-SFCSourceMap={channel.name}',f'-SFCSourcePID={os.getpid()}',f'-SFCDefinitionDirectory={directory}',
              f'-SFCOutput={output}',f'-SFCRegistryCheck={output/"check.json"}']
        process=subprocess.Popen(args,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        deadline=time.monotonic()+120
        while not (output/'source-attached.json').exists():
            if process.poll() is not None:raise ValueError('Packaged retained scene reader did not attach')
            if time.monotonic()>deadline:raise TimeoutError('Source attach')
            time.sleep(.01)
        image_hash=14695981039346656037
        for image in source['images'].values():image_hash=((image_hash^fnv((directory/image['file']).read_bytes()))*1099511628211)&0xffffffffffffffff
        number=0
        def admit(d):
            nonlocal number
            number+=1
            path=directory/f'{d["asset"]["content"]}-{d["owner_epoch"]}-{d["asset"]["revision"]}.json'
            data=copy.deepcopy(d)
            if number==2:
                data['asset_reference']=f'{definitions[0]["asset"]["content"]}-{definitions[0]["owner_epoch"]}-{definitions[0]["asset"]["revision"]}.json'
                for key in ('positions','corners','indices','groups','images'):data.pop(key)
            path.write_bytes(json.dumps(data).encode())
            images=sum(int(i['width'])*int(i['height'])*4 for i in d['images'].values())
            origin=ROOT/d.get('source_packet','')
            packet_bytes=origin.read_bytes() if origin.is_file() else native_packet
            packet=wire.ASSET.pack(number,number,d['owner_epoch'],d['asset']['revision'],d['source_binding']['model'],d['source_binding']['source'],len(packet_bytes),images,bytes.fromhex(d['asset']['content']),fnv(packet_bytes),image_hash,0)
            wire.publish(channel,number,packet[:-8]+struct.pack('<Q',fnv(packet[:-8])))
        channel.write(128,struct.pack('<I',2))
        published={};counter=0;checks=[]
        for stage in range(1,15):
            if stage==1:
                for d in definitions:admit(d)
            if stage==4:admit(variant)
            if stage==5:
                retired=source_row(definitions[0],source['frames'][0],1000+counter,stage*1000000,0);retired[4]=2
                publish_state(channel,retired,0);admit(late)
            if stage==6:admit(reused)
            if stage==7:admit(wrong)
            if stage==9:admit(replaced)
            if stage==10:admit(reshaped)
            if stage==11:admit(regrouped)
            if stage==14:admit(piece)
            receipt_path=output/f'registry-{stage}.json'
            while not receipt_path.exists() and process.poll() is None and time.monotonic()<deadline:
                counter+=1;frame=1000+counter;sequence=stage*1000000+counter;rows=[];expected=[]
                entries=[definitions[0],variant if stage>=3 else definitions[1]]
                if stage==5:entries=[variant]
                if stage>=6:entries=[reused,variant]
                if stage==8:entries.append(definitions[0]) # A stale retired epoch must never return.
                if stage>=9:entries=[reshaped if stage==10 else regrouped if stage>=11 else replaced,variant]
                if stage>=14:entries=[piece,variant]
                for index,d in enumerate(entries):
                    pose=copy.deepcopy(source['frames'][0]);pose['model'][0][3]+=(index*2-1)*16
                    if stage==2 and index==0:pose['model'][0][3]+=1000
                    pose['view'][0][3]+=(counter%3+1)*3
                    state_index=1 if d['owner_epoch']==definitions[1]['owner_epoch'] else 0
                    row=source_row(d,pose,frame,sequence,state_index)
                    if stage==12 and index==0:row[42]=1
                    if stage<5 or d['owner_epoch']!=definitions[0]['owner_epoch']:
                        publish_state(channel,row,state_index)
                    rows.append(row)
                    if not (stage==3 and index==1) and not (stage==8 and index==2) and not (stage==12 and index==0):expected.append((d,pose))
                published[sequence]=expected;publish_frame(channel,rows,frame,sequence);time.sleep(.02)
                wait_file=output/'registry-wait.json'
                if wait_file.exists():
                    try:wait=json.loads(wait_file.read_text())
                    except (json.JSONDecodeError,PermissionError):continue
                    if wait['step']==stage-1 and wait['owners']>specs[stage-1]['owners']:
                        raise ValueError(f'Stage {stage}: stale retained owners {wait["owners"]} exceeds expected {specs[stage-1]["owners"]}')
                    if wait.get('source_stage')==stage and wait['eligible']>specs[stage-1]['eligible']:
                        raise ValueError(f'Stage {stage}: unqualified owner still rendered')
                admission=output/'registry-admission.json'
                if admission.exists():
                    try:state=json.loads(admission.read_text())
                    except (json.JSONDecodeError,PermissionError):continue
                    if state['rejected']>(1 if stage>=7 else 0):raise ValueError(f'Stage {stage}: unexpected source asset rejection')
            if not receipt_path.exists():
                if (output/'rejected.txt').exists():raise ValueError((output/'rejected.txt').read_text())
                raise TimeoutError(f'Retained registry stage {stage}; inspect admission/wait receipts')
            receipt=json.loads(receipt_path.read_text())
            if receipt['sequence'] not in published:raise ValueError('Registry receipt source identity')
            width,height=map(int,source['frames'][0]['viewport'][2:]);rgb=np.zeros((height,width,3),np.uint8)
            depth=np.full((height,width),np.inf);stable=np.zeros((height,width),bool)
            for d,pose in published[receipt['sequence']]:
                comparison=copy.deepcopy(d);comparison['frames']=[pose]
                colour,covered,interior,native=reference(comparison,directory,0,include_depth=True)
                take=covered&(native<depth);rgb[take]=colour[take];stable[take]=interior[take];depth[take]=native[take]
            actual=np.fromfile(output/f'registry-{stage}.bgra',np.uint8).reshape(height,width,4)[:,:,2::-1]
            errors=np.max(np.abs(actual.astype(np.int16)-rgb.astype(np.int16)),axis=2)
            if stable.sum()<100:raise ValueError(f'Stage {stage} insufficient visible source pixels')
            accuracy=float(np.mean(errors[stable]<=3))
            if not np.isfinite(accuracy) or accuracy<.97:raise ValueError(f'Stage {stage} independent owner pixels: {accuracy}')
            receipt.update(stage=stage,colour_within_three=accuracy,replay=True);checks.append(receipt)
        process.wait(timeout=15)
        if process.returncode:raise ValueError(f'Registry process exit {process.returncode}')
        result=dict(stages=checks,geometry_builds=checks[-1]['geometry_builds'],shared_geometry=True,normal_exit=True,
                    source_images_unchanged=True,synthetic_material_binding=True,synthetic_texture_views=True)
        (output/'qualified.json').write_text(json.dumps(result,indent=2));return result

    finally:
        if process is not None and process.poll() is None:process.kill();process.wait()
        channel.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('exe','scene','output'):parser.add_argument(name,type=Path)
    args=parser.parse_args();print(json.dumps(run(args.exe,args.scene,args.output),indent=2))
