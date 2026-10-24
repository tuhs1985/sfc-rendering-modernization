// x64 worker ONLY. Source callback never waits,loads assets or calls renderer.
#pragma once
#include "live_owner_decode.h"
#include "../m1_component/m1_present_calibration.h"
#include "worker_poll.h"
#include "owner_rebind.h"
#include "input_admission.h"
#include "multi_scene_wire.h"
struct LiveOwnerInput {
 sfc_calibration::Reader source;live_owner::Store* store=nullptr;uint64_t last=0,started=0;DWORD invalid=0,replaced=0,received=0,unqualified=0;
 DWORD owner=0,revision=0,model=0,meshSource=0;uint64_t limit=90000;
 uint64_t next_enter=0,validation_ticks=0,sleep_ticks=0,empty_polls=0;
 WorkerPoll poll;
 owner_rebind::Control* binding=nullptr;uint64_t bindCookie=0;DWORD bindGeneration=0,rebound=0,oldPackets=0;
 DWORD previousOwner=0,previousRevision=0,previousModel=0,previousSource=0;
 uint64_t frequency=0;DWORD expired=0;
 volatile LONG* closedFrame=nullptr;DWORD admissionCounts[2][static_cast<unsigned>(live_owner::Admission::Count)]{};
 void (*idleWork)(void*)=nullptr;void* idleContext=nullptr; // Backend worker only;never installed in SFC.
 static uint64_t ticks(){LARGE_INTEGER q{};QueryPerformanceCounter(&q);return static_cast<uint64_t>(q.QuadPart);}
 ~LiveOwnerInput(){source.close();}
 void start(const Scene& scene){
  wchar_t game[2]{};if(GetEnvironmentVariableW(L"SFC_D3D9_GAME_OUTPUT",game,2)==1&&game[0]==L'1')limit=110000;
  require(source.prepare()&&source.requested,"live input explicit mapping");
  auto* base=reinterpret_cast<BYTE*>(source.mailbox)-sfc_calibration::Offset;store=reinterpret_cast<live_owner::Store*>(base+live_owner::Offset);
  wchar_t pidText[16]{};GetEnvironmentVariableW(L"SFC_D3D9_GAME_PID",pidText,16);const auto pid=static_cast<DWORD>(_wcstoui64(pidText,nullptr,10));
  require(pid&&live_owner::header_valid(store->header,source.session)&&store->header.pid==pid&&!frame_ingress::state(&store->header.stopped),"live input process/session/header");
  wchar_t label[32]{};GetEnvironmentVariableW(L"SFC_D3D9_EXPECTED_MODEL",label,32);model=static_cast<DWORD>(_wcstoui64(label,nullptr,10));
  ZeroMemory(label,sizeof(label));GetEnvironmentVariableW(L"SFC_D3D9_EXPECTED_SOURCE",label,32);meshSource=static_cast<DWORD>(_wcstoui64(label,nullptr,10));require(model&&meshSource,"fresh asset source labels required");
  const auto& first=scene.frames.front();owner=first.owner;revision=first.revision;const auto selected=static_cast<LONG64>(live_owner::selection(owner,revision));
  require(InterlockedCompareExchange64(&store->header.selected,selected,0)==0,"one explicit selected owner");started=GetTickCount64();
  LARGE_INTEGER rate{};require(QueryPerformanceFrequency(&rate)!=FALSE,"live input QPC frequency");frequency=static_cast<uint64_t>(rate.QuadPart);
  wchar_t cookieText[32]{};
  wchar_t multi[2]{};if(GetEnvironmentVariableW(L"SFC_D3D9_MULTISCENE",multi,2)==1&&multi[0]==L'1'){
   auto* cohort=reinterpret_cast<multi_scene::Store*>(base+multi_scene::Offset);
   require(multi_scene::valid(cohort->header,source.session,pid),"buffered cohort admission watermark");closedFrame=&cohort->header.closed_frame;
  }
  if(GetEnvironmentVariableW(L"SFC_D3D9_REBIND_COOKIE",cookieText,32)){
   bindCookie=_wcstoui64(cookieText,nullptr,16);binding=reinterpret_cast<owner_rebind::Control*>(base+owner_rebind::Offset);
   owner_rebind::Target t{};
   require(owner_rebind::read(*binding,store->header,t)&&t.owner==owner&&t.revision==revision&&t.model==model&&t.source==meshSource&&
    owner_rebind::apply(*binding,*store,t,bindCookie,bindGeneration),"initial qualified content binding");
  }
 }
 void rebind(){
  if(!binding)return;owner_rebind::Target t{};
  if(!owner_rebind::read(*binding,store->header,t)||t.generation==bindGeneration)return;
  if(!owner_rebind::valid(t,bindCookie,bindGeneration)){++binding->rejected;return;}
  previousOwner=owner;previousRevision=revision;previousModel=model;previousSource=meshSource;
  owner=t.owner;revision=t.revision;model=t.model;meshSource=t.source;
  require(owner_rebind::apply(*binding,*store,t,bindCookie,bindGeneration),"qualified owner rebind");++rebound;
  std::cout<<"OWNER_REBOUND generation="<<bindGeneration<<" owner="<<owner<<" revision="<<revision<<" resident_assets=1\n";
 }
 bool next(const Scene& scene,Frame& out,live_owner::Packet& packet){
  next_enter=ticks();validation_ticks=sleep_ticks=empty_polls=0;
  while(store&&!frame_ingress::state(&store->header.stopped)&&GetTickCount64()-started<limit){
   if(idleWork)idleWork(idleContext); // Admit new assets even if the old scheduling anchor retired.
   rebind();
   if(live_owner::take(store->input,store->header,packet,last,invalid)){
    const auto validation_started=ticks();
    if(live_owner::matches_asset(packet,previousOwner,previousRevision,previousModel,previousSource)){++oldPackets;continue;}
    if(!live_owner::matches_asset(packet,owner,revision,model,meshSource)||!live_owner::decode(packet,out)||packet.row[47]!=store->header.source_thread){++unqualified;continue;}
    if(!admit(packet,0))continue;
    bool good=true;const size_t stride=(std::max)(size_t(1),scene.vertices.size()/64);
    for(size_t i=0;i<scene.vertices.size();i+=stride)if(!live_owner::projection_matches(packet,out,scene.vertices[i].p)){good=false;break;}
    if(!good){++unqualified;continue;}validation_ticks=ticks()-validation_started;++received;return true;
   }++empty_polls;const auto sleeping=ticks();poll.pause();sleep_ticks+=ticks()-sleeping;
  }return false;
 }
 bool admit(const live_owner::Packet& p,unsigned stage=1){
  const auto reason=store?live_owner::admission(p,store->header,ticks(),frequency,closedFrame):live_owner::Admission::Clock;
  ++admissionCounts[stage==0?0:1][static_cast<unsigned>(reason)];
  if(reason==live_owner::Admission::Accepted)return true;
  ++expired;return false;
 }
 void complete(const live_owner::Packet& input,uint64_t now){
  if(!store||frame_ingress::state(&store->header.stopped))return;
  live_owner::Completion c{};memcpy(c.session,input.session,16);c.sequence=input.sequence;c.offered=input.offered;c.completed=now;c.state_hash=input.state_hash;
  c.frame=input.row[2];c.owner=input.row[1];c.revision=input.row[7];c.checksum=live_owner::checksum(c);
  require(live_owner::publish(store->output,c,replaced),"live completion inbox unavailable");
 }
};
