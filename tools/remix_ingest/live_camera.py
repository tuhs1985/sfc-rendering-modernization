"""Same-frame camera conversion and projection checks; no camera-mode guesses."""
import math
import struct
import sys
from pathlib import Path
component=Path(__file__).resolve().parents[1]/'m1_component'
if component.is_dir():sys.path.insert(0,str(component))
from analyze_live_camera import inverse, multiply, native_matrix, project


def camera_state(record, origin, points):
    if len(record)!=96 or record[48]!=1:raise ValueError('Protocol2 camera observation required')
    if any(record[42:45]):raise ValueError('Unsupported native math dispatch')
    view=native_matrix(record[49:66]);projection=native_matrix(record[66:83])
    x,y,width,height,half_w,half_h=struct.unpack('<6f',struct.pack('<6I',*record[83:89]))
    if (not all(math.isfinite(v) for v in (x,y,width,height,half_w,half_h)) or
        min(x,y)<0 or not 1<=width<=4096 or not 1<=height<=4096 or
        abs(width-round(width))>1e-3 or abs(height-round(height))>1e-3 or
        abs(half_w-width/2)>1e-3 or abs(half_h-height/2)>1e-3):raise ValueError('Unsupported viewport')
    if view[3]!=[0,0,0,1]:raise ValueError('View must be affine')
    for i in range(3):
        for j in range(3):
            if abs(sum(view[i][k]*view[j][k] for k in range(3))-(i==j))>1e-3:raise ValueError('Nonrigid view')
    determinant=(view[0][0]*(view[1][1]*view[2][2]-view[1][2]*view[2][1])-
                 view[0][1]*(view[1][0]*view[2][2]-view[1][2]*view[2][0])+
                 view[0][2]*(view[1][0]*view[2][1]-view[1][1]*view[2][0]))
    if abs(determinant-1)>1e-3:raise ValueError('Unqualified reflected camera')
    # Admit the inspected perspective form only. No silent orthographic fallback.
    if (max(abs(projection[3][i]-[0,0,-1,0][i]) for i in range(4))>1e-5 or
        any(abs(projection[i][j])>1e-5 for i,j in ((0,1),(0,3),(1,0),(1,3),(2,0),(2,1))) or
        projection[0][0]<=0 or projection[1][1]<=0):raise ValueError('Unqualified projection form')
    a,b=projection[2][2:4]
    if abs(a-1)<1e-9 or abs(a+1)<1e-9:raise ValueError('Degenerate clipping planes')
    near,far=b/(a-1),b/(a+1)
    if not 0<near<far or far>1e9:raise ValueError('Unsupported clipping range')
    if abs((projection[1][1]/projection[0][0])/(width/height)-1)>1e-4:raise ValueError('Projection/viewport aspect mismatch')
    viewport=[[half_w,0,0,x+half_w],[0,-half_h,0,y+half_h],[0,0,1,0],[0,0,0,1]]
    model=native_matrix(record[8:25]);composed=native_matrix(record[25:42])
    expected=multiply(multiply(multiply(viewport,projection),view),model)
    pixel_error=0
    for point in points:
        p=project(expected,point);q=project(composed,point)
        pixel_error=max(pixel_error,abs(p[0]-q[0]),abs(p[1]-q[1]))
    if pixel_error>.25:raise ValueError('Native independent camera composition differs by >.25pixel')
    inv=inverse(view);scale=100.0
    transform=tuple(tuple(inv[j][i] for j in range(3))+(0.,) for i in range(3))+(tuple((inv[i][3]-origin[i])*scale for i in range(3))+(1.,),)
    aperture=20.;focal=projection[0][0]*aperture/2;vertical=2*focal/projection[1][1]
    return {'camera_transform':transform,'focal':focal,'horizontal_aperture':aperture,
            'vertical_aperture':vertical,'horizontal_offset':projection[0][2]*aperture/2,
            'vertical_offset':projection[1][2]*vertical/2,'near':near*scale,'far':far*scale,
            'viewport':[x,y,int(width),int(height)],'native_composition_pixel_error':pixel_error,
            'native_model':model,'native_composed':composed,'origin':origin}


def apply_camera(state, camera, camera_op, api, points, mesh_world):
    from pxr import Gf, Usd
    camera_op.Set(Gf.Matrix4d(*[v for row in state['camera_transform'] for v in row]))
    camera.CreateHorizontalApertureAttr(state['horizontal_aperture'])
    camera.CreateVerticalApertureAttr(state['vertical_aperture'])
    camera.CreateHorizontalApertureOffsetAttr(state['horizontal_offset'])
    camera.CreateVerticalApertureOffsetAttr(state['vertical_offset'])
    camera.CreateFocalLengthAttr(state['focal'])
    camera.CreateClippingRangeAttr(Gf.Vec2f(state['near'],state['far']))
    x,y,w,h=state['viewport'];api.set_texture_resolution((w,h))
    actual=camera.GetCamera(Usd.TimeCode.Default()).frustum
    vp=actual.ComputeViewMatrix()*actual.ComputeProjectionMatrix()
    error=0
    for p in points:
        # Independent effective USD scene hierarchy, not our assumed model formula.
        out=(Gf.Vec4d(*p,1)*mesh_world)*vp
        if abs(out[3])<1e-10:raise ValueError('USD point on projection plane')
        px=x+(out[0]/out[3]+1)*w/2;py=y+(1-out[1]/out[3])*h/2
        native=project(state['native_composed'],p)
        error=max(error,abs(px-native[0]),abs(py-native[1]))
    if error>.25:raise ValueError('USD camera projection differs from native by >.25pixel')
    return error
