// Host-owned GPU-only final-colour adjustment. No change to picking/depth/alpha.
#pragma once
#include <d3dcompiler.h>
#include <array>
#include <cstdint>
#include <string>
#include <stdexcept>
class RemixImageAdjust {
 Microsoft::WRL::ComPtr<ID3D11Texture2D> scratch;
 Microsoft::WRL::ComPtr<ID3D11ShaderResourceView> input;
 Microsoft::WRL::ComPtr<ID3D11RenderTargetView> output;
 Microsoft::WRL::ComPtr<ID3D11VertexShader> vs;
 Microsoft::WRL::ComPtr<ID3D11PixelShader> ps;
 Microsoft::WRL::ComPtr<ID3D11PixelShader> coveragePs;
 Microsoft::WRL::ComPtr<ID3D11ShaderResourceView> depth;
 Microsoft::WRL::ComPtr<ID3D11RenderTargetView> coverage;
 Microsoft::WRL::ComPtr<ID3D11Buffer> constants;
 static std::string pixelSource(bool withCoverage){
  const std::string common=R"(
Texture2D<float4> source:register(t0);cbuffer Params:register(b0){float contrast;float gamma;float saturation;float unused;};
float3 toLinear(float3 x){return float3(x.r<=.04045?x.r/12.92:pow((x.r+.055)/1.055,2.4),x.g<=.04045?x.g/12.92:pow((x.g+.055)/1.055,2.4),x.b<=.04045?x.b/12.92:pow((x.b+.055)/1.055,2.4));}
float3 srgb(float3 x){return float3(x.r<=.0031308?12.92*x.r:1.055*pow(x.r,1./2.4)-.055,x.g<=.0031308?12.92*x.g:1.055*pow(x.g,1./2.4)-.055,x.b<=.0031308?12.92*x.b:1.055*pow(x.b,1./2.4)-.055);}
float4 adjust(float4 p){
 float4 c=source.Load(int3(int2(p.xy),0));
 if(contrast!=1||saturation!=1){float3 l=saturate(contrast*(toLinear(c.rgb)-.18)+.18);l=lerp(dot(l,float3(.2126,.7152,.0722)).xxx,l,saturation);c.rgb=srgb(saturate(l));}
 if(gamma!=1)c.rgb=pow(saturate(c.rgb),1/gamma);
 return c;
})";
  return common+(withCoverage?R"(
Texture2D<float> z:register(t1);
struct Result {float4 color:SV_Target0;float owner:SV_Target1;};
Result main(float4 p:SV_Position){Result r;r.color=adjust(p);float d=z.Load(int3(int2(p.xy),0));r.owner=isfinite(d)&&d>=0&&d<=1?unused:asfloat(0u);return r;}
)":"float4 main(float4 p:SV_Position):SV_Target{return adjust(p);}");
 }
public:
 void prepare(ID3D11Device* d,ID3D11Texture2D* target){
  D3D11_TEXTURE2D_DESC desc{};target->GetDesc(&desc);desc.MiscFlags=0;desc.BindFlags=D3D11_BIND_SHADER_RESOURCE;
  check(d->CreateTexture2D(&desc,nullptr,&scratch),"image scratch");check(d->CreateShaderResourceView(scratch.Get(),nullptr,&input),"image input");check(d->CreateRenderTargetView(target,nullptr,&output),"image target");
  const char* vertex="float4 main(uint i:SV_VertexID):SV_Position{float2 p[3]={float2(-1,-1),float2(-1,3),float2(3,-1)};return float4(p[i],0,1);}";
  const auto pixel=pixelSource(false);
  Microsoft::WRL::ComPtr<ID3DBlob> v,p;
  check(D3DCompile(vertex,strlen(vertex),nullptr,nullptr,nullptr,"main","vs_4_1",D3DCOMPILE_ENABLE_STRICTNESS,0,&v,nullptr),"image VS compile");
  check(D3DCompile(pixel.data(),pixel.size(),nullptr,nullptr,nullptr,"main","ps_4_1",D3DCOMPILE_ENABLE_STRICTNESS,0,&p,nullptr),"image PS compile");
  check(d->CreateVertexShader(v->GetBufferPointer(),v->GetBufferSize(),nullptr,&vs),"image VS");check(d->CreatePixelShader(p->GetBufferPointer(),p->GetBufferSize(),nullptr,&ps),"image PS");
  D3D11_BUFFER_DESC b{};b.ByteWidth=16;b.BindFlags=D3D11_BIND_CONSTANT_BUFFER;check(d->CreateBuffer(&b,nullptr,&constants),"image constants");
 }
 // Worker-owned MRT path:exact same grade,depth sentinel and owner bits as the
 // separate passes. No colour-key masks or new synchronization assumptions.
 void prepareCoverage(ID3D11Device* d,ID3D11Texture2D* sourceDepth,ID3D11Texture2D* target){
  check(d->CreateShaderResourceView(sourceDepth,nullptr,&depth),"combined depth input");
  check(d->CreateRenderTargetView(target,nullptr,&coverage),"combined coverage target");
  const auto shader=pixelSource(true);Microsoft::WRL::ComPtr<ID3DBlob> code;
  check(D3DCompile(shader.data(),shader.size(),nullptr,nullptr,nullptr,"main","ps_4_1",D3DCOMPILE_ENABLE_STRICTNESS,0,&code,nullptr),"combined image/coverage compile");
  check(d->CreatePixelShader(code->GetBufferPointer(),code->GetBufferSize(),nullptr,&coveragePs),"combined image/coverage PS");
 }
 bool drawCoverage(ID3D11DeviceContext* c,ID3D11Texture2D* target,std::array<float,4> params,uint32_t owner){
  if(!coveragePs||!owner)throw std::runtime_error("Combined image/coverage not prepared or missing owner");
  memcpy(&params[3],&owner,4);D3D11_TEXTURE2D_DESC d{};target->GetDesc(&d);
  c->ClearState();c->CopyResource(scratch.Get(),target);c->UpdateSubresource(constants.Get(),0,nullptr,params.data(),0,0);
  auto* b=constants.Get();ID3D11RenderTargetView* targets[]{output.Get(),coverage.Get()};ID3D11ShaderResourceView* inputs[]{input.Get(),depth.Get()};
  c->VSSetShader(vs.Get(),nullptr,0);c->PSSetShader(coveragePs.Get(),nullptr,0);c->PSSetConstantBuffers(0,1,&b);c->PSSetShaderResources(0,2,inputs);
  c->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);c->OMSetRenderTargets(2,targets,nullptr);
  D3D11_VIEWPORT viewport{0,0,float(d.Width),float(d.Height),0,1};c->RSSetViewports(1,&viewport);c->Draw(3,0);c->ClearState();return true;
 }
 bool draw(ID3D11DeviceContext* c,ID3D11Texture2D* target,const std::array<float,4>& params){
  if(params[0]==1&&params[1]==1&&params[2]==1)return false;
  D3D11_TEXTURE2D_DESC d{};target->GetDesc(&d);c->ClearState();c->CopyResource(scratch.Get(),target);c->UpdateSubresource(constants.Get(),0,nullptr,params.data(),0,0);
  auto* b=constants.Get();auto* r=output.Get();auto* s=input.Get();c->VSSetShader(vs.Get(),nullptr,0);c->PSSetShader(ps.Get(),nullptr,0);c->PSSetConstantBuffers(0,1,&b);c->PSSetShaderResources(0,1,&s);
  c->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);c->OMSetRenderTargets(1,&r,nullptr);
  D3D11_VIEWPORT viewport{0,0,static_cast<float>(d.Width),static_cast<float>(d.Height),0,1};c->RSSetViewports(1,&viewport);c->Draw(3,0);c->ClearState();return true;
 }
};
