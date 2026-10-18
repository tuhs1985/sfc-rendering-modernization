// Default-off additive opaque-ship compositor. No scene-depth/UI qualification.
// Construct outside render callbacks. No waits, readback or file I/O in draw.
#pragma once
#include "ship_triplet_consumer.h"
#include <d3dcompiler.h>
#include <cstring>
namespace ship_triplet {
class Compositor {
 ComPtr<ID3D11DeviceContext> immediate,deferred;
 ComPtr<ID3D11VertexShader> vertex;
 ComPtr<ID3D11PixelShader> pixel;
 ComPtr<ID3D11Buffer> parameters;
 ComPtr<ID3D11RasterizerState> raster;
 ComPtr<ID3D11DepthStencilState> noDepth;
 ComPtr<ID3D11BlendState> opaque;
 struct Parameters {float origin[2],scale[2];uint32_t owner,width,height,pad;};
public:
 explicit Compositor(ID3D11Device* device){
  if(device->GetFeatureLevel()<D3D_FEATURE_LEVEL_10_1)throw std::runtime_error("compositor feature level");
  device->GetImmediateContext(&immediate);
  checked(device->CreateDeferredContext(0,&deferred),"compositor deferred");
  const char* vs="float4 main(uint i:SV_VertexID):SV_Position{float2 p[3]={float2(-1,-1),float2(-1,3),float2(3,-1)};return float4(p[i],0,1);}";
  const char* ps=R"(
Texture2D<float4> color:register(t0);
Texture2D<float> depth:register(t1);
Texture2D<float> picking:register(t2);
cbuffer Params:register(b0){float2 origin;float2 scale;uint owner;uint width;uint height;uint pad;};
float4 main(float4 p:SV_Position):SV_Target{
 int2 q=int2(floor((p.xy-origin)*scale));
 if(any(q<0)||q.x>=int(width)||q.y>=int(height))discard;
 if(asuint(picking.Load(int3(q,0)))!=owner)discard;
 float z=depth.Load(int3(q,0));if(!isfinite(z)||z<0||z>1)discard;
 return float4(color.Load(int3(q,0)).rgb,1);
})";
  ComPtr<ID3DBlob> vb,pb;
  checked(D3DCompile(vs,strlen(vs),nullptr,nullptr,nullptr,"main","vs_4_1",D3DCOMPILE_ENABLE_STRICTNESS,0,&vb,nullptr),"compositor VS compile");
  checked(D3DCompile(ps,strlen(ps),nullptr,nullptr,nullptr,"main","ps_4_1",D3DCOMPILE_ENABLE_STRICTNESS,0,&pb,nullptr),"compositor PS compile");
  checked(device->CreateVertexShader(vb->GetBufferPointer(),vb->GetBufferSize(),nullptr,&vertex),"compositor VS");
  checked(device->CreatePixelShader(pb->GetBufferPointer(),pb->GetBufferSize(),nullptr,&pixel),"compositor PS");
  D3D11_BUFFER_DESC b{};b.ByteWidth=sizeof(Parameters);b.BindFlags=D3D11_BIND_CONSTANT_BUFFER;
  checked(device->CreateBuffer(&b,nullptr,&parameters),"compositor parameters");
  D3D11_RASTERIZER_DESC r{};r.FillMode=D3D11_FILL_SOLID;r.CullMode=D3D11_CULL_NONE;r.DepthClipEnable=TRUE;
  checked(device->CreateRasterizerState(&r,&raster),"compositor raster");
  D3D11_DEPTH_STENCIL_DESC z{};checked(device->CreateDepthStencilState(&z,&noDepth),"compositor no depth");
  D3D11_BLEND_DESC blend{};blend.RenderTarget[0].RenderTargetWriteMask=D3D11_COLOR_WRITE_ENABLE_ALL;
  checked(device->CreateBlendState(&blend,&opaque),"compositor opaque");
 }
 bool draw(ID3D11RenderTargetView* target,ID3D11ShaderResourceView* const (&views)[3],
           const Key& key,const D3D11_VIEWPORT& viewport){
  if(!target||!views[0]||!views[1]||!views[2]||!validKey(key)||
     !std::isfinite(viewport.TopLeftX)||!std::isfinite(viewport.TopLeftY)||
     !std::isfinite(viewport.Width)||!std::isfinite(viewport.Height)||
     viewport.TopLeftX<0||viewport.TopLeftY<0||viewport.Width<1||viewport.Height<1||
     viewport.TopLeftX+viewport.Width>1920||viewport.TopLeftY+viewport.Height>1080)return false;
  // Ensure the caller did not request an out-of-target viewport. No allocation.
  ComPtr<ID3D11Resource> resource;target->GetResource(&resource);
  ComPtr<ID3D11Texture2D> texture;if(FAILED(resource.As(&texture)))return false;
  D3D11_TEXTURE2D_DESC desc{};texture->GetDesc(&desc);
  if(viewport.TopLeftX+viewport.Width>desc.Width||viewport.TopLeftY+viewport.Height>desc.Height)return false;
  Parameters p{{viewport.TopLeftX,viewport.TopLeftY},{key.width/viewport.Width,key.height/viewport.Height},key.objectId,key.width,key.height,0};
  deferred->ClearState();deferred->UpdateSubresource(parameters.Get(),0,nullptr,&p,0,0);
  auto* buffer=parameters.Get();deferred->PSSetConstantBuffers(0,1,&buffer);
  deferred->VSSetShader(vertex.Get(),nullptr,0);deferred->PSSetShader(pixel.Get(),nullptr,0);
  deferred->PSSetShaderResources(0,3,views);
  deferred->IASetInputLayout(nullptr);deferred->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);
  deferred->RSSetState(raster.Get());deferred->RSSetViewports(1,&viewport);
  deferred->OMSetRenderTargets(1,&target,nullptr);deferred->OMSetDepthStencilState(noDepth.Get(),0);
  deferred->OMSetBlendState(opaque.Get(),nullptr,0xffffffff);deferred->Draw(3,0);
  ComPtr<ID3D11CommandList> commands;
  if(FAILED(deferred->FinishCommandList(FALSE,&commands)))return false;
  // Restore ALL immediate-context state; no hand-written partial state backup.
  immediate->ExecuteCommandList(commands.Get(),TRUE);return true;
 }
};
}
