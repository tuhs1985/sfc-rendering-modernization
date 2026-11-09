"""Version1 actual-rendered membership and per-owner native insertion receipts."""
import hashlib,json,struct
from pathlib import Path
from player_replacement import ROOT,OFFSET as BASE
from runtime_context import CONTEXT
from scene_capacity import COHORT_OFFSET,OWNERS
OFFSET=COHORT_OFFSET
MANIFEST_BYTES=64+52*OWNERS
CELL_BYTES=MANIFEST_BYTES+64
OWNER_BASE=64+3*CELL_BYTES
SIZE=OWNER_BASE+OWNERS*32
MAGIC=0x31434e53
RECEIPT=CONTEXT.artifact('player-replacement/native-cohort-tests/qualification.json')
EDITABLE_VISUALS=frozenset({'tools/remix_runtime/config/lights.toml','tools/remix_runtime/config/rendering.toml'})


def current_visual_inputs():
    """Appearance is editable; reuse runtime validators instead of old hashes.

    This runs once during preflight,never in a rendering callback. Historical
    qualification hashes remain evidence;record current validated hashes too.
    """
    import tomllib
    from light_controls import validate
    from live_lights import REGISTRY
    from image_controls import encode_current as image
    from material_controls import encode as material
    from quality_controls import encode as quality
    result={}
    for name in sorted(EDITABLE_VISUALS):
        cap=65536 if name.endswith('/lights.toml') else 16384
        with (CONTEXT.setting(Path(name).name) if CONTEXT.release else ROOT/name).open('rb') as stream:raw=stream.read(cap+1)
        if len(raw)>cap:raise ValueError('Visual config byte limit: '+name)
        if name.endswith('/lights.toml'):
            controls=validate(tomllib.loads(raw.decode('utf-8')),REGISTRY)
            if not {'native_directional_0','native_directional_1'}<={r['id'] for r in controls}:raise ValueError('Both qualified native directional controls required')
        else:image(raw);material(raw);quality(raw)
        result[name]=hashlib.sha256(raw).hexdigest().upper()
    return result

def decode(raw):
    if len(raw)!=SIZE:raise ValueError('Native cohort layout')
    h=struct.unpack_from('<16I',raw)
    if h[:3]!=(MAGIC,2,SIZE) or not h[3]:raise ValueError('Native cohort identity')
    owners=[]
    for i in range(OWNERS):
        v=struct.unpack_from('<8I',raw,OWNER_BASE+i*32)
        if v[0]:owners.append(dict(zip(('owner','revision','model','source','inserted','suppressed','unavailable','last_frame'),v)))
    return dict(pid=h[3],session=list(h[4:8]),inserted=h[8],suppressed=h[9],unavailable=h[10],omitted=h[11],owners=owners)

def save(channel,folder):
    raw=channel.read(OFFSET,SIZE);value=decode(raw);folder=Path(folder)
    (folder/'NATIVE-COHORT-001.bin').write_bytes(raw);(folder/'NATIVE-COHORT-001.json').write_text(json.dumps(value,indent=2));return value

def require_qualification(policy):
    if CONTEXT.release:
        from release_manifest import load
        from async_material_checkout import backend_inputs,receipt
        manifest=load(CONTEXT.package_root)
        if policy!='ExtraFrame':raise ValueError('Alpha release uses the qualified ExtraFrame policy')
        return dict(result='RELEASE_MANIFEST_INPUTS',version=manifest['version'],
                    backend_inputs=receipt(backend_inputs()),active_visual_inputs=current_visual_inputs())
    q=json.loads(RECEIPT.read_text())
    if q['result']!='NATIVE_COHORT_PREPARED' or policy not in q['policies']:raise ValueError('Native cohort not qualified')
    for name,sha in q['files'].items():
        if name in EDITABLE_VISUALS:continue
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest().upper()!=sha:raise ValueError('Native cohort inputs changed: '+name)
    active_visual_inputs=current_visual_inputs()
    from async_material_checkout import backend_inputs,receipt
    return dict(q,backend_inputs=receipt(backend_inputs()),active_visual_inputs=active_visual_inputs)
