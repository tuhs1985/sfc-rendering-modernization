"""Prepare immutable captured debris for the ordinary D3D9 consumer."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/scene_bridge'))
sys.path.insert(0,str(ROOT/'tools/m1_component'))
from break_scene import decode_capture
from scene_bundle import prepare, read_replay
from analyze_live_camera import native_matrix
from live_camera import camera_state


def prepare_capture(capture,output,game_root):
    capture=Path(capture).resolve();capture.relative_to(ROOT/'artifacts')
    output=Path(output).resolve();output.relative_to(ROOT/'artifacts')
    if output.exists():raise ValueError('Refuse to overwrite break replay')
    scene=decode_capture(capture)
    result=json.loads((capture/'result.json').read_text())['report']
    session=json.loads((capture/'manifest.json').read_text())['session']
    rows={piece['child']:piece for piece in result['pieces']}
    observation={row['index']:row for row in result['geometry']}
    output.mkdir(parents=True)
    prepared=[]
    for index,mesh in sorted(scene['pieces'].items()):
        row=rows[mesh['piece']['child']]
        cameras={value['sample']:value['words'] for value in row.get('cameras',[])}
        poses=row['draws'];frames=[];slot=observation[index]['slot']
        for sample,pose in enumerate(poses,1):
            camera=cameras.get(sample)
            if camera is None:raise ValueError('Captured camera missing for piece pose')
            record=[0]*96
            record[8:25]=pose['supplied'];record[25:42]=pose['composed']
            record[48]=1;record[49:89]=camera
            qualified=camera_state(record,[0,0,0],mesh['used_points'])
            frames.append(dict(owner=mesh['header'][4],revision=index+1,frame=sample,active=1,
                               model=native_matrix(pose['supplied']),view=native_matrix(camera[:17]),
                               projection=native_matrix(camera[17:34]),viewport=qualified['viewport'],
                               native_composed=native_matrix(pose['composed']),
                               composition_error_pixels=qualified['native_composition_pixel_error']))
        source=capture/f'break-piece-{slot}.bin'
        mesh['_capture_refs_sha256']=hashlib.sha256(source.with_suffix('.json').read_bytes()).hexdigest()
        directory=output/f'piece-{index}'
        manifest=prepare(source,directory,game_root,qualified_mesh=mesh,
                         break_replay=dict(metadata=str(capture/'manifest.json'),session=session,frames=frames,revision=index+1),
                         output_extent=(1920,1080))
        readback=read_replay(directory/'scene.bin')
        expected=[(*mesh['points'][i],*normal,*uv) for i,normal,uv in mesh['corners']]
        if readback['vertices']!=expected or len(readback['indices'])!=len(expected):
            raise ValueError('D3D9 piece array read-back differs')
        if len(readback['frames'])!=len(frames):raise ValueError('D3D9 pose count differs')
        prepared.append(dict(index=index,folder=str(directory.relative_to(ROOT)),
                             triangles=manifest['triangles'],textures=len(manifest['textures']),
                             frames=len(frames),asset_sha256=manifest['asset_sha256'],
                             max_camera_error_pixels=max(f['composition_error_pixels'] for f in frames)))
    receipt=dict(result='CAPTURED_BREAK_PIECES_PREPARED_FOR_D3D9',pieces=prepared,
                 source=str(capture.relative_to(ROOT)),source_session=session,
                 scope='Independent captured piece poses; no simultaneous source-frame claim or native suppression')
    (output/'break-replay.json').write_text(json.dumps(receipt,indent=2))
    return receipt


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture',type=Path);parser.add_argument('output',type=Path)
    parser.add_argument('--game-root',type=Path,default=Path(r'C:\Project\SFC-Remix-Return-Test'))
    args=parser.parse_args()
    print(json.dumps(prepare_capture(args.capture,args.output,args.game_root),indent=2))


if __name__=='__main__':main()
