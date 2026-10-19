"""Strict Remix light controls; no native SFC state is modified."""
import math
from pathlib import Path
import tomllib
from light_shapes import FIELDS as SHAPE_FIELDS,validate_shape

FIELDS = {'id', 'enabled', 'intensity_multiplier', 'color_multiplier',
          'position_offset', 'direction_override', 'radius',
          'angular_diameter_degrees', 'volumetric_multiplier', 'raytracing'} | SHAPE_FIELDS


def number(value, lo, hi):
    if type(value) not in (int, float) or not math.isfinite(value) or not lo <= value <= hi:
        raise ValueError('Light control must be a finite number within documented bounds')
    return value


def vector(value, lo, hi):
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError('Light control requires exactly three numbers')
    return [number(v, lo, hi) for v in value]


def validate(data, registry):
    """Registry supplied by adjudicated discovery, not config-created light roles.

    Registry maps stable logical ID to {kind: directional|point}. Unknown native
    types are deliberately not eligible. No process pointers are accepted as IDs.
    """
    if set(data)-{'schema_version', 'backend', 'lights', 'conversion_scale', 'master_multiplier'}:
        raise ValueError('Unknown light configuration field')
    if type(data.get('schema_version')) is not int or data['schema_version'] != 1 or data.get('backend') != 'remix_sdk_0_6_4':
        raise ValueError('Unsupported light schema/backend')
    scales(data)
    rows = data.get('lights', [])
    if not isinstance(rows, list) or len(rows) > 64:
        raise ValueError('At most 64 configured logical lights')
    result, seen = [], set()
    for row in rows:
        if not isinstance(row, dict) or set(row)-FIELDS:
            raise ValueError('Unknown per-light field')
        identity = row.get('id')
        if not isinstance(identity, str) or identity not in registry or identity in seen:
            raise ValueError('Unresolved or duplicate logical light ID')
        seen.add(identity)
        kind = registry[identity]['kind']
        if kind not in ('directional', 'point'):
            raise ValueError('Unqualified light kind')
        enabled = row.get('enabled', True)
        if type(enabled) is not bool:
            raise ValueError('enabled must be true/false')
        if row.get('raytracing', 'renderer_default') != 'renderer_default':
            raise ValueError('Pinned Remix SDK has no qualified per-light raytracing/shadow switch; use enabled=false to remove the light')
        out = dict(id=identity, enabled=enabled, raytracing='renderer_default',
                   intensity_multiplier=number(row.get('intensity_multiplier', 1), 0, 1000),
                   color_multiplier=vector(row.get('color_multiplier', [1, 1, 1]), 0, 16),
                   volumetric_multiplier=number(row.get('volumetric_multiplier', 1), 0, 16))
        if 'type' in row:out['shape']=validate_shape(row,number,vector)
        elif set(row)&(SHAPE_FIELDS-{'radius'}):raise ValueError('Explicit type required for light-shape settings')
        if 'direction_override' in row:
            if kind != 'directional' and 'type' not in row:
                raise ValueError('Direction override not qualified for this light kind')
            d = vector(row['direction_override'], -1e6, 1e6)
            length = math.hypot(*d)
            if length < 1e-8:
                raise ValueError('Direction must be nonzero')
            out['direction_override'] = [v/length for v in d]
        for field, eligible, limits in (
                ('position_offset', 'point', None), ('radius', 'point', (1e-5, 1e6)),
                ('angular_diameter_degrees', 'directional', (0, 180))):
            if field not in row:
                continue
            if kind != eligible and 'type' not in row:
                raise ValueError('Shape control incompatible with light kind')
            out[field] = vector(row[field], -1e6, 1e6) if limits is None else number(row[field], *limits)
        result.append(out)
    if sum(r['enabled'] and r.get('shape',{}).get('type')=='dome' for r in result)>1:
        raise ValueError('At most one enabled dome environment per scene')
    return result


def scales(data):
    return (number(data.get('conversion_scale',1),0,1000),
            number(data.get('master_multiplier',1),0,16))


def load(path, registry):
    path = Path(path)
    if path.stat().st_size > 64*1024:
        raise ValueError('Light config 64KiB limit')
    return validate(tomllib.loads(path.read_text(encoding='utf-8')), registry)
