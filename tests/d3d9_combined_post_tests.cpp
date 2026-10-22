// Actual GPU equivalence and bounded same-device timestamp comparison.
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <d3d11.h>
#include <wrl/client.h>
#include <array>
#include <algorithm>
#include <vector>
#include <iostream>
#include <cstring>
#include <limits>
#include <stdexcept>
#include <cmath>
#include "../tools/d3d9_proof/output_channel.h"
static void check(HRESULT r,const char* why){if(FAILED(r))throw std::runtime_error(why);}
static void require(bool r,const char* why){if(!r)throw std::runtime_error(why);}
#include "../tools/remix_runtime/remix_image_adjust.h"
#include "../tools/d3d9_proof/normal_coverage.h"
using Microsoft::WRL::ComPtr;
static std::vector<BYTE> read(ID3D11Device* d,ID3D11DeviceContext* c,ID3D11Texture2D* t){
 D3D11_TEXTURE2D_DESC desc{};t->GetDesc(&desc);desc.BindFlags=desc.MiscFlags=0;desc.Usage=D3D11_USAGE_STAGING;desc.CPUAccessFlags=D3D11_CPU_ACCESS_READ;
 ComPtr<ID3D11Texture2D> copy;check(d->CreateTexture2D(&desc,nullptr,&copy),"test staging");c->CopyResource(copy.Get(),t);
 D3D11_MAPPED_SUBRESOURCE m{};check(c->Map(copy.Get(),0,D3D11_MAP_READ,0,&m),"test readback");std::vector<BYTE> out(size_t(desc.Width)*desc.Height*4);
 for(unsigned y=0;y<desc.Height;++y)memcpy(out.data()+size_t(y)*desc.Width*4,static_cast<BYTE*>(m.pData)+size_t(y)*m.RowPitch,size_t(desc.Width)*4);
 c->Unmap(copy.Get(),0);return out;
}
int main(){try{
 SetEnvironmentVariableW(L"SFC_D3D9_COVERAGE_TEST",L"1");ComPtr<ID3D11Device> device;ComPtr<ID3D11DeviceContext> context;
 check(D3D11CreateDevice(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,0,nullptr,0,D3D11_SDK_VERSION,&device,nullptr,&context),"actual GPU device");
 unsigned checks=0;auto test=[&](bool r){++checks;require(r,"combined post mismatch");};
 D3D11_TEXTURE2D_DESC desc{};desc.Width=1920;desc.Height=1080;desc.MipLevels=desc.ArraySize=desc.SampleDesc.Count=1;desc.Format=DXGI_FORMAT_B8G8R8A8_UNORM;desc.BindFlags=D3D11_BIND_RENDER_TARGET|D3D11_BIND_SHADER_RESOURCE;
 ComPtr<ID3D11Texture2D> colors[2],masks[2],depth;for(auto& c:colors)check(device->CreateTexture2D(&desc,nullptr,&c),"color");
 desc.Format=DXGI_FORMAT_R32_FLOAT;for(auto& m:masks)check(device->CreateTexture2D(&desc,nullptr,&m),"mask");check(device->CreateTexture2D(&desc,nullptr,&depth),"depth");
 std::vector<BYTE> color(size_t(desc.Width)*desc.Height*4);std::vector<float> z(size_t(desc.Width)*desc.Height);
 const float depths[]{0,.2f,1,-1,2,std::numeric_limits<float>::quiet_NaN(),std::numeric_limits<float>::infinity()};
 for(size_t i=0;i<z.size();++i){z[i]=depths[i%7];color[i*4]=BYTE(i%256);color[i*4+1]=BYTE((i/13)%256);color[i*4+2]=BYTE((i/257)%256);color[i*4+3]=BYTE((i/17)%256);}
 context->UpdateSubresource(depth.Get(),0,nullptr,z.data(),desc.Width*4,0);RemixImageAdjust grade[2];NormalCoverage coverage;
 for(unsigned i=0;i<2;++i)grade[i].prepare(device.Get(),colors[i].Get());grade[1].prepareCoverage(device.Get(),depth.Get(),masks[1].Get());coverage.start(device.Get(),depth.Get(),masks[0].Get());
 const std::array<float,4> parameters[]{{1,1,1,0},{1.12f,.7f,1.2f,0},{0,.25f,0,0},{2,4,2,0}};
 for(const auto& p:parameters)for(uint32_t owner:{1u,2u,32u,0x01000001u}){
  for(auto& c:colors)context->UpdateSubresource(c.Get(),0,nullptr,color.data(),desc.Width*4,0);
  grade[0].draw(context.Get(),colors[0].Get(),p);coverage.draw(context.Get(),owner,desc.Width,desc.Height);
  grade[1].drawCoverage(context.Get(),colors[1].Get(),p,owner);
  const auto a=read(device.Get(),context.Get(),colors[0].Get()),b=read(device.Get(),context.Get(),colors[1].Get());test(a==b);
  const auto m=read(device.Get(),context.Get(),masks[1].Get());test(m==read(device.Get(),context.Get(),masks[0].Get()));
  bool good=true;for(size_t i=0;i<z.size();++i){uint32_t v=0;memcpy(&v,m.data()+i*4,4);if(v!=(std::isfinite(z[i])&&z[i]>=0&&z[i]<=1?owner:0u)){good=false;break;}}test(good);
 }
 bool rejected=false;try{grade[1].drawCoverage(context.Get(),colors[1].Get(),parameters[0],0);}catch(const std::runtime_error&){rejected=true;}test(rejected);
 // Eight batches per route,alternated order;median limits scheduling outliers.
 // GPU timestamps exclude CPU recording;this is NOT whole-renderer timing.
 std::array<double,8> batches[2]{};
 for(unsigned round=0;round<16;++round){unsigned route=round%2;ComPtr<ID3D11Query> disjoint,begin,end;
  D3D11_QUERY_DESC q{D3D11_QUERY_TIMESTAMP_DISJOINT,0};check(device->CreateQuery(&q,&disjoint),"disjoint");q.Query=D3D11_QUERY_TIMESTAMP;check(device->CreateQuery(&q,&begin),"timestamp");check(device->CreateQuery(&q,&end),"timestamp");
  context->Begin(disjoint.Get());context->End(begin.Get());for(unsigned n=0;n<32;++n){if(route)grade[1].drawCoverage(context.Get(),colors[1].Get(),parameters[1],2);else{grade[0].draw(context.Get(),colors[0].Get(),parameters[1]);coverage.draw(context.Get(),2,desc.Width,desc.Height);}}
  context->End(end.Get());context->End(disjoint.Get());context->Flush();D3D11_QUERY_DATA_TIMESTAMP_DISJOINT rate{};const auto deadline=GetTickCount64()+5000;HRESULT status;
  while((status=context->GetData(disjoint.Get(),&rate,sizeof(rate),0))==S_FALSE){require(GetTickCount64()<deadline,"GPU test timeout");Sleep(1);}check(status,"GPU disjoint");test(!rate.Disjoint&&rate.Frequency);
  UINT64 a=0,b=0;check(context->GetData(begin.Get(),&a,sizeof(a),0),"begin");check(context->GetData(end.Get(),&b,sizeof(b),0),"end");require(b>=a,"timestamp order");
  batches[route][round/2]=double(b-a)*1e6/double(rate.Frequency)/32;
  std::cout<<"POST_GPU route="<<(route?"combined":"separate")<<" round="<<round<<" mean_us="<<batches[route][round/2]<<'\n';
 }
 for(unsigned route=0;route<2;++route){auto& b=batches[route];std::sort(b.begin(),b.end());std::cout<<"POST_GPU_MEDIAN route="<<(route?"combined":"separate")<<" batches=8 us="<<(b[3]+b[4])/2<<'\n';}
 context->ClearState();context->Flush();check(device->GetDeviceRemovedReason(),"GPU healthy");SetEnvironmentVariableW(L"SFC_D3D9_COVERAGE_TEST",nullptr);
 std::cout<<"Combined post PASS "<<checks<<" checks exact_color_alpha_owner_sentinel=1 size=1920x1080\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}return 0;}
