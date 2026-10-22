// Offline-qualified building block ONLY;not installed into SFC by this header.
// Composite at a qualified pre-UI boundary,writing returned normalized depth.
#pragma once
#include "ship_triplet_compositor.h"
namespace ship_replacement {
using Microsoft::WRL::ComPtr;
class DepthCompositor {
 ComPtr<ID3D11Device> ownerDevice;
 ComPtr<ID3D11DeviceContext> immediate,deferred;
 ComPtr<ID3D11VertexShader> vertex;ComPtr<ID3D11PixelShader> pixel;
 ComPtr<ID3D11DepthStencilState> depthState;ComPtr<ID3D11RasterizerState> raster;
 ComPtr<ID3D11BlendState> blend;ComPtr<ID3D11Buffer> parameters;
 struct Parameters{uint32_t owner,width,height,pad;float viewportMap[4];};
public:
 explicit DepthCompositor(ID3D11Device* device):ownerDevice(device){
  using ship_triplet::checked;
  if(device->GetFeatureLevel()<D3D_FEATURE_LEVEL_10_1)throw std::runtime_error("replacement feature level");
  device->GetImmediateContext(&immediate);checked(device->CreateDeferredContext(0,&deferred),"replacement context");
  const char* vs="float4 main(uint i:SV_VertexID):SV_Position{float2 p[3]={float2(-1,-1),float2(-1,3),float2(3,-1)};return float4(p[i],0,1);}";
  const char* ps=R"(
Texture2D<float4> color:register(t0);Texture2D<float> depth:register(t1);
Texture2D<float> picking:register(t2);
cbuffer Params:register(b0){uint owner;uint width;uint height;uint pad;float4 viewportMap;};
struct Output{float4 color:SV_Target;float depth:SV_Depth;};
Output main(float4 p:SV_Position){
 int2 q=int2(floor((p.xy-viewportMap.xy)*viewportMap.zw));if(any(q<0)||q.x>=int(width)||q.y>=int(height))discard;
 if(asuint(picking.Load(int3(q,0)))!=owner)discard;
 float z=depth.Load(int3(q,0));float4 c=color.Load(int3(q,0));
 if(!isfinite(z)||z<0||z>1||!all(isfinite(c)))discard;
 Output o;o.color=float4(c.rgb,1);o.depth=z;return o;
})";
  ComPtr<ID3DBlob> v,p;
  checked(D3DCompile(vs,strlen(vs),nullptr,nullptr,nullptr,"main","vs_4_1",D3DCOMPILE_ENABLE_STRICTNESS,0,&v,nullptr),"replacement VS compile");
  checked(D3DCompile(ps,strlen(ps),nullptr,nullptr,nullptr,"main","ps_4_1",D3DCOMPILE_ENABLE_STRICTNESS,0,&p,nullptr),"replacement PS compile");
  checked(device->CreateVertexShader(v->GetBufferPointer(),v->GetBufferSize(),nullptr,&vertex),"replacement VS");
  checked(device->CreatePixelShader(p->GetBufferPointer(),p->GetBufferSize(),nullptr,&pixel),"replacement PS");
  D3D11_DEPTH_STENCIL_DESC z{};z.DepthEnable=TRUE;z.DepthWriteMask=D3D11_DEPTH_WRITE_MASK_ALL;z.DepthFunc=D3D11_COMPARISON_LESS_EQUAL;
  checked(device->CreateDepthStencilState(&z,&depthState),"replacement depth state");
  D3D11_RASTERIZER_DESC r{};r.FillMode=D3D11_FILL_SOLID;r.CullMode=D3D11_CULL_NONE;r.DepthClipEnable=TRUE;r.MultisampleEnable=TRUE;
  checked(device->CreateRasterizerState(&r,&raster),"replacement raster");
  D3D11_BLEND_DESC b{};b.RenderTarget[0].RenderTargetWriteMask=D3D11_COLOR_WRITE_ENABLE_ALL;
  checked(device->CreateBlendState(&b,&blend),"replacement blend");
  D3D11_BUFFER_DESC cb{};cb.ByteWidth=sizeof(Parameters);cb.BindFlags=D3D11_BIND_CONSTANT_BUFFER;
  checked(device->CreateBuffer(&cb,nullptr,&parameters),"replacement parameters");
 }
 bool draw(ID3D11RenderTargetView* target,ID3D11DepthStencilView* nativeDepth,
           ID3D11ShaderResourceView* const (&views)[3],const ship_triplet::Key& key){
  // Full-resolution 1:1 inputs only. No nearest-rescale/misregistered depth.
  if(!target||!nativeDepth||!views[0]||!views[1]||!views[2]||!ship_triplet::validKey(key)||key.diagnosticMode)return false;
  ComPtr<ID3D11Device> td,zd;target->GetDevice(&td);nativeDepth->GetDevice(&zd);
  if(td.Get()!=ownerDevice.Get()||zd.Get()!=ownerDevice.Get())return false;
  ComPtr<ID3D11Resource> cr,zr;target->GetResource(&cr);nativeDepth->GetResource(&zr);
  ComPtr<ID3D11Texture2D> ct,zt;if(FAILED(cr.As(&ct))||FAILED(zr.As(&zt)))return false;
  D3D11_TEXTURE2D_DESC c{},z{};ct->GetDesc(&c);zt->GetDesc(&z);
  D3D11_RENDER_TARGET_VIEW_DESC rv{};target->GetDesc(&rv);D3D11_DEPTH_STENCIL_VIEW_DESC dv{};nativeDepth->GetDesc(&dv);
  if(c.Width!=key.width||c.Height!=key.height||c.Width!=z.Width||c.Height!=z.Height||
     uint64_t(key.viewport[0])+key.viewport[2]>c.Width||uint64_t(key.viewport[1])+key.viewport[3]>c.Height||
     c.ArraySize!=1||c.MipLevels!=1||z.ArraySize!=1||z.MipLevels!=1||
     c.SampleDesc.Count!=8||c.SampleDesc.Quality!=0||z.SampleDesc.Count!=8||z.SampleDesc.Quality!=0||
     c.Format!=DXGI_FORMAT_B8G8R8A8_UNORM||z.Format!=DXGI_FORMAT_R32_TYPELESS||
     rv.ViewDimension!=D3D11_RTV_DIMENSION_TEXTURE2DMS||rv.Format!=c.Format||
     dv.ViewDimension!=D3D11_DSV_DIMENSION_TEXTURE2DMS||dv.Format!=DXGI_FORMAT_D32_FLOAT||dv.Flags)return false;
  for(unsigned i=0;i<3;++i){
   ComPtr<ID3D11Device> vd;views[i]->GetDevice(&vd);if(vd.Get()!=ownerDevice.Get())return false;
   ComPtr<ID3D11Resource> r;views[i]->GetResource(&r);ComPtr<ID3D11Texture2D> t;
   if(FAILED(r.As(&t))||r.Get()==cr.Get()||r.Get()==zr.Get())return false;
   D3D11_TEXTURE2D_DESC d{};t->GetDesc(&d);D3D11_SHADER_RESOURCE_VIEW_DESC s{};views[i]->GetDesc(&s);
   const auto format=i?DXGI_FORMAT_R32_FLOAT:DXGI_FORMAT_B8G8R8A8_UNORM;
   if(d.Width!=key.width||d.Height!=key.height||d.SampleDesc.Count!=1||d.ArraySize!=1||d.MipLevels!=1||
      d.Format!=format||s.Format!=format||s.ViewDimension!=D3D11_SRV_DIMENSION_TEXTURE2D||s.Texture2D.MostDetailedMip||s.Texture2D.MipLevels!=1)return false;
  }
  Parameters p{key.objectId,key.width,key.height,0,{static_cast<float>(key.viewport[0]),static_cast<float>(key.viewport[1]),
      static_cast<float>(key.width)/key.viewport[2],static_cast<float>(key.height)/key.viewport[3]}};deferred->ClearState();
  deferred->UpdateSubresource(parameters.Get(),0,nullptr,&p,0,0);auto* cb=parameters.Get();deferred->PSSetConstantBuffers(0,1,&cb);
  deferred->VSSetShader(vertex.Get(),nullptr,0);deferred->PSSetShader(pixel.Get(),nullptr,0);deferred->PSSetShaderResources(0,3,views);
  deferred->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);deferred->RSSetState(raster.Get());
  const D3D11_VIEWPORT vp{static_cast<float>(key.viewport[0]),static_cast<float>(key.viewport[1]),static_cast<float>(key.viewport[2]),static_cast<float>(key.viewport[3]),0,1};
  deferred->RSSetViewports(1,&vp);deferred->OMSetRenderTargets(1,&target,nativeDepth);
  deferred->OMSetDepthStencilState(depthState.Get(),0);deferred->OMSetBlendState(blend.Get(),nullptr,0xffffffff);deferred->Draw(3,0);
  ComPtr<ID3D11CommandList> commands;if(FAILED(deferred->FinishCommandList(FALSE,&commands)))return false;
  immediate->ExecuteCommandList(commands.Get(),TRUE);return true;
 }
};
}
