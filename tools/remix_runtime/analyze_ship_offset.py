"""Compare bounded, same-source unmodified/offset GPU fixtures. No game launch."""
from pathlib import Path
import argparse
import json
import numpy as np
from PIL import Image, ImageDraw
from run_coverage_probe import ROOT, digest

def compare(baseline,offset):
    baseline=Path(baseline).resolve();offset=Path(offset).resolve()
    for folder in (baseline,offset):
        if folder.parent!=(ROOT/'artifacts/remix-runtime/runs').resolve():raise ValueError('Exact project run required')
    a=json.loads((baseline/'manifest.json').read_text());b=json.loads((offset/'manifest.json').read_text())
    ca=a['replay_camera'];cb=b['replay_camera'];change=cb['diagnostic_offset']
    for name in ('source_capture','source_snapshot','owner_epoch','frame','asset_revision','output_sha256'):
        if ca[name]!=cb[name]:raise ValueError('Different source/camera: '+name)
    if a['mesh']['source_sha256']!=b['mesh']['source_sha256'] or digest(baseline/'coverage-mesh.bin')!=digest(offset/'coverage-mesh.bin'):
        raise ValueError('Different geometry')
    if ca.get('diagnostic_offset') or change['mode']!=1:raise ValueError('Expected unmodified then offset')
    for folder in (baseline,offset):
        result=json.loads((folder/'result.json').read_text())
        if result['result']!='TRIPLET_GPU_RETURN_QUALIFIED':raise ValueError('Unqualified GPU fixture')
        child=(folder/'triplet-consumer.log').read_text()
        if 'sequences=2 masked_composite=exact state_restored=1' not in child:raise ValueError('Missing actual receiver/compositor proof')
    model=np.array(change['original_native_model']);shifted=np.array(change['rendered_native_model'])
    if not np.array_equal(model[:3,:3],shifted[:3,:3]):raise ValueError('Rotation/scale changed')
    if not np.allclose(shifted[:3,3]-model[:3,3],change['world_translation'],rtol=0,atol=1e-5):raise ValueError('Translation mismatch')
    panels=[];centers=[];counts=[]
    for folder,label in ((baseline,'Original pose - offline Remix'),(offset,'3D offset - offline Remix')):
        for name in ('picking','color'):
            if (folder/f'coverage-5-{name}.bin').stat().st_size!=256*256*4:raise ValueError('Plane size cap')
        picking=np.fromfile(folder/'coverage-5-picking.bin',dtype='<u4').reshape(256,256)
        mask=picking==29;y,x=np.where(mask)
        if len(x)<=10:raise ValueError('Missing owner')
        centers.append([float(x.mean()),float(y.mean())]);counts.append(len(x))
        pixels=np.fromfile(folder/'coverage-5-color.bin',dtype='u1').reshape(256,256,4)[:,:,[2,1,0]]
        # Figure background is intentionally checkerboard; only real owner pixels
        # copied from returned color. NOT a game compositor or replacement test.
        yy,xx=np.indices((256,256));bg=np.where(((xx//16+yy//16)%2)[...,None],32,48)*np.ones((256,256,3),dtype='u1')
        bg=bg.astype('u1');bg[mask]=pixels[mask]
        panel=Image.new('RGB',(256,284));panel.paste(Image.fromarray(bg),(0,28));ImageDraw.Draw(panel).text((5,7),label,fill='white');panels.append(panel)
    figure=Image.new('RGB',(512,284));figure.paste(panels[0]);figure.paste(panels[1],(256,0));figure.save(offset/'offset-comparison.png')
    dx=centers[1][0]-centers[0][0];dy=centers[1][1]-centers[0][1]
    if abs(dx-change['screen_fraction']*256)>1 or abs(dy)>1:raise ValueError('Unexpected projected displacement')
    report=dict(result='OFFLINE_OFFSET_COMPOSITOR_QUALIFIED',baseline=str(baseline.relative_to(ROOT)),offset=str(offset.relative_to(ROOT)),
                owner_epoch=ca['owner_epoch'],asset_revision=ca['asset_revision'],source_engine_frame=ca['frame'],
                world_translation=change['world_translation'],mask_pixels=counts,centroids=centers,projected_shift=[dx,dy],
                original_mesh_camera_unchanged=True,original_game_launched=False,game_integration_qualified=False,
                scope='Actual standalone Remix world offset and native x86 masked compositor;NOT SFC presentation/UI/visibility or live latency proof')
    (offset/'offset.analysis.json').write_text(json.dumps(report,indent=2,allow_nan=False));return report

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('baseline',type=Path);parser.add_argument('offset',type=Path);args=parser.parse_args()
    print(json.dumps(compare(args.baseline,args.offset),indent=2))
