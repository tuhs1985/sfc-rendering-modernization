// Default-off, three read-only GPU snapshots. Not a replacement/occlusion contract.
#pragma once
#include <d3dcompiler.h>
#include <atomic>
#include <algorithm>
#include <cstring>
#include <cstdio>
#include "../m1_component/m1_present_calibration.h"
namespace depth_snapshot {
using Microsoft::WRL::ComPtr;
constexpr unsigned MaxWidth=1920,MaxHeight=1080,Shots=3;
constexpr size_t PlaneBytes=size_t(MaxWidth)*MaxHeight*4,SlotBytes=PlaneBytes*2;
// 32 uint64 fields followed by 16 rows of four uint64 fields (768 bytes).
struct Header {uint64_t fields[32]{};uint64_t states[16][4]{};};
static_assert(sizeof(Header)==768);
inline bool supported(const D3D11_TEXTURE2D_DESC& d){
 return d.Width&&d.Height&&d.Width<=MaxWidth&&d.Height<=MaxHeight&&
 d.MipLevels==1&&d.ArraySize==1&&d.Format==DXGI_FORMAT_R32_TYPELESS&&
 d.SampleDesc.Count==8&&(d.BindFlags&D3D11_BIND_SHADER_RESOURCE)&&
 (d.BindFlags&D3D11_BIND_DEPTH_STENCIL);
}
inline constexpr char Shader[]=R"(
Texture2DMS<float,8> src:register(t0);
float4 main(float4 p:SV_Position):SV_Target{
 int2 xy=int2(p.xy)*2;
 float a=src.Load(xy,0),lo=a,hi=a,sum=a;
 [unroll]for(int s=1;s<8;++s){float v=src.Load(xy,s);lo=min(lo,v);hi=max(hi,v);sum+=v;}
 return float4(a,lo,hi,sum/8.0);
})";
inline constexpr char Vertex[]=R"(
float4 main(uint id:SV_VertexID):SV_Position{
 float2 p[3]={float2(-1,-1),float2(-1,3),float2(3,-1)};
 return float4(p[id],0,1);
})";
enum class Stage:unsigned {None,Feature,CompileVS,CompilePS,CreateVS,CreatePS,
 Deferred,Raster,DepthState,OutputTexture,OutputView,StagingDepth,SourceView,Query,
 StateOverflow,Poll,Timeout,MapDepth,MapColor,ColorDescriptor,ColorChanged,
 StagingColor,Commands};
class Capture {
 struct Slot {std::atomic<LONG> ready{0};Header h{};BYTE* bytes=nullptr;
  uint64_t stamp[16]{};sfc_calibration::Snapshot semantic{};};
 Slot slots[Shots];wchar_t directory[1024]{};HANDLE worker=nullptr;
 sfc_calibration::Reader semantic;
 DWORD drawEngineFrame=0,lastCapturedEngineFrame=0;
 std::atomic<bool> stopping{false};std::atomic<unsigned> files{0},ioError{0};
 return_path::State* control=nullptr;
 ComPtr<ID3D11Device> device;ComPtr<ID3D11DeviceContext> context,deferred;
 ComPtr<ID3D11VertexShader> vertex;ComPtr<ID3D11PixelShader> pixel;
 ComPtr<ID3D11RasterizerState> raster;ComPtr<ID3D11DepthStencilState> noDepth;
 ComPtr<ID3D11Texture2D> source,output,readDepth,readColor;
 ComPtr<ID3D11ShaderResourceView> sourceView;ComPtr<ID3D11RenderTargetView> outputView;
 ComPtr<ID3D11Query> query;
 uint64_t resourceEpoch=0,frame=0,gate=0,submitted=0,lastDraw=~uint64_t(0);unsigned issued=0,pending=Shots,failures=0;
 bool disabled=false,ambiguous=false;Header states{};unsigned stateCount=0;
 D3D11_TEXTURE2D_DESC sourceDesc{},colorDesc{};
 unsigned featureLevel=0;Stage failedStage=Stage::None;HRESULT failedResult=S_OK;
 static DWORD WINAPI run(void* p){return static_cast<Capture*>(p)->writeLoop();}
 DWORD writeLoop(){
  for(;;){
   bool busy=false;
   for(unsigned i=0;i<Shots;++i)if(slots[i].ready.load(std::memory_order_acquire)==1){
    busy=true;auto& s=slots[i];wchar_t path[1100]{};
    swprintf_s(path,L"%s\\depth-%u.bin",directory,i);
    HANDLE file=CreateFileW(path,GENERIC_WRITE,0,nullptr,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,nullptr);
    DWORD n=0;const auto bytes=static_cast<DWORD>(s.h.fields[14]+s.h.fields[15]);
    bool ok=file!=INVALID_HANDLE_VALUE;
    if(ok){ok=WriteFile(file,&s.h,sizeof(s.h),&n,nullptr)&&n==sizeof(s.h);
     if(ok)ok=WriteFile(file,s.bytes,bytes,&n,nullptr)&&n==bytes;
     CloseHandle(file);}
    if(ok&&semantic.requested){
     swprintf_s(path,L"%s\\semantic-%u.bin",directory,i);
     file=CreateFileW(path,GENERIC_WRITE,0,nullptr,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,nullptr);
     ok=file!=INVALID_HANDLE_VALUE;
     if(ok){ok=WriteFile(file,s.stamp,sizeof(s.stamp),&n,nullptr)&&n==sizeof(s.stamp);
      if(ok)ok=WriteFile(file,&s.semantic,sizeof(s.semantic),&n,nullptr)&&n==sizeof(s.semantic);
      CloseHandle(file);}
    }
    if(ok)++files;else ++ioError;
    s.ready.store(2,std::memory_order_release);
   }
   if(stopping.load(std::memory_order_acquire)&&!busy)break;
   Sleep(5);
  }
  wchar_t path[1100]{};swprintf_s(path,L"%s\\depth-status.json",directory);
  HANDLE f=CreateFileW(path,GENERIC_WRITE,0,nullptr,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,nullptr);
  if(f!=INVALID_HANDLE_VALUE){char b[768]{};int n=sprintf_s(b,"{\"files\":%u,\"io_errors\":%u,\"gpu_failures\":%u,\"ambiguous\":%s,\"issued\":%u,\"pending_abandoned\":%s,\"reader\":\"ps_4_1\",\"feature_level\":%u,\"failure_stage\":%u,\"failure_hresult\":%u,\"source_width\":%u,\"source_height\":%u,\"source_format\":%u,\"source_samples\":%u,\"color_width\":%u,\"color_height\":%u,\"color_format\":%u}",files.load(),ioError.load(),failures,ambiguous?"true":"false",issued,pending<Shots?"true":"false",featureLevel,static_cast<unsigned>(failedStage),static_cast<unsigned>(failedResult),sourceDesc.Width,sourceDesc.Height,static_cast<unsigned>(sourceDesc.Format),sourceDesc.SampleDesc.Count,colorDesc.Width,colorDesc.Height,static_cast<unsigned>(colorDesc.Format));DWORD done=0;WriteFile(f,b,static_cast<DWORD>(n),&done,nullptr);CloseHandle(f);}
  return 0;
 }
 void fail(Stage stage,HRESULT h){if(!failures){failedStage=stage;failedResult=h;}++failures;disabled=true;}
 bool checked(HRESULT h,Stage stage){if(SUCCEEDED(h))return true;fail(stage,h);return false;}
 bool setup(){
  D3D11_TEXTURE2D_DESC d{};d.Width=(sourceDesc.Width+1)/2;d.Height=(sourceDesc.Height+1)/2;
  d.MipLevels=d.ArraySize=1;d.SampleDesc.Count=1;d.Format=DXGI_FORMAT_R32G32B32A32_FLOAT;d.Usage=D3D11_USAGE_DEFAULT;d.BindFlags=D3D11_BIND_RENDER_TARGET;
  if(!checked(device->CreateTexture2D(&d,nullptr,&output),Stage::OutputTexture)||!checked(device->CreateRenderTargetView(output.Get(),nullptr,&outputView),Stage::OutputView))return false;
  d.BindFlags=0;d.Usage=D3D11_USAGE_STAGING;d.CPUAccessFlags=D3D11_CPU_ACCESS_READ;
  if(!checked(device->CreateTexture2D(&d,nullptr,&readDepth),Stage::StagingDepth))return false;
  D3D11_SHADER_RESOURCE_VIEW_DESC v{};v.Format=DXGI_FORMAT_R32_FLOAT;v.ViewDimension=D3D11_SRV_DIMENSION_TEXTURE2DMS;
  if(!checked(device->CreateShaderResourceView(source.Get(),&v,&sourceView),Stage::SourceView))return false;
  D3D11_QUERY_DESC q{D3D11_QUERY_EVENT,0};return checked(device->CreateQuery(&q,&query),Stage::Query);
 }
public:
 bool prepare(return_path::State* s,const wchar_t* path){
  if(!s||!path||wcslen(path)>1000)return false;control=s;wcscpy_s(directory,path);
  if(!semantic.prepare())return false;
  for(auto& slot:slots){slot.bytes=static_cast<BYTE*>(VirtualAlloc(nullptr,SlotBytes,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE));if(!slot.bytes)return false;}
  worker=CreateThread(nullptr,0,run,this,0,nullptr);return worker!=nullptr;
 }
 // Before tactical capture: compile once, not during draw/Present/readback.
 void init(ID3D11Device* d){
  if(device||disabled||stopping)return;device=d;device->GetImmediateContext(&context);
  featureLevel=device->GetFeatureLevel();
  if(featureLevel<D3D_FEATURE_LEVEL_10_1){fail(Stage::Feature,E_NOTIMPL);return;}
  ComPtr<ID3DBlob> code,error;
  if(!checked(D3DCompile(Vertex,sizeof(Vertex)-1,nullptr,nullptr,nullptr,"main","vs_4_1",D3DCOMPILE_ENABLE_STRICTNESS,0,&code,&error),Stage::CompileVS))return;
  if(!checked(device->CreateVertexShader(code->GetBufferPointer(),code->GetBufferSize(),nullptr,&vertex),Stage::CreateVS))return;
  code.Reset();error.Reset();
  if(!checked(D3DCompile(Shader,sizeof(Shader)-1,nullptr,nullptr,nullptr,"main","ps_4_1",D3DCOMPILE_ENABLE_STRICTNESS,0,&code,&error),Stage::CompilePS))return;
  if(!checked(device->CreatePixelShader(code->GetBufferPointer(),code->GetBufferSize(),nullptr,&pixel),Stage::CreatePS))return;
  if(!checked(device->CreateDeferredContext(0,&deferred),Stage::Deferred))return;
  D3D11_RASTERIZER_DESC r{};r.FillMode=D3D11_FILL_SOLID;r.CullMode=D3D11_CULL_NONE;r.DepthClipEnable=TRUE;
  if(!checked(device->CreateRasterizerState(&r,&raster),Stage::Raster))return;
  D3D11_DEPTH_STENCIL_DESC ds{};ds.DepthFunc=D3D11_COMPARISON_ALWAYS;
  checked(device->CreateDepthStencilState(&ds,&noDepth),Stage::DepthState);
 }
 // Actual native DSV at original draw time, not a guessed process-local label.
 void draw(uint64_t nativeContext=0){
  if(!context||disabled||!return_path::read(control->armed)||return_path::read(control->stop))return;
  if(nativeContext&&nativeContext!=reinterpret_cast<uintptr_t>(context.Get()))return;
  ComPtr<ID3D11DepthStencilView> view;context->OMGetRenderTargets(0,nullptr,&view);if(!view)return;
  ComPtr<ID3D11Resource> r;view->GetResource(&r);ComPtr<ID3D11Texture2D> texture;
  if(FAILED(r.As(&texture)))return;D3D11_TEXTURE2D_DESC d{};texture->GetDesc(&d);if(!supported(d))return;
  if(source&&source.Get()!=texture.Get()){ambiguous=true;disabled=true;return;}
  if(!source){source=texture;sourceDesc=d;++resourceEpoch;}
  lastDraw=frame;
  if(semantic.requested){const auto f=sfc_calibration::frame(semantic.mailbox);
   if(!f||(drawEngineFrame&&drawEngineFrame!=f))drawEngineFrame=0xffffffffu;
   else drawEngineFrame=f;}
  ComPtr<ID3D11DepthStencilState> state;UINT reference=0;context->OMGetDepthStencilState(&state,&reference);
  D3D11_DEPTH_STENCIL_DESC desc{};
  if(state)state->GetDesc(&desc);else {desc.DepthEnable=TRUE;desc.DepthWriteMask=D3D11_DEPTH_WRITE_MASK_ALL;desc.DepthFunc=D3D11_COMPARISON_LESS;}
  const uint64_t flags=uint64_t(desc.DepthEnable)|(uint64_t(desc.DepthWriteMask)<<8)|(uint64_t(desc.StencilEnable)<<16);
  unsigned index=0;for(;index<stateCount;++index)if(states.states[index][0]==flags&&states.states[index][1]==desc.DepthFunc&&states.states[index][2]==reference)break;
  if(index==stateCount){if(stateCount==16){fail(Stage::StateOverflow,HRESULT_FROM_WIN32(ERROR_BUFFER_OVERFLOW));return;}++stateCount;states.states[index][0]=flags;states.states[index][1]=desc.DepthFunc;states.states[index][2]=reference;}
  ++states.states[index][3];
 }
 void present(ID3D11Texture2D* backbuffer,uint64_t now=GetTickCount64()){
  if(!context||disabled||stopping)return;++frame;
  const DWORD drawnEngineFrame=drawEngineFrame;drawEngineFrame=0;
  if(!return_path::read(control->armed)||return_path::read(control->stop))return;
  if(!gate)gate=now;
  if(pending<Shots){
   BOOL done=FALSE;const auto h=context->GetData(query.Get(),&done,sizeof(done),D3D11_ASYNC_GETDATA_DONOTFLUSH);
   if(!checked(h,Stage::Poll))return;
   if(h!=S_OK||!done){if(now-submitted>2000)fail(Stage::Timeout,HRESULT_FROM_WIN32(WAIT_TIMEOUT));return;}
   D3D11_MAPPED_SUBRESOURCE depth{},color{};
   auto a=context->Map(readDepth.Get(),0,D3D11_MAP_READ,D3D11_MAP_FLAG_DO_NOT_WAIT,&depth);
   if(a==DXGI_ERROR_WAS_STILL_DRAWING)return;if(!checked(a,Stage::MapDepth))return;
   auto b=context->Map(readColor.Get(),0,D3D11_MAP_READ,D3D11_MAP_FLAG_DO_NOT_WAIT,&color);
   if(b==DXGI_ERROR_WAS_STILL_DRAWING){context->Unmap(readDepth.Get(),0);return;}
   if(!checked(b,Stage::MapColor)){context->Unmap(readDepth.Get(),0);return;}
   auto& slot=slots[pending];const auto dw=static_cast<unsigned>(slot.h.fields[3]),dh=static_cast<unsigned>(slot.h.fields[4]);
   for(unsigned y=0;y<dh;++y)std::memcpy(slot.bytes+size_t(y)*dw*16,static_cast<BYTE*>(depth.pData)+size_t(y)*depth.RowPitch,size_t(dw)*16);
   for(unsigned y=0;y<colorDesc.Height;++y)std::memcpy(slot.bytes+slot.h.fields[14]+size_t(y)*colorDesc.Width*4,static_cast<BYTE*>(color.pData)+size_t(y)*color.RowPitch,size_t(colorDesc.Width)*4);
   context->Unmap(readColor.Get(),0);context->Unmap(readDepth.Get(),0);
   slot.ready.store(1,std::memory_order_release);pending=Shots;
  }
  if(issued==Shots||!source||!backbuffer||lastDraw+1!=frame||now-gate<2000+uint64_t(issued)*5000)return;
  sfc_calibration::Snapshot observation{};
  if(semantic.requested && (!sfc_calibration::read(semantic.mailbox,observation)||
     observation.frame!=drawnEngineFrame||drawnEngineFrame==0xffffffffu||
     drawnEngineFrame==lastCapturedEngineFrame))return;
  if(semantic.requested){bool qualified=false;
   for(const auto& r:observation.owner)if(r[1]&&r[4]==1&&r[7]&&r[48]==1){
    if(r[47]!=GetCurrentThreadId())return;qualified=true;}
   if(!qualified)return;}
  if(!output&&!setup())return;
  D3D11_TEXTURE2D_DESC c{};backbuffer->GetDesc(&c);
  if(!c.Width||!c.Height||c.Width>MaxWidth||c.Height>MaxHeight||c.SampleDesc.Count!=1||
     c.Width!=sourceDesc.Width||c.Height!=sourceDesc.Height||c.MipLevels!=1||c.ArraySize!=1||
     (c.Format!=DXGI_FORMAT_B8G8R8A8_UNORM&&c.Format!=DXGI_FORMAT_R8G8B8A8_UNORM)){colorDesc=c;fail(Stage::ColorDescriptor,E_NOTIMPL);return;}
  if(readColor&&(colorDesc.Width!=c.Width||colorDesc.Height!=c.Height||colorDesc.Format!=c.Format)){fail(Stage::ColorChanged,E_NOTIMPL);return;}
  if(!readColor){colorDesc=c;c.Usage=D3D11_USAGE_STAGING;c.BindFlags=c.MiscFlags=0;c.CPUAccessFlags=D3D11_CPU_ACCESS_READ;
   if(!checked(device->CreateTexture2D(&c,nullptr,&readColor),Stage::StagingColor))return;}
  // A private deferred context + RestoreContextState TRUE isolates ALL original
  // immediate-context bindings. Never bind/clear the original depth as output.
  ID3D11ShaderResourceView* srv=sourceView.Get();ID3D11RenderTargetView* rt=outputView.Get();
  deferred->ClearState();deferred->OMSetRenderTargets(1,&rt,nullptr);deferred->OMSetDepthStencilState(noDepth.Get(),0);
  deferred->RSSetState(raster.Get());D3D11_VIEWPORT vp{0,0,static_cast<float>((sourceDesc.Width+1)/2),static_cast<float>((sourceDesc.Height+1)/2),0,1};deferred->RSSetViewports(1,&vp);
  deferred->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);
  deferred->VSSetShader(vertex.Get(),nullptr,0);deferred->PSSetShader(pixel.Get(),nullptr,0);deferred->PSSetShaderResources(0,1,&srv);
  deferred->Draw(3,0);
  deferred->ClearState();deferred->CopyResource(readDepth.Get(),output.Get());deferred->CopyResource(readColor.Get(),backbuffer);
  deferred->End(query.Get());ComPtr<ID3D11CommandList> commands;
  if(!checked(deferred->FinishCommandList(FALSE,&commands),Stage::Commands))return;
  if(semantic.requested&&sfc_calibration::frame(semantic.mailbox)!=observation.frame)return;
  context->ExecuteCommandList(commands.Get(),TRUE);
  auto& h=slots[issued].h;h=states;
  uint64_t values[]={0x44535031,1,sizeof(Header),(sourceDesc.Width+1)/2,(sourceDesc.Height+1)/2,colorDesc.Width,colorDesc.Height,sourceDesc.Width,sourceDesc.Height,8,2,return_path::now(),frame,resourceEpoch,uint64_t((sourceDesc.Width+1)/2)*((sourceDesc.Height+1)/2)*16,uint64_t(colorDesc.Width)*colorDesc.Height*4,static_cast<uint64_t>(colorDesc.Format),stateCount};
  std::memcpy(h.fields,values,sizeof(values));pending=issued++;submitted=now;
  if(semantic.requested){auto& slot=slots[pending];slot.semantic=observation;
   uint64_t stamp[]={0x31504353,1,128+sizeof(observation),h.fields[11],frame,resourceEpoch,
      observation.frame,drawnEngineFrame,GetCurrentProcessId(),GetCurrentThreadId()};
   std::memcpy(slot.stamp,stamp,sizeof(stamp));lastCapturedEngineFrame=observation.frame;}
 }
 void shutdown(){
  if(!worker)return;
  // Called from runtime destruction, NOT DllMain. No future device callbacks
  // accepted. Writer touches only fixed CPU slots, never COM/game resources.
  disabled=true;sourceView.Reset();source.Reset();outputView.Reset();output.Reset();readDepth.Reset();readColor.Reset();query.Reset();vertex.Reset();pixel.Reset();raster.Reset();noDepth.Reset();deferred.Reset();context.Reset();device.Reset();
  semantic.close();
  stopping.store(true,std::memory_order_release);
  if(WaitForSingleObject(worker,250)==WAIT_OBJECT_0){CloseHandle(worker);worker=nullptr;for(auto& slot:slots){VirtualFree(slot.bytes,0,MEM_RELEASE);slot.bytes=nullptr;}}
  // A stalled writer retains its CPU slots until process exit; never hot unload.
 }
};
// Intentionally resident on abnormal process teardown. Normal runtime destroy
// releases GPU resources and joins writer; DllMain never waits on loader lock.
inline Capture* capture=nullptr;
inline thread_local bool nested=false;
inline bool onDraw(reshade::api::command_list* c,uint32_t,uint32_t,uint32_t,uint32_t){
 if(capture&&!nested&&c->get_device()->get_api()==reshade::api::device_api::d3d11){nested=true;capture->draw(c->get_native());nested=false;}return false;
}
inline bool onIndexed(reshade::api::command_list* c,uint32_t,uint32_t,uint32_t,int32_t,uint32_t){return onDraw(c,0,0,0,0);}
inline void events(bool add){
 if(add){reshade::register_event<reshade::addon_event::draw>(onDraw);reshade::register_event<reshade::addon_event::draw_indexed>(onIndexed);}
 else {reshade::unregister_event<reshade::addon_event::draw>(onDraw);reshade::unregister_event<reshade::addon_event::draw_indexed>(onIndexed);}
}
}
