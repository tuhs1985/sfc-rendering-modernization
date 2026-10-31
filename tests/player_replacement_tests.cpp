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
#include "../tools/remix_runtime/ship_triplet_compositor.h"
#include "../tools/remix_runtime/replacement_presentation.h"
#include "../tools/d3d9_proof/input_admission.h"
#include "../tools/d3d9_proof/multi_scene_wire.h"
using Microsoft::WRL::ComPtr;
static unsigned checks=0;
static void test(bool b){++checks;if(!b)throw std::runtime_error("replacement check "+std::to_string(checks));}
static std::vector<BYTE> read(ID3D11Device* d,ID3D11DeviceContext* c,ID3D11Texture2D* t){
 D3D11_TEXTURE2D_DESC shape{};t->GetDesc(&shape);shape.Usage=D3D11_USAGE_STAGING;shape.BindFlags=shape.MiscFlags=0;shape.CPUAccessFlags=D3D11_CPU_ACCESS_READ;
 ComPtr<ID3D11Texture2D> copy;ship_triplet::checked(d->CreateTexture2D(&shape,nullptr,&copy),"test staging");c->CopyResource(copy.Get(),t);D3D11_MAPPED_SUBRESOURCE m{};
 ship_triplet::checked(c->Map(copy.Get(),0,D3D11_MAP_READ,0,&m),"test map");std::vector<BYTE> out(size_t(shape.Width)*shape.Height*4);
 for(unsigned y=0;y<shape.Height;++y)memcpy(out.data()+size_t(y)*shape.Width*4,static_cast<BYTE*>(m.pData)+size_t(y)*m.RowPitch,size_t(shape.Width)*4);c->Unmap(copy.Get(),0);return out;
}
int main(){try{
 static_assert(replacement::Offset>=synchronized_frame::Offset+sizeof(synchronized_frame::Store));
 static_assert(replacement::Offset+replacement::Bytes<=source_timing::Offset);
 auto store=std::make_unique<replacement::Store>();DWORD session[]{1,2,3,4};replacement::initialize(*store,session,42);
 test(replacement::valid(store.get(),session,42));test(!replacement::valid(store.get(),session,43));
 replacement::Control control{};control.mode=replacement::Active;control.generation=2;control.owner=3;control.revision=4;control.model=5;control.source=6;control.thread=7;control.epoch=1;control.permit=100;control.expires=1500;
 replacement::write(store->control,control);replacement::begin(*store,100,7);
 test(!replacement::suppress(*store,100,4,4,5,6,7,true,1000));
 test(!replacement::suppress(*store,100,3,5,5,6,7,true,1000));
 test(!replacement::suppress(*store,100,3,4,5,6,8,true,1000));
 test(!replacement::suppress(*store,100,3,4,5,6,7,true,1600));
 replacement::begin(*store,100,7); // Separate fresh-frame test after the rejected transactions above.
 test(replacement::suppress(*store,100,3,4,5,6,7,true,1000));
 test(replacement::suppress(*store,100,3,4,5,6,7,false,2000)); // Same-frame secondary retains decision even if its first-list lease has expired.
 replacement::Receipt receipt{};test(replacement::sample(*store,100,receipt));test(receipt.primary==1&&receipt.secondary==1);
 replacement::Binding binding{};binding.output=8;binding.sourceSequence=9;binding.stateHash=10;binding.frame=100;binding.generation=2;binding.owner=3;binding.revision=4;binding.epoch=1;
 test(replacement::bindingMatches(binding,receipt,8,9,10,1));
 for(unsigned field=0;field<4;++field){auto bad=binding;if(field==0)++bad.generation;if(field==1)++bad.owner;if(field==2)++bad.revision;if(field==3)++bad.epoch;test(!replacement::bindingMatches(bad,receipt,8,9,10,1));}
 replacement::invalidate(*store,100);replacement::sample(*store,100,receipt);test(!replacement::bindingMatches(binding,receipt,8,9,10,1));
 replacement::begin(*store,164,7);test(!replacement::sample(*store,100,receipt));
 replacement::Policy policy;test(!policy.miss());policy.completed();policy.mode=replacement::Active;
 test(policy.miss()&&policy.repeats==1&&policy.mode==replacement::Active);test(policy.miss()&&policy.repeats==2&&policy.mode==replacement::Recovering);
 policy.nativeRecovery();test(policy.mode==replacement::NativeFallback);policy.completed();test(policy.mode==replacement::NativeFallback);
 policy.nativeRecovery(true);test(policy.mode==replacement::LatchedOriginal);policy.completed();test(policy.mode==replacement::LatchedOriginal);
 ComPtr<ID3D11Device> device;ComPtr<ID3D11DeviceContext> context;
 ship_triplet::checked(D3D11CreateDevice(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,0,nullptr,0,D3D11_SDK_VERSION,&device,nullptr,&context),"device");
 D3D11_TEXTURE2D_DESC desc{};desc.Width=1920;desc.Height=1080;desc.MipLevels=desc.ArraySize=1;desc.Format=DXGI_FORMAT_B8G8R8A8_UNORM;desc.SampleDesc.Count=1;
 ComPtr<ID3D11Texture2D> back;ship_triplet::checked(device->CreateTexture2D(&desc,nullptr,&back),"back");replacement::Presentation tx(device.Get(),back.Get());
 desc.Format=DXGI_FORMAT_R32_FLOAT;desc.SampleDesc.Count=8;desc.BindFlags=D3D11_BIND_RENDER_TARGET|D3D11_BIND_SHADER_RESOURCE;
 ComPtr<ID3D11Texture2D> depth;ComPtr<ID3D11RenderTargetView> zTarget;ComPtr<ID3D11ShaderResourceView> zView;
 ship_triplet::checked(device->CreateTexture2D(&desc,nullptr,&depth),"depth");ship_triplet::checked(device->CreateRenderTargetView(depth.Get(),nullptr,&zTarget),"z target");ship_triplet::checked(device->CreateShaderResourceView(depth.Get(),nullptr,&zView),"z view");
 const float clear[]{.8f,0,0,0};context->ClearRenderTargetView(zTarget.Get(),clear);
 std::vector<BYTE> native(size_t(1920)*1080*4,31);native[0]=201;const size_t ship=(size_t(540)*1920+960)*4;native[ship]=240;
 auto absent=native;absent[ship]=31;auto finished=absent;finished[ship]=180;
 context->UpdateSubresource(back.Get(),0,nullptr,native.data(),1920*4,0);tx.native(back.Get(),100,1000);
 live_owner::Row row{};row[1]=3;row[2]=101;row[4]=1;row[5]=5;row[6]=6;row[7]=4;row[94]=1;
 context->UpdateSubresource(back.Get(),0,nullptr,absent.data(),1920*4,0);tx.history.captureAt(0,back.Get(),zView.Get(),row,1017,123);
 tx.show(back.Get());test(read(device.Get(),context.Get(),back.Get())==native); // Missing output never exposes hole.
 context->UpdateSubresource(tx.history.slot(0).color.Get(),0,nullptr,finished.data(),1920*4,0);
 tx.show(back.Get());test(read(device.Get(),context.Get(),back.Get())==native); // Staging is invisible before commit.
 tx.commit(0,1034);tx.show(back.Get());test(read(device.Get(),context.Get(),back.Get())==finished);
 tx.show(back.Get());test(read(device.Get(),context.Get(),back.Get())==finished); // No accumulated grading.
 test(!tx.history.slot(0).valid);test(tx.committedFrame==101);
 bool rejected=false;try{tx.commit(0,1050);}catch(const std::runtime_error&){rejected=true;}test(rejected);
 tx.native(back.Get(),102,1050);tx.policy.nativeRecovery();test(tx.policy.mode==replacement::NativeFallback);
 context->ClearState();context->Flush();ship_triplet::checked(device->GetDeviceRemovedReason(),"healthy");
 std::cout<<"Player replacement transaction PASS checks="<<checks<<" bits="<<sizeof(void*)*8<<" missing_output_hole_prevented=1 offscreen_commit=1 repeat_pixels_exact=1 ABI_layout=1\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}return 0;}
