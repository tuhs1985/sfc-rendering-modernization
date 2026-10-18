// Bounded OFFLINE SDK texture orientation/emission control. Never attaches SFC.
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <d3d9.h>
#include <wrl/client.h>
#include <remix/remix_c.h>
#include <fstream>
#include <iostream>
#include <stdexcept>
using Microsoft::WRL::ComPtr;
static void check(HRESULT r){if(FAILED(r))throw std::runtime_error("D3D operation failed");}
static void check(remixapi_ErrorCode r){if(r!=REMIXAPI_ERROR_CODE_SUCCESS)throw std::runtime_error("SDK operation failed");}
static LRESULT CALLBACK proc(HWND w,UINT m,WPARAM p,LPARAM l){return DefWindowProcW(w,m,p,l);}
int wmain(int argc,wchar_t** argv){
 if(argc!=3)return 2;std::cout.setf(std::ios::unitbuf);
 remixapi_Interface api{};HMODULE dll=nullptr;HWND window=nullptr;
 try{
  WNDCLASSW wc{};wc.lpfnWndProc=proc;wc.hInstance=GetModuleHandleW(nullptr);wc.lpszClassName=L"SFC_OfflineUVProbe";
  if(!RegisterClassW(&wc))throw std::runtime_error("class");
  window=CreateWindowW(wc.lpszClassName,L"Offline UV control",WS_POPUP,0,0,256,256,nullptr,nullptr,wc.hInstance,nullptr);
  if(!window)throw std::runtime_error("window");
  check(remixapi_lib_loadRemixDllAndInitialize(argv[1],&api,&dll));check(api.SetConfigVariable("rtx.resolutionScale","1.0"));
  {
   ComPtr<IDirect3D9Ex> d9;ComPtr<IDirect3DDevice9Ex> owned;check(api.dxvk_CreateD3D9(FALSE,&d9));
   D3DPRESENT_PARAMETERS pp{};pp.BackBufferWidth=pp.BackBufferHeight=256;pp.BackBufferCount=1;pp.BackBufferFormat=D3DFMT_X8R8G8B8;
   pp.Windowed=TRUE;pp.hDeviceWindow=window;pp.SwapEffect=D3DSWAPEFFECT_DISCARD;pp.PresentationInterval=D3DPRESENT_INTERVAL_IMMEDIATE;
   check(d9->CreateDeviceEx(0,D3DDEVTYPE_HAL,window,D3DCREATE_HARDWARE_VERTEXPROCESSING,&pp,nullptr,&owned));
   check(api.dxvk_RegisterD3D9Device(owned.Get()));auto* device=owned.Detach();
   ComPtr<IDirect3DSurface9> target,staging;ComPtr<IDirect3DQuery9> fence;
   check(device->CreateRenderTarget(256,256,D3DFMT_A8R8G8B8,D3DMULTISAMPLE_NONE,0,FALSE,&target,nullptr));
   check(device->CreateOffscreenPlainSurface(256,256,D3DFMT_A8R8G8B8,D3DPOOL_SYSTEMMEM,&staging,nullptr));
   check(device->CreateQuery(D3DQUERYTYPE_EVENT,&fence));
   remixapi_HardcodedVertex vertices[4]{};
   const float positions[4][3]={{-2,2,6},{2,2,6},{-2,-2,6},{2,-2,6}};
   const float uv[4][2]={{0,0},{1,0},{0,1},{1,1}};const uint32_t indices[6]={0,1,2,2,1,3};
   for(unsigned i=0;i<4;++i){for(unsigned j=0;j<3;++j)vertices[i].position[j]=positions[i][j];vertices[i].normal[2]=-1;vertices[i].color=0xffffffff;vertices[i].texcoord[0]=uv[i][0];vertices[i].texcoord[1]=uv[i][1];}
   remixapi_LightInfoSphereEXT sphere{};sphere.sType=REMIXAPI_STRUCT_TYPE_LIGHT_INFO_SPHERE_EXT;sphere.radius=.1f;
   remixapi_LightInfo li{};li.sType=REMIXAPI_STRUCT_TYPE_LIGHT_INFO;li.pNext=&sphere;li.hash=0x55565001;li.radiance={200,200,200};
   remixapi_LightHandle light=nullptr;check(api.CreateLight(&li,&light));
   for(unsigned mode=0;mode<2;++mode){
    remixapi_MaterialInfoOpaqueEXT opaque{};opaque.sType=REMIXAPI_STRUCT_TYPE_MATERIAL_INFO_OPAQUE_EXT;
    opaque.albedoConstant={1,1,1};opaque.opacityConstant=1;opaque.roughnessConstant=1;opaque.alphaTestType=7;
    remixapi_MaterialInfo mi{};mi.sType=REMIXAPI_STRUCT_TYPE_MATERIAL_INFO;mi.pNext=&opaque;mi.hash=0x55565010+mode;
    mi.albedoTexture=argv[2];mi.emissiveTexture=argv[2];mi.emissiveIntensity=float(mode);mi.emissiveColorConstant={1,1,1};
    remixapi_MaterialHandle material=nullptr;check(api.CreateMaterial(&mi,&material));
    remixapi_MeshInfoSurfaceTriangles surface{};surface.vertices_values=vertices;surface.vertices_count=4;surface.indices_values=indices;surface.indices_count=6;surface.material=material;
    remixapi_MeshInfo meshInfo{};meshInfo.sType=REMIXAPI_STRUCT_TYPE_MESH_INFO;meshInfo.hash=0x55565020+mode;meshInfo.surfaces_values=&surface;meshInfo.surfaces_count=1;
    remixapi_MeshHandle mesh=nullptr;check(api.CreateMesh(&meshInfo,&mesh));
    for(unsigned frame=0;frame<32;++frame){
     MSG msg{};while(PeekMessageW(&msg,nullptr,0,0,PM_REMOVE)){TranslateMessage(&msg);DispatchMessageW(&msg);}
     remixapi_CameraInfoParameterizedEXT cp{};cp.sType=REMIXAPI_STRUCT_TYPE_CAMERA_INFO_PARAMETERIZED_EXT;cp.forward={0,0,1};cp.right={1,0,0};cp.up={0,1,0};cp.fovYInDegrees=70;cp.aspect=1;cp.nearPlane=.1f;cp.farPlane=100;
     remixapi_CameraInfo ci{};ci.sType=REMIXAPI_STRUCT_TYPE_CAMERA_INFO;ci.pNext=&cp;check(api.SetupCamera(&ci));
     remixapi_InstanceInfo instance{};instance.sType=REMIXAPI_STRUCT_TYPE_INSTANCE_INFO;instance.mesh=mesh;instance.doubleSided=1;instance.transform={{{1,0,0,0},{0,1,0,0},{0,0,1,0}}};
     check(api.DrawInstance(&instance));check(api.DrawLightInstance(light));check(api.Present(nullptr));
    }
    check(api.dxvk_CopyRenderingOutput(target.Get(),REMIXAPI_DXVK_COPY_RENDERING_OUTPUT_TYPE_FINAL_COLOR));check(fence->Issue(D3DISSUE_END));
    const auto limit=GetTickCount64()+5000;HRESULT status;
    while((status=fence->GetData(nullptr,0,D3DGETDATA_FLUSH))==S_FALSE){if(GetTickCount64()>limit)throw std::runtime_error("GPU timeout");Sleep(1);}check(status);
    check(device->GetRenderTargetData(target.Get(),staging.Get()));D3DLOCKED_RECT pixels{};check(staging->LockRect(&pixels,nullptr,D3DLOCK_READONLY));
    std::ofstream file(mode?"emission-on.bgra":"emission-off.bgra",std::ios::binary);
    for(unsigned y=0;y<256;++y)file.write(static_cast<const char*>(pixels.pBits)+size_t(y)*pixels.Pitch,256*4);
    check(staging->UnlockRect());if(!file)throw std::runtime_error("bounded output write");
    check(api.DestroyMesh(mesh));check(api.DestroyMaterial(material));std::cout<<"CAPTURE mode="<<mode<<" frames=32 bytes=262144\n";
   }
   check(api.DestroyLight(light));
  }
  check(api.Shutdown());FreeLibrary(dll);DestroyWindow(window);std::cout<<"OFFLINE_UV_CONTROL_PASS\n";return 0;
 }catch(const std::exception& e){std::cout<<"PARTIAL "<<e.what()<<"\n";if(api.Shutdown)api.Shutdown();if(dll)FreeLibrary(dll);if(window)DestroyWindow(window);return 1;}
}
