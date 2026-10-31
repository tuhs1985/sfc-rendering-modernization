#pragma once
#include "retained_resources.h"
#include <algorithm>
#include <d3d11_1.h>

namespace native_foreground {
// Exact VS/PS draw retention for the bounded indexed-triangle subset. Unsupported
// bindings reject; shaders are retained, never reconstructed from metadata.
struct DrawBindings {
    ComPtr<ID3D11VertexShader> vs;
    ComPtr<ID3D11PixelShader> ps;
    ComPtr<ID3D11InputLayout> layout;
    ComPtr<ID3D11RasterizerState> raster;
    ComPtr<ID3D11BlendState> blend;
    ComPtr<ID3D11DepthStencilState> depth;
    ComPtr<ID3D11Buffer> vb, ib;
    std::array<ComPtr<ID3D11Buffer>,16> constants;
    std::array<ComPtr<ID3D11ShaderResourceView>,16> views;
    std::array<ComPtr<ID3D11SamplerState>,16> samplers;
    D3D11_VIEWPORT viewport[16]{};
    D3D11_RECT scissor[16]{};
    UINT viewCount=16, scissorCount=16, stride{}, vertexOffset{}, indexOffset{};
    UINT sampleMask{}, stencil{};
    FLOAT blendFactor[4]{};
    DXGI_FORMAT indexFormat{};
    bool read(ID3D11DeviceContext* c) noexcept {
        if (!c || c->GetType()!=D3D11_DEVICE_CONTEXT_IMMEDIATE) return false;
        UINT classes=0;
        c->VSGetShader(vs.ReleaseAndGetAddressOf(),nullptr,&classes); if(classes) return false;
        c->PSGetShader(ps.ReleaseAndGetAddressOf(),nullptr,&classes); if(classes) return false;
        ComPtr<ID3D11GeometryShader> gs; ComPtr<ID3D11HullShader> hs; ComPtr<ID3D11DomainShader> ds;
        c->GSGetShader(&gs,nullptr,nullptr); c->HSGetShader(&hs,nullptr,nullptr); c->DSGetShader(&ds,nullptr,nullptr);
        if(gs || hs || ds || !vs || !ps) return false;
        ComPtr<ID3D11Predicate> pred; BOOL predicate{}; c->GetPredication(&pred,&predicate); if(pred) return false;
        ID3D11RenderTargetView* targets[8]{};c->OMGetRenderTargets(8,targets,nullptr);
        bool targetGood=targets[0]!=nullptr;
        if(targets[0]){D3D11_RENDER_TARGET_VIEW_DESC t{};targets[0]->GetDesc(&t);
            targetGood=t.Format==DXGI_FORMAT_R8G8B8A8_UNORM||t.Format==DXGI_FORMAT_B8G8R8A8_UNORM;}
        for(unsigned i=0;i<8;++i)if(targets[i]){if(i)targetGood=false;targets[i]->Release();}
        if(!targetGood)return false;
        ID3D11Buffer* outputs[4]{};c->SOGetTargets(4,outputs);
        bool streamOutput=false;for(auto* output:outputs)if(output){streamOutput=true;output->Release();}
        if(streamOutput)return false;
        // Reject resource-bearing shader stages outside the supported VS/PS set.
        ID3D11ShaderResourceView* vertexViews[128]{};c->VSGetShaderResources(0,128,vertexViews);
        bool vertexResources=false;for(auto* v:vertexViews)if(v){vertexResources=true;v->Release();}
        if(vertexResources)return false;
        for(UINT i=0;i<8;++i) {ComPtr<ID3D11UnorderedAccessView> u; c->OMGetRenderTargetsAndUnorderedAccessViews(0,nullptr,nullptr,i,1,&u); if(u)return false;}
        ID3D11Buffer* vertices[31]{};UINT strides[31]{},offsets[31]{};
        c->IAGetVertexBuffers(1,31,vertices,strides,offsets);bool extraVertices=false;
        for(auto* v:vertices)if(v){extraVertices=true;v->Release();}if(extraVertices)return false;
        D3D11_PRIMITIVE_TOPOLOGY topology{};c->IAGetPrimitiveTopology(&topology);
        if(topology!=D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST)return false;
        c->IAGetVertexBuffers(0,1,vb.ReleaseAndGetAddressOf(),&stride,&vertexOffset);
        c->IAGetIndexBuffer(ib.ReleaseAndGetAddressOf(),&indexFormat,&indexOffset);
        if(!vb||!ib||!stride||stride>256||indexFormat!=DXGI_FORMAT_R32_UINT||indexOffset%4)return false;
        c->IAGetInputLayout(layout.ReleaseAndGetAddressOf()); if(!layout)return false;
        c->RSGetState(raster.ReleaseAndGetAddressOf());viewCount=scissorCount=16;
        c->RSGetViewports(&viewCount,viewport);c->RSGetScissorRects(&scissorCount,scissor);
        if(!viewCount||viewCount>16||scissorCount>16)return false;
        c->OMGetBlendState(blend.ReleaseAndGetAddressOf(),blendFactor,&sampleMask);
        c->OMGetDepthStencilState(depth.ReleaseAndGetAddressOf(),&stencil);
        for(UINT i=0;i<14;++i) {
            ComPtr<ID3D11Buffer> a,b; c->VSGetConstantBuffers(i,1,&a);c->PSGetConstantBuffers(i,1,&b);
            if(i>=8) {if(a||b)return false;}
            else {constants[i]=a;constants[8+i]=b;}
        }
        ComPtr<ID3D11DeviceContext1> context1;
        if(SUCCEEDED(c->QueryInterface(IID_PPV_ARGS(&context1)))) {
            UINT first[14]{},length[14]{};
            ID3D11Buffer* returned[14]{};
            context1->VSGetConstantBuffers1(0,14,returned,first,length);
            for(auto* b:returned)if(b)b->Release();
            for(unsigned i=0;i<8;++i)if(constants[i]&&(first[i]||length[i]!=4096))return false;
            context1->PSGetConstantBuffers1(0,14,returned,first,length);
            for(auto* b:returned)if(b)b->Release();
            for(unsigned i=0;i<8;++i)if(constants[8+i]&&(first[i]||length[i]!=4096))return false;
        }
        ID3D11ShaderResourceView* pixelViews[128]{};c->PSGetShaderResources(0,128,pixelViews);
        bool extraViews=false;for(UINT i=0;i<128;++i) {
            if(i<16)views[i].Attach(pixelViews[i]);else if(pixelViews[i]){extraViews=true;pixelViews[i]->Release();}
        }if(extraViews)return false;
        for(UINT i=0;i<16;++i)c->PSGetSamplers(i,1,samplers[i].ReleaseAndGetAddressOf());
        return true;
    }
};

class DrawSnapshot {
    RetainedResources resources_;
    DrawBindings expected_, captured_;
    std::array<ComPtr<ID3D11Texture2D>,3> images_;
    std::array<ComPtr<ID3D11ShaderResourceView>,16> frozenViews_;
    unsigned imageCount_{};
    Identity identity_{};
    UINT count_{},start_{};INT base_{};
    bool prepared_{},sealed_{};
    static void check(HRESULT h) {if(FAILED(h))throw std::runtime_error("native draw preparation");}
public:
    // Worker/setup phase only, never called inside the observed draw callback.
    void prepare(ID3D11Device* d, const DrawBindings& b) {
        if(prepared_)throw std::runtime_error("native draw already prepared");
        expected_=b;resources_.initialize(d);
        auto prep=[&](unsigned i,ID3D11Buffer* buffer,UINT bind) {
            if(!buffer)return;D3D11_BUFFER_DESC desc{};buffer->GetDesc(&desc);
            resources_.prepareBuffer(d,i,desc.ByteWidth,bind);
        };
        prep(0,b.vb.Get(),D3D11_BIND_VERTEX_BUFFER);prep(1,b.ib.Get(),D3D11_BIND_INDEX_BUFFER);
        for(unsigned i=0;i<16;++i)prep(2+i,b.constants[i].Get(),D3D11_BIND_CONSTANT_BUFFER);
        for(unsigned i=0;i<16;++i)if(b.views[i]) {
            ComPtr<ID3D11Resource> r;b.views[i]->GetResource(&r);ComPtr<ID3D11Texture2D> t;
            check(r.As(&t));unsigned slot=0;
            while(slot<imageCount_&&images_[slot].Get()!=t.Get())++slot;
            if(slot==imageCount_) {
                if(imageCount_==images_.size())throw std::runtime_error("native draw image cap");
                D3D11_TEXTURE2D_DESC td{};t->GetDesc(&td);resources_.prepareImage(d,slot,td);
                images_[imageCount_++]=t;
            }
            D3D11_SHADER_RESOURCE_VIEW_DESC view{};b.views[i]->GetDesc(&view);
            resources_.prepareImageView(d,slot,view,&frozenViews_[i]);
        }
        prepared_=true;
    }
    bool capture(ID3D11DeviceContext* c,const Identity& id,UINT count,UINT start,INT base) noexcept {
        if(!prepared_||sealed_||!count||count%3||base<0)return false;
        DrawBindings b;if(!b.read(c))return false;
        if(b.vb.Get()!=expected_.vb.Get()||b.ib.Get()!=expected_.ib.Get())return false;
        for(unsigned i=0;i<16;++i)if(b.constants[i].Get()!=expected_.constants[i].Get()||b.views[i].Get()!=expected_.views[i].Get())return false;
        D3D11_BUFFER_DESC ib{};b.ib->GetDesc(&ib);
        if(uint64_t(b.indexOffset)+uint64_t(start+uint64_t(count))*4>ib.ByteWidth)return false;
        if(!resources_.begin(id))return false;
        bool good=resources_.captureBuffer(c,0,b.vb.Get())&&resources_.captureBuffer(c,1,b.ib.Get());
        for(unsigned i=0;i<16;++i)if(b.constants[i])good=resources_.captureBuffer(c,2+i,b.constants[i].Get())&&good;
        for(unsigned i=0;i<imageCount_;++i)good=resources_.captureImage(c,i,images_[i].Get())&&good;
        if(!good||!resources_.seal()){resources_.finish(c);return false;}
        captured_=b;identity_=id;count_=count;start_=start;base_=base;sealed_=true;return true;
    }
    // Compatibility check only: all views were allocated during setup.
    void prepareViews(ID3D11Device* d,const Identity& id) {
        if(!sealed_||!(id==identity_))throw std::runtime_error("native draw view identity");
        (void)d;
    }
    // Caller supplies a deferred context. ExecuteCommandList(TRUE) preserves
    // native immediate state. Optional depth override adds a qualified mask.
    bool record(ID3D11DeviceContext* deferred,ID3D11RenderTargetView* target,ID3D11DepthStencilView* depthTarget,
                const Identity& id,ID3D11DepthStencilState* depthOverride=nullptr,UINT stencil=0) noexcept {
        if(!sealed_||!(id==identity_)||!deferred||deferred->GetType()!=D3D11_DEVICE_CONTEXT_DEFERRED||!target)return false;
        for(unsigned i=0;i<16;++i)if(expected_.views[i]&&!frozenViews_[i])return false;
        deferred->ClearState();deferred->IASetInputLayout(captured_.layout.Get());
        deferred->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);
        ID3D11Buffer* vb=resources_.buffer(0,id);deferred->IASetVertexBuffers(0,1,&vb,&captured_.stride,&captured_.vertexOffset);
        deferred->IASetIndexBuffer(resources_.buffer(1,id),captured_.indexFormat,captured_.indexOffset);
        deferred->VSSetShader(captured_.vs.Get(),nullptr,0);deferred->PSSetShader(captured_.ps.Get(),nullptr,0);
        for(unsigned i=0;i<8;++i) {
            ID3D11Buffer* vs=resources_.buffer(2+i,id);ID3D11Buffer* ps=resources_.buffer(10+i,id);
            deferred->VSSetConstantBuffers(i,1,&vs);deferred->PSSetConstantBuffers(i,1,&ps);
        }
        for(unsigned i=0;i<16;++i) {
            auto* v=frozenViews_[i].Get();auto* sampler=captured_.samplers[i].Get();
            deferred->PSSetShaderResources(i,1,&v);deferred->PSSetSamplers(i,1,&sampler);
        }
        deferred->RSSetState(captured_.raster.Get());deferred->RSSetViewports(captured_.viewCount,captured_.viewport);
        deferred->RSSetScissorRects(captured_.scissorCount,captured_.scissor);
        deferred->OMSetBlendState(captured_.blend.Get(),captured_.blendFactor,captured_.sampleMask);
        deferred->OMSetDepthStencilState(depthOverride?depthOverride:captured_.depth.Get(),depthOverride?stencil:captured_.stencil);
        deferred->OMSetRenderTargets(1,&target,depthTarget);deferred->DrawIndexed(count_,start_,base_);return true;
    }
    bool finish(ID3D11DeviceContext* c) noexcept {if(!sealed_)return false;if(!resources_.finish(c))return false;sealed_=false;return true;}
    bool tryRecycle(ID3D11DeviceContext* c) noexcept {return resources_.tryRecycle(c);}
    uint64_t bytes() const noexcept {return resources_.bytes();}
    bool available() const noexcept {return !sealed_&&resources_.available();}
};
} // namespace native_foreground
