#pragma once
// Standalone fixture only. Real production compositor followed by ordinary
// native far/near geometry and depth-disabled text. No effect capture/replay.
#include "../tools/remix_runtime/ship_replacement_compositor.h"
#include <algorithm>
struct UENativeEffects {
    using Texture=Microsoft::WRL::ComPtr<ID3D11Texture2D>;
    using View=Microsoft::WRL::ComPtr<ID3D11RenderTargetView>;
    Microsoft::WRL::ComPtr<ID3D11Device> device;
    Microsoft::WRL::ComPtr<ID3D11DeviceContext> context;
    Texture native,depth,resolved,readback;
    View target;Microsoft::WRL::ComPtr<ID3D11DepthStencilView> zview;
    Microsoft::WRL::ComPtr<ID3D11VertexShader> vertex;
    Microsoft::WRL::ComPtr<ID3D11PixelShader> farEffect,nearEffect,text;
    Microsoft::WRL::ComPtr<ID3D11DepthStencilState> farState,noDepth;
    Microsoft::WRL::ComPtr<ID3D11RasterizerState> raster;
    Microsoft::WRL::ComPtr<ID3D11BlendState> additive;
    std::unique_ptr<ship_replacement::DepthCompositor> compositor;
    UINT width=0,height=0;uint64_t checkedPixels=0;
    void prepare(ID3D11Device* d,ID3D11DeviceContext* c,UINT w,UINT h){
        device=d;context=c;width=w;height=h;compositor=std::make_unique<ship_replacement::DepthCompositor>(d);
        D3D11_TEXTURE2D_DESC desc{};desc.Width=w;desc.Height=h;desc.ArraySize=desc.MipLevels=1;desc.SampleDesc.Count=8;desc.Format=DXGI_FORMAT_R8G8B8A8_TYPELESS;desc.BindFlags=D3D11_BIND_RENDER_TARGET;
        hr(d->CreateTexture2D(&desc,nullptr,&native),"Native fixture RGBA8 MSAA");
        D3D11_RENDER_TARGET_VIEW_DESC rv{};rv.Format=DXGI_FORMAT_R8G8B8A8_UNORM;rv.ViewDimension=D3D11_RTV_DIMENSION_TEXTURE2DMS;
        hr(d->CreateRenderTargetView(native.Get(),&rv,&target),"Native fixture linear view");
        desc.Format=DXGI_FORMAT_R32_TYPELESS;desc.BindFlags=D3D11_BIND_DEPTH_STENCIL;
        hr(d->CreateTexture2D(&desc,nullptr,&depth),"Native fixture physical D32");
        D3D11_DEPTH_STENCIL_VIEW_DESC dv{};dv.Format=DXGI_FORMAT_D32_FLOAT;dv.ViewDimension=D3D11_DSV_DIMENSION_TEXTURE2DMS;
        hr(d->CreateDepthStencilView(depth.Get(),&dv,&zview),"Native fixture depth view");
        desc.SampleDesc.Count=1;desc.Format=DXGI_FORMAT_R8G8B8A8_UNORM;desc.BindFlags=0;
        hr(d->CreateTexture2D(&desc,nullptr,&resolved),"Native fixture resolve");
        desc.Usage=D3D11_USAGE_STAGING;desc.CPUAccessFlags=D3D11_CPU_ACCESS_READ;
        hr(d->CreateTexture2D(&desc,nullptr,&readback),"Native fixture readback");
        const char* shader=R"(
float4 vs(uint i:SV_VertexID):SV_Position{float2 v[3]={float2(-1,-1),float2(-1,3),float2(3,-1)};return float4(v[i],0,1);}
struct O{float4 c:SV_Target;float z:SV_Depth;};
O farFX(float4 p:SV_Position){O o;o.c=float4(0,1,0,1);o.z=1;return o;}
O nearFX(float4 p:SV_Position){if(uint(p.y)%64>=4)discard;O o;o.c=float4(0,0,.125,0);o.z=0;return o;}
float4 hud(float4 p:SV_Position):SV_Target{if(uint(p.x)%64>=8)discard;return float4(0,1,0,1);}
)";
        Microsoft::WRL::ComPtr<ID3DBlob> vs,ps;
        hr(D3DCompile(shader,strlen(shader),nullptr,nullptr,nullptr,"vs","vs_4_1",D3DCOMPILE_ENABLE_STRICTNESS,0,&vs,nullptr),"Native fixture shader");
        hr(d->CreateVertexShader(vs->GetBufferPointer(),vs->GetBufferSize(),nullptr,&vertex),"Native fixture VS");
        for(unsigned i=0;i<3;++i){ps.Reset();hr(D3DCompile(shader,strlen(shader),nullptr,nullptr,nullptr,i==0?"farFX":i==1?"nearFX":"hud","ps_4_1",D3DCOMPILE_ENABLE_STRICTNESS,0,&ps,nullptr),"Native fixture PS");
            hr(d->CreatePixelShader(ps->GetBufferPointer(),ps->GetBufferSize(),nullptr,i==0?&farEffect:i==1?&nearEffect:&text),"Native fixture pixel shader");}
        D3D11_DEPTH_STENCIL_DESC z{};z.DepthEnable=TRUE;z.DepthFunc=D3D11_COMPARISON_LESS_EQUAL;z.DepthWriteMask=D3D11_DEPTH_WRITE_MASK_ZERO;
        hr(d->CreateDepthStencilState(&z,&farState),"Native fixture depth state");z.DepthEnable=FALSE;hr(d->CreateDepthStencilState(&z,&noDepth),"Native fixture HUD state");
        D3D11_RASTERIZER_DESC r{};r.FillMode=D3D11_FILL_SOLID;r.CullMode=D3D11_CULL_NONE;r.ScissorEnable=r.MultisampleEnable=TRUE;r.DepthClipEnable=TRUE;
        hr(d->CreateRasterizerState(&r,&raster),"Native fixture raster state");
        D3D11_BLEND_DESC b{};auto& t=b.RenderTarget[0];t.BlendEnable=TRUE;t.SrcBlend=t.DestBlend=t.SrcBlendAlpha=t.DestBlendAlpha=D3D11_BLEND_ONE;t.BlendOp=t.BlendOpAlpha=D3D11_BLEND_OP_ADD;t.RenderTargetWriteMask=15;
        hr(d->CreateBlendState(&b,&additive),"Native fixture near blend");
    }
    void draw(ID3D11Texture2D* const (&images)[3],const ship_triplet::Key& key){
        Microsoft::WRL::ComPtr<ID3D11ShaderResourceView> views[3];
        for(unsigned n=0;n<3;++n)hr(device->CreateShaderResourceView(images[n],nullptr,&views[n]),"Native fixture source view");
        ID3D11ShaderResourceView* inputs[]{views[0].Get(),views[1].Get(),views[2].Get()};
        const float black[]{0,0,0,1};context->ClearRenderTargetView(target.Get(),black);context->ClearDepthStencilView(zview.Get(),D3D11_CLEAR_DEPTH,1,0);
        auto* rtv=target.Get();context->OMSetRenderTargets(1,&rtv,zview.Get());
        const D3D11_VIEWPORT viewport{0,0,float(width),float(height),0,1};context->RSSetViewports(1,&viewport);
        const D3D11_RECT full{0,0,LONG(width),LONG(height)};context->RSSetScissorRects(1,&full);context->RSSetState(raster.Get());
        const float factor[]{.1f,.2f,.3f,.4f};context->OMSetBlendState(additive.Get(),factor,0xffffffff);context->OMSetDepthStencilState(farState.Get(),13);
        context->VSSetShader(vertex.Get(),nullptr,0);context->PSSetShader(farEffect.Get(),nullptr,0);context->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);
        need(compositor->draw(target.Get(),zview.Get(),inputs,key,ship_replacement::ImageLayout::NativeTarget),"Native fixture insertion rejected");
        Microsoft::WRL::ComPtr<ID3D11RenderTargetView> restoredTarget;Microsoft::WRL::ComPtr<ID3D11DepthStencilView> restoredDepth;
        context->OMGetRenderTargets(1,&restoredTarget,&restoredDepth);need(restoredTarget.Get()==target.Get()&&restoredDepth.Get()==zview.Get(),"Native targets not restored");
        Microsoft::WRL::ComPtr<ID3D11BlendState> blend;float got[4]{};UINT mask=0;context->OMGetBlendState(&blend,got,&mask);
        need(blend.Get()==additive.Get()&&!memcmp(factor,got,sizeof(got))&&mask==0xffffffff,"Native blend state not restored");
        Microsoft::WRL::ComPtr<ID3D11DepthStencilState> zs;UINT stencil=0;context->OMGetDepthStencilState(&zs,&stencil);need(zs.Get()==farState.Get()&&stencil==13,"Native depth state not restored");
        Microsoft::WRL::ComPtr<ID3D11RasterizerState> rs;context->RSGetState(&rs);need(rs.Get()==raster.Get(),"Native raster state not restored");
        D3D11_VIEWPORT restored{};UINT n=1;context->RSGetViewports(&n,&restored);need(n==1&&!memcmp(&viewport,&restored,sizeof(viewport)),"Native viewport not restored");
        D3D11_RECT rect{};n=1;context->RSGetScissorRects(&n,&rect);need(n==1&&!memcmp(&rect,&full,sizeof(full)),"Native scissor not restored");
        Microsoft::WRL::ComPtr<ID3D11VertexShader> vs;Microsoft::WRL::ComPtr<ID3D11PixelShader> ps;
        context->VSGetShader(&vs,nullptr,nullptr);context->PSGetShader(&ps,nullptr,nullptr);need(vs.Get()==vertex.Get()&&ps.Get()==farEffect.Get(),"Native shaders not restored");
        D3D11_PRIMITIVE_TOPOLOGY topology{};context->IAGetPrimitiveTopology(&topology);need(topology==D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST,"Native topology not restored");
        // All three are ordinary subsequent native draws, not replayed images.
        context->OMSetBlendState(nullptr,nullptr,0xffffffff);context->OMSetDepthStencilState(farState.Get(),0);context->Draw(3,0);
        context->OMSetBlendState(additive.Get(),nullptr,0xffffffff);context->PSSetShader(nearEffect.Get(),nullptr,0);context->Draw(3,0);
        context->OMSetBlendState(nullptr,nullptr,0xffffffff);context->OMSetDepthStencilState(noDepth.Get(),0);context->PSSetShader(text.Get(),nullptr,0);context->Draw(3,0);
        context->OMSetRenderTargets(0,nullptr,nullptr);context->ResolveSubresource(resolved.Get(),0,native.Get(),0,DXGI_FORMAT_R8G8B8A8_UNORM);
        context->CopyResource(readback.Get(),resolved.Get());
    }
    void verify(ID3D11Texture2D* const (&reference)[3],uint32_t owner){
        D3D11_MAPPED_SUBRESOURCE actual{},source[3]{};
        hr(context->Map(readback.Get(),0,D3D11_MAP_READ,0,&actual),"Native completed readback");
        for(unsigned n=0;n<3;++n)hr(context->Map(reference[n],0,D3D11_MAP_READ,0,&source[n]),"Native reference readback");
        unsigned mismatches=0,covered=0;
        for(unsigned y=0;y<height;++y)for(unsigned x=0;x<width;++x){
            const auto id=reinterpret_cast<const uint32_t*>(static_cast<const BYTE*>(source[2].pData)+y*source[2].RowPitch)[x];
            const auto z=reinterpret_cast<const float*>(static_cast<const BYTE*>(source[1].pData)+y*source[1].RowPitch)[x];
            uint32_t expected=0xff00ff00;
            if(id==owner&&std::isfinite(z)&&z>=0&&z<1){
                ++covered;const auto bgra=reinterpret_cast<const uint32_t*>(static_cast<const BYTE*>(source[0].pData)+y*source[0].RowPitch)[x];
                expected=(bgra&0xff00ff00u)|((bgra&0xff)<<16)|((bgra>>16)&0xff)|0xff000000;
            }
            if(y%64<4){const auto blue=(std::min)(255u,((expected>>16)&255)+32);expected=(expected&0xff00ffffu)|(blue<<16);}
            if(x%64<8)expected=0xff00ff00;
            const auto pixel=reinterpret_cast<const uint32_t*>(static_cast<const BYTE*>(actual.pData)+y*actual.RowPitch)[x];
            mismatches+=pixel!=expected;
        }
        context->Unmap(readback.Get(),0);for(unsigned n=0;n<3;++n)context->Unmap(reference[n],0);
        checkedPixels+=uint64_t(width)*height;
        std::printf("UE_NATIVE_EFFECTS mismatches=%u covered=%u pixels=%u\n",mismatches,covered,width*height);
        need(covered>20&&mismatches==0,"Native placement/depth/effect/text ordering mismatch");
    }
};
