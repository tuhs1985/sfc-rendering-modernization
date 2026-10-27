"""Run196 standalone fast KFF/FCA material-notice diagnosis,never SFC.

Uses the just-completed live capture, synthetic fixture camera, actual consumer.
The optional notification is a hypothesis,not a production readiness signal.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import struct
import sys
import time

ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'tools/remix_runtime'),str(ROOT/'tools/d3d9_proof'),str(ROOT/'tools/scene_bridge')]
SOURCE=ROOT/'artifacts/remix-runtime/runs/20261026-022855-157867-in-game/gate'


def run(notice,ready_first=False,cached_materials=False,synchronous=False,private_prewarm=False,zero_emission=False,idle_seconds=0):
    import async_material_checkout as checkout
    import multi_scene_fixture as scene
    import run_return_fixture as fixture
    from live_scene import decode_mesh
    if private_prewarm:
        original_init=checkout.Relay.__init__
        def init(self,*args,**kwargs):
            original_init(self,*args,**kwargs)
            if zero_emission:
                import re
                self.material_config=re.sub(rb"(?m)^illumination_strength\s*=.*$",b"illumination_strength = 0.0",self.material_config)
                from material_controls import encode
                self.preparer.values=struct.unpack("<2I10fQ",encode(self.material_config))[2:12]
        checkout.Relay.__init__=init
        original_configuration=checkout.configure_child
        def prepared(backend,env):
            text,report=original_configuration(backend,env)
            env["SFC_D3D9_RENDER_PREWARM"]="triangle"
            report["diagnostic_private_prewarm"]=True
            return text+"rtx.enableReplacementAssets = True\n",report
        checkout.configure_child=prepared
    if synchronous:
        original_configure=checkout.configure_child
        def configure(backend,env):
            text,report=original_configure(backend,env)
            env['DXVK_ASYNC_ASSET_LOADING']='0';report['diagnostic_synchronous']=True
            return text+'rtx.initializer.asyncAssetLoading = False\n',report
        checkout.configure_child=configure
    if cached_materials:
        # Timing fault injection only: compute identical derivative bytes before
        # the replay so their early publication can overlap initial USD loading.
        # This is NOT a new production cache or a CPU performance measurement.
        import parallel_assets as parts
        from material_controls import encode
        values=struct.unpack('<2I10fQ',encode((ROOT/'tools/remix_runtime/config/materials.toml').read_bytes()))[2:12]
        images={};pieces={};original_piece=parts.material_piece
        for i in (1,2):
            source=SOURCE/f'LIVE-SCENE-001-asset-{i}.bin'
            mesh=decode_mesh(source.read_bytes(),source.with_suffix('.json').read_bytes())
            resources={r['id']:r for r in mesh['refs']['resources']}
            for g in mesh['groups']:
                names=[resources[g['primary']]['filename']]
                if g['flags']&0x20:names.append(resources[g['secondary']]['filename'])
                for name in names:
                    if name not in images:images[name]=parts.load_image(fixture.TEST,name)
                a=images[names[0]];b=images[names[1]] if len(names)>1 else None
                key=(a['sha256'],b['sha256'] if b else None,tuple(values))
                if key not in pieces:pieces[key]=original_piece(a,b,values)
        assert sum(len(data) for piece in pieces.values() for data,_ in piece['encoded'].values())<=256*1024*1024
        images.clear()
        def material_piece(a,b,v):
            return copy.deepcopy(pieces[(a['sha256'],b['sha256'] if b else None,tuple(v))])
        parts.material_piece=material_piece
    original_rows=scene.rows_and_packets
    def rows(work,session,extended=False):
        assert not extended
        generated=original_rows(work,session,False);proof=[]
        for i in range(2):
            source=SOURCE/f'LIVE-SCENE-001-asset-{i+1}.bin'
            mesh=decode_mesh(source.read_bytes(),source.with_suffix('.json').read_bytes())
            row=generated[i];row[1],row[5],row[6],row[7]=mesh['header'][4],mesh['header'][10],mesh['header'][12],i+1
            for extension in ('bin','json'):
                shutil.copyfile(source.with_suffix('.'+extension),work/'gate'/f'LIVE-SCENE-001-asset-{i+1}.{extension}')
            proof.append(dict(path=str(source.relative_to(ROOT)),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),model=mesh['refs']['model_filename']))
        assert generated[0][1]!=generated[1][1]
        (work/'fixture-rows.bin').write_bytes(b''.join(struct.pack('<96I',*r) for r in generated))
        (work/'fast-source-provenance.json').write_text(json.dumps(dict(synthetic_poses=True,source=proof),indent=2))
        return generated
    scene.rows_and_packets=rows
    if ready_first:
        original_current=checkout.Relay.current_rows
        def current(self):
            # Reproduce gameplay's already-prepared renderer before tactical
            # discovery. Device readiness does NOT acknowledge material loading.
            if not (self.folder/'gpu/renderer-ready.bin').is_file():return []
            if not hasattr(self,'diagnostic_idle_start'):self.diagnostic_idle_start=time.monotonic()
            if time.monotonic()-self.diagnostic_idle_start<idle_seconds:return []
            return original_current(self)
        checkout.Relay.current_rows=current
    original_flush=checkout.Relay.flush_enhancements;events=[]
    original_commit=checkout.Relay.commit_layers
    def commit(self,initial):
        original_commit(self,initial)
        if notice!='post-publish':return
        master=self.folder/'gpu/rtx-remix/mods/sfc-policy/mod.usda'
        before=hashlib.sha256(master.read_bytes()).hexdigest();master.touch()
        assert hashlib.sha256(master.read_bytes()).hexdigest()==before
        events.append(dict(at_ns=time.perf_counter_ns(),sha256=before,meaning='Explicit last-write notification immediately after finalized atomic publication;no timer/frame wait'))
    checkout.Relay.commit_layers=commit
    def flush(self):
        original_flush(self)
        if notice in ('none','post-publish') or events or not self.material_events:return
        if any(j['phase'] not in ('ready','alias') for j in self.preparer.jobs.values()):return
        if self.pending_enhancements or self.pending_stage_ids or self.pending_library:return
        # Read already-existing current-session additive counters,not runtime
        # internals. A returned frame is NOT assumed to acknowledge USD loading.
        pool=self.receiver.channel.read(11*1024*1024+128*1024,576)
        drawn=struct.unpack_from('<I',pool,512)[0]
        threshold=1 if notice=='first-return' else 120
        if drawn<threshold:return
        master=self.folder/'gpu/rtx-remix/mods/sfc-policy/mod.usda'
        before=hashlib.sha256(master.read_bytes()).hexdigest();master.touch()
        assert hashlib.sha256(master.read_bytes()).hexdigest()==before
        events.append(dict(at_ns=time.perf_counter_ns(),drawn=drawn,sha256=before,
                           meaning='One metadata-only notification;not GPU/material ACK or a proposed120-frame delay'))
    checkout.Relay.flush_enhancements=flush
    before=set((ROOT/'artifacts/remix-runtime/runs').iterdir())
    sys.argv=['run_return_fixture.py','--async-material-checkout','--multi-ship','--prewarm','--startup-profile','--pipeline-mode','performance']
    try:fixture.main()
    finally:
        for p in set((ROOT/'artifacts/remix-runtime/runs').iterdir())-before:
            effective=[]
            if zero_emission:
                for material in (p/'gpu/assets').glob('*/material-binding.json'):
                    effective.append(json.loads(material.read_text())['values'][1])
                if effective and any(effective):raise ValueError('Diagnostic zero emission did not reach generated material values')
            record=dict(effective_emission_values=effective,diagnostic_only=True,notice=notice,ready_first=ready_first,cached_materials=cached_materials,synchronous=synchronous,private_prewarm=private_prewarm,zero_emission=zero_emission,idle_seconds=idle_seconds,events=events,probe_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),production_qualification_eligible=False,scope='Live KFF/FCA geometry in synthetic standalone camera;early publication/notification diagnosis only')
            (p/'early-material-notice-probe.json').write_text(json.dumps(record,indent=2))
            if (p/'result.json').is_file():
                r=json.loads((p/'result.json').read_text());r['early_material_notice_probe']=record;r['production_qualification_eligible']=False
                r['diagnostic_original_reference_locks']=r.pop('multi_ship_build_locks',None)
                (p/'result.json').write_text(json.dumps(r,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--notice',choices=('none','first-return','120-returns','post-publish'),default='none')
    p.add_argument('--ready-first',action='store_true');p.add_argument('--cached-materials',action='store_true');p.add_argument('--synchronous',action='store_true');p.add_argument('--private-prewarm',action='store_true');p.add_argument('--zero-emission',action='store_true');p.add_argument('--idle-seconds',type=int,choices=(0,30),default=0);args=p.parse_args()
    run(args.notice,args.ready_first,args.cached_materials,args.synchronous,args.private_prewarm,args.zero_emission,args.idle_seconds)
