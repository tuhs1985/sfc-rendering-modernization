// Default-off ONE immutable prepared-layer GPU snapshot. No callback Map/IO/wait.
#pragma once
#include "ship_live_request.h"
namespace ship_image {
using Microsoft::WRL::ComPtr;
constexpr uint32_t Offset=2304,Magic=0x31495353,Version=1;
enum Status:LONG{Off,Armed,Copying,Ready,Reading,Written,Error,Cancelled};
struct alignas(8) Header {
 uint32_t magic=Magic,version=Version,bytes=sizeof(Header);volatile LONG status=Off;
 uint32_t pid=0,width=0,height=0,format=87;
 uint64_t handle=0,capturedAt=0,sourceObservedAt=0,frequency=0;
 uint32_t sequence=0,flags=0;float rect[4]{};ship_triplet::Key key{};
 uint32_t error=0,model=0,source=0,lod=0;
};
static_assert(sizeof(Header)==256&&Offset>=ship_live::RegistrationOffset+sizeof(ship_live::Registration)&&Offset+sizeof(Header)<4096);
inline Header& header(return_path::Mapping& m){return *reinterpret_cast<Header*>(reinterpret_cast<BYTE*>(m.state)+Offset);}
inline bool valid(const Header& h){return h.magic==Magic&&h.version==Version&&h.bytes==sizeof(Header)&&h.pid&&h.format==87&&ship_triplet::dimensions(h.width,h.height)&&h.handle&&h.handle<=UINT32_MAX&&h.frequency;}
class Snapshot {
 Header& h;ComPtr<ID3D11Texture2D> target;ComPtr<ID3D11Query> fence;
 uint64_t firstDisplay=0,delayMs=15000;bool submitted=false;
public:
 explicit Snapshot(return_path::Mapping& m):h(header(m)){}
 void init(ID3D11Device* d,uint32_t width,uint32_t height,uint64_t frequency){
  if(GetEnvironmentVariableW(L"SFC_REMIX_CAPTURE_SHIP_IMAGE",nullptr,0)==0)return;
  // Device recreation must not overwrite an immutable snapshot or reader lease.
  // A cancelled/failed request remains PARTIAL; never silently take another shot.
  if(h.magic==Magic&&h.version==Version&&h.pid==GetCurrentProcessId()&&return_path::read(h.status)!=Off)return;
  h=Header{};h.pid=GetCurrentProcessId();h.width=width;h.height=height;h.frequency=frequency;
  wchar_t text[16]{};const auto n=GetEnvironmentVariableW(L"SFC_REMIX_CAPTURE_SHIP_IMAGE_DELAY_MS",text,16);
  if(n){wchar_t* end=nullptr;const auto value=wcstoul(text,&end,10);if(n>=16||!end||*end||value>15000){h.error=1;return_path::write(h.status,Error);return;}delayMs=value;}
  D3D11_TEXTURE2D_DESC desc{};desc.Width=width;desc.Height=height;desc.MipLevels=desc.ArraySize=1;desc.Format=DXGI_FORMAT_B8G8R8A8_UNORM;desc.SampleDesc.Count=1;desc.MiscFlags=D3D11_RESOURCE_MISC_SHARED;desc.BindFlags=D3D11_BIND_SHADER_RESOURCE;
  D3D11_QUERY_DESC q{D3D11_QUERY_EVENT,0};ComPtr<IDXGIResource> resource;HANDLE handle=nullptr;
  if(!ship_triplet::dimensions(width,height)||FAILED(d->CreateTexture2D(&desc,nullptr,&target))||FAILED(d->CreateQuery(&q,&fence))||FAILED(target.As(&resource))||FAILED(resource->GetSharedHandle(&handle))||!handle){h.error=2;return_path::write(h.status,Error);return;}
  h.handle=static_cast<uint64_t>(reinterpret_cast<uintptr_t>(handle));return_path::write(h.status,Armed);
 }
 void poll(ID3D11DeviceContext* context){
  if(return_path::read(h.status)!=Copying||!submitted)return;
  BOOL done=FALSE;const auto status=context->GetData(fence.Get(),&done,sizeof(done),D3D11_ASYNC_GETDATA_DONOTFLUSH);
  if(FAILED(status)){h.error=3;return_path::write(h.status,Error);}
  else if(status==S_OK&&done&&(h.flags&1))return_path::write(h.status,Ready);
 }
 void enqueue(ID3D11DeviceContext* context,ID3D11Texture2D* texture,const ship_triplet::Key& key,LONG sequence,uint64_t observed,const float (&rect)[4],const ship_live::Seed& seed){
  if(return_path::read(h.status)!=Armed||!target||!texture||sequence<=0)return;
  const auto now=return_path::now();if(!firstDisplay)firstDisplay=now;
  if(now-firstDisplay<h.frequency*delayMs/1000)return;
  h.key=key;h.sequence=static_cast<uint32_t>(sequence);h.sourceObservedAt=observed;h.capturedAt=now;
  memcpy(h.rect,rect,sizeof(h.rect));h.model=seed.model;h.source=seed.source;h.lod=seed.lod;
  context->CopyResource(target.Get(),texture);context->End(fence.Get());submitted=true;return_path::write(h.status,Copying);
 }
 void markDisplay(){if(submitted&&return_path::read(h.status)==Copying)h.flags|=1;}
 void stop(){const auto s=return_path::read(h.status);if(s==Armed||s==Copying)return_path::write(h.status,Cancelled);}
};
}
