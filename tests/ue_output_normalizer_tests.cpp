// GPU fixture only: synthetic CPU upload/readback is not runtime transport.
#include "../src/rendering/ue/ue_output_normalizer.h"
#include <windows.h>
#include <cstdio>
#include <vector>
using Microsoft::WRL::ComPtr;
using sfc_ue_output::Normalizer;
void need(bool ok,const char* why){if(!ok)throw std::runtime_error(why);}
void hr(HRESULT value){need(SUCCEEDED(value),"GPU fixture operation");}
unsigned check_extent(Normalizer& normalizer,ID3D11Device* device,ID3D11DeviceContext* context,
                      UINT Width,UINT Height,UINT TargetWidth,UINT TargetHeight,UINT X,UINT Y,UINT frames){
    std::array<ComPtr<ID3D11Texture2D>,3> targets,staging;
    ID3D11Texture2D* destinations[3]{};
    for(UINT i=0;i<3;++i){
        D3D11_TEXTURE2D_DESC d{};d.Width=TargetWidth;d.Height=TargetHeight;
        d.MipLevels=d.ArraySize=d.SampleDesc.Count=1;
        d.Format=i?DXGI_FORMAT_R32_FLOAT:DXGI_FORMAT_B8G8R8A8_UNORM;d.BindFlags=D3D11_BIND_RENDER_TARGET;
        hr(device->CreateTexture2D(&d,nullptr,&targets[i]));destinations[i]=targets[i].Get();
        d.BindFlags=0;d.Usage=D3D11_USAGE_STAGING;d.CPUAccessFlags=D3D11_CPU_ACCESS_READ;
        hr(device->CreateTexture2D(&d,nullptr,&staging[i]));
    }
    auto output=normalizer.bind_targets(destinations);
    unsigned checked=0;
    for(UINT frame=1;frame<=frames;++frame){
        const UINT owner=frame==frames?0xffffffffu:0x12345670u+frame;
        std::vector<uint32_t> colours(Width*Height);std::vector<float> depths(Width*Height);
        for(UINT i=0;i<Width*Height;++i){
            colours[i]=i==0?0xff000000u:(0xff000000u|(frame*31u<<16)|(i*3u));
            depths[i]=i%5?float(100+frame+i):0.f;
        }
        depths[0]=120; // Opaque black must retain coverage.
        ComPtr<ID3D11Texture2D> colour,linear;
        D3D11_TEXTURE2D_DESC d{};d.Width=Width;d.Height=Height;
        d.MipLevels=d.ArraySize=d.SampleDesc.Count=1;d.BindFlags=D3D11_BIND_SHADER_RESOURCE;
        d.Format=DXGI_FORMAT_B8G8R8A8_UNORM;
        D3D11_SUBRESOURCE_DATA bytes{colours.data(),Width*4,0};hr(device->CreateTexture2D(&d,&bytes,&colour));
        d.Format=DXGI_FORMAT_R32_FLOAT;bytes.pSysMem=depths.data();hr(device->CreateTexture2D(&d,&bytes,&linear));
        auto input=normalizer.bind_inputs(colour.Get(),linear.Get());
        bool rejected=false;
        try{normalizer.draw(context,input,output,UINT32_MAX,Y,-1.0000666f,-2.0000668f,owner);}
        catch(const std::runtime_error&){rejected=true;}need(rejected,"Invalid viewport accepted");
        normalizer.draw(context,input,output,X,Y,-1.0000666f,-2.0000668f,owner);
        for(UINT i=0;i<3;++i)context->CopyResource(staging[i].Get(),targets[i].Get());
        context->Flush();
        for(UINT plane=0;plane<3;++plane){
            D3D11_MAPPED_SUBRESOURCE map{};hr(context->Map(staging[plane].Get(),0,D3D11_MAP_READ,0,&map));
            bool good=true;
            for(UINT y=0;y<TargetHeight;++y)for(UINT x=0;x<TargetWidth;++x){
                const bool inside=x>=X&&y>=Y&&x<X+Width&&y<Y+Height;
                const UINT index=inside?(y-Y)*Width+(x-X):0;
                const float nativeZ=depths[index]>0?1.0000666f-2.0000668f/depths[index]:-1234.f;
                const bool covered=inside&&depths[index]>0&&nativeZ>=0&&nativeZ<1;
                const auto bits=reinterpret_cast<const uint32_t*>(static_cast<const uint8_t*>(map.pData)+y*map.RowPitch)[x];
                if(plane==0)good&=bits==(inside?colours[index]:0);
                else if(plane==2)good&=bits==(covered?owner:0);
                else{
                    float actual;std::memcpy(&actual,&bits,4);
                    const float expected=covered?nativeZ:-1234.f;
                    good&=std::abs(actual-expected)<1e-6f;
                }
                ++checked;
            }
            context->Unmap(staging[plane].Get(),0);need(good,"Wrong normalized pixels/coverage/depth");
        }
    }
    std::printf("PASS %u GPU pixel checks: %ux%u at %u,%u in %ux%u; %u changing frames\n",checked,Width,Height,X,Y,TargetWidth,TargetHeight,frames);
    return checked;
}
int main(){try{
    ComPtr<ID3D11Device> device;ComPtr<ID3D11DeviceContext> context;
    hr(D3D11CreateDevice(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,0,nullptr,0,D3D11_SDK_VERSION,&device,nullptr,&context));
    Normalizer normalizer(device.Get());
    const auto a=check_extent(normalizer,device.Get(),context.Get(),11,7,19,13,3,2,4);
    const auto b=check_extent(normalizer,device.Get(),context.Get(),1280,360,1280,720,0,180,2);
    const auto c=check_extent(normalizer,device.Get(),context.Get(),1720,1020,1920,1080,200,30,2);
    std::printf("PASS total %u GPU pixel checks; target recreation reuses one normalizer, margins, opaque black and exact owner bits\n",a+b+c);
    return 0;
}catch(const std::exception& error){std::fprintf(stderr,"%s\n",error.what());return 1;}}
