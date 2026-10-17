"""Bounded fresh scene receiver in installed Kit; all geometry in session layer."""
import asyncio
import json
from pathlib import Path
import time
from live_scene import SceneChannel,SceneConsumer,ImageStore,qualify_mesh,MEMORY_LIMIT
from live_camera import camera_state,apply_camera
from fresh_mesh_usd import build_asset,make_instance


async def run_scene(stage,config,app,report,on_status,camera,camera_op,api):
    from pxr import Gf,UsdGeom
    work=Path(config['work']);live=config['live_bridge'];channel=SceneChannel(live['channel'])
    consumer=SceneConsumer();images=ImageStore(live['game_root'],work/'live-images')
    assets={};cache={};instances={};instance_revisions={};failures=[];pending={};seen_generations={}
    counts={};accepted=0;camera_rejected=0;max_error=0.;bytes_written=0;hidden=0;warning=False;saturated=False
    total_mesh_memory=0;deadline=time.monotonic()+config['ready_seconds'];latest_camera=None
    UsdGeom.Xform.Define(stage,'/Library');UsdGeom.Imageable(stage.GetPrimAtPath('/Library')).MakeInvisible()
    UsdGeom.Xform.Define(stage,'/Ships').AddScaleOp().Set(Gf.Vec3f(100))
    # One image/packet preparation task at a time, fixed transfer slots provide backpressure.
    task=None;transfer=None;screenshot=False
    try:
        with (work/'live-viewer-updates.jsonl').open('x',encoding='utf-8') as stream:
            while time.monotonic()<deadline:
                if channel.validate() in (2,3):break
                if task is not None and task.done():
                    slot,generation,revision,owner,packet,refs=transfer
                    data=None
                    try:
                        data=task.result()
                        if data['header'][4]!=owner or revision in assets:raise ValueError('Transfer owner/revision identity')
                        signature=data['asset_sha256'];memory=0 if signature in cache else data['memory_bytes']
                        if total_mesh_memory+memory+images.memory>MEMORY_LIMIT:raise ValueError('Viewer asset memory cap')
                        if signature not in cache:
                            cache[signature]=build_asset(stage,data);total_mesh_memory+=memory
                        # Keep only render/checkpoint metadata after authoring, not Python mesh copies.
                        manifest={k:v for k,v in data.items() if k not in ('points','corners','polygons','refs')}
                        manifest['resource_associations']=data['refs']
                        manifest['revision']=revision;manifest['geometry_readback_verified']=True
                        payload=(json.dumps(manifest,allow_nan=False,indent=2)+'\n').encode()
                        if len(payload)>512*1024:raise ValueError('Asset manifest bound')
                        with (work/f'live-asset-{revision}-verification.json').open('xb') as output:output.write(payload)
                        assets[revision]={'header':data['header'],'used_points':data['used_points'],
                            'asset_sha256':signature,'asset_path':cache[signature]}
                    except (ValueError,OSError,KeyError,RuntimeError) as exc:
                        if data is not None and data['asset_sha256'] not in cache:
                            stage.RemovePrim('/Library/a_'+data['asset_sha256'])
                        if len(failures)<64:failures.append({'revision':revision,'error':str(exc)})
                    finally:
                        channel.acknowledge(slot,generation);seen_generations[slot]=generation;task=None;transfer=None
                if task is None:
                    for slot in range(4):
                        payload=channel.asset_transfer(slot)
                        if payload is None:continue
                        generation,revision,owner,packet,refs=payload
                        if seen_generations.get(slot)==generation:continue
                        transfer=(slot,generation,revision,owner,packet,refs)
                        task=asyncio.ensure_future(asyncio.to_thread(qualify_mesh,packet,refs,images));break
                updates=[]
                for index in range(32):
                    r=channel.sample_owner(index)
                    if r is not None and r[0]>consumer.last.get(index,0):
                        # Do not consume an update before its asset arrives; retirement is immediate.
                        if r[4]!=1 or r[7] in assets:pending[index]=r
                        else:consumer.seen.pop(index,None)
                    r=pending.pop(index,None)
                    if r is None:continue
                    matrix=consumer.update(r,assets)
                    if matrix is None:continue
                    data=assets[r[7]]
                    try:
                        if instance_revisions.get(index)!=r[7]:
                            instances[index]=make_instance(stage,index,data['asset_path']);instance_revisions[index]=r[7]
                        prim,op=instances[index];op.Set(Gf.Matrix4d(*[x for row in matrix for x in row]))
                        state=camera_state(r,consumer.origin,data['used_points'])
                        # Check each owner using its own same-frame captured camera, then select newest camera below.
                        err=apply_camera(state,camera,camera_op,api,data['used_points'],UsdGeom.XformCache().GetLocalToWorldTransform(prim))
                        max_error=max(max_error,err)
                        candidate=(r[2],state,data['used_points'],UsdGeom.XformCache().GetLocalToWorldTransform(prim))
                        if latest_camera is None or r[2]>=latest_camera[0]:latest_camera=candidate
                        if any(abs(op.Get()[i][j]-matrix[i][j])>1e-9 for i in range(4) for j in range(4)):raise ValueError('Instance matrix readback')
                        accepted+=1
                        if counts.get(index,0)<2700:
                            row=json.dumps(dict(sequence=r[0],owner=r[1],slot=index,revision=r[7],frame=r[2],elapsed_ms=r[3],
                                matrix=matrix,camera_projection_error_pixels=err,asset_sha256=data['asset_sha256']),separators=(',',':'))+'\n'
                            if bytes_written+len(row)<=16*1024*1024:
                                stream.write(row);bytes_written+=len(row);counts[index]=counts.get(index,0)+1
                            else:saturated=True
                    except (ValueError,RuntimeError) as exc:
                        consumer.seen.pop(index,None);camera_rejected+=1
                        if len(failures)<64:failures.append({'owner':r[1],'error':str(exc)})
                # Earlier owner checks may temporarily author older camera state. Restore latest accepted one.
                if latest_camera is not None:
                    _,state,points,world=latest_camera
                    apply_camera(state,camera,camera_op,api,points,world)
                visible=0
                for index,(prim,_) in instances.items():
                    item=UsdGeom.Imageable(prim)
                    if consumer.fresh(index):item.MakeVisible();visible+=1
                    else:
                        if item.GetVisibilityAttr().Get()!='invisible':hidden+=1
                        item.MakeInvisible()
                warning=bytes_written>=8*1024*1024 or images.bytes>=64*1024*1024
                on_status(f'LIVE {visible} ships / {len(cache)} fresh mesh assets — primary textures; original SFC camera')
                if config.get('live_replay') and visible>=2 and accepted>=20 and not screenshot:
                    from omni.kit.viewport.utility import capture_viewport_to_file
                    capture=capture_viewport_to_file(api,str(work/'fresh-scene-replay.png'));await capture.wait_for_result()
                    screenshot=True
                await app.next_update_async()
    finally:
        # Await bounded file/decode work before freeing shared channel/storage.
        if task is not None:
            try:await task
            except Exception:pass
        for prim,_ in instances.values():UsdGeom.Imageable(prim).MakeInvisible()
        channel.close()
        report(work/'live-viewer-result.json',dict(schema='sfc.live.scene.v3',accepted=accepted,rejected=consumer.rejected,
            camera_updates=accepted,camera_rejected=camera_rejected,max_camera_projection_error_pixels=max_error,
            asset_epochs=len(assets),unique_assets=len(cache),owners=len(instances),asset_failures=failures,
            hidden_transitions=hidden,records=sum(counts.values()),log_bytes=bytes_written,image_bytes=images.bytes,
            asset_memory_bytes=images.memory+total_mesh_memory,warning=warning,saturated=saturated,
            session_layer_only=True,source_changes=False,template_loaded=False,geometry_readback_verified=True))
