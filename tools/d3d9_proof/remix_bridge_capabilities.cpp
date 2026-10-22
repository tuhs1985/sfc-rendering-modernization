// Read the pinned normal x86 bridge's public interface. No SDK mesh submission.
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#define REMIX_WINAPI_NO_LIBRARY_LOADER
#define REMIX_ALLOW_X86
#include <windows.h>
#include <d3d9.h>
#include <remix_c.h>
#include <wrl/client.h>
#include <filesystem>
#include <iostream>
#include <stdexcept>
using Microsoft::WRL::ComPtr;
static void check(bool value,const char* text){if(!value)throw std::runtime_error(text);}
static LRESULT CALLBACK proc(HWND w,UINT m,WPARAM p,LPARAM l){return DefWindowProcW(w,m,p,l);}
int wmain(int argc,wchar_t** argv){
 std::cout.setf(std::ios::unitbuf);HMODULE module=nullptr;HWND window=nullptr;int result=1;
 try{
  check(argc==2,"one pinned client DLL path required");const auto path=std::filesystem::absolute(argv[1]);
  module=LoadLibraryExW(path.c_str(),nullptr,LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR|LOAD_LIBRARY_SEARCH_SYSTEM32);check(module!=nullptr,"bridge DLL load");
  wchar_t actual[MAX_PATH]{};check(GetModuleFileNameW(module,actual,MAX_PATH)>0&&std::filesystem::equivalent(actual,path),"loaded DLL path differs");
  const auto create=reinterpret_cast<decltype(&Direct3DCreate9)>(GetProcAddress(module,"Direct3DCreate9"));check(create!=nullptr,"normal D3D9 export");
  ComPtr<IDirect3D9> api;api.Attach(create(D3D_SDK_VERSION));check(bool(api),"normal bridge D3D9 create");
  WNDCLASSW wc{};wc.hInstance=GetModuleHandleW(nullptr);wc.lpfnWndProc=proc;wc.lpszClassName=L"SFC_Remix_Capability_Probe";check(RegisterClassW(&wc)!=0,"window class");
  window=CreateWindowW(wc.lpszClassName,L"Offline bridge capability probe",WS_POPUP,0,0,320,240,nullptr,nullptr,wc.hInstance,nullptr);check(window!=nullptr,"window");
  D3DPRESENT_PARAMETERS pp{};pp.BackBufferWidth=320;pp.BackBufferHeight=240;pp.BackBufferFormat=D3DFMT_A8R8G8B8;pp.BackBufferCount=1;pp.Windowed=TRUE;
  pp.hDeviceWindow=window;pp.SwapEffect=D3DSWAPEFFECT_DISCARD;pp.PresentationInterval=D3DPRESENT_INTERVAL_IMMEDIATE;
  ComPtr<IDirect3DDevice9> device;check(SUCCEEDED(api->CreateDevice(0,D3DDEVTYPE_HAL,window,D3DCREATE_HARDWARE_VERTEXPROCESSING|D3DCREATE_FPU_PRESERVE,&pp,&device)),"normal bridge device create");
  const auto initialize=reinterpret_cast<PFN_remixapi_InitializeLibrary>(GetProcAddress(module,"remixapi_InitializeLibrary"));check(initialize!=nullptr,"public API export");
  remixapi_InitializeLibraryInfo info{};info.sType=REMIXAPI_STRUCT_TYPE_INITIALIZE_LIBRARY_INFO;info.version=REMIXAPI_VERSION_MAKE(REMIXAPI_VERSION_MAJOR,REMIXAPI_VERSION_MINOR,REMIXAPI_VERSION_PATCH);
  remixapi_Interface surface{};const auto initialized=initialize(&info,&surface);
  std::cout<<"INITIALIZE result="<<initialized<<" version="<<REMIXAPI_VERSION_MAJOR<<'.'<<REMIXAPI_VERSION_MINOR<<'.'<<REMIXAPI_VERSION_PATCH<<'\n';
  check(initialized==REMIXAPI_ERROR_CODE_SUCCESS,"API initialization did not succeed;not proof of missing capability");
  std::cout<<"CAPABILITIES copy_output="<<bool(surface.dxvk_CopyRenderingOutput)
   <<" external_swapchain="<<bool(surface.dxvk_GetExternalSwapchain)<<" vk_image="<<bool(surface.dxvk_GetVkImage)
   <<" set_default_output="<<bool(surface.dxvk_SetDefaultOutput)<<" request_picking="<<bool(surface.pick_RequestObjectPicking)
   <<" setup_camera="<<bool(surface.SetupCamera)<<" create_mesh="<<bool(surface.CreateMesh)<<" present="<<bool(surface.Present)<<'\n';
  // Never call absent functions,register SDK geometry,or reinterpret server handles.
  std::cout<<(surface.dxvk_CopyRenderingOutput||surface.dxvk_GetExternalSwapchain?
   "OUTPUT_ENTRYPOINT_PRESENT_NOT_TRANSFER_QUALIFIED":"BLOCKED_NORMAL_BRIDGE_OUTPUT_ENTRYPOINTS_ABSENT")<<'\n';
  auto* d=device.Detach();const auto deviceRefs=d->Release();auto* a=api.Detach();const auto apiRefs=a->Release();
  std::cout<<"PROBE_DONE device_refs="<<deviceRefs<<" api_refs="<<apiRefs<<" sdk_mesh_calls=0\n";
  check(deviceRefs==0&&apiRefs==0,"client device references retained");result=0;
 }catch(const std::exception& error){std::cerr<<"CAPABILITY_PROBE_FAILED "<<error.what()<<'\n';}
 if(window)DestroyWindow(window);if(module)FreeLibrary(module);return result;
}
