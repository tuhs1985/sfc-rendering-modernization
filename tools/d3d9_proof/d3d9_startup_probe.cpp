// Bounded,standalone native D3D9 startup diagnostics. No game or Remix load.
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <d3d9.h>
#include <wrl/client.h>
#include <iostream>
#include <filesystem>
using Microsoft::WRL::ComPtr;
static LRESULT CALLBACK proc(HWND w,UINT m,WPARAM p,LPARAM l){return DefWindowProcW(w,m,p,l);}
static void hr(const char* name,HRESULT value){std::cout<<name<<"=0x"<<std::hex<<static_cast<unsigned long>(value)<<std::dec<<' ';}
static void desktopName(const char* label,HANDLE object){
 wchar_t name[256]{};DWORD needed=0;
 if(object&&GetUserObjectInformationW(object,UOI_NAME,name,sizeof(name),&needed))std::wcout<<label<<L'='<<name<<L'\n';
 else std::cout<<label<<"_error="<<GetLastError()<<'\n';
}
int wmain(){
 std::cout.setf(std::ios::unitbuf);
 DWORD session=0;ProcessIdToSessionId(GetCurrentProcessId(),&session);std::cout<<"SESSION "<<session<<'\n';
 HANDLE token=nullptr;TOKEN_ELEVATION elevation{};DWORD returned=0;
 if(OpenProcessToken(GetCurrentProcess(),TOKEN_QUERY,&token)){
  if(GetTokenInformation(token,TokenElevation,&elevation,sizeof(elevation),&returned))std::cout<<"TOKEN_ELEVATED "<<elevation.TokenIsElevated<<'\n';
  CloseHandle(token);
 }
 desktopName("STATION",GetProcessWindowStation());desktopName("THREAD_DESKTOP",GetThreadDesktop(GetCurrentThreadId()));
 const auto input=OpenInputDesktop(0,FALSE,DESKTOP_READOBJECTS);desktopName("INPUT_DESKTOP",input);if(input)CloseDesktop(input);
 wchar_t system[MAX_PATH]{};if(!GetSystemDirectoryW(system,MAX_PATH))return 2;
 const auto library=std::filesystem::path(system)/L"d3d9.dll";
 const auto module=LoadLibraryExW(library.c_str(),nullptr,LOAD_LIBRARY_SEARCH_SYSTEM32);if(!module)return 3;
 const auto create=reinterpret_cast<decltype(&Direct3DCreate9)>(GetProcAddress(module,"Direct3DCreate9"));if(!create)return 4;
 ComPtr<IDirect3D9> api;api.Attach(create(D3D_SDK_VERSION));if(!api)return 5;
 WNDCLASSW wc{};wc.hInstance=GetModuleHandleW(nullptr);wc.lpfnWndProc=proc;wc.lpszClassName=L"SFC_D3D9_Startup_Diagnostic";
 if(!RegisterClassW(&wc))return 6;
 const UINT count=api->GetAdapterCount();std::cout<<"ADAPTER_COUNT "<<count<<'\n';if(count>16)return 7;
 unsigned successes=0;
 for(UINT a=0;a<count;++a){
  D3DADAPTER_IDENTIFIER9 id{};D3DDISPLAYMODE mode{};D3DCAPS9 caps{};
  const auto ident=api->GetAdapterIdentifier(a,0,&id),display=api->GetAdapterDisplayMode(a,&mode),cap=api->GetDeviceCaps(a,D3DDEVTYPE_HAL,&caps);
  const auto monitor=api->GetAdapterMonitor(a);MONITORINFOEXW info{};info.cbSize=sizeof(info);const BOOL located=GetMonitorInfoW(monitor,&info);
  std::cout<<"ADAPTER "<<a<<" description="<<id.Description<<" device="<<id.DeviceName<<" vendor="<<id.VendorId<<" product="<<id.DeviceId<<' ';
  hr("identity",ident);hr("mode",display);hr("caps",cap);std::cout<<" extent="<<mode.Width<<'x'<<mode.Height<<" format="<<mode.Format<<" hz="<<mode.RefreshRate<<" monitor="<<located<<'\n';
  if(located)std::wcout<<L"MONITOR "<<info.szDevice<<L" rect="<<info.rcMonitor.left<<L','<<info.rcMonitor.top<<L','<<info.rcMonitor.right<<L','<<info.rcMonitor.bottom<<L'\n';
  RECT rect{0,0,320,240};AdjustWindowRect(&rect,WS_OVERLAPPEDWINDOW,FALSE);
  const auto window=CreateWindowW(wc.lpszClassName,L"SFC startup diagnostic",WS_OVERLAPPEDWINDOW,
   (located?info.rcMonitor.left:0)+64,(located?info.rcMonitor.top:0)+64,rect.right-rect.left,rect.bottom-rect.top,nullptr,nullptr,wc.hInstance,nullptr);
  if(!window)return 8;
  for(const auto format:{D3DFMT_A8R8G8B8,D3DFMT_X8R8G8B8,D3DFMT_UNKNOWN}){
   const auto type=api->CheckDeviceType(a,D3DDEVTYPE_HAL,mode.Format,format,TRUE);
   std::cout<<"COMBINATION adapter="<<a<<" backbuffer="<<format<<' ';hr("type",type);
   const auto depth=api->CheckDeviceFormat(a,D3DDEVTYPE_HAL,mode.Format,D3DUSAGE_DEPTHSTENCIL,D3DRTYPE_SURFACE,D3DFMT_D24S8);
   hr("depth",depth);
   // Attempt creation as an independent observation,even if the capability query
   // failed. A successful creation never silently waives a failed query.
   D3DPRESENT_PARAMETERS pp{};pp.BackBufferWidth=320;pp.BackBufferHeight=240;pp.BackBufferFormat=format;pp.BackBufferCount=1;
   pp.Windowed=TRUE;pp.hDeviceWindow=window;pp.SwapEffect=D3DSWAPEFFECT_DISCARD;pp.PresentationInterval=D3DPRESENT_INTERVAL_IMMEDIATE;
   pp.EnableAutoDepthStencil=TRUE;pp.AutoDepthStencilFormat=D3DFMT_D24S8;
   ComPtr<IDirect3DDevice9> device;
   const auto result=api->CreateDevice(a,D3DDEVTYPE_HAL,window,D3DCREATE_HARDWARE_VERTEXPROCESSING|D3DCREATE_FPU_PRESERVE,&pp,&device);
   hr("create",result);if(SUCCEEDED(result)){++successes;hr("clear",device->Clear(0,nullptr,D3DCLEAR_TARGET|D3DCLEAR_ZBUFFER,0xff102030,1,0));hr("present",device->Present(nullptr,nullptr,nullptr,nullptr));}
   if(device){auto* raw=device.Detach();std::cout<<"device_refs="<<raw->Release()<<' ';}std::cout<<'\n';
  }
  DestroyWindow(window);
 }
 auto* raw=api.Detach();std::cout<<"PROBE_DONE successes="<<successes<<" api_refs="<<raw->Release()<<'\n';FreeLibrary(module);return 0;
}
