"""Isolated Run193 upstream hot-reload qualification; never launches SFC.

Use the verified 1.6.1 host/header/runtime and Run191 completed-stage publication.
Supply ONE explicit loading option to the owning native child, not globally.
"""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import re
import sys
import time

ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(Path(__file__).parent),str(ROOT/'tools/remix_runtime'),str(ROOT/'tools/d3d9_proof')]
HERE=ROOT/'artifacts/candidate-hot-reload'


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def alias_release(original,self,job):
    # Diagnostic correction: an alias no longer needs its queued per-group
    # consumers. Cancel them before releasing their shared dependencies.
    # Running consumers already own their submitted argument references.
    if job['phase']=='alias':
        for key,task in self.graph.tasks.items():
            if len(key)>1 and key[1]==job['id'] and task['state']=='queued':
                task.update(state='failed',error='Alias uses canonical prepared content',fn=None)
    return original(self,job)


def self_test():
    from parallel_assets import Tasks,Pipeline
    def fixture():
        p=object.__new__(Pipeline);p.graph=Tasks(1);key=('derived','fixture')
        p.graph.tasks[key]=dict(state='done',value={'image':True},deps=(),fn=None,priority=3)
        p.graph.add(('material',4,0),lambda value:value,(key,))
        p.image_users={key:{4}}
        job=dict(id=4,phase='alias',piece_keys={0:key})
        return p,job
    p,job=fixture()
    try:
        Pipeline._release(p,job)
        try:p.graph.pump()
        except KeyError:pass
        else:raise AssertionError('Original missing-dependency race not reproduced')
    finally:p.graph.close()
    p,job=fixture()
    try:
        alias_release(Pipeline._release,p,job);p.graph.pump()
        assert not p.graph.tasks and not p.image_users
    finally:p.graph.close()
    p,job=fixture()
    try:
        p.graph.pump() # Consumer now owns its submitted image argument.
        alias_release(Pipeline._release,p,job)
        until=time.monotonic()+2
        while p.graph.tasks[('material',4,0)]['state']=='running':
            assert time.monotonic()<until;p.graph.pump();time.sleep(.001)
        assert p.graph.tasks[('material',4,0)]['value']=={'image':True}
    finally:p.graph.close()
    print('Alias lifetime self-check PASS: original reproduced,queued consumers cancelled,running arguments retained')


def handoff_source():
    source=(ROOT/'tools/d3d9_proof/d3d9_direct_host.cpp').read_text()
    needle='apiok(external.dxvk_RegisterD3D9Device(device.Get()),"register ordinary device for output only");registered=true;'
    assert source.count(needle)==1
    return source.replace(needle,needle+'\n  apiok(external.SetConfigVariable("rtx.initializer.asyncAssetLoading","True"),"diagnostic asynchronous reload handoff");\n  std::cout<<"CANDIDATE_ASYNC_HANDOFF initial_config_sync=1 after_device=1 api_success=1\\n";')


def run(mode,emission_off=False,retouch_final=False,disable_preserve=False,complete_before_device=False,late_emission_off=False,flat_library=False,late_asset=False):
    import live_owner_timing as live
    import runtime_candidate
    from run_offline import storage,AGGREGATE_BYTES
    HERE.mkdir(exist_ok=True)
    extras=sum(p.stat().st_size for name in ('resource-stall','staging-integration','present-stall','material-transaction','candidate-hot-reload') for p in (ROOT/'artifacts'/name).rglob('*') if p.is_file())
    assert storage()+extras+1024**3<AGGREGATE_BYTES,'Existing1GiB fixture reservation required'
    candidate=runtime_candidate.verify(require_host=True)
    frozen={str(p.relative_to(ROOT)):sha(p) for p in (live.EXE,live.RUNTIME,ROOT/'tools/remix_runtime/progressive_scene_relay.py',ROOT/'tools/d3d9_proof/d3d9_direct_host.cpp')}
    original_exe,original_runtime=live.EXE,live.RUNTIME
    live.EXE=candidate['exe'];live.RUNTIME=candidate['runtime']
    if mode=='handoff':
        assert (HERE/'handoff_host.cpp').read_text()==handoff_source()
        live.EXE=HERE/'handoff_host.exe'
        assert live.EXE.is_file() and live.EXE.stat().st_mtime_ns>=(HERE/'handoff_host.cpp').stat().st_mtime_ns
    actual_exe=live.EXE
    import progressive_scene_relay as progressive
    import run_return_fixture as fixture
    transaction=importlib.import_module('20261025_material_transaction_probe')
    retouches=[];late_edits=[]
    def flush(self):
        if flat_library:
            assert self.offline_fixture
            self.material_library='flat'
        transaction.transaction_flush(self)
        if late_emission_off and self.process and not late_edits:
            log=self.folder/'fixture.log'
            if log.is_file() and 'SHIP_SNAPSHOT once=1 late=0' in log.read_text(errors='replace'):
                edits=[]
                for path in sorted((self.folder/'gpu/assets').glob('*/rtx-remix/mods/sfc-policy/mod.usda')):
                    text=path.read_text();changed,count=re.subn(r'float inputs:emissive_intensity = [^\n]+','float inputs:emissive_intensity = 0',text)
                    assert count and changed!=text
                    pending=path.with_suffix('.pending');pending.write_text(changed);pending.replace(path)
                    edits.append(dict(path=str(path.relative_to(self.folder)),count=count,before_sha256=hashlib.sha256(text.encode()).hexdigest(),after_sha256=sha(path)))
                assert len(edits)==3
                (self.folder/'gpu/rtx-remix/mods/sfc-policy/mod.usda').touch()
                late_edits.append(dict(at_ns=time.perf_counter_ns(),edits=edits,scope='Existing material emission changed after first closed snapshot;no geometry/image changes'))
        if not retouch_final or retouches or not self.material_events:return
        if self.pending_enhancements or self.pending_stage_ids or self.pending_library:return
        if any(j['phase'] not in ('ready','alias') for j in self.preparer.jobs.values()):return
        # Diagnostic notification only; no wait before base/normal stage output.
        # Test an update lost during async loading, not a proposed2s workaround.
        if time.perf_counter_ns()-self.material_events[-1]['supervisor_monotonic_ns']<2_000_000_000:return
        path=self.folder/'gpu/rtx-remix/mods/sfc-policy/mod.usda'
        before=sha(path);assert path.is_file();path.touch()
        assert sha(path)==before
        retouches.append(dict(at_ns=time.perf_counter_ns(),sha256=before,scope='One metadata-only final-master notification2s after completed publications;diagnosis,not a readiness/fix claim'))
    progressive.Relay.flush_enhancements=flush
    if complete_before_device:
        # Diagnosis only: distinguish initial asynchronous material loading from
        # later rebuilds. This intentionally postpones device startup, never a
        # proposed performance policy or all-owner barrier for gameplay.
        progressive.Relay.start_on_launch=lambda self,pid:None
        original_launch=live.Relay.launch
        def launch(self,*args,**kwargs):
            self.flush_enhancements()
            if not self.preparer.jobs or any(j['phase'] not in ('ready','alias') for j in self.preparer.jobs.values()):return
            if self.pending_enhancements or self.pending_stage_ids or self.pending_library:return
            return original_launch(self,*args,**kwargs)
        live.Relay.launch=launch
    from parallel_assets import Pipeline
    original_release=Pipeline._release
    Pipeline._release=lambda self,job:alias_release(original_release,self,job)
    if emission_off:
        import material_binding
        original_shader=material_binding.shader
        def shader(name,images,values):
            override=list(values);override[1]=0.0
            return original_shader(name,images,override)
        material_binding.shader=shader
    before=set((ROOT/'artifacts/remix-runtime/runs').iterdir())
    original_popen=subprocess.Popen;launches=[]

    def popen(command,*args,**kwargs):
        if isinstance(command,list) and len(command)>5 and command[5]==str(actual_exe):
            assert not launches and Path(command[0]).name=='bounded_job.exe','One owned renderer only'
            gpu=Path(command[1]).resolve();gpu.relative_to((ROOT/'artifacts/remix-runtime/runs').resolve())
            assert gpu.name=='gpu' and kwargs['env']['SFC_D3D9_MULTISCENE']=='1'
            env=dict(kwargs['env'])
            if mode=='handoff':env.pop('DXVK_ASYNC_ASSET_LOADING',None)
            else:env['DXVK_ASYNC_ASSET_LOADING']='1' if mode=='async' else '0'
            config=Path(env['DXVK_CONFIG_FILE']).resolve();assert config==gpu/'rtx.conf'
            with config.open('a') as stream:stream.write('\nrtx.initializer.asyncAssetLoading = '+('True' if mode=='async' else 'False')+'\n')
            if disable_preserve:
                with config.open('a') as stream:stream.write('rtx.enablePreservePath = False\n')
            if late_emission_off:
                with config.open('a') as stream:stream.write('rtx.usd.watchDependencies = True\n')
            kwargs['env']=env
            receipt=dict(mode=mode,option='rtx.initializer.asyncAssetLoading',value=mode=='async',
                environment=dict(DXVK_ASYNC_ASSET_LOADING=env.get('DXVK_ASYNC_ASSET_LOADING')),
                supplied_qpc_ns=time.perf_counter_ns(),runtime=str(candidate['runtime']),runtime_sha256=sha(candidate['runtime']),
                host_sha256=sha(actual_exe),header_sha256=candidate['manifest']['header_sha256'],
                api_handoff_after_device=mode=='handoff',
                enable_preserve_path=False if disable_preserve else 'inherited',
                release_source_commit=candidate['manifest']['source_commit'],source_parity='Packaged5a7eec84banner vs public0a6cd5b remains a qualification caveat',
                scope='This exact owned native child only;outer loading-inputs inherit receipt precedes this diagnostic override')
            launches.append(receipt)
            (gpu/'candidate-hot-reload-input.json').write_text(json.dumps(receipt,indent=2))
        return original_popen(command,*args,**kwargs)

    subprocess.Popen=popen
    sys.argv=['run_return_fixture.py','--multi-ship','--multi-ship-resources','--prewarm','--startup-profile',
              '--pipeline-mode','performance','--parallel-assets','--asset-admission-service','on','--texture-upload','initial-data']
    if late_asset:sys.argv.append('--multi-ship-late-asset')
    try:fixture.main()
    finally:
        subprocess.Popen=original_popen
        assert all(sha(ROOT/p)==h for p,h in frozen.items()),'Production inputs changed'
        folders=set((ROOT/'artifacts/remix-runtime/runs').iterdir())-before
        receipt=dict(diagnostic_only=True,production_qualification_eligible=False,mode=mode,launches=launches,
                     diagnostic_emission_override=0.0 if emission_off else None,
                     diagnostic_final_retouch=retouch_final,retouches=retouches,
                     diagnostic_disable_preserve=disable_preserve,
                     diagnostic_complete_before_device=complete_before_device,
                     diagnostic_late_emission_off=late_emission_off,late_edits=late_edits,
                     diagnostic_flat_library=flat_library,
                     diagnostic_late_asset=late_asset,
                     diagnostic_alias_lifetime_correction=True,
                     emission_scope='Only generated USD emissive_intensity;accepted config and all images remain unchanged',
                     unchanged_production=frozen,probe_sha256=sha(__file__),transaction_probe_sha256=sha(transaction.__file__),
                     folders=[str(p) for p in folders],scope='Verified isolated1.6.1ordinaryD3D9;complete material stages;explicit loading input;not gameplay/default promotion')
        for folder in folders:
            path=folder/'result.json'
            if path.is_file():
                data=json.loads(path.read_text());data['diagnostic_original_reference_locks']=data.pop('multi_ship_build_locks',None)
                data['production_qualification_eligible']=False;data['candidate_hot_reload_probe']=receipt
                path.write_text(json.dumps(data,indent=2))
            (folder/'candidate-hot-reload-probe.json').write_text(json.dumps(receipt,indent=2))
        (HERE/(mode+'-'+str(time.perf_counter_ns())+'.json')).write_text(json.dumps(receipt,indent=2))
        live.EXE,live.RUNTIME=original_exe,original_runtime


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=('async','sync','handoff'),default='async')
    parser.add_argument('--emission-off',action='store_true')
    parser.add_argument('--self-test',action='store_true')
    parser.add_argument('--retouch-final',action='store_true')
    parser.add_argument('--prepare-handoff-host',action='store_true')
    parser.add_argument('--disable-preserve',action='store_true')
    parser.add_argument('--complete-before-device',action='store_true')
    parser.add_argument('--late-emission-off',action='store_true')
    parser.add_argument('--flat-library',action='store_true')
    parser.add_argument('--late-asset',action='store_true')
    args=parser.parse_args()
    if args.self_test:self_test()
    elif args.prepare_handoff_host:
        HERE.mkdir(exist_ok=True);(HERE/'handoff_host.cpp').write_text(handoff_source())
    else:
        if args.late_emission_off and (not args.complete_before_device or args.emission_off):parser.error('Late edit requires complete-before-device and full initial materials')
        run(args.mode,args.emission_off,args.retouch_final,args.disable_preserve,args.complete_before_device,args.late_emission_off,args.flat_library,args.late_asset)
