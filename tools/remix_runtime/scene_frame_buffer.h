// Same-game-context GPU history,preallocated before activation. Captures the
// complete pre-ReShade backbuffer (including native HUD) plus conservative depth.
// No waits/readback/IO. Two slots retain ONE prior frame while capturing current.
#pragma once
#include "../d3d9_proof/synchronized_frame.h"
namespace scene_frame_buffer {
using Microsoft::WRL::ComPtr;
struct Frame {ComPtr<ID3D11Texture2D> color,depth;ComPtr<ID3D11RenderTargetView> depthTarget;ComPtr<ID3D11ShaderResourceView> depthView;
 live_owner::Row row{};uint64_t captured=0;bool valid=false;};
class History {
 ComPtr<ID3D11DeviceContext> context,deferred;ComPtr<ID3D11VertexShader> vertex;ComPtr<ID3D11PixelShader> pixel;
 Frame frames[2];unsigned next=0;D3D11_TEXTURE2D_DESC descriptor{};
public:
 History(ID3D11Device* device,ID3D11Texture2D* target){
  target->GetDesc(&descriptor);if(descriptor.Width!=1920||descriptor.Height!=1080||descriptor.SampleDesc.Count!=1||descriptor.MipLevels!=1||descriptor.ArraySize!=1||
    (descriptor.Format!=DXGI_FORMAT_B8G8R8A8_UNORM&&descriptor.Format!=DXGI_FORMAT_R8G8B8A8_UNORM))throw std::runtime_error("Buffered scene target unsupported");
  // Existing3source+6pool+1grade+4historytextures remain below128MiB.
  if(uint64_t(descriptor.Width)*descriptor.Height*4*14>128ull*1024*1024)throw std::runtime_error("Buffered output resource128MiB cap");
  device->GetImmediateContext(&context);ship_triplet::checked(device->CreateDeferredContext(0,&deferred),"buffer deferred");
  auto d=descriptor;d.Usage=D3D11_USAGE_DEFAULT;d.CPUAccessFlags=d.MiscFlags=d.BindFlags=0;
  for(auto& f:frames){ship_triplet::checked(device->CreateTexture2D(&d,nullptr,&f.color),"buffer color");auto z=d;z.Format=DXGI_FORMAT_R32_FLOAT;z.BindFlags=D3D11_BIND_RENDER_TARGET|D3D11_BIND_SHADER_RESOURCE;
   ship_triplet::checked(device->CreateTexture2D(&z,nullptr,&f.depth),"buffer depth");ship_triplet::checked(device->CreateRenderTargetView(f.depth.Get(),nullptr,&f.depthTarget),"buffer depth target");ship_triplet::checked(device->CreateShaderResourceView(f.depth.Get(),nullptr,&f.depthView),"buffer depth view");}
  const char* vs="float4 main(uint i:SV_VertexID):SV_Position{float2 p[3]={float2(-1,-1),float2(-1,3),float2(3,-1)};return float4(p[i],0,1);}";
  const char* ps="Texture2DMS<float,8> source:register(t0);float main(float4 p:SV_Position):SV_Target{float closest=1;[unroll]for(int s=0;s<8;++s){float d=source.Load(int2(p.xy),s);if(!isfinite(d)||d<0||d>1)return asfloat(0x7fc00000u);closest=min(closest,d);}return closest;}";
  ComPtr<ID3DBlob> a,b;ship_triplet::checked(D3DCompile(vs,strlen(vs),nullptr,nullptr,nullptr,"main","vs_4_1",D3DCOMPILE_ENABLE_STRICTNESS,0,&a,nullptr),"buffer VS compile");ship_triplet::checked(D3DCompile(ps,strlen(ps),nullptr,nullptr,nullptr,"main","ps_4_1",D3DCOMPILE_ENABLE_STRICTNESS,0,&b,nullptr),"buffer depth compile");
  ship_triplet::checked(device->CreateVertexShader(a->GetBufferPointer(),a->GetBufferSize(),nullptr,&vertex),"buffer VS");ship_triplet::checked(device->CreatePixelShader(b->GetBufferPointer(),b->GetBufferSize(),nullptr,&pixel),"buffer PS");
 }
 void reset(){for(auto& f:frames)f.valid=false;next=0;}
 Frame* prior(){auto& p=frames[next^1];return p.valid?&p:nullptr;}
 void capture(ID3D11Texture2D* target,ID3D11ShaderResourceView* depth,const live_owner::Row& row,uint64_t now){
  if(!target||!depth||!row[2])throw std::runtime_error("Buffered scene inputs missing");
  D3D11_SHADER_RESOURCE_VIEW_DESC view{};depth->GetDesc(&view);ComPtr<ID3D11Resource> resource;depth->GetResource(&resource);ComPtr<ID3D11Texture2D> source;
  ship_triplet::checked(resource.As(&source),"Buffered depth resource");D3D11_TEXTURE2D_DESC sourceDesc{};source->GetDesc(&sourceDesc);
  if(view.ViewDimension!=D3D11_SRV_DIMENSION_TEXTURE2DMS||view.Format!=DXGI_FORMAT_R32_FLOAT||sourceDesc.Width!=1920||sourceDesc.Height!=1080||sourceDesc.SampleDesc.Count!=8||sourceDesc.SampleDesc.Quality)throw std::runtime_error("Buffered depth shape");
  D3D11_TEXTURE2D_DESC d{};target->GetDesc(&d);if(d.Width!=descriptor.Width||d.Height!=descriptor.Height||d.Format!=descriptor.Format||d.SampleDesc.Count!=1)throw std::runtime_error("Buffered scene target changed");
  auto& f=frames[next];deferred->ClearState();deferred->CopyResource(f.color.Get(),target);
  auto* r=f.depthTarget.Get();deferred->OMSetRenderTargets(1,&r,nullptr);deferred->VSSetShader(vertex.Get(),nullptr,0);deferred->PSSetShader(pixel.Get(),nullptr,0);deferred->PSSetShaderResources(0,1,&depth);
  deferred->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);D3D11_VIEWPORT v{0,0,float(d.Width),float(d.Height),0,1};deferred->RSSetViewports(1,&v);deferred->Draw(3,0);
  ComPtr<ID3D11CommandList> commands;ship_triplet::checked(deferred->FinishCommandList(FALSE,&commands),"buffer capture commands");context->ExecuteCommandList(commands.Get(),TRUE);
  f.row=row;f.captured=now;f.valid=true;next^=1;
 }
 void restore(ID3D11Texture2D* target,Frame& f){context->CopyResource(target,f.color.Get());}
};
}
