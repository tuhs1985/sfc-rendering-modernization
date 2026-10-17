"""Isolated installed-Kit preview. Author only an anonymous session layer."""
import asyncio
import hashlib
import json
import math
import os
from pathlib import Path
import time
import traceback
import sys
import carb.settings

import omni.kit.app
import omni.kit.renderer_capture
import omni.ui as ui
import omni.usd
from omni.kit.widget.viewport import ViewportWidget
from omni.kit.viewport.utility import capture_viewport_to_file
from lightspeed.hydra.remix.core import retry_remix_support_async, is_remix_supported, RemixSupport
from pxr import Gf, Sdf, Usd, UsdGeom, UsdLux, UsdShade

KEEP = {}


def report(path, data):
    payload = (json.dumps(data, allow_nan=False, indent=2)+'\n').encode()
    if len(payload) > 65536:
        raise ValueError('Preview report exceeds cap')
    with path.open('xb') as stream:
        stream.write(payload)


async def run():
    app = omni.kit.app.get_app()
    config = json.loads(Path(os.environ['SFC_MESH_PREVIEW_CONFIG']).read_text())
    work, asset = Path(config['work']), Path(config['asset'])
    status = {'schema': 'sfc.remix.preview.v1', 'status': 'FAIL'}
    try:
        if hashlib.sha256(asset.read_bytes()).hexdigest() != config['source_sha256']:
            raise ValueError('Scratch asset differs from accepted input')
        for name, expected in config.get('dependency_sha256', {}).items():
            if hashlib.sha256((work/name).read_bytes()).hexdigest() != expected:
                raise ValueError('Scratch texture dependency changed')
        context = omni.usd.get_context()
        success, error = await context.open_stage_async(str(asset))
        if not success:
            raise ValueError(f'Cannot open scratch USD: {error}')
        stage = context.get_stage()
        meshes = [UsdGeom.Mesh(p) for p in stage.Traverse() if p.IsA(UsdGeom.Mesh)]
        count = sum(len(m.GetFaceVertexCountsAttr().Get() or []) for m in meshes)
        if count != config['expected_triangles']:
            raise ValueError('Unexpected triangle count')
        bounds = UsdGeom.BBoxCache(Usd.TimeCode.Default(), [UsdGeom.Tokens.default_, UsdGeom.Tokens.render]).ComputeWorldBound(stage.GetPrimAtPath('/ReferenceTarget')).ComputeAlignedRange()
        if bounds.IsEmpty() and config.get('fresh_scene'):
            bounds=Gf.Range3d(Gf.Vec3d(-1),Gf.Vec3d(1))
        if bounds.IsEmpty():
            raise ValueError('Empty preview bounds')
        center = (bounds.GetMin()+bounds.GetMax())*0.5
        radius = (bounds.GetMax()-bounds.GetMin()).GetLength()*0.5
        if not math.isfinite(radius) or radius <= 0:
            raise ValueError('Invalid preview radius')
        # All new cameras/lights live only here; no Save/export of captured layers.
        stage.SetEditTarget(stage.GetSessionLayer())
        if config.get('live_bridge'):
            UsdGeom.Imageable(stage.GetPrimAtPath('/ReferenceTarget')).MakeInvisible()
        surface_diagnostic = config.get('surface_diagnostic')
        if surface_diagnostic:
            if not config.get('smoke') or not config.get('textures') or config.get('provisional_lighting'):
                raise ValueError('Surface diagnostic must remain isolated textured smoke')
            if surface_diagnostic not in ('left-handed', 'quarter-light', 'two-sided', 'emissive-surface'):
                raise ValueError('Unknown surface diagnostic')
            if surface_diagnostic == 'left-handed':
                orientations = []
                for mesh in meshes:
                    original = mesh.GetOrientationAttr().Get()
                    if original != UsdGeom.Tokens.rightHanded:
                        raise ValueError('Facing diagnostic requires the observed rightHanded baseline')
                    mesh.CreateOrientationAttr(UsdGeom.Tokens.leftHanded)
                    orientations.append({'mesh': str(mesh.GetPath()), 'before': str(original),
                                         'test': str(mesh.GetOrientationAttr().Get())})
                report(work/'preview-facing-test.json', {'session_only': True, 'mode': surface_diagnostic,
                       'orientations': orientations, 'index_or_normal_edits': False})
            if surface_diagnostic == 'two-sided':
                values = []
                for mesh in meshes:
                    original = mesh.GetDoubleSidedAttr().Get()
                    mesh.CreateDoubleSidedAttr(True)
                    values.append({'mesh': str(mesh.GetPath()), 'before': original,
                                   'test': mesh.GetDoubleSidedAttr().Get()})
                report(work/'preview-facing-test.json', {'session_only': True, 'mode': surface_diagnostic,
                       'double_sided': values, 'index_or_normal_edits': False})
            if surface_diagnostic == 'emissive-surface':
                rows = []
                for prim in stage.Traverse():
                    if not prim.IsA(UsdShade.Shader):
                        continue
                    shader = UsdShade.Shader(prim)
                    primary = shader.GetInput('diffuse_texture')
                    if not primary or not primary.Get():
                        continue
                    shader.CreateInput('emissive_mask_texture', Sdf.ValueTypeNames.Asset).Set(primary.Get())
                    shader.CreateInput('enable_emission', Sdf.ValueTypeNames.Bool).Set(True)
                    shader.CreateInput('emissive_intensity', Sdf.ValueTypeNames.Float).Set(1.0)
                    rows.append({'shader': str(prim.GetPath()), 'primary_as_emission': primary.Get().path})
                if len(rows) != 5:
                    raise ValueError('Expected five visibility-test materials')
                report(work/'preview-emissive-surface-test.json', {'session_only': True,
                       'mode': surface_diagnostic, 'assignments': rows, 'recovered_glow_claim': False})
        if config.get('provisional_lighting'):
            hypothesis = config['provisional_lighting']
            if not config.get('textures') or hypothesis['status'] != 'PROVISIONAL_RUNTIME_UNVERIFIED':
                raise ValueError('Missing explicit provisional authority/metadata')
            rows = []
            for group in hypothesis['groups']:
                path = f'/ReferenceTarget/XForms/World/Looks/source_{group["group"]:03d}/Shader'
                shader = UsdShade.Shader(stage.GetPrimAtPath(path))
                if not shader or not shader.GetInput('diffuse_texture').Get():
                    raise ValueError('Provisional group has no captured material')
                expected_primary = f'resource_{group["primary"]:04d}.a.rtex.dds'
                if Path(shader.GetInput('diffuse_texture').Get().path).name != expected_primary:
                    raise ValueError('Group/primary material association mismatch')
                image_path = str(work/group['dds'])
                shader.CreateInput('emissive_mask_texture', Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath(image_path))
                shader.CreateInput('enable_emission', Sdf.ValueTypeNames.Bool).Set(True)
                shader.CreateInput('emissive_intensity', Sdf.ValueTypeNames.Float).Set(1.0)
                rows.append({'shader': path, 'primary': group['primary'], 'secondary': group['secondary'],
                             'emissive_image': shader.GetInput('emissive_mask_texture').Get().path,
                             'enabled': shader.GetInput('enable_emission').Get(),
                             'intensity': shader.GetInput('emissive_intensity').Get()})
            if len(rows) != 5:
                raise ValueError('Expected five provisional lighting assignments')
            report(work/'preview-provisional-lighting.json', {'status': hypothesis['status'],
                   'assignments': rows, 'session_only': True, 'runtime_verification': 'PENDING'})
        if config.get('nearest_filter_diagnostic'):
            if not config.get('textures') or not config.get('smoke'):
                raise ValueError('Material filtering diagnostic requires textured smoke')
            shaders = [UsdShade.Shader(p) for p in stage.Traverse()
                       if p.IsA(UsdShade.Shader) and p.GetAttribute('inputs:diffuse_texture').HasAuthoredValueOpinion()]
            if len(shaders) != 5:
                raise ValueError('Expected exactly five captured primary-image shaders')
            rows = []
            for shader in shaders:
                value = shader.CreateInput('filter_mode', Sdf.ValueTypeNames.Int)
                value.Set(0)  # Installed AperturePBR_Model.mdl: Nearest=0, Linear=1.
                if value.Get() != 0:
                    raise ValueError('Session material filtering request not authored')
                rows.append({'shader': str(shader.GetPath()), 'filter_mode': value.Get()})
            report(work/'preview-filter-test.json', {'scope': 'anonymous session only; no source or DDS change',
                   'request': 'Nearest=0', 'authored_shaders': rows,
                   'gpu_sampler_readback': 'unavailable'})
        camera = UsdGeom.Camera.Define(stage, '/SFCPreview/Camera')
        camera.CreateClippingRangeAttr(Gf.Vec2f(max(radius/1000, 0.001), radius*100))
        camera.CreateHorizontalApertureAttr(24)
        camera.CreateVerticalApertureAttr(15)
        camera.CreateFocalLengthAttr(28)
        camera_op = camera.AddTransformOp()
        dome = UsdLux.DomeLight.Define(stage, '/SFCPreview/NeutralFill')
        dome.CreateIntensityAttr(0.7)
        key = UsdLux.DistantLight.Define(stage, '/SFCPreview/Key')
        key.CreateIntensityAttr(2.0)
        camera.CreateFStopAttr(0.0)
        key.CreateAngleAttr(1.0)
        key.AddRotateXYZOp().Set(Gf.Vec3f(-35, 35, 0))
        if surface_diagnostic == 'quarter-light':
            dome.GetIntensityAttr().Set(0.175)
            key.GetIntensityAttr().Set(0.5)
            report(work/'preview-illumination-test.json', {'session_only': True, 'mode': surface_diagnostic,
                   'before': {'dome': 0.7, 'key': 2.0},
                   'test': {'dome': dome.GetIntensityAttr().Get(), 'key': key.GetIntensityAttr().Get()},
                   'material_or_exposure_edits': False})

        def view(direction):
            eye = center+Gf.Vec3d(*direction).GetNormalized()*radius*4.5
            up = Gf.Vec3d(*config['above_up']) if direction[1] > 0.99 and direction[0] == 0 else Gf.Vec3d(0,1,0)
            camera_op.Set(Gf.Matrix4d().SetLookAt(eye, center, up).GetInverse())

        window = ui.Window('SFC live ship bridge' if config.get('live_bridge') else 'Captured ship | offline Remix preview', width=1240, height=780)
        window.setPosition(0, 0)
        with window.frame:
            with ui.VStack(spacing=5):
                appearance = 'recovered PRIMARY images; secondary/glow UNPROVEN' if config.get('textures') else 'grey diagnostic materials'
                if config.get('provisional_lighting'):
                    appearance = 'PROVISIONAL lighting masks - SFC runtime/fidelity NOT VERIFIED'
                ui.Label(f'SFC CAPTURED MESH - {count} triangles - {appearance}, NOT the game', height=26)
                KEEP['live_status']=ui.Label('Waiting for verified ship and SFC camera' if config.get('live_bridge',{}).get('game_camera') else ('LIVE kff.mod; may be enemy. Fixed external camera; waiting for verified ship.' if config.get('live_bridge') else 'Synthetic camera/lights. Geometry, winding and imported normals unchanged. Auto-closes in 2 minutes.'), height=22)
                with ui.HStack(height=30):
                    if config.get('live_bridge') and not config['live_bridge'].get('game_camera'):
                        ui.Button('Frame ship', clicked_fn=lambda: KEEP.get('frame_live',lambda:None)())
                    for label, direction in ({} if config.get('live_bridge',{}).get('game_camera') else config['views']).items():
                        ui.Button(label, clicked_fn=lambda d=direction: view(d))
                    ui.Button('Close preview', clicked_fn=lambda: app.post_quit(0))
                viewport = ViewportWidget(usd_context_name='', camera_path='/SFCPreview/Camera', resolution=(1024,640))
        KEEP.update(window=window, viewport=viewport, context=context)
        api = viewport.viewport_api
        if api.set_hd_engine('pxr', 'HdRemixRendererPlugin') != 'pxr':
            raise ValueError('Remix renderer activation request not accepted')
        view(config['views']['Angled'])
        for _ in range(120):
            await app.next_update_async()
        await retry_remix_support_async(timeout_frames=500, reason='SFC isolated preview')
        support, support_message = is_remix_supported()
        if support != RemixSupport.SUPPORTED:
            raise ValueError(f'Remix readiness not confirmed: {support_message}')
        # Published settings only: no setter, runtime override, or GPU-state claim.
        sys.path.insert(0, str(work))
        from preview_sampling_audit import collect
        report(work/'preview-sampling-audit.json', collect(carb.settings.get_settings(), (1024, 640)))
        report(work/'preview-setup.json', {'camera_path': str(api.camera_path),
               'renderer': api.render_mode, 'support': str(support),
               'bbox_min': list(bounds.GetMin()), 'bbox_max': list(bounds.GetMax()),
               'camera_matrix': [list(r) for r in camera_op.Get()], 'radius': radius})
        if config.get('live_bridge'):
            def frame_live():
                nonlocal center
                box=UsdGeom.BBoxCache(Usd.TimeCode.Default(),[UsdGeom.Tokens.default_,UsdGeom.Tokens.render]).ComputeWorldBound(stage.GetPrimAtPath('/ReferenceTarget')).ComputeAlignedRange()
                if not box.IsEmpty():center=(box.GetMin()+box.GetMax())*.5
                view(config['views']['Angled'])
            KEEP['frame_live']=frame_live
            # Live mode bypasses the offline screenshot/view cycling path.
            status.update(status='READY',triangles=count,meshes=len(meshes),session_layer_only=True,
                          mode='LIVE_WAITING_FOR_QUALIFIED_SHIP',model='kff.mod (not necessarily player)')
            UsdGeom.Imageable(stage.GetPrimAtPath('/ReferenceTarget')).MakeInvisible()
            report(work/'preview-ready.json',status)
            if config.get('fresh_scene'):
                from kit_live_scene import run_scene
                await run_scene(stage,config,app,report,lambda text:setattr(KEEP['live_status'],'text',text),camera,camera_op,api)
            else:
                from kit_live_bridge import run_live
                await run_live(stage,config,app,stage.GetPrimAtPath('/ReferenceTarget'),frame_live,report,
                               lambda text:setattr(KEEP['live_status'],'text',text),camera,camera_op,api)
            if hashlib.sha256(asset.read_bytes()).hexdigest()!=config['source_sha256']:
                raise ValueError('Scratch USD changed')
            app.post_quit(0)
            return
        # PNG is evidence of this diagnostic setup, not a faithful game scene.
        shots = [('angled', config['views']['Angled'])]
        if config['smoke']:
            shots += [('above', config['views']['Above']), ('front', config['views']['Front'])]
        for name, direction in shots:
            view(direction)
            for _ in range(45):
                await app.next_update_async()
            capture = capture_viewport_to_file(api, str(work/f'{name}.png'))
            await capture.wait_for_result()
            path = work/f'{name}.png'
            # Vendor capture completion can precede asynchronous PNG file flush.
            # Match its tests' capture drain, then bound any remaining I/O wait.
            capture_interface = omni.kit.renderer_capture.acquire_renderer_capture_interface()
            for _ in range(3):
                capture_interface.wait_async_capture()
                await app.next_update_async()
            flush_deadline = time.monotonic()+10
            while not path.is_file() and time.monotonic() < flush_deadline:
                await app.next_update_async()
            if not path.is_file() or path.stat().st_size > 8*1024*1024:
                raise ValueError('Preview PNG missing or oversized')
        if hashlib.sha256(asset.read_bytes()).hexdigest() != config['source_sha256']:
            raise ValueError('Scratch USD changed')
        status.update(status='READY', triangles=count, meshes=len(meshes), renderer_request=api.render_mode,
                      source_sha256=config['source_sha256'], stage_units=UsdGeom.GetStageMetersPerUnit(stage),
                      bbox_min=list(bounds.GetMin()), bbox_max=list(bounds.GetMax()),
                      view_directions=config['views'], above_up=config['above_up'],
                      synthetic_camera_lights=True, mesh_edits=surface_diagnostic in ('left-handed', 'two-sided'),
                      geometry_numeric_edits=False, session_layer_only=True)
        report(work/'preview-ready.json', status)
        print('SFC mesh preview READY. No game files changed.', flush=True)
        if config['smoke']:
            app.post_quit(0)
            return
        view(config['views']['Angled'])
        deadline = time.monotonic()+config['ready_seconds']
        while time.monotonic() < deadline:
            await app.next_update_async()
        app.post_quit(0)
    except Exception as exc:
        status.update(error=str(exc), traceback=traceback.format_exc()[-8000:])
        if not (work/'preview-ready.json').exists():
            report(work/'preview-ready.json', status)
        print(json.dumps(status), flush=True)
        app.post_quit(2)


asyncio.ensure_future(run())
