"""Dependency-driven preparation. Four workers; only the coordinator joins tasks.

Experimental until progressive USD consumption passes the existing GPU checks.
No engine callbacks, native interfaces or worker-to-worker waits.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import io
import json
import struct
import threading
import time

WORKERS=4
ACTIVE_ASSETS=4
IMAGE_BYTES=256*1024*1024  # Working RGBA+BGRA+encoded originals; output limits unchanged.


class Tasks:
    def __init__(self,workers=WORKERS):
        if not 1<=workers<=WORKERS:raise ValueError('Task worker bound')
        self.pool=ThreadPoolExecutor(max_workers=workers,thread_name_prefix='SFC-parts')
        self.tasks={};self.spans=[];self.closed=False;self.workers=workers

    def add(self,key,fn,deps=(),priority=None):
        if self.closed:raise ValueError('Preparation closed')
        if key in self.tasks:
            if priority is not None:
                old=self.tasks[key].get('priority')
                self.tasks[key]['priority']=priority if old is None else min(old,priority)
            return
        if len(self.tasks)>=8192:raise ValueError('Preparation task capacity')
        self.tasks[key]=dict(fn=fn,deps=tuple(deps),state='queued',future=None,priority=priority)

    def _run(self,key,fn,args):
        begin=time.perf_counter_ns()
        try:return dict(value=fn(*args),begin_ns=begin,end_ns=time.perf_counter_ns(),thread=threading.get_ident())
        except Exception as e:return dict(error=str(e),begin_ns=begin,end_ns=time.perf_counter_ns(),thread=threading.get_ident())

    def pump(self):
        done=[]
        priority={'decode':0,'geometry':0,'basic':1,'hashes':1,'material':3,'derived':3,'image':2,'read_image':2}
        def order(item):return item[1]['priority'] if item[1].get('priority') is not None else priority.get(item[0][0],4)
        for key,t in sorted(list(self.tasks.items()),key=order):
            if t['state']=='running' and t['future'].done():
                r=t.pop('future').result();t.update(r,state='failed' if 'error' in r else 'done')
                t['fn']=None
                self.spans.append(dict(task=list(key),**{k:v for k,v in r.items() if k!='value'}));done.append(key)
        active=sum(t['state']=='running' for t in self.tasks.values())
        for key,t in sorted(list(self.tasks.items()),key=order):
            if t['state']!='queued':continue
            if any(self.tasks[d]['state']=='failed' for d in t['deps']):
                t.update(state='failed',error='Dependency failed',fn=None);done.append(key);continue
            if active>=self.workers or not all(self.tasks[d]['state']=='done' for d in t['deps']):continue
            t['future']=self.pool.submit(self._run,key,t['fn'],[self.tasks[d]['value'] for d in t['deps']])
            t['state']='running';active+=1
        return done

    def close(self):
        if self.closed:return
        self.closed=True;self.pool.shutdown(wait=True,cancel_futures=True)
        for key,t in self.tasks.items():
            if t['state']=='running':
                future=t.pop('future',None)
                if future is not None and not future.cancelled():
                    result=future.result()
                    self.spans.append(dict(task=list(key),shutdown=True,**{k:v for k,v in result.items() if k!='value'}))
            if t['state'] in ('running','queued'):t.update(state='cancelled',fn=None)


def read_image(root,filename):
    from scene_bundle import resolve_image
    raw=resolve_image(root,filename).read_bytes()
    return dict(raw=raw,sha256=hashlib.sha256(raw).hexdigest())


def load_image(root,filename,source_data=None):
    """One read/decode supplies ordinary BGRA and all enhanced material roles."""
    from PIL import Image
    source_data=source_data if source_data is not None else read_image(root,filename)
    raw=source_data['raw']
    with Image.open(io.BytesIO(raw)) as source:
        if not 1<=source.width<=4096 or not 1<=source.height<=4096:raise ValueError('Texture dimensions')
        image=source.convert('RGBA')
        opaque=image.getextrema()[3]==(255,255)
        metadata=dict(width=image.width,height=image.height,format=source.format)
    return dict(raw=raw,sha256=source_data['sha256'],image=image,
                metadata=metadata,bgra=image.tobytes('raw','BGRA'),opaque=opaque)


def material_piece(primary,secondary,values):
    from PIL import Image
    import numpy as np
    from material_binding import encode_remix_material_dds
    from roughness_maps import pixels
    color=primary['image'];encoded={}
    def save(image):
        data=encode_remix_material_dds(image);digest=hashlib.sha256(data).hexdigest()
        name='textures/'+digest+'.dds'
        encoded[name]=(data,dict(sha256=digest,dimensions=list(image.size),bytes=len(data)))
        return name
    images=dict(color=save(color))
    if secondary is not None:
        second=secondary['image'];size=(max(color.width,second.width),max(color.height,second.height))
        a=color.convert('RGB').resize(size,Image.Resampling.BILINEAR)
        b=second.convert('RGB').resize(size,Image.Resampling.BILINEAR)
        emission=Image.fromarray(((np.asarray(a,dtype=np.uint16)*np.asarray(b,dtype=np.uint16)+127)//255).astype(np.uint8)).convert('RGBA')
        images['emission']=save(emission)
    if values[4]:images['roughness']=save(pixels(color,values[0],values[5],values[6],values[7],bool(values[8]),values[9]))
    return dict(images=images,encoded=encoded,primary_sha256=primary['sha256'],
                secondary_sha256=secondary['sha256'] if secondary else None)


class Pipeline:
    """At most four decoded assets; tiny pending descriptors cover remaining64.

    Each decoded input set is limited256MiB (RGBA+BGRA+original combined).
    Geometry/textures are immutable. Material pieces are published only by pump.
    """
    def __init__(self,relay):
        self.relay=relay;self.graph=Tasks();self.jobs={};self.contents={}
        self.spans=self.graph.spans;self.closed=False;self.events=[];self.image_users={}
        from material_controls import encode
        self.values=struct.unpack('<2I10fQ',encode(relay.material_config))[2:12]
        if self.values[3]<0:raise ValueError('Negative normal USD anisotropy unsupported')

    def submit(self,identity,row):
        if self.closed or identity in self.jobs or not 1<=identity<=64:raise ValueError('Preparation job identity/state')
        self.jobs[identity]=dict(id=identity,row=list(row),phase='waiting',discovered_ns=time.perf_counter_ns())

    def decode(self,job):
        from live_scene import decode_mesh
        from mesh_checksum import calculate
        source=self.relay.folder/'gate'/f"LIVE-SCENE-001-asset-{job['row'][7]}.bin"
        if source.stat().st_size>2*1024*1024 or source.with_suffix('.json').stat().st_size>256*1024:raise ValueError('Capture bounds')
        raw=source.read_bytes();refs=source.with_suffix('.json').read_bytes()
        mesh=decode_mesh(raw,refs,checksum=calculate)
        row=job['row']
        if (mesh['header'][4],mesh['header'][10],mesh['header'][12])!=(row[1],row[5],row[6]):raise ValueError('Capture owner identity')
        mesh['_capture_refs_sha256']=hashlib.sha256(refs).hexdigest()
        return source,raw,refs,mesh

    def _expand(self,job,capture):
        from scene_bundle import geometry_parts
        source,raw,refs,mesh=capture;job.update(capture=capture,phase='parts')
        resources={r['id']:r for r in mesh['refs']['resources']}
        primary=[];secondary=[]
        for g in mesh['groups']:
            if not g['flags']&1 or g['primary'] not in resources:raise ValueError('Unqualified primary association')
            primary.append(resources[g['primary']]['filename'])
            if g['secondary'] in resources:secondary.append(resources[g['secondary']]['filename'])
        job['primary']=list(dict.fromkeys(primary));names=list(dict.fromkeys(primary+secondary))
        if not 1<=len(names)<=256:raise ValueError('Image count')
        job['images']={};job['source_images']={};job['image_keys']={};job['read_keys']={}
        geometry=('geometry',job['id']);job['geometry_key']=geometry
        self.graph.add(geometry,lambda:geometry_parts(mesh))
        # Geometry and each image are independent tasks, not serial functions.
        for n,name in enumerate(names):
            key=('image',name.replace('\\','/').casefold());job['image_keys'][name]=key
            self.image_users.setdefault(key,set()).add(job['id'])
            read=('read_image',key[1]);job['read_keys'][name]=read
            self.image_users.setdefault(read,set()).add(job['id'])
            priority=2 if name in job['primary'] else 3
            self.graph.add(read,lambda name=name:read_image(self.relay.root,name),priority=priority)
            self.graph.add(key,lambda data,name=name:load_image(self.relay.root,name,data),(read,),priority=priority)
        job['materials']=[];job['material_done']=set();job['piece_keys']={};job['basic_ready']=False

    def _basic(self,job):
        from scene_bundle import prepare
        import multi_scene as wire
        from mesh_checksum import asset_identity
        started=time.perf_counter_ns();steps=[]
        source,raw,refs,mesh=job['capture'];images=job['images']
        # Base residency identity needs base content only. Secondary association
        # names disambiguate policies without waiting for enhancement IO. Image
        # hashes for enhanced materials remain attached to each completed piece.
        resources={r['id']:r for r in mesh['refs']['resources']}
        identity=[mesh['geometry_sha256'],list(mesh['header'][20:23]),mesh['refs'].get('secondary_role'),[
            [g['group'],g['flags'],images[resources[g['primary']]['filename']]['sha256'],
             resources.get(g['secondary'],{}).get('filename','').replace('\\','/').casefold() if g['flags']&0x20 else None]
            for g in mesh['groups']]]
        signature=hashlib.sha256(json.dumps(['sfc.base-asset.v2.remix-image-origin-v1',identity],sort_keys=True,separators=(',',':')).encode()).hexdigest()
        steps.append(dict(stage='base_identity',seconds=(time.perf_counter_ns()-started)/1e9));begin=time.perf_counter_ns()
        from remix_coordinates import base_image,POLICY
        if sum(len(i['raw'])+2*len(i['bgra']) for i in images.values())+sum(len(images[n]['bgra']) for n in job['primary'])>IMAGE_BYTES:
            raise ValueError('Remix base adaptation256MiB working cap')
        upload_images={name:base_image(images[name]) for name in job['primary']}
        folder=job['output']
        manifest=prepare(source,folder,self.relay.root,live_record=job['row'],evidence_mode='performance',
            qualified_mesh=mesh,prepared_capture=(raw,refs),prepared_images=upload_images,
            prepared_geometry=self.graph.tasks[job['geometry_key']]['value'],output_extent=(1920,1080),identity_calculator=asset_identity)
        steps.append(dict(stage='bundle_assembly_and_write',seconds=(time.perf_counter_ns()-begin)/1e9));begin=time.perf_counter_ns()
        packet=wire.prepared_packet(job['id'],job['id'],job['row'],signature,manifest['catalog_identity'])
        steps.append(dict(stage='catalog_from_written_bytes',seconds=(time.perf_counter_ns()-begin)/1e9))
        manifest['conventions']['image']='Remix-only bottom-row-first BGRA8;original images/captured UV unchanged'
        manifest['remix_texture_origin']=POLICY
        (folder/'scene.json').write_text(json.dumps(manifest,indent=2))
        manifest['base_identity_schema']='sfc.base-asset.v2.remix-image-origin-v1;primary content plus declared enhancement associations;not enhanced readiness'
        return folder,manifest,signature,packet,steps

    def _queue_derivatives(self,job):
        # Pure image work does not require the bundle, a native texture identity,
        # a renderer or a completed secondary image belonging to another group.
        mesh=job['capture'][3];resources={r['id']:r for r in mesh['refs']['resources']}
        for group in mesh['groups']:
            identity=group['group'];key=('material',job['id'],identity)
            if key in self.graph.tasks:continue
            primary=job['images'].get(resources[group['primary']]['filename'])
            secondary=None
            if group['flags']&0x20:
                resource=resources.get(group['secondary'])
                if resource is None:job['enhancement_error']='Missing secondary association';continue
                secondary=job['images'].get(resource['filename'])
                if secondary is None:continue
            if primary is None:continue
            delay=getattr(self.relay,'parallel_material_delay_ms',0)
            if delay and identity==mesh['groups'][-1]['group'] and (not job['basic_ready'] or time.perf_counter_ns()<job['basic_ready_ns']+delay*1_000_000):continue
            values=self.values
            digest=hashlib.sha256(json.dumps([primary['sha256'],secondary['sha256'] if secondary else None,list(values)]).encode()).hexdigest()
            shared=('derived',digest);job['piece_keys'][identity]=shared
            self.image_users.setdefault(shared,set()).add(job['id'])
            self.graph.add(shared,lambda p=primary,s=secondary,v=values:material_piece(p,s,v))
            self.graph.add(key,lambda piece:dict(piece),(shared,))

    def _materials(self,job):
        # Only the material's native identity needs base texture ordering. Image
        # generation already runs independently; no subprocess or file rereads.
        from mesh_checksum import texture_identity
        values=self.values
        folder=job['gpu'];scene=job['manifest'];mesh=job['capture'][3]
        resources={r['id']:r for r in mesh['refs']['resources']};groups={g['group']:g for g in mesh['groups']}
        hashes=[]
        for t in scene['textures']:
            image=job['images'][t['filename']]
            from remix_coordinates import bgra as remix_bgra
            upload=remix_bgra(image['bgra'],t['width'],t['height'])
            hashes.append(format(texture_identity(upload,t['width'],t['height']),'x'))
        if len(hashes)!=len(scene['textures']) or any(not 1<=len(h)<=16 or any(c not in '0123456789abcdef' for c in h) for h in hashes):raise ValueError('Material hash format/count')
        return values,hashes,resources,groups

    def pump(self):
        if self.closed:return []
        completed=[];self.graph.pump()
        for key,users in list(self.image_users.items()):
            task=self.graph.tasks.get(key)
            if not users and task and task['state'] not in ('running','queued'):
                self.graph.tasks.pop(key);self.image_users.pop(key,None)
        for job in self.jobs.values():
            if job['phase'] in ('failed','alias'):
                for key,t in self.graph.tasks.items():
                    if len(key)>1 and key[1]==job['id'] and t['state']=='queued':t.update(state='failed',error='Asset retired from preparation',fn=None)
                if not any(t['state']=='running' for key,t in self.graph.tasks.items() if len(key)>1 and key[1]==job['id']):self._release(job)
        active=sum('reservation' in j for j in self.jobs.values())
        for job in self.jobs.values():
            if job['phase']=='waiting' and active<ACTIVE_ASSETS:
                # Reservation remains held across all tasks, not one per piece.
                try:
                    job['output']=self.relay.folder/'gpu/staging'/str(job['id'])
                    job['reservation']=self.relay.output_reservations.asset(lambda job=job:job['output'])
                    job['reservation'].__enter__()
                    self.graph.add(('decode',job['id']),lambda job=job:self.decode(job))
                    job['phase']='decode';active+=1
                except ValueError:job.pop('reservation',None);continue
            if job['phase'] in ('waiting','ready','failed','alias'):continue
            try:
                if job['phase']=='decode':
                    t=self.graph.tasks[('decode',job['id'])]
                    if t['state']=='failed':raise ValueError(t['error'])
                    if t['state']!='done':continue
                    self._expand(job,t.pop('value'));continue
                for name,key in job['read_keys'].items():
                    t=self.graph.tasks[key]
                    if t['state']=='failed':
                        if name in job['primary']:raise ValueError(t['error'])
                        job['enhancement_error']=t['error'];continue
                    if t['state']=='done':job['source_images'][name]=t['value']
                for name,key in job['image_keys'].items():
                    t=self.graph.tasks[key]
                    if t['state']=='failed':
                        if name in job['primary']:raise ValueError(t['error'])
                        job['enhancement_error']=t['error'];continue
                    if t['state']=='done' and name not in job['images']:job['images'][name]=t['value']
                used=sum(len(i['raw']) for i in job['source_images'].values())+sum(len(i['bgra'])*2 for i in job['images'].values())
                job['peak_working_image_bytes']=max(job.get('peak_working_image_bytes',0),used)
                if used>IMAGE_BYTES:raise ValueError('Decoded asset256MiB working cap')
                g=self.graph.tasks[job['geometry_key']]
                if g['state']=='failed':raise ValueError(g['error'])
                self._queue_derivatives(job)
                if not job['basic_ready'] and g['state']=='done' and all(n in job['images'] for n in job['primary']):
                    if any(not job['images'][n]['opaque'] for n in job['primary']):raise ValueError('Primary alpha unsupported')
                    key=('basic',job['id'])
                    self.graph.add(key,lambda job=job:self._basic(job));job['phase']='basic'
                if job['phase']=='basic':
                    t=self.graph.tasks[('basic',job['id'])]
                    if t['state']=='failed':raise ValueError(t['error'])
                    if t['state']!='done':continue
                    folder,manifest,signature,packet,steps=t.pop('value');job['base_steps']=steps
                    job.update(gpu=folder,manifest=manifest,signature=signature,basic_ready=True,phase='materials',wire=packet,new=True,
                               basic_ready_ns=time.perf_counter_ns())
                    canonical=self.contents.get(signature)
                    if canonical is not None:
                        job.update(phase='alias',canonical=canonical);self._release(job);completed.append(job);continue
                    self.contents[signature]=job['id'];self.events.append(('basic',job))
                    self.graph.add(('hashes',job['id']),lambda job=job:self._materials(job))
                if job['phase']=='materials':
                    if job.get('enhancement_error'):raise ValueError('Base remains available;enhancement partial: '+job['enhancement_error'])
                    t=self.graph.tasks[('hashes',job['id'])]
                    if t['state']=='failed':raise ValueError(t['error'])
                    if t['state']!='done':continue
                    values,hashes,resources,groups=t['value']
                    for identity,index,_,_ in job['manifest']['groups']:
                        key=('material',job['id'],identity)
                        task=self.graph.tasks.get(key)
                        if task and task['state']=='failed':raise ValueError(task['error'])
                        if task and task['state']=='done' and identity not in job['material_done']:
                            piece=task.pop('value');piece.update(group=identity,ordinary_texture=index,remix_hash=hashes[index].upper().zfill(16),values=list(values))
                            self.events.append(('material',(job,piece)));job['material_done'].add(identity)
                    if len(job['material_done'])==len(job['manifest']['groups']):
                        job.update(phase='ready',enhanced_ready_ns=time.perf_counter_ns());completed.append(job);self.events.append(('complete',job))
            except Exception as e:
                job.update(phase='failed',error=str(e));self.events.append(('failed',job));completed.append(job)
                for key,t in self.graph.tasks.items():
                    if len(key)>1 and key[1]==job['id'] and t['state']=='queued':t.update(state='failed',error='Asset failed',fn=None)
                # In-flight tasks must finish before input references/reservations
                # are released. close() handles failed assets after the pool drains.
        return completed

    def _release(self,job):
        if job['phase']=='alias':
            # Canonical content owns the result. Cancel queued alias consumers
            # before their shared dependency entries can be removed. Running
            # tasks already hold their submitted argument references.
            for key,t in self.graph.tasks.items():
                if len(key)>1 and key[1]==job['id'] and t['state']=='queued':
                    t.update(state='failed',error='Alias uses canonical prepared content',fn=None)
        reservation=job.pop('reservation',None)
        if reservation:reservation.__exit__(None,None,None)
        job.pop('capture',None);job.pop('images',None);job.pop('source_images',None)
        shared_keys=set(job.get('image_keys',{}).values())|set(job.get('read_keys',{}).values())|set(job.get('piece_keys',{}).values())
        for key in shared_keys:
            users=self.image_users.get(key,set());users.discard(job['id'])
            if not users:
                t=self.graph.tasks.get(key)
                if t and t['state']!='running':
                    self.graph.tasks.pop(key);self.image_users.pop(key,None)
        for key,t in list(self.graph.tasks.items()):
            if len(key)>1 and key[1]==job['id'] and t['state'] not in ('running','queued'):self.graph.tasks.pop(key)

    def settled(self,identities):
        return all(self.jobs[i]['phase'] in ('ready','failed','alias') for i in identities)

    def close(self):
        if self.closed:return
        self.closed=True;self.graph.close()
        for job in self.jobs.values():self._release(job)

    def report(self):
        return dict(workers=WORKERS,parallel_parts=True,closed=self.closed,spans=self.spans,
                    jobs_summary=[{k:v for k,v in j.items() if k in ('id','phase','discovered_ns','basic_ready_ns','enhanced_ready_ns','canonical','error','peak_working_image_bytes','base_steps')} for j in self.jobs.values()],
                    unfinished=[j['id'] for j in self.jobs.values() if j['phase'] not in ('ready','failed','alias')])
