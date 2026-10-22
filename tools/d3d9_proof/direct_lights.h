// Reuse the existing Remix light adapter;geometry remains ordinary D3D9.
#pragma once
#include "../remix_runtime/ship_live_request.h"
#include "../remix_runtime/remix_live_lights.h"
#include <thread>
#include <mutex>
#include <atomic>
#include "../m1_component/m1_light_transport.h"
struct DirectLights {
 bool enabled=false;RemixLiveLights lights;
 std::mutex mutex;std::thread reader;std::atomic<bool> stopping{false};
 LiveLightPacket cached{};LightShapePacket cachedShapes{};bool ready=false;uint64_t reads=0,readFailures=0;
 sfc_calibration::Reader sharedSource;sfc_light_transport::Encoded* shared=nullptr;DWORD expectedPid=0;
 ~DirectLights(){stop();sharedSource.close();}
 void stop(){stopping.store(true);if(reader.joinable())reader.join();}
 void read(){
  LiveLightPacket p{};LightShapePacket shapes{};
  std::ifstream file("live-lights.bin",std::ios::binary);
  if(!file||!file.read(reinterpret_cast<char*>(&p),sizeof(p))||file.peek()!=EOF){++readFailures;return;}
  if(p.checksum!=lightChecksum(p)){++readFailures;return;}
  if(p.rows[0].values[10]||p.rows[1].values[10]){
   std::ifstream sf("light-shapes.bin",std::ios::binary);
   if(!sf||!sf.read(reinterpret_cast<char*>(&shapes),sizeof(shapes))||sf.peek()!=EOF||!validShapes(shapes,p.revision)){++readFailures;return;}
  }
  // No file IO/API calls under this lock. Context/freshness checked by update.
  std::lock_guard<std::mutex> lock(mutex);cached=p;cachedShapes=shapes;ready=true;++reads;
 }
 bool update(remixapi_Interface& api,const Frame& state,const live_owner::Packet* packet,const LiveOwnerInput& input,uint64_t frequency){
  if(!enabled)return true;
  ship_live::Seed seed{};ship_live::Key key{};
  if(packet){
   memcpy(key.sourceSession,packet->session,16);seed.model=input.model;seed.source=input.meshSource;
  }else{
   // Offline fixture identity only;never substitutes a historical light in SFC.
   std::ifstream f("light-fixture-identity.bin",std::ios::binary);uint32_t identity[6]{};
   if(!f||!f.read(reinterpret_cast<char*>(identity),sizeof(identity))||f.peek()!=EOF)return false;
   memcpy(key.sourceSession,identity,16);seed.model=identity[4];seed.source=identity[5];
  }
  key.owner=state.owner;key.revision=state.revision;key.frame=state.frame;
  LiveLightPacket p{};LightShapePacket shapes{};
  if(shared){
   if(!sfc_light_transport::valid(shared->header,sfc_light_transport::EncodedMagic,sizeof(*shared),sharedSource.session,expectedPid))return false;
   sfc_light_transport::EncodedPayload payload{};ULONGLONG captured=0;
   if(!sfc_light_transport::read(shared->cell,payload,captured))return false;
   memcpy(&p,payload.packet,sizeof(p));memcpy(&shapes,payload.shapes,sizeof(shapes));++reads;
   if(captured!=p.observed)return false;
  }else{std::unique_lock<std::mutex> lock(mutex,std::try_to_lock);if(!lock.owns_lock()||!ready)return false;p=cached;shapes=cachedShapes;}
  return lights.update(api,seed,key,frequency,state.model,&p,&shapes);
 }
 void start(){wchar_t flag[2]{};enabled=GetEnvironmentVariableW(L"SFC_D3D9_LIGHT_SETTINGS",flag,2)==1&&flag[0]==L'1';if(enabled){
  wchar_t fast[2]{};const bool requested=GetEnvironmentVariableW(L"SFC_D3D9_SHARED_LIGHTS",fast,2)==1&&fast[0]==L'1';
  if(requested){
   require(sharedSource.prepare()&&sharedSource.requested,"explicit shared light mapping");
   auto* base=reinterpret_cast<BYTE*>(sharedSource.mailbox)-sfc_calibration::Offset;
   shared=reinterpret_cast<sfc_light_transport::Encoded*>(base+sfc_light_transport::EncodedOffset);
   wchar_t pid[16]{};GetEnvironmentVariableW(L"SFC_D3D9_GAME_PID",pid,16);expectedPid=static_cast<DWORD>(_wcstoui64(pid,nullptr,10));
   require(expectedPid&&sfc_light_transport::valid(shared->header,sfc_light_transport::EncodedMagic,sizeof(*shared),sharedSource.session,expectedPid),"shared light session/PID/contract");
   std::cout<<"SHARED_LIGHTS active=1 per_frame_file_reads=0\n";
  }else{read();reader=std::thread([this]{while(!stopping.load()){read();Sleep(10);}});}
 }}
 void draw(remixapi_Interface& api){if(enabled)lights.draw(api);}
 void close(remixapi_Interface& api){stop();if(enabled){std::cout<<"LIGHT_UPDATE_SUMMARY changes="<<lights.applied<<" cache_reads="<<reads<<" read_failures="<<readFailures<<'\n';lights.close(api);}}
};
