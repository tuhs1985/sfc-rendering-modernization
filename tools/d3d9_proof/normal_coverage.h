// Backend-only UNION coverage for the ordinary D3D9 scene. The anchor label is
// NOT a per-object picking ID when multiple retained ships are drawn.
// Normal Remix picking0 can be real geometry. Use qualified depth sentinel,
// never an RGB/background-colour cutout,rectangle or guessed material->owner ID.
#pragma once
struct NormalCoverage {
 Microsoft::WRL::ComPtr<ID3D11VertexShader> vertex;Microsoft::WRL::ComPtr<ID3D11PixelShader> pixel;
 Microsoft::WRL::ComPtr<ID3D11ShaderResourceView> depth;Microsoft::WRL::ComPtr<ID3D11RenderTargetView> target;
 Microsoft::WRL::ComPtr<ID3D11Buffer> constant;bool enabled=false;
 void start(ID3D11Device* device,ID3D11Texture2D* source,ID3D11Texture2D* output){
  wchar_t flag[2]{};enabled=GetEnvironmentVariableW(L"SFC_D3D9_GAME_OUTPUT",flag,2)==1&&flag[0]==L'1';
  ZeroMemory(flag,sizeof(flag));enabled=enabled||(GetEnvironmentVariableW(L"SFC_D3D9_COVERAGE_TEST",flag,2)==1&&flag[0]==L'1');if(!enabled)return;
  check(device->CreateShaderResourceView(source,nullptr,&depth),"coverage depth SRV");check(device->CreateRenderTargetView(output,nullptr,&target),"coverage target");
  const char* vs="float4 main(uint i:SV_VertexID):SV_Position{float2 p[3]={float2(-1,-1),float2(-1,3),float2(3,-1)};return float4(p[i],0,1);}";
  const char* ps="Texture2D<float> z:register(t0);cbuffer K:register(b0){uint owner;uint3 pad;};float main(float4 p:SV_Position):SV_Target{float d=z.Load(int3(int2(p.xy),0));return isfinite(d)&&d>=0&&d<=1?asfloat(owner):asfloat(0u);}";
  Microsoft::WRL::ComPtr<ID3DBlob> a,b;check(D3DCompile(vs,strlen(vs),nullptr,nullptr,nullptr,"main","vs_4_1",D3DCOMPILE_ENABLE_STRICTNESS,0,&a,nullptr),"coverage VS compile");
  check(D3DCompile(ps,strlen(ps),nullptr,nullptr,nullptr,"main","ps_4_1",D3DCOMPILE_ENABLE_STRICTNESS,0,&b,nullptr),"coverage PS compile");
  check(device->CreateVertexShader(a->GetBufferPointer(),a->GetBufferSize(),nullptr,&vertex),"coverage VS");check(device->CreatePixelShader(b->GetBufferPointer(),b->GetBufferSize(),nullptr,&pixel),"coverage PS");
  D3D11_BUFFER_DESC d{};d.ByteWidth=16;d.BindFlags=D3D11_BIND_CONSTANT_BUFFER;check(device->CreateBuffer(&d,nullptr,&constant),"coverage constants");
 }
 bool draw(ID3D11DeviceContext* context,uint32_t owner,uint32_t width,uint32_t height){
  if(!enabled)return false;require(owner&&output_wire::qualified_extent(width,height),"coverage anchor/qualified output required");
  const uint32_t data[4]={owner,0,0,0};context->ClearState();context->UpdateSubresource(constant.Get(),0,nullptr,data,0,0);
  auto* c=constant.Get();auto* s=depth.Get();auto* r=target.Get();context->VSSetShader(vertex.Get(),nullptr,0);context->PSSetShader(pixel.Get(),nullptr,0);
  context->PSSetShaderResources(0,1,&s);context->PSSetConstantBuffers(0,1,&c);context->OMSetRenderTargets(1,&r,nullptr);
  D3D11_VIEWPORT viewport{0,0,float(width),float(height),0,1};context->RSSetViewports(1,&viewport);context->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);context->Draw(3,0);context->ClearState();return true;
 }
};
