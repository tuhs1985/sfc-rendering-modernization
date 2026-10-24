// Standalone receiver worker ONLY. No game callback allocation,waits or file IO.
#pragma once
#include "game_output_wire.h"
#include "live_owner_wire.h"
#include <cmath>
#include "../m1_component/m1_present_calibration.h"
struct GameOutputWriter {
 sfc_calibration::Reader source;game_output::Pool* pool=nullptr;
 Microsoft::WRL::ComPtr<ID3D11Texture2D> textures[2][3];uint64_t handles[2][3]{};
 bool enabled=false,retainReady=false;uint64_t session=0;
 ~GameOutputWriter(){if(pool){InterlockedExchange(&pool->header.stopped,1);InterlockedExchange(&pool->header.ready,0);}source.close();}
 void start(){wchar_t mode[2]{};enabled=GetEnvironmentVariableW(L"SFC_D3D9_GAME_OUTPUT",mode,2)==1&&mode[0]==L'1';
  retainReady=GetEnvironmentVariableW(L"SFC_D3D9_SYNC_BUFFER",mode,2)==1&&mode[0]==L'1';}
 void prepare(ID3D11Device* device,const output_wire::Packet& input){
  if(!enabled||pool)return;
  check(source.prepare()&&source.requested,"game pool explicit semantic mapping");
  auto* base=reinterpret_cast<BYTE*>(source.mailbox)-sfc_calibration::Offset;
  const auto& live=reinterpret_cast<live_owner::Store*>(base+live_owner::Offset)->header;
  const auto game=live.pid;check(game&&live_owner::header_valid(live,source.session),"game pool source PID/session");
  pool=reinterpret_cast<game_output::Pool*>(base+game_output::Offset);
  check(pool->header.magic==0,"game pool must be fresh");
  for(unsigned slot=0;slot<2;++slot)for(unsigned i=0;i<3;++i){
   D3D11_TEXTURE2D_DESC d{};d.Width=input.width;d.Height=input.height;d.MipLevels=d.ArraySize=d.SampleDesc.Count=1;
   d.Format=i?DXGI_FORMAT_R32_FLOAT:DXGI_FORMAT_B8G8R8A8_UNORM;d.BindFlags=D3D11_BIND_RENDER_TARGET|D3D11_BIND_SHADER_RESOURCE;d.MiscFlags=D3D11_RESOURCE_MISC_SHARED;
   hr(device->CreateTexture2D(&d,nullptr,&textures[slot][i]),"game pool GPU texture");
   Microsoft::WRL::ComPtr<IDXGIResource> r;hr(textures[slot][i].As(&r),"game pool shared interface");HANDLE handle=nullptr;hr(r->GetSharedHandle(&handle),"game pool handle");handles[slot][i]=reinterpret_cast<uintptr_t>(handle);
  }
  memset(pool,0,sizeof(*pool));auto& h=pool->header;h.magic=game_output::Magic;h.version=game_output::Version;h.bytes=sizeof(*pool);h.game_pid=game;
  wchar_t asset[66]{};check(GetEnvironmentVariableW(L"SFC_D3D9_ASSET_SHA256",asset,66)==64,"game pool content identity required");
  for(unsigned i=0;i<32;++i){unsigned byte=0;for(unsigned j=0;j<2;++j){const auto c=asset[2*i+j];check((c>=L'0'&&c<=L'9')||(c>=L'a'&&c<=L'f'),"game pool asset hex");byte=byte*16+unsigned(c<=L'9'?c-L'0':c-L'a'+10);}pool->asset[i]=static_cast<BYTE>(byte);}
  wchar_t offset[64]{};check(GetEnvironmentVariableW(L"SFC_D3D9_OFFSET_X",offset,64)>0,"diagnostic world offset required");
  wchar_t multi[2]{};const bool cohort=GetEnvironmentVariableW(L"SFC_D3D9_MULTISCENE",multi,2)==1&&multi[0]==L'1';
  pool->camera_offset[0]=static_cast<float>(_wtof(offset));
  check(std::isfinite(pool->camera_offset[0])&&(cohort?(pool->camera_offset[0]<=0&&pool->camera_offset[0]>=-1e6f):(pool->camera_offset[0]<-1e-5f&&pool->camera_offset[0]>=-1e6f)),"explicit aligned-cohort or camera-left diagnostic offset");
  pool->diagnostic_mode=pool->camera_offset[0]==0?0u:1u;pool->reserved[2]=cohort?1u:0u; // Union coverage,not a native per-owner picking map.
  pool->reserved[3]=retainReady?1u:0u;
  memcpy(h.session,source.session,16);h.receiver_pid=GetCurrentProcessId();h.host_pid=input.producer_pid;session=input.session;
  check(game_output::valid(h,source.session,game),"game pool header");InterlockedExchange(&h.ready,1);
 }
 int copy(ID3D11Device* device,ID3D11DeviceContext* context,const output_wire::Packet& input,const game_output::Metadata& metadata,ID3D11Texture2D* const (&images)[3]){
  prepare(device,input);
  if(!game_output::valid(metadata,source.session))return -1; // Bootstrap is never displayed.
  check(input.session==session&&input.producer_pid==pool->header.host_pid,"game pool source identity changed");
  // Buffered presentation still needs READY images;never replace one before
  // the game acquires it. Busy skips this publication,never waits on SFC.
  int slot=game_output::reserve(*pool,retainReady);if(slot<0)return -1;
  for(unsigned i=0;i<3;++i)context->CopyResource(textures[slot][i].Get(),images[i]);
  return slot;
 }
 void publish(int slot,output_wire::Packet packet,const game_output::Metadata& metadata){
  if(slot<0)return;
  auto& out=pool->slots[slot];packet.producer_pid=GetCurrentProcessId();packet.resource_epoch=static_cast<uint64_t>(slot+1);
  memcpy(packet.handles,handles[slot],sizeof(packet.handles));packet.checksum=output_wire::checksum(packet);
  out.packet=packet;game_output::metadata(out,metadata);InterlockedIncrement(&pool->header.published);InterlockedExchange(&out.state,output_wire::ready);
 }
};
