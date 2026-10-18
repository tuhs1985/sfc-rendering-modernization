#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include "ship_triplet_compositor.h"
#include <iostream>
#include <vector>
#include <fstream>
// Offline x86 test pilot for the SAME native Consumer class. Readback belongs
// here,not in that class or a future SFC render callback.
int wmain(int argc,wchar_t** argv){
 if(argc!=2)return 2;
 std::ofstream log("triplet-consumer.log",std::ios::trunc);
 if(!log)return 5;
 struct LogScope{std::streambuf* original;~LogScope(){std::cout.rdbuf(original);}} scope{std::cout.rdbuf(log.rdbuf())};
 std::cout.setf(std::ios::unitbuf);
 try{
  return_path::Mapping mapping(false,argv[1]);auto& s=*reinterpret_cast<ship_triplet::Wire*>(reinterpret_cast<BYTE*>(mapping.state)+ship_triplet::Offset);
  using namespace ship_triplet;Key expected=s.requested;Key named{};sessionKey(mapping.name,named);
  if(!valid(s)||std::memcmp(named.session,s.session,16)||!same(expected,s.requested))throw std::runtime_error("consumer session");
  ComPtr<ID3D11Device> d;ComPtr<ID3D11DeviceContext> c;D3D_FEATURE_LEVEL level=D3D_FEATURE_LEVEL_10_1;
  checked(D3D11CreateDevice(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,0,&level,1,D3D11_SDK_VERSION,&d,nullptr,&c),"consumer10_1");
  Consumer consumer(s,d.Get());std::array<ComPtr<ID3D11Texture2D>,3> staging;
  for(unsigned i=0;i<3;++i){D3D11_TEXTURE2D_DESC desc{};consumer.textures[i]->GetDesc(&desc);desc.Usage=D3D11_USAGE_STAGING;desc.BindFlags=desc.MiscFlags=0;desc.CPUAccessFlags=D3D11_CPU_ACCESS_READ;
   checked(d->CreateTexture2D(&desc,nullptr,&staging[i]),"consumer staging");}
  Compositor compositor(d.Get());ComPtr<ID3D11Texture2D> composed,readComposed,sentinel;
  ComPtr<ID3D11RenderTargetView> composedView,sentinelView;
  D3D11_TEXTURE2D_DESC td{};td.Width=s.width+16;td.Height=s.height+16;td.MipLevels=td.ArraySize=1;td.Format=DXGI_FORMAT_B8G8R8A8_UNORM;td.SampleDesc.Count=1;td.BindFlags=D3D11_BIND_RENDER_TARGET;
  checked(d->CreateTexture2D(&td,nullptr,&composed),"composed target");checked(d->CreateRenderTargetView(composed.Get(),nullptr,&composedView),"composed view");
  checked(d->CreateTexture2D(&td,nullptr,&sentinel),"state sentinel");checked(d->CreateRenderTargetView(sentinel.Get(),nullptr,&sentinelView),"sentinel view");
  td.BindFlags=0;td.Usage=D3D11_USAGE_STAGING;td.CPUAccessFlags=D3D11_CPU_ACCESS_READ;
  checked(d->CreateTexture2D(&td,nullptr,&readComposed),"composed staging");
  const size_t pixelsCount=size_t(s.width)*s.height;
  std::vector<uint32_t> colors(pixelsCount),ids(pixelsCount);std::vector<float> depths(pixelsCount);
  ComPtr<ID3D11Buffer> sentinelBuffer;D3D11_BUFFER_DESC bd{};bd.ByteWidth=32;bd.BindFlags=D3D11_BIND_CONSTANT_BUFFER;
  checked(d->CreateBuffer(&bd,nullptr,&sentinelBuffer),"sentinel buffer");
  store(s.consumerPid,static_cast<LONG>(GetCurrentProcessId()));LONG last=0;const auto deadline=GetTickCount64()+110000;
  wchar_t fault[8]{};GetEnvironmentVariableW(L"SFC_TRIPLET_FAULT",fault,8);bool faultDone=false;
  while(!load(s.stop)){
   if(GetTickCount64()>deadline)throw std::runtime_error("consumer110s cap");
   if(!faultDone&&load(s.lease)==Ready){faultDone=true;if(fault[0]==L'e')return 9;if(fault[0]==L's')Sleep(6000);}
   if(!consumer.acquire(expected)){Sleep(1);continue;}
   const LONG sequence=load(s.sequence);if(sequence!=last+1)throw std::runtime_error("consumer sequence");
   if(consumer.poll())throw std::runtime_error("GPU lease acknowledged before submission");
   auto* oldTarget=sentinelView.Get();c->OMSetRenderTargets(1,&oldTarget,nullptr);
   auto* oldBuffer=sentinelBuffer.Get();c->PSSetConstantBuffers(0,1,&oldBuffer);
   auto* oldView=consumer.views[0].Get();c->PSSetShaderResources(4,1,&oldView);
   c->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_LINELIST);
   const D3D11_VIEWPORT oldViewport{3,4,101,102,0,1};c->RSSetViewports(1,&oldViewport);
   const float background[]={17.f/255,35.f/255,51.f/255,1};c->ClearRenderTargetView(composedView.Get(),background);
   ID3D11ShaderResourceView* inputViews[]={consumer.views[0].Get(),consumer.views[1].Get(),consumer.views[2].Get()};
   const D3D11_VIEWPORT viewport{8,8,static_cast<float>(s.width),static_cast<float>(s.height),0,1};
   if(!compositor.draw(composedView.Get(),inputViews,expected,viewport))throw std::runtime_error("compositor draw");
   ComPtr<ID3D11RenderTargetView> restoredTarget;c->OMGetRenderTargets(1,&restoredTarget,nullptr);
   ComPtr<ID3D11Buffer> restoredBuffer;c->PSGetConstantBuffers(0,1,&restoredBuffer);
   ComPtr<ID3D11ShaderResourceView> restoredView;c->PSGetShaderResources(4,1,&restoredView);
   D3D11_PRIMITIVE_TOPOLOGY topology{};c->IAGetPrimitiveTopology(&topology);
   D3D11_VIEWPORT restoredViewport{};UINT viewportCount=1;c->RSGetViewports(&viewportCount,&restoredViewport);
   if(restoredTarget.Get()!=oldTarget||restoredBuffer.Get()!=oldBuffer||restoredView.Get()!=oldView||
      topology!=D3D11_PRIMITIVE_TOPOLOGY_LINELIST||viewportCount!=1||memcmp(&oldViewport,&restoredViewport,sizeof(oldViewport)))throw std::runtime_error("compositor state restoration");
   c->CopyResource(readComposed.Get(),composed.Get());
   for(unsigned i=0;i<3;++i)c->CopyResource(staging[i].Get(),consumer.textures[i].Get());
   consumer.submitted();c->Flush();
   // Verify CPU bytes before ACK to keep this test's expected hashes leased.
   uint64_t hashes[3]{};unsigned ownedPixels=0;
   for(unsigned i=0;i<3;++i){D3D11_MAPPED_SUBRESOURCE pixels{};checked(c->Map(staging[i].Get(),0,D3D11_MAP_READ,0,&pixels),"fixture GPU readback");
    bool malformed=false;uint64_t h=14695981039346656037ull;for(unsigned y=0;y<s.height;++y){const auto* row=static_cast<const BYTE*>(pixels.pData)+size_t(y)*pixels.RowPitch;
     for(unsigned x=0;x<s.width*4;++x){h^=row[x];h*=1099511628211ull;}
     for(unsigned x=0;x<s.width;++x){
      if(i==2){uint32_t id=0;std::memcpy(&id,row+x*4,4);if(id&&id!=expected.objectId)malformed=true;if(id)++ownedPixels;}
      if(i==1){float z=0;std::memcpy(&z,row+x*4,4);if(!std::isfinite(z)||(z!=-1234&&(z<0||z>1)))malformed=true;}}
    }
    void* destination=i==0?static_cast<void*>(colors.data()):i==1?static_cast<void*>(depths.data()):static_cast<void*>(ids.data());
    for(unsigned y=0;y<s.height;++y)memcpy(static_cast<BYTE*>(destination)+size_t(y)*s.width*4,static_cast<const BYTE*>(pixels.pData)+size_t(y)*pixels.RowPitch,size_t(s.width)*4);
    hashes[i]=h;c->Unmap(staging[i].Get(),0);if(malformed||h!=s.expected[i])throw std::runtime_error("triplet bytes/owner/depth differ");}
   D3D11_MAPPED_SUBRESOURCE compositePixels{};checked(c->Map(readComposed.Get(),0,D3D11_MAP_READ,0,&compositePixels),"compositor verify");
   bool exact=true;unsigned drawn=0;
   for(unsigned y=0;y<td.Height;++y)for(unsigned x=0;x<td.Width;++x){
    uint32_t expectedPixel=0xff112333;
    if(x>=8&&y>=8&&x<s.width+8&&y<s.height+8){const auto i=size_t(y-8)*s.width+x-8;
     if(ids[i]==expected.objectId&&std::isfinite(depths[i])&&depths[i]>=0&&depths[i]<=1){expectedPixel=colors[i]|0xff000000;++drawn;}}
    uint32_t actual=0;memcpy(&actual,static_cast<const BYTE*>(compositePixels.pData)+size_t(y)*compositePixels.RowPitch+x*4,4);if(actual!=expectedPixel)exact=false;}
   c->Unmap(readComposed.Get(),0);if(!exact||drawn<=10)throw std::runtime_error("compositor mask/background/color mismatch");
   if(ownedPixels<=10)throw std::runtime_error("missing returned owner coverage");std::memcpy(s.consumed,hashes,sizeof(hashes));
   while(!consumer.poll()){if(load(s.error)||GetTickCount64()>deadline)throw std::runtime_error("consumer completion");Sleep(1);}
   last=sequence;
  }
  c->ClearState();std::cout<<"TRIPLET_X86_CONSUMER_PASS sequences="<<last<<" masked_composite=exact state_restored=1\n";return last==2?0:4;
 }catch(const std::exception& e){std::cout<<"TRIPLET_X86_FAILED "<<e.what()<<"\n";return 3;}
}
