// Remix adapter's ordinary D3D9 geometric decal submission. Renderer worker only.
#pragma once
#include "../scene_bridge/damage_state.h"
struct DamageLayer {
 struct Geometry {ComPtr<IDirect3DVertexBuffer9> vertices;uint64_t bytes=0;};
 ComPtr<IDirect3DDevice9> device;std::array<ComPtr<IDirect3DTexture9>,9> textures;
 bool enabled=false;uint64_t draws=0,unqualified=0,textureBytes=0;
 static bool requested(){wchar_t v[2]{};return GetEnvironmentVariableW(L"SFC_DAMAGE_TEXTURES",v,2)==1&&v[0]==L'1';}
 void start(IDirect3DDevice9* d,const fs::path& root){
  enabled=requested();if(!enabled)return;device=d;
  const auto index=read(root/L"damage-index.bin",160);require(index.size()==160,"damage texture index layout");
  size_t at=0;const auto header=take<std::array<uint32_t,4>>(index,at);require(header[0]==0x314C4D44&&header[1]==1&&header[2]==9&&header[3]<=128*1024*1024,"damage library bounds");
  for(unsigned i=0;i<9;++i){const auto width=take<uint32_t>(index,at),height=take<uint32_t>(index,at);const auto hash=take<uint64_t>(index,at);
   auto raw=read(root/(L"damage-texture-"+std::to_wstring(i)+L".bin"),64*1024*1024+16);size_t offset=0;const auto h=take<std::array<uint32_t,4>>(raw,offset);
   require(h[0]==0x31544653&&h[1]==width&&h[2]==height&&width&&height&&width<=4096&&height<=4096&&h[3]==uint64_t(width)*height*4&&raw.size()==16+h[3]&&output_wire::hash(raw.data(),raw.size())==hash,"damage image identity/layout");
   textureBytes+=h[3];require(textureBytes<=128*1024*1024,"damage GPU texture cap");
   ComPtr<IDirect3DTexture9> staging;ok(d->CreateTexture(width,height,1,0,D3DFMT_A8R8G8B8,D3DPOOL_DEFAULT,&textures[i],nullptr),"damage texture");
   ok(d->CreateTexture(width,height,1,0,D3DFMT_A8R8G8B8,D3DPOOL_SYSTEMMEM,&staging,nullptr),"damage staging");
   D3DLOCKED_RECT lock{};ok(staging->LockRect(0,&lock,nullptr,0),"damage staging lock");require(lock.Pitch>=static_cast<INT>(width*4),"damage row pitch");
   for(unsigned y=0;y<height;++y)memcpy(static_cast<BYTE*>(lock.pBits)+y*lock.Pitch,raw.data()+16+y*width*4,width*4);
   ok(staging->UnlockRect(0),"damage staging unlock");ok(d->UpdateTexture(staging.Get(),textures[i].Get()),"damage upload");
  }
  std::cout<<"DAMAGE_LIBRARY_READY textures=9 bytes="<<textureBytes<<" native_black_key=1 remix_decal=1\n";
 }
 Geometry prepare(const Scene& scene){Geometry out{};if(!enabled)return out;
  // A mixed scene may contain qualified rigid debris with no intact-ship
  // damage channel. Do not invent UVs or block its otherwise qualified hull.
  if(scene.damageUV.empty())return out;
  require(scene.damageUV.size()==scene.vertices.size(),"fresh damage UV channel missing");
  std::vector<Vertex> vertices=scene.vertices;for(size_t i=0;i<vertices.size();++i)memcpy(vertices[i].uv,scene.damageUV[i].data(),8);
  out.bytes=vertices.size()*sizeof(Vertex);ok(device->CreateVertexBuffer(static_cast<UINT>(out.bytes),0,D3DFVF_XYZ|D3DFVF_NORMAL|D3DFVF_TEX1,D3DPOOL_DEFAULT,&out.vertices,nullptr),"damage vertex buffer");
  void* target=nullptr;ok(out.vertices->Lock(0,0,&target,0),"damage geometry upload");memcpy(target,vertices.data(),static_cast<size_t>(out.bytes));ok(out.vertices->Unlock(),"damage geometry unlock");return out;
 }
 bool ready(const sfc_damage::State& state,const Geometry& geometry){if(!enabled)return true;
  // Optional damage qualification must not hide an otherwise qualified hull.
  // Report a partial damage layer; never infer an undamaged source state.
  if(!sfc_damage::valid(state)||!geometry.vertices)++unqualified;return true;}
 void draw(const Scene& scene,Renderer& renderer,const Geometry& geometry,const sfc_damage::State& state){
  if(!enabled||!sfc_damage::valid(state)||!geometry.vertices)return;const int tier=sfc_damage::severity(state.scalar);if(tier<0)return;
  auto* d=device.Get();ok(d->SetStreamSource(0,geometry.vertices.Get(),0,sizeof(Vertex)),"damage stream");ok(d->SetIndices(renderer.ib.Get()),"damage indices");
  ok(d->SetTexture(0,textures[state.family*3+tier].Get()),"damage selected original pair");
  ok(d->SetTextureStageState(0,D3DTSS_ALPHAOP,D3DTOP_SELECTARG1),"damage alpha source");ok(d->SetTextureStageState(0,D3DTSS_ALPHAARG1,D3DTA_TEXTURE),"damage texture alpha");
  ok(d->SetRenderState(D3DRS_ALPHATESTENABLE,TRUE),"damage alpha test");ok(d->SetRenderState(D3DRS_ALPHAREF,8),"native damage alpha ref");ok(d->SetRenderState(D3DRS_ALPHAFUNC,D3DCMP_GREATER),"native damage alpha compare");
  // Pinned Remix InstanceManager::calculateAlphaState only sets isDecal
  // when blending is enabled, even with decalTextures and alpha testing.
  // Without this the duplicate hull stays coplanar instead of using Remix's
  // decal offset/material blend and can fight or obscure the opaque hull.
  ok(d->SetRenderState(D3DRS_SRCBLEND,D3DBLEND_SRCALPHA),"damage source alpha");
  ok(d->SetRenderState(D3DRS_DESTBLEND,D3DBLEND_INVSRCALPHA),"damage underlying hull");
  ok(d->SetRenderState(D3DRS_BLENDOP,D3DBLENDOP_ADD),"damage blend operation");
  ok(d->SetRenderState(D3DRS_ALPHABLENDENABLE,TRUE),"Remix decal requires blending");ok(d->SetRenderState(D3DRS_ZWRITEENABLE,FALSE),"damage no hull depth replacement");
  ok(d->BeginScene(),"damage begin");ok(d->DrawIndexedPrimitive(D3DPT_TRIANGLELIST,0,0,static_cast<UINT>(scene.vertices.size()),0,static_cast<UINT>(scene.indices.size()/3)),"damage decal draw");ok(d->EndScene(),"damage end");
  ok(d->SetRenderState(D3DRS_ALPHATESTENABLE,FALSE),"restore damage alpha test");ok(d->SetRenderState(D3DRS_ALPHABLENDENABLE,FALSE),"restore opaque hull blend");ok(d->SetRenderState(D3DRS_SRCBLEND,D3DBLEND_ONE),"restore opaque source");ok(d->SetRenderState(D3DRS_DESTBLEND,D3DBLEND_ZERO),"restore opaque destination");ok(d->SetRenderState(D3DRS_ZWRITEENABLE,TRUE),"restore damage depth write");ok(d->SetTextureStageState(0,D3DTSS_ALPHAOP,D3DTOP_DISABLE),"restore damage alpha operation");++draws;
 }
 ~DamageLayer(){if(enabled)std::cout<<"DAMAGE_SUMMARY draws="<<draws<<" unqualified="<<unqualified<<" shared_textures=9 bytes="<<textureBytes<<'\n';}
};
