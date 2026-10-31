// Standalone fixture only. Native effects draw normally AFTER genuine Remix
// insertion;no shield capture/replay and no SFC launch.
#pragma once
#include "gate_contract.h"
#include "../d3d9_proof/game_output_wire.h"
#include "../d3d9_proof/multi_scene_wire.h"
#include <d3d11.h>
#include <d3dcompiler.h>
#include <wrl/client.h>
#include <iostream>
#include <vector>
namespace native_gate {
using Microsoft::WRL::ComPtr;
struct Fixture {
 ComPtr<ID3D11Device> d;ComPtr<ID3D11DeviceContext> c;
 ComPtr<ID3D11Texture2D> colour,resolved,readNative,expected[3];ComPtr<ID3D11RenderTargetView> target;
 ComPtr<ID3D11ShaderResourceView> resolvedView;ComPtr<ID3D11VertexShader> vertex;ComPtr<ID3D11PixelShader> effect,nearEffect,text,blit;
 ComPtr<ID3D11BlendState> additive;
 ComPtr<ID3D11Query> expectedCopied;
 ComPtr<ID3D11DepthStencilState> farState,noDepth;ComPtr<ID3D11RasterizerState> raster;
 Store* store=nullptr;game_output::Pool* pool=nullptr;replacement::Store* ledger=nullptr;DWORD* session=nullptr;
 Dispatch dispatch=nullptr;bool baseline=false,armedVerification=false,rejectedTickets=false;unsigned checks=0,verified=0,draws=0;DWORD w=1920,h=1080;
 float mappedViewport[4]{0,0,1920,1080};
 void check(bool b,const char* why){++checks;if(!b)throw std::runtime_error(why);}
 void init(ID3D11Device* device,ID3D11DeviceContext* context,BYTE* base,DWORD* s,HMODULE addon){
  d=device;c=context;session=s;store=reinterpret_cast<Store*>(base+Offset);pool=reinterpret_cast<game_output::Pool*>(base+game_output::Offset);ledger=reinterpret_cast<replacement::Store*>(base+replacement::Offset);
  wchar_t baselineValue[4]{};GetEnvironmentVariableW(L"SFC_NATIVE_GATE_BASELINE",baselineValue,4);baseline=baselineValue[0]==L'1';dispatch=reinterpret_cast<Dispatch>(GetProcAddress(addon,"SFCNativeInsertionV1"));check(dispatch!=nullptr,"Native gate fixture export");
  D3D11_TEXTURE2D_DESC t{};t.Width=w;t.Height=h;t.MipLevels=t.ArraySize=1;t.SampleDesc.Count=8;t.Format=DXGI_FORMAT_R8G8B8A8_TYPELESS;t.BindFlags=D3D11_BIND_RENDER_TARGET;
  check(SUCCEEDED(d->CreateTexture2D(&t,nullptr,&colour)),"Native gate fixture colour");
  D3D11_RENDER_TARGET_VIEW_DESC rv{};rv.Format=DXGI_FORMAT_R8G8B8A8_UNORM;rv.ViewDimension=D3D11_RTV_DIMENSION_TEXTURE2DMS;
  check(SUCCEEDED(d->CreateRenderTargetView(colour.Get(),&rv,&target)),"Native gate fixture view");
  t.SampleDesc.Count=1;t.Format=DXGI_FORMAT_R8G8B8A8_UNORM;t.BindFlags=D3D11_BIND_SHADER_RESOURCE;
  check(SUCCEEDED(d->CreateTexture2D(&t,nullptr,&resolved)),"Native gate resolved colour");check(SUCCEEDED(d->CreateShaderResourceView(resolved.Get(),nullptr,&resolvedView)),"Native gate resolved view");
  t.BindFlags=0;t.Usage=D3D11_USAGE_STAGING;t.CPUAccessFlags=D3D11_CPU_ACCESS_READ;check(SUCCEEDED(d->CreateTexture2D(&t,nullptr,&readNative)),"Native gate fixture staging");
  for(unsigned i=0;i<3;++i){t.Format=i?DXGI_FORMAT_R32_FLOAT:DXGI_FORMAT_B8G8R8A8_UNORM;check(SUCCEEDED(d->CreateTexture2D(&t,nullptr,&expected[i])),"Native gate expected staging");}
  const char* source=R"(
float4 vs(uint i:SV_VertexID):SV_Position{float2 p[3]={float2(-1,-1),float2(-1,3),float2(3,-1)};return float4(p[i],0,1);}
struct O{float4 c:SV_Target;float z:SV_Depth;};
O fx(float4 p:SV_Position){O o;o.c=float4(0,1,0,1);o.z=1;return o;}
O nearFX(float4 p:SV_Position){if(uint(p.y)%64>=4)discard;O o;o.c=float4(0,0,.125,0);o.z=0;return o;}
float4 hud(float4 p:SV_Position):SV_Target{if(uint(p.x)%64>=8)discard;return float4(0,1,0,1);}
Texture2D<float4> image:register(t0);float4 copy(float4 p:SV_Position):SV_Target{return image.Load(int3(p.xy,0));}
)";
  ComPtr<ID3DBlob> v,f,b;check(SUCCEEDED(D3DCompile(source,strlen(source),nullptr,nullptr,nullptr,"vs","vs_4_1",0,0,&v,nullptr)),"Fixture VS");
  check(SUCCEEDED(D3DCompile(source,strlen(source),nullptr,nullptr,nullptr,"fx","ps_4_1",0,0,&f,nullptr)),"Fixture FX");
  check(SUCCEEDED(D3DCompile(source,strlen(source),nullptr,nullptr,nullptr,"copy","ps_4_1",0,0,&b,nullptr)),"Fixture blit");
  check(SUCCEEDED(d->CreateVertexShader(v->GetBufferPointer(),v->GetBufferSize(),nullptr,&vertex)),"Fixture VS create");
  check(SUCCEEDED(d->CreatePixelShader(f->GetBufferPointer(),f->GetBufferSize(),nullptr,&effect)),"Fixture FX create");
  check(SUCCEEDED(d->CreatePixelShader(b->GetBufferPointer(),b->GetBufferSize(),nullptr,&blit)),"Fixture blit create");
  ComPtr<ID3DBlob> nearCode,textCode;check(SUCCEEDED(D3DCompile(source,strlen(source),nullptr,nullptr,nullptr,"nearFX","ps_4_1",0,0,&nearCode,nullptr)),"Fixture near FX");
  check(SUCCEEDED(D3DCompile(source,strlen(source),nullptr,nullptr,nullptr,"hud","ps_4_1",0,0,&textCode,nullptr)),"Fixture native text");
  check(SUCCEEDED(d->CreatePixelShader(nearCode->GetBufferPointer(),nearCode->GetBufferSize(),nullptr,&nearEffect)),"Fixture near PS");
  check(SUCCEEDED(d->CreatePixelShader(textCode->GetBufferPointer(),textCode->GetBufferSize(),nullptr,&text)),"Fixture text PS");
  D3D11_BLEND_DESC a{};a.RenderTarget[0].BlendEnable=TRUE;a.RenderTarget[0].SrcBlend=a.RenderTarget[0].DestBlend=D3D11_BLEND_ONE;
  a.RenderTarget[0].BlendOp=a.RenderTarget[0].BlendOpAlpha=D3D11_BLEND_OP_ADD;a.RenderTarget[0].SrcBlendAlpha=a.RenderTarget[0].DestBlendAlpha=D3D11_BLEND_ONE;a.RenderTarget[0].RenderTargetWriteMask=15;
  check(SUCCEEDED(d->CreateBlendState(&a,&additive)),"Fixture native additive blend");
  D3D11_DEPTH_STENCIL_DESC z{};z.DepthEnable=TRUE;z.DepthWriteMask=D3D11_DEPTH_WRITE_MASK_ZERO;z.DepthFunc=D3D11_COMPARISON_LESS_EQUAL;
  check(SUCCEEDED(d->CreateDepthStencilState(&z,&farState)),"Fixture read-only depth");z.DepthEnable=FALSE;check(SUCCEEDED(d->CreateDepthStencilState(&z,&noDepth)),"Fixture HUD depth");
  D3D11_RASTERIZER_DESC r{};r.FillMode=D3D11_FILL_SOLID;r.CullMode=D3D11_CULL_NONE;r.DepthClipEnable=TRUE;r.ScissorEnable=TRUE;r.MultisampleEnable=TRUE;
  check(SUCCEEDED(d->CreateRasterizerState(&r,&raster)),"Fixture raster");
  D3D11_QUERY_DESC query{D3D11_QUERY_EVENT,0};check(SUCCEEDED(d->CreateQuery(&query,&expectedCopied)),"Fixture verification fence");
 }
 bool frame(const multi_scene::Frame& source,ID3D11DepthStencilView* depth,ID3D11RenderTargetView* back,bool verify){
  const float blue[]{0,0,1,1};c->ClearRenderTargetView(target.Get(),blue);c->ClearDepthStencilView(depth,D3D11_CLEAR_DEPTH,1,0);
  auto* rt=target.Get();c->OMSetRenderTargets(1,&rt,depth);c->OMSetDepthStencilState(nullptr,0);
  D3D11_VIEWPORT vp{0,0,float(w),float(h),0,1};c->RSSetViewports(1,&vp);
  bool inserted=false;Ticket t{};Reply reply{};
  if(source.frame%37==0)store->current.flags|=4;else if(source.frame%19==0)store->current.flags|=8;
  if(!baseline&&valid(source)){
   for(const auto& row:source.rows)if(row[1]==source.anchor&&row[7]==source.revision){
    memcpy(t.session,session,16);t.pid=GetCurrentProcessId();t.thread=GetCurrentThreadId();t.frame=source.frame;t.owner=row[1];t.revision=row[7];t.model=row[5];t.source=row[6];
    t.manager=1;t.count=1;t.primary=1;t.secondary=1;t.generation=store->header.generation;t.sequence=source.sequence;t.hash=source.checksum;t.offered=source.offered;t.frameStart=store->header.frameStart;t.deadline=deadline(store->header,t.frameStart);memcpy(mappedViewport,row.data()+83,16);break;}
   if(!rejectedTickets&&valid(t,store->header)){
    auto wrong=t;wrong.hash^=1;check(dispatch(DWORD(Action::Acquire),&wrong,&reply)!=DWORD(Result::Acquired),"Wrong camera/cohort ticket admitted");
    wrong=t;++wrong.generation;check(dispatch(DWORD(Action::Acquire),&wrong,&reply)!=DWORD(Result::Acquired),"Stale generation admitted");
    wrong=t;--wrong.frame;check(dispatch(DWORD(Action::Acquire),&wrong,&reply)!=DWORD(Result::Acquired),"Stale source frame admitted");
    wrong=t;++wrong.revision;check(dispatch(DWORD(Action::Acquire),&wrong,&reply)!=DWORD(Result::Acquired),"Wrong asset revision admitted");
    rejectedTickets=true;std::cout<<"NATIVE_GATE_REJECTIONS wrong_cohort_generation_frame_revision=1\n";
   }
   if(valid(t,store->header)&&dispatch(DWORD(Action::Acquire),&t,&reply)==DWORD(Result::Acquired)){
    // Snapshot expected triplet while the acquired lease prevents overwrite.
    // GPU copies precede Commit's read fence;CPU readback happens after Present.
    armedVerification=false;
    if(verify){
     for(auto& slot:pool->slots)if(output_wire::state(&slot)==output_wire::acquired&&slot.packet.source_frame==t.frame){
      for(unsigned i=0;i<3;++i){ComPtr<ID3D11Texture2D> image;check(SUCCEEDED(d->OpenSharedResource(reinterpret_cast<HANDLE>(uintptr_t(slot.packet.handles[i])),IID_PPV_ARGS(&image))),"Fixture leased output");c->CopyResource(expected[i].Get(),image.Get());}
      armedVerification=true;break;
     }
     if(armedVerification){c->End(expectedCopied.Get());c->Flush();BOOL done=FALSE;const auto until=GetTickCount64()+1000;
      while(c->GetData(expectedCopied.Get(),&done,sizeof(done),0)==S_FALSE||!done){check(GetTickCount64()<until,"Fixture expected copy deadline");Sleep(1);}
      store->current.flags|=2; // Diagnostic readback frame,not a clean timing sample.
     }
    }
    inserted=dispatch(DWORD(Action::Commit),&t,&reply)==DWORD(Result::Inserted);
    if(!inserted){dispatch(DWORD(Action::Cancel),&t,&reply);armedVerification=false;}
    if(inserted){++draws;store->current.primary=store->current.secondary=1;
     replacement::Receipt r{};if(replacement::sample(*ledger,t.frame,r)){r.owner=t.owner;r.revision=t.revision;r.flags|=replacement::Seen|replacement::Suppressed;replacement::write(ledger->receipt[t.frame%replacement::Frames],r);InterlockedIncrement(&ledger->suppressed);}}
   }
  }
  // A normal native far effect with depth testing ON and writes OFF. It must
  // remain behind covered ship pixels,without any effect replay machinery.
  c->VSSetShader(vertex.Get(),nullptr,0);c->PSSetShader(effect.Get(),nullptr,0);c->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);
  c->OMSetBlendState(nullptr,nullptr,0xffffffff);c->OMSetDepthStencilState(farState.Get(),0);c->RSSetState(raster.Get());D3D11_RECT full{0,0,LONG(w),LONG(h)};c->RSSetScissorRects(1,&full);c->Draw(3,0);
  // Near additive geometry uses native depth testing but does not write depth.
  c->OMSetBlendState(additive.Get(),nullptr,0xffffffff);c->PSSetShader(nearEffect.Get(),nullptr,0);c->Draw(3,0);
  // Depth-disabled text surrogate crosses returned and native pixels.
  c->OMSetBlendState(nullptr,nullptr,0xffffffff);c->OMSetDepthStencilState(noDepth.Get(),0);c->PSSetShader(text.Get(),nullptr,0);c->Draw(3,0);
  c->OMSetRenderTargets(0,nullptr,nullptr);c->ResolveSubresource(resolved.Get(),0,colour.Get(),0,DXGI_FORMAT_R8G8B8A8_UNORM);
  if(inserted&&armedVerification)c->CopyResource(readNative.Get(),resolved.Get());
  c->OMSetRenderTargets(1,&back,nullptr);c->OMSetDepthStencilState(noDepth.Get(),0);c->RSSetScissorRects(1,&full);c->PSSetShader(blit.Get(),nullptr,0);
  auto* view=resolvedView.Get();c->PSSetShaderResources(0,1,&view);c->Draw(3,0);ID3D11ShaderResourceView* none=nullptr;c->PSSetShaderResources(0,1,&none);
  return inserted;
 }
 void verify(DWORD owner){if(!armedVerification)return;D3D11_MAPPED_SUBRESOURCE actual{},ref[3]{};
  check(SUCCEEDED(c->Map(readNative.Get(),0,D3D11_MAP_READ,0,&actual)),"Native fixture readback");
  for(unsigned i=0;i<3;++i)check(SUCCEEDED(c->Map(expected[i].Get(),0,D3D11_MAP_READ,0,&ref[i])),"Reference fixture readback");
  unsigned mismatches=0,covered=0,textCovered=0;
  for(unsigned y=0;y<h;++y)for(unsigned x=0;x<w;++x){DWORD id{};float z=1;
   const auto qx=static_cast<int>(floor((float(x)+.5f-mappedViewport[0])*w/mappedViewport[2])),qy=static_cast<int>(floor((float(y)+.5f-mappedViewport[1])*h/mappedViewport[3]));
   if(qx>=0&&qy>=0&&qx<int(w)&&qy<int(h)){memcpy(&id,static_cast<BYTE*>(ref[2].pData)+qy*ref[2].RowPitch+qx*4,4);memcpy(&z,static_cast<BYTE*>(ref[1].pData)+qy*ref[1].RowPitch+qx*4,4);}
   DWORD expectedColour=0xff00ff00; // native green background/effect
   if(id==owner&&std::isfinite(z)&&z>=0&&z<1){++covered;if(x%64<8)++textCovered;DWORD bgra{};memcpy(&bgra,static_cast<BYTE*>(ref[0].pData)+qy*ref[0].RowPitch+qx*4,4);expectedColour=(bgra&0xff00ff00u)|((bgra&0xff)<<16)|((bgra>>16)&0xff);expectedColour|=0xff000000;}
   if(y%64<4){const auto blue=(std::min<DWORD>)(255,((expectedColour>>16)&255)+32);expectedColour=(expectedColour&0xff00ffffu)|(blue<<16);}
   if(x%64<8)expectedColour=0xff00ff00;
   DWORD pixel{};memcpy(&pixel,static_cast<BYTE*>(actual.pData)+y*actual.RowPitch+x*4,4);if(pixel!=expectedColour)++mismatches;
  }
  c->Unmap(readNative.Get(),0);for(unsigned i=0;i<3;++i)c->Unmap(expected[i].Get(),0);
  std::cout<<"NATIVE_GATE_PIXELS mismatches="<<mismatches<<" covered="<<covered<<" native_depth_and_text=1\n";
  check(covered>100&&textCovered>10&&mismatches==0,"Native gate colour/depth/coverage/native text mismatch");++verified;armedVerification=false;
 }
};
}
