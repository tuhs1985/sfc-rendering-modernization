// Offline source thread:synthetic60Hz demand cycling recorded OWNER snapshots.
// Deliberately independent of GPU/receiver progress. Never used in SFC callbacks.
#pragma once
#include "frame_ingress.h"
#include <thread>
#include <atomic>
static uint64_t ingressAssetHash(const Scene& scene,const fs::path& root){
 // Decoded geometry/group/image content,not replay poses,viewport or pointers.
 uint64_t result=14695981039346656037ull;
 const auto mix=[&](const void* p,size_t n){const auto h=frame_ingress::hash(p,n);result^=h;result*=1099511628211ull;};
 mix(scene.vertices.data(),scene.vertices.size()*sizeof(Vertex));mix(scene.indices.data(),scene.indices.size()*sizeof(uint32_t));mix(scene.groups.data(),scene.groups.size()*sizeof(Group));
 std::set<uint32_t> materials;for(const auto& g:scene.groups)materials.insert(g.material);size_t bytes=0;
 for(auto material:materials){const auto image=read(root/(L"texture-"+std::to_wstring(material)+L".bin"),128*1024*1024);bytes+=image.size();require(bytes<=128*1024*1024,"input asset byte cap");mix(image.data(),image.size());}
 require(result!=0,"input asset hash");return result;
}
struct IngressReplay {
 frame_ingress::Channel channel{};frame_ingress::Consumer consumer;frame_ingress::TakeStats stats{};
 std::thread source;std::atomic<bool> finished=false;std::atomic<unsigned> source_late=0;
 HANDLE event=nullptr;uint64_t frequency=0,lag_sequence=0;unsigned lag_ms=0;bool lag_used=false;
 IngressReplay(){event=CreateEventW(nullptr,FALSE,FALSE,nullptr);require(event!=nullptr,"offline source event");}
 ~IngressReplay(){InterlockedExchange(&channel.stopped,1);if(event)SetEvent(event);if(source.joinable())source.join();if(event)CloseHandle(event);}
 void start(const Scene& scene,uint64_t asset,unsigned count,uint64_t freq,unsigned lag){
  require(!source.joinable()&&count==300&&freq,"offline input replay bounds");channel.session=9;frequency=freq;lag_ms=lag;
  source=std::thread([this,&scene,asset,count]{
   frame_ingress::Producer producer;LARGE_INTEGER q{};QueryPerformanceCounter(&q);const auto origin=static_cast<uint64_t>(q.QuadPart);
   for(unsigned i=0;i<count&&!frame_ingress::state(&channel.stopped);++i){
    const uint64_t due=origin+uint64_t(i)*frequency/60;uint64_t now=0;
    do{QueryPerformanceCounter(&q);now=static_cast<uint64_t>(q.QuadPart);if(now<due)Sleep(1);}while(now<due&&!frame_ingress::state(&channel.stopped));
    if(frame_ingress::state(&channel.stopped))break;
    const uint64_t deadline=due+frequency/60;if(now>=deadline){++source_late;continue;}
    const auto& f=scene.frames[i%scene.frames.size()];frame_ingress::Packet p{};
    p.key={9,uint64_t(i)+1,f.frame,0,asset,f.owner,f.revision};p.offered_qpc=now;p.deadline_qpc=deadline;
    memcpy(p.model,f.model,sizeof(p.model));memcpy(p.view,f.view,sizeof(p.view));memcpy(p.projection,f.projection,sizeof(p.projection));memcpy(p.viewport,f.viewport,sizeof(p.viewport));
    p.key.state_hash=frame_ingress::state_hash(p);p.checksum=frame_ingress::checksum(p);
    if(!producer.publish(channel,p))++source_late;else SetEvent(event);
   }
   finished=true;SetEvent(event);
  });
 }
 bool next(frame_ingress::Packet& packet,Frame& frame){
  const auto began=GetTickCount64();
  for(;;){LARGE_INTEGER q{};require(QueryPerformanceCounter(&q)!=FALSE,"offline input clock");
   if(consumer.take(channel,9,static_cast<uint64_t>(q.QuadPart),packet,stats)){
    frame={};frame.owner=packet.key.owner_epoch;frame.revision=packet.key.revision;frame.frame=static_cast<uint32_t>(packet.key.source_frame);frame.active=1;
    memcpy(frame.model,packet.model,sizeof(frame.model));memcpy(frame.view,packet.view,sizeof(frame.view));memcpy(frame.projection,packet.projection,sizeof(frame.projection));memcpy(frame.viewport,packet.viewport,sizeof(frame.viewport));
    if(lag_ms&&!lag_used&&packet.key.sequence>=75){lag_sequence=packet.key.sequence;Sleep(lag_ms);lag_used=true;}return true;
   }
   if(finished)return false;
   require(GetTickCount64()-began<10000,"offline input progress10s limit");require(WaitForSingleObject(event,100)!=WAIT_FAILED,"offline input event");
  }
 }
};
