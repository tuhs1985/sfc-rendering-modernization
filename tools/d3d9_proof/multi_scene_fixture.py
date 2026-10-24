"""Explicit synthetic scene from two distinct historical runtime captures.

This is offline transport/render validation,not fresh SFC runtime evidence.
Model files are never read. Poses below are synthetic,using qualified arithmetic.
"""
import json
from pathlib import Path
import shutil
import struct
from scene_bundle import ROOT,snapshots
from live_scene import decode_mesh
from analyze_live_camera import native_matrix,multiply

CAPTURES=(ROOT/'artifacts/m1/runs/20261016-223535-enabled/LIVE-SCENE-001-asset-3.bin',
          ROOT/'artifacts/remix-runtime/runs/20261022-045744-572970-in-game/gate/LIVE-SCENE-001-asset-1.bin')


def synthetic_instance(packet,references,owner):
    """Offline identity substitution ONLY;unchanged captured geometry/image content."""
    raw=bytearray(packet);refs=json.loads(references)
    struct.pack_into('<I',raw,16,owner);struct.pack_into('<I',raw,32,0x10000000+owner*0x1000)
    value=2166136261
    for i,byte in enumerate(raw):value=((value^(0 if 12<=i<16 else byte))*16777619)&0xffffffff
    struct.pack_into('<I',raw,12,value);refs.update(owner_epoch=owner,packet_fnv1a=value)
    return bytes(raw),json.dumps(refs).encode()


def rows_and_packets(work,session,extended=False):
    gate=work/'gate';gate.mkdir()
    first=decode_mesh(CAPTURES[0].read_bytes(),CAPTURES[0].with_suffix('.json').read_bytes())
    updates=CAPTURES[0].parent/'LIVE-SCENE-001-updates.jsonl'
    chosen=snapshots(first,updates,3)[0]
    with updates.open() as stream:
        anchor=next(json.loads(line) for number,line in enumerate(stream,1) if number==chosen['line'])
    rows=[];proof=[]
    sources=list(CAPTURES)
    if extended:sources+=[ROOT/'artifacts/remix-runtime/runs/20261023-191630-707670-in-game/gate/LIVE-SCENE-001-asset-2.bin',CAPTURES[0]]
    for index,path in enumerate(sources):
        mesh=decode_mesh(path.read_bytes(),path.with_suffix('.json').read_bytes())
        revision=int(path.stem.rsplit('-',1)[1]);row=list(anchor)
        row[1],row[5],row[6],row[7]=mesh['header'][4],mesh['header'][10],mesh['header'][12],revision
        row[2]=200000;row[4]=1;row[42:45]=[0,0,0];row[48]=1
        world=native_matrix(row[8:25]);view=native_matrix(row[49:66]);projection=native_matrix(row[66:83])
        # Two different meshes,side by side in the SAME synthetic game camera.
        span=max(max(p[a] for p in mesh['points'])-min(p[a] for p in mesh['points']) for a in range(3))
        for axis in range(3):world[axis][3]+=view[0][axis]*span*(index-.5)*1.5
        viewport=struct.unpack('<6f',struct.pack('<6I',*row[83:89]))
        screen=[[viewport[4],0,0,viewport[0]+viewport[4]],
                [0,-viewport[5],0,viewport[1]+viewport[5]],[0,0,1,0],[0,0,0,1]]
        composed=multiply(screen,multiply(projection,multiply(view,world)))
        row[8:25]=list(struct.unpack('<16I',struct.pack('<16f',*(x for r in world for x in r))))+[0x100]
        row[25:42]=list(struct.unpack('<16I',struct.pack('<16f',*(x for r in composed for x in r))))+[0]
        rows.append(row)
        if extended and index==3:
            packet,references=synthetic_instance(path.read_bytes(),path.with_suffix('.json').read_bytes(),31)
            revision=63;row[1]=31;row[7]=revision
            (gate/f'LIVE-SCENE-001-asset-{revision}.bin').write_bytes(packet)
            (gate/f'LIVE-SCENE-001-asset-{revision}.json').write_bytes(references)
        else:
            for extension in ('bin','json'):shutil.copyfile(path.with_suffix('.'+extension),gate/f'LIVE-SCENE-001-asset-{revision}.{extension}')
        proof.append(dict(source=str(path.relative_to(ROOT)),geometry=mesh['geometry_sha256'],model=mesh['refs']['model_filename']))
    if len({p['geometry'] for p in proof})!=(3 if extended else 2) or len({r[1] for r in rows})!=len(sources):raise ValueError('Distinct captured assets and independent fixture owners required')
    (gate/'LIVE-SCENE-001-updates.jsonl').write_bytes(b'')
    (work/'manifest.json').write_text(json.dumps(dict(synthetic_source=True,source_assets=proof,
                semantic_calibration={'scene_session':session}),indent=2))
    (work/'fixture-rows.bin').write_bytes(b''.join(struct.pack('<96I',*r) for r in rows))
    return rows
