// Standalone SDK experiment only. Never imported into the SFC observer.
#pragma once
#include <vector>
#include <algorithm>
#include <cstring>
#include <d3dcompiler.h>
#ifdef SFC_TRIPLET_PROBE
#include "ship_triplet_fixture.h"
#endif
static void renderCoverage(remixapi_Interface& r,IDirect3DDevice9Ex* device){
 ComPtr<ID3D11Device> consumer;ComPtr<ID3D11DeviceContext> consumerContext;const D3D_FEATURE_LEVEL level=D3D_FEATURE_LEVEL_10_1;
 hr("coverage_native10_1",D3D11CreateDevice(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,0,&level,1,D3D11_SDK_VERSION,&consumer,nullptr,&consumerContext));
 struct Output{D3DFORMAT format;remixapi_dxvk_CopyRenderingOutputType type;const char* name;ComPtr<IDirect3DSurface9> gpu,cpu;ComPtr<IDirect3DTexture9> imported;ComPtr<ID3D11Texture2D> native,staging;};
 Output outputs[]={{D3DFMT_A8R8G8B8,REMIXAPI_DXVK_COPY_RENDERING_OUTPUT_TYPE_FINAL_COLOR,"color",{},{},{},{},{}},
  {D3DFMT_R32F,REMIXAPI_DXVK_COPY_RENDERING_OUTPUT_TYPE_DEPTH,"depth",{},{},{},{},{}},
  {D3DFMT_R32F,REMIXAPI_DXVK_COPY_RENDERING_OUTPUT_TYPE_OBJECT_PICKING,"picking",{},{},{},{},{}}};
 uint64_t sharedHandles[3]{};unsigned outputIndex=0;
 for(auto& o:outputs){
  D3D11_TEXTURE2D_DESC d{};d.Width=d.Height=256;d.MipLevels=d.ArraySize=1;d.SampleDesc.Count=1;d.Format=o.format==D3DFMT_R32F?DXGI_FORMAT_R32_FLOAT:DXGI_FORMAT_B8G8R8A8_UNORM;d.BindFlags=D3D11_BIND_RENDER_TARGET|D3D11_BIND_SHADER_RESOURCE;d.MiscFlags=D3D11_RESOURCE_MISC_SHARED;
  hr("coverage_native_shared",consumer->CreateTexture2D(&d,nullptr,&o.native));ComPtr<IDXGIResource> resource;hr("coverage_native_dxgi",o.native.As(&resource));HANDLE handle=nullptr;hr("coverage_native_handle",resource->GetSharedHandle(&handle));
  hr("coverage_reverse_import",device->CreateTexture(256,256,1,D3DUSAGE_RENDERTARGET,o.format,D3DPOOL_DEFAULT,&o.imported,&handle));hr("coverage_import_surface",o.imported->GetSurfaceLevel(0,&o.gpu));
#ifdef SFC_TRIPLET_PROBE
  sharedHandles[outputIndex]=ship_triplet::canonicalHandle(handle);
#endif
  ++outputIndex;
  d.BindFlags=d.MiscFlags=0;d.Usage=D3D11_USAGE_STAGING;d.CPUAccessFlags=D3D11_CPU_ACCESS_READ;hr("coverage_native_staging",consumer->CreateTexture2D(&d,nullptr,&o.staging));
  hr("coverage_readback",device->CreateOffscreenPlainSurface(256,256,o.format,D3DPOOL_SYSTEMMEM,&o.cpu,nullptr));
 }
#ifndef SFC_TRIPLET_PROBE
 (void)sharedHandles;
#else
 std::unique_ptr<ship_triplet::Publisher> triplet;
 if(GetEnvironmentVariableW(L"SFC_RETURN_TRIPLET",nullptr,0))triplet=std::make_unique<ship_triplet::Publisher>(consumer.Get(),sharedHandles);
#endif
 ComPtr<ID3D11Texture2D> decoded,decodedCPU;D3D11_TEXTURE2D_DESC md{};md.Width=md.Height=256;md.MipLevels=md.ArraySize=1;md.SampleDesc.Count=1;md.Format=DXGI_FORMAT_R32_UINT;md.BindFlags=D3D11_BIND_RENDER_TARGET;
 hr("coverage_id_decode_target",consumer->CreateTexture2D(&md,nullptr,&decoded));ComPtr<ID3D11RenderTargetView> decodedRT;hr("coverage_id_decode_view",consumer->CreateRenderTargetView(decoded.Get(),nullptr,&decodedRT));md.BindFlags=0;md.Usage=D3D11_USAGE_STAGING;md.CPUAccessFlags=D3D11_CPU_ACCESS_READ;hr("coverage_id_decode_staging",consumer->CreateTexture2D(&md,nullptr,&decodedCPU));
 ComPtr<ID3D11ShaderResourceView> idSRV;hr("coverage_id_srv",consumer->CreateShaderResourceView(outputs[2].native.Get(),nullptr,&idSRV));
 const char* vcode="float4 main(uint i:SV_VertexID):SV_Position{float2 p[3]={float2(-1,-1),float2(-1,3),float2(3,-1)};return float4(p[i],0,1);}";
 const char* pcode="Texture2D<float> ids:register(t0);uint main(float4 p:SV_Position):SV_Target{return asuint(ids.Load(int3(int2(p.xy),0)));}";
 ComPtr<ID3DBlob> vb,pb;ComPtr<ID3D11VertexShader> vs;ComPtr<ID3D11PixelShader> ps;
 hr("coverage_id_vs_compile",D3DCompile(vcode,strlen(vcode),nullptr,nullptr,nullptr,"main","vs_4_1",0,0,&vb,nullptr));hr("coverage_id_ps_compile",D3DCompile(pcode,strlen(pcode),nullptr,nullptr,nullptr,"main","ps_4_1",0,0,&pb,nullptr));hr("coverage_id_vs",consumer->CreateVertexShader(vb->GetBufferPointer(),vb->GetBufferSize(),nullptr,&vs));hr("coverage_id_ps",consumer->CreatePixelShader(pb->GetBufferPointer(),pb->GetBufferSize(),nullptr,&ps));
 D3D11_RASTERIZER_DESC rd{};rd.FillMode=D3D11_FILL_SOLID;rd.CullMode=D3D11_CULL_NONE;rd.DepthClipEnable=TRUE;ComPtr<ID3D11RasterizerState> raster;hr("coverage_id_raster",consumer->CreateRasterizerState(&rd,&raster));
 ComPtr<IDirect3DQuery9> done;hr("coverage_event",device->CreateQuery(D3DQUERYTYPE_EVENT,&done));
 remixapi_Float4D clear{-1234,0,0,0},zero{};
 api("coverage_clear_depth",r.dxvk_SetDefaultOutput(REMIXAPI_DXVK_COPY_RENDERING_OUTPUT_TYPE_DEPTH,&clear));
 api("coverage_clear_id",r.dxvk_SetDefaultOutput(REMIXAPI_DXVK_COPY_RENDERING_OUTPUT_TYPE_OBJECT_PICKING,&zero));
 api("coverage_prime_picking_no_sample",r.dxvk_CopyRenderingOutput(outputs[2].gpu.Get(),outputs[2].type));wait9(done.Get());
 remixapi_HardcodedVertex control[3]{};const float xy[3][2]={{-.7f,-.7f},{0,.7f},{.7f,-.7f}};uint32_t ci[]={0,1,2};
 for(unsigned i=0;i<3;++i){control[i].position[0]=xy[i][0];control[i].position[1]=xy[i][1];control[i].normal[2]=-1;control[i].color=0xFFFFFFFF;}
 remixapi_MeshInfoSurfaceTriangles ct{};ct.vertices_values=control;ct.vertices_count=3;ct.indices_values=ci;ct.indices_count=3;
 remixapi_MeshInfo cm{};cm.sType=REMIXAPI_STRUCT_TYPE_MESH_INFO;cm.hash=0x534643C001;cm.surfaces_count=1;cm.surfaces_values=&ct;
 remixapi_MeshHandle controlMesh=nullptr,ship=nullptr;api("coverage_control_mesh",r.CreateMesh(&cm,&controlMesh));
 std::ifstream input("coverage-mesh.bin",std::ios::binary|std::ios::ate);if(!input||input.tellg()>2*1024*1024)throw std::runtime_error("coverage bounded mesh input");input.seekg(0);
 uint32_t h[4]{};float fit[4]{};input.read(reinterpret_cast<char*>(h),sizeof(h));input.read(reinterpret_cast<char*>(fit),sizeof(fit));
 if(h[0]!=0x53464347||h[1]!=1||!h[2]||h[2]>32768||h[2]%3||h[3]!=h[2])throw std::runtime_error("coverage mesh header");
 for(float v:fit)if(!std::isfinite(v))throw std::runtime_error("coverage nonfinite fit");if(fit[3]<=0)throw std::runtime_error("coverage fit");
 std::vector<remixapi_HardcodedVertex> vertices(h[2]);std::vector<uint32_t> indices(h[2]);
 for(unsigned i=0;i<h[2];++i){float v[8]{};input.read(reinterpret_cast<char*>(v),sizeof(v));for(float f:v)if(!std::isfinite(f))throw std::runtime_error("coverage nonfinite vertex");std::memcpy(vertices[i].position,v,12);std::memcpy(vertices[i].normal,v+3,12);std::memcpy(vertices[i].texcoord,v+6,8);vertices[i].color=0xFFFFFFFF;indices[i]=i;}
 if(!input||input.peek()!=EOF)throw std::runtime_error("coverage incomplete mesh");
 uint32_t cameraHeader[4]{};float replay[28]{};std::ifstream cameraFile("coverage-camera.bin",std::ios::binary);cameraFile.read(reinterpret_cast<char*>(cameraHeader),sizeof(cameraHeader));cameraFile.read(reinterpret_cast<char*>(replay),sizeof(replay));
 if(!cameraFile||cameraFile.peek()!=EOF||cameraHeader[0]!=0x43414D31||cameraHeader[1]!=1||!cameraHeader[2]||!cameraHeader[3])throw std::runtime_error("coverage camera packet");
 for(float f:replay)if(!std::isfinite(f))throw std::runtime_error("coverage camera finite");
 if(replay[24]<=0||replay[24]>=180||replay[25]<=0||replay[26]<=0||replay[27]<=replay[26])throw std::runtime_error("coverage clipping/FOV");
 remixapi_MeshInfoSurfaceTriangles st{};st.vertices_values=vertices.data();st.vertices_count=vertices.size();st.indices_values=indices.data();st.indices_count=indices.size();
 remixapi_MeshInfo sm{};sm.sType=REMIXAPI_STRUCT_TYPE_MESH_INFO;sm.hash=0x534643C002;sm.surfaces_count=1;sm.surfaces_values=&st;api("coverage_ship_mesh",r.CreateMesh(&sm,&ship));
 remixapi_LightInfoSphereEXT ls{};ls.sType=REMIXAPI_STRUCT_TYPE_LIGHT_INFO_SPHERE_EXT;ls.position={0,0,0};ls.radius=.1f;
 remixapi_LightInfo light{};light.sType=REMIXAPI_STRUCT_TYPE_LIGHT_INFO;light.pNext=&ls;light.hash=0x534643C003;light.radiance={200,200,200};remixapi_LightHandle lh=nullptr;api("coverage_light",r.CreateLight(&light,&lh));
 auto draw=[&](remixapi_MeshHandle mesh,uint32_t id,float x,float z,bool fitted){
  remixapi_InstanceInfoObjectPickingEXT picking{};picking.sType=REMIXAPI_STRUCT_TYPE_INSTANCE_INFO_OBJECT_PICKING_EXT;picking.objectPickingValue=id;
  remixapi_InstanceInfo inst{};inst.sType=REMIXAPI_STRUCT_TYPE_INSTANCE_INFO;inst.pNext=&picking;inst.mesh=mesh;inst.doubleSided=1;
  const float s=fitted?fit[3]:1;inst.transform={{{s,0,0,x-(fitted?fit[0]*s:0)},{0,s,0,-(fitted?fit[1]*s:0)},{0,0,s,z-(fitted?fit[2]*s:0)}}};api("coverage_draw",r.DrawInstance(&inst));
 };
 for(unsigned phase=0;phase<6;++phase){
  for(unsigned frame=0;frame<16;++frame){
   MSG msg{};while(PeekMessageW(&msg,nullptr,0,0,PM_REMOVE)){TranslateMessage(&msg);DispatchMessageW(&msg);}
   remixapi_CameraInfoParameterizedEXT cp{};cp.sType=REMIXAPI_STRUCT_TYPE_CAMERA_INFO_PARAMETERIZED_EXT;cp.forward={0,0,1};cp.up={0,1,0};cp.right={1,0,0};cp.fovYInDegrees=70;cp.aspect=1;cp.nearPlane=.1f;cp.farPlane=100;
   if(phase==5){cp.position={replay[12],replay[13],replay[14]};cp.right={replay[15],replay[16],replay[17]};cp.up={replay[18],replay[19],replay[20]};cp.forward={replay[21],replay[22],replay[23]};cp.fovYInDegrees=replay[24];cp.aspect=replay[25];cp.nearPlane=replay[26];cp.farPlane=replay[27];}
   remixapi_CameraInfo cam{};cam.sType=REMIXAPI_STRUCT_TYPE_CAMERA_INFO;cam.pNext=&cp;api("coverage_camera",r.SetupCamera(&cam));
   if(phase==5){remixapi_InstanceInfoObjectPickingEXT pick{};pick.sType=REMIXAPI_STRUCT_TYPE_INSTANCE_INFO_OBJECT_PICKING_EXT;pick.objectPickingValue=29;remixapi_InstanceInfo inst{};inst.sType=REMIXAPI_STRUCT_TYPE_INSTANCE_INFO;inst.pNext=&pick;inst.mesh=ship;inst.doubleSided=1;std::memcpy(&inst.transform,replay,12*sizeof(float));
#ifdef SFC_TRIPLET_PROBE
    if(triplet)triplet->offset(&inst.transform.matrix[0][0]);
#endif
    api("coverage_replay_draw",r.DrawInstance(&inst));}
   else if(phase==4)draw(ship,23,0,8,true);
   else {if(phase!=2)draw(controlMesh,phase==3?13:7,-1.5f,phase==1?8.0f:6.0f,false);draw(controlMesh,11,1.5f,9,false);}
   api("coverage_draw_light",r.DrawLightInstance(lh));api("coverage_present",r.Present(nullptr));
   bool sample=frame==15;
#ifdef SFC_TRIPLET_PROBE
   sample|=triplet&&phase==5&&frame==7;
#endif
   if(sample){
#ifdef SFC_TRIPLET_PROBE
    if(triplet&&phase==5)triplet->reserve();
#endif
    for(auto& o:outputs){api(o.name,r.dxvk_CopyRenderingOutput(o.gpu.Get(),o.type));}wait9(done.Get());
#ifdef SFC_TRIPLET_PROBE
    uint64_t tripletHashes[3]{};unsigned hashIndex=0;
#endif
    for(auto& o:outputs){hr("coverage_read",device->GetRenderTargetData(o.gpu.Get(),o.cpu.Get()));D3DLOCKED_RECT data{};hr("coverage_lock",o.cpu->LockRect(&data,nullptr,D3DLOCK_READONLY));
     consumerContext->CopyResource(o.staging.Get(),o.native.Get());consumerContext->Flush();D3D11_MAPPED_SUBRESOURCE nativeData{};hr("coverage_native_map",consumerContext->Map(o.staging.Get(),0,D3D11_MAP_READ,0,&nativeData));bool equal=true;
     for(unsigned y=0;y<256;++y)if(std::memcmp(static_cast<const char*>(data.pBits)+size_t(y)*data.Pitch,static_cast<const char*>(nativeData.pData)+size_t(y)*nativeData.RowPitch,1024))equal=false;
     consumerContext->Unmap(o.staging.Get(),0);if(!equal)throw std::runtime_error("native GPU output bytes differ");std::cout<<"COVERAGE_NATIVE_GPU_EXACT phase="<<phase<<" output="<<o.name<<"\n";
     if(o.type==REMIXAPI_DXVK_COPY_RENDERING_OUTPUT_TYPE_OBJECT_PICKING){
      auto* rt=decodedRT.Get();auto* srv=idSRV.Get();consumerContext->OMSetRenderTargets(1,&rt,nullptr);consumerContext->RSSetState(raster.Get());D3D11_VIEWPORT vp{0,0,256,256,0,1};consumerContext->RSSetViewports(1,&vp);consumerContext->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);consumerContext->VSSetShader(vs.Get(),nullptr,0);consumerContext->PSSetShader(ps.Get(),nullptr,0);consumerContext->PSSetShaderResources(0,1,&srv);consumerContext->Draw(3,0);consumerContext->ClearState();consumerContext->CopyResource(decodedCPU.Get(),decoded.Get());consumerContext->Flush();D3D11_MAPPED_SUBRESOURCE ids{};hr("coverage_id_shader_map",consumerContext->Map(decodedCPU.Get(),0,D3D11_MAP_READ,0,&ids));bool exact=true;
      for(unsigned y=0;y<256;++y)if(std::memcmp(static_cast<const char*>(data.pBits)+size_t(y)*data.Pitch,static_cast<const char*>(ids.pData)+size_t(y)*ids.RowPitch,1024))exact=false;
      consumerContext->Unmap(decodedCPU.Get(),0);if(!exact)throw std::runtime_error("shader ID bit decode differs");std::cout<<"COVERAGE_SHADER_ID_EXACT phase="<<phase<<"\n";
     }
     const std::string name="coverage-"+std::to_string(phase)+"-"+o.name+".bin";std::ofstream file(name,std::ios::binary);
     for(unsigned y=0;y<256;++y)file.write(static_cast<const char*>(data.pBits)+size_t(y)*data.Pitch,1024);
#ifdef SFC_TRIPLET_PROBE
     uint64_t hash=14695981039346656037ull;
     for(unsigned y=0;y<256;++y){const auto* row=static_cast<const BYTE*>(data.pBits)+size_t(y)*data.Pitch;
      for(unsigned x=0;x<1024;++x){hash^=row[x];hash*=1099511628211ull;}}
     tripletHashes[hashIndex++]=hash;
#endif
     const bool ok=bool(file);hr("coverage_unlock",o.cpu->UnlockRect());if(!ok)throw std::runtime_error("coverage write");
    }
#ifdef SFC_TRIPLET_PROBE
    if(triplet&&phase==5)triplet->transfer(tripletHashes);
#endif
    std::cout<<"COVERAGE_SAMPLE phase="<<phase<<" frame="<<phase*16+frame<<" outputs=3\n";
   }
   Sleep(10);
  }
 }
#ifdef SFC_TRIPLET_PROBE
 if(triplet)triplet->finish();
#endif
 api("coverage_destroy_control",r.DestroyMesh(controlMesh));api("coverage_destroy_ship",r.DestroyMesh(ship));api("coverage_destroy_light",r.DestroyLight(lh));wait9(done.Get());
 std::cout<<"COVERAGE_CAPTURED_6_PHASES_NOT_YET_QUALIFIED\n";
}
