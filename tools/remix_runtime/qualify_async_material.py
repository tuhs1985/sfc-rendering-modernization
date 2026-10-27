"""Separate opt-in checkout gate; never writes the normal qualification receipt."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from additive_qualification import ROOT,digest,delivery_window
from async_material_checkout import backend_inputs,receipt
from qualify_multiship import locks

RECEIPT=ROOT/'artifacts/d3d9-proof/async-material/qualification.json'
REFERENCE=ROOT/'artifacts/staging-integration/20261025-220919-119346-return-fixture-archive.json'


def validate_revisions(events):
    if not events:raise ValueError('No material revision evidence')
    last=None
    for event in events:
        revision=event.get('usd_revision') or {}
        before=revision.get('previous_mtime_ns');after=revision.get('published_mtime_ns')
        if (revision.get('policy')!='remix-openusd-windows-second-revision-v1'
                or not isinstance(before,int) or not isinstance(after,int)
                or after//1_000_000_000<=before//1_000_000_000
                or (last is not None and before!=last)):
            raise ValueError('Material revisions collide at Windows OpenUSD timestamp precision')
        last=after


def match_assets(reference,actual):
    index={}
    for path,model,geometry in actual:
        key=(model,geometry)
        if key in index:raise ValueError('Ambiguous reference asset match')
        index[key]=path
    mapping={}
    for path,model,geometry in reference:
        if (model,geometry) not in index:raise ValueError('Accepted captured model missing')
        mapping[path]=index[(model,geometry)]
    if len(mapping)!=len(reference) or len(set(mapping.values()))!=len(reference):
        raise ValueError('Captured asset matching is not one-to-one')
    return mapping


def policy(result):
    if (result.get('async_material_checkout') is not True or not result.get('runtime_candidate')
            or result.get('material_library')!='flat' or not result.get('prewarm')
            or result.get('pipeline_mode')!='performance' or not result.get('multi_ship_resources_fixture')):
        raise ValueError('Explicit async/flat/prewarmed resource checkout required')
    for key in ('error','fixture_exit','host_exit','api_texture_prefetch','diagnostic_skip_initial_material_library','diagnostic_skip_late_material_reload'):
        if result.get(key):raise ValueError('Incomplete or diagnostic-only checkout: '+key)
    if result.get('candidate_hot_reload_probe') or result.get('production_qualification_eligible') is False:
        raise ValueError('Monkeypatched diagnostic cannot qualify integrated checkout')
    if (result.get('loading_policy')!='inherit' or result.get('material_texture_loading')!='preload'
            or result.get('render_prewarm')!='off' or result.get('native_log_level')!='inherit'):
        raise ValueError('Unqualified additional rendering policy')


def delivery(raw):
    fmt=struct.Struct('<8I5Q')
    if len(raw)<64 or (len(raw)-64)%fmt.size:raise ValueError('Sync receipt record layout')
    rows=[fmt.unpack_from(raw,i) for i in range(64,len(raw),fmt.size)]
    first=next((i for i,r in enumerate(rows) if r[3]==1),None)
    if first is None:raise ValueError('No matched returned output')
    count=peak=current=0
    for row in rows[first:]:
        if row[3]==2:count+=1;current+=1;peak=max(peak,current)
        else:current=0
    if peak>2:raise ValueError('Long returned-image interruption after first match')
    return dict(post_start_omissions=count,max_consecutive_omissions=peak,records=len(rows))


def reference_adaptation(archive,records,asset):
    """Derive expected Remix base uploads/names from immutable accepted bytes."""
    from remix_coordinates import bgra
    from mesh_checksum import texture_identity
    converted={};names={}
    prefix='/gpu/assets/'+asset+'/'
    for key in records:
        if prefix not in key:continue
        tail=key.split(prefix,1)[1]
        if not(tail.startswith('texture-') and tail.endswith('.bin')):continue
        raw=archive.read(key);magic,w,h,size=struct.unpack_from('<4I',raw)
        if magic!=0x31544653 or size!=len(raw)-16:raise ValueError('Reference texture layout')
        pixels=bgra(raw[16:],w,h);converted[tail]=raw[:16]+pixels
        old=f'{texture_identity(raw[16:],w,h):016X}'
        new=f'{texture_identity(pixels,w,h):016X}'
        names['mat_'+old]='mat_'+new
    return converted,names


def coherent_fixture_frame(old,new,rows):
    """Shared geometry may be first prepared by either declared fixture owner.

    Accept only an exact declared model/view/projection/viewport, not arbitrary
    frame bytes. All geometry/UV/group bytes still match the accepted capture.
    """
    from scene_bundle import FRAME,flatten
    from analyze_live_camera import native_matrix
    if len(rows)!=4*384 or len(new)!=len(old):return False
    _,_,nv,ni,ng,nf,*_=struct.unpack_from('<8I',old)
    frame=32+nv*32+ni*4+ng*16
    if nf!=1 or old[:frame]!=new[:frame] or len(new)!=frame+FRAME.size:return False
    owner,revision,sequence,active=struct.unpack_from('<4I',new,frame)
    for at in range(0,len(rows),384):
        r=struct.unpack_from('<96I',rows,at)
        if (owner,revision,active)!=(r[1],r[7],1) or not r[2]<=sequence<=r[2]+10000:continue
        viewport=struct.unpack('<6f',struct.pack('<6I',*r[83:89]))[:4]
        wanted=FRAME.pack(owner,revision,sequence,active,
            *flatten(native_matrix(r[8:25])),*flatten(native_matrix(r[49:66])),
            *flatten(native_matrix(r[66:83])),*viewport)
        if new[frame:]==wanted:return True
    return False


def content(folder,material_config=None):
    import zipfile
    reference=json.loads(REFERENCE.read_text())
    expected={k.split('/gpu/',1)[1]:v['sha256'] for k,v in reference['files'].items()
              if '/assets/' in k and (k.endswith(('.dds','/mod.usda','/scene.bin')) or '/texture-' in k)}
    exceptions=[];actual=[]
    for path in (folder/'gpu/assets').glob('*/scene.json'):
        data=json.loads(path.read_text());actual.append((path.parent.name,data['model_name'],data['geometry_sha256']))
    with zipfile.ZipFile(ROOT/reference['archive']) as archive:
        captured=[]
        for key in reference['files']:
            if key.endswith('/scene.json'):
                old=json.loads(archive.read(key))
                captured.append((key.split('/assets/',1)[1].split('/',1)[0],old['model_name'],old['geometry_sha256']))
        mapping=match_assets(captured,actual)
        if len(mapping)!=3:raise ValueError('Captured fixture inventory changed')
        adaptations={identity:reference_adaptation(archive,reference['files'],identity) for identity in mapping}
        for name,want in expected.items():
            _,identity,tail=name.split('/',2)
            path=folder/'gpu/assets'/mapping[identity]/tail
            if not path.is_file():raise ValueError('Missing finalized asset: '+name)
            old=archive.read(next(k for k in reference['files'] if k.endswith('/gpu/'+name)))
            converted,names=adaptations[identity]
            if tail in converted:
                old=converted[tail];exceptions.append(name+': Remix-only base row-origin conversion')
            elif tail.endswith('/mod.usda'):
                text=old.decode()
                # One simultaneous rename; a hash permutation must not cascade.
                import re
                text=re.sub(r'mat_[0-9A-F]{16}',lambda m:names.get(m[0],m[0]),text)
                if material_config is not None:
                    from material_controls import encode
                    values=struct.unpack('<2I10fQ',encode(material_config))[2:12]
                    for field,value in [('reflection_roughness_constant',values[0]),('emissive_intensity',values[1]),('metallic_constant',values[2]),('anisotropy',values[3])]:
                        text=re.sub(r'(float inputs:'+field+r' = )[^\r\n]+',lambda m:m[1]+format(value,'.9g'),text)
                    exceptions.append(name+': explicit sponsor-baseline native material constants;images still exact')
                old=text.encode()
            new=path.read_bytes()
            if new!=old:
                if tail!='scene.bin':raise ValueError('Accepted fixture content differs beyond Remix conversion: '+name)
                if not coherent_fixture_frame(old,new,(folder/'fixture-rows.bin').read_bytes()):
                    raise ValueError('Geometry/transform differs from accepted geometry and declared fixture owners')
                exceptions.append(name+': exact declared shared-owner fixture pose/frame;geometry unchanged')
    if len(expected)!=381:raise ValueError('Accepted reference inventory changed')
    return dict(files=len(expected),exceptions=exceptions,reference_to_received_paths=mapping)


def inspect(folder,backend,material_config=None):
    folder=Path(folder).resolve();folder.relative_to(ROOT/'artifacts/remix-runtime/runs')
    result=json.loads((folder/'result.json').read_text());policy(result)
    if result.get('multi_ship_build_locks')!=locks() or result['runtime_candidate']!=receipt(backend):
        raise ValueError('Checkout source/binary/config/backend receipt stale')
    live=result.get('live_owner_timing') or {};multi=live.get('multi_scene') or {};state=multi.get('state') or {}
    if live.get('result')!='MULTISHIP_OVERLAY_REVIEW_REQUIRED' or not live.get('normal_owned_exit'):
        raise ValueError('Returned scene or owned shutdown incomplete')
    selected=multi.get('async_material_checkout') or {}
    if selected.get('backend')!=receipt(backend) or selected.get('material_library')!='flat' or not selected.get('complete_asset_stages'):
        raise ValueError('Integrated checkout relay not exercised')
    primed=selected.get('material_priming') or {}
    publications=multi.get('material_events') or []
    validate_revisions(publications)
    if (not primed.get('qpc') or primed.get('qpc')!=multi.get('prewarm_ready_qpc')
            or primed.get('host_pid')!=multi.get('prewarm_host_pid') or not publications):
        raise ValueError('Initial material priming/host readiness not exercised')
    assets=multi.get('assets') or [];draws=multi.get('draws') or []
    if (len(assets)!=4 or len({a['signature'] for a in assets})!=3 or len({a['path_id'] for a in assets})!=3
            or any(a.get('acknowledgement')!=1 for a in assets) or len(draws)!=4 or min(d['draws'] for d in draws)<100):
        raise ValueError('Distinct and shared fresh assets/owners not demonstrated')
    if multi.get('partial') or any(state.get(k,1) for k in ('invalid','asset_rejected')) or state.get('asset_ready')!=4:
        raise ValueError('Asset qualification or identity failure')
    prep=multi.get('preparation') or {}
    if prep.get('workers')!=4 or not prep.get('closed') or prep.get('unfinished'):
        raise ValueError('Preparation workers not drained')
    if not multi.get('native_initial_texture_data') or not multi.get('native_admission_service'):
        raise ValueError('Qualified upload/admission path not active')
    for key in ('lookup_header','lookup_packet','lookup_identity'):
        if multi.get('delivery_stages',{}).get(key,1):raise ValueError('Frame correspondence failed')
    output=live.get('game_output') or {};sync=output.get('synchronized_buffer') or {}
    if any(output.get(k,1) for k in ('invalid','error','resource_failed','overwritten')) or not output.get('drawn'):
        raise ValueError('Returned image/state failed')
    if sync.get('paired',0)<540 or sync.get('failed',1) or sync.get('dropped',1):raise ValueError('Paired-frame checks failed')
    log=(folder/'fixture.log').read_text();native=(folder/'gpu/job-console.log').read_text()
    import re
    completed=re.search(r'STARTUP_PROFILE stage=render_warm_complete index=0 qpc=(\d+) frequency=(\d+)',native)
    marker='RENDER_PREWARM mode=triangle frames=56 private_primitives=1 published=0 gpu_complete=1 state_restored=1'
    if (native.count(marker)!=1 or not completed or int(completed[1])>primed['qpc']
            or min(e['supervisor_monotonic_ns'] for e in publications)*int(completed[2])<primed['qpc']*1_000_000_000):
        raise ValueError('Private priming must finish once before enhancement publication')
    for marker in ('native_HUD_and_scene_exact=1','state_errors=0 resized=1 recreated=1','GAME_IMAGE_PIXELS'):
        if marker not in log:raise ValueError('Missing native pixel/state check: '+marker)
    for marker in ('rtx.initializer.asyncAssetLoading = True','OUTPUT_API_SHUTDOWN 0','sdk_mesh_calls=0'):
        if marker not in native:raise ValueError('Missing runtime check: '+marker)
    job=json.loads((folder/'gpu/job-result.json').read_text())
    if job['exit_code'] or job['stop_reason'] or job['remaining_owned_processes']:raise ValueError('Owned renderer cleanup failed')
    loading=json.loads((folder/'gpu/loading-inputs.json').read_text())['async_material_checkout']
    if loading['supplied_async_asset_loading']!='1' or loading['host_sha256']!=backend['host_sha256']:
        raise ValueError('Actual candidate loading input missing')
    if loading.get('initial_material_priming') is not True or loading.get('private_render_prewarm')!='triangle':
        raise ValueError('Actual priming configuration missing')
    frames,rendered=delivery_window(log)
    result=dict(folder=str(folder.relative_to(ROOT)),result_sha256=digest(folder/'result.json'),
        late_asset=bool(result['multi_ship_late_asset_fixture']),content=content(folder,material_config),
        delivery=delivery((folder/'D3D9-SYNC-BUFFER-001.bin').read_bytes()),steady_frames=frames,steady_draws=rendered)
    return result


def baseline(path):
    if path is None:return None,None
    path=Path(path).resolve();path.relative_to(ROOT/'docs/reconnaissance/evidence/baselines')
    manifest=json.loads((path/'manifest.json').read_text());raw=(path/'rendering.toml').read_bytes()
    sha=hashlib.sha256(raw).hexdigest()
    if manifest['files']['tools/remix_runtime/config/rendering.toml']['sha256']!=sha:raise ValueError('Sponsor baseline snapshot changed')
    return raw,dict(path=str(path.relative_to(ROOT)),sha256=sha)


def qualify(initial,late,appearance_baseline=None):
    from qualify_multiship import require_qualification as normal
    normal()  # Keep the unchanged runtime's path usable and independently gated.
    config,approved=baseline(appearance_baseline)
    backend=backend_inputs();proofs=[inspect(p,backend,config) for p in (initial,late)]
    if [p['late_asset'] for p in proofs]!=[False,True]:raise ValueError('Initial and late-asset controls required')
    RECEIPT.parent.mkdir(exist_ok=True)
    RECEIPT.write_text(json.dumps(dict(result='ASYNC_MATERIAL_CHECKOUT_PREPARED_NOT_SFC_PASS',
        locks=locks(),backend=receipt(backend),evidence=proofs,appearance_baseline=approved,
        limitations=['Separate opt-in runtime','No sub2s startup claim','Original ships remain visible',
                     'Packaged/source parity caveat retained','Actual gameplay checkout pending']),indent=2))
    require_qualification();print('Async material checkout offline preparation PASS;not SFC PASS')


def require_qualification():
    from qualify_multiship import require_qualification as normal
    normal();backend=backend_inputs();q=json.loads(RECEIPT.read_text())
    if q.get('result')!='ASYNC_MATERIAL_CHECKOUT_PREPARED_NOT_SFC_PASS' or q.get('locks')!=locks() or q.get('backend')!=receipt(backend):
        raise ValueError('Async material checkout qualification stale/missing;no game launch')
    for proof in q['evidence']:
        if digest(ROOT/proof['folder']/'result.json')!=proof['result_sha256']:raise ValueError('Checkout evidence changed')
    # This entire result is also persisted by the gameplay launcher. Keep path
    # objects inside backend verification, not in the public qualification data.
    return {**q,'backend_inputs':receipt(backend)}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--initial',required=True);p.add_argument('--late',required=True)
    p.add_argument('--appearance-baseline',type=Path)
    args=p.parse_args();qualify(args.initial,args.late,args.appearance_baseline)
