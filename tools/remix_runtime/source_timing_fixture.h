// Synthetic source rows for the standalone D3D11 fixture ONLY,never SFC.
#pragma once
#include "../m1_component/m1_present_calibration.h"
#include "../d3d9_proof/live_owner_wire.h"
#include "../d3d9_proof/owner_rebind.h"
#include "../d3d9_proof/multi_scene_wire.h"
#include "../d3d9_proof/replacement_transaction.h"
#include "../native_insertion/gate_contract.h"
#include "../scene_bridge/persistent_scene.h"
#include <vector>
#include <fstream>
struct SourceTimingFixture {
 sfc_calibration::Reader source;bool enabled=false;
 bool liveEnabled=false,rebindFixture=false,lateAssetFixture=false;live_owner::Source live;multi_scene::Source cohort;std::vector<live_owner::Row> rows;
 SourceTimingFixture(){
  wchar_t mode[2]{};enabled=GetEnvironmentVariableW(L"SFC_D3D9_SOURCE_TIMING",mode,2)==1&&mode[0]==L'1';
  if(enabled){if(!source.prepare()||!source.requested)throw std::runtime_error("fixture source channel");source.mailbox->snapshot={};memcpy(source.mailbox->snapshot.session,source.session,16);InterlockedExchange(&source.mailbox->active,1);}
  wchar_t liveMode[2]{},path[1024]{};liveEnabled=GetEnvironmentVariableW(L"SFC_D3D9_LIVE_TIMING",liveMode,2)==1&&liveMode[0]==L'1';
  if(liveEnabled){
   wchar_t rebindMode[2]{};rebindFixture=GetEnvironmentVariableW(L"SFC_D3D9_REBIND_FIXTURE",rebindMode,2)==1&&rebindMode[0]==L'1';
   if(!enabled||!live.attach(reinterpret_cast<BYTE*>(source.mailbox)-sfc_calibration::Offset,source.session)||!GetEnvironmentVariableW(L"SFC_D3D9_FIXTURE_ROWS",path,1024))throw std::runtime_error("live fixture input");
   std::ifstream f(path,std::ios::binary|std::ios::ate);const auto bytes=f.tellg();if(bytes<=0||bytes>384*16||bytes%384)throw std::runtime_error("live fixture row bound");
   rows.resize(static_cast<size_t>(bytes)/384);f.seekg(0);f.read(reinterpret_cast<char*>(rows.data()),static_cast<std::streamsize>(bytes));if(!f)throw std::runtime_error("live fixture rows");
   wchar_t multi[2]{};if(GetEnvironmentVariableW(L"SFC_D3D9_MULTISCENE",multi,2)==1&&multi[0]==L'1'){
    if(rows.size()<2||rows.size()>16||!cohort.attach(reinterpret_cast<BYTE*>(source.mailbox)-sfc_calibration::Offset,source.session))throw std::runtime_error("multi-scene fixture input");
    wchar_t late[2]{};lateAssetFixture=GetEnvironmentVariableW(L"SFC_MULTISCENE_LATE_ASSET",late,2)==1&&late[0]==L'1';}
  }
  // Standalone startup experiment only: publish the verified PID, but no
  // geometry/state until the requested menu-like idle has elapsed.
  wchar_t idle[16]{};
  if(GetEnvironmentVariableW(L"SFC_FIXTURE_MENU_IDLE_MS",idle,16)){
   const auto delay=_wtol(idle);if(!liveEnabled||!cohort.store||delay<0||delay>60000)throw std::runtime_error("fixture menu idle bound");
   const auto end=GetTickCount64()+static_cast<uint64_t>(delay);while(GetTickCount64()<end)Sleep(25);
  }
 }
 ~SourceTimingFixture(){cohort.close();live.close();source.close();}
 void publish(DWORD frame){
  if(!enabled)return;
  if(liveEnabled){frame+=200000;sfc_calibration::begin(source.mailbox,frame);live.begin(frame);
   if(native_gate::requested()){auto* base=reinterpret_cast<BYTE*>(source.mailbox)-sfc_calibration::Offset;
    auto* gate=reinterpret_cast<native_gate::Store*>(base+native_gate::Offset);if(gate->header.magic==native_gate::Magic)native_gate::begin(*gate,frame,GetCurrentThreadId());}
   if(cohort.store){cohort.begin();live_owner::Packet anchor{};bool prepared=false;auto* base=reinterpret_cast<BYTE*>(source.mailbox)-sfc_calibration::Offset;
    auto* replacementStore=reinterpret_cast<replacement::Store*>(base+replacement::Offset);
    if(replacement::requested()&&replacement::valid(replacementStore,source.session,GetCurrentProcessId())){InterlockedExchange(&replacementStore->native_capable,1);replacement::begin(*replacementStore,frame,GetCurrentThreadId());}
    for(DWORD i=0;i<rows.size();++i){
     if(lateAssetFixture&&i==2&&InterlockedCompareExchange(reinterpret_cast<LONG*>(base+11*1024*1024+128*1024+512),0,0)<120)continue;
     auto row=rows[i];row[2]=frame;row[45]=i;row[47]=GetCurrentThreadId();row[94]=row[95]=0;
     if(native_gate::requested()){
      // Fixture-only changing rigid pose. Recompute the independently checked
      // engine-composed projection rather than pairing old pixels with a pose.
      sfc_scene::Matrix world{},view{},projection{};memcpy(world.data(),row.data()+8,64);memcpy(view.data(),row.data()+49,64);memcpy(projection.data(),row.data()+66,64);
      auto turn=sfc_scene::identity();const float angle=float(frame%600)*.002f;turn[0]=turn[10]=cosf(angle);turn[2]=sinf(angle);turn[8]=-sinf(angle);
      world=sfc_scene::multiply(world,turn);world[3]+=sinf(angle)*.1f;memcpy(row.data()+8,world.data(),64);
      auto screen=sfc_scene::identity();float viewport[6]{};memcpy(viewport,row.data()+83,24);screen[0]=viewport[4];screen[5]=-viewport[5];screen[3]=viewport[0]+viewport[4];screen[7]=viewport[1]+viewport[5];
      const auto composed=sfc_scene::multiply(screen,sfc_scene::multiply(projection,sfc_scene::multiply(view,world)));memcpy(row.data()+25,composed.data(),64);
     }
     if(!native_gate::requested()&&replacement::requested()&&replacement::valid(replacementStore,source.session,GetCurrentProcessId()))replacement::suppress(*replacementStore,frame,row[1],row[7],row[5],row[6],GetCurrentThreadId(),true,replacement::now()); // SYNTHETIC source only; not an installed engine hook.
     LARGE_INTEGER q{};QueryPerformanceCounter(&q);sfc_calibration::stamp(row,static_cast<ULONGLONG>(q.QuadPart));if(live.prepare(row,anchor))prepared=true;
     if(!sfc_calibration::offer(source.mailbox,i,row))live.reject(frame);cohort.offer(row);
     auto* guard=reinterpret_cast<LONG*>(base+4096+i*512);InterlockedIncrement(guard);memcpy(base+4100+i*512,row.data(),sizeof(row));InterlockedIncrement(guard);}
    if(cohort.publish(static_cast<uint64_t>(InterlockedCompareExchange64(&live.store->header.selected,0,0)))&&prepared)live.commit(anchor);
    if(!native_gate::requested())Sleep(GetEnvironmentVariableW(L"SFC_SYNC_FIXTURE_SHORT_LEAD",nullptr,0)?3:16);return;
   }
   auto row=rows[(frame-200001)%rows.size()];row[0]=0;row[2]=frame;row[4]=1;row[45]=0;row[47]=GetCurrentThreadId();row[94]=row[95]=0;
   if(rebindFixture){
    auto* base=reinterpret_cast<BYTE*>(source.mailbox)-sfc_calibration::Offset;
    auto& binding=*reinterpret_cast<owner_rebind::Control*>(base+owner_rebind::Offset);owner_rebind::Target t{};
    // Explicit synthetic producer follows ACK,never injected into SFC.
    if(owner_rebind::read(binding,live.store->header,t)&&static_cast<DWORD>(InterlockedCompareExchange(&binding.acknowledged,0,0))==t.generation){
     row[1]=t.owner;row[7]=t.revision;row[5]=t.model;row[6]=t.source;
    }
   }
   LARGE_INTEGER q{};QueryPerformanceCounter(&q);sfc_calibration::stamp(row,static_cast<ULONGLONG>(q.QuadPart));live.offer(row);
   if(!sfc_calibration::offer(source.mailbox,0,row))live.reject(frame);
   auto* base=reinterpret_cast<BYTE*>(source.mailbox)-sfc_calibration::Offset;
   auto* guard=reinterpret_cast<LONG*>(base+4096);InterlockedIncrement(guard);memcpy(base+4100,row.data(),sizeof(row));InterlockedIncrement(guard);
   Sleep(GetEnvironmentVariableW(L"SFC_SYNC_FIXTURE_SHORT_LEAD",nullptr,0)?3:16);return; // STANDALONE only;never inserted into SFC
  }
  sfc_calibration::begin(source.mailbox,frame);
  std::array<DWORD,96> row{};row[1]=7;row[2]=frame;row[4]=1;row[5]=99;row[6]=98;row[7]=1;row[47]=GetCurrentThreadId();row[48]=1;
  LARGE_INTEGER q{};QueryPerformanceCounter(&q);sfc_calibration::stamp(row,static_cast<ULONGLONG>(q.QuadPart));sfc_calibration::offer(source.mailbox,0,row);
  QueryPerformanceCounter(&q);sfc_calibration::stamp(row,static_cast<ULONGLONG>(q.QuadPart));sfc_calibration::offer(source.mailbox,0,row);
 }
};
