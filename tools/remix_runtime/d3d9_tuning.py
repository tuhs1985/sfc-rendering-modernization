"""Live controls for the existing async D3D9 path; never called inside SFC."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib,json,os,struct,time
from rendering_config import DEFAULT,scoped
from material_controls import encode
from image_controls import Relay as Images
from quality_controls import Relay as Quality


def build_materials(root,jobs,raw,output):
    from parallel_assets import load_image,material_piece
    from material_binding import shader
    values=struct.unpack('<2I10fQ',encode(raw))[2:12]
    if values[3]<0:raise ValueError('Negative normal USD anisotropy unsupported')
    from run_offline import storage,AGGREGATE_BYTES
    available=max(0,AGGREGATE_BYTES-storage());blocks={};definitions={};written=0
    for job in jobs:
        refs=json.loads((Path(job['packet']).with_suffix('.json')).read_text())
        resources={r['id']:r for r in refs['resources']};groups={g['group']:g for g in refs['groups']}
        cache={};cache_bytes=0;asset_bytes=0;asset_names=set()
        def image(filename):
            nonlocal cache_bytes
            if filename not in cache:
                item=load_image(root,filename);size=len(item['raw'])+len(item['bgra'])*2
                if size>256*1024*1024:raise ValueError('Tuning image working-set cap')
                if cache_bytes+size>256*1024*1024:cache.clear();cache_bytes=0
                cache[filename]=item;cache_bytes+=size
            return cache[filename]
        for piece in job['pieces']:
            previous=piece.get('values')
            if previous and job.get('base') and ((not values[4] and not previous[4]) or (values[0]==previous[0] and tuple(values[4:])==tuple(previous[4:]))):
                # Emission strength/metallic/anisotropy are shader constants.
                # Reuse the already prepared images;do not read/hash/re-encode
                # the game's textures just to change a scalar.
                canonical=shader(piece['remix_hash'],piece['images'],values);block=canonical
                for name in piece['images'].values():
                    relative=os.path.relpath(Path(job['base'])/name,output.parent).replace('\\','/')
                    block=block.replace('@'+name+'@','@'+relative+'@')
                key=piece['remix_hash']
                if key in definitions and definitions[key]!=canonical:raise ValueError('Conflicting live material association')
                if key not in blocks:blocks[key]=block;definitions[key]=canonical
                continue
            g=groups[piece['group']];primary=image(resources[g['primary']]['filename'])
            second=image(resources[g['secondary']]['filename']) if g.get('flags',0)&0x20 and g.get('secondary') in resources else None
            p=material_piece(primary,second,values)
            if (p['primary_sha256'],p['secondary_sha256'])!=(piece['primary_sha256'],piece['secondary_sha256']):raise ValueError('Captured source images changed during tuning')
            for name,(data,_) in p['encoded'].items():
                if name not in asset_names:asset_bytes+=len(data);asset_names.add(name)
                if asset_bytes>128*1024*1024:raise ValueError('Tuning per-asset image cap')
                target=output/name;target.parent.mkdir(parents=True,exist_ok=True)
                if not target.exists():
                    # Keep immutable resources alive until renderer exit; no
                    # unsupported assumption of a per-material retirement ACK.
                    if written+len(data)>available:raise ValueError('Tuning aggregate image budget;last good retained')
                    pending=target.with_suffix('.pending');pending.write_bytes(data);pending.replace(target);written+=len(data)
            canonical=shader(piece['remix_hash'],p['images'],values);block=canonical
            for name in p['images'].values():block=block.replace('@'+name+'@','@tuning/'+name+'@')
            key=piece['remix_hash']
            if key in definitions and definitions[key]!=canonical:raise ValueError('Conflicting live material association')
            if key not in blocks:blocks[key]=block;definitions[key]=canonical
    return blocks,written


class Controls:
    def __init__(self,relay,config=DEFAULT):
        self.relay=relay;self.gpu=relay.folder/'gpu';self.gpu.mkdir(exist_ok=True)
        self.config=Path(config);self.images=Images(self.gpu,self.config);self.quality=Quality(self.gpu,self.config)
        self.pool=ThreadPoolExecutor(max_workers=1,thread_name_prefix='sfc-material-tuning')
        self.future=None;self.pending_key=None;self.accepted_key=None;self.rejected_key=None;self.last=0;self.messages=0;self.accepted=0;self.rejected=0;self.bytes=0
    def poll(self):
        if time.monotonic()-self.last<.5:return
        self.last=time.monotonic();self.images.poll();self.quality.poll()
        if self.future and self.future.done():
            try:
                blocks,written=self.future.result();old=getattr(self.relay,'tuning_overrides',{})
                self.relay.tuning_overrides=blocks
                try:self.relay.commit_layers(initial=False)
                except Exception:self.relay.tuning_overrides=old;raise
                self.accepted_key=self.pending_key;self.accepted+=1;self.bytes+=written
                (self.gpu/'tuning-material-config-accepted.toml').write_bytes(self.pending_raw)
                self.report('D3D9 MATERIAL CONFIG_ACCEPTED revision='+str(self.accepted))
            except (OSError,ValueError) as exc:self.rejected_key=self.pending_key;self.rejected+=1;self.report('D3D9 MATERIAL CONFIG_REJECTED last_good=1 '+str(exc))
            self.future=None
        if self.future or self.accepted>=256:return
        try:
            raw=scoped(self.config.read_bytes(),'material');encode(raw)
            jobs=[]
            for job in self.relay.preparer.jobs.values():
                pieces=self.relay.material_pieces.get(job['id'],{})
                if job.get('phase')!='ready' or not pieces or job['id'] in self.relay.pending_complete_ids:continue
                scene=json.loads((job['gpu']/'scene.json').read_text())
                from live_owner_timing import ROOT
                jobs.append(dict(id=job['id'],packet=str(ROOT/scene['source_packet']),base=str(job['gpu']/'rtx-remix/mods/sfc-policy'),pieces=list(pieces.values())))
            if not jobs:return
            key=(hashlib.sha256(raw).hexdigest(),tuple((j['id'],len(j['pieces'])) for j in jobs))
            if key in (self.accepted_key,self.rejected_key):return
            # Initial assets already use the captured launch profile. Do not
            # regenerate them merely because live controls have been attached.
            if raw==self.relay.material_config and not getattr(self.relay,'tuning_overrides',None):
                self.accepted_key=key;return
            self.pending_raw=raw;self.pending_key=key
            target=self.gpu/'rtx-remix/mods/sfc-policy/tuning'
            self.future=self.pool.submit(build_materials,self.relay.root,jobs,raw,target)
        except (OSError,ValueError) as exc:self.rejected+=1;self.report('D3D9 MATERIAL CONFIG_REJECTED last_good=1 '+str(exc))
    def report(self,text):
        if self.messages<100:print(text,flush=True);self.messages+=1
    def close(self):
        self.pool.shutdown(wait=True,cancel_futures=True)
        (self.gpu/'tuning-controls-summary.json').write_text(json.dumps(dict(accepted=self.accepted,rejected=self.rejected,generated_bytes=self.bytes,image_revisions=self.images.accepted,quality_revisions=self.quality.accepted),indent=2))
