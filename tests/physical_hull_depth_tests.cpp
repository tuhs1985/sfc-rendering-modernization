#define SFC_D3D9_REPLAY_TYPES_ONLY
#include "../tools/d3d9_proof/d3d9_replay.cpp"
#include <d3d11.h>
#include <d3dcompiler.h>
#include "../tools/d3d9_proof/physical_hull_depth.h"
static Frame pose(){Frame f{};f.active=1;for(auto* m:{f.model,f.view,f.projection})for(unsigned i=0;i<4;++i)m[i*4+i]=1;f.viewport[2]=1920;f.viewport[3]=1080;return f;}
int main(){try{
 ComPtr<ID3D11Device> d;ComPtr<ID3D11DeviceContext> c;D3D_FEATURE_LEVEL level{};
 ok(D3D11CreateDevice(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,0,nullptr,0,D3D11_SDK_VERSION,&d,&level,&c),"test device");
 D3D11_TEXTURE2D_DESC desc{};desc.Width=96;desc.Height=64;desc.ArraySize=desc.MipLevels=desc.SampleDesc.Count=1;desc.Format=DXGI_FORMAT_R32_FLOAT;desc.BindFlags=D3D11_BIND_RENDER_TARGET|D3D11_BIND_SHADER_RESOURCE;
 ComPtr<ID3D11Texture2D> output,staging;ok(d->CreateTexture2D(&desc,nullptr,&output),"test output");
 desc.BindFlags=0;desc.Usage=D3D11_USAGE_STAGING;desc.CPUAccessFlags=D3D11_CPU_ACCESS_READ;ok(d->CreateTexture2D(&desc,nullptr,&staging),"test staging");
 PhysicalHullDepth hull;hull.start(d.Get(),output.Get(),true);
 Scene scene;scene.vertices={{{-.8f,-.8f,.5f},{0,0,1},{0,0}},{{0,.8f,.5f},{0,0,1},{0,0}},{{.8f,-.8f,.5f},{0,0,1},{0,0}}};scene.indices={0,1,2};
 auto mesh=hull.prepare(scene);require(mesh.bytes==108,"one cached mesh byte count");
 auto sample=[&](unsigned x,unsigned y){c->CopyResource(staging.Get(),output.Get());D3D11_MAPPED_SUBRESOURCE m{};ok(c->Map(staging.Get(),0,D3D11_MAP_READ,0,&m),"test read");float z;memcpy(&z,static_cast<BYTE*>(m.pData)+y*m.RowPitch+x*4,4);c->Unmap(staging.Get(),0);return z;};
 auto expectDepth=[](float a,float b){require(std::abs(a-b)<1e-6f,"physical hull expected depth");};
 auto f=pose();hull.begin();hull.submit(mesh,f);hull.draw(c.Get());expectDepth(sample(48,32),.5f);expectDepth(sample(0,0),-1234);
 auto close=f;close.model[11]=-.25f;hull.begin();hull.submit(mesh,close);hull.submit(mesh,f);hull.draw(c.Get());expectDepth(sample(48,32),.25f);
 hull.begin();hull.submit(mesh,f);hull.submit(mesh,close);hull.draw(c.Get());expectDepth(sample(48,32),.25f); // independent of submission order
 auto moved=f;moved.model[3]=1.2f;hull.begin();hull.submit(mesh,moved);hull.draw(c.Get());expectDepth(sample(48,32),-1234);expectDepth(sample(88,32),.5f);
 auto rotated=f;rotated.model[0]=0;rotated.model[1]=-1;rotated.model[4]=1;rotated.model[5]=0;hull.begin();hull.submit(mesh,rotated);hull.draw(c.Get());expectDepth(sample(48,32),.5f);expectDepth(sample(12,50),-1234);
 auto clipped=f;clipped.model[11]=-1;hull.begin();hull.submit(mesh,clipped);hull.draw(c.Get());expectDepth(sample(48,32),-1234);
 auto viewport=f;viewport.viewport[0]=960;viewport.viewport[2]=960;hull.begin();hull.submit(mesh,viewport);hull.draw(c.Get());expectDepth(sample(48,32),.5f);expectDepth(sample(0,0),-1234); // receiver applies native viewport once
 auto inactive=f;inactive.active=0;hull.begin();hull.submit(mesh,inactive);hull.draw(c.Get());expectDepth(sample(48,32),-1234);
 hull.begin();hull.draw(c.Get());expectDepth(sample(72,32),-1234); // no stale depth on retirement
 hull.begin();for(unsigned i=0;i<scene_capacity::Owners;++i){f.owner=i+1;require(hull.submit(mesh,f),"admitted scene owner has hull capacity");}
 require(hull.count==scene_capacity::Owners&&hull.count>100,"full scene capacity beyond model33");
 require(!hull.submit(mesh,f)&&hull.count==scene_capacity::Owners&&hull.omitted==1,"overflow omits owner without exception or overwrite");
 hull.draw(c.Get());expectDepth(sample(48,32),.5f);
 hull.begin();require(hull.submit(mesh,f)&&hull.count==1,"next frame recovers after capacity pressure");
 PhysicalHullDepth::Mesh missing;require(!hull.submit(missing,f)&&hull.count==1,"invalid coverage cannot authorize colour");
 require(hull.geometryBytes==108,"no geometry uploads on pose updates");
 // Actual per-owner GPU coverage for the full admitted scene,not just array
 // insertion. One shared mesh,256 distinct transforms/owner IDs;owner33 and
 // later must occupy their own pixels and remain eligible for replacement.
 SetEnvironmentVariableW(L"SFC_NATIVE_INSERTION_GATE",L"1");SetEnvironmentVariableW(L"SFC_NATIVE_INSERTION_ALL_SHIPS",L"1");
 D3D11_TEXTURE2D_DESC od{};output->GetDesc(&od);ComPtr<ID3D11Texture2D> ownerImage,ownerReadback;
 ok(d->CreateTexture2D(&od,nullptr,&ownerImage),"owner coverage target");od.Usage=D3D11_USAGE_STAGING;od.BindFlags=0;od.CPUAccessFlags=D3D11_CPU_ACCESS_READ;
 ok(d->CreateTexture2D(&od,nullptr,&ownerReadback),"owner coverage readback");
 PhysicalHullDepth fleet;fleet.start(d.Get(),output.Get(),true,ownerImage.Get());auto shared=fleet.prepare(scene);fleet.begin();
 for(unsigned i=0;i<scene_capacity::Owners;++i){auto ship=pose();ship.owner=0x3f800000u+i;
  ship.model[0]=ship.model[5]=.05f;ship.model[3]=-.9375f+float(i%16)*.125f;ship.model[7]=.9375f-float(i/16)*.125f;
  require(fleet.submit(shared,ship),"full fleet coverage admission");}
 fleet.draw(c.Get());c->CopyResource(ownerReadback.Get(),ownerImage.Get());D3D11_MAPPED_SUBRESOURCE owners{};
 ok(c->Map(ownerReadback.Get(),0,D3D11_MAP_READ,0,&owners),"fleet owner readback");
 for(unsigned i=0;i<scene_capacity::Owners;++i){const unsigned x=(i%16)*6+3,y=(i/16)*4+2;uint32_t owner=0;
  memcpy(&owner,static_cast<BYTE*>(owners.pData)+y*owners.RowPitch+x*4,4);require(owner==0x3f800000u+i,"correct independent owner pixels through full capacity");}
 c->Unmap(ownerReadback.Get(),0);require(fleet.draws==scene_capacity::Owners&&fleet.geometryBytes==108,"fleet shares immutable geometry");
 std::cout<<"FLEET_OWNER_PIXELS draws="<<fleet.draws<<" shared_geometry=1\n";
 // Debris has an independent high-bit epoch namespace. R32_FLOAT is a raw
 // identity carrier here: preserve signed/subnormal bit patterns exactly.
 for(uint32_t identity:{0x80000001u,0x80000002u}){
  auto debris=pose();debris.owner=identity;fleet.begin();require(fleet.submit(shared,debris),"debris hull admission");fleet.draw(c.Get());
  c->CopyResource(ownerReadback.Get(),ownerImage.Get());ok(c->Map(ownerReadback.Get(),0,D3D11_MAP_READ,0,&owners),"debris owner readback");
  uint32_t actual=0;memcpy(&actual,static_cast<BYTE*>(owners.pData)+32*owners.RowPitch+48*4,4);
  c->Unmap(ownerReadback.Get(),0);require(actual==identity,"independent debris identity survives actual GPU output");
 }
 std::cout<<"Physical hull GPU PASS translation rotation viewport clipping overlap order retirement capacity cache; checks="<<checks<<'\n';return 0;
 }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
