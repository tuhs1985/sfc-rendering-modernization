"""Read-only comparison of normal Remix capture to original neutral replay.

Uses already installed USD libraries only;does not start Toolkit or render.
"""
from itertools import permutations
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import numpy as np
from PIL import Image
from run_offline import ROOT,read_replay,digest

USD=Path(r'C:\Project\RTXRemix\extscache\omni.usd.libs-1.0.3+6312fa25.wx64.r.cp312')


def match_corners(actual,expected):
    """Numeric tolerance,not decimal rounding at a UV half-boundary.

    USD export reverses winding and converts texture origin. Detect/document the
    conversion here ONLY;the D3D9 input and source captures remain untouched.
    """
    def position_key(face):return tuple(sorted(tuple(round(float(x),5) for x in v[:3]) for v in face))
    for flip in (False,True):
        available={}
        for face in expected:available.setdefault(position_key(face),[]).append(np.asarray(face))
        error=0.;valid=True
        for face in actual:
            face=np.array(face,dtype=float)
            if flip:face[:,7]=1-face[:,7]
            key=position_key(face);best=None
            for i,candidate in enumerate(available.get(key,[])):
                e=min(float(np.max(np.abs(face[list(order)]-candidate))) for order in permutations(range(3)))
                if best is None or e<best[0]:best=(e,i)
            if best is None or best[0]>1e-5:valid=False;break
            error=max(error,best[0]);available[key].pop(best[1])
        if valid and all(not rows for rows in available.values()):return flip,error
    return None


def decoded(path):
    with Image.open(path) as image:
        image.load();return image.size,hashlib.sha256(image.convert('RGBA').tobytes()).hexdigest()


def inspect(folder,source_index=0):
    folder=Path(folder).resolve();folder.relative_to(ROOT/'artifacts/d3d9-intercept/runs')
    if not USD.is_dir():raise ValueError('Installed USD read-only parser unavailable')
    dll=os.add_dll_directory(str(USD/'bin'));sys.path.insert(0,str(USD))
    from pxr import Usd,UsdGeom,UsdShade,Gf
    source=read_replay(folder/'scene.bin');manifest=json.loads((folder/'scene.json').read_text())
    path=folder/'rtx-remix/captures/proof.usda'
    if not path.is_file():raise ValueError('No actual normal-interception scene capture')
    stage=Usd.Stage.Open(str(path))
    if not stage:raise ValueError('Runtime USD capture cannot open')
    expected={}
    for identity,material,first,count in source['groups']:
        faces=[]
        for start in range(first,first+count,3):
            corners=[source['vertices'][source['indices'][start+j]] for j in range(3)]
            faces.append(corners)
        expected[identity]=(material,faces)
    matched=set();records=[];projection_error=0;raw_projection_error=0;uv_modes=set();face_count=0
    cache=UsdGeom.XformCache(Usd.TimeCode.Default())
    camera=UsdGeom.Camera(stage.GetPrimAtPath('/RootNode/cameras/Camera'))
    if not camera:raise ValueError('Capture missing camera')
    captured_camera=camera.GetCamera()
    raw_camera_vp=captured_camera.frustum.ComputeViewMatrix()*captured_camera.frustum.ComputeProjectionMatrix()
    frame=manifest['frames'][source_index];native=np.array(frame['native_composed'])
    x,y,w,h=frame['viewport']
    actual_view=np.asarray(captured_camera.frustum.ComputeViewMatrix()).T
    actual_projection=np.asarray(captured_camera.frustum.ComputeProjectionMatrix()).T
    view_error=float(np.max(np.abs(actual_view-np.asarray(frame['view']))))
    horizontal_error=abs(float(actual_projection[0,0])-frame['projection'][0][0])
    if view_error>1e-4 or horizontal_error>1e-5:raise ValueError('Exported view/horizontal projection mismatch')
    vertical_authored=camera.GetVerticalApertureAttr().HasAuthoredValueOpinion()
    if not vertical_authored:
        # Explicit analysis-only reconstruction from the independent source
        # viewport. Do NOT edit the capture or claim the missing field was exported.
        captured_camera.verticalAperture=captured_camera.horizontalAperture/(w/h)
    camera_vp=captured_camera.frustum.ComputeViewMatrix()*captured_camera.frustum.ComputeProjectionMatrix()
    for prim in stage.Traverse():
        if not str(prim.GetPath()).startswith('/RootNode/instances/') or not prim.IsA(UsdGeom.Mesh):continue
        mesh=UsdGeom.Mesh(prim);points=mesh.GetPointsAttr().Get();indices=list(mesh.GetFaceVertexIndicesAttr().Get());counts=list(mesh.GetFaceVertexCountsAttr().Get())
        if not counts or any(n!=3 for n in counts):raise ValueError('Captured non-triangle group')
        normals=mesh.GetNormalsAttr().Get();normal_mode=mesh.GetNormalsInterpolation()
        uv=UsdGeom.PrimvarsAPI(mesh).GetPrimvar('st');coords=uv.ComputeFlattened();uv_mode=uv.GetInterpolation()
        observed=[]
        for offset in range(0,len(indices),3):
            corners=[]
            for j in range(3):
                ci=offset+j;vi=indices[ci];normal=normals[ci if normal_mode=='faceVarying' else vi]
                tex=coords[ci if uv_mode=='faceVarying' else vi]
                corners.append((*points[vi],*normal,float(tex[0]),float(tex[1])))
            observed.append(corners)
        matches=[]
        for identity,(material,faces) in expected.items():
            if identity in matched or len(faces)!=len(observed):continue
            result=match_corners(observed,faces)
            if result is not None:matches.append((identity,material,*result))
        if not matches:
            # Preserve a small numeric diagnostic rather than relaxing tolerance.
            vertices=[]
            for ci,vi in enumerate(indices):
                n=normals[ci if normal_mode=='faceVarying' else vi];t=coords[ci if uv_mode=='faceVarying' else vi]
                vertices.append([*points[vi],*n,*t])
            p=np.array(vertices,dtype=float)
            diagnostics=[]
            for identity,material,first,count in source['groups']:
                if count!=len(indices):continue
                q=np.array([source['vertices'][i] for i in source['indices'][first:first+count]])
                distances=np.max(np.abs(p[:,None,:3]-q[None,:,:3]),axis=2);nearest=distances.argmin(axis=1)
                diagnostics.append(dict(group=identity,position=float(distances.min(axis=1).max()),
                    normal=float(np.max(np.abs(p[:,3:6]-q[nearest,3:6]))),
                    uv=float(np.max(np.abs(p[:,6:8]-q[nearest,6:8])))))
            (folder/'unmatched-group.json').write_text(json.dumps(dict(mesh=str(prim.GetPath()),candidates=diagnostics),indent=2))
            raise ValueError('Captured geometry/normal/UV group unmatched;see unmatched-group.json')
        identity,material,flip,attribute_error=matches[0];matched.add(identity);uv_modes.add('USD-exporter V flip' if flip else 'raw UV')
        binding=prim
        while binding and not binding.GetRelationship('material:binding').GetTargets():binding=binding.GetParent()
        targets=binding.GetRelationship('material:binding').GetTargets() if binding else []
        mat=UsdShade.Material(stage.GetPrimAtPath(targets[0])) if len(targets)==1 else None
        images=[]
        if mat:
            for child in Usd.PrimRange(mat.GetPrim()):
                attr=child.GetAttribute('inputs:diffuse_texture')
                if attr and attr.Get():
                    value=attr.Get();resolved=Path(value.resolvedPath)
                    if not resolved.is_file():raise ValueError('Captured diffuse image missing')
                    resolved.resolve().relative_to(folder)
                    images.append(decoded(resolved))
        expected_texture=folder/f'texture-{material}.bin';raw=expected_texture.read_bytes()
        width,height=np.frombuffer(raw,dtype='<u4',count=4)[1:3]
        bgra=np.frombuffer(raw,dtype=np.uint8,offset=16).reshape(int(height),int(width),4)
        rgba=bgra[:,:,[2,1,0,3]].tobytes();expected_image=((int(width),int(height)),hashlib.sha256(rgba).hexdigest())
        if expected_image not in images:raise ValueError('Captured material/image assignment differs for group'+str(identity))
        world=cache.GetLocalToWorldTransform(prim)
        # Check every exported vertex against the captured SFC composed projection,
        # through the ACTUAL composed runtime-exported hierarchy/camera.
        for point in points:
            actual=(Gf.Vec4d(*point,1)*world)*camera_vp
            raw_actual=(Gf.Vec4d(*point,1)*world)*raw_camera_vp
            p=native@np.array([*point,1]);expected_xy=p[:2]/p[3]
            actual_xy=np.array([x+(float(actual[0]/actual[3])+1)*w/2,y+(1-float(actual[1]/actual[3]))*h/2])
            projection_error=max(projection_error,float(np.max(np.abs(actual_xy-expected_xy))))
            raw_xy=np.array([x+(float(raw_actual[0]/raw_actual[3])+1)*w/2,y+(1-float(raw_actual[1]/raw_actual[3]))*h/2])
            raw_projection_error=max(raw_projection_error,float(np.max(np.abs(raw_xy-expected_xy))))
        face_count+=len(counts);records.append(dict(group=identity,triangles=len(counts),material=material,uv_export_flip=flip,max_attribute_error=attribute_error))
    if matched!=set(expected) or face_count!=len(source['indices'])//3:raise ValueError('Missing/extra captured ship groups')
    if projection_error>.25:raise ValueError('Captured camera/object projection error >.25pixel:'+str(projection_error))
    result=dict(result='NORMAL_D3D9_REMIX_CAPTURE_MATCH',groups=records,triangles=face_count,
        source_index=source_index,source_frame=frame['frame'],max_projection_error_pixels=projection_error,
        raw_export_projection_error_pixels=raw_projection_error,vertical_aperture_authored=vertical_authored,
        camera_view_error=view_error,horizontal_projection_error=horizontal_error,
        camera_status='FULL_EXPORT' if vertical_authored else 'PARTIAL_EXPORT_VERTICAL_RECONSTRUCTED_FROM_SOURCE_VIEWPORT_ANALYSIS_ONLY',
        uv_conventions=sorted(uv_modes),capture_sha256=digest(path),replay_sha256=digest(folder/'scene.bin'),
        sdk_registration=False,usd_parser_version=list(Usd.GetVersion()),scope='geometry/primary image/camera capture;not appearance or live game integration')
    result['analysis_source_sha256']=digest(Path(__file__))
    (folder/'capture-comparison.json').write_text(json.dumps(result,indent=2))
    _=dll
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('folder',type=Path);parser.add_argument('--source-index',type=int,default=0);args=parser.parse_args()
    print(json.dumps(inspect(args.folder,args.source_index),indent=2))
