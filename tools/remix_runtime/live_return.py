"""Fresh asset worker/provenance and bounded return telemetry; never a game callback."""
from pathlib import Path
import ctypes as C
import hashlib
import json
import struct
import sys
import numpy as np
from run_coverage_probe import prepare_mesh,diagnostic_offset,ROOT,digest
from present_calibration import Receiver
from live_camera import camera_state
from analyze_live_camera import native_matrix,inverse
import math

def fnv(raw):
    h=14695981039346656037
    for b in raw:h=((h^b)*1099511628211)&0xffffffffffffffff
    return h

LIVE_SOURCES=('remix_texture_coordinates.h','ship_image_snapshot.h','ship_image_reader.cpp','ship_image_snapshot.py','ship_live_request.h','ship_live_camera.h','ship_live_receiver.h','ship_live_host.cpp',
    'ship_live_gpu_fixture.cpp','ship_triplet_wire.h','ship_triplet_consumer.h','ship_triplet_compositor.h',
    'return_addon.cpp','build_live_return.ps1','run_return_game.py','start_return_image_session.ps1',
    'live_return.py','qualify_live_return.py','run_coverage_probe.py','textured_asset.py','ship_textured_asset.h','../m1_component/m1_present_calibration.h')
QUALIFICATION=ROOT/'artifacts/remix-runtime/deps/live-return-qualification.json'
def source_hashes():return {n:digest(Path(__file__).parent/n) for n in LIVE_SOURCES}
def binary_hashes():
    folder=ROOT/'artifacts/remix-runtime/live-return-bin'
    return {n:digest(folder/n) for n in ('ship_live_host.exe','ship_live_gpu_fixture.exe','SFCRemixReturn.dll','ship_image_reader.exe')}
def require_qualification(visible=False,textured=False,capture_image=False):
    q=json.loads(QUALIFICATION.read_text())
    if q.get('result')!='OFFLINE_PRIVATE_RETURN_QUALIFIED' or q.get('source_hashes')!=source_hashes() or q.get('binaries')!=binary_hashes():raise ValueError('Private return offline qualification stale/missing')
    if visible and not q.get('visible_camera_qualified'):raise ValueError('Visible ship camera/pixel qualification missing')
    if textured and not q.get('textured_delivery_qualified'):raise ValueError('Textured full-resolution/buffered qualification missing')
    if capture_image and not q.get('prepared_image_qualified'):raise ValueError('Prepared ship image qualification missing')
    return q
def qualify(folders):
    hashes=source_hashes();binaries=binary_hashes();seen=set();evidence=[];image_qualified=False
    for folder in folders:
        folder=Path(folder).resolve()
        if folder.parent!=(ROOT/'artifacts/remix-runtime/runs').resolve():raise ValueError('Exact private fixture required')
        r=json.loads((folder/'result.json').read_text());m=json.loads((folder/'manifest.json').read_text())
        if r.get('result') not in ('OFFLINE_FRESH_PRIVATE_RETURN_PASS','OFFLINE_PROXY_PRIVATE_RETURN_PASS') or m.get('source_hashes')!=hashes or m.get('binaries')!=binaries:raise ValueError('Fixture evidence/source mismatch')
        if r.get('sfc_launched') or r.get('fixture_exit') or r['telemetry']['failed']:raise ValueError('Fixture failed/unsafe')
        if r.get('prepared_image_verified'):image_qualified=True
        if r.get('textured_delivery_verified'):seen.add('textured_disconnect' if r.get('renderer_disconnect') else ('textured_slow' if r.get('slow_receiver') else 'textured'))
        elif r.get('visible_camera_verified') and r.get('mask_iou',0)>=.95:seen.add('visible')
        elif r.get('renderer_disconnect'):seen.add('disconnect')
        elif r.get('slow_receiver'):
            if 'SLOW_LEASE_NO_OVERWRITE' not in (folder/'fixture.log').read_text():raise ValueError('No slow ownership proof')
            seen.add('slow')
        elif r.get('game_callback_qualified'):seen.add('callback')
        elif r.get('mask_iou',0)>=.95:seen.add('direct')
        evidence.append(str(folder.relative_to(ROOT)))
    if not {'direct','callback','slow','disconnect'}.issubset(seen) or seen-{'direct','callback','slow','disconnect','visible','textured','textured_slow','textured_disconnect'}:raise ValueError('Four distinct private gates required')
    QUALIFICATION.write_text(json.dumps(dict(result='OFFLINE_PRIVATE_RETURN_QUALIFIED',source_hashes=hashes,binaries=binaries,evidence=evidence,visible_camera_qualified='visible' in seen,textured_delivery_qualified={'textured','textured_slow','textured_disconnect'}.issubset(seen),prepared_image_qualified=image_qualified),indent=2))
    return require_qualification()

class FreshReceiver(Receiver):
    def __init__(self,folder,textured=False):
        super().__init__();self.folder=Path(folder);self.assets={};self.selected=None;self.pid=None;self.session=None;self.attempted=set();self.textured=textured
    def context(self,session,pid):self.session=session;self.pid=pid
    def drain(self):
        from live_scene import decode_mesh
        for slot in range(4):
            transfer=self.channel.asset_transfer(slot)
            if transfer is None:continue
            generation,revision,owner,packet,refs=transfer
            if not 1<=revision<=8:raise ValueError('Fresh return eight-revision bound')
            mesh=decode_mesh(packet,refs);h=mesh['header']
            if h[4]!=owner:raise ValueError('Fresh return asset owner')
            digest=hashlib.sha256(packet+refs).hexdigest()
            if revision in self.revisions and self.revisions[revision]!=digest:raise ValueError('Reused fresh revision')
            self.revisions[revision]=digest
            asset=self.folder/'assets';asset.mkdir(exist_ok=True)
            path=asset/f'asset-{revision}.bin';path.write_bytes(packet);path.with_suffix('.json').write_bytes(refs)
            self.assets[revision]=(path,mesh);self.channel.acknowledge(slot,generation)
        if self.selected or not self.pid or not self.session:return
        for index in range(32):
            row=self.channel.sample_owner(index)
            if row is None or row[4]!=1 or row[7] not in self.assets or row[7] in self.attempted:continue
            source,mesh=self.assets[row[7]];h=mesh['header']
            if (h[4],h[10],h[12])!=(row[1],row[5],row[6]) or h[6]>row[2]:raise ValueError('Fresh source association mismatch')
            try:
                state=camera_state(row,[0,0,0],mesh['used_points']);v=inverse(native_matrix(row[49:66]));p=native_matrix(row[66:83])
                points=np.array(mesh['used_points']);projected=np.c_[points,np.ones(len(points))]@np.array(state['native_composed']).T
                if np.any(projected[:,3]<=0):raise ValueError('Selected owner clips near camera')
                xy=projected[:,:2]/projected[:,3,None]
                span=np.ptp(xy,axis=0)*256/np.array(state['viewport'][2:])
                if min(span)<8:raise ValueError('Selected owner too small for diagnostic return')
                near=p[2][3]/p[2][2];far=p[2][3]/(p[2][2]+1)
                params=[v[i][3] for i in range(3)]+[v[i][0] for i in range(3)]+[v[i][1] for i in range(3)]+[-v[i][2] for i in range(3)]+[math.degrees(2*math.atan(1/p[1][1])),p[1][1]/p[0][0],near,far]
                camera=dict(native_model=state['native_model'],native_composed=state['native_composed'],viewport=state['viewport'],sdk_parameters=params)
                manifest=prepare_mesh(source,self.folder/'coverage-mesh.bin')
                offset=diagnostic_offset(camera,self.folder)
            except ValueError as exc:
                # A too-small/clipped first owner must not block a different one.
                self.attempted.add(row[7]);(self.folder/f'unsupported-{row[7]}.json').write_text(json.dumps({'reason':str(exc),'owner':row[1],'revision':row[7]}));continue
            native=(self.folder/'coverage-mesh.bin').read_bytes();(self.folder/'live-mesh.bin').write_bytes(native)
            texture=None
            if self.textured:
                from textured_asset import prepare
                texture=prepare(source.read_bytes(),source.with_suffix('.json').read_bytes(),self.folder,ROOT.parent/'SFC-Remix-Return-Test')
            source_session=self.channel.name[-32:]
            key=struct.pack('<8I2Q8I32s6II3f',0,0,0,0,row[1],row[7],row[2],29,
                fnv(struct.pack('<17I',*row[8:25])),fnv(struct.pack('<40I',*row[49:89])),
                *( (1920,1080) if self.textured else (256,256)),*map(int,state['viewport']),1,1,bytes.fromhex(texture['asset_sha256'] if texture else hashlib.sha256(source.read_bytes()).hexdigest()),
                *(int(source_session[i:i+8],16) for i in range(0,32,8)),self.pid,0,2 if self.textured else 1,*offset['world_translation'])
            seed=key+struct.pack('<4IQ',row[5],row[6],row[46],0,fnv(native))
            if len(seed)!=176:raise ValueError('Fresh seed ABI')
            self.selected=dict(owner_epoch=row[1],revision=row[7],source_pid=self.pid,scene_session=self.channel.name,
                model_name=mesh['refs']['model_filename'],packet_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                references_sha256=hashlib.sha256(source.with_suffix('.json').read_bytes()).hexdigest(),
                native_mesh_sha256=hashlib.sha256(native).hexdigest(),seed_sha256=hashlib.sha256(seed).hexdigest(),
                mesh=manifest,initial_offset=offset,material='Original primary images,surface color only;whole-hull emission off;provisional white directional inspection light;secondary roles unresolved' if self.textured else 'SDK opaque emissive magenta diagnostic,not recovered appearance',textures=texture,saved_template_used=False)
            (self.folder/'fresh-asset.json').write_text(json.dumps(self.selected,indent=2))
            pending=self.folder/'live-asset.pending';pending.write_bytes(seed);pending.replace(self.folder/'live-asset.seed')
            break

def telemetry(address):
    # Independently atomic counters only. Not a coherent row/frame capture.
    def i(offset):return C.c_int32.from_address(address+offset).value
    return dict(lease=i(512+112),sequence=i(512+116),ack=i(512+120),
                offered=i(1024+560),invalid=i(1024+564),acquired=i(1024+568),drawn=i(1024+572),
                late=i(1024+576),failed=i(1024+580),rendered=i(1024+584),cancelled=i(1024+588))
