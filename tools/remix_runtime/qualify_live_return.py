"""Owned standalone fresh-request integration test. NEVER launches SFC."""
from pathlib import Path
import argparse
import ctypes as C
import datetime as dt
import json
import os
import re
import struct
import subprocess as sp
import time
import shutil
from live_return import FreshReceiver,telemetry,source_hashes,binary_hashes,qualify
from run_return_fixture import ROOT,DLL,ENV,digest
from return_channel import Channel

BIN=ROOT/'artifacts/remix-runtime/live-return-bin'
SOURCE=ROOT/'artifacts/remix-runtime/runs/20261018-025737-262069-in-game'

def projected_display_mask(mask,viewport):
    """Native viewport placement with the display stage's bilinear alpha sampling."""
    import numpy as np
    vx,vy,vw,vh=map(int,viewport)
    if np.ndim(mask)!=2:raise ValueError('Display mask viewport')
    sh,sw=np.shape(mask)
    if not 1<=sw<=1920 or not 1<=sh<=1080 or min(vx,vy)<0 or min(vw,vh)<1 or vx+vw>1920 or vy+vh>1080:raise ValueError('Display mask viewport')
    x=(np.arange(vw)+.5)*sw/vw-.5;y=(np.arange(vh)+.5)*sh/vh-.5
    ix=np.floor(x).astype(int);iy=np.floor(y).astype(int);fx=x-ix;fy=y-iy
    jx=np.clip(ix+1,0,sw-1);jy=np.clip(iy+1,0,sh-1);ix=np.clip(ix,0,sw-1);iy=np.clip(iy,0,sh-1)
    alpha=(1-fy[:,None])*((1-fx)*mask[iy[:,None],ix]+fx*mask[iy[:,None],jx])+fy[:,None]*((1-fx)*mask[jy[:,None],ix]+fx*mask[jy[:,None],jx])
    canvas=np.zeros((1080,1920),dtype=bool);canvas[vy:vy+vh,vx:vx+vw]=alpha>.01
    return canvas

def textured_footprint(predicted,actual):
    """Color-derived silhouettes permit only a narrow native-pixel edge band."""
    import numpy as np
    def expand(mask):
        h,w=mask.shape;padded=np.pad(mask,3);out=np.zeros_like(mask)
        for y in range(7):
            for x in range(7):np.logical_or(out,padded[y:y+h,x:x+w],out=out)
        return out
    p=int(predicted.sum());a=int(actual.sum())
    if not p or not a:return dict(qualified=False)
    unexpected=int((actual&~expand(predicted)).sum());missing=int((predicted&~expand(actual)).sum())
    delta=float(np.linalg.norm(np.argwhere(actual).mean(0)-np.argwhere(predicted).mean(0)))
    return dict(qualified=.9<=a/p<=1.1 and delta<=1 and unexpected+missing<=max(8,int(p*.001)),
        unexpected_beyond3px=unexpected,missing_beyond3px=missing,centroid_error_pixels=delta,area_ratio=a/p)

def main():
    p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');p.add_argument('--addon',action='store_true');p.add_argument('--visible',action='store_true');p.add_argument('--textured',action='store_true');p.add_argument('--slow',action='store_true');p.add_argument('--disconnect',action='store_true');p.add_argument('--qualify',nargs='+',type=Path)
    p.add_argument('--capture-image',action='store_true')
    p.add_argument('--light-wiring',action='store_true')
    p.add_argument('--light-types',action='store_true')
    p.add_argument('--project-fill',action='store_true')
    p.add_argument('--material-controls',action='store_true')
    p.add_argument('--image-controls',action='store_true')
    p.add_argument('--quality-controls',action='store_true')
    p.add_argument('--image-proof',type=Path)
    p.add_argument('--scene-depth',action='store_true')
    # Parse the added optional offline image control alongside existing modes.
    args=p.parse_args()
    if args.scene_depth:args.textured=True;args.addon=True
    if args.light_types:args.light_wiring=True
    if args.project_fill:args.light_wiring=True
    if args.material_controls:args.textured=True;args.addon=True
    if args.image_controls:args.textured=True;args.addon=True
    if args.quality_controls:args.textured=True;args.addon=True
    if args.light_wiring:args.textured=True;args.addon=True
    if args.capture_image and not (args.textured and args.addon):p.error('--capture-image requires --textured --addon')
    if args.textured:args.visible=True
    if args.visible and not args.addon:p.error('--visible requires --addon')
    if args.qualify:print(json.dumps(qualify(args.qualify,args.image_proof),indent=2));return
    if not args.execute:print('Offline fixture only; --execute starts owned SDK/native test processes,not SFC.');return
    if digest(DLL)!='F7C310821AA98BCDFDEC120330B0A89457B7C5EBA58D21464AF32639611C809F':raise ValueError('Pinned runtime mismatch')
    from broad_capture import storage_bytes,OVERALL
    # Explicit disk bounds:128MiB images+32MiB other output+32MiB margin.
    # This is reservation accounting only;capture/output caps are NOT increased.
    reserve=(192 if args.textured else 64)*1024*1024
    if storage_bytes()+reserve>OVERALL or shutil.disk_usage(ROOT).free<reserve:raise ValueError('Evidence/archive allowance or disk space')
    work=ROOT/'artifacts/remix-runtime/runs'/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f-live-private');work.mkdir()
    if args.addon:
        from run_return_fixture import TEST
        if digest(TEST/'dxgi.dll')!='E35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7':raise ValueError('Copied proxy mismatch')
        proxy=TEST/'dxgi.dll'
        if args.scene_depth:
            from broad_capture import qualified_full
            proxy=qualified_full()
        for source,name in ((proxy,'dxgi.dll'),(BIN/'SFCRemixReturn.dll','SFCRemixReturn.dll'),(BIN/'ship_live_gpu_fixture.exe','d3d11_return_fixture.exe')):shutil.copyfile(source,work/name)
        (work/'ReShade.ini').write_text('[GENERAL]\nEffectSearchPaths=./no-effects\nPresetPath=./fixture.ini\n[OVERLAY]\nTutorialProgress=4\nShowFPS=0\nShowFrameTime=0\n[INPUT]\nInputProcessing=0\n')
    original=json.loads((SOURCE/'semantic.analysis.json').read_text())['snapshots'][0]['associations']
    association=next(a for a in original if a['owner']==2);row=association['record']
    (work/'fixture-row.bin').write_bytes(struct.pack('<96I',*row))
    receiver=FreshReceiver(work,textured=args.textured);channel=None;host=fixture=image_reader=None;error=None;streams=[];start=time.monotonic()
    light_relay=None;light_changed=False;types_step=0;types_next=0
    fill_step=0
    material_step=0;material_relay=None
    image_step=0;image_relay=None
    quality_step=0;quality_relay=None
    if args.quality_controls:
        from quality_controls import Relay as QualityRelay
        quality_path=work/'quality-test.toml';quality_path.write_text('[quality]\nenabled=true\nmax_anisotropy=16\n')
        quality_relay=QualityRelay(work,quality_path)
    if args.image_controls:
        from image_controls import Relay as ImageRelay
        image_path=work/'image-test.toml';image_path.write_text('[image]\nenabled=true\ngamma=1.0\n')
        image_relay=ImageRelay(work,image_path)
    if args.material_controls:
        from material_controls import Relay as MaterialRelay
        material_path=work/'materials-test.toml'
        material_path.write_text('[material]\nroughness=0.4\nillumination_strength=0\n')
        material_relay=MaterialRelay(work,material_path)
        material_relay.poll() # Freeze private factory profile BEFORE asset preparation.
    type_sequence=['dome','sphere','rectangle','disk','cylinder','spot','directional']
    if args.light_wiring:
        from live_lights import Relay
        (work/'gate').mkdir();control_path=work/'lights-test.toml'
        # Private deterministic fixture, independent of sponsor's live edits.
        control_path.write_text('schema_version = 1\nbackend = "remix_sdk_0_6_4"\nmaster_multiplier = 0.5\n'
            '[[lights]]\nid = "native_directional_0"\n[[lights]]\nid = "native_directional_1"\n')
        if args.project_fill:control_path.write_text(control_path.read_text()+'[[lights]]\nid = "project_fill"\ntype = "dome"\nenabled = true\nintensity_multiplier = 0.05\n')
        light_relay=Relay(work,receiver,control_path)
        # Fixtures must NEVER follow sponsor's mutable image/material/quality edits.
        from material_controls import Relay as MaterialRelay
        from image_controls import Relay as ImageRelay
        from quality_controls import Relay as QualityRelay
        for name,section in (('material','material'),('image','image'),('quality','quality')):(work/f'{name}-factory.toml').write_text(f'[{section}]\n')
        light_relay.materials=MaterialRelay(work,work/'material-factory.toml')
        light_relay.images=ImageRelay(work,work/'image-factory.toml')
        light_relay.quality=QualityRelay(work,work/'quality-factory.toml')
        # Freeze the private material profile before FreshReceiver prepares its
        # first asset; otherwise it can read the sponsor's tuned default first.
        light_relay.materials.poll()
    if args.textured and not args.material_controls and not args.light_wiring:
        # The other textured fixtures also need a private initial profile. They
        # test delivery/image/quality, not the sponsor's mutable map generation.
        from material_controls import Relay as MaterialRelay
        factory=work/'material-factory.toml';factory.write_text('[material]\n')
        MaterialRelay(work,factory).poll()
    def output(name):f=(work/name).open('wb');streams.append(f);return f
    warned=False
    def check():
        nonlocal warned
        size=sum(f.stat().st_size for f in work.rglob('*') if f.is_file())
        images=sum(f.stat().st_size for f in (work/'textures').glob('*') if f.is_file()) if args.textured else 0
        if images>128*1024*1024:raise RuntimeError('Fixture original/derived image128MiB cap')
        size-=images
        if size>16*1024*1024 and not warned:print('Private fixture16MiB warning;32MiB cap remains.',flush=True);warned=True
        if time.monotonic()-start>60 or size>32*1024*1024:raise RuntimeError('Owned test60s/32MiB cap')
    manifest=dict(probe='REMIX-LIVE-RETURN-001',kind='OFFLINE_PROXY_CALLBACK_NOT_SFC' if args.addon else 'OFFLINE_SYNTHETIC_PUBLISHER_NOT_SFC',source_capture=str(SOURCE.relative_to(ROOT)),
        source_frame=120,limits={'seconds':60,'bytes':32*1024*1024,'image_bytes':128*1024*1024 if args.textured else 0,'bytes_excludes_textures':bool(args.textured)},runtime_sha256=digest(DLL),
        binaries=binary_hashes(),environment=ENV,source_hashes=source_hashes(),capture_image=args.capture_image)
    (work/'manifest.json').write_text(json.dumps(manifest,indent=2))
    try:
        env={**os.environ,**ENV,'SFC_REMIX_CALIBRATION_SCENE':receiver.name,'DXVK_LOG_PATH':str(work)}
        env.pop('SFC_REMIX_TEXTURED_SHIP',None)
        env.pop('SFC_REMIX_LIGHT_WIRING',None)
        env.pop('SFC_REMIX_SCENE_DEPTH',None)
        if args.scene_depth:env['SFC_REMIX_SCENE_DEPTH']='1'
        if args.light_wiring:env['SFC_REMIX_LIGHT_WIRING']='1'
        if args.textured:env['SFC_REMIX_TEXTURED_SHIP']='1'
        if args.slow:env['SFC_PRIVATE_SLOW']='1'
        if args.disconnect:env['SFC_PRIVATE_DISCONNECT']='1'
        if args.visible:env['SFC_REMIX_VISIBLE_SHIP']='1'
        if args.material_controls:env['SFC_PRIVATE_MATERIAL_CACHE']='1'
        env.pop('SFC_REMIX_CAPTURE_SHIP_IMAGE',None);env.pop('SFC_REMIX_CAPTURE_SHIP_IMAGE_DELAY_MS',None)
        if args.capture_image:env.update(SFC_REMIX_CAPTURE_SHIP_IMAGE='1',SFC_REMIX_CAPTURE_SHIP_IMAGE_DELAY_MS='2000')
        host=sp.Popen([str(BIN/'ship_live_host.exe'),str(DLL)],cwd=work,env=env,stdout=output('host.log'),stderr=sp.STDOUT,creationflags=sp.CREATE_NO_WINDOW)
        session=None
        while session is None:
            check();text=(work/'host.log').read_text(errors='replace');m=re.search(r'SESSION (Local\\SFC-Remix-Return-\{[^}]+\})',text)
            if m:session=m[1];break
            if host.poll() is not None:raise RuntimeError('Fresh host initialization failed')
            time.sleep(.05)
        channel=Channel(session)
        if args.addon:
            env.update(SFC_REMIX_RETURN_SESSION=session,SFC_REMIX_EXPECTED_IMAGE=str(work/'d3d11_return_fixture.exe'),SFC_REMIX_PRELOAD_REQUIRED='1',SFC_REMIX_PRIVATE_SHIP='1',SFC_PRIVATE_CALLBACK_FIXTURE='1')
            command=[str(ROOT/'artifacts/remix-runtime/return-bin/return_launcher.exe'),'--fixture',str(work/'d3d11_return_fixture.exe'),str(work/'SFCRemixReturn.dll'),digest(work/'d3d11_return_fixture.exe'),digest(work/'SFCRemixReturn.dll')]
        else:command=[str(BIN/'ship_live_gpu_fixture.exe'),session]
        fixture=sp.Popen(command,cwd=work,env=env,stdout=output('fixture.log'),stderr=sp.STDOUT,creationflags=sp.CREATE_NO_WINDOW)
        pid=None
        while pid is None:
            check();text=(work/'fixture.log').read_text(errors='replace');m=re.search(r'FIXTURE_PID (\d+)',text)
            if m:pid=int(m[1]);break
            if fixture.poll() is not None:raise RuntimeError('Private fixture initialization failed')
            time.sleep(.01)
        receiver.context(session,pid)
        if args.capture_image:image_reader=sp.Popen([str(BIN/'ship_image_reader.exe'),session,str(work)],cwd=work,env=env,stdout=output('ship-image-reader.log'),stderr=sp.STDOUT,creationflags=sp.CREATE_NO_WINDOW)
        # Simulated native worker transfer,using real recorded geometry only as
        # fixture input. Production FreshReceiver has no SOURCE/template fallback.
        packet=(SOURCE/'gate/LIVE-SCENE-001-asset-2.bin').read_bytes();refs=(SOURCE/'gate/LIVE-SCENE-001-asset-2.json').read_bytes()
        address=receiver.channel.view;C.memmove(address+65536,packet+refs,len(packet)+len(refs))
        descriptor=struct.pack('<6I',1,0,len(packet),len(refs),2,2);C.memmove(address+256,descriptor,len(descriptor))
        history=[];disconnected=False;displayed_at_disconnect=None
        while fixture.poll() is None:
            check();receiver.drain();history.append(telemetry(channel.address))
            if quality_relay:
                quality_relay.poll();host_text=(work/'host.log').read_text(errors='replace')
                if quality_step==0 and 'samples=16 bias=0 aa=0 denoise=1' in host_text:
                    quality_path.write_text('[quality]\nenabled=true\ntexture_filtering="trilinear"\nanti_aliasing="temporal"\ndenoising=false\n');quality_step=1
                elif quality_step==1 and 'aa=3 denoise=0' in host_text:
                    quality_path.write_text('[quality]\nsupersampling=2.0\n');quality_step=2
                elif quality_step==2 and quality_relay.rejected:
                    quality_path.write_text('[quality]\n');quality_step=3
            if image_relay:
                image_relay.poll();host_text=(work/'host.log').read_text(errors='replace')
                if image_step==0 and 'gamma=1 saturation=1 grade=host_linear' in host_text:
                    image_path.write_text('[image]\nenabled=true\ngamma=2.0\n');image_step=1
                elif image_step==1 and 'gamma=2 saturation=1 grade=host_linear' in host_text:
                    image_path.write_text('[image]\ngamma=0.0\n');image_step=2
                elif image_step==2 and image_relay.rejected:
                    image_path.write_text('[image]\nenabled=true\ntone_mapping="global"\ncontrast=0.7\nsaturation=0.5\n');image_step=3
                elif image_step==3 and 'saturation=0.5 grade=native_global' in host_text:
                    image_path.write_text('[image]\n');image_step=4
            if material_relay:
                material_relay.poll();host_text=(work/'host.log').read_text(errors='replace')
                if material_step==0 and 'roughness=0.4 illumination=0' in host_text:
                    material_path.write_text('[material]\nroughness=0.7\nillumination_strength=2\nmetallic=0.2\nroughness_map_enabled=true\nroughness_map_strength=0.1\n');material_step=1
                elif 1<=material_step<=4 and material_relay.pending_revision is None and material_relay.accepted==material_step+1:
                    if material_step<4:
                        material_step+=1
                        material_path.write_text(f'[material]\nroughness=0.7\nillumination_strength=2\nmetallic=0.2\nroughness_map_enabled=true\nroughness_map_strength={material_step/10}\n')
                    else:material_path.write_text('[material]\nroughness=99\n');material_step=5
                elif material_step==5 and material_relay.rejected:
                    material_path.write_text('[material]\nroughness=0.5\nillumination_strength=1\n');material_step=6
            if light_relay:
                light_relay.poll()
                if not light_changed and 'NATIVE_LIGHT_APPLIED slot=1' in (work/'host.log').read_text(errors='replace'):
                    control_path.write_text(control_path.read_text().replace('master_multiplier = 0.5','master_multiplier = 0.25'))
                    light_changed=True
                if args.project_fill and light_changed:
                    text=(work/'host.log').read_text(errors='replace')
                    if fill_step==0 and 'slot=1 enabled=1 radiance=0.0625' in text:
                        control_path.write_text(control_path.read_text().replace('enabled = true','enabled = false'));fill_step=1
                    elif fill_step==1 and 'PROJECT_LIGHT_APPLIED slot=2 enabled=0' in text:
                        control_path.write_text(control_path.read_text().replace('enabled = false','enabled = true'));fill_step=2
                if args.light_types and light_changed and time.monotonic()>=types_next:
                    log_text=(work/'host.log').read_text(errors='replace')
                    from light_shapes import TYPES
                    previous_ok=types_step==0 or f'LIGHT_TYPE_APPLIED slot=1 type={TYPES[type_sequence[types_step-1]]}' in log_text
                    if previous_ok and types_step<len(type_sequence):
                        text='schema_version = 1\nbackend = "remix_sdk_0_6_4"\nmaster_multiplier = 0.25\n'
                        text+='[[lights]]\nid = "native_directional_0"\ntype = "directional"\n'
                        text+=f'[[lights]]\nid = "native_directional_1"\ntype = "{type_sequence[types_step]}"\nradius = 0.01\nwidth = 0.02\nheight = 0.02\nlength = 0.02\n'
                        control_path.write_text(text);types_step+=1;types_next=time.monotonic()+.6
            marker=(work/'fixture.log').read_text(errors='replace')
            ready_to_disconnect='TEXTURED_PIXELS_PASS' in marker if args.textured else ('PRIVATE_MASK ' in marker or 'PRIVATE_CALLBACK_ACTIVE ' in marker)
            if args.scene_depth:ready_to_disconnect='SCENE_DEPTH_PHASES_READY' in marker
            if args.disconnect and not disconnected and ready_to_disconnect:
                host.terminate();host.wait(timeout=5);disconnected=True;displayed_at_disconnect=channel.state.drawCount
            if host.poll() is not None:
                # The fixture signals stop before the verified launcher finishes
                # proxy teardown. Accept only its explicit completed-test marker.
                if args.disconnect and disconnected:time.sleep(.02);continue
                if host.returncode==0 and 'PRIVATE_GPU_FIXTURE_PASS' in (work/'fixture.log').read_text(errors='replace'):
                    fixture.wait(timeout=8);break
                raise RuntimeError('Fresh host exited during test')
            time.sleep(.02)
        if fixture.returncode:raise RuntimeError('Native private receiver fixture failed')
        host.wait(timeout=8)
        if host.returncode and not disconnected:raise RuntimeError('Fresh host shutdown failed')
        log=(work/'fixture.log').read_text()
        if quality_relay:
            host_text=(work/'host.log').read_text()
            if quality_step!=3 or ' enabled=0 aniso=1 samples=8' not in host_text or ' filter=1' not in host_text or 'QUALITY_SAMPLER_APPLIED revision=0 filter=0' not in host_text or quality_relay.accepted!=3:raise RuntimeError('Quality reload/rejection/restore incomplete')
        if image_relay:
            host_text=(work/'host.log').read_text()
            if image_step!=4 or ' enabled=0 mode=local' not in host_text or 'image native' in host_text or image_relay.accepted!=4:
                raise RuntimeError('Image hot-reload/rejection/restoration proof incomplete')
        if material_relay:
            host_text=(work/'host.log').read_text()
            if material_step!=6 or material_relay.accepted!=6 or material_relay.pending_revision is not None or not material_relay.reclaimed_bytes or not all(s in host_text for s in ('roughness=0.4 illumination=0 roughness_map=0','roughness=0.7 illumination=2 roughness_map=1','roughness=0.5 illumination=1 roughness_map=0')) or 'MATERIAL_REJECTED' in host_text:
                raise RuntimeError('Material SDK hot-reload/last-good proof incomplete')
            if not receiver.selected['textures']['secondary_applied']:raise RuntimeError('Fixture has no qualified product illumination')
        if light_relay:
            hostlog=(work/'host.log').read_text()
            if not all(s in hostlog for s in ('slot=0 enabled=1 radiance=0.75,0.75,0.75','slot=1 enabled=1 radiance=0.125,0.125,0.125','slot=0 enabled=1 radiance=0.375,0.375,0.375','slot=1 enabled=1 radiance=0.0625,0.0625,0.0625')):
                raise RuntimeError('Native light hot-reload SDK application missing')
            if args.light_types:
                from light_shapes import TYPES
                applied=[int(m[1]) for m in re.finditer(r'LIGHT_TYPE_APPLIED slot=1 type=(\d+)',hostlog)]
                if types_step!=len(type_sequence) or applied[-len(type_sequence):]!=[TYPES[k] for k in type_sequence]:
                    raise RuntimeError('Not all requested Remix light types were exercised')
            if args.project_fill:
                states=[int(m[1]) for m in re.finditer(r'PROJECT_LIGHT_APPLIED slot=2 enabled=(\d+)',hostlog)]
                if states!=[1,0,1] or 'PROJECT_LIGHT_APPLIED slot=2 enabled=1 radiance=0.05,0.05,0.05' not in hostlog:
                    raise RuntimeError('Independent project dome on/off/on not confirmed')
        if args.visible and 'VISIBLE_CAMERA_PIXELS_PASS' not in log:raise RuntimeError('Visible game-camera pixel proof missing')
        if args.textured and ('TEXTURED_PIXELS_PASS' not in log or (not args.disconnect and not args.scene_depth and 'STEADY_DISPLAY_PASS' not in log)):raise RuntimeError('Textured/cadence proof missing')
        if args.scene_depth and 'SCENE_DEPTH_CALLBACK_PASS' not in log:raise RuntimeError('Actual scene-depth callbacks/occlusion/fallback proof missing')
        if 'PRIVATE_GPU_FIXTURE_PASS' not in log or 'retired_draws_stopped=1 disabled_draws_stopped=1' not in log:raise RuntimeError('Private lifecycle proof incomplete')
        if not args.addon and (work/'private-picking.bin').stat().st_size!=256*256*4:raise RuntimeError('Picking output missing')
        # Reuse the independent native projection oracle with the SAME source
        # geometry/camera,including the deliberate world translation.
        from run_coverage_probe import expected_replay
        import numpy as np
        asset=receiver.selected;iou=None;footprint=None
        camera=asset['initial_offset'];oracle={'replay_camera':{'native_composed':camera['original_native_composed'],
            'viewport':list(struct.unpack('<6f',struct.pack('<6I',*row[83:89])))[:4],'depth_reference':'native_z','diagnostic_offset':camera}}
        if args.visible:
            if args.textured:
                predicted=projected_display_mask(np.isfinite(expected_replay(work,oracle,resolution=(1920,1080))),oracle['replay_camera']['viewport'])
            else:predicted=projected_display_mask(np.isfinite(expected_replay(work,oracle)),oracle['replay_camera']['viewport'])
            # Image samples contain the already WORLD-offset ship. Scale the
            # complete camera image to its native viewport,not a fitted inset.
            predicted[:96]=False
            actual=np.fromfile(work/'visible-camera-mask.bin',dtype='u1').reshape(1080,1920)!=0
            iou=float((actual&predicted).sum()/max(1,(actual|predicted).sum()))
            if args.textured:
                footprint=textured_footprint(predicted,actual)
                if not footprint['qualified'] or iou<.98:raise RuntimeError('Textured native-resolution silhouette requires IoU>=0.98 and native edge/centroid/background bounds')
                if 'LIVE_RENDER_RESOLUTION client=1920x1080 swapchain=1920x1080 scale=1.0' not in (work/'host.log').read_text(errors='replace'):
                    raise RuntimeError('Textured actual post-Present resolution was not verified')
            elif iou<.95:raise RuntimeError('Visible ship location/scale/background differs from native camera projection')
        if not args.addon:
            predicted=np.isfinite(expected_replay(work,oracle))
            actual=np.fromfile(work/'private-picking.bin',dtype='<u4').reshape(256,256)==29
            iou=float((actual&predicted).sum()/max(1,(actual|predicted).sum()))
            if iou<.95:raise RuntimeError('Fresh output pose/coverage projection mismatch')
            colors=np.fromfile(work/'private-color.bin',dtype='u1').reshape(256,256,4)
            if not actual.any() or float(np.median(colors[actual,2]))<20 or float(np.median(colors[actual,0]))<20:raise RuntimeError('Diagnostic material invisible')
        final=telemetry(channel.address)
        if args.textured and args.slow and final['late']<1:raise RuntimeError('Expired buffered output was not rejected')
        if args.textured and disconnected and channel.state.drawCount>displayed_at_disconnect+1:raise RuntimeError('Buffered display continued after producer death')
        image_result=None
        if args.capture_image:
            image_reader.wait(timeout=8)
            if image_reader.returncode:raise RuntimeError('Prepared image reader failed')
            from ship_image_snapshot import convert
            image_result=convert(work)
            if image_result['owner_epoch']!=asset['owner_epoch'] or image_result['revision']!=asset['revision'] or image_result['asset_sha256']!=asset['textures']['asset_sha256'] or image_result['nonzero_alpha_pixels']<10:
                raise RuntimeError('Prepared image does not match selected live asset/nonempty layer')
        result=dict(result='OFFLINE_PROXY_PRIVATE_RETURN_PASS' if args.addon else 'OFFLINE_FRESH_PRIVATE_RETURN_PASS',seconds=time.monotonic()-start,source_session=receiver.name,
            selected=asset,telemetry=final,mask_iou=iou,sfc_launched=False,game_callback_qualified=args.addon,source='synthetic current-frame publisher with recorded fixture geometry',
            host_exit=host.returncode,fixture_exit=fixture.returncode,history=history)
        result.update(slow_receiver=args.slow,renderer_disconnect=disconnected,visible_camera_verified=bool(args.visible and not args.textured),textured_delivery_verified=bool(args.textured),textured_footprint=footprint,output_size=[1920,1080] if args.textured else [256,256])
        if light_relay:result.update(light_wiring_verified=True,light_controls=light_relay.summary(),synthetic_native_lights=True)
        if args.light_types:result['light_types_verified']=type_sequence
        if args.project_fill:result['project_fill_verified']=True
        if material_relay:result.update(material_controls_verified=True,material_changes=material_relay.accepted,material_invalid_rejected=material_relay.rejected,material_cache_reclaimed_bytes=material_relay.reclaimed_bytes,material_pending_revision=material_relay.pending_revision)
        if image_relay:result.update(image_controls_verified=True,image_changes=image_relay.accepted,image_invalid_rejected=image_relay.rejected)
        if quality_relay:result.update(quality_controls_verified=True,quality_changes=quality_relay.accepted,quality_invalid_rejected=quality_relay.rejected)
        result.update(prepared_image_verified=bool(image_result),prepared_image=image_result)
        if args.scene_depth:
            from live_return import depth_telemetry
            depth=depth_telemetry(channel.address)
            if not depth['qualified'] or not depth['found'] or depth['failed'] or depth['wrong_thread']:raise RuntimeError('Native scene-depth qualification failed')
            result.update(scene_depth_verified=True,scene_depth=depth,proxy_sha256=digest(work/'dxgi.dll'))
    except Exception as exc:error=str(exc);result=dict(result='PARTIAL',error=error,sfc_launched=False)
    finally:
        if channel:channel.set('stop',1)
        for process in (fixture,host,image_reader):
            if process and process.poll() is None:
                try:process.wait(timeout=8)
                except sp.TimeoutExpired:process.terminate();process.wait(timeout=5)
        if channel:channel.close()
        receiver.close()
        for f in streams:f.close()
        (work/'result.json').write_text(json.dumps(result,indent=2))
    print('Evidence: '+str(work))
    if error:raise RuntimeError(error)

if __name__=='__main__':main()
