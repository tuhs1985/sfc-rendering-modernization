// No SFC/Remix launch: synthetic admission + actual D3D11 8MSAA composition.
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include "../tools/remix_runtime/ship_replacement_contract.h"
#include "../tools/remix_runtime/ship_replacement_compositor.h"
#include "../tools/remix_runtime/ship_scene_depth.h"
#include <iostream>
#include <vector>
#include <limits>
using namespace ship_replacement;
using ship_triplet::checked;
static unsigned checks=0;
static void check(bool b){++checks;if(!b)throw std::runtime_error("replacement check "+std::to_string(checks));}
static Observation observation(){Observation o{};auto& k=o.key;
 k.session[0]=1;k.sourceSession[0]=2;k.sourcePid=3;k.owner=k.revision=k.frame=k.resourceEpoch=k.depthConvention=1;
 k.objectId=7;k.pose=ship_triplet::hash(o.state,17*4);k.camera=ship_triplet::hash(o.state+34,40*4);
 k.width=k.height=64;k.viewport[2]=k.viewport[3]=64;k.asset[0]=1;return o;
}
static void admission(){
 const auto o=observation();Evidence e{true,true,true,true,true,100,1000,1};
 check(adjudicate(o,o,e,101)==Refusal::None);
 for(unsigned i=0;i<5;++i){auto bad=e;switch(i){case 0:bad.gpuReady=false;break;case 1:bad.coverage=false;break;case 2:bad.visibility=false;break;case 3:bad.preUi=false;break;case 4:bad.target=false;break;}
  check(adjudicate(o,o,bad,101)!=Refusal::None);}
 check(adjudicate(o,o,Evidence{},101)!=Refusal::None);
 auto malformed=o;const float nan=std::numeric_limits<float>::quiet_NaN();memcpy(malformed.state+17,&nan,4);
 check(adjudicate(malformed,malformed,e,101)==Refusal::Invalid);
 for(unsigned i=0;i<16;++i){auto bad=o;switch(i){case 0:++bad.key.owner;break;case 1:++bad.key.revision;break;case 2:++bad.key.sourcePid;break;
 case 3:++bad.key.sourceSession[0];break;case 4:++bad.key.session[0];break;case 5:++bad.key.resourceEpoch;break;case 6:++bad.key.asset[0];break;
 case 7:++bad.key.pose;break;case 8:++bad.key.camera;break;case 9:++bad.key.frame;break;case 10:++bad.state[17];break;
 case 11:++bad.state[73];break;case 12:++bad.key.objectId;break;case 13:--bad.key.viewport[2];break;case 14:bad.key.depthConvention=0;break;case 15:bad.key.reserved=1;break;}
 check(adjudicate(bad,o,e,101)!=Refusal::None);}
 for(uint32_t mode:{1u,2u}){auto bad=o;bad.key.diagnosticMode=mode;bad.key.worldOffset[0]=1;
  check(ship_triplet::validKey(bad.key)&&adjudicate(bad,bad,e,101)==Refusal::Diagnostic);}
 check(adjudicate(o,o,e,201)==Refusal::Stale);check(adjudicate(o,o,e,99)==Refusal::Stale);
 Admission a;check(!a.commit(o,o,e,101,false));check(a.inspect(o,o,e,101)==Refusal::None);
 check(a.commit(o,o,e,101,true));check(a.inspect(o,o,e,101)==Refusal::AlreadyConsumed);
 ++e.sequence;auto changed=o;++changed.key.frame;check(!a.commit(changed,o,e,102,true));check(a.commit(o,o,e,102,true));
 std::array<uint32_t,96> row{};for(unsigned i=0;i<96;++i)row[i]=i;
 const auto raw=observe(o.key,row);check(raw.state[0]==8&&raw.state[33]==41&&raw.state[34]==49&&raw.state[73]==88);
}
static void gpu(){
 ComPtr<ID3D11Device> d;ComPtr<ID3D11DeviceContext> c;D3D_FEATURE_LEVEL obtained{};
 const D3D_FEATURE_LEVEL level=D3D_FEATURE_LEVEL_10_1;
 checked(D3D11CreateDevice(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,0,&level,1,D3D11_SDK_VERSION,&d,&obtained,&c),"hardware device");
 UINT quality=0;checked(d->CheckMultisampleQualityLevels(DXGI_FORMAT_B8G8R8A8_UNORM,8,&quality),"8MSAA query");check(quality>0);
 DepthCompositor compositor(d.Get());const auto o=observation();
 D3D11_TEXTURE2D_DESC desc{};desc.Width=desc.Height=64;desc.ArraySize=desc.MipLevels=1;desc.SampleDesc.Count=8;
 desc.Format=DXGI_FORMAT_B8G8R8A8_UNORM;desc.BindFlags=D3D11_BIND_RENDER_TARGET;
 ComPtr<ID3D11Texture2D> color,depth,resolved,staging;ComPtr<ID3D11RenderTargetView> target;ComPtr<ID3D11DepthStencilView> zview;
 checked(d->CreateTexture2D(&desc,nullptr,&color),"native color");checked(d->CreateRenderTargetView(color.Get(),nullptr,&target),"native RTV");
 desc.Format=DXGI_FORMAT_R32_TYPELESS;desc.BindFlags=D3D11_BIND_DEPTH_STENCIL|D3D11_BIND_SHADER_RESOURCE;
 checked(d->CreateTexture2D(&desc,nullptr,&depth),"native depth");
 D3D11_DEPTH_STENCIL_VIEW_DESC zd{};zd.Format=DXGI_FORMAT_D32_FLOAT;zd.ViewDimension=D3D11_DSV_DIMENSION_TEXTURE2DMS;
 checked(d->CreateDepthStencilView(depth.Get(),&zd,&zview),"native DSV");
 desc.SampleDesc.Count=1;desc.Format=DXGI_FORMAT_B8G8R8A8_UNORM;desc.BindFlags=0;
 checked(d->CreateTexture2D(&desc,nullptr,&resolved),"resolve");desc.Usage=D3D11_USAGE_STAGING;desc.CPUAccessFlags=D3D11_CPU_ACCESS_READ;
 checked(d->CreateTexture2D(&desc,nullptr,&staging),"staging");
 std::vector<uint32_t> rgba(4096,0xffff0000u),ids(4096,0);std::vector<float> zs(4096,.5f);
 for(unsigned y=16;y<48;++y)for(unsigned x=16;x<48;++x)ids[y*64+x]=7;
 ids[20*64+20]=8;zs[21*64+21]=std::numeric_limits<float>::quiet_NaN();
 rgba[22*64+22]=0xff000000u; // Legitimately BLACK covered surface must not become a cutout.
 zs[23*64+23]=-1;zs[24*64+24]=std::numeric_limits<float>::infinity();zs[25*64+25]=1.01f;
 ComPtr<ID3D11Texture2D> inputs[3];ComPtr<ID3D11ShaderResourceView> srvs[3];
 desc.Usage=D3D11_USAGE_DEFAULT;desc.CPUAccessFlags=0;desc.BindFlags=D3D11_BIND_SHADER_RESOURCE;
 for(unsigned i=0;i<3;++i){desc.Format=i?DXGI_FORMAT_R32_FLOAT:DXGI_FORMAT_B8G8R8A8_UNORM;
  D3D11_SUBRESOURCE_DATA data{};data.pSysMem=i==0?static_cast<void*>(rgba.data()):i==1?static_cast<void*>(zs.data()):static_cast<void*>(ids.data());data.SysMemPitch=256;
  checked(d->CreateTexture2D(&desc,&data,&inputs[i]),"triplet input");checked(d->CreateShaderResourceView(inputs[i].Get(),nullptr,&srvs[i]),"triplet view");}
 ID3D11ShaderResourceView* views[]={srvs[0].Get(),srvs[1].Get(),srvs[2].Get()};
 const float blue[4]={0,0,1,1};
 auto read=[&](){c->OMSetRenderTargets(0,nullptr,nullptr);c->ResolveSubresource(resolved.Get(),0,color.Get(),0,DXGI_FORMAT_B8G8R8A8_UNORM);c->CopyResource(staging.Get(),resolved.Get());
  D3D11_MAPPED_SUBRESOURCE m{};checked(c->Map(staging.Get(),0,D3D11_MAP_READ,0,&m),"fixture readback");std::vector<uint32_t> pixels(4096);
  for(unsigned y=0;y<64;++y)memcpy(pixels.data()+y*64,static_cast<BYTE*>(m.pData)+y*m.RowPitch,256);c->Unmap(staging.Get(),0);return pixels;};
 c->ClearRenderTargetView(target.Get(),blue);c->ClearDepthStencilView(zview.Get(),D3D11_CLEAR_DEPTH,.25f,0);
 c->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_LINELIST);auto* rt=target.Get();c->OMSetRenderTargets(1,&rt,zview.Get());
 check(compositor.draw(target.Get(),zview.Get(),views,o.key));
 D3D11_PRIMITIVE_TOPOLOGY topology{};c->IAGetPrimitiveTopology(&topology);check(topology==D3D11_PRIMITIVE_TOPOLOGY_LINELIST);
 ComPtr<ID3D11RenderTargetView> saved;ComPtr<ID3D11DepthStencilView> savedDepth;c->OMGetRenderTargets(1,&saved,&savedDepth);
 check(saved.Get()==target.Get()&&savedDepth.Get()==zview.Get());
 auto pixels=read();check(pixels[32*64+32]==0xff0000ffu); // Near retained scene wins.
 c->ClearRenderTargetView(target.Get(),blue);c->ClearDepthStencilView(zview.Get(),D3D11_CLEAR_DEPTH,1,0);
 check(compositor.draw(target.Get(),zview.Get(),views,o.key));pixels=read();
 check(pixels[32*64+32]==0xffff0000u&&pixels[0]==0xff0000ffu);
 check(pixels[20*64+20]==0xff0000ffu&&pixels[21*64+21]==0xff0000ffu);
 check(pixels[22*64+22]==0xff000000u);
 bool exactCoverage=true;
 for(unsigned y=0;y<64;++y)for(unsigned x=0;x<64;++x){const auto i=y*64+x;
  const bool covered=ids[i]==7&&std::isfinite(zs[i])&&zs[i]>=0&&zs[i]<=1;
  exactCoverage&=pixels[i]==(covered?rgba[i]:0xff0000ffu);}
 check(exactCoverage);
 // Ordinary subsequent native drawing: farther surface must be occluded by
 // the returned ship's depth; nearer surface/HUD must remain visible.
 const char* shader=R"(
float4 vs(uint i:SV_VertexID):SV_Position{float2 p[3]={float2(-1,-1),float2(-1,3),float2(3,-1)};return float4(p[i],0,1);}
struct O{float4 c:SV_Target;float z:SV_Depth;};
O farPS(){O o;o.c=float4(0,1,0,1);o.z=.75;return o;}
O nearPS(){O o;o.c=float4(0,1,0,1);o.z=.1;return o;}
)";
 ComPtr<ID3DBlob> vb,fb,nb;ComPtr<ID3D11VertexShader> vs;ComPtr<ID3D11PixelShader> farPixel,nearPixel;
 checked(D3DCompile(shader,strlen(shader),nullptr,nullptr,nullptr,"vs","vs_4_1",0,0,&vb,nullptr),"native VS");
 checked(D3DCompile(shader,strlen(shader),nullptr,nullptr,nullptr,"farPS","ps_4_1",0,0,&fb,nullptr),"native far PS");
 checked(D3DCompile(shader,strlen(shader),nullptr,nullptr,nullptr,"nearPS","ps_4_1",0,0,&nb,nullptr),"native near PS");
 checked(d->CreateVertexShader(vb->GetBufferPointer(),vb->GetBufferSize(),nullptr,&vs),"native VS create");
 checked(d->CreatePixelShader(fb->GetBufferPointer(),fb->GetBufferSize(),nullptr,&farPixel),"native far create");checked(d->CreatePixelShader(nb->GetBufferPointer(),nb->GetBufferSize(),nullptr,&nearPixel),"native near create");
 c->ClearState();c->OMSetRenderTargets(1,&rt,zview.Get());c->VSSetShader(vs.Get(),nullptr,0);c->PSSetShader(farPixel.Get(),nullptr,0);
 c->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);D3D11_VIEWPORT vp{0,0,64,64,0,1};c->RSSetViewports(1,&vp);c->Draw(3,0);pixels=read();
 check(pixels[32*64+32]==0xffff0000u&&pixels[0]==0xff00ff00u);
 c->OMSetRenderTargets(1,&rt,zview.Get());c->PSSetShader(nearPixel.Get(),nullptr,0);c->Draw(3,0);pixels=read();check(pixels[32*64+32]==0xff00ff00u);
 // UI-like last draw with depth disabled (same PS) must cover the ship.
 c->ClearDepthStencilView(zview.Get(),D3D11_CLEAR_DEPTH,1,0);check(compositor.draw(target.Get(),zview.Get(),views,o.key));
 D3D11_DEPTH_STENCIL_DESC noZ{};ComPtr<ID3D11DepthStencilState> ui;checked(d->CreateDepthStencilState(&noZ,&ui),"UI depth state");
 c->OMSetRenderTargets(1,&rt,zview.Get());c->OMSetDepthStencilState(ui.Get(),0);c->PSSetShader(farPixel.Get(),nullptr,0);c->Draw(3,0);pixels=read();check(pixels[32*64+32]==0xff00ff00u);
 auto bad=o.key;bad.diagnosticMode=2;bad.worldOffset[0]=1;check(!compositor.draw(target.Get(),zview.Get(),views,bad));
 check(!compositor.draw(target.Get(),nullptr,views,o.key));
 bad=o.key;bad.width=63;check(!compositor.draw(target.Get(),zview.Get(),views,bad));
 bad=o.key;bad.viewport[0]=1;check(!compositor.draw(target.Get(),zview.Get(),views,bad));
 auto* original=views[1];views[1]=srvs[0].Get();check(!compositor.draw(target.Get(),zview.Get(),views,o.key));views[1]=original;
 ComPtr<ID3D11RenderTargetView> wrongTarget;desc.Format=DXGI_FORMAT_B8G8R8A8_UNORM;desc.BindFlags=D3D11_BIND_RENDER_TARGET;
 ComPtr<ID3D11Texture2D> single;checked(d->CreateTexture2D(&desc,nullptr,&single),"single sample target");checked(d->CreateRenderTargetView(single.Get(),nullptr,&wrongTarget),"single RTV");
 check(!compositor.draw(wrongTarget.Get(),zview.Get(),views,o.key));
 // Existing additive path: compare SDK pixels with the retained native scene
 // through the ACTUAL offset viewport,not an assumed full-screen identity map.
 ship_triplet::Compositor filter(d.Get(),true);ship_scene_depth::Data stats{};ship_scene_depth::Source retained(d.Get(),stats);
 sfc_calibration::Mailbox mailbox{};mailbox.active=1;mailbox.snapshot.frame=10;
 c->OMSetRenderTargets(1,&rt,zview.Get());retained.observe(reinterpret_cast<uintptr_t>(c.Get()),&mailbox);
 auto* nativeView=retained.finish(10,64,64);check(nativeView&&stats.qualified==1&&stats.epoch==1);
 check(!retained.finish(11,64,64)); // Never reuse a previous frame's observation.
 c->ClearDepthStencilView(zview.Get(),D3D11_CLEAR_DEPTH,1,0);c->OMSetRenderTargets(1,&rt,zview.Get());
 c->OMSetDepthStencilState(nullptr,0);c->VSSetShader(vs.Get(),nullptr,0);c->PSSetShader(nearPixel.Get(),nullptr,0);
 c->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);vp.Width=32;vp.Height=64;c->RSSetViewports(1,&vp);c->Draw(3,0);
 c->OMSetRenderTargets(0,nullptr,nullptr);const float empty[4]{};c->ClearRenderTargetView(wrongTarget.Get(),empty);
 auto mapped=o.key;mapped.viewport[0]=4;mapped.viewport[1]=6;mapped.viewport[2]=40;mapped.viewport[3]=50;
 D3D11_VIEWPORT full{0,0,64,64,0,1};check(filter.draw(wrongTarget.Get(),views,mapped,full,nativeView));
 // single is already non-MSAA:read back without ResolveSubresource.
 c->CopyResource(staging.Get(),single.Get());D3D11_MAPPED_SUBRESOURCE filtered{};checked(c->Map(staging.Get(),0,D3D11_MAP_READ,0,&filtered),"filtered depth readback");
 bool mappedCorrectly=true;
 for(unsigned y=0;y<64;++y)for(unsigned x=0;x<64;++x){const auto i=y*64+x;uint32_t actual=0;memcpy(&actual,static_cast<BYTE*>(filtered.pData)+y*filtered.RowPitch+x*4,4);
  const unsigned nativeX=static_cast<unsigned>(std::floor(4+(x+.5)*40/64));
  const bool visible=ids[i]==7&&std::isfinite(zs[i])&&zs[i]>=0&&zs[i]<=1&&nativeX>=32;
  mappedCorrectly&=actual==(visible?rgba[i]:0u);}
 c->Unmap(staging.Get(),0);check(mappedCorrectly);check(!filter.draw(wrongTarget.Get(),views,mapped,full));
 c->OMSetRenderTargets(1,&rt,zview.Get());mailbox.snapshot.frame=20;retained.observe(reinterpret_cast<uintptr_t>(c.Get()),&mailbox);
 mailbox.snapshot.frame=21;retained.observe(reinterpret_cast<uintptr_t>(c.Get()),&mailbox);check(!retained.finish(21,64,64));
 retained.observe(reinterpret_cast<uintptr_t>(c.Get()),&mailbox);check(retained.finish(21,64,64)!=nullptr);
 retained.observe(reinterpret_cast<uintptr_t>(c.Get()),&mailbox);retained.cleared(reinterpret_cast<uintptr_t>(c.Get()));check(!retained.finish(21,64,64));
 retained.observe(reinterpret_cast<uintptr_t>(c.Get()),&mailbox);check(retained.finish(21,64,64)!=nullptr);
 ComPtr<ID3D11Texture2D> secondDepth;ComPtr<ID3D11DepthStencilView> secondView;D3D11_TEXTURE2D_DESC secondDesc{};depth->GetDesc(&secondDesc);
 checked(d->CreateTexture2D(&secondDesc,nullptr,&secondDepth),"second depth epoch");checked(d->CreateDepthStencilView(secondDepth.Get(),&zd,&secondView),"second DSV");
 retained.observe(reinterpret_cast<uintptr_t>(c.Get()),&mailbox);c->OMSetRenderTargets(1,&rt,secondView.Get());retained.observe(reinterpret_cast<uintptr_t>(c.Get()),&mailbox);
 check(!retained.finish(21,64,64));retained.observe(reinterpret_cast<uintptr_t>(c.Get()),&mailbox);check(retained.finish(21,64,64)&&stats.epoch==2);
}
int main(){try{admission();gpu();std::cout<<"Replacement offline PASS "<<checks<<" checks;8MSAA depth/coverage/order/state;NO SFC hooks or suppression\n";return 0;}
 catch(const std::exception& e){std::cerr<<e.what()<<"\n";return 1;}}
