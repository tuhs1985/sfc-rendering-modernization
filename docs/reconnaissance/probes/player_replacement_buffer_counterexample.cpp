// Test the existing GPU history implementation, not a replacement compositor.
// No SFC/Remix launch. Synthetic ship/HUD pixels isolate the missing-output case.
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <d3d11.h>
#include <wrl/client.h>
#include <array>
#include <cmath>
#include <iostream>
#include <stdexcept>
#include <vector>
#include "../../../tools/remix_runtime/ship_triplet_compositor.h"
#include "../../../tools/remix_runtime/scene_frame_buffer.h"
using Microsoft::WRL::ComPtr;
static unsigned checks=0;
static void test(bool b){++checks;if(!b)throw std::runtime_error("buffer counterexample assertion");}
static std::vector<BYTE> read(ID3D11Device* d,ID3D11DeviceContext* c,ID3D11Texture2D* t){
 D3D11_TEXTURE2D_DESC desc{};t->GetDesc(&desc);desc.Usage=D3D11_USAGE_STAGING;
 desc.BindFlags=desc.MiscFlags=0;desc.CPUAccessFlags=D3D11_CPU_ACCESS_READ;
 ComPtr<ID3D11Texture2D> staging;ship_triplet::checked(d->CreateTexture2D(&desc,nullptr,&staging),"staging");
 c->CopyResource(staging.Get(),t);D3D11_MAPPED_SUBRESOURCE map{};
 ship_triplet::checked(c->Map(staging.Get(),0,D3D11_MAP_READ,0,&map),"map");
 std::vector<BYTE> out(size_t(desc.Width)*desc.Height*4);
 for(unsigned y=0;y<desc.Height;++y)memcpy(out.data()+size_t(y)*desc.Width*4,static_cast<BYTE*>(map.pData)+size_t(y)*map.RowPitch,size_t(desc.Width)*4);
 c->Unmap(staging.Get(),0);return out;
}
int main(){try{
 ComPtr<ID3D11Device> d;ComPtr<ID3D11DeviceContext> c;
 ship_triplet::checked(D3D11CreateDevice(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,0,nullptr,0,D3D11_SDK_VERSION,&d,nullptr,&c),"device");
 D3D11_TEXTURE2D_DESC desc{};desc.Width=1920;desc.Height=1080;desc.MipLevels=desc.ArraySize=1;
 desc.Format=DXGI_FORMAT_B8G8R8A8_UNORM;desc.SampleDesc.Count=1;
 ComPtr<ID3D11Texture2D> back;ship_triplet::checked(d->CreateTexture2D(&desc,nullptr,&back),"back");
 scene_frame_buffer::History history(d.Get(),back.Get());
 desc.Format=DXGI_FORMAT_R32_FLOAT;desc.SampleDesc.Count=8;desc.BindFlags=D3D11_BIND_RENDER_TARGET|D3D11_BIND_SHADER_RESOURCE;
 ComPtr<ID3D11Texture2D> depth;ComPtr<ID3D11RenderTargetView> depthTarget;ComPtr<ID3D11ShaderResourceView> depthView;
 ship_triplet::checked(d->CreateTexture2D(&desc,nullptr,&depth),"depth");
 ship_triplet::checked(d->CreateRenderTargetView(depth.Get(),nullptr,&depthTarget),"depth target");
 ship_triplet::checked(d->CreateShaderResourceView(depth.Get(),nullptr,&depthView),"depth view");
 const float clear[]{.8f,0,0,0};c->ClearRenderTargetView(depthTarget.Get(),clear);
 live_owner::Row a{};a[1]=2;a[2]=100;a[4]=1;a[5]=9;a[6]=10;a[7]=3;a[94]=1;
 auto b=a;b[2]++;b[94]++;
 test(synchronized_frame::adjacent(a,b,1000,1017,1000));
 std::vector<BYTE> original(size_t(1920)*1080*4,31);original[0]=201;
 const size_t ship=(size_t(540)*1920+960)*4;original[ship]=240;
 auto suppressed=original;suppressed[ship]=31;
 auto current=original;current[0]=99;current[ship]=120;
 // Actual additive behavior: restore the previous source even if no output is ready.
 c->UpdateSubresource(back.Get(),0,nullptr,original.data(),1920*4,0);
 history.capture(back.Get(),depthView.Get(),a,1000);auto* prior=history.prior();test(prior!=nullptr);
 c->UpdateSubresource(back.Get(),0,nullptr,current.data(),1920*4,0);
 history.capture(back.Get(),depthView.Get(),b,1017);history.restore(back.Get(),*prior);
 auto additive=read(d.Get(),c.Get(),back.Get());test(additive==original);test(additive[ship]==240);
 history.reset();
 c->UpdateSubresource(back.Get(),0,nullptr,suppressed.data(),1920*4,0);
 history.capture(back.Get(),depthView.Get(),a,1000);prior=history.prior();test(prior!=nullptr);
 c->UpdateSubresource(back.Get(),0,nullptr,current.data(),1920*4,0);
 history.capture(back.Get(),depthView.Get(),b,1017);history.restore(back.Get(),*prior);
 // No matching Remix output: current receiver's loop simply reaches its audit tail.
 auto missing=read(d.Get(),c.Get(),back.Get());test(missing==suppressed);test(missing[ship]!=240);
 test(missing[0]==201);test(prior->row==a);test(prior->stateHash==live_owner::row_hash(a));
 c->ClearState();c->Flush();ship_triplet::checked(d->GetDeviceRemovedReason(),"healthy");
 std::cout<<"Replacement buffer counterexample REPRODUCED checks="<<checks
 <<" additive_missing_output_original_present=1 suppressed_missing_output_ship_absent=1 HUD_frame_identity_preserved=1"
 <<" implementation=existing_History synthetic_pixels=1 replacement_gate=BLOCKED not_gameplay=1\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}return 0;}
