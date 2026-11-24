// Actual native target fixture: no SFC/UE launch, no CPU runtime transport.
#include "../tools/remix_runtime/ship_replacement_compositor.h"
#include <cstdio>
#include <vector>
using Microsoft::WRL::ComPtr;
void need(bool ok,const char* why){if(!ok)throw std::runtime_error(why);}
void hr(HRESULT v,const char* why){need(SUCCEEDED(v),why);}
int main(){try{
    ComPtr<ID3D11Device> device;ComPtr<ID3D11DeviceContext> context;
    hr(D3D11CreateDevice(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,0,nullptr,0,D3D11_SDK_VERSION,&device,nullptr,&context),"Fixture device");
    constexpr unsigned W=19,H=13;
    D3D11_TEXTURE2D_DESC d{};d.Width=W;d.Height=H;d.ArraySize=d.MipLevels=1;d.SampleDesc.Count=8;d.Format=DXGI_FORMAT_R8G8B8A8_TYPELESS;d.BindFlags=D3D11_BIND_RENDER_TARGET;
    ComPtr<ID3D11Texture2D> native,depth,resolved,readback;ComPtr<ID3D11RenderTargetView> rtv;ComPtr<ID3D11DepthStencilView> dsv;
    hr(device->CreateTexture2D(&d,nullptr,&native),"Native RGBA8 MSAA target");
    D3D11_RENDER_TARGET_VIEW_DESC rd{};rd.Format=DXGI_FORMAT_R8G8B8A8_UNORM;rd.ViewDimension=D3D11_RTV_DIMENSION_TEXTURE2DMS;
    hr(device->CreateRenderTargetView(native.Get(),&rd,&rtv),"Native linear RTV");
    d.Format=DXGI_FORMAT_R32_TYPELESS;d.BindFlags=D3D11_BIND_DEPTH_STENCIL;
    hr(device->CreateTexture2D(&d,nullptr,&depth),"Native D32 MSAA target");
    D3D11_DEPTH_STENCIL_VIEW_DESC zd{};zd.Format=DXGI_FORMAT_D32_FLOAT;zd.ViewDimension=D3D11_DSV_DIMENSION_TEXTURE2DMS;
    hr(device->CreateDepthStencilView(depth.Get(),&zd,&dsv),"Native DSV");
    d.SampleDesc.Count=1;d.Format=DXGI_FORMAT_R8G8B8A8_UNORM;d.BindFlags=0;
    hr(device->CreateTexture2D(&d,nullptr,&resolved),"Resolve target");
    d.Usage=D3D11_USAGE_STAGING;d.CPUAccessFlags=D3D11_CPU_ACCESS_READ;
    hr(device->CreateTexture2D(&d,nullptr,&readback),"Fixture readback");
    std::vector<uint32_t> colours(W*H),owners(W*H);std::vector<float> zs(W*H,-1234.f);
    for(unsigned y=4;y<8;++y)for(unsigned x=6;x<12;++x){
        const unsigned i=y*W+x;owners[i]=7;zs[i]=.5f;colours[i]=0xff000000u|(x*9u<<16)|(y*11u<<8)|(x+y);
    }
    colours[4*W+7]=0xff000000u; // Black hull markings remain covered.
    ComPtr<ID3D11Texture2D> images[3];ComPtr<ID3D11ShaderResourceView> owned[3];
    d.Usage=D3D11_USAGE_DEFAULT;d.CPUAccessFlags=0;d.BindFlags=D3D11_BIND_SHADER_RESOURCE;
    for(unsigned i=0;i<3;++i){
        d.Format=i?DXGI_FORMAT_R32_FLOAT:DXGI_FORMAT_B8G8R8A8_UNORM;
        D3D11_SUBRESOURCE_DATA bytes{i==0?static_cast<void*>(colours.data()):i==1?static_cast<void*>(zs.data()):static_cast<void*>(owners.data()),W*4,0};
        hr(device->CreateTexture2D(&d,&bytes,&images[i]),"Native-aligned input");hr(device->CreateShaderResourceView(images[i].Get(),nullptr,&owned[i]),"Input SRV");
    }
    ID3D11ShaderResourceView* views[]{owned[0].Get(),owned[1].Get(),owned[2].Get()};
    ship_triplet::Key key{};key.session[0]=key.sourceSession[0]=1;key.sourcePid=17;key.asset[0]=1;
    key.owner=key.revision=key.frame=key.resourceEpoch=key.depthConvention=1;key.objectId=7;key.pose=key.camera=1;
    key.width=W;key.height=H;key.viewport[0]=3;key.viewport[1]=2;key.viewport[2]=11;key.viewport[3]=7;
    ship_replacement::DepthCompositor compositor(device.Get());
    const float clear[]{.1f,.2f,.3f,1};
    context->ClearRenderTargetView(rtv.Get(),clear);context->ClearDepthStencilView(dsv.Get(),D3D11_CLEAR_DEPTH,1,0);
    need(compositor.draw(rtv.Get(),dsv.Get(),views,key,ship_replacement::ImageLayout::NativeTarget),"Native composition refused");
    context->ResolveSubresource(resolved.Get(),0,native.Get(),0,DXGI_FORMAT_R8G8B8A8_UNORM);context->CopyResource(readback.Get(),resolved.Get());
    D3D11_MAPPED_SUBRESOURCE map{};hr(context->Map(readback.Get(),0,D3D11_MAP_READ,0,&map),"Fixture completed pixels");
    unsigned wrong=0;
    for(unsigned y=2;y<9;++y)for(unsigned x=3;x<14;++x){
        if(!owners[y*W+x])continue;
        const auto actual=reinterpret_cast<const uint32_t*>(static_cast<const BYTE*>(map.pData)+y*map.RowPitch)[x];
        const auto bgra=colours[y*W+x];const auto expected=(bgra&0xff00ff00u)|((bgra&0xff)<<16)|((bgra>>16)&0xff);
        wrong+=actual!=expected;
    }
    context->Unmap(readback.Get(),0);std::printf("NATIVE_TARGET_PLACEMENT mismatched_covered_pixels=%u\n",wrong);
    need(wrong==0,"Full-native UE images were remapped a second time");
    std::puts("PASS native-aligned tactical placement and opaque black coverage");return 0;
}catch(const std::exception& e){std::fprintf(stderr,"%s\n",e.what());return 1;}}
