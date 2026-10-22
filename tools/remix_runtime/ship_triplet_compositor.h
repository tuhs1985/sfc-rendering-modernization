// Default-off additive opaque-ship compositor. No scene-depth/UI qualification.
// Construct outside render callbacks. No waits, readback or file I/O in draw.
#pragma once
#include "ship_triplet_consumer.h"
#include <d3dcompiler.h>
#include <cstring>
#include "native_viewport_mapping.h"
namespace ship_triplet {
class Compositor {
 ComPtr<ID3D11DeviceContext> immediate,deferred;
 ComPtr<ID3D11VertexShader> vertex;
 ComPtr<ID3D11PixelShader> pixel;
 const bool sceneDepth,nativeScreen;
 ComPtr<ID3D11Buffer> parameters;
 ComPtr<ID3D11RasterizerState> raster;
 ComPtr<ID3D11DepthStencilState> noDepth;
 ComPtr<ID3D11BlendState> opaque;
 struct Parameters {float origin[2],scale[2];uint32_t owner,width,height,pad;float nativeMap[4];};
public:
 explicit Compositor(ID3D11Device* device,bool useSceneDepth=false,bool nativeScreenOutput=false):sceneDepth(useSceneDepth),nativeScreen(nativeScreenOutput){
  if(device->GetFeatureLevel()<D3D_FEATURE_LEVEL_10_1)throw std::runtime_error("compositor feature level");
  device->GetImmediateContext(&immediate);
  checked(device->CreateDeferredContext(0,&deferred),"compositor deferred");
  const char* vs="float4 main(uint i:SV_VertexID):SV_Position{float2 p[3]={float2(-1,-1),float2(-1,3),float2(3,-1)};return float4(p[i],0,1);}";
  const char* ps=R"(
Texture2D<float4> color:register(t0);
Texture2D<float> depth:register(t1);
Texture2D<float> picking:register(t2);
#ifdef SCENE_DEPTH
Texture2DMS<float,8> scene:register(t3);
#endif
cbuffer Params:register(b0){float2 origin;float2 scale;uint owner;uint width;uint height;uint pad;float4 nativeMap;};
float4 main(float4 p:SV_Position):SV_Target{
 int2 q=int2(floor((p.xy-origin)*scale));
 if(any(q<0)||q.x>=int(width)||q.y>=int(height))discard;
 if(asuint(picking.Load(int3(q,0)))!=owner)discard;
 float z=depth.Load(int3(q,0));if(!isfinite(z)||z<0||z>1)discard;
#ifdef SCENE_DEPTH
 int2 n=int2(floor(nativeMap.xy+(float2(q)+.5)*nativeMap.zw));
 float closest=1;
 [unroll]for(int s=0;s<8;++s){float d=scene.Load(n,s);if(!isfinite(d)||d<0||d>1)discard;closest=min(closest,d);}
 if(z>closest)discard;
#endif
 return float4(color.Load(int3(q,0)).rgb,1);
})";
  ComPtr<ID3DBlob> vb,pb;
  const D3D_SHADER_MACRO definitions[]={{"SCENE_DEPTH","1"},{nullptr,nullptr}};
  checked(D3DCompile(vs,strlen(vs),nullptr,nullptr,nullptr,"main","vs_4_1",D3DCOMPILE_ENABLE_STRICTNESS,0,&vb,nullptr),"compositor VS compile");
  checked(D3DCompile(ps,strlen(ps),nullptr,sceneDepth?definitions:nullptr,nullptr,"main","ps_4_1",D3DCOMPILE_ENABLE_STRICTNESS,0,&pb,nullptr),"compositor PS compile");
  checked(device->CreateVertexShader(vb->GetBufferPointer(),vb->GetBufferSize(),nullptr,&vertex),"compositor VS");
  checked(device->CreatePixelShader(pb->GetBufferPointer(),pb->GetBufferSize(),nullptr,&pixel),"compositor PS");
  D3D11_BUFFER_DESC b{};b.ByteWidth=sizeof(Parameters);b.BindFlags=D3D11_BIND_CONSTANT_BUFFER;
  checked(device->CreateBuffer(&b,nullptr,&parameters),"compositor parameters");
  D3D11_RASTERIZER_DESC r{};r.FillMode=D3D11_FILL_SOLID;r.CullMode=D3D11_CULL_NONE;r.DepthClipEnable=TRUE;r.ScissorEnable=nativeScreen;
  checked(device->CreateRasterizerState(&r,&raster),"compositor raster");
  D3D11_DEPTH_STENCIL_DESC z{};checked(device->CreateDepthStencilState(&z,&noDepth),"compositor no depth");
  D3D11_BLEND_DESC blend{};blend.RenderTarget[0].RenderTargetWriteMask=D3D11_COLOR_WRITE_ENABLE_ALL;
  checked(device->CreateBlendState(&blend,&opaque),"compositor opaque");
 }
 bool draw(ID3D11RenderTargetView* target,ID3D11ShaderResourceView* const (&views)[3],
           const Key& key,const D3D11_VIEWPORT& viewport,ID3D11ShaderResourceView* nativeDepth=nullptr){
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
  if(sceneDepth){
   if(!nativeDepth)return false;ComPtr<ID3D11Resource> r;nativeDepth->GetResource(&r);
   ComPtr<ID3D11Texture2D> t;if(FAILED(r.As(&t)))return false;D3D11_TEXTURE2D_DESC n{};t->GetDesc(&n);
   D3D11_SHADER_RESOURCE_VIEW_DESC s{};nativeDepth->GetDesc(&s);
   ComPtr<ID3D11Device> a,b;target->GetDevice(&a);nativeDepth->GetDevice(&b);
   if(a.Get()!=b.Get()||s.ViewDimension!=D3D11_SRV_DIMENSION_TEXTURE2DMS||s.Format!=DXGI_FORMAT_R32_FLOAT||
      n.Format!=DXGI_FORMAT_R32_TYPELESS||n.SampleDesc.Count!=8||n.SampleDesc.Quality||n.ArraySize!=1||n.MipLevels!=1||
      uint64_t(key.viewport[0])+key.viewport[2]>n.Width||uint64_t(key.viewport[1])+key.viewport[3]>n.Height)return false;
  }else if(nativeDepth)return false;
  Parameters p{{viewport.TopLeftX,viewport.TopLeftY},{key.width/viewport.Width,key.height/viewport.Height},key.objectId,key.width,key.height,0,
      {static_cast<float>(key.viewport[0]),static_cast<float>(key.viewport[1]),static_cast<float>(key.viewport[2])/key.width,static_cast<float>(key.viewport[3])/key.height}};
  if(nativeScreen){native_viewport::Mapping map{};if(!native_viewport::mapping(key.width,key.height,key.viewport,map))return false;
   memcpy(p.origin,map.origin,sizeof(p.origin));memcpy(p.scale,map.scale,sizeof(p.scale));}
  deferred->ClearState();deferred->UpdateSubresource(parameters.Get(),0,nullptr,&p,0,0);
  auto* buffer=parameters.Get();deferred->PSSetConstantBuffers(0,1,&buffer);
  deferred->VSSetShader(vertex.Get(),nullptr,0);deferred->PSSetShader(pixel.Get(),nullptr,0);
  deferred->PSSetShaderResources(0,3,views);
  if(sceneDepth)deferred->PSSetShaderResources(3,1,&nativeDepth);
  deferred->IASetInputLayout(nullptr);deferred->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);
  deferred->RSSetState(raster.Get());deferred->RSSetViewports(1,&viewport);
  if(nativeScreen){const D3D11_RECT rect{static_cast<LONG>(key.viewport[0]),static_cast<LONG>(key.viewport[1]),static_cast<LONG>(key.viewport[0]+key.viewport[2]),static_cast<LONG>(key.viewport[1]+key.viewport[3])};deferred->RSSetScissorRects(1,&rect);}
  deferred->OMSetRenderTargets(1,&target,nullptr);deferred->OMSetDepthStencilState(noDepth.Get(),0);
  deferred->OMSetBlendState(opaque.Get(),nullptr,0xffffffff);deferred->Draw(3,0);
  ComPtr<ID3D11CommandList> commands;
  if(FAILED(deferred->FinishCommandList(FALSE,&commands)))return false;
  // Restore ALL immediate-context state; no hand-written partial state backup.
  immediate->ExecuteCommandList(commands.Get(),TRUE);return true;
 }
};
}
