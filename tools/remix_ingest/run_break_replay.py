"""Bounded standalone Remix rendering of the freshly captured debris replay."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import struct
import ctypes
import uuid

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/remix_runtime'),str(ROOT/'tools/d3d9_proof'),
              str(ROOT/'tools/scene_bridge')]
from runtime_candidate import verify
from live_owner_timing import CONFIG
from material_binding import prepare as bind
from scene_bundle import read_replay,FRAME
from run_offline import storage,AGGREGATE_BYTES
from image_controls import encode as encode_image
from quality_controls import encode as encode_quality
from live_lights import packet as light_packet


def inspect_output(root,sample):
    """Check actual returned pixels, not just successful API/output receipts."""
    import numpy as np
    color=(root/f'returned-{sample}-0.raw32').read_bytes()
    depth=(root/f'returned-{sample}-1.raw32').read_bytes()
    w,h=struct.unpack_from('<2I',color)
    if not 1<=w<=1920 or not 1<=h<=1080 or len(color)!=8+w*h*4:
        raise ValueError('Returned colour extent/length')
    if depth[:8]!=color[:8] or len(depth)!=len(color):raise ValueError('Returned depth extent/length')
    rgb=np.frombuffer(color[8:],dtype=np.uint8).reshape(h,w,4)[:,:,:3]
    z=np.frombuffer(depth[8:],dtype='<f4').reshape(h,w)
    covered=np.isfinite(z)&(z>=0)&(z<=1)
    changed=np.any(rgb!=rgb[0,0],axis=2)
    return dict(sample=sample,hull_pixels=int(covered.sum()),
                shaded_hull_pixels=int((covered&changed).sum()),
                varied_colour=bool(changed.any()))


def execute(folder,*,legacy_startup_warmup=False,piece_index=None,snapshots=1,base_materials=False,capture=False,synchronous_shaders=False):
    folder=Path(folder).resolve();folder.relative_to(ROOT/'artifacts')
    receipt=json.loads((folder/'break-replay.json').read_text())
    if receipt['result']!='CAPTURED_BREAK_PIECES_PREPARED_FOR_D3D9':
        raise ValueError('Qualified preparation receipt missing')
    if storage()+256*1024*1024>AGGREGATE_BYTES:
        raise ValueError('Debris replay lacks256MiB evidence reservation')
    backend=verify()
    # Build the existing host into this diagnostic's directory. Keep the
    # gameplay executable and its qualification receipt independent.
    binary=folder/'bin'
    build=subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass',
                          '-File',str(Path(__file__).with_name('build_break_replay.ps1')),
                          '-OutputDirectory',str(binary)],timeout=90,
                         creationflags=subprocess.CREATE_NO_WINDOW,capture_output=True,text=True)
    (folder/'host-build.log').write_text(build.stdout+build.stderr)
    if build.returncode:raise ValueError('Standalone debris host build failed')
    host=binary/'d3d9_direct_host.exe'
    guard=ROOT/'artifacts/remix-ingest/bin/bounded_job.exe'
    results=[]
    for piece in receipt['pieces']:
        if piece_index is not None and piece['index']!=piece_index:continue
        root=(ROOT/piece['folder']).resolve();root.relative_to(folder)
        if (root/'job-result.json').exists():raise ValueError('Replay output already exists')
        manifest=json.loads((root/'scene.json').read_text())
        replay=read_replay(root/'scene.bin');count=len(replay['frames'])
        if not 1<=snapshots<=min(2,count):raise ValueError('Replay snapshot bound')
        payload=bytearray((root/'scene.bin').read_bytes())
        if snapshots<count:del payload[len(payload)-(count-snapshots)*FRAME.size:]
        struct.pack_into('<I',payload,20,snapshots)
        (root/'scene.bin').write_bytes(payload)
        if not base_materials:
            bind(root,Path(r'C:\Project\SFC-Remix-Return-Test'),
                 config=(ROOT/'tools/remix_runtime/config/rendering.toml').read_bytes(),
                 evidence_mode='performance')
        profile=(ROOT/'tools/remix_runtime/config/rendering.toml').read_bytes()
        (root/'image-controls.bin').write_bytes(encode_image(profile))
        (root/'quality-controls.bin').write_bytes(encode_quality(profile))
        (root/'rtx.conf').write_text(CONFIG.replace('rtx.enableReplacementAssets = False',
            'rtx.enableReplacementAssets = '+('False' if base_materials else 'True'))+
            '\nrtx.enableReplacementMaterials = '+('False' if base_materials else 'True')+
            '\nrtx.enableReplacementMeshes = False\n')
        if synchronous_shaders:
            with (root/'rtx.conf').open('a') as stream:
                stream.write('rtx.shader.enableAsyncCompilation = False\n')
        # Explicit offline illumination fixture, not inferred SFC lighting.
        # Use the existing light packet/consumer, with this replay's identity.
        session_hex=uuid.UUID(receipt['source_session'].split('{')[1].rstrip('}')).hex
        session=[int(session_hex[i:i+8],16) for i in range(0,32,8)]
        source=ROOT/manifest['source_packet']
        header=struct.unpack_from('<24I',source.read_bytes())
        state=__import__('scene_bundle').read_replay(root/'scene.bin')['frames'][0]
        identity=dict(session_words=session,owner_epoch=state[0],
            model_process_local=header[10],source_process_local=header[12],frame=state[2],
            slots=[dict(native_type=0,values=dict(direction_input=direction,
                   type_dependent_scalar=1.,contribution_channels=[1.,1.,1.]))
                   for direction in ([0.,0.,-1.],[0.,0.,1.])])
        controls={f'native_directional_{i}':dict(enabled=True,intensity_multiplier=1.,
            color_multiplier=[1.,1.,1.],volumetric_multiplier=1.) for i in range(2)}
        observed=ctypes.c_longlong()
        if not ctypes.windll.kernel32.QueryPerformanceCounter(ctypes.byref(observed)):
            raise OSError('Offline light clock unavailable')
        (root/'live-lights.bin').write_bytes(light_packet(identity,identity,session,controls,
            1.,1.,1,observed.value,1,persistent_scene=True))
        (root/'light-fixture-identity.bin').write_bytes(struct.pack('<6I',*session,
            header[10],header[12]))
        env={key:value for key,value in os.environ.items()
             if not key.startswith(('SFC_','RTX_','DXVK_'))}
        env.update(DXVK_CONFIG_FILE=str(root/'rtx.conf'),
                   RTX_AUTOMATION_DISABLE_BLOCKING_DIALOG_BOXES='1',
                   RTX_CAPTURE_REMIX_CONFIGS='0',DXVK_ENABLE_RAYTRACING='1',
                   DXVK_GRAPHICS_PRESET_TYPE='4',RTX_INTEGRATE_INDIRECT_MODE='0',
                   DXVK_DLSS_PRESET='0',SFC_DIRECT64_SINGLE_PRESENT='0',
                   SFC_DIRECT64_PACED_FRAMES='0',SFC_DIRECT64_TIMING_ONLY='0',
                   SFC_D3D9_GAME_OUTPUT='1',SFC_D3D9_OFFSET_X='-0.0001',
                   SFC_D3D9_VISUAL_SETTINGS='1',SFC_D3D9_LIGHT_SETTINGS='1',
                   SFC_DIRECT64_BACKBUFFER_DIAGNOSTIC='1',SFC_PIPELINE_MODE='performance')
        env['SFC_D3D9_LEGACY_STARTUP_WARMUP']='1' if legacy_startup_warmup else '0'
        if capture:
            if piece_index is None:raise ValueError('Diagnostic vendor capture requires one selected piece')
            env['DXVK_RTX_CAPTURE_ENABLE_ON_FRAME']='12'
        command=[str(guard),str(root),'60',str((256 if capture else 128)*1024*1024),str(2*1024*1024),
                 str(host),str(root),str(backend['runtime'])]
        process=subprocess.run(command,env=env,timeout=70,creationflags=subprocess.CREATE_NO_WINDOW)
        job=json.loads((root/'job-result.json').read_text())
        text=(root/'job-console.log').read_text()
        if (process.returncode or job['exit_code'] or job['stop_reason']
                or job['remaining_owned_processes']
                or 'DIRECT64_OUTPUT_RETURNED sdk_mesh_calls=0' not in text
                or 'OUTPUT_API_SHUTDOWN 0' not in text):
            raise ValueError(f"Piece {piece['index']} renderer/output failed; evidence retained")
        pixels=[inspect_output(root,i) for i in range(snapshots)]
        results.append(dict(index=piece['index'],job=job,pixels=pixels,
                            replay_sha256=hashlib.sha256((root/'scene.bin').read_bytes()).hexdigest()))
    visible=bool(results) and all(all(p['shaded_hull_pixels']>0 for p in r['pixels']) for r in results)
    out=dict(result='STANDALONE_DEBRIS_SHADED' if visible else 'PARTIAL_DEBRIS_OUTPUT',pieces=results,
             legacy_startup_warmup=legacy_startup_warmup,
             base_materials=base_materials,snapshots=snapshots,
             synchronous_shaders=synchronous_shaders,vendor_capture=capture,
             scope='Independent captured poses; explicit offline opposed directional lights; SFC not launched')
    (folder/'render-review.json').write_text(json.dumps(out,indent=2))
    return out


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder',type=Path)
    parser.add_argument('--execute',action='store_true',required=True)
    parser.add_argument('--legacy-startup-warmup',action='store_true')
    parser.add_argument('--piece',type=int,choices=range(4))
    parser.add_argument('--snapshots',type=int,choices=(1,2),default=1)
    parser.add_argument('--base-materials',action='store_true')
    parser.add_argument('--capture',action='store_true')
    parser.add_argument('--synchronous-shaders',action='store_true')
    args=parser.parse_args()
    print(json.dumps(execute(args.folder,legacy_startup_warmup=args.legacy_startup_warmup,
                            piece_index=args.piece,snapshots=args.snapshots,
                            base_materials=args.base_materials,capture=args.capture,
                            synchronous_shaders=args.synchronous_shaders),indent=2))


if __name__=='__main__':main()
