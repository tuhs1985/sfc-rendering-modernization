"""Explicit fresh-model selection for the sponsor's known player-ship fixture.

Not an engine player-ownership API; ambiguous same-model owners are unsupported.
"""
from pathlib import Path
import tomllib

CONFIG=Path(__file__).with_name('offset_ship.toml')

def camera_left_offset(span):
    if not 0<span<=500000:raise ValueError('Diagnostic offset asset bounds')
    # Sponsor2026-10-21:one-third less separation than previous1.5*span.
    # Camera-left diagnostic placement only;no model scale/depth change.
    return [-float(span),0,0]


def selected_model(raw=None):
    raw=CONFIG.read_bytes() if raw is None else raw
    if len(raw)>4096:raise ValueError('Owner selection config4KiB cap')
    data=tomllib.loads(raw.decode('utf-8'))
    if set(data)!={'selected_model'}:raise ValueError('Owner selection keys')
    value=data['selected_model']
    if not isinstance(value,str) or value!=value.lower() or '\\' in value or '..' in value or not value.startswith('assets/models/') or not value.endswith('.mod') or len(value)>240:
        raise ValueError('Exact normalized selected model required')
    return value

def choose(candidates,model):
    matching=[(row,mesh) for row,mesh in candidates if mesh['refs']['model_filename'].lower().replace('\\','/')==model]
    owners={(row[1],row[7]) for row,_ in matching}
    if len(owners)>1:raise ValueError('Multiple owners of configured player-fixture model;no guessed selection')
    return matching[0] if matching else None
