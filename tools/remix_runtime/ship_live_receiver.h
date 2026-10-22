// Same-process current-state gate and PRIVATE GPU draw; never binds a game target.
#pragma once
#include "ship_live_request.h"
#include "ship_triplet_compositor.h"
#include "ship_image_snapshot.h"
#include "ship_scene_depth.h"
namespace ship_live {
class Receiver {
 return_path::Mapping& mapping;Wire& wire;Command& commands;
 struct Source:sfc_calibration::Reader{~Source(){close();}} source;
 const bool depthTest=GetEnvironmentVariableW(L"SFC_REMIX_SCENE_DEPTH",nullptr,0)!=0;
 Consumer consumer;Compositor compositor;ship_scene_depth::Source scene;
 ComPtr<ID3D11Texture2D> privateTarget;ComPtr<ID3D11RenderTargetView> privateView;
 ComPtr<ID3D11DeviceContext> context;
 ComPtr<ID3D11ShaderResourceView> displayView;Key drawnKey{};uint64_t drawnAt=0;
 LONG drawnSequence=0;
 ship_image::Snapshot image;
 bool stopped=false;
 const bool buffered=GetEnvironmentVariableW(L"SFC_REMIX_TEXTURED_SHIP",nullptr,0)!=0;
 const DWORD renderThread=GetCurrentThreadId();
 struct Process{HANDLE handle=nullptr;~Process(){if(handle)CloseHandle(handle);}} producer;
public:
#ifdef SFC_LIVE_FIXTURE
 ID3D11Texture2D* fixtureOutput()const{return privateTarget.Get();}
 ID3D11Texture2D* fixturePicking()const{return consumer.textures[2].Get();}
 ID3D11Texture2D* fixtureDepth()const{return consumer.textures[1].Get();}
#endif
 Receiver(return_path::Mapping& m,ID3D11Device* d):mapping(m),wire(*reinterpret_cast<Wire*>(reinterpret_cast<BYTE*>(m.state)+ship_triplet::Offset)),commands(command(m)),consumer(wire,d),compositor(d,depthTest),scene(d,ship_scene_depth::data(m)),image(m){
  if(!source.prepare()||!source.requested)throw std::runtime_error("fresh semantic mailbox required");
  d->GetImmediateContext(&context);
  if(wire.creator!=mapping.state->creatorPid)throw std::runtime_error("fresh producer identity");
  if(buffered!=(wire.version==BufferedVersion))throw std::runtime_error("ship display policy mismatch");
  producer.handle=OpenProcess(SYNCHRONIZE,FALSE,wire.creator);if(!producer.handle)throw std::runtime_error("fresh producer process");
  D3D11_TEXTURE2D_DESC desc{};desc.Width=wire.width;desc.Height=wire.height;desc.Format=DXGI_FORMAT_B8G8R8A8_UNORM;desc.MipLevels=desc.ArraySize=1;desc.SampleDesc.Count=1;desc.BindFlags=D3D11_BIND_RENDER_TARGET|D3D11_BIND_SHADER_RESOURCE;
  checked(d->CreateTexture2D(&desc,nullptr,&privateTarget),"private ship target");checked(d->CreateRenderTargetView(privateTarget.Get(),nullptr,&privateView),"private ship RTV");
  checked(d->CreateShaderResourceView(privateTarget.Get(),nullptr,&displayView),"ship display SRV");
  image.init(d,wire.width,wire.height,wire.frequency);
 }
 ~Receiver(){source.close();}
 void observeDepth(uint64_t nativeContext){if(depthTest&&!stopped)scene.observe(nativeContext,source.mailbox);}
 void depthCleared(uint64_t nativeContext){if(depthTest&&!stopped)scene.cleared(nativeContext);}
 void step(const sfc_calibration::Snapshot* fixture=nullptr){
  try{
   if(GetCurrentThreadId()!=renderThread)throw std::runtime_error("private receiver wrong thread");
   consumer.poll();image.poll(context.Get());if(depthTest)drawnAt=0;if(stopped)return;
   if(load(wire.error)){stopped=true;InterlockedIncrement(&commands.failed);return;}
   if(WaitForSingleObject(producer.handle,0)!=WAIT_TIMEOUT){store(wire.stop,1);stopped=true;return;}
   if(load(wire.stop)||!load(wire.ready)||!return_path::read(mapping.state->armed)||!return_path::read(mapping.state->enabled))return;
   Seed seed{};{Lock lock(wire);auto& reg=registration(mapping);if(!lock.held||!load(reg.ready))return;seed=reg.seed;}
   sfc_calibration::Snapshot snap{};if(fixture)snap=*fixture;else if(!sfc_calibration::read(source.mailbox,snap)){InterlockedIncrement(&commands.invalid);return;}
   Key current{};std::array<uint32_t,96> row{};
   if(!makeKey(seed,snap,GetCurrentProcessId(),GetCurrentThreadId(),current,row)){InterlockedIncrement(&commands.invalid);if(load(wire.lease)==Ready)claim(wire,Key{},return_path::now());return;}
   ID3D11ShaderResourceView* nativeDepth=nullptr;
   if(depthTest){nativeDepth=scene.finish(snap.frame,wire.width,wire.height);if(!nativeDepth)return;}
   const LONG rejected=load(wire.rejected);
   if(!(buffered?consumer.acquireBuffered(current):consumer.acquire(current))){if(load(wire.rejected)>rejected)InterlockedIncrement(&commands.late);return;}
   InterlockedIncrement(&commands.acquired);
   if(depthTest&&(wire.published.pose!=current.pose||wire.published.camera!=current.camera)){
    InterlockedIncrement(&ship_scene_depth::data(mapping).stateMismatch);
    // Claim is released through the consumer's usual EVENT/ACK path,not a
    // metadata-only ACK or producer-surface overwrite.
    consumer.submitted();return;
   }
   ID3D11ShaderResourceView* views[]={consumer.views[0].Get(),consumer.views[1].Get(),consumer.views[2].Get()};
   D3D11_VIEWPORT viewport{0,0,static_cast<float>(wire.width),static_cast<float>(wire.height),0,1};
   const float transparent[4]{};context->ClearRenderTargetView(privateView.Get(),transparent);
   if(!compositor.draw(privateView.Get(),views,current,viewport,nativeDepth))throw std::runtime_error("private ship draw refused");
   drawnKey=buffered?wire.published:current;drawnAt=buffered?wire.publishedAt:return_path::now();
   drawnSequence=load(wire.sequence);InterlockedIncrement(&mapping.state->copyCount);
   consumer.submitted();InterlockedIncrement(&commands.drawn);
  }catch(...){InterlockedIncrement(&commands.failed);store(wire.error,10);stopped=true;}
 }
 ID3D11ShaderResourceView* currentDisplay(float width,float height,float (&rect)[4]){
  if(stopped||GetCurrentThreadId()!=renderThread||!drawnAt||load(wire.stop)||load(wire.error)||!load(wire.ready)||!return_path::read(mapping.state->armed)||return_path::read(mapping.state->stop)||!return_path::read(mapping.state->enabled)||!return_path::fresh(drawnAt,return_path::now(),wire.frequency)||WaitForSingleObject(producer.handle,0)!=WAIT_TIMEOUT)return nullptr;
  Seed seed{};{Lock lock(wire);auto& reg=registration(mapping);if(!lock.held||!load(reg.ready))return nullptr;seed=reg.seed;}
  sfc_calibration::Snapshot snap{};Key current{};std::array<uint32_t,96> row{};
  if(!sfc_calibration::read(source.mailbox,snap)||!makeKey(seed,snap,GetCurrentProcessId(),renderThread,current,row)||
     !(buffered?(current.frame>=drawnKey.frame&&sameIdentity(current,drawnKey)&&sourceRecent(drawnAt,return_path::now(),wire.frequency)):same(current,drawnKey))||!displayRect(drawnKey,width,height,rect))return nullptr;
  if(depthTest&&(current.pose!=drawnKey.pose||current.camera!=drawnKey.camera||current.frame!=ship_scene_depth::data(mapping).engineFrame))return nullptr;
  image.enqueue(context.Get(),privateTarget.Get(),drawnKey,drawnSequence,drawnAt,rect,seed);
  if(depthTest)InterlockedIncrement(&ship_scene_depth::data(mapping).displayed);
  return displayView.Get();
 }
 void imageDisplayed(){image.markDisplay();}
 LONG displaySequence()const{return drawnSequence;}
 uint32_t displayFrame()const{return drawnKey.frame;}
 uint64_t displayObservedAt()const{return drawnAt;}
 void stop(){stopped=true;image.stop();store(wire.stop,1);if(GetCurrentThreadId()==renderThread)consumer.poll();}
};
}
