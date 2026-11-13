// Standalone GPU interoperability diagnostic. CPU readback verifies the fixture;
// no CPU pixels are transported to SFC, which is never launched by this tool.
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#define REMIX_WINAPI_NO_LIBRARY_LOADER
#include <windows.h>
#include <d3d9.h>
#include <d3d11.h>
#include <dxgi.h>
#include <wrl/client.h>
#include <remix_c.h>
#include <iostream>
#include <stdexcept>
#include <string_view>
#include "../d3d9_proof/output_extent.h"
using Microsoft::WRL::ComPtr;
static void require(bool value,const char* why){if(!value)throw std::runtime_error(why);}
static void hr(HRESULT value,const char* why){if(FAILED(value)){std::cout<<why<<" hr="<<std::hex<<unsigned(value)<<std::dec<<'\n';throw std::runtime_error(why);}}
static void api(remixapi_ErrorCode value,const char* why){require(value==REMIXAPI_ERROR_CODE_SUCCESS,why);}
static LRESULT CALLBACK proc(HWND h,UINT m,WPARAM w,LPARAM l){return DefWindowProcW(h,m,w,l);}
int wmain(int argc,wchar_t** argv){
 std::cout.setf(std::ios::unitbuf);
 const bool adapterOnly=argc==3&&std::wstring_view(argv[2])==L"--adapter-only";
 if(!adapterOnly&&argc!=4)return 2;
 const UINT width=adapterOnly?128:static_cast<UINT>(_wtoi(argv[2]));
 const UINT height=adapterOnly?128:static_cast<UINT>(_wtoi(argv[3]));
 if(!output_extent::valid(width,height)||width<2||height<2)return 2;
 HMODULE module=nullptr;HWND window=nullptr;remixapi_Interface remix{};int result=1;
 try{
  WNDCLASSW wc{};wc.lpfnWndProc=proc;wc.hInstance=GetModuleHandleW(nullptr);wc.lpszClassName=L"SFCAlphaSharedLayout";
  require(RegisterClassW(&wc)!=0,"register window");window=CreateWindowW(wc.lpszClassName,L"Standalone shared layout",WS_POPUP,0,0,int(width),int(height),nullptr,nullptr,wc.hInstance,nullptr);require(window!=nullptr,"window");
  module=LoadLibraryExW(argv[1],nullptr,LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR|LOAD_LIBRARY_SEARCH_SYSTEM32);require(module!=nullptr,"pinned runtime load");
  const auto init=reinterpret_cast<PFN_remixapi_InitializeLibrary>(GetProcAddress(module,"remixapi_InitializeLibrary"));require(init!=nullptr,"API entry");
  remixapi_InitializeLibraryInfo info{};info.sType=REMIXAPI_STRUCT_TYPE_INITIALIZE_LIBRARY_INFO;info.version=REMIXAPI_VERSION_MAKE(REMIXAPI_VERSION_MAJOR,REMIXAPI_VERSION_MINOR,REMIXAPI_VERSION_PATCH);api(init(&info,&remix),"API init");
  {
   ComPtr<IDirect3D9Ex> d9;ComPtr<IDirect3DDevice9Ex> owner;
   if(adapterOnly){
    const auto create=reinterpret_cast<decltype(&Direct3DCreate9Ex)>(GetProcAddress(module,"Direct3DCreate9Ex"));
    require(create!=nullptr,"ordinary D3D9Ex export");
    hr(create(D3D_SDK_VERSION,&d9),"ordinary D3D9Ex factory");
   }else api(remix.dxvk_CreateD3D9(FALSE,&d9),"D3D9 factory");
   D3DPRESENT_PARAMETERS pp{};pp.BackBufferWidth=width;pp.BackBufferHeight=height;pp.BackBufferFormat=D3DFMT_A8R8G8B8;pp.BackBufferCount=1;pp.Windowed=TRUE;pp.hDeviceWindow=window;pp.SwapEffect=D3DSWAPEFFECT_DISCARD;pp.PresentationInterval=D3DPRESENT_INTERVAL_IMMEDIATE;
   if(adapterOnly){pp.EnableAutoDepthStencil=TRUE;pp.AutoDepthStencilFormat=D3DFMT_D24S8;}
   const DWORD flags=D3DCREATE_HARDWARE_VERTEXPROCESSING|(adapterOnly?D3DCREATE_FPU_PRESERVE:0);
   hr(d9->CreateDeviceEx(0,D3DDEVTYPE_HAL,window,flags,&pp,nullptr,&owner),"D3D9 device");
   LUID luid{};hr(d9->GetAdapterLUID(0,&luid),"LUID");
   std::cout<<"REMIX_D3D9_ADAPTER luid="<<luid.HighPart<<':'<<luid.LowPart<<'\n';
   if(adapterOnly)result=0;
   else{
   api(remix.dxvk_RegisterD3D9Device(owner.Get()),"register device");auto* device=owner.Detach(); // same SDK-owned lifetime as existing output probe
   ComPtr<IDXGIFactory1> factory;hr(CreateDXGIFactory1(IID_PPV_ARGS(&factory)),"DXGI factory");ComPtr<IDXGIAdapter1> selected;
   for(UINT i=0;i<16;++i){ComPtr<IDXGIAdapter1> a;if(factory->EnumAdapters1(i,&a)==DXGI_ERROR_NOT_FOUND)break;DXGI_ADAPTER_DESC1 desc{};hr(a->GetDesc1(&desc),"adapter");if(desc.AdapterLuid.LowPart==luid.LowPart&&desc.AdapterLuid.HighPart==luid.HighPart){selected=a;break;}}
   require(bool(selected),"same GPU");ComPtr<ID3D11Device> native;ComPtr<ID3D11DeviceContext> context;
   hr(D3D11CreateDevice(selected.Get(),D3D_DRIVER_TYPE_UNKNOWN,nullptr,D3D11_CREATE_DEVICE_BGRA_SUPPORT,nullptr,0,D3D11_SDK_VERSION,&native,nullptr,&context),"native device");
   D3D11_TEXTURE2D_DESC desc{};desc.Width=width;desc.Height=height;desc.MipLevels=desc.ArraySize=desc.SampleDesc.Count=1;desc.Format=DXGI_FORMAT_B8G8R8A8_UNORM;desc.BindFlags=D3D11_BIND_RENDER_TARGET|D3D11_BIND_SHADER_RESOURCE;desc.MiscFlags=D3D11_RESOURCE_MISC_SHARED;
   ComPtr<ID3D11Texture2D> image,staging;hr(native->CreateTexture2D(&desc,nullptr,&image),"shared native texture");ComPtr<IDXGIResource> resource;hr(image.As(&resource),"shared interface");HANDLE handle=nullptr;hr(resource->GetSharedHandle(&handle),"shared handle");
   ComPtr<IDirect3DTexture9> texture;ComPtr<IDirect3DSurface9> surface;hr(device->CreateTexture(width,height,1,D3DUSAGE_RENDERTARGET,D3DFMT_A8R8G8B8,D3DPOOL_DEFAULT,&texture,&handle),"Remix imports native texture");hr(texture->GetSurfaceLevel(0,&surface),"shared surface");
   const D3DCOLOR colors[]={0xff1155aa,0xffbb2277,0xff66cc33,0xffdd9944};
   const LONG halfW=LONG(width/2),halfH=LONG(height/2);const RECT rects[]={{0,0,halfW,halfH},{halfW,0,LONG(width),halfH},{0,halfH,halfW,LONG(height)},{halfW,halfH,LONG(width),LONG(height)}};
   for(unsigned i=0;i<4;++i)hr(device->ColorFill(surface.Get(),&rects[i],colors[i]),"quadrant GPU fill");
   ComPtr<IDirect3DQuery9> fence;hr(device->CreateQuery(D3DQUERYTYPE_EVENT,&fence),"GPU fence");hr(fence->Issue(D3DISSUE_END),"fence issue");const auto deadline=GetTickCount64()+5000;HRESULT ready;
   while((ready=fence->GetData(nullptr,0,D3DGETDATA_FLUSH))==S_FALSE){require(GetTickCount64()<deadline,"GPU completion timeout");Sleep(1);}hr(ready,"GPU completion");
   ComPtr<IDirect3DSurface9> sourceReadback;hr(device->CreateOffscreenPlainSurface(width,height,D3DFMT_A8R8G8B8,D3DPOOL_SYSTEMMEM,&sourceReadback,nullptr),"D3D9 verification staging");
   hr(device->GetRenderTargetData(surface.Get(),sourceReadback.Get()),"D3D9 verification copy");D3DLOCKED_RECT sourcePixels{};hr(sourceReadback->LockRect(&sourcePixels,nullptr,D3DLOCK_READONLY),"D3D9 verification lock");uint64_t sourceMismatches=0;
   for(UINT y=0;y<height;++y){const auto* row=reinterpret_cast<const DWORD*>(static_cast<const BYTE*>(sourcePixels.pBits)+size_t(y)*sourcePixels.Pitch);for(UINT x=0;x<width;++x)sourceMismatches+=row[x]!=colors[(y>=UINT(halfH)?2:0)+(x>=UINT(halfW)?1:0)];}
   hr(sourceReadback->UnlockRect(),"D3D9 verification unlock");std::cout<<"GPU_SOURCE_LAYOUT width="<<width<<" height="<<height<<" row_pitch="<<sourcePixels.Pitch<<" mismatches="<<sourceMismatches<<'\n';
   desc.BindFlags=desc.MiscFlags=0;desc.Usage=D3D11_USAGE_STAGING;desc.CPUAccessFlags=D3D11_CPU_ACCESS_READ;hr(native->CreateTexture2D(&desc,nullptr,&staging),"verification staging");context->CopyResource(staging.Get(),image.Get());
   D3D11_MAPPED_SUBRESOURCE mapped{};hr(context->Map(staging.Get(),0,D3D11_MAP_READ,0,&mapped),"verification map");uint64_t mismatches=0;
   for(UINT y=0;y<height;++y){const auto* row=reinterpret_cast<const DWORD*>(static_cast<const BYTE*>(mapped.pData)+size_t(y)*mapped.RowPitch);for(UINT x=0;x<width;++x)mismatches+=row[x]!=colors[(y>=UINT(halfH)?2:0)+(x>=UINT(halfW)?1:0)];}
   context->Unmap(staging.Get(),0);std::cout<<"GPU_SHARED_LAYOUT width="<<width<<" height="<<height<<" row_pitch="<<mapped.RowPitch<<" mismatches="<<mismatches<<" pixels="<<uint64_t(width)*height<<"\n";result=(sourceMismatches||mismatches)?1:0;
   }
  }
 }catch(const std::exception& e){std::cout<<"PARTIAL "<<e.what()<<'\n';}
 if(window)SetWindowLongPtrW(window,GWLP_WNDPROC,reinterpret_cast<LONG_PTR>(proc));
 if(remix.Shutdown){
  const auto status=remix.Shutdown();
  std::cout<<"SHUTDOWN "<<unsigned(status)<<'\n';
  if(adapterOnly&&status!=REMIXAPI_ERROR_CODE_SUCCESS)result=1;
 }
 // The one-shot helper exits after releasing its device and shutting down
 // the SDK. Keep the module loaded until process exit.
 if(adapterOnly)return result;
 if(window)DestroyWindow(window);if(module)FreeLibrary(module);return result;
}
