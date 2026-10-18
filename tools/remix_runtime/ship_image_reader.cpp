// Owned external one-shot worker. All CPU readback and disk IO stay OUT of SFC.
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <d3d11.h>
#include <dxgi.h>
#include <wrl/client.h>
#include <fstream>
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include "ship_image_snapshot.h"
using Microsoft::WRL::ComPtr;
static void check(HRESULT h){if(FAILED(h))throw std::runtime_error("image worker D3D failure");}
int wmain(int argc,wchar_t** argv){
 if(argc!=3)return 2;
 try{
  return_path::Mapping m(false,argv[1]);auto& h=ship_image::header(m);
  const auto until=GetTickCount64()+95000;
  while(return_path::read(h.status)!=ship_image::Ready){
   const auto status=return_path::read(h.status);
   if(GetTickCount64()>until||status==ship_image::Error||status==ship_image::Cancelled||return_path::read(m.state->stop))throw std::runtime_error("no prepared image before stop/limit");
   Sleep(20);
  }
  if(!ship_image::valid(h)||h.pid!=m.state->gamePid||!ship_triplet::validKey(h.key)||h.pid!=h.key.sourcePid||h.width!=h.key.width||h.height!=h.key.height||h.flags!=1||!h.sequence||!h.model||!h.source)throw std::runtime_error("image identity/metadata invalid");
  if(InterlockedCompareExchange(&h.status,ship_image::Reading,ship_image::Ready)!=ship_image::Ready)throw std::runtime_error("image lease unavailable");
  ComPtr<ID3D11Device> d;ComPtr<ID3D11DeviceContext> c;D3D_FEATURE_LEVEL level{};
  check(D3D11CreateDevice(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,0,nullptr,0,D3D11_SDK_VERSION,&d,&level,&c));
  ComPtr<IDXGIDevice> dx;ComPtr<IDXGIAdapter> adapter;DXGI_ADAPTER_DESC ad{};
  check(d.As(&dx));check(dx->GetAdapter(&adapter));check(adapter->GetDesc(&ad));
  auto& wire=*reinterpret_cast<ship_triplet::Wire*>(reinterpret_cast<BYTE*>(m.state)+ship_triplet::Offset);
  if(ad.AdapterLuid.LowPart!=wire.adapterLow||static_cast<uint32_t>(ad.AdapterLuid.HighPart)!=wire.adapterHigh)throw std::runtime_error("image worker adapter mismatch");
  ComPtr<ID3D11Texture2D> image,staging;check(d->OpenSharedResource(reinterpret_cast<HANDLE>(static_cast<uintptr_t>(h.handle)),IID_PPV_ARGS(&image)));
  D3D11_TEXTURE2D_DESC desc{};image->GetDesc(&desc);
  if(desc.Width!=h.width||desc.Height!=h.height||desc.Format!=DXGI_FORMAT_B8G8R8A8_UNORM||desc.MipLevels!=1||desc.ArraySize!=1||desc.SampleDesc.Count!=1)throw std::runtime_error("image descriptor mismatch");
  desc.Usage=D3D11_USAGE_STAGING;desc.BindFlags=desc.MiscFlags=0;desc.CPUAccessFlags=D3D11_CPU_ACCESS_READ;
  check(d->CreateTexture2D(&desc,nullptr,&staging));D3D11_QUERY_DESC query{D3D11_QUERY_EVENT,0};ComPtr<ID3D11Query> done;check(d->CreateQuery(&query,&done));
  c->CopyResource(staging.Get(),image.Get());c->End(done.Get());c->Flush();BOOL complete=FALSE;const auto gpuUntil=GetTickCount64()+5000;
  while(c->GetData(done.Get(),&complete,sizeof(complete),0)!=S_OK||!complete){if(GetTickCount64()>gpuUntil)throw std::runtime_error("image worker GPU timeout");Sleep(1);}
  const auto path=std::filesystem::path(argv[2])/L"prepared-ship-image.sfcimg";
  if(!std::filesystem::is_directory(path.parent_path())||std::filesystem::exists(path))throw std::runtime_error("image output exists/missing folder");
  D3D11_MAPPED_SUBRESOURCE data{};check(c->Map(staging.Get(),0,D3D11_MAP_READ,0,&data));
  ship_image::Header captured{};memcpy(&captured,&h,sizeof(h));
  std::ofstream f(path,std::ios::binary);f.write(reinterpret_cast<const char*>(&captured),sizeof(captured));
  for(uint32_t y=0;y<h.height;++y)f.write(static_cast<const char*>(data.pData)+size_t(y)*data.RowPitch,size_t(h.width)*4);
  c->Unmap(staging.Get(),0);f.close();if(!f)throw std::runtime_error("image worker output failure");
  return_path::write(h.status,ship_image::Written);std::cout<<"PREPARED_IMAGE_SAVED sequence="<<h.sequence<<" frame="<<h.key.frame<<" owner="<<h.key.owner<<" size="<<h.width<<"x"<<h.height<<"\n";return 0;
 }catch(const std::exception& e){std::cout<<"PREPARED_IMAGE_PARTIAL "<<e.what()<<"\n";return 1;}
}
