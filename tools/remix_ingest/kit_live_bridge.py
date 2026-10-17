"""Anonymous-layer receiver for the approved live-ship proof; no game writes."""
import json
from pathlib import Path
import time
from live_bridge import Channel, Consumer, qualify


async def run_live(stage, config, app, root, on_frame, report, on_status, camera, camera_op, api):
    from pxr import Gf, UsdGeom
    work=Path(config['work']);live=config['live_bridge']
    channel=Channel(live['channel']);consumer=Consumer();assets={};attempted=set()
    world=stage.GetPrimAtPath('/ReferenceTarget/XForms/World')
    if not world:raise ValueError('Qualified import transform hierarchy missing')
    op=UsdGeom.Xformable(world).AddTransformOp(opSuffix='sfcLive')
    imageable=UsdGeom.Imageable(root);imageable.MakeInvisible()
    deadline=time.monotonic()+config['ready_seconds'];recorded=0;failures=[];framed=False;last_epoch=None;hidden_transitions=0;was_visible=False
    log=work/'live-viewer-updates.jsonl'
    aligned=live.get('game_camera',False);camera_updates=0;camera_rejected=0;max_camera_error=0;camera_errors=[]
    try:
        with log.open('x',encoding='utf-8') as stream:
            while time.monotonic()<deadline:
                state=channel.validate()
                if state in (2,3):imageable.MakeInvisible();on_status('Disconnected — ship hidden');break
                for slot in (0,1):
                    if slot in attempted:continue
                    asset=channel.asset(slot)
                    if asset is None:continue
                    attempted.add(slot);packet,refs,owner=asset
                    try:
                        qualified=qualify(packet,refs,live['template_capture'],live['game_root'])
                        if qualified['owner']!=owner:raise ValueError('Descriptor identity mismatch')
                        assets[slot]=qualified
                        report(work/f'live-asset-{slot}-verification.json',qualified)
                    except (ValueError,OSError,KeyError) as exc:
                        failures.append({'slot':slot,'error':str(exc)})
                record=channel.sample()
                matrix=consumer.update(record[:48] if record is not None else None,assets)
                camera_error=None
                if matrix is not None and aligned:
                    try:
                        from live_camera import camera_state,apply_camera
                        points=assets[record[45]]['check_points']
                        state=camera_state(record,consumer.origin,points)
                        op.Set(Gf.Matrix4d(*[x for row in matrix for x in row]))
                        mesh_world=UsdGeom.XformCache().GetLocalToWorldTransform(world)
                        camera_error=apply_camera(state,camera,camera_op,api,points,mesh_world)
                        camera_updates+=1;max_camera_error=max(max_camera_error,camera_error)
                    except ValueError as exc:
                        camera_rejected+=1;consumer.visible=False;matrix=None
                        if len(camera_errors)<8:camera_errors.append(str(exc))
                if matrix is not None:
                    op.Set(Gf.Matrix4d(*[x for row in matrix for x in row]))
                    actual=op.Get()
                    if any(abs(actual[i][j]-matrix[i][j])>1e-9 for i in range(4) for j in range(4)):
                        raise ValueError('Live session transform readback mismatch')
                    if recorded<2700:
                        stream.write(json.dumps({'sequence':record[0],'owner':record[1],'frame':record[2],
                            'elapsed_ms':record[3],'matrix':matrix,'authored_readback_match':True,
                            'camera_projection_error_pixels':camera_error},separators=(',',':'))+'\n');recorded+=1
                    if log.stat().st_size>8*1024*1024:raise ValueError('Viewer evidence limit')
                if consumer.fresh():
                    imageable.MakeVisible()
                    on_status('LIVE selected Klingon — SFC camera, selected ship only' if aligned else 'LIVE Klingon kff.mod — may be the enemy. Frame ship if it moves out of view.')
                    if consumer.epoch!=last_epoch:framed=False;last_epoch=consumer.epoch
                    if not framed and not aligned:on_frame();framed=True
                else:
                    imageable.MakeInvisible()
                    on_status('Ship hidden — waiting for a fresh, verified observation' if not failures else 'Ship hidden — asset verification failed; preserve results')
                if was_visible and not consumer.visible:hidden_transitions+=1
                was_visible=consumer.visible
                await app.next_update_async()
    finally:
        imageable.MakeInvisible();channel.close()
        report(work/'live-viewer-result.json',{'schema':'sfc.live.viewer.v1','accepted':consumer.accepted,
            'rejected':consumer.rejected,'asset_failures':failures,'asset_epochs':len(assets),
            'records':recorded,'session_layer_only':True,'source_changes':False,
            'hidden_transitions':hidden_transitions,'authored_readback_verified':True,
            'camera_aligned':aligned,'camera_updates':camera_updates,'camera_rejected':camera_rejected,
            'camera_errors':camera_errors,'max_camera_projection_error_pixels':max_camera_error,
            'runtime_motion_camera_independence':'REQUIRES_RUNTIME_ADJUDICATION'})
