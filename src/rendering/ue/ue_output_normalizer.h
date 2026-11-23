#pragma once
// Receiver-owned D3D11 worker. No game callback, waits, readback or file I/O.
// Caller owns source leases, destination slots and GPU completion/publication.
#include <d3d11.h>
#include <d3dcompiler.h>
#include <wrl/client.h>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <stdexcept>
#include "ue_output_contract.h"

namespace sfc_ue_output {
class Normalizer {
    template<class T> using Ptr=Microsoft::WRL::ComPtr<T>;
    Ptr<ID3D11Device> device;
    Ptr<ID3D11VertexShader> vertex;
    Ptr<ID3D11PixelShader> pixel;
    Ptr<ID3D11Buffer> constants;
    Ptr<ID3D11RasterizerState> raster;
    Ptr<ID3D11DepthStencilState> depth;
    Ptr<ID3D11BlendState> blend;
    struct Parameters { float p22,p23;uint32_t owner,pad;int32_t x,y;uint32_t width,height; };
    static void checked(HRESULT hr) { if(FAILED(hr)) throw std::runtime_error("UE output normalization GPU operation failed"); }
public:
    struct Inputs {
        Ptr<ID3D11ShaderResourceView> colour,linear;
        uint32_t width{},height{};
    };
    struct Targets {
        std::array<Ptr<ID3D11RenderTargetView>,3> views;
        uint32_t width{},height{};
    };
    explicit Normalizer(ID3D11Device* source):device(source) {
        if(!source) throw std::runtime_error("Missing normalization device");
        const char* shader=R"(
cbuffer Parameters:register(b0){float p22;float p23;uint owner;uint pad;int2 origin;uint2 extent;};
Texture2D<float4> colour:register(t0);
Texture2D<float> linearDepth:register(t1);
float4 VS(uint id:SV_VertexID):SV_Position {
 return float4(id==2?3:-1,id==1?3:-1,0,1);
}
struct Output {float4 colour:SV_Target0;float depth:SV_Target1;float owner:SV_Target2;};
Output PS(float4 position:SV_Position){
 Output o;int2 p=int2(position.xy)-origin;
 float d=linearDepth.Load(int3(p,0));float z=-p22+p23/d;
 bool covered=isfinite(d)&&d>0&&isfinite(z)&&z>=0&&z<1;
 o.colour=colour.Load(int3(p,0));o.depth=covered?z:-1234;
 o.owner=asfloat(covered?owner:0);return o;
})";
        Ptr<ID3DBlob> vs,ps,error;
        checked(D3DCompile(shader,std::strlen(shader),nullptr,nullptr,nullptr,"VS","vs_5_0",D3DCOMPILE_ENABLE_STRICTNESS,0,&vs,&error));
        checked(D3DCompile(shader,std::strlen(shader),nullptr,nullptr,nullptr,"PS","ps_5_0",D3DCOMPILE_ENABLE_STRICTNESS,0,&ps,&error));
        checked(device->CreateVertexShader(vs->GetBufferPointer(),vs->GetBufferSize(),nullptr,&vertex));
        checked(device->CreatePixelShader(ps->GetBufferPointer(),ps->GetBufferSize(),nullptr,&pixel));
        D3D11_BUFFER_DESC cb{};cb.ByteWidth=sizeof(Parameters);cb.BindFlags=D3D11_BIND_CONSTANT_BUFFER;
        checked(device->CreateBuffer(&cb,nullptr,&constants));
        D3D11_RASTERIZER_DESC rd{};rd.FillMode=D3D11_FILL_SOLID;rd.CullMode=D3D11_CULL_NONE;rd.DepthClipEnable=TRUE;
        checked(device->CreateRasterizerState(&rd,&raster));
        D3D11_DEPTH_STENCIL_DESC dd{};checked(device->CreateDepthStencilState(&dd,&depth));
        D3D11_BLEND_DESC bd{};
        for(auto& target:bd.RenderTarget) target.RenderTargetWriteMask=D3D11_COLOR_WRITE_ENABLE_ALL;
        checked(device->CreateBlendState(&bd,&blend));
    }
    Inputs bind_inputs(ID3D11Texture2D* colour,ID3D11Texture2D* linear) const {
        if(!colour||!linear) throw std::runtime_error("Missing normalization input");
        D3D11_TEXTURE2D_DESC c{},d{};colour->GetDesc(&c);linear->GetDesc(&d);
        auto owned=[&](ID3D11Texture2D* image) {
            Ptr<ID3D11Device> actual;image->GetDevice(&actual);return actual.Get()==device.Get();
        };
        if(!owned(colour)||!owned(linear)||c.Format!=DXGI_FORMAT_B8G8R8A8_UNORM||d.Format!=DXGI_FORMAT_R32_FLOAT||
           !c.Width||!c.Height||c.Width!=d.Width||c.Height!=d.Height||c.MipLevels!=1||d.MipLevels!=1||
           c.ArraySize!=1||d.ArraySize!=1||c.SampleDesc.Count!=1||d.SampleDesc.Count!=1)
            throw std::runtime_error("Normalization source descriptor/device mismatch");
        Inputs result;result.width=c.Width;result.height=c.Height;
        checked(device->CreateShaderResourceView(colour,nullptr,&result.colour));
        checked(device->CreateShaderResourceView(linear,nullptr,&result.linear));return result;
    }
    Targets bind_targets(ID3D11Texture2D* const (&images)[3]) const {
        Targets result;
        for(uint32_t i=0;i<3;++i) {
            if(!images[i]) throw std::runtime_error("Missing normalization destination");
            D3D11_TEXTURE2D_DESC d{};images[i]->GetDesc(&d);
            Ptr<ID3D11Device> actual;images[i]->GetDevice(&actual);
            if(actual.Get()!=device.Get()||!d.Width||!d.Height||d.MipLevels!=1||d.ArraySize!=1||d.SampleDesc.Count!=1||
               d.Format!=(i?DXGI_FORMAT_R32_FLOAT:DXGI_FORMAT_B8G8R8A8_UNORM)||
               (i&&(d.Width!=result.width||d.Height!=result.height)))
                throw std::runtime_error("Normalization destination descriptor/device mismatch");
            result.width=d.Width;result.height=d.Height;
            checked(device->CreateRenderTargetView(images[i],nullptr,&result.views[i]));
        }
        return result;
    }
    void draw(ID3D11DeviceContext* context,const Inputs& input,const Targets& target,
              uint32_t x,uint32_t y,float p22,float p23,uint32_t owner) const {
        Ptr<ID3D11Device> actual;if(context)context->GetDevice(&actual);
        if(actual.Get()!=device.Get()||!input.colour||!input.linear||!owner||!std::isfinite(p22)||
           !std::isfinite(p23)||p23==0||uint64_t(x)+input.width>target.width||uint64_t(y)+input.height>target.height||
           uint64_t(target.width)*target.height*OutputBytesPerPixel>ResourceBudget)
            throw std::runtime_error("Normalization frame/viewport invalid");
        for(const auto& view:target.views) if(!view) throw std::runtime_error("Normalization targets incomplete");
        const Parameters parameters{p22,p23,owner,0,int32_t(x),int32_t(y),input.width,input.height};
        context->UpdateSubresource(constants.Get(),0,nullptr,&parameters,0,0);
        context->ClearState();
        const float black[4]{},empty[4]{-1234,-1234,-1234,-1234};
        context->ClearRenderTargetView(target.views[0].Get(),black);
        context->ClearRenderTargetView(target.views[1].Get(),empty);
        context->ClearRenderTargetView(target.views[2].Get(),black);
        ID3D11RenderTargetView* views[]{target.views[0].Get(),target.views[1].Get(),target.views[2].Get()};
        context->OMSetRenderTargets(3,views,nullptr);context->OMSetDepthStencilState(depth.Get(),0);
        context->OMSetBlendState(blend.Get(),nullptr,0xffffffff);
        const D3D11_VIEWPORT viewport{float(x),float(y),float(input.width),float(input.height),0,1};
        context->RSSetViewports(1,&viewport);context->RSSetState(raster.Get());
        context->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);
        context->VSSetShader(vertex.Get(),nullptr,0);context->PSSetShader(pixel.Get(),nullptr,0);
        ID3D11ShaderResourceView* sources[]{input.colour.Get(),input.linear.Get()};
        context->PSSetShaderResources(0,2,sources);
        auto* cb=constants.Get();context->PSSetConstantBuffers(0,1,&cb);
        context->Draw(3,0);context->ClearState();
    }
};
}
