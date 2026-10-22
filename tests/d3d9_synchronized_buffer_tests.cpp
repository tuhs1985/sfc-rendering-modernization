#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <d3d11.h>
#include <wrl/client.h>
#include <array>
#include <cmath>
#include <stdexcept>
#include <iostream>
#include <vector>
#include <thread>
#include "../tools/remix_runtime/ship_triplet_compositor.h"
#include "../tools/remix_runtime/scene_frame_buffer.h"
#include "../tools/remix_runtime/game_gpu_read_lease.h"
using Microsoft::WRL::ComPtr;
static std::vector<BYTE> read(ID3D11Device* d,ID3D11DeviceContext* c,ID3D11Texture2D* t){
 D3D11_TEXTURE2D_DESC shape{};t->GetDesc(&shape);shape.Usage=D3D11_USAGE_STAGING;shape.BindFlags=shape.MiscFlags=0;shape.CPUAccessFlags=D3D11_CPU_ACCESS_READ;
 ComPtr<ID3D11Texture2D> copy;ship_triplet::checked(d->CreateTexture2D(&shape,nullptr,&copy),"test staging");c->CopyResource(copy.Get(),t);D3D11_MAPPED_SUBRESOURCE m{};
 ship_triplet::checked(c->Map(copy.Get(),0,D3D11_MAP_READ,0,&m),"test map");std::vector<BYTE> out(size_t(shape.Width)*shape.Height*4);
 for(unsigned y=0;y<shape.Height;++y)memcpy(out.data()+size_t(y)*shape.Width*4,static_cast<BYTE*>(m.pData)+size_t(y)*m.RowPitch,size_t(shape.Width)*4);c->Unmap(copy.Get(),0);return out;
}
int main(){try{unsigned n=0;auto test=[&](bool b){++n;if(!b)throw std::runtime_error("synchronized buffer check");};
 live_owner::Row a{};a[1]=2;a[2]=100;a[4]=1;a[5]=9;a[6]=10;a[7]=3;a[94]=1;auto b=a;b[2]++;b[94]++;
 test(synchronized_frame::adjacent(a,b,1000,1017,1000));b[49]=123;test(synchronized_frame::adjacent(a,b,1000,1017,1000)); // Camera may change;whole scene delayed.
 for(unsigned field:{1u,5u,6u,7u}){auto bad=b;++bad[field];test(!synchronized_frame::adjacent(a,bad,1000,1017,1000));}
 auto bad=b;bad[4]=2;test(!synchronized_frame::adjacent(a,bad,1000,1017,1000));bad=b;++bad[2];test(!synchronized_frame::adjacent(a,bad,1000,1017,1000));
 test(!synchronized_frame::adjacent(a,b,1000,1051,1000));test(!synchronized_frame::adjacent(a,b,1000,999,1000));test(!synchronized_frame::adjacent(a,b,1000,1017,0));
 auto store=std::make_unique<synchronized_frame::Store>();synchronized_frame::Audit event{};event.current=101;event.scene=100;event.status=2;
 for(unsigned i=0;i<synchronized_frame::Capacity+2;++i)synchronized_frame::append(*store,event);test(store->header.count==synchronized_frame::Capacity&&store->header.dropped==2);
 ComPtr<ID3D11Device> d;ComPtr<ID3D11DeviceContext> c;ship_triplet::checked(D3D11CreateDevice(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,0,nullptr,0,D3D11_SDK_VERSION,&d,nullptr,&c),"actual GPU");
 D3D11_TEXTURE2D_DESC desc{};desc.Width=1920;desc.Height=1080;desc.MipLevels=desc.ArraySize=desc.SampleDesc.Count=1;desc.Format=DXGI_FORMAT_B8G8R8A8_UNORM;desc.BindFlags=D3D11_BIND_RENDER_TARGET;
 ComPtr<ID3D11Texture2D> back;ship_triplet::checked(d->CreateTexture2D(&desc,nullptr,&back),"back");scene_frame_buffer::History history(d.Get(),back.Get());test(!history.prior());
 desc.Format=DXGI_FORMAT_R32_FLOAT;desc.SampleDesc.Count=8;desc.BindFlags=D3D11_BIND_RENDER_TARGET|D3D11_BIND_SHADER_RESOURCE;ComPtr<ID3D11Texture2D> depth;ComPtr<ID3D11RenderTargetView> rt;ComPtr<ID3D11ShaderResourceView> view;
 ship_triplet::checked(d->CreateTexture2D(&desc,nullptr,&depth),"MS source");ship_triplet::checked(d->CreateRenderTargetView(depth.Get(),nullptr,&rt),"MS target");ship_triplet::checked(d->CreateShaderResourceView(depth.Get(),nullptr,&view),"MS view");
 const char* vs="float4 main(uint i:SV_VertexID):SV_Position{float2 p[3]={float2(-1,-1),float2(-1,3),float2(3,-1)};return float4(p[i],0,1);}";
 const char* ps="float main(float4 p:SV_Position,uint s:SV_SampleIndex):SV_Target{if(p.x<1&&s==6)return asfloat(0x7fc00000u);if(p.x>=1&&p.x<2&&s==3)return -1;if(p.x>=2&&p.x<3&&s==2)return 2;if(p.x>=3&&p.x<4&&s==0)return asfloat(0x7f800000u);return .1+.1*s;}";
 ComPtr<ID3DBlob> vb,pb;ship_triplet::checked(D3DCompile(vs,strlen(vs),nullptr,nullptr,nullptr,"main","vs_4_1",0,0,&vb,nullptr),"test VS");ship_triplet::checked(D3DCompile(ps,strlen(ps),nullptr,nullptr,nullptr,"main","ps_4_1",0,0,&pb,nullptr),"test PS");
 ComPtr<ID3D11VertexShader> vertex;ComPtr<ID3D11PixelShader> pixel;ship_triplet::checked(d->CreateVertexShader(vb->GetBufferPointer(),vb->GetBufferSize(),nullptr,&vertex),"VS");ship_triplet::checked(d->CreatePixelShader(pb->GetBufferPointer(),pb->GetBufferSize(),nullptr,&pixel),"PS");
 auto* r=rt.Get();c->OMSetRenderTargets(1,&r,nullptr);c->VSSetShader(vertex.Get(),nullptr,0);c->PSSetShader(pixel.Get(),nullptr,0);c->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);D3D11_VIEWPORT viewport{0,0,1920,1080,0,1};c->RSSetViewports(1,&viewport);c->Draw(3,0);
 std::vector<BYTE> first(size_t(1920)*1080*4,27),second(first.size(),81);first[0]=199;first[first.size()-1]=93; // Native HUD/scene corner markers.
 c->UpdateSubresource(back.Get(),0,nullptr,first.data(),1920*4,0);history.capture(back.Get(),view.Get(),a,1000);auto* previous=history.prior();test(previous&&previous->row==a);
 ComPtr<ID3D11RenderTargetView> restored;c->OMGetRenderTargets(1,&restored,nullptr);test(restored.Get()==rt.Get());ComPtr<ID3D11PixelShader> restoredPS;c->PSGetShader(&restoredPS,nullptr,nullptr);test(restoredPS.Get()==pixel.Get());
 c->UpdateSubresource(back.Get(),0,nullptr,second.data(),1920*4,0);history.capture(back.Get(),view.Get(),b,1017);history.restore(back.Get(),*previous);test(read(d.Get(),c.Get(),back.Get())==first);test(previous->row==a&&previous->captured==1000);
 auto raw=read(d.Get(),c.Get(),previous->depth.Get());bool minGood=true;for(size_t i=0;i<raw.size()/4;++i){float x=0;memcpy(&x,raw.data()+i*4,4);if(i%1920<4?!std::isnan(x):fabs(x-.1f)>1e-6){minGood=false;break;}}test(minGood);
 auto* next=history.prior();test(next&&next->row==b);history.restore(back.Get(),*next);test(read(d.Get(),c.Get(),back.Get())==second);history.reset();test(!history.prior());
 // Resolved-depth compositor must compile independently of the unchanged MS8 path.
 ship_triplet::Compositor resolved(d.Get(),true,true,true);ship_triplet::Compositor legacy(d.Get(),true,true,false);test(true);
 game_gpu::ReadLease lease;lease.prepare(d.Get());ComPtr<ID3D11DeviceContext4> fenceContext;ship_triplet::checked(c.As(&fenceContext),"test fence context");
 test(!lease.pending());test(!lease.retire());
 for(unsigned cycle=0;cycle<2;++cycle){
  c->CopyResource(back.Get(),previous->color.Get());lease.signal(fenceContext.Get());test(lease.pending());
  bool duplicateRejected=false;try{lease.signal(fenceContext.Get());}catch(const std::runtime_error&){duplicateRejected=true;}test(duplicateRejected);
  c->Flush();bool retired=false;std::thread worker([&]{const auto end=GetTickCount64()+5000;while(GetTickCount64()<end){if(lease.retire()){retired=true;break;}Sleep(1);}});worker.join();
  test(retired);test(!lease.pending());
 }
 c->ClearState();c->Flush();ship_triplet::checked(d->GetDeviceRemovedReason(),"healthy");
 std::cout<<"Synchronized buffer PASS "<<n<<" checks color_HUD_depth_identity_age_state=1 size=1920x1080 pointer_bits="<<sizeof(void*)*8<<'\n';
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}return 0;}
