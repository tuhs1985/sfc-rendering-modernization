#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <d3d11.h>
#include <wrl/client.h>
#include <reshade.hpp>
#include <fstream>
#include <iostream>
#include <vector>
#include "../tools/remix_runtime/return_wire.h"
#include "../tools/remix_runtime/depth_snapshot.h"
using Microsoft::WRL::ComPtr;
static void check(bool v,const char* s){if(!v)throw std::runtime_error(s);}
int wmain(int argc,wchar_t** argv){try{
 check(argc==2,"unique output directory required");check(CreateDirectoryW(argv[1],nullptr)!=FALSE,"output must be new");
 ComPtr<ID3D11Device> d;ComPtr<ID3D11DeviceContext> c;
 const D3D_FEATURE_LEVEL level=D3D_FEATURE_LEVEL_10_1;
 check(SUCCEEDED(D3D11CreateDevice(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,0,&level,1,D3D11_SDK_VERSION,&d,nullptr,&c)),"explicit10_1 hardware device");
 check(d->GetFeatureLevel()==level,"actual10_1,no higher-feature fallback");
 const char* oldCS="RWTexture2D<float4> o:register(u0);[numthreads(1,1,1)]void main(uint3 p:SV_DispatchThreadID){o[p.xy]=1;}";
 ComPtr<ID3DBlob> oldCode;ComPtr<ID3D11ComputeShader> oldShader;
 check(SUCCEEDED(D3DCompile(oldCS,strlen(oldCS),nullptr,nullptr,nullptr,"main","cs_5_0",0,0,&oldCode,nullptr)),"old profile compile");
 const HRESULT legacy=d->CreateComputeShader(oldCode->GetBufferPointer(),oldCode->GetBufferSize(),nullptr,&oldShader);
 check(FAILED(legacy),"SM5 rejected by10_1 device");
 {std::ofstream f(std::wstring(argv[1])+L"\\legacy-profile-check.json");f<<"{\"feature_level\":"<<static_cast<unsigned>(level)<<",\"legacy_create_shader_hresult\":"<<static_cast<unsigned>(legacy)<<"}";}
 D3D11_TEXTURE2D_DESC desc{};desc.Width=64;desc.Height=48;desc.MipLevels=desc.ArraySize=1;desc.Format=DXGI_FORMAT_R32_TYPELESS;desc.SampleDesc.Count=8;desc.BindFlags=D3D11_BIND_DEPTH_STENCIL|D3D11_BIND_SHADER_RESOURCE;
 check(depth_snapshot::supported(desc),"supported descriptor");
 auto bad=desc;bad.SampleDesc.Count=4;check(!depth_snapshot::supported(bad),"unsupported sample count");bad=desc;bad.Width=1921;check(!depth_snapshot::supported(bad),"dimension bound");bad=desc;bad.ArraySize=2;check(!depth_snapshot::supported(bad),"array rejection");
 ComPtr<ID3D11Texture2D> z,color;check(SUCCEEDED(d->CreateTexture2D(&desc,nullptr,&z)),"8sample depth creation");
 D3D11_DEPTH_STENCIL_VIEW_DESC vd{};vd.Format=DXGI_FORMAT_D32_FLOAT;vd.ViewDimension=D3D11_DSV_DIMENSION_TEXTURE2DMS;
 ComPtr<ID3D11DepthStencilView> dv;check(SUCCEEDED(d->CreateDepthStencilView(z.Get(),&vd,&dv)),"depth view");
 desc.Format=DXGI_FORMAT_B8G8R8A8_UNORM;desc.SampleDesc.Count=1;desc.BindFlags=D3D11_BIND_RENDER_TARGET|D3D11_BIND_SHADER_RESOURCE;
 check(SUCCEEDED(d->CreateTexture2D(&desc,nullptr,&color)),"color creation");ComPtr<ID3D11RenderTargetView> rt;check(SUCCEEDED(d->CreateRenderTargetView(color.Get(),nullptr,&rt)),"color view");
 float rgba[]={1,0,1,1};c->ClearRenderTargetView(rt.Get(),rgba);c->ClearDepthStencilView(dv.Get(),D3D11_CLEAR_DEPTH,.625f,0);
 D3D11_DEPTH_STENCIL_DESC ds{};ds.DepthEnable=TRUE;ds.DepthWriteMask=D3D11_DEPTH_WRITE_MASK_ALL;ds.DepthFunc=D3D11_COMPARISON_ALWAYS;
 ComPtr<ID3D11DepthStencilState> state;check(SUCCEEDED(d->CreateDepthStencilState(&ds,&state)),"depth state");c->OMSetDepthStencilState(state.Get(),7);
 c->OMSetRenderTargets(0,nullptr,dv.Get());
 ComPtr<ID3D11ShaderResourceView> sentinel;check(SUCCEEDED(d->CreateShaderResourceView(color.Get(),nullptr,&sentinel)),"sentinel view");ID3D11ShaderResourceView* originalSRV=sentinel.Get();c->PSSetShaderResources(0,1,&originalSRV);
 D3D11_VIEWPORT viewport{3,4,20,21,.2f,.9f};c->RSSetViewports(1,&viewport);
 return_path::State control{};control.armed=1;
 sfc_calibration::Reader provider;check(provider.prepare(),"optional calibration mapping");
 DWORD engineFrame=0;
 if(provider.requested){provider.mailbox->snapshot={};
  std::memcpy(provider.mailbox->snapshot.session,provider.session,16);provider.mailbox->active=1;}
 auto originalDraw=[&](){if(provider.requested){
  sfc_calibration::begin(provider.mailbox,++engineFrame);
  std::array<DWORD,96> r{};r[1]=7;r[2]=engineFrame;r[4]=1;r[5]=99;r[6]=98;r[7]=1;r[47]=GetCurrentThreadId();r[48]=1;
  check(sfc_calibration::offer(provider.mailbox,0,r),"fixture semantic publish");}
 };
 auto cap=std::make_unique<depth_snapshot::Capture>();check(cap->prepare(&control,argv[1]),"CPU storage/worker");cap->init(d.Get());originalDraw();cap->draw();
 // No ship source field or image is guessed: all8samples have known clear value.
 cap->present(color.Get(),100);
 for(unsigned shot=0;shot<3;++shot){
  if(shot==1){
   const char* vs="float4 main(uint id:SV_VertexID):SV_Position{float2 p[3]={float2(-1,-1),float2(-1,3),float2(3,-1)};return float4(p[id],0,1);}";
   const char* ps="float main(float4 p:SV_Position,uint s:SV_SampleIndex):SV_Depth{return .1+.08*s+.001*p.x+.002*p.y;}";
   ComPtr<ID3DBlob> vb,pb;ComPtr<ID3D11VertexShader> vertex;ComPtr<ID3D11PixelShader> pixel;
   check(SUCCEEDED(D3DCompile(vs,strlen(vs),nullptr,nullptr,nullptr,"main","vs_4_1",0,0,&vb,nullptr)),"sample VS compile");
   check(SUCCEEDED(D3DCompile(ps,strlen(ps),nullptr,nullptr,nullptr,"main","ps_4_1",0,0,&pb,nullptr)),"sample PS compile");
   check(SUCCEEDED(d->CreateVertexShader(vb->GetBufferPointer(),vb->GetBufferSize(),nullptr,&vertex)),"sample VS");
   check(SUCCEEDED(d->CreatePixelShader(pb->GetBufferPointer(),pb->GetBufferSize(),nullptr,&pixel)),"sample PS");
   D3D11_RASTERIZER_DESC rd{};rd.FillMode=D3D11_FILL_SOLID;rd.CullMode=D3D11_CULL_NONE;rd.DepthClipEnable=TRUE;rd.MultisampleEnable=TRUE;
   ComPtr<ID3D11RasterizerState> raster;check(SUCCEEDED(d->CreateRasterizerState(&rd,&raster)),"sample raster");c->RSSetState(raster.Get());
   D3D11_VIEWPORT full{0,0,64,48,0,1};c->RSSetViewports(1,&full);c->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);c->VSSetShader(vertex.Get(),nullptr,0);c->PSSetShader(pixel.Get(),nullptr,0);c->Draw(3,0);
   c->VSSetShader(nullptr,nullptr,0);c->PSSetShader(nullptr,nullptr,0);c->RSSetViewports(1,&viewport);
  }
  const uint64_t t=2200+uint64_t(shot)*5000;originalDraw();cap->draw();cap->present(color.Get(),t);c->Flush();
  for(unsigned i=0;i<40;++i){originalDraw();cap->draw();cap->present(color.Get(),t+1+i);Sleep(5);}
  ComPtr<ID3D11DepthStencilView> actual;c->OMGetRenderTargets(0,nullptr,&actual);check(actual.Get()==dv.Get(),"original DSV restored");
  ComPtr<ID3D11DepthStencilState> actualState;UINT ref=0;c->OMGetDepthStencilState(&actualState,&ref);check(actualState.Get()==state.Get()&&ref==7,"depth state/reference restored");
  D3D11_VIEWPORT actualViewport{};UINT n=1;c->RSGetViewports(&n,&actualViewport);check(n==1&&!std::memcmp(&viewport,&actualViewport,sizeof(viewport)),"viewport restored");
  ComPtr<ID3D11ComputeShader> cs;c->CSGetShader(&cs,nullptr,nullptr);check(!cs,"compute shader binding restored");
  ComPtr<ID3D11ShaderResourceView> actualSRV;c->PSGetShaderResources(0,1,&actualSRV);check(actualSRV.Get()==sentinel.Get(),"original pixel resource restored");
  ComPtr<ID3D11PixelShader> actualPS;c->PSGetShader(&actualPS,nullptr,nullptr);check(!actualPS,"pixel shader restored");
  ComPtr<ID3D11VertexShader> actualVS;c->VSGetShader(&actualVS,nullptr,nullptr);check(!actualVS,"vertex shader restored");
 }
 cap->shutdown();
 if(provider.requested){provider.mailbox->active=0;provider.close();}
 for(unsigned i=0;i<3;++i){wchar_t p[1100]{};swprintf_s(p,L"%s\\depth-%u.bin",argv[1],i);std::ifstream f(p,std::ios::binary);check(bool(f),"snapshot file");depth_snapshot::Header h{};f.read(reinterpret_cast<char*>(&h),sizeof(h));
  check(h.fields[0]==0x44535031&&h.fields[3]==32&&h.fields[4]==24&&h.fields[9]==8,"wire descriptor");
  std::vector<float> values(32*24*4);f.read(reinterpret_cast<char*>(values.data()),static_cast<std::streamsize>(values.size()*sizeof(float)));
  for(unsigned y=0;y<24;++y)for(unsigned x=0;x<32;++x){const float base=.1015f+.002f*x+.004f*y;float expected[]={base,base,base+.56f,base+.28f};for(unsigned j=0;j<4;++j)check(std::abs(values[(y*32+x)*4+j]-(i?expected[j]:.625f))<.00001f,"all8samples plus XY orientation/stride");}
  f.seekg(static_cast<std::streamoff>(sizeof(h)+h.fields[14]));unsigned char b[4]{};f.read(reinterpret_cast<char*>(b),4);check(b[0]==255&&b[1]==0&&b[2]==255&&b[3]==255,"paired color orientation/format");
  check(h.fields[17]==1&&h.states[0][0]==257&&h.states[0][1]==8&&h.states[0][2]==7,"actual static depth state");
 }
 c->ClearState();std::cout<<"Depth snapshot GPU PASS: explicit feature10_1, legacy SM5 rejected HRESULT="<<static_cast<unsigned>(legacy)<<", three paired snapshots, 8sample values, state restoration and bounds\n";return 0;
 }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
