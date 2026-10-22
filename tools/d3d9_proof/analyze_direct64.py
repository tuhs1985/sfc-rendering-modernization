"""Bounded actual returned-pixel analysis,not USD reconstruction or image tuning."""
import argparse
import json
from pathlib import Path
import struct
import numpy as np
from PIL import Image
from run_offline import ROOT,oracle,neighborhood,digest


def raw32(path):
    path=Path(path);raw=path.read_bytes()
    if not 8<=len(raw)<=1920*1080*4+8:raise ValueError('Returned image cap')
    width,height=struct.unpack_from('<2I',raw)
    if not width or not height or width>1920 or height>1080 or len(raw)!=8+width*height*4:raise ValueError('Returned image schema')
    return width,height,raw[8:]


def overlap(actual,expected):
    return dict(pixels=int(actual.sum()),expected=int(expected.sum()),iou=float((actual&expected).sum()/max(1,(actual|expected).sum())),
        outside_1px=int((actual&~neighborhood(expected,1)).sum()),missing_1px=int((expected&~neighborhood(actual,1)).sum()))


def analyze(folder):
    folder=Path(folder).resolve();folder.relative_to(ROOT/'artifacts/d3d9-intercept/direct64-runs')
    manifest=json.loads((folder/'scene.json').read_text());rows=[]
    result=json.loads((folder/'result.json').read_text()) if (folder/'result.json').exists() else {}
    if result.get('timing_only'):raise ValueError('Timing-only run has no pixel evidence')
    paced=result.get('paced_frames',0)
    if paced not in (0,120,300):raise ValueError('Paced analysis bound')
    mapping=[(i,i%len(manifest['frames'])) for i in range(paced) if i==0 or (i+1)%59==0] if paced else list(enumerate(range(len(manifest['frames']))))
    for frame,source_index in mapping:
        width,height,color=raw32(folder/f'returned-{frame}-0.raw32')
        dw,dh,depth=raw32(folder/f'returned-{frame}-1.raw32');pw,ph,picking=raw32(folder/f'returned-{frame}-2.raw32')
        if (width,height)!=(dw,dh) or (width,height)!=(pw,ph):raise ValueError('Triplet size mismatch')
        rgba=np.frombuffer(color,dtype=np.uint8).reshape(height,width,4)[:,:,[2,1,0,3]]
        z=np.frombuffer(depth,dtype='<f4').reshape(height,width);ids=np.frombuffer(picking,dtype='<u4').reshape(height,width)
        picking_mask=ids!=0;finite=z[np.isfinite(z)]
        sentinel=int((z==-1234).sum())
        # Normal intercepted draws can return ID0 on a visible surface. It is
        # NOT the SDK's explicit selected-owner ID. Use qualified depth/sentinel
        # coverage only for this isolated one-ship proof;never black-color keying.
        mask=(np.isfinite(z)&(z>=0)&(z<=1)) if sentinel else np.zeros(z.shape,dtype=bool)
        candidates={mode:overlap(mask,oracle(folder,source_index,width,height,viewport_mode=mode)) for mode in ('captured','full_frustum')}
        candidates['full_frustum_half_pixel']=overlap(mask,oracle(folder,source_index,width,height,viewport_mode='full_frustum',pixel_center=.5))
        expected_depth=oracle(folder,source_index,width,height,viewport_mode='full_frustum',pixel_center=.5,return_depth=True)
        common=mask&np.isfinite(expected_depth)
        depth_error=float(np.max(np.abs(z[common]-expected_depth[common]))) if common.any() else None
        Image.fromarray(rgba).save(folder/f'returned-{frame}.png')
        depth_values=[float(x) for x in np.quantile(finite,[0,.01,.5,.99,1])] if finite.size else []
        on=z[mask];off=z[~mask]
        rows.append(dict(frame=frame,source_frame=manifest['frames'][source_index]['frame'],width=width,height=height,
            coverage_pixels=int(mask.sum()),depth_background_sentinel_pixels=sentinel,
            picking_nonzero_pixels=int(picking_mask.sum()),zero_picking_on_valid_depth=int((mask&~picking_mask).sum()),
            unique_nonzero_picking=int(np.unique(ids[picking_mask]).size),
            picking_ids=[int(x) for x in np.unique(ids[mask])[:16]],depth_finite=int(np.isfinite(z).sum()),depth_quantiles=depth_values,
            covered_depth_range=[float(on.min()),float(on.max())] if on.size and np.isfinite(on).all() else [],
            background_depth_values=[float(x) for x in np.unique(off)[:8]],
            colors_in_coverage=int(np.unique(rgba[mask,:3],axis=0).shape[0]),projection_candidates=candidates,
            common_depth_pixels=int(common.sum()),max_normalized_depth_error=depth_error,
            color_sha256=digest(folder/f'returned-{frame}-0.raw32')))
    matched=all(r['projection_candidates']['full_frustum_half_pixel']['iou']>=.98 and r['depth_background_sentinel_pixels']>0
        and r['max_normalized_depth_error'] is not None and r['max_normalized_depth_error']<=1e-5 for r in rows)
    report=dict(result='DIRECT64_STATIC_FRAME_OUTPUT_CORRELATED' if matched else 'DIRECT64_PIXELS_REVIEW_REQUIRED',frames=rows,sdk_mesh_calls=0,
        analysis_source_sha256=digest(Path(__file__)),oracle_source_sha256=digest(ROOT/'tools/d3d9_proof/run_offline.py'),
        scope='isolated actual output samples;cross-process byte proof separate;not original-rate replay,live cadence,appearance parity or lifecycle qualification')
    (folder/'pixel-analysis.json').write_text(json.dumps(report,indent=2));return report


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('folder',type=Path);args=parser.parse_args();report=analyze(args.folder);print(json.dumps(report,indent=2))
    if report['result']!='DIRECT64_STATIC_FRAME_OUTPUT_CORRELATED':raise SystemExit(2)
