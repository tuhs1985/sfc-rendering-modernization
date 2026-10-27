"""Re-read Run200 fixed-camera roughness controls; no GPU/game launch."""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[3]
RUNS=ROOT/'artifacts/remix-runtime/runs'
CASES={
    'natural_failure':'20261026-104508-124830-return-fixture',
    'unused_material_only':'20261026-104559-209587-return-fixture',
    'after_first_snapshot':'20261026-104652-057412-return-fixture',
    'distinct_timestamp_diagnostic':'20261026-104940-800962-return-fixture',
    'constant_timestamp_negative':'20261026-105119-089917-return-fixture',
    'integrated_fix':'20261026-105556-985784-return-fixture',
    'integrated_fix_forced_collision':'20261026-105854-127363-return-fixture',
}


def analyze():
    rows=[]
    for name,folder in CASES.items():
        p=RUNS/folder;result=json.loads((p/'result.json').read_text())
        samples=[]
        for image in ('fixture-ship.bmp','fixture-ship-late.bmp'):
            raw=(p/image).read_bytes();pixels=np.asarray(Image.open(p/image))
            # Exact fixed-pose FCA region used for all these two-ship controls.
            # Includes clear pixels;two colors means uniform surface+background.
            roi=pixels[740:915,815:1050,:3]
            samples.append(dict(path=str((p/image).relative_to(ROOT)),sha256=hashlib.sha256(raw).hexdigest(),
                fca_region_unique_colors=len(np.unique(roi.reshape(-1,3),axis=0))))
        rows.append(dict(case=name,folder=str(p.relative_to(ROOT)),error=result.get('error'),
            fixture_exit=result.get('fixture_exit'),host_exit=result.get('host_exit'),snapshots=samples,
            probe=json.loads((p/'material-refresh-isolation.json').read_text()),
            material_events=result['live_owner_timing']['multi_scene']['material_events']))
    by={r['case']:r for r in rows}
    for name in ('natural_failure','after_first_snapshot','constant_timestamp_negative'):
        assert by[name]['snapshots'][1]['fca_region_unique_colors']==2
    for name in ('unused_material_only','distinct_timestamp_diagnostic','integrated_fix','integrated_fix_forced_collision'):
        assert by[name]['snapshots'][1]['fca_region_unique_colors']>100
    assert all(r['error'] is None and r['fixture_exit']==r['host_exit']==0 for r in rows)
    report=dict(schema='sfc.material-refresh-isolation.v1',diagnostic_only=True,game_launched=False,
        roughness_view=dict(index=89,meaning='NVIDIA primary perceptual roughness;final grading still applies'),
        region=[815,740,1050,915],cases=rows,
        packaged_timestamp=json.loads((ROOT/'artifacts/candidate-hot-reload/run200-usd-timestamp.json').read_text()),
        conclusion='Same-second revisions invisible to packaged Windows OpenUSD;distinct revision timestamps restore roughness without new geometry or periodic notification',
        limits=['Synthetic fixed camera and saved live geometry','First snapshot can precede enhancement installation',
            'No per-material installed ACK','Actual SFC confirmation pending','Runtime/public-source instruction parity not asserted'])
    (ROOT/'artifacts/candidate-hot-reload/run200-refresh-analysis.json').write_text(json.dumps(report,indent=2))
    print('Seven standalone controls reanalyzed;negative and positive roughness outcomes PASS')
    return report


if __name__=='__main__':analyze()
