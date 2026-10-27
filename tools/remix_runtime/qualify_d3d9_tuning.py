"""Default-off live controls qualification on the established D3D9 return path."""
from pathlib import Path
import argparse,json
from qualify_multiship import locks,ROOT,digest
from async_material_checkout import backend_inputs,receipt
from qualify_async_material import baseline,inspect

RECEIPT=ROOT/'artifacts/d3d9-proof/tuning/qualification.json'

def tuning_locks():
    value=locks()
    # Explicit tuning admits edited appearance inputs. Keep all code,binaries,
    # dependency and placement locks; only these two editable profiles vary.
    for name in ('rendering','lights'):value['configs'].pop(name)
    return value

def qualify(folder,appearance_baseline):
    from qualify_async_material import require_qualification
    require_qualification()
    config,approved=baseline(appearance_baseline)
    backend=backend_inputs();proof=inspect(folder,backend,config)
    folder=Path(folder);r=json.loads((folder/'result.json').read_text())
    if not r.get('live_tuning_fixture'):raise ValueError('Actual live-control fixture required')
    native=(folder/'gpu/job-console.log').read_text()
    if 'D3D9_VISUAL_TUNING_APPLIED' not in native:raise ValueError('Native D3D9 visual hot update missing')
    controls=json.loads((folder/'gpu/tuning-controls-summary.json').read_text())
    if controls['accepted']<1 or controls['rejected']:raise ValueError('Live material publication did not complete')
    if controls['generated_bytes']!=0:raise ValueError('Scalar tuning unnecessarily regenerated prepared images')
    stage=(folder/'gpu/rtx-remix/mods/sfc-policy/mod.usda').read_text()
    if 'float inputs:emissive_intensity = 0.25' not in stage:raise ValueError('Fixture material update absent from final library')
    RECEIPT.parent.mkdir(parents=True,exist_ok=True)
    RECEIPT.write_text(json.dumps(dict(result='OFFLINE_D3D9_TUNING_PREPARED_NOT_GAMEPLAY_PASS',locks=tuning_locks(),backend=receipt(backend),evidence=proof,controls=controls,appearance_baseline=approved,tactical_seconds=1800,workflow_seconds=1980,editable_profiles=['rendering.toml','lights.toml']),indent=2))
    require_qualification_tuning();print('Current D3D9 live tuning offline qualification PASS')

def require_qualification_tuning():
    q=json.loads(RECEIPT.read_text());backend=backend_inputs()
    if q.get('result')!='OFFLINE_D3D9_TUNING_PREPARED_NOT_GAMEPLAY_PASS' or q['locks']!=tuning_locks() or q['backend']!=receipt(backend):raise ValueError('D3D9 tuning source/binary qualification stale')
    proof=q['evidence']
    if digest(ROOT/proof['folder']/'result.json')!=proof['result_sha256']:raise ValueError('Tuning evidence changed')
    from rendering_config import DEFAULT
    from image_controls import encode as image
    from material_controls import encode as material
    from quality_controls import encode as quality
    raw=DEFAULT.read_bytes();image(raw);material(raw);quality(raw)
    return {**q,'backend_inputs':receipt(backend)}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--fixture',type=Path,required=True);p.add_argument('--appearance-baseline',type=Path,required=True);a=p.parse_args();qualify(a.fixture,a.appearance_baseline)
