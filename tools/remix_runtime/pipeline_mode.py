"""Evidence policy only; never disables identity, bounds, fences or cleanup."""
MODES=('performance','test')

def validate(mode):
    if mode not in MODES:raise ValueError('Pipeline mode must be performance or test')
    return mode

def policy(mode):
    validate(mode)
    return dict(mode=mode,detailed_evidence=mode=='test',asset_ready_target_seconds=2,
                safety_checks=True,continuous_image_readback=False,
                earlier_asset_discovery=False)
