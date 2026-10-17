"""Prewarm bounded Kit preview then launch existing neutral SFC runner, or replay.

Replay never launches/injects SFC. All children and output locations are explicit.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import time
from live_bridge import Channel, SIZE, STRIDE, WORDS
from live_camera import multiply

ROOT=Path(__file__).resolve().parents[2]
PWSH=Path('C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe')
JOB=Path('C:/Project/RemixJobs/20261016-050350Z-6dffd5be')
GAME=Path('C:/Games/Taldren Software Inc/Starfleet Command Orion Pirates')


def replay(channel, capture):
    def stamp(r,shift=0):
        view=[[1.,0.,0.,shift],[0.,1.,0.,0.],[0.,0.,1.,-20.],[0.,0.,0.,1.]]
        p=[[2.,0.,.12,0.],[0.,3.2,-.08,0.],[0.,0.,-1.002002,-2.002002],[0.,0.,-1.,0.]]
        s=[[512.,0.,0.,712.],[0.,-320.,0.,320.],[0.,0.,1.,0.],[0.,0.,0.,1.]]
        model=struct.unpack('<16f',struct.pack('<16I',*r[8:24]));model=[list(model[i:i+4]) for i in (0,4,8,12)]
        bits=lambda m:list(struct.unpack('<16I',struct.pack('<16f',*(x for row in m for x in row))))
        r[24]=256;r[25:41]=bits(multiply(multiply(multiply(s,p),view),model));r[41]=0
        r[48]=1;r[49:66]=bits(view)+[256];r[66:83]=bits(p)+[0]
        r[83:89]=struct.unpack('<6I',struct.pack('<6f',200,0,1024,640,512,320))
    packet=(capture/'MESH-EXPORT-001.bin').read_bytes();refs=(capture/'TEXTURE-EXPORT-001.json').read_bytes()
    h=struct.unpack_from('<64I',packet)
    if len(packet)+len(refs)>STRIDE:raise ValueError('Replay asset bound')
    channel.write(4096,packet+refs)
    channel.write(128,struct.pack('<4I',1,len(packet),len(refs),h[4]))
    channel.write(12,struct.pack('<I',1))
    for i in range(90):
        r=[0]*WORDS;r[:7]=[i+1,h[4],i+1,i*34,1,h[10],h[12]];r[45]=0
        values=[1.,0.,0.,i/20,0.,1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.]
        if i>=45:values[:3]=[0.,-1.,0.];values[4:7]=[1.,0.,0.]
        r[8:24]=struct.unpack('<16I',struct.pack('<16f',*values));stamp(r,i*.01)
        channel.write(256,struct.pack('<I',i*2+1));channel.write(260,struct.pack('<96I',*r));channel.write(256,struct.pack('<I',i*2+2))
        time.sleep(.034)
    # Explicit retire then keep connected long enough for stale/disappear observation.
    r[0]+=1;r[4]=2
    channel.write(256,struct.pack('<I',181));channel.write(260,struct.pack('<96I',*r));channel.write(256,struct.pack('<I',182))
    time.sleep(1.2)
    # New display epoch, SAME opaque model/source pointers: no pointer-only reuse.
    copy=bytearray(packet);hh=list(h);hh[4]+=1;hh[3]=0
    struct.pack_into('<64I',copy,0,*hh)
    value=2166136261
    for byte in copy:value=((value^byte)*16777619)&0xffffffff
    hh[3]=value;struct.pack_into('<64I',copy,0,*hh)
    rr=json.loads(refs);rr['owner_epoch']=hh[4];rr['packet_fnv1a']=value
    reference=json.dumps(rr).encode()
    channel.write(4096+STRIDE,bytes(copy)+reference)
    channel.write(160,struct.pack('<4I',1,len(copy),len(reference),hh[4]))
    for i in range(30):
        r[0]+=1;r[1]=hh[4];r[4]=1;r[45]=1;r[2]+=1;r[3]+=34
        stamp(r,i*.01)
        channel.write(256,struct.pack('<I',183+i*2));channel.write(260,struct.pack('<96I',*r));channel.write(256,struct.pack('<I',184+i*2))
        time.sleep(.034)
    channel.write(12,struct.pack('<I',2))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--replay',action='store_true')
    parser.add_argument('--fixed-camera',action='store_true',help='Explicit old fixed-view diagnostic; default follows game camera')
    parser.add_argument('--fresh-scene',action='store_true',help='Protocol3 multi-ship fresh geometry, no prepared ship')
    args=parser.parse_args()
    if args.fresh_scene and args.fixed_camera:parser.error('Fresh scene requires game camera')
    from live_scene import SceneChannel
    start=time.monotonic();channel=SceneChannel(create=True) if args.fresh_scene else Channel(create=True)
    work=ROOT/'artifacts/live-bridge'/channel.name[-32:];work.mkdir(parents=True,exist_ok=False)
    launch=work/'viewer-launch.json';preview=None;game=None;out=None;result={'replay':args.replay,'status':'PARTIAL','channel':channel.name}
    try:
        command=[sys.executable,str(Path(__file__).with_name('run_mesh_preview.py')),'--job',str(JOB),
                 '--textures','--resident-textures','--provisional-lighting','--live-channel',channel.name,
                 '--live-game-root',str(GAME),'--live-launch-record',str(launch)]
        if args.fresh_scene:
            command=[sys.executable,str(Path(__file__).with_name('run_mesh_preview.py')),'--job',str(ROOT/'artifacts/no-template-job'),
                 '--textures','--resident-textures','--fresh-scene','--live-channel',channel.name,
                 '--live-game-root',str(GAME),'--live-launch-record',str(launch)]
        if not args.fixed_camera:command.append('--game-camera')
        if args.fresh_scene and args.replay:command.append('--live-replay')
        (work/'configuration.json').write_text(json.dumps({'command':command,'capture_seconds':90,'total_seconds':300,
            'mapping_bytes':channel.size,'movement_limit_per_owner':2700,'evidence_limit':(32 if args.fresh_scene else 8)*1024*1024,
            'fresh_scene':args.fresh_scene,'replay':args.replay},indent=2))
        out=(work/'viewer-console.log').open('xb');preview=subprocess.Popen(command,stdout=out,stderr=subprocess.STDOUT)
        preview_work=None
        while time.monotonic()-start<180:
            if preview.poll() is not None:raise RuntimeError('Preview exited before readiness; inspect viewer-console.log')
            if (work/'viewer-console.log').stat().st_size>8*1024*1024:raise RuntimeError('Console cap')
            if launch.exists():
                try:preview_work=Path(json.loads(launch.read_text())['work'])
                except json.JSONDecodeError:time.sleep(.05);continue
                ready=preview_work/'preview-ready.json'
                if ready.exists():
                    try:data=json.loads(ready.read_text())
                    except json.JSONDecodeError:time.sleep(.05);continue
                    if data.get('status')!='READY':raise RuntimeError('Preview setup failed')
                    break
            time.sleep(.1)
        else:raise RuntimeError('Viewer startup180s limit')
        result['preview_work']=str(preview_work)
        if args.replay:
            if args.fresh_scene:
                from replay_live_scene import replay_scene
                replay_scene(channel,ROOT/'artifacts/m1/runs/20261016-215022-enabled')
            else:
                capture=Path(json.loads((JOB/'job-metadata.json').read_text())['capture'])
                replay(channel,capture)
        else:
            if time.monotonic()-start>45:raise RuntimeError('Insufficient remaining budget for safely bounded gameplay; game not launched')
            entry='start_live_scene_session.ps1' if args.fresh_scene else 'start_live_bridge_session.ps1'
            command=[str(PWSH),'-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'tools/m1_component'/entry),
                     '-Prepared','-LiveChannel',channel.name]
            # Inherit console for sponsor instructions/exit cues; do not conceal gameplay requests.
            game=subprocess.Popen(command)
            while game.poll() is None and time.monotonic()-start<295:
                if (work/'viewer-console.log').stat().st_size>8*1024*1024:raise RuntimeError('Console cap')
                time.sleep(.2)
            if game.poll() is None:raise RuntimeError('Workflow deadline: game runner safely parked, do not kill game/controller with live hooks')
            result['game_runner_exit']=game.returncode
            if game.returncode:raise RuntimeError('Game runner failed; preserve cleanup evidence before retry')
        channel.write(12,struct.pack('<I',2))
        preview.wait(timeout=max(1,300-(time.monotonic()-start)))
        result['preview_exit']=preview.returncode
        report=preview_work/'live-viewer-result.json'
        if report.exists():result['viewer']=json.loads(report.read_text())
        if preview.returncode or result.get('viewer',{}).get('accepted',0)==0:raise RuntimeError('No validated live updates; review evidence')
        if not args.fixed_camera and (result.get('viewer',{}).get('camera_updates',0)==0 or result['viewer'].get('camera_rejected')):
            raise RuntimeError('Camera alignment rejected/missing; preserve evidence, no fixed-camera fallback')
        if args.fresh_scene and (result['viewer'].get('owners',0)<2 or result['viewer'].get('asset_failures') or
            result['viewer'].get('template_loaded') is not False or not result['viewer'].get('geometry_readback_verified')):
            raise RuntimeError('Fresh multi-ship asset proof incomplete; inspect owner/asset/readback results')
        if args.fresh_scene:
            console=(preview_work/'job-console.log').read_text(errors='replace')
            if 'Unsupported image file format' in console or 'Failed to load texture' in console:
                raise RuntimeError('Renderer rejected live textures; mesh/material authoring alone is not image-display proof')
            originals={}
            for path in preview_work.glob('live-asset-*-verification.json'):
                manifest=json.loads(path.read_text())
                for group in manifest['assignments']:
                    for role in ('primary','secondary'):
                        image=group.get(role)
                        if image:originals[image['filename']]=image['sha256']
            for name,digest in originals.items():
                path=(GAME/name).resolve()
                if not path.is_relative_to(GAME.resolve()) or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
                    raise RuntimeError('Original texture changed during fresh-asset proof')
            result['fresh_source_images_unchanged']=True
            if not args.replay:
                matches=[]
                for path in sorted((ROOT/'artifacts/m1/runs').glob('*/run-metadata.json'),key=lambda x:x.stat().st_mtime,reverse=True)[:10]:
                    if json.loads(path.read_text(encoding='utf-8-sig')).get('live_channel')==channel.name:matches.append(path.parent)
                if len(matches)!=1:raise RuntimeError('Fresh native run provenance missing/ambiguous')
                native=matches[0];worker=json.loads((native/'LIVE-SCENE-001-worker.json').read_text())
                outcome=json.loads((native/'run-result.json').read_text(encoding='utf-8-sig'))
                summary=json.loads((native/'M1-A-summary.json').read_text())
                result.update(native_run=str(native),native_worker=worker,native_exit=outcome)
                if (worker['io_failed'] or worker['capture_failures'] or worker['owner_overflow'] or worker['unsent_assets'] or
                    not outcome['client_unchanged'] or not outcome['normal_exit_observed'] or not summary['hooks_restored']):
                    raise RuntimeError('Fresh native capture/cleanup incomplete; preserve partial evidence')
                for path in preview_work.glob('live-asset-*-verification.json'):
                    manifest=json.loads(path.read_text());packet=native/f"LIVE-SCENE-001-asset-{manifest['revision']}.bin"
                    if hashlib.sha256(packet.read_bytes()).hexdigest()!=manifest['packet_sha256']:
                        raise RuntimeError('Viewer geometry differs from fresh native packet')
        result['status']='REPLAY_PASSED_RUNTIME_UNPROVEN' if args.replay else 'CAPTURE_COMPLETE_REQUIRES_ADJUDICATION'
    except (OSError,RuntimeError,ValueError,subprocess.TimeoutExpired) as exc:
        result['error']=str(exc)
    finally:
        channel.write(12,struct.pack('<I',3 if result['status']=='PARTIAL' else 2))
        if preview is not None and preview.poll() is None:
            try:preview.wait(timeout=3)
            except subprocess.TimeoutExpired:
                # Parent runner's Windows job owns/limits Kit; do not orphan it by killing its controller.
                result['preview_guard_pending']=True
        if game is not None and game.poll() is None:result['game_cleanup_pending']=True
        channel.close()
        if out:out.close()
        result['elapsed_seconds']=time.monotonic()-start
        (work/'result.json').write_text(json.dumps(result,indent=2)+'\n')
        print('Live bridge evidence:',work);print(json.dumps(result,indent=2))
    return 1 if result['status']=='PARTIAL' else 0


if __name__=='__main__':raise SystemExit(main())
