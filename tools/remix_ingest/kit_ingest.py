"""Executed only by the isolated vendor Kit CLI, never by SFC or the open GUI."""
import asyncio
import json
import os
from pathlib import Path
import traceback

import omni.kit.app
from pxr import Usd, UsdGeom, UsdShade
from omni.flux.validator.mass.core import cli as vendor_cli
from omni.flux.utils.common.path_utils import read_metadata


def write_bounded(path, value, limit):
    data = (json.dumps(value, allow_nan=False, separators=(',', ':')) + '\n').encode()
    if len(data) > limit:
        raise ValueError('Kit inspection output exceeds cap')
    with path.open('xb') as stream:
        stream.write(data)


def inspect_stage(path):
    stage = Usd.Stage.Open(str(path))
    if stage is None:
        raise ValueError('Cannot open ingested stage')
    meshes, points_total, corners_total = [], 0, 0
    for prim in stage.Traverse():
        if not prim.IsA(UsdGeom.Mesh):
            continue
        mesh = UsdGeom.Mesh(prim)
        counts = list(mesh.GetFaceVertexCountsAttr().Get() or [])
        indices = list(mesh.GetFaceVertexIndicesAttr().Get() or [])
        points = mesh.GetPointsAttr().Get() or []
        points_total += len(points)
        corners_total += len(indices)
        if len(meshes) >= 16 or points_total > 8192 or corners_total > 1536 or any(n != 3 for n in counts):
            raise ValueError('Ingested topology outside first-mesh inspection bounds')
        if sum(counts) != len(indices) or any(i < 0 or i >= len(points) for i in indices):
            raise ValueError('Malformed ingested indices')
        normals = mesh.GetNormalsAttr().Get() or []
        st = UsdGeom.PrimvarsAPI(prim).GetPrimvar('st')
        uv = st.ComputeFlattened() if st else []
        if len(normals) > 8192 or len(uv or []) > 8192:
            raise ValueError('Ingested attribute arrays exceed bounds')
        matrix = UsdGeom.XformCache().GetLocalToWorldTransform(prim)
        bound_material = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()[0]
        meshes.append({'path': str(prim.GetPath()), 'points': [list(p) for p in points],
                       'counts': counts, 'indices': indices, 'normals': [list(p) for p in normals],
                       'normal_interpolation': str(mesh.GetNormalsInterpolation()),
                       'uv': [list(p) for p in (uv or [])], 'uv_interpolation': str(st.GetInterpolation()) if st else None,
                       'orientation': str(mesh.GetOrientationAttr().Get()),
                       'local_to_world': [list(row) for row in matrix],
                       'material': str(bound_material.GetPath()) if bound_material else None})
    if not meshes:
        raise ValueError('No mesh prims in ingested stage')
    return {'meshes': meshes, 'meters_per_unit': UsdGeom.GetStageMetersPerUnit(stage),
            'up_axis': str(UsdGeom.GetStageUpAxis(stage))}


async def run():
    config = json.loads(Path(os.environ['SFC_REMIX_JOB_CONFIG']).read_text())
    root = Path(config['work'])
    report = {'schema': 'sfc.remix.inspect.v1', 'fixture': config['fixture'], 'status': 'FAIL'}
    try:
        # Invoke installed official schema runner, not a custom asset converter.
        # Its post_quit is queued; synchronous inspection follows before returning
        # to the Kit update loop. Never replace a vendor failure with exit code 0.
        await vendor_cli.run([config['schema']], executor=0, print_result=True, silent=False, timeout=120)
        stage_path = Path(config['output']) / 'ship.usda'
        if read_metadata(str(stage_path), 'validation_passed') is not True:
            raise ValueError('No affirmative vendor validation_passed metadata')
        geometry = inspect_stage(stage_path)
        write_bounded(root / 'geometry.json', geometry, 2*1024*1024)
        report.update(status='INSPECTED', stage=str(stage_path), meshes=len(geometry['meshes']),
                      triangles=sum(len(m['counts']) for m in geometry['meshes']), vendor_validation_passed=True)
    except Exception as exc:
        report.update(error=str(exc)[:2000], traceback=traceback.format_exc()[-8000:])
        omni.kit.app.get_app().post_quit(2)
    finally:
        write_bounded(root / 'inspection.json', report, 65536)


asyncio.ensure_future(run())
