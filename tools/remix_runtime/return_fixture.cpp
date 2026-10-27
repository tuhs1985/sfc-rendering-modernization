#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <d3d11.h>
#include <dxgi.h>
#include <d3dcompiler.h>
#include <wrl/client.h>
#include <iostream>
#include <fstream>
#include <cstring>
#include <dbghelp.h>
#include "return_wire.h"
#include "depth_search_wire.h"
#include "broad_trace.h"
#include "source_timing_fixture.h"
#include "../d3d9_proof/game_output_wire.h"
#include "../d3d9_proof/synchronized_frame.h"
using Microsoft::WRL::ComPtr;
static void check(HRESULT h,const char* text){if(FAILED(h))throw std::runtime_error(text);}
static LRESULT CALLBACK proc(HWND w,UINT m,WPARAM p,LPARAM l){return DefWindowProcW(w,m,p,l);}
__declspec(naked) static void probeBegin(){__asm{push ebx} __asm{push esi} __asm{mov esi,ecx} __asm{push edi} __asm{pop edi} __asm{pop esi} __asm{pop ebx} __asm{ret}}
__declspec(naked) static void probeEnd(){__asm{push ebx} __asm{push esi} __asm{mov esi,ecx} __asm{push edi} __asm{pop edi} __asm{pop esi} __asm{pop ebx} __asm{ret}}
__declspec(naked) static void probePresent(){__asm{push ebx} __asm{push esi} __asm{mov esi,ecx} __asm{push edi} __asm{pop edi} __asm{pop esi} __asm{pop ebx} __asm{ret}}
static depth_search::Data* fakeSearch=nullptr;static bool slowRequested=false,slowDone=false;static DWORD fakeStart=0;
static void maybeSlow(){
  __declspec(align(16)) BYTE saved[512];
  __asm{fxsave saved}
  if(slowRequested&&!slowDone&&fakeSearch&&GetTickCount()-fakeStart>4000){
    slowDone=true;InterlockedExchange(&fakeSearch->reserved,1);Sleep(2000);
    InterlockedExchange(&fakeSearch->reserved,2);
  }
  __asm{fxrstor saved}
}
__declspec(naked) static void fakeEndScene(){__asm{call maybeSlow} __asm{xor eax,eax} __asm{ret 4}}
static void* fakeTable[11]={nullptr,nullptr,nullptr,nullptr,nullptr,nullptr,nullptr,nullptr,nullptr,nullptr,reinterpret_cast<void*>(&fakeEndScene)};
static void* fakeDevice=fakeTable;
// Mirrors actual mid-function call/test bytes and COM stack consumption.
__declspec(naked) static void probeAfterFlush(){__asm{call dword ptr [ecx+28h]} __asm{test eax,eax} __asm{ret}}
__declspec(naked) static void invokeAfterFlush(){
  __asm{push offset finished}
  __asm{push offset fakeDevice}
  __asm{mov ecx,offset fakeTable}
  __asm{jmp probeAfterFlush}
  __asm{finished: ret}
}
static bool preserved(void (*function)(),bool midCall=false){
  __declspec(align(16)) BYTE before[512]{},after[512]{};
  DWORD stackBefore=0,stackAfter=0,flagsBefore=0,flagsAfter=0,answer=1;
  __asm{mov stackBefore,esp}
  __asm{pushfd}
  __asm{pop flagsBefore}
  __asm{fxsave before}
  __asm{call function}
  __asm{mov answer,eax}
  __asm{fxsave after}
  __asm{pushfd}
  __asm{pop flagsAfter}
  __asm{mov stackAfter,esp}
  return stackBefore==stackAfter&&!std::memcmp(before,after,512)&&
    (midCall?(answer==0&&(flagsAfter&64)!=0):((flagsBefore^flagsAfter)&0xCD5)==0);
}
static LONG CALLBACK traceCrash(EXCEPTION_POINTERS* exception){
  static LONG once=0;
  if(exception->ExceptionRecord->ExceptionCode!=EXCEPTION_STACK_OVERFLOW&&exception->ExceptionRecord->ExceptionCode!=EXCEPTION_ACCESS_VIOLATION)return EXCEPTION_CONTINUE_SEARCH;
  if(InterlockedExchange(&once,1))return EXCEPTION_CONTINUE_SEARCH;
  std::cout<<"FIXTURE_EXCEPTION code=0x"<<std::hex<<exception->ExceptionRecord->ExceptionCode<<std::dec<<"\n";
  void* frames[32]{};const auto count=CaptureStackBackTrace(0,32,frames,nullptr);
  for(unsigned i=0;i<count;++i){HMODULE module=nullptr;char file[1024]{};
    if(GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,reinterpret_cast<LPCSTR>(frames[i]),&module))GetModuleFileNameA(module,file,1024);
    std::cout<<"STACK "<<i<<" "<<file<<" +0x"<<std::hex<<(reinterpret_cast<uintptr_t>(frames[i])-reinterpret_cast<uintptr_t>(module))<<std::dec<<"\n";
  }
  HANDLE file=CreateFileW(L"fixture-crash.dmp",GENERIC_WRITE,0,nullptr,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,nullptr);
  if(file!=INVALID_HANDLE_VALUE){MINIDUMP_EXCEPTION_INFORMATION info{GetCurrentThreadId(),exception,FALSE};MiniDumpWriteDump(GetCurrentProcess(),GetCurrentProcessId(),file,MiniDumpNormal,&info,nullptr,nullptr);CloseHandle(file);}
  TerminateProcess(GetCurrentProcess(),exception->ExceptionRecord->ExceptionCode);
  return EXCEPTION_CONTINUE_SEARCH;
}
struct Scene {
  ComPtr<ID3D11Device> device;ComPtr<ID3D11DeviceContext> context;ComPtr<IDXGISwapChain> swap;
  ComPtr<ID3D11RenderTargetView> target;ComPtr<ID3D11RasterizerState> raster;ComPtr<ID3D11BlendState> blend;ComPtr<ID3D11DepthStencilState> depth;
  ComPtr<ID3D11DepthStencilView> fixtureDepth;
  ComPtr<ID3D11Texture2D> fixtureColor;
  ComPtr<ID3D11VertexShader> fixtureVS;ComPtr<ID3D11PixelShader> fixturePS;ComPtr<ID3D11Buffer> fixtureIndices;
  uint32_t width=800,height=600;
  void targetView(){
    D3D11_TEXTURE2D_DESC color{};color.Width=color.Height=16;color.MipLevels=color.ArraySize=1;color.Format=DXGI_FORMAT_B8G8R8A8_UNORM;color.SampleDesc.Count=1;color.BindFlags=D3D11_BIND_SHADER_RESOURCE;
    fixtureColor.Reset();check(device->CreateTexture2D(&color,nullptr,&fixtureColor),"fixture explicit color resource event");
    ComPtr<ID3D11Texture2D> texture;check(swap->GetBuffer(0,IID_PPV_ARGS(&texture)),"fixture backbuffer");check(device->CreateRenderTargetView(texture.Get(),nullptr,&target),"fixture RTV");
    fixtureDepth.Reset();
    if(GetEnvironmentVariableW(L"SFC_RETURN_FIXTURE_DEPTH",nullptr,0)){
      D3D11_TEXTURE2D_DESC desc{};desc.Width=width;desc.Height=height;desc.MipLevels=desc.ArraySize=1;
      desc.Format=DXGI_FORMAT_D24_UNORM_S8_UINT;desc.SampleDesc.Count=1;desc.BindFlags=D3D11_BIND_DEPTH_STENCIL;
      const bool snapshot=GetEnvironmentVariableW(L"SFC_REMIX_DEPTH_OUTPUT",nullptr,0)!=0||GetEnvironmentVariableW(L"SFC_D3D9_GAME_OUTPUT",nullptr,0)!=0;
      if(snapshot){desc.Format=DXGI_FORMAT_R32_TYPELESS;desc.SampleDesc.Count=8;desc.BindFlags|=D3D11_BIND_SHADER_RESOURCE;}
      ComPtr<ID3D11Texture2D> resource;check(device->CreateTexture2D(&desc,nullptr,&resource),"fixture known depth resource");
      D3D11_DEPTH_STENCIL_VIEW_DESC vd{};vd.Format=DXGI_FORMAT_D32_FLOAT;vd.ViewDimension=D3D11_DSV_DIMENSION_TEXTURE2DMS;
      check(device->CreateDepthStencilView(resource.Get(),snapshot?&vd:nullptr,&fixtureDepth),"fixture known depth view");
      if(snapshot)context->ClearDepthStencilView(fixtureDepth.Get(),D3D11_CLEAR_DEPTH,GetEnvironmentVariableW(L"SFC_D3D9_GAME_OUTPUT",nullptr,0)?1.f:.625f,0);
      D3D11_TEXTURE2D_DESC actual{};resource->GetDesc(&actual);
      D3D11_DEPTH_STENCIL_VIEW_DESC actualView{};fixtureDepth->GetDesc(&actualView);
      std::cout<<"KNOWN_FIXTURE_DEPTH width="<<width<<" height="<<height<<" resource_format="<<actual.Format<<" view_format="<<actualView.Format<<" flags="<<actual.BindFlags<<"\n";
      // Known bound descriptor only; depth testing stays disabled. Not scene data.
    }
  }
  void init(HWND window){
    DXGI_SWAP_CHAIN_DESC desc{};desc.BufferDesc.Width=width;desc.BufferDesc.Height=height;desc.BufferDesc.Format=DXGI_FORMAT_B8G8R8A8_UNORM;
    desc.BufferCount=1;desc.SampleDesc.Count=1;desc.BufferUsage=DXGI_USAGE_RENDER_TARGET_OUTPUT;desc.OutputWindow=window;desc.Windowed=TRUE;desc.SwapEffect=DXGI_SWAP_EFFECT_SEQUENTIAL;
    const D3D_FEATURE_LEVEL level=D3D_FEATURE_LEVEL_10_1;
    const bool snapshot=GetEnvironmentVariableW(L"SFC_REMIX_DEPTH_OUTPUT",nullptr,0)!=0;
    check(D3D11CreateDeviceAndSwapChain(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,0,snapshot?&level:nullptr,snapshot?1:0,D3D11_SDK_VERSION,&desc,&swap,&device,nullptr,&context),"fixture device/swapchain");
    if(snapshot){if(device->GetFeatureLevel()!=level)throw std::runtime_error("snapshot fixture feature level mismatch");std::cout<<"DEPTH_FEATURE_LEVEL "<<static_cast<unsigned>(device->GetFeatureLevel())<<"\n";}targetView();
    D3D11_RASTERIZER_DESC rd{};rd.FillMode=D3D11_FILL_SOLID;rd.CullMode=D3D11_CULL_FRONT;rd.DepthClipEnable=TRUE;rd.ScissorEnable=TRUE;check(device->CreateRasterizerState(&rd,&raster),"fixture raster");
    D3D11_BLEND_DESC bd{};bd.RenderTarget[0].RenderTargetWriteMask=D3D11_COLOR_WRITE_ENABLE_ALL;check(device->CreateBlendState(&bd,&blend),"fixture blend");
    D3D11_DEPTH_STENCIL_DESC dd{};dd.DepthEnable=FALSE;dd.DepthWriteMask=D3D11_DEPTH_WRITE_MASK_ZERO;dd.DepthFunc=D3D11_COMPARISON_ALWAYS;check(device->CreateDepthStencilState(&dd,&depth),"fixture depth");
    if(GetEnvironmentVariableW(L"SFC_REMIX_BROAD_OUTPUT",nullptr,0)||GetEnvironmentVariableW(L"SFC_REMIX_DEPTH_OUTPUT",nullptr,0)||GetEnvironmentVariableW(L"SFC_D3D9_GAME_OUTPUT",nullptr,0)){
      const char* code="float4 vs(uint id:SV_VertexID):SV_Position { float2 p[3]={float2(-.5,-.5),float2(0,.5),float2(.5,-.5)};return float4(p[id],.5,1); } float4 ps():SV_Target { return float4(.02,.05,.3,1); }";
      ComPtr<ID3DBlob> vs,ps,errors;
      check(D3DCompile(code,std::strlen(code),nullptr,nullptr,nullptr,"vs","vs_4_0",D3DCOMPILE_ENABLE_STRICTNESS,0,&vs,&errors),"fixture VS compile");
      check(D3DCompile(code,std::strlen(code),nullptr,nullptr,nullptr,"ps","ps_4_0",D3DCOMPILE_ENABLE_STRICTNESS,0,&ps,&errors),"fixture PS compile");
      check(device->CreateVertexShader(vs->GetBufferPointer(),vs->GetBufferSize(),nullptr,&fixtureVS),"fixture VS");
      check(device->CreatePixelShader(ps->GetBufferPointer(),ps->GetBufferSize(),nullptr,&fixturePS),"fixture PS");
      const uint16_t indices[]={0,1,2};D3D11_BUFFER_DESC indexDesc{};indexDesc.ByteWidth=sizeof(indices);indexDesc.Usage=D3D11_USAGE_IMMUTABLE;indexDesc.BindFlags=D3D11_BIND_INDEX_BUFFER;
      D3D11_SUBRESOURCE_DATA data{indices,0,0};check(device->CreateBuffer(&indexDesc,&data,&fixtureIndices),"fixture index buffer");
    }
  }
  void resize(){context->ClearState();target.Reset();width=1024;height=768;check(swap->ResizeBuffers(1,width,height,DXGI_FORMAT_B8G8R8A8_UNORM,0),"fixture resize");targetView();}
  void clear(){
    const float blue[]={0.02f,0.05f,0.3f,1};context->ClearRenderTargetView(target.Get(),blue);
    const float factor[]={0.1f,0.2f,0.3f,0.4f};context->OMSetBlendState(blend.Get(),factor,0xFFFFFFFA);context->OMSetDepthStencilState(depth.Get(),42);
    context->RSSetState(raster.Get());D3D11_VIEWPORT viewport{3,4,static_cast<float>(width-10),static_cast<float>(height-20),0.2f,0.8f};context->RSSetViewports(1,&viewport);
    const D3D11_RECT scissor{10,20,500,400};context->RSSetScissorRects(1,&scissor);
    context->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_LINELIST);auto* rt=target.Get();
    if(GetEnvironmentVariableW(L"SFC_REMIX_DEPTH_OUTPUT",nullptr,0)||GetEnvironmentVariableW(L"SFC_D3D9_GAME_OUTPUT",nullptr,0))context->OMSetRenderTargets(0,nullptr,fixtureDepth.Get());
    else context->OMSetRenderTargets(1,&rt,fixtureDepth.Get());
  }
  bool statePreserved(bool depthUnbound=false){
    ComPtr<ID3D11BlendState> bs;float factor[4]{};UINT mask=0;context->OMGetBlendState(&bs,factor,&mask);
    ComPtr<ID3D11DepthStencilState> ds;UINT stencil=0;context->OMGetDepthStencilState(&ds,&stencil);
    ComPtr<ID3D11RasterizerState> rs;context->RSGetState(&rs);ComPtr<ID3D11RenderTargetView> rt;ComPtr<ID3D11DepthStencilView> boundDepth;context->OMGetRenderTargets(1,&rt,&boundDepth);
    UINT n=1;D3D11_VIEWPORT vp{};context->RSGetViewports(&n,&vp);UINT nr=1;D3D11_RECT rect{};context->RSGetScissorRects(&nr,&rect);
    D3D11_PRIMITIVE_TOPOLOGY topology{};context->IAGetPrimitiveTopology(&topology);
    return bs.Get()==blend.Get()&&ds.Get()==depth.Get()&&rs.Get()==raster.Get()&&rt.Get()==target.Get()&&boundDepth.Get()==(depthUnbound?nullptr:fixtureDepth.Get())&&mask==0xFFFFFFFA&&stencil==42&&factor[0]==0.1f&&factor[3]==0.4f&&n==1&&vp.TopLeftX==3&&vp.TopLeftY==4&&vp.Width==width-10&&vp.Height==height-20&&vp.MinDepth==0.2f&&vp.MaxDepth==0.8f&&nr==1&&rect.left==10&&rect.bottom==400&&topology==D3D11_PRIMITIVE_TOPOLOGY_LINELIST;
  }
  void stampFrame(DWORD frame){
    ComPtr<ID3D11Texture2D> back;check(swap->GetBuffer(0,IID_PPV_ARGS(&back)),"stamp back");
    DWORD markers[]{0xff000000u|(frame&0xffffffu),0xff000000u|((frame^0x55aa55u)&0xffffffu)};
    const unsigned y[]{4,height-5};for(unsigned i=0;i<2;++i){D3D11_BOX box{100,y[i],0,101,y[i]+1,1};context->UpdateSubresource(back.Get(),0,&box,&markers[i],4,4);}
  }
  void shipSample(DWORD expectedScene=0,bool late=false,bool requireShip=true){
    ComPtr<ID3D11Texture2D> back;check(swap->GetBuffer(0,IID_PPV_ARGS(&back)),"game fixture backbuffer");D3D11_TEXTURE2D_DESC desc{};back->GetDesc(&desc);
    desc.Usage=D3D11_USAGE_STAGING;desc.BindFlags=desc.MiscFlags=0;desc.CPUAccessFlags=D3D11_CPU_ACCESS_READ;
    ComPtr<ID3D11Texture2D> staging;check(device->CreateTexture2D(&desc,nullptr,&staging),"game fixture one-shot staging");context->CopyResource(staging.Get(),back.Get());
    D3D11_MAPPED_SUBRESOURCE p{};check(context->Map(staging.Get(),0,D3D11_MAP_READ,0,&p),"game fixture one-shot pixels");unsigned changed=0;bool border=true;
    if(expectedScene){DWORD actual[2]{};memcpy(&actual[0],static_cast<BYTE*>(p.pData)+4*p.RowPitch+400,4);memcpy(&actual[1],static_cast<BYTE*>(p.pData)+(height-5)*p.RowPitch+400,4);
      const bool exact=actual[0]==(0xff000000u|(expectedScene&0xffffffu))&&actual[1]==(0xff000000u|((expectedScene^0x55aa55u)&0xffffffu));
      std::cout<<"BUFFERED_SCENE_PIXELS frame="<<expectedScene<<" native_HUD_and_scene_exact="<<exact<<'\n';if(!exact)throw std::runtime_error("Buffered background/HUD mixed with newer frame");}
    for(unsigned y=0;y<height;++y){const auto* row=static_cast<const unsigned char*>(p.pData)+y*p.RowPitch;for(unsigned x=0;x<width;++x){const auto* c=row+x*4;
      const bool different=std::abs(int(c[0])-77)>3||std::abs(int(c[1])-13)>3||std::abs(int(c[2])-5)>3;
      changed+=different;if(x<80&&y>height-80&&different)border=false;
    }}
    if(GetEnvironmentVariableW(L"SFC_FIXTURE_SHIP_SNAPSHOT",nullptr,0)){
      if(width>1920||height>1080)throw std::runtime_error("fixture image extent cap");
      BITMAPFILEHEADER f{};f.bfType=0x4D42;f.bfOffBits=sizeof(f)+sizeof(BITMAPINFOHEADER);f.bfSize=f.bfOffBits+width*height*4;
      BITMAPINFOHEADER b{};b.biSize=sizeof(b);b.biWidth=static_cast<LONG>(width);b.biHeight=-static_cast<LONG>(height);b.biPlanes=1;b.biBitCount=32;
      std::ofstream image(late?"fixture-ship-late.bmp":"fixture-ship.bmp",std::ios::binary);image.write(reinterpret_cast<const char*>(&f),sizeof(f));image.write(reinterpret_cast<const char*>(&b),sizeof(b));
      for(unsigned y=0;y<height;++y)image.write(static_cast<const char*>(p.pData)+y*p.RowPitch,width*4);
      if(!image)throw std::runtime_error("fixture image write");
      std::cout<<"SHIP_SNAPSHOT once=1 late="<<late<<" source_frame="<<expectedScene<<" width="<<width<<" height="<<height<<'\n';
    }
    context->Unmap(staging.Get(),0);std::cout<<"GAME_IMAGE_PIXELS changed="<<changed<<" border_untouched="<<border<<'\n';
    if((requireShip&&changed<8)||!border)throw std::runtime_error("No actual additive ship pixels or original border damaged");
  }
  unsigned sample(const char* phase,bool save){
    ComPtr<ID3D11Texture2D> back;check(swap->GetBuffer(0,IID_PPV_ARGS(&back)),"fixture sampled backbuffer");D3D11_TEXTURE2D_DESC desc{};back->GetDesc(&desc);
    desc.Usage=D3D11_USAGE_STAGING;desc.BindFlags=0;desc.MiscFlags=0;desc.CPUAccessFlags=D3D11_CPU_ACCESS_READ;
    ComPtr<ID3D11Texture2D> staging;check(device->CreateTexture2D(&desc,nullptr,&staging),"fixture staging");context->CopyResource(staging.Get(),back.Get());
    D3D11_MAPPED_SUBRESOURCE pixels{};check(context->Map(staging.Get(),0,D3D11_MAP_READ,0,&pixels),"fixture verification readback");
    unsigned green=0;bool untouched=true;
    for(unsigned y=96;y<352;++y){const auto* row=static_cast<const unsigned char*>(pixels.pData)+y*pixels.RowPitch;for(unsigned x=width-272;x<width-16;++x){if(row[x*4+1]>row[x*4]+20&&row[x*4+1]>row[x*4+2]+20)++green;}}
    // A blue-only region outside the image verifies original drawing remains.
    for(unsigned y=height-80;y<height-20;++y){const auto* row=static_cast<const unsigned char*>(pixels.pData)+y*pixels.RowPitch;for(unsigned x=20;x<80;++x)if(row[x*4]<50||row[x*4+1]>30||row[x*4+2]>20)untouched=false;}
    if(save){
      BITMAPFILEHEADER f{};f.bfType=0x4D42;f.bfOffBits=sizeof(f)+sizeof(BITMAPINFOHEADER);f.bfSize=f.bfOffBits+width*height*4;
      BITMAPINFOHEADER b{};b.biSize=sizeof(b);b.biWidth=static_cast<LONG>(width);b.biHeight=-static_cast<LONG>(height);b.biPlanes=1;b.biBitCount=32;
      std::ofstream image("fixture-enabled.bmp",std::ios::binary);image.write(reinterpret_cast<const char*>(&f),sizeof(f));image.write(reinterpret_cast<const char*>(&b),sizeof(b));
      for(unsigned y=0;y<height;++y)image.write(static_cast<const char*>(pixels.pData)+y*pixels.RowPitch,width*4);
    }
    context->Unmap(staging.Get(),0);
    std::cout<<"SAMPLE "<<phase<<" green="<<green<<" outside_blue="<<untouched<<" width="<<width<<" height="<<height<<"\n";
    if(!untouched)throw std::runtime_error("fixture original drawing changed outside tile");return green;
  }
  void reset(){if(context)context->ClearState();fixtureIndices.Reset();fixtureVS.Reset();fixturePS.Reset();fixtureColor.Reset();fixtureDepth.Reset();target.Reset();raster.Reset();blend.Reset();depth.Reset();swap.Reset();context.Reset();device.Reset();}
  ~Scene(){reset();}
};
int wmain(){
  std::cout.setf(std::ios::unitbuf);HWND window=nullptr;HMODULE proxy=nullptr,component=nullptr;int result=1;
  if(GetEnvironmentVariableW(L"SFC_RETURN_CAPTURE_CRASH",nullptr,0)){ULONG bytes=65536;SetThreadStackGuarantee(&bytes);AddVectoredExceptionHandler(1,traceCrash);}
  try{
    wchar_t name[128]{};if(!GetEnvironmentVariableW(L"SFC_REMIX_RETURN_SESSION",name,128))throw std::runtime_error("fixture session");return_path::Mapping mapping(false,name);auto& s=*mapping.state;
    proxy=LoadLibraryW(L".\\dxgi.dll");if(!proxy)throw std::runtime_error("fixture copied ReShade proxy");
    // Limited ReShade deliberately omits automatic add-on loading, but supports
    // external registration and overlay/runtime events. Use those public APIs;
    // no proxy patch, restricted application event or ReShade binary replacement.
    component=GetModuleHandleW(L"SFCRemixReturn.dll");if(!component)throw std::runtime_error("fixture startup component missing");
    WNDCLASSW wc{};wc.lpfnWndProc=proc;wc.hInstance=GetModuleHandleW(nullptr);wc.lpszClassName=L"SFC_ReturnFixture";if(!RegisterClassW(&wc))throw std::runtime_error("fixture class");
    window=CreateWindowW(wc.lpszClassName,L"Offline returned-image fixture — NOT SFC",WS_POPUP,100,100,800,600,nullptr,nullptr,wc.hInstance,nullptr);if(!window)throw std::runtime_error("fixture window");ShowWindow(window,SW_SHOWNOACTIVATE);
    {
      const bool gameOutput=GetEnvironmentVariableW(L"SFC_D3D9_GAME_OUTPUT",nullptr,0)!=0;bool imageSample=false;unsigned resizedFrame=0,imageStartFrame=0,multiReadyAt=0;LONG imageStartDraws=0;
      SourceTimingFixture sourceTiming;Scene scene;if(gameOutput){scene.width=1920;scene.height=1080;}scene.init(window);const auto start=GetTickCount64();bool enabled=false,disabled=false,resized=false,recreated=false,afterResize=false,afterRecreate=false,disconnected=false;unsigned frames=0,stateErrors=0;
      LONG withheld[2]{-1,-1};unsigned withholdPresents=0;bool singleFaultDone=false;
      const bool replacementFaults=replacement::requested()&&GetEnvironmentVariableW(L"SFC_REPLACEMENT_FIXTURE_FAULTS",nullptr,0)!=0;
      const bool observationOnly=GetEnvironmentVariableW(L"SFC_RETURN_OBSERVATION_ONLY",nullptr,0)!=0;
      const bool expanded=GetEnvironmentVariableW(L"SFC_RETURN_EXPANDED_SEARCH",nullptr,0)!=0;
      const bool broad=GetEnvironmentVariableW(L"SFC_REMIX_BROAD_OUTPUT",nullptr,0)!=0;
      const bool snapshot=GetEnvironmentVariableW(L"SFC_REMIX_DEPTH_OUTPUT",nullptr,0)!=0;
      auto* broadHeader=reinterpret_cast<broad_trace::Header*>(reinterpret_cast<BYTE*>(&s)+256);
      auto* search=reinterpret_cast<depth_search::Data*>(reinterpret_cast<BYTE*>(&s)+256);
      if(expanded){
        fakeSearch=search;fakeStart=GetTickCount();slowRequested=GetEnvironmentVariableW(L"SFC_RETURN_SLOW_END",nullptr,0)!=0;
        auto install=reinterpret_cast<BOOL(__cdecl*)(void* const*)>(GetProcAddress(component,"SFCSearchFixtureStart"));
        void* points[]={reinterpret_cast<void*>(&probeBegin),reinterpret_cast<void*>(&probeEnd),reinterpret_cast<void*>(&probeAfterFlush),reinterpret_cast<void*>(&probePresent)};
        if(!install||!install(points))throw std::runtime_error("fixture search installation");
      }
      while(GetTickCount64()-start<(gameOutput?45000ull:25000ull)){
        MSG m{};while(PeekMessageW(&m,nullptr,0,0,PM_REMOVE)){TranslateMessage(&m);DispatchMessageW(&m);}
        if(gameOutput)sourceTiming.publish(frames+1);
        scene.clear();
        if(broad||snapshot||gameOutput){
          // Valid original geometry exercises both public draw callbacks. Same
          // blue as clear; depth testing remains explicitly disabled.
          scene.context->VSSetShader(scene.fixtureVS.Get(),nullptr,0);scene.context->PSSetShader(scene.fixturePS.Get(),nullptr,0);
          scene.context->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);
          scene.context->Draw(3,0);scene.context->IASetIndexBuffer(scene.fixtureIndices.Get(),DXGI_FORMAT_R16_UINT,0);scene.context->DrawIndexed(3,0,0);
          scene.context->IASetIndexBuffer(nullptr,DXGI_FORMAT_UNKNOWN,0);scene.context->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_LINELIST);
          scene.context->VSSetShader(nullptr,nullptr,0);scene.context->PSSetShader(nullptr,nullptr,0);
          auto* rt=scene.target.Get();scene.context->OMSetRenderTargets(1,&rt,nullptr);
        }
        if(expanded){if(!preserved(probeBegin)||!preserved(probeEnd)||!preserved(invokeAfterFlush,true)||!preserved(probePresent))throw std::runtime_error("engine observer stack/flags/FP state changed");}
        const bool synchronized=GetEnvironmentVariableW(L"SFC_D3D9_SYNC_BUFFER",nullptr,0)!=0;
        if(synchronized)scene.stampFrame(200001+frames);
        if(!gameOutput)sourceTiming.publish(frames+1);check(scene.swap->Present(0,0),"fixture present");++frames;if(!scene.statePreserved(broad||snapshot||gameOutput))++stateErrors;
        if(gameOutput){
          auto* base=reinterpret_cast<BYTE*>(sourceTiming.source.mailbox)-sfc_calibration::Offset;auto& pool=*reinterpret_cast<game_output::Pool*>(base+game_output::Offset);
          if(replacementFaults){
            auto& ledger=*reinterpret_cast<replacement::Store*>(base+replacement::Offset);
            if(withholdPresents&&!--withholdPresents){for(unsigned slot=0;slot<2;++slot)if(withheld[slot]>=0){InterlockedExchange(&pool.slots[slot].state,withheld[slot]);withheld[slot]=-1;}}
            if(imageSample&&(frames==imageStartFrame+100||frames==imageStartFrame+200)){
              Sleep(8); // STANDALONE fixture only: let producer finish before taking test leases.
              unsigned taken=0;for(unsigned slot=0;slot<2;++slot){auto& state=pool.slots[slot].state;
                for(LONG prior:{LONG(output_wire::ready),LONG(output_wire::idle)})if(InterlockedCompareExchange(&state,output_wire::acquired,prior)==prior){withheld[slot]=prior;++taken;break;}}
              if(!taken)throw std::runtime_error("No output leases available for deterministic fault");
              withholdPresents=frames==imageStartFrame+100?1u:2u;
              std::cout<<"REPLACEMENT_OUTPUT_WITHHELD presents="<<withholdPresents<<" leases="<<taken<<'\n';
            }
            if(imageSample&&frames==imageStartFrame+110){replacement::Control c{};replacement::read(ledger.control,c);
              if(c.mode!=replacement::Active||!ledger.repeated||ledger.recovered)throw std::runtime_error("Single missed output did not resume replacement");singleFaultDone=true;
              std::cout<<"REPLACEMENT_SINGLE_MISS_RECOVERED repeated="<<ledger.repeated<<'\n';}
            if(imageSample&&frames==imageStartFrame+210){replacement::Control c{};replacement::read(ledger.control,c);
              if(!singleFaultDone||c.mode!=replacement::LatchedOriginal||!ledger.recovered||ledger.repeat_max>2)throw std::runtime_error("Sustained missed output failed safe native recovery");
              std::cout<<"REPLACEMENT_SUSTAINED_MISS_NATIVE repeat_max="<<ledger.repeat_max<<" recovered="<<ledger.recovered<<'\n';}
          }
          if(sourceTiming.cohort.store&&!multiReadyAt&&sourceTiming.cohort.store->header.asset_ready==static_cast<LONG>(sourceTiming.rows.size())){multiReadyAt=frames;std::cout<<"MULTISCENE_BOTH_READY frame="<<frames<<" first_draws="<<pool.stats.drawn<<'\n';}
          const bool cohortSettled=replacement::requested()||!sourceTiming.cohort.store||(multiReadyAt&&frames>=multiReadyAt+60);
          // A synchronous test-only GPU readback can exceed the live 50ms
          // authorization lease. Measure continuous delivery BEFORE readback;
          // never renew production authorization to conceal a diagnostic stall.
          if(!imageSample&&cohortSettled&&pool.stats.drawn&&pool.stats.frame+(synchronized?1u:0u)==200000+frames){if(!replacement::requested())scene.shipSample(synchronized?pool.stats.frame:0);imageSample=true;imageStartFrame=frames;imageStartDraws=pool.stats.drawn;}
          if(!replacement::requested()&&synchronized&&imageSample&&frames==imageStartFrame+200){return_path::write(s.enabled,0);std::cout<<"BUFFER_FIXTURE_DISABLED frame="<<frames<<'\n';}
          if(!replacement::requested()&&synchronized&&imageSample&&frames==imageStartFrame+205){return_path::write(s.enabled,1);std::cout<<"BUFFER_FIXTURE_REENABLED frame="<<frames<<'\n';}
          if(!resized&&imageSample&&frames>=imageStartFrame+600){std::cout<<"GAME_DELIVERY_WINDOW frames="<<frames-imageStartFrame<<" draws="<<pool.stats.drawn-imageStartDraws<<'\n';
            if(replacementFaults)scene.shipSample(200000+frames,false,false); // Verify the recovered native frame,not stale ship pixels.
            else if(replacement::requested())scene.shipSample(pool.stats.frame); // A held complete frame must retain its own HUD stamp too.
            else if(!replacement::requested()&&GetEnvironmentVariableW(L"SFC_FIXTURE_SHIP_SNAPSHOT",nullptr,0)&&pool.stats.frame+(synchronized?1u:0u)==200000+frames)scene.shipSample(synchronized?pool.stats.frame:0,true);
            scene.resize();resized=true;resizedFrame=frames;}
          if(resized&&!recreated&&frames>=resizedFrame+90){scene.reset();scene.width=1920;scene.height=1080;scene.init(window);recreated=true;}
          if(recreated&&frames>=resizedFrame+180)break;
        }
        if(sourceTiming.enabled){if(!gameOutput&&frames==(sourceTiming.liveEnabled?450u:90u)){scene.resize();resized=true;}if(!gameOutput&&frames==(sourceTiming.liveEnabled?900u:180u)){scene.reset();scene.init(window);recreated=true;}if(!gameOutput&&frames>=(sourceTiming.liveEnabled?1800u:210u))break;if(!sourceTiming.liveEnabled)Sleep(16);else if(synchronized)Sleep(13);continue;}
        if(snapshot){if(GetTickCount64()-start>16000)break;Sleep(16);continue;}
        if(broad){
          if(frames==90){scene.resize();resized=true;}
          if(frames==180){scene.reset();scene.init(window);recreated=true;}
          if(broadHeader->status>=3)break;
          Sleep(16);continue;
        }
        if(expanded){
          if(frames==90){scene.resize();resized=true;}
          if(frames==180){scene.reset();scene.init(window);recreated=true;}
          if(search->status==depth_search::Removed)break;
          Sleep(16);continue;
        }
        if(observationOnly){
          if(return_path::read(s.visibilitySamples)>=3&&!resized){scene.resize();resized=true;}
          if(return_path::read(s.visibilitySamples)>=5&&!recreated){scene.reset();scene.init(window);recreated=true;}
          if(return_path::read(s.visibilitySamples)==8)break;
          Sleep(16);continue;
        }
        if(!enabled&&return_path::read(s.drawCount)>30){if(scene.sample("enabled",true)<1000)throw std::runtime_error("returned image missing");enabled=true;}
        if(enabled&&!disabled&&!return_path::read(s.enabled)){if(scene.sample("disabled",false)>10)throw std::runtime_error("disabled image visible");disabled=true;}
        if(disabled&&!resized&&return_path::read(s.enabled)){scene.resize();SetWindowPos(window,nullptr,100,100,1024,768,SWP_NOACTIVATE|SWP_NOZORDER);resized=true;}
        if(resized&&!afterResize&&return_path::read(s.ready)&&return_path::read(s.epoch)>=2&&return_path::read(s.presentedEpoch)==return_path::read(s.epoch)&&return_path::read(s.drawCount)>80){if(scene.sample("resized",false)<1000)throw std::runtime_error("image missing after resize");afterResize=true;}
        if(afterResize&&!recreated){scene.reset();Sleep(50);scene.init(window);recreated=true;}
        if(recreated&&!afterRecreate&&return_path::read(s.ready)&&return_path::read(s.epoch)>=3&&return_path::read(s.presentedEpoch)==return_path::read(s.epoch)&&return_path::read(s.drawCount)>100){if(scene.sample("recreated",false)<1000)throw std::runtime_error("image missing after recreation");afterRecreate=true;}
        if(afterRecreate&&!disconnected&&!return_path::fresh(s.renderedAt,return_path::now(),s.qpcFrequency)){
          // Allow one presented frame after expiry to remove cached draw list.
          scene.clear();check(scene.swap->Present(0,0),"fixture disconnect present");
          if(scene.sample("disconnected",false)>10)throw std::runtime_error("stale renderer image visible");disconnected=true;break;
        }
        Sleep(16);
      }
      if(sourceTiming.enabled){std::cout<<"SOURCE_TIMING_END frames="<<frames<<" state_errors="<<stateErrors<<" resized="<<resized<<" recreated="<<recreated<<'\n';if(stateErrors||!resized||!recreated)throw std::runtime_error("source timing state/resize/recreation");}
      else if(snapshot){
        std::cout<<"DEPTH_SNAPSHOT_END frames="<<frames<<" state_errors="<<stateErrors<<"\n";
        if(stateErrors)throw std::runtime_error("snapshot fixture original state changed");
      }else if(broad){
        std::cout<<"BROAD_END frames="<<frames<<" state_errors="<<stateErrors<<" status="<<broadHeader->status<<" drops="<<broadHeader->dropped<<" resized="<<resized<<" recreated="<<recreated<<"\n";
        if(stateErrors||broadHeader->status!=3||broadHeader->error||!resized||!recreated)throw std::runtime_error("broad fixture incomplete");
      }else if(expanded){
        std::cout<<"SEARCH_END frames="<<frames<<" state_errors="<<stateErrors<<" restored="<<search->restoredMask<<" seen="<<search->seenMask<<"\n";
        if(stateErrors||search->status!=depth_search::Removed||search->restoredMask!=15||search->seenMask!=63)throw std::runtime_error("expanded search restoration/coverage failed");
        if(slowRequested&&(!slowDone||search->reserved!=2))throw std::runtime_error("slow in-flight restoration test incomplete");
      }else if(observationOnly){
        std::cout<<"OBSERVATION_END frames="<<frames<<" state_errors="<<stateErrors<<" samples="<<return_path::read(s.visibilitySamples)<<" resized="<<resized<<" recreated="<<recreated<<"\n";
        if(stateErrors||return_path::read(s.visibilitySamples)!=8||!resized||!recreated)throw std::runtime_error("observation fixture incomplete");
      }else{
        std::cout<<"FIXTURE_END frames="<<frames<<" state_errors="<<stateErrors<<" phases="<<enabled<<disabled<<afterResize<<afterRecreate<<disconnected<<"\n";
        if(!enabled||!disabled||!afterResize||!afterRecreate||!disconnected||stateErrors)throw std::runtime_error("fixture phases/state incomplete");
      }
      result=0;
    }
  }catch(const std::exception& e){std::cout<<"FIXTURE_FAILED "<<e.what()<<"\n";}
  if(window)DestroyWindow(window);if(proxy)FreeLibrary(proxy);return result;
}
