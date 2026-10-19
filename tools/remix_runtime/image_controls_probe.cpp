// Offline-only fixed scene and GPU colour probes. NEVER loads/injects SFC.
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <d3d9.h>
#include <d3d11.h>
#include <wrl/client.h>
#include <remix/remix_c.h>
#include <iostream>
#include <vector>
#include <array>
#include <cmath>
#include <cstring>
using Microsoft::WRL::ComPtr;
static void check(HRESULT h,const char* s){if(FAILED(h))throw std::runtime_error(s);}
static void check(remixapi_ErrorCode h,const char* s){if(h!=REMIXAPI_ERROR_CODE_SUCCESS)throw std::runtime_error(s);}
#include "remix_image_controls.h"
#include "remix_image_adjust.h"
#include "remix_quality_controls.h"
static LRESULT CALLBACK proc(HWND w,UINT m,WPARAM a,LPARAM b){return DefWindowProcW(w,m,a,b);}
static void wait9(IDirect3DQuery9* q){check(q->Issue(D3DISSUE_END),"probe9 fence");auto end=GetTickCount64()+5000;HRESULT h;while((h=q->GetData(nullptr,0,D3DGETDATA_FLUSH))==S_FALSE){if(GetTickCount64()>end)throw std::runtime_error("probe9 timeout");Sleep(1);}check(h,"probe9 done");}
static std::array<double,3> mean(ID3D11DeviceContext* c,ID3D11Texture2D* source,ID3D11Texture2D* stage){
 c->CopyResource(stage,source);D3D11_MAPPED_SUBRESOURCE m{};check(c->Map(stage,0,D3D11_MAP_READ,0,&m),"probe CPU read");
 std::array<double,3> sum{};for(unsigned y=56;y<72;++y)for(unsigned x=56;x<72;++x){auto* p=static_cast<const unsigned char*>(m.pData)+size_t(y)*m.RowPitch+x*4;for(unsigned k=0;k<3;++k)sum[k]+=p[2-k]/256.;}c->Unmap(stage,0);return sum;
}
int wmain(int argc,wchar_t** argv){if(argc!=2)return 2;std::cout.setf(std::ios::unitbuf);remixapi_Interface api{};HMODULE dll=nullptr;HWND window=nullptr;int result=1;
 const bool qualityMode=GetEnvironmentVariableW(L"SFC_QUALITY_PROBE",nullptr,0)!=0;
 try{
  WNDCLASSW wc{};wc.lpfnWndProc=proc;wc.hInstance=GetModuleHandleW(nullptr);wc.lpszClassName=L"SFC_ImageControlProbe";if(!RegisterClassW(&wc))throw std::runtime_error("probe class");
  window=CreateWindowW(wc.lpszClassName,L"Offline image probe",WS_POPUP,0,0,128,128,nullptr,nullptr,wc.hInstance,nullptr);if(!window)throw std::runtime_error("probe window");
  check(remixapi_lib_loadRemixDllAndInitialize(argv[1],&api,&dll),"probe runtime");
  {
   ComPtr<IDirect3D9Ex> d9;ComPtr<IDirect3DDevice9Ex> initial;check(api.dxvk_CreateD3D9(FALSE,&d9),"probe d9");
   D3DPRESENT_PARAMETERS pp{};pp.BackBufferWidth=pp.BackBufferHeight=128;pp.BackBufferCount=1;pp.BackBufferFormat=D3DFMT_X8R8G8B8;pp.Windowed=TRUE;pp.hDeviceWindow=window;pp.SwapEffect=D3DSWAPEFFECT_DISCARD;pp.PresentationInterval=D3DPRESENT_INTERVAL_IMMEDIATE;
   check(d9->CreateDeviceEx(0,D3DDEVTYPE_HAL,window,D3DCREATE_HARDWARE_VERTEXPROCESSING,&pp,nullptr,&initial),"probe device");check(api.dxvk_RegisterD3D9Device(initial.Get()),"probe register");auto* device=initial.Detach();
   ComPtr<ID3D11Device> native;ComPtr<ID3D11DeviceContext> context;check(D3D11CreateDevice(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,0,nullptr,0,D3D11_SDK_VERSION,&native,nullptr,&context),"probe native");
   D3D11_TEXTURE2D_DESC td{};td.Width=td.Height=128;td.MipLevels=td.ArraySize=1;td.Format=DXGI_FORMAT_B8G8R8A8_UNORM;td.SampleDesc.Count=1;td.BindFlags=D3D11_BIND_RENDER_TARGET|D3D11_BIND_SHADER_RESOURCE;td.MiscFlags=D3D11_RESOURCE_MISC_SHARED;
   ComPtr<ID3D11Texture2D> output,stage;check(native->CreateTexture2D(&td,nullptr,&output),"probe output");td.MiscFlags=td.BindFlags=0;td.Usage=D3D11_USAGE_STAGING;td.CPUAccessFlags=D3D11_CPU_ACCESS_READ;check(native->CreateTexture2D(&td,nullptr,&stage),"probe staging");
   ComPtr<IDXGIResource> resource;check(output.As(&resource),"probe shared");HANDLE h=nullptr;check(resource->GetSharedHandle(&h),"probe handle");
   ComPtr<IDirect3DTexture9> imported;ComPtr<IDirect3DSurface9> surface;check(device->CreateTexture(128,128,1,D3DUSAGE_RENDERTARGET,D3DFMT_A8R8G8B8,D3DPOOL_DEFAULT,&imported,&h),"probe import");check(imported->GetSurfaceLevel(0,&surface),"probe surface");
   ComPtr<IDirect3DQuery9> fence;check(device->CreateQuery(D3DQUERYTYPE_EVENT,&fence),"probe query");RemixImageAdjust adjust;adjust.prepare(native.Get(),output.Get());
   // Exact deterministic texture checks independently validate fallback math,
   // BGRA channel order, neutral bypass and alpha preservation on the real GPU.
   std::vector<unsigned char> pattern(128*128*4);for(size_t i=0;i<pattern.size();i+=4){pattern[i]=32;pattern[i+1]=96;pattern[i+2]=160;pattern[i+3]=77;}
   context->UpdateSubresource(output.Get(),0,nullptr,pattern.data(),128*4,0);
   if(adjust.draw(context.Get(),output.Get(),{1,1,1,0}))throw std::runtime_error("neutral is not bypass");
   auto base=mean(context.Get(),output.Get(),stage.Get());if(base[0]!=160||base[1]!=96||base[2]!=32)throw std::runtime_error("neutral channels");
   adjust.draw(context.Get(),output.Get(),{1,2,1,0});auto gamma=mean(context.Get(),output.Get(),stage.Get());
   if(std::abs(gamma[0]-255*std::sqrt(160/255.))>1||std::abs(gamma[1]-255*std::sqrt(96/255.))>1)throw std::runtime_error("gamma GPU oracle");
   D3D11_MAPPED_SUBRESOURCE m{};check(context->Map(stage.Get(),0,D3D11_MAP_READ,0,&m),"alpha read");bool alpha=static_cast<const unsigned char*>(m.pData)[3]==77;context->Unmap(stage.Get(),0);if(!alpha)throw std::runtime_error("alpha changed");
   context->UpdateSubresource(output.Get(),0,nullptr,pattern.data(),128*4,0);adjust.draw(context.Get(),output.Get(),{1,1,0,0});auto grey=mean(context.Get(),output.Get(),stage.Get());if(std::abs(grey[0]-grey[1])>1||std::abs(grey[1]-grey[2])>1)throw std::runtime_error("saturation GPU oracle");
   std::cout<<"IMAGE_GPU_ORACLE_PASS neutral_bypass=1 gamma=1 grey=1 alpha=1\n";
   remixapi_MaterialInfoOpaqueEXT opaque{};opaque.sType=REMIXAPI_STRUCT_TYPE_MATERIAL_INFO_OPAQUE_EXT;opaque.albedoConstant={.3f,.1f,.02f};opaque.opacityConstant=1;opaque.roughnessConstant=1;opaque.alphaTestType=7;
   wchar_t texturePath[MAX_PATH]{};if(qualityMode&&!GetFullPathNameW(L"quality-checker.dds",MAX_PATH,texturePath,nullptr))throw std::runtime_error("quality texture path");
   remixapi_MaterialInfo mi{};mi.sType=REMIXAPI_STRUCT_TYPE_MATERIAL_INFO;mi.pNext=&opaque;mi.hash=0x494d4701;mi.emissiveColorConstant={.3f,.1f,.02f};mi.emissiveIntensity=1;
   if(qualityMode){mi.albedoTexture=texturePath;mi.emissiveTexture=texturePath;mi.emissiveColorConstant={0,0,0};mi.filterMode=1;}
   remixapi_MaterialHandle material=nullptr;check(api.CreateMaterial(&mi,&material),"probe material");
   remixapi_HardcodedVertex vertices[3]{};float xy[3][2]{{-4,-4},{0,4},{4,-4}};uint32_t indices[3]{0,1,2};for(unsigned i=0;i<3;++i){vertices[i].position[0]=xy[i][0];vertices[i].position[1]=xy[i][1];vertices[i].position[2]=6;vertices[i].normal[2]=-1;vertices[i].color=0xffffffff;}
   if(qualityMode){vertices[1].position[2]=18;vertices[1].texcoord[1]=2;vertices[2].texcoord[0]=2;}
   remixapi_MeshInfoSurfaceTriangles part{};part.vertices_values=vertices;part.vertices_count=3;part.indices_values=indices;part.indices_count=3;part.material=material;remixapi_MeshInfo meshInfo{};meshInfo.sType=REMIXAPI_STRUCT_TYPE_MESH_INFO;meshInfo.hash=0x494d4702;meshInfo.surfaces_values=&part;meshInfo.surfaces_count=1;remixapi_MeshHandle mesh=nullptr;check(api.CreateMesh(&meshInfo,&mesh),"probe mesh");
   remixapi_LightInfoSphereEXT sphere{};sphere.sType=REMIXAPI_STRUCT_TYPE_LIGHT_INFO_SPHERE_EXT;sphere.position={0,0,0};sphere.radius=.25f;remixapi_LightInfo lightInfo{};lightInfo.sType=REMIXAPI_STRUCT_TYPE_LIGHT_INFO;lightInfo.pNext=&sphere;lightInfo.hash=0x514c5401;lightInfo.radiance={2000,2000,2000};remixapi_LightHandle lamp=nullptr;if(qualityMode)check(api.CreateLight(&lightInfo,&lamp),"quality lamp");
   const auto start=GetTickCount64();
   struct Case{const char* name;RemixImageControls value;};std::vector<Case> cases;
   RemixImageControls s;cases.push_back({"startup",s});s.enabled=1;cases.push_back({"local_auto",s});s.automatic=0;cases.push_back({"local_manual",s});s.values[0]=-2;cases.push_back({"local_exposure",s});s.values[0]=0;s.brightness=0;cases.push_back({"local_brightness",s});s.brightness=50;s.values[3]=0;cases.push_back({"local_saturation",s});s.values[3]=1;s.values[1]=0;cases.push_back({"local_contrast",s});s.values[1]=1;s.values[2]=2;cases.push_back({"local_gamma",s});s.values[2]=1;s.mode=0;cases.push_back({"global_manual",s});s.values[3]=0;cases.push_back({"global_saturation",s});s.values[3]=1;s.values[1]=0;cases.push_back({"global_contrast",s});s.values[1]=1;s.values[0]=-2;cases.push_back({"global_exposure",s});s.values[0]=0;s.brightness=0;cases.push_back({"global_brightness",s});s.brightness=50;s.automatic=1;cases.push_back({"global_auto",s});s.enabled=0;cases.push_back({"restored",s});
   RemixImageControls boosted;boosted.enabled=1;boosted.automatic=0;boosted.values[1]=1.5f;boosted.values[3]=1.5f;cases.push_back({"local_boost",boosted});boosted.mode=0;cases.push_back({"global_boost",boosted});
   std::vector<RemixQualityControls> quality;
   if(qualityMode){RemixImageControls neutral;neutral.enabled=1;neutral.automatic=0;if(!neutral.apply([&](const char* k,const char* v){return api.SetConfigVariable(k,v)==REMIXAPI_ERROR_CODE_SUCCESS;}))throw std::runtime_error("quality image setup");
    cases.clear();RemixQualityControls q;q.enabled=1;q.samples=16;
    auto add=[&](const char* name){cases.push_back({name,neutral});quality.push_back(q);};
    add("aniso16");q.anisotropic=0;add("trilinear");q.anisotropic=1;q.samples=1;add("aniso1");q.samples=16;q.bias=-1;add("mip_sharp");q.bias=1;add("mip_soft");q.bias=0;q.aa=3;add("temporal");q.aa=0;q.denoising=0;add("denoise_off");q.denoising=1;add("denoise_on");q.enabled=0;add("restored");add("point_reference");
   }
   for(size_t ci=0;ci<cases.size();++ci){auto& item=cases[ci];
    if(qualityMode&&ci==9){check(api.DestroyMesh(mesh),"quality old mesh");check(api.DestroyMaterial(material),"quality old material");wait9(fence.Get());mi.hash=0x494d4703;mi.filterMode=0;check(api.CreateMaterial(&mi,&material),"point reference material");part.material=material;meshInfo.hash=0x494d4704;check(api.CreateMesh(&meshInfo,&mesh),"point reference mesh");}
    auto setter=[&](const char* k,const char* v){auto code=api.SetConfigVariable(k,v);std::cout<<"NATIVE_OPTION "<<k<<" value="<<v<<" result="<<static_cast<unsigned>(code)<<"\n";return code==REMIXAPI_ERROR_CODE_SUCCESS;};
    if(qualityMode){if(!quality[ci].apply(setter))throw std::runtime_error("native quality option rejected");}
    else if(ci&&!item.value.apply(setter))throw std::runtime_error("native image option rejected");
    std::array<double,3> sums{};unsigned samples=0;double spatial=0,temporal=0;std::array<double,256> previous{};const auto begin=GetTickCount64();
    for(unsigned frame=0;frame<64;++frame){
     if(GetTickCount64()-start>60000)throw std::runtime_error("probe60s cap");
     MSG msg{};while(PeekMessageW(&msg,nullptr,0,0,PM_REMOVE)){TranslateMessage(&msg);DispatchMessageW(&msg);}
     remixapi_CameraInfoParameterizedEXT cp{};cp.sType=REMIXAPI_STRUCT_TYPE_CAMERA_INFO_PARAMETERIZED_EXT;cp.forward={0,0,1};cp.right={1,0,0};cp.up={0,1,0};cp.fovYInDegrees=70;cp.aspect=1;cp.nearPlane=.1f;cp.farPlane=100;
     remixapi_CameraInfo cam{};cam.sType=REMIXAPI_STRUCT_TYPE_CAMERA_INFO;cam.pNext=&cp;check(api.SetupCamera(&cam),"probe camera");remixapi_InstanceInfo instance{};instance.sType=REMIXAPI_STRUCT_TYPE_INSTANCE_INFO;instance.mesh=mesh;instance.doubleSided=1;instance.transform={{{1,0,0,0},{0,1,0,0},{0,0,1,0}}};check(api.DrawInstance(&instance),"probe draw");if(qualityMode&&(ci==6||ci==7))check(api.DrawLightInstance(lamp),"quality draw lamp");check(api.Present(nullptr),"probe present");check(api.dxvk_CopyRenderingOutput(surface.Get(),REMIXAPI_DXVK_COPY_RENDERING_OUTPUT_TYPE_FINAL_COLOR),"probe final color");wait9(fence.Get());
     adjust.draw(context.Get(),output.Get(),item.value.post());auto rgb=mean(context.Get(),output.Get(),stage.Get());if(frame>=48){for(unsigned k=0;k<3;++k)sums[k]+=rgb[k]/16; ++samples;
      if(qualityMode){D3D11_MAPPED_SUBRESOURCE data{};check(context->Map(stage.Get(),0,D3D11_MAP_READ,0,&data),"quality stats");double avg=0;std::array<double,256> current{};unsigned i=0;
       for(unsigned y=56;y<72;++y)for(unsigned x=56;x<72;++x){auto* p=static_cast<const unsigned char*>(data.pData)+size_t(y)*data.RowPitch+x*4;current[i]=.2126*p[2]+.7152*p[1]+.0722*p[0];avg+=current[i++]/256.;}
       context->Unmap(stage.Get(),0);for(unsigned j=0;j<256;++j){spatial+=(current[j]-avg)*(current[j]-avg)/4096.;if(frame>48)temporal+=std::abs(current[j]-previous[j])/3840.;}previous=current;
      }
     }Sleep(16);
    }
    std::cout<<"IMAGE_CASE "<<item.name<<" rgb="<<sums[0]<<","<<sums[1]<<","<<sums[2]<<" samples="<<samples<<" ms="<<GetTickCount64()-begin<<"\n";
    if(qualityMode)std::cout<<"QUALITY_CASE "<<item.name<<" spatial="<<spatial<<" temporal="<<temporal<<"\n";
   }
   check(api.DestroyMesh(mesh),"probe retire mesh");check(api.DestroyMaterial(material),"probe retire material");if(lamp)check(api.DestroyLight(lamp),"quality retire lamp");wait9(fence.Get());result=0;
  }
 }catch(const std::exception& e){std::cout<<"IMAGE_PROBE_FAILED "<<e.what()<<"\n";}
 if(window)SetWindowLongPtrW(window,GWLP_WNDPROC,reinterpret_cast<LONG_PTR>(proc));
 if(api.Shutdown)std::cout<<"IMAGE_SHUTDOWN api="<<static_cast<unsigned>(api.Shutdown())<<"\n";if(window)DestroyWindow(window);if(dll)FreeLibrary(dll);return result;
}
