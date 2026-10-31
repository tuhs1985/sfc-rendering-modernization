#pragma once
#include <d3dcompiler.h>
#include <cstring>
#include <cmath>
#include "retained_resources.h"

namespace native_foreground {
// Experimental D24S8 reuse: same four bytes/pixel as the existing R32 history
// plane. Not yet selected by production History. Explicit precision conversion.
class MaskedAssembly {
    ComPtr<ID3D11VertexShader> vertex_;
    ComPtr<ID3D11PixelShader> pixel_;
    ComPtr<ID3D11DepthStencilState> hull_, foreground_;
    ComPtr<ID3D11BlendState> opaque_;
    ComPtr<ID3D11RasterizerState> raster_;
    ComPtr<ID3D11Buffer> parameters_;
    struct Parameters {float origin[2],scale[2];UINT owner,width,height,pad;};
    static void check(HRESULT h){if(FAILED(h))throw std::runtime_error("masked foreground setup");}
public:
    explicit MaskedAssembly(ID3D11Device* d) {
        const char* vs="float4 main(uint i:SV_VertexID):SV_Position{float2 p[3]={float2(-1,-1),float2(-1,3),float2(3,-1)};return float4(p[i],0,1);}";
        const char* ps=R"(
Texture2D<float4> color:register(t0);Texture2D<float> hull:register(t1);
Texture2D<float> coverage:register(t2);
cbuffer Params:register(b0){float2 origin;float2 scale;uint owner,width,height,pad;};
struct Output{float4 color:SV_Target;float depth:SV_Depth;};
Output main(float4 p:SV_Position){int2 q=int2(floor((p.xy-origin)*scale));
 if(any(q<0)||q.x>=int(width)||q.y>=int(height))discard;float z=hull.Load(int3(q,0));
 if(asuint(coverage.Load(int3(q,0)))!=owner||!isfinite(z)||z<0||z>1)discard;
 Output o;o.color=float4(color.Load(int3(q,0)).rgb,1);o.depth=z;return o;})";
        ComPtr<ID3DBlob> v,p;
        check(D3DCompile(vs,strlen(vs),nullptr,nullptr,nullptr,"main","vs_4_1",D3DCOMPILE_ENABLE_STRICTNESS,0,&v,nullptr));
        check(D3DCompile(ps,strlen(ps),nullptr,nullptr,nullptr,"main","ps_4_1",D3DCOMPILE_ENABLE_STRICTNESS,0,&p,nullptr));
        check(d->CreateVertexShader(v->GetBufferPointer(),v->GetBufferSize(),nullptr,&vertex_));
        check(d->CreatePixelShader(p->GetBufferPointer(),p->GetBufferSize(),nullptr,&pixel_));
        D3D11_DEPTH_STENCIL_DESC z{};z.DepthEnable=TRUE;z.DepthWriteMask=D3D11_DEPTH_WRITE_MASK_ALL;
        z.DepthFunc=D3D11_COMPARISON_LESS_EQUAL;z.StencilEnable=TRUE;z.StencilReadMask=z.StencilWriteMask=255;
        // Bit2 marks invalid native depth; bit0 marks replaced hull pixels.
        z.StencilReadMask=4;z.StencilWriteMask=1;
        z.FrontFace.StencilFunc=D3D11_COMPARISON_EQUAL;
        z.FrontFace.StencilFailOp=z.FrontFace.StencilDepthFailOp=D3D11_STENCIL_OP_KEEP;
        z.FrontFace.StencilPassOp=D3D11_STENCIL_OP_REPLACE;z.BackFace=z.FrontFace;
        check(d->CreateDepthStencilState(&z,&hull_));
        z.DepthWriteMask=D3D11_DEPTH_WRITE_MASK_ZERO;z.StencilWriteMask=0;z.StencilReadMask=5;
        z.FrontFace.StencilFunc=D3D11_COMPARISON_EQUAL;z.FrontFace.StencilPassOp=D3D11_STENCIL_OP_KEEP;z.BackFace=z.FrontFace;
        check(d->CreateDepthStencilState(&z,&foreground_));
        D3D11_BLEND_DESC b{};b.RenderTarget[0].RenderTargetWriteMask=D3D11_COLOR_WRITE_ENABLE_ALL;
        check(d->CreateBlendState(&b,&opaque_));
        D3D11_RASTERIZER_DESC r{};r.FillMode=D3D11_FILL_SOLID;r.CullMode=D3D11_CULL_NONE;r.DepthClipEnable=TRUE;
        check(d->CreateRasterizerState(&r,&raster_));
        D3D11_BUFFER_DESC params{};params.ByteWidth=sizeof(Parameters);params.BindFlags=D3D11_BIND_CONSTANT_BUFFER;
        check(d->CreateBuffer(&params,nullptr,&parameters_));
    }
    ID3D11DepthStencilState* foregroundState() const {return foreground_.Get();}
    bool record(ID3D11DeviceContext* c,ID3D11RenderTargetView* target,ID3D11DepthStencilView* depth,
                ID3D11ShaderResourceView*const(&views)[3],UINT width,UINT height,UINT owner=1,
                const float* origin=nullptr,const float* scale=nullptr) noexcept {
        if(!c||c->GetType()!=D3D11_DEVICE_CONTEXT_DEFERRED||!target||!depth||
           !views[0]||!views[1]||!views[2]||!width||!height||width>1920||height>1080)return false;
        D3D11_DEPTH_STENCIL_VIEW_DESC z{};depth->GetDesc(&z);
        if(z.Format!=DXGI_FORMAT_D24_UNORM_S8_UINT||z.ViewDimension!=D3D11_DSV_DIMENSION_TEXTURE2D||z.Flags)return false;
        Parameters params{{origin?origin[0]:0,origin?origin[1]:0},{scale?scale[0]:1,scale?scale[1]:1},owner,width,height,0};
        for(unsigned i=0;i<2;++i)if(!std::isfinite(params.origin[i])||!std::isfinite(params.scale[i])||params.scale[i]<=0)return false;
        c->ClearState();c->UpdateSubresource(parameters_.Get(),0,nullptr,&params,0,0);
        auto* constants=parameters_.Get();c->PSSetConstantBuffers(0,1,&constants);
        c->VSSetShader(vertex_.Get(),nullptr,0);c->PSSetShader(pixel_.Get(),nullptr,0);
        c->PSSetShaderResources(0,3,views);c->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);
        c->RSSetState(raster_.Get());D3D11_VIEWPORT v{0,0,float(width),float(height),0,1};c->RSSetViewports(1,&v);
        c->OMSetBlendState(opaque_.Get(),nullptr,~0u);c->OMSetDepthStencilState(hull_.Get(),1);
        c->OMSetRenderTargets(1,&target,depth);c->Draw(3,0);return true;
    }
};
} // namespace native_foreground
