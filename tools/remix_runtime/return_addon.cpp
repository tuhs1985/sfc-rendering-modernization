#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <d3d11.h>
#include <dxgi.h>
#include <wrl/client.h>
#include <memory>
#include <imgui.h>
#include <reshade.hpp>
#include <detours.h>
#include "return_wire.h"
#include "depth_search.h"
#include "broad_events.h"
#include "depth_snapshot.h"
#include "source_timing_addon.h"
#include "d3d9_game_receiver.h"
#ifdef SFC_LIVE_RETURN
#include "ship_live_receiver.h"
#endif
using Microsoft::WRL::ComPtr;
// A normal import from the EXISTING copied proxy ensures ReShade initializes
// before this external component. No replacement or forwarder is supplied.
extern "C" __declspec(dllimport) bool ReShadeRegisterAddon(void*,uint32_t);
extern "C" __declspec(dllexport) const char* NAME="SFC Remix return-path proof";
extern "C" __declspec(dllexport) const char* DESCRIPTION="Default-off additive diagnostic image; no ship suppression.";
namespace {
wchar_t session[128]{};bool registered=false;
std::unique_ptr<return_path::Mapping> channel;
reshade::api::effect_runtime* activeRuntime=nullptr;
ComPtr<ID3D11Device> device;ComPtr<ID3D11DeviceContext> context;
ComPtr<ID3D11Texture2D> sharedTexture,displayTexture;
ComPtr<ID3D11ShaderResourceView> displayView;ComPtr<ID3D11Query> copyComplete;
LONG pending=0;uint64_t visibleAt=0;bool firstPacket=true;
bool inspectVisibility=false,inspectEarly=false;ULONGLONG lastVisibility=0;
bool searchMode=false,searchFixture=false;depth_search::Search search;
bool broadMode=false;
bool sourceTimingRequested=false;std::unique_ptr<source_timing::Observer> sourceTiming;
bool directGameRequested=false;std::unique_ptr<d3d9_game::Receiver> directGame;
ComPtr<ID3D11RenderTargetView> directTargets[4];uint64_t directBack[4]{};uint32_t directCount=0;
bool directDraw(reshade::api::command_list* c,uint32_t,uint32_t,uint32_t,uint32_t){if(directGame)directGame->observe(c->get_native());return false;}
bool directIndexed(reshade::api::command_list* c,uint32_t,uint32_t,uint32_t,int32_t,uint32_t){return directDraw(c,0,0,0,0);}
bool directClear(reshade::api::command_list* c,reshade::api::resource_view,const float*,const uint8_t*,uint32_t,const reshade::api::rect*){if(directGame)directGame->cleared(c->get_native());return false;}
#ifdef SFC_LIVE_RETURN
std::unique_ptr<ship_live::Receiver> liveReceiver;
bool visibleShip=false;
bool sceneDepthTest=false;
bool sceneDraw(reshade::api::command_list* c,uint32_t,uint32_t,uint32_t,uint32_t){
 if(liveReceiver&&sceneDepthTest)liveReceiver->observeDepth(c->get_native());return false;
}
bool sceneIndexed(reshade::api::command_list* c,uint32_t,uint32_t,uint32_t,int32_t,uint32_t){return sceneDraw(c,0,0,0,0);}
bool sceneClear(reshade::api::command_list* c,reshade::api::resource_view,const float*,const uint8_t*,uint32_t,const reshade::api::rect*){
 if(liveReceiver&&sceneDepthTest)liveReceiver->depthCleared(c->get_native());return false;
}
#endif
void inspectDepth(return_path::State& s){
  // Presence/descriptor only, NOT proof of tactical depth or occlusion. No
  // resource creation, copies, readback, rebinding, retained COM objects or waits.
  if(!inspectVisibility||!return_path::read(s.armed)||return_path::read(s.stop)||
     return_path::read(s.visibilitySamples)>=8)return;
  const auto now=GetTickCount64();if(lastVisibility&&now-lastVisibility<1000)return;
  lastVisibility=now;ComPtr<ID3D11DepthStencilView> bound;
  context->OMGetRenderTargets(0,nullptr,&bound);
  if(bound){
    D3D11_DEPTH_STENCIL_VIEW_DESC view{};bound->GetDesc(&view);
    ComPtr<ID3D11Resource> resource;bound->GetResource(&resource);
    ComPtr<ID3D11Texture2D> texture;
    if(SUCCEEDED(resource.As(&texture))){
      D3D11_TEXTURE2D_DESC desc{};texture->GetDesc(&desc);
      return_path::write(s.depthWidth,static_cast<LONG>(desc.Width));
      return_path::write(s.depthHeight,static_cast<LONG>(desc.Height));
      return_path::write(s.depthFormat,static_cast<LONG>(desc.Format));
      return_path::write(s.depthViewFormat,static_cast<LONG>(view.Format));
      return_path::write(s.depthBindFlags,static_cast<LONG>(desc.BindFlags));
      return_path::write(s.depthMultisamples,static_cast<LONG>(desc.SampleDesc.Count));
      InterlockedIncrement(&s.depthPresentSamples);
    }
  }
  return_path::write(s.visibilityScope,inspectEarly?2:1);
  return_path::write(s.visibilityVersion,1);InterlockedIncrement(&s.visibilitySamples);
}
void hide(){visibleAt=0;}
void releaseResources(){
  directGame.reset();for(auto& target:directTargets)target.Reset();directCount=0;
  sourceTiming.reset();
#ifdef SFC_LIVE_RETURN
  if(liveReceiver){liveReceiver->stop();liveReceiver.reset();}
#endif
  if(depth_snapshot::capture)depth_snapshot::capture->shutdown();
  if(searchMode)search.setContext(nullptr);
  if(channel){return_path::write(channel->state->ready,0);channel->state->sharedHandle=0;InterlockedIncrement(&channel->state->clearCount);}
  hide();pending=0;copyComplete.Reset();displayView.Reset();displayTexture.Reset();sharedTexture.Reset();context.Reset();device.Reset();activeRuntime=nullptr;
}
void failure(LONG code){if(channel){return_path::write(channel->state->error,code);return_path::write(channel->state->ready,0);}hide();}
void init(reshade::api::effect_runtime* runtime){
  if(activeRuntime||runtime->get_device()->get_api()!=reshade::api::device_api::d3d11)return;
  uint32_t width=0,height=0;runtime->get_screenshot_width_and_height(&width,&height);
  if(channel){return_path::write(channel->state->lastWidth,static_cast<LONG>(width));return_path::write(channel->state->lastHeight,static_cast<LONG>(height));}
  if(!return_path::displaySupported(static_cast<float>(width),static_cast<float>(height)))return;
  try{
    if(!channel)channel=std::make_unique<return_path::Mapping>(false,session);
    auto& s=*channel->state;if(return_path::read(s.stop)||!return_path::valid(s))return;
    device=reinterpret_cast<ID3D11Device*>(static_cast<uintptr_t>(runtime->get_device()->get_native()));
    device->GetImmediateContext(&context);
    if(sourceTimingRequested){sourceTiming=std::make_unique<source_timing::Observer>();sourceTiming->prepare();
      if(directGameRequested){
       directCount=runtime->get_back_buffer_count();if(!directCount||directCount>4)throw std::runtime_error("Bounded game backbuffer count");
       for(unsigned i=0;i<directCount;++i){directBack[i]=runtime->get_back_buffer(i).handle;auto* back=reinterpret_cast<ID3D11Texture2D*>(static_cast<uintptr_t>(directBack[i]));
        if(!back)throw std::runtime_error("Game backbuffer missing");ship_triplet::checked(device->CreateRenderTargetView(back,nullptr,&directTargets[i]),"Game target view");}
       directGame=std::make_unique<d3d9_game::Receiver>(*channel,device.Get());
      }
      activeRuntime=runtime;s.gamePid=GetCurrentProcessId();InterlockedIncrement(&s.epoch);return_path::write(s.ready,1);return;}
    if(depth_snapshot::capture)depth_snapshot::capture->init(device.Get());
    if(searchMode)search.setContext(context.Get());
#ifdef SFC_LIVE_RETURN
    liveReceiver=std::make_unique<ship_live::Receiver>(*channel,device.Get());
    activeRuntime=runtime;s.gamePid=GetCurrentProcessId();InterlockedIncrement(&s.epoch);
    return_path::write(s.ready,1);return;
#else
    D3D11_TEXTURE2D_DESC desc{};desc.Width=desc.Height=256;desc.MipLevels=desc.ArraySize=1;desc.Format=DXGI_FORMAT_B8G8R8A8_UNORM;desc.SampleDesc.Count=1;
    desc.BindFlags=D3D11_BIND_RENDER_TARGET|D3D11_BIND_SHADER_RESOURCE;desc.MiscFlags=D3D11_RESOURCE_MISC_SHARED;
    if(FAILED(device->CreateTexture2D(&desc,nullptr,&sharedTexture)))throw std::runtime_error("addon output allocation");
    desc.MiscFlags=0;desc.BindFlags=D3D11_BIND_SHADER_RESOURCE;
    if(FAILED(device->CreateTexture2D(&desc,nullptr,&displayTexture))||FAILED(device->CreateShaderResourceView(displayTexture.Get(),nullptr,&displayView)))throw std::runtime_error("addon local display allocation");
    D3D11_QUERY_DESC query{D3D11_QUERY_EVENT,0};if(FAILED(device->CreateQuery(&query,&copyComplete)))throw std::runtime_error("addon query");
    ComPtr<IDXGIResource> resource;if(FAILED(sharedTexture.As(&resource)))throw std::runtime_error("addon DXGI");
    HANDLE handle=nullptr;if(FAILED(resource->GetSharedHandle(&handle))||!handle)throw std::runtime_error("addon export");
    activeRuntime=runtime;s.gamePid=GetCurrentProcessId();s.sharedHandle=reinterpret_cast<uintptr_t>(handle);
    // Producer/ACK sequence is session-monotonic. Device recreation gets a new
    // resource epoch, not recycled sequence numbers or an early GPU-read ACK.
    return_path::write(s.presentedEpoch,0);return_path::write(s.error,0);firstPacket=true;
    return_path::write(s.lastWidth,static_cast<LONG>(width));return_path::write(s.lastHeight,static_cast<LONG>(height));
    InterlockedIncrement(&s.epoch);return_path::write(s.ready,1);
#endif
  }catch(...){failure(1);releaseResources();}
}
void destroy(reshade::api::effect_runtime* runtime){if(runtime==activeRuntime)releaseResources();}
void beforePresent(reshade::api::command_queue* queue,reshade::api::swapchain* swap,
  const reshade::api::rect*,const reshade::api::rect*,uint32_t,const reshade::api::rect*){
  // Public, limited-build permitted Present event precedes effect processing.
  // Ignore other devices/windows/swapchains; never infer that a DSV is scene depth.
  if((!inspectEarly&&!depth_snapshot::capture&&!sourceTimingRequested
#ifdef SFC_LIVE_RETURN
      &&!liveReceiver
#endif
     )||!activeRuntime||!channel||!context||
     queue->get_device()!=activeRuntime->get_device()||
     swap->get_hwnd()!=activeRuntime->get_hwnd()||
     swap->get_current_back_buffer().handle!=activeRuntime->get_current_back_buffer().handle)return;
  if(sourceTimingRequested){if(sourceTiming&&return_path::read(channel->state->armed)&&!return_path::read(channel->state->stop))sourceTiming->observe(1);
    if(directGame){auto handle=swap->get_current_back_buffer().handle;for(unsigned i=0;i<directCount;++i)if(directBack[i]==handle){directGame->step(directTargets[i].Get());break;}}return;}
#ifdef SFC_LIVE_RETURN
  if(liveReceiver){liveReceiver->step();return;}
#endif
  if(depth_snapshot::capture){
    auto* back=reinterpret_cast<ID3D11Texture2D*>(static_cast<uintptr_t>(swap->get_current_back_buffer().handle));
    depth_snapshot::capture->present(back);
  }
  auto& s=*channel->state;if(return_path::valid(s)){if(searchMode)search.observe(depth_search::DxgiPresent);else inspectDepth(s);}
}
void overlay(reshade::api::effect_runtime* runtime){
  if(runtime!=activeRuntime||!channel)return;
  if(sourceTimingRequested){if(sourceTiming&&return_path::read(channel->state->armed)&&!return_path::read(channel->state->stop))sourceTiming->observe(2);if(directGame)directGame->retire();return;}
#ifdef SFC_LIVE_RETURN
  if(liveReceiver){
    if(visibleShip){
      const auto size=ImGui::GetIO().DisplaySize;float rect[4]{};auto* view=liveReceiver->currentDisplay(size.x,size.y,rect);
      if(view){
        ImGui::GetBackgroundDrawList()->AddImage(static_cast<ImTextureID>(reinterpret_cast<uintptr_t>(view)),ImVec2(rect[0],rect[1]),ImVec2(rect[2],rect[3]));
        liveReceiver->imageDisplayed();
        InterlockedIncrement(&channel->state->drawCount);return_path::write(channel->state->presented,liveReceiver->displaySequence());
        channel->state->renderedAt=liveReceiver->displayObservedAt();channel->state->renderFrame=liveReceiver->displayFrame();
      }
    }
    return;
  }
#endif
  auto& s=*channel->state;
  // No waits, Map/readback, filesystem operations, shader compilation or bindings.
  if(!return_path::valid(s)){failure(2);return;}
  if(searchMode)search.observe(depth_search::Overlay);else if(!inspectEarly)inspectDepth(s);
  if(pending){
    BOOL done=FALSE;const auto status=context->GetData(copyComplete.Get(),&done,sizeof(done),D3D11_ASYNC_GETDATA_DONOTFLUSH);
    if(status==S_OK&&done){return_path::write(s.acknowledged,pending);pending=0;}
    else if(FAILED(status)){failure(3);return;}
  }
  if(!return_path::read(s.ready)||!return_path::read(s.armed)||!return_path::read(s.enabled)||return_path::read(s.stop)||return_path::read(s.error)){
    hide();InterlockedIncrement(&s.skipCount);return;
  }
  const auto produced=return_path::read(s.produced);
  if(!pending&&produced!=return_path::read(s.acknowledged)){
    if(produced<=return_path::read(s.acknowledged)||(!firstPacket&&produced!=return_path::read(s.acknowledged)+1)){failure(4);return;}
    if(return_path::read(s.renderEpoch)!=return_path::read(s.epoch)){
      return_path::write(s.acknowledged,produced);hide();InterlockedIncrement(&s.skipCount);return;
    }
    if(return_path::fresh(s.renderedAt,return_path::now(),s.qpcFrequency)){
      context->CopyResource(displayTexture.Get(),sharedTexture.Get());context->End(copyComplete.Get());
      pending=produced;visibleAt=s.renderedAt;firstPacket=false;InterlockedIncrement(&s.copyCount);
    }else{InterlockedIncrement(&s.staleCount);return_path::write(s.acknowledged,produced);hide();}
  }
  if(!return_path::fresh(visibleAt,return_path::now(),s.qpcFrequency)){hide();return;}
  const auto size=ImGui::GetIO().DisplaySize;
  if(!return_path::displaySupported(size.x,size.y)){hide();InterlockedIncrement(&s.skipCount);return;}
  // Pixel-sized tile in upper-right tactical scene, not an input window/menu.
  const ImVec2 a(size.x-272,96),b(size.x-16,352);
  ImGui::GetBackgroundDrawList()->AddImage(static_cast<ImTextureID>(reinterpret_cast<uintptr_t>(displayView.Get())),a,b);
  return_path::write(s.presented,produced);return_path::write(s.presentedEpoch,return_path::read(s.epoch));InterlockedIncrement(&s.drawCount);
}
}
static BOOL attach(HMODULE module){
    // Keep bounded path buffers out of DllMain's every-thread prologue. The
    // static CRT needs thread notifications; driver threads may have tiny stacks.
    auto* importedRegistration=&ReShadeRegisterAddon;
    if(!importedRegistration)return FALSE;
    const BOOL restored=DetourRestoreAfterWith();
    if(GetEnvironmentVariableW(L"SFC_REMIX_PRELOAD_REQUIRED",nullptr,0)&&!restored)return FALSE;
    wchar_t expected[1024]{},actual[1024]{};
    const auto n=GetEnvironmentVariableW(L"SFC_REMIX_EXPECTED_IMAGE",expected,1024);
    const auto m=GetEnvironmentVariableW(L"SFC_REMIX_RETURN_SESSION",session,128);
    if(!n||n>=1024||!m||m>=128)return TRUE; // Default off, including ordinary copied-game launches.
#ifdef SFC_LIVE_RETURN
    wchar_t live[2]{};if(GetEnvironmentVariableW(L"SFC_REMIX_PRIVATE_SHIP",live,2)!=1||live[0]!=L'1')return FALSE;
    wchar_t show[2]{};visibleShip=GetEnvironmentVariableW(L"SFC_REMIX_VISIBLE_SHIP",show,2)==1&&show[0]==L'1';
    sceneDepthTest=GetEnvironmentVariableW(L"SFC_REMIX_SCENE_DEPTH",nullptr,0)!=0;
#endif
    const auto length=GetModuleFileNameW(nullptr,actual,1024);
    if(!length||length>=1024||CompareStringOrdinal(actual,-1,expected,-1,TRUE)!=CSTR_EQUAL)return TRUE;
    wchar_t inspect[2]{};
    const auto inspectLength=GetEnvironmentVariableW(L"SFC_REMIX_INSPECT_VISIBILITY",inspect,2);
    searchMode=inspectLength==1&&inspect[0]==L'3';
    inspectEarly=inspectLength==1&&(inspect[0]==L'2'||searchMode);
    inspectVisibility=!searchMode&&inspectLength==1&&(inspect[0]==L'1'||inspectEarly);
    wchar_t timing[2]{};sourceTimingRequested=GetEnvironmentVariableW(L"SFC_D3D9_SOURCE_TIMING",timing,2)==1&&timing[0]==L'1';
    wchar_t direct[2]{};directGameRequested=GetEnvironmentVariableW(L"SFC_D3D9_GAME_OUTPUT",direct,2)==1&&direct[0]==L'1';
    if(directGameRequested&&!sourceTimingRequested)return FALSE;
    if(sourceTimingRequested&&(searchMode||inspectVisibility||GetEnvironmentVariableW(L"SFC_REMIX_DEPTH_OUTPUT",nullptr,0)||GetEnvironmentVariableW(L"SFC_REMIX_BROAD_OUTPUT",nullptr,0)))return FALSE;
    try{channel=std::make_unique<return_path::Mapping>(false,session);channel->state->gamePid=GetCurrentProcessId();return_path::write(channel->state->startupRestored,restored?1:0);return_path::write(channel->state->startupVerified,1);}
    catch(...){return FALSE;}
    if(searchMode){
      search.prepare(channel->state,channel->state->stop,channel->state->armed);
      searchFixture=wcsstr(actual,L"\\artifacts\\remix-runtime\\runs\\")!=nullptr;
      if(!searchFixture){
        if(CompareStringOrdinal(actual,-1,L"C:\\Project\\SFC-Remix-Return-Test\\StarFleetOP.exe",-1,TRUE)!=CSTR_EQUAL||GetModuleHandleW(nullptr)!=reinterpret_cast<HMODULE>(0x00400000))return FALSE;
        void* points[]={reinterpret_cast<void*>(0x0069E300),reinterpret_cast<void*>(0x0069E3D0),reinterpret_cast<void*>(0x0069E41B),reinterpret_cast<void*>(0x0069EB90)};
        // Before client entry: no game thread can yet execute these sites.
        search.install(points,false); // Failure leaves original bytes/control flow.
      }
    }
    if(!reshade::register_addon(module))return FALSE;
    registered=true;
    if(directGameRequested){reshade::register_event<reshade::addon_event::draw>(directDraw);reshade::register_event<reshade::addon_event::draw_indexed>(directIndexed);reshade::register_event<reshade::addon_event::clear_depth_stencil_view>(directClear);}
#ifdef SFC_LIVE_RETURN
    if(sceneDepthTest){reshade::register_event<reshade::addon_event::draw>(sceneDraw);reshade::register_event<reshade::addon_event::draw_indexed>(sceneIndexed);reshade::register_event<reshade::addon_event::clear_depth_stencil_view>(sceneClear);}
#endif
    wchar_t depthPath[1024]{};
    const auto depthLength=GetEnvironmentVariableW(L"SFC_REMIX_DEPTH_OUTPUT",depthPath,1024);
    if(depthLength&&depthLength<1024){
      if(searchMode||inspectVisibility||GetEnvironmentVariableW(L"SFC_REMIX_BROAD_OUTPUT",nullptr,0))return FALSE;
      depth_snapshot::capture=new depth_snapshot::Capture();
      if(!depth_snapshot::capture->prepare(channel->state,depthPath))return FALSE;
      depth_snapshot::events(true);
    }
    wchar_t broadPath[1024]{};
    const auto broadLength=GetEnvironmentVariableW(L"SFC_REMIX_BROAD_OUTPUT",broadPath,1024);
    if(broadLength&&broadLength<1024){
      broadMode=broad_events::trace.prepare(channel->state,broadPath);
      if(!broadMode)return FALSE;
      broad_events::events(true);
    }
    reshade::register_event<reshade::addon_event::init_effect_runtime>(init);
    reshade::register_event<reshade::addon_event::destroy_effect_runtime>(destroy);
    reshade::register_event<reshade::addon_event::reshade_overlay>(overlay);
    if(inspectEarly||depth_snapshot::capture||sourceTimingRequested
#ifdef SFC_LIVE_RETURN
       ||true
#endif
      )reshade::register_event<reshade::addon_event::present>(beforePresent);
    return TRUE;
}
extern "C" __declspec(dllexport) BOOL __cdecl SFCSearchFixtureStart(void* const* points){
  return searchMode&&searchFixture&&search.install(points,true);
}
BOOL WINAPI DllMain(HMODULE module,DWORD reason,LPVOID){
  if(DetourIsHelperProcess())return TRUE;
  if(reason==DLL_PROCESS_ATTACH)return attach(module);
  if(reason==DLL_PROCESS_DETACH&&registered){
    if(directGameRequested){reshade::unregister_event<reshade::addon_event::draw>(directDraw);reshade::unregister_event<reshade::addon_event::draw_indexed>(directIndexed);reshade::unregister_event<reshade::addon_event::clear_depth_stencil_view>(directClear);}
#ifdef SFC_LIVE_RETURN
    if(sceneDepthTest){reshade::unregister_event<reshade::addon_event::draw>(sceneDraw);reshade::unregister_event<reshade::addon_event::draw_indexed>(sceneIndexed);reshade::unregister_event<reshade::addon_event::clear_depth_stencil_view>(sceneClear);}
#endif
    if(broadMode)broad_events::events(false);
    if(depth_snapshot::capture)depth_snapshot::events(false);
    if(inspectEarly||depth_snapshot::capture||sourceTimingRequested
#ifdef SFC_LIVE_RETURN
       ||true
#endif
      )reshade::unregister_event<reshade::addon_event::present>(beforePresent);
    reshade::unregister_event<reshade::addon_event::reshade_overlay>(overlay);
    reshade::unregister_event<reshade::addon_event::destroy_effect_runtime>(destroy);
    reshade::unregister_event<reshade::addon_event::init_effect_runtime>(init);
    reshade::unregister_addon(module);
    // Normal runtime destroy callback empties COM state before unload. No hot
    // unload while active: disable through channel; remove file after game exit.
  }
  return TRUE;
}
