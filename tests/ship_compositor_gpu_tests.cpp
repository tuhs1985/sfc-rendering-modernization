#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include "../tools/remix_runtime/ship_triplet_compositor.h"
#include <iostream>
#include <limits>
using namespace ship_triplet;
static unsigned checks=0;
static void check(bool value,const char* message){++checks;if(!value)throw std::runtime_error(message);}
int main(){try{
 ComPtr<ID3D11Device> d;ComPtr<ID3D11DeviceContext> c;D3D_FEATURE_LEVEL level=D3D_FEATURE_LEVEL_10_1;
 checked(D3D11CreateDevice(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,0,&level,1,D3D11_SDK_VERSION,&d,nullptr,&c),"GPU10_1");
 Compositor compositor(d.Get());Key key{};key.session[0]=1;key.sourceSession[0]=2;key.sourcePid=3;key.owner=key.revision=key.frame=key.resourceEpoch=key.depthConvention=1;
 key.objectId=29;key.pose=key.camera=1;key.width=key.height=8;key.viewport[2]=key.viewport[3]=8;key.asset[0]=1;
 uint32_t colors[64]{},ids[64]{};float depths[64]{};
 for(unsigned i=0;i<64;++i){colors[i]=0xff800000|i;ids[i]=i%3==0?0:i%3==1?29:30;
  const float z[]={.5f,-1234.f,-.1f,1.1f,std::numeric_limits<float>::quiet_NaN(),std::numeric_limits<float>::infinity(),0.f,1.f};depths[i]=z[i%8];}
 std::array<ComPtr<ID3D11Texture2D>,3> textures;std::array<ComPtr<ID3D11ShaderResourceView>,3> ownedViews;
 for(unsigned i=0;i<3;++i){D3D11_TEXTURE2D_DESC t{};t.Width=t.Height=8;t.MipLevels=t.ArraySize=1;t.SampleDesc.Count=1;t.Format=i?DXGI_FORMAT_R32_FLOAT:DXGI_FORMAT_B8G8R8A8_UNORM;t.BindFlags=D3D11_BIND_SHADER_RESOURCE;
  D3D11_SUBRESOURCE_DATA data{};data.pSysMem=i==0?static_cast<const void*>(colors):i==1?static_cast<const void*>(depths):static_cast<const void*>(ids);data.SysMemPitch=32;
  checked(d->CreateTexture2D(&t,&data,&textures[i]),"inputs");checked(d->CreateShaderResourceView(textures[i].Get(),nullptr,&ownedViews[i]),"views");}
 ID3D11ShaderResourceView* views[]={ownedViews[0].Get(),ownedViews[1].Get(),ownedViews[2].Get()};
 for(unsigned size:{16u,24u}){
  D3D11_TEXTURE2D_DESC t{};t.Width=t.Height=size;t.MipLevels=t.ArraySize=1;t.Format=DXGI_FORMAT_B8G8R8A8_UNORM;t.SampleDesc.Count=1;t.BindFlags=D3D11_BIND_RENDER_TARGET;
  ComPtr<ID3D11Texture2D> target,staging;ComPtr<ID3D11RenderTargetView> rtv;
  checked(d->CreateTexture2D(&t,nullptr,&target),"target");checked(d->CreateRenderTargetView(target.Get(),nullptr,&rtv),"RTV");
  t.BindFlags=0;t.Usage=D3D11_USAGE_STAGING;t.CPUAccessFlags=D3D11_CPU_ACCESS_READ;checked(d->CreateTexture2D(&t,nullptr,&staging),"readback");
  D3D11_BLEND_DESC blend{};blend.RenderTarget[0].RenderTargetWriteMask=7;ComPtr<ID3D11BlendState> bs;checked(d->CreateBlendState(&blend,&bs),"blend");
  D3D11_DEPTH_STENCIL_DESC depth{};depth.DepthEnable=TRUE;depth.DepthWriteMask=D3D11_DEPTH_WRITE_MASK_ALL;depth.DepthFunc=D3D11_COMPARISON_GREATER;
  ComPtr<ID3D11DepthStencilState> ds;checked(d->CreateDepthStencilState(&depth,&ds),"depth");
  D3D11_RASTERIZER_DESC raster{};raster.FillMode=D3D11_FILL_WIREFRAME;raster.CullMode=D3D11_CULL_FRONT;raster.ScissorEnable=TRUE;
  ComPtr<ID3D11RasterizerState> rs;checked(d->CreateRasterizerState(&raster,&rs),"raster");
  const float factor[]={.1f,.2f,.3f,.4f};c->OMSetBlendState(bs.Get(),factor,0xabcdef);c->OMSetDepthStencilState(ds.Get(),42);c->RSSetState(rs.Get());
  const D3D11_RECT scissor{1,2,3,4};c->RSSetScissorRects(1,&scissor);
  const float bg[]={17.f/255,35.f/255,51.f/255,1};c->ClearRenderTargetView(rtv.Get(),bg);
  const D3D11_VIEWPORT viewport{4,4,8,8,0,1};check(compositor.draw(rtv.Get(),views,key,viewport),"draw");
  ComPtr<ID3D11BlendState> gotBlend;float gotFactor[4]{};UINT mask=0;c->OMGetBlendState(&gotBlend,gotFactor,&mask);
  check(gotBlend.Get()==bs.Get()&&!memcmp(gotFactor,factor,sizeof(factor))&&mask==0xabcdef,"blend/factors/mask restored");
  ComPtr<ID3D11DepthStencilState> gotDepth;UINT reference=0;c->OMGetDepthStencilState(&gotDepth,&reference);check(gotDepth.Get()==ds.Get()&&reference==42,"depth restored");
  ComPtr<ID3D11RasterizerState> gotRaster;c->RSGetState(&gotRaster);check(gotRaster.Get()==rs.Get(),"raster restored");
  D3D11_RECT gotScissor{};UINT count=1;c->RSGetScissorRects(&count,&gotScissor);check(count==1&&!memcmp(&gotScissor,&scissor,sizeof(scissor)),"scissor restored");
  auto invalid=viewport;invalid.TopLeftX=std::numeric_limits<float>::quiet_NaN();check(!compositor.draw(rtv.Get(),views,key,invalid),"nonfinite viewport rejected");
  invalid=viewport;invalid.Width=1921;check(!compositor.draw(rtv.Get(),views,key,invalid),"oversize rejected");
  invalid=viewport;invalid.TopLeftX=static_cast<float>(size);check(!compositor.draw(rtv.Get(),views,key,invalid),"out of target rejected");
  auto wrong=key;wrong.objectId=0;check(!compositor.draw(rtv.Get(),views,wrong,viewport),"invalid key rejected");
  check(!compositor.draw(nullptr,views,key,viewport),"missing target rejected");
  c->CopyResource(staging.Get(),target.Get());c->Flush();D3D11_MAPPED_SUBRESOURCE pixels{};checked(c->Map(staging.Get(),0,D3D11_MAP_READ,0,&pixels),"offline map");
  bool exact=true;unsigned affected=0;
  for(unsigned y=0;y<size;++y)for(unsigned x=0;x<size;++x){uint32_t expected=0xff112333;
   if(x>=4&&x<12&&y>=4&&y<12){const auto i=(y-4)*8+x-4;if(ids[i]==29&&std::isfinite(depths[i])&&depths[i]>=0&&depths[i]<=1){expected=colors[i];++affected;}}
   uint32_t actual=0;memcpy(&actual,static_cast<const BYTE*>(pixels.pData)+size_t(y)*pixels.RowPitch+x*4,4);exact&=actual==expected;}
  c->Unmap(staging.Get(),0);check(exact&&affected>0,"exact mask/color,foreign owner/bad depth discarded,background unchanged");
 }
 c->ClearState();std::cout<<"SHIP_COMPOSITOR_GPU_PASS checks="<<checks<<" feature10_1=1 sizes=2\n";return 0;
}catch(const std::exception& e){std::cerr<<"SHIP_COMPOSITOR_GPU_FAIL "<<e.what()<<"\n";return 1;}}
