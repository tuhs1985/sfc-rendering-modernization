"""Author exact packet arrays into the live session layer, without imported USD."""

def build_asset(stage,data):
    from pxr import Gf,Sdf,UsdGeom,UsdShade,Vt
    path='/Library/a_'+data['asset_sha256']
    if stage.GetPrimAtPath(path):raise ValueError('Unexpected existing asset outside qualified cache')
    UsdGeom.Xform.Define(stage,path)
    mesh=UsdGeom.Mesh.Define(stage,path+'/Mesh')
    points=[Gf.Vec3f(*p) for p in data['points']]
    indices=[data['corners'][start+j][0] for _,start in data['polygons'] for j in range(3)]
    normals=[Gf.Vec3f(*data['corners'][start+j][1]) for _,start in data['polygons'] for j in range(3)]
    uvs=[Gf.Vec2f(*data['corners'][start+j][2]) for _,start in data['polygons'] for j in range(3)]
    mesh.CreatePointsAttr(points);mesh.CreateFaceVertexCountsAttr([3]*len(data['polygons']))
    mesh.CreateFaceVertexIndicesAttr(indices);mesh.CreateNormalsAttr(normals);mesh.SetNormalsInterpolation('faceVarying')
    mesh.CreateSubdivisionSchemeAttr('none');mesh.CreateOrientationAttr('rightHanded')
    st=UsdGeom.PrimvarsAPI(mesh).CreatePrimvar('st',Sdf.ValueTypeNames.TexCoord2fArray,'faceVarying');st.Set(uvs)
    if (list(mesh.GetPointsAttr().Get())!=points or list(mesh.GetFaceVertexIndicesAttr().Get())!=indices or
        list(mesh.GetNormalsAttr().Get())!=normals or list(st.Get())!=uvs):raise ValueError('Authored mesh readback mismatch')
    for assignment in data['assignments']:
        group=assignment['group'];material=UsdShade.Material.Define(stage,path+f'/Looks/g_{group}')
        shader=UsdShade.Shader.Define(stage,str(material.GetPath())+'/Shader')
        shader.SetSourceAsset(Sdf.AssetPath('AperturePBR_Opacity.mdl'),'mdl')
        shader.SetSourceAssetSubIdentifier('AperturePBR_Opacity','mdl')
        output=shader.CreateOutput('out',Sdf.ValueTypeNames.Token)
        for kind in ('surface','displacement','volume'):
            material.CreateOutput('mdl:'+kind,Sdf.ValueTypeNames.Token).ConnectToSource(output)
        shader.CreateInput('diffuse_color_constant',Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(1))
        shader.CreateInput('enable_emission',Sdf.ValueTypeNames.Bool).Set(False)
        shader.CreateInput('opacity_constant',Sdf.ValueTypeNames.Float).Set(1.)
        shader.CreateInput('encoding',Sdf.ValueTypeNames.Int).Set(2)
        primary=assignment['primary']
        if primary:
            texture=Sdf.AssetPath(primary['dds'])
            shader.CreateInput('diffuse_texture',Sdf.ValueTypeNames.Asset).Set(texture)
            if shader.GetInput('diffuse_texture').Get().path.replace('\\','/')!=texture.path.replace('\\','/'):
                raise ValueError('Material image readback mismatch')
        faces=[i for i,(g,_) in enumerate(data['polygons']) if g==group]
        subset=UsdGeom.Subset.CreateGeomSubset(mesh,'g_'+str(group),'face',Vt.IntArray(faces),'materialBind','partition')
        binding=UsdShade.MaterialBindingAPI.Apply(subset.GetPrim());binding.Bind(material)
        if binding.ComputeBoundMaterial()[0].GetPath()!=material.GetPath():raise ValueError('Material binding readback mismatch')
        if list(subset.GetIndicesAttr().Get())!=faces:raise ValueError('Group readback mismatch')
    return path


def make_instance(stage,index,asset_path):
    from pxr import UsdGeom
    path='/Ships/owner_'+str(index)
    if stage.GetPrimAtPath(path):stage.RemovePrim(path)
    prim=UsdGeom.Xform.Define(stage,path).GetPrim();prim.GetReferences().AddInternalReference(asset_path)
    # Root transform belongs to this owner, asset geometry/materials remain shared.
    op=UsdGeom.Xformable(prim).AddTransformOp(opSuffix='sfcLive')
    return prim,op
