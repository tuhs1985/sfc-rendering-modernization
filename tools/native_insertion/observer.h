#pragma once
#include "probe_wire.h"
#include "../d3d9_proof/game_output_wire.h"
#include <d3d11.h>
#include <wrl/client.h>

namespace native_insertion {
using Microsoft::WRL::ComPtr;
class Observer {
    Store* store_;DWORD session_[4]{};
    ComPtr<ID3D11DeviceContext> context_;
    bool active(){return valid(store_->header,session_,GetCurrentProcessId())&&!store_->header.stopped&&
        store_->header.frame&&store_->header.owner&&thread(store_->header);}
    void output(Event& e,game_output::Pool* pool){
        if(!pool||!game_output::valid(pool->header,session_,GetCurrentProcessId()))return;
        for(auto& slot:pool->slots){
            if(output_wire::state(&slot)!=output_wire::ready)continue;
            const auto sequence=slot.packet.sequence;const auto packet=slot.packet;const auto meta=game_output::metadata(slot);MemoryBarrier();
            if(output_wire::state(&slot)!=output_wire::ready||slot.packet.sequence!=sequence||
               !output_wire::valid(packet,packet.session,pool->header.receiver_pid)||!game_output::valid(meta,session_))continue;
            if(packet.owner!=e.owner||packet.revision!=e.revision||packet.source_frame>UINT32_MAX)continue;
            if(packet.source_frame>=e.outputFrame){e.outputFrame=static_cast<DWORD>(packet.source_frame);
                e.outputSequence=static_cast<DWORD>(sequence);e.outputQpc=packet.published_qpc;e.flags|=1;}
        }
    }
public:
    Observer(ID3D11Device* d,BYTE* base,const DWORD* session):store_(reinterpret_cast<Store*>(base+Offset)){
        memcpy(session_,session,16);d->GetImmediateContext(&context_);
    }
    void draw(uint64_t native,game_output::Pool* pool){
        if(native!=reinterpret_cast<uintptr_t>(context_.Get())||!active())return;
        auto& h=store_->header;if(h.draws++>=2)return; // at most two draws per phase, metadata only
        Event e=context(h,NativeDraw);output(e,pool);
        ComPtr<ID3D11RenderTargetView> target;ComPtr<ID3D11DepthStencilView> depth;context_->OMGetRenderTargets(1,&target,&depth);
        if(target){e.target=reinterpret_cast<uintptr_t>(target.Get());D3D11_RENDER_TARGET_VIEW_DESC v{};target->GetDesc(&v);e.viewFormat=v.Format;
            ComPtr<ID3D11Resource> r;target->GetResource(&r);ComPtr<ID3D11Texture2D> t;if(SUCCEEDED(r.As(&t))){D3D11_TEXTURE2D_DESC d{};t->GetDesc(&d);
                e.width=d.Width;e.height=d.Height;e.targetFormat=d.Format;e.samples=d.SampleDesc.Count;}}
        if(depth){e.depth=reinterpret_cast<uintptr_t>(depth.Get());D3D11_DEPTH_STENCIL_VIEW_DESC v{};depth->GetDesc(&v);e.depthFormat=v.Format;}
        ComPtr<ID3D11DepthStencilState> z;UINT stencil{};context_->OMGetDepthStencilState(&z,&stencil);
        D3D11_DEPTH_STENCIL_DESC desc{};if(z)z->GetDesc(&desc);else{desc.DepthEnable=TRUE;desc.DepthWriteMask=D3D11_DEPTH_WRITE_MASK_ALL;desc.DepthFunc=D3D11_COMPARISON_LESS;}
        e.depthEnabled=desc.DepthEnable;e.depthWrite=desc.DepthWriteMask;e.depthFunc=desc.DepthFunc;
        // One bounded stack sample per phase joins the native queue flush origin.
        if(h.draws==1){void* stack[16]{};const auto count=CaptureStackBackTrace(0,16,stack,nullptr);
            for(unsigned i=0;i<count;++i){const auto p=reinterpret_cast<uintptr_t>(stack[i]);if(p>=0x00400000&&p<0x00760000){e.caller=static_cast<DWORD>(p);break;}}}
        publish(*store_,e);
    }
    void present(game_output::Pool* pool){if(!active())return;Event e=context(store_->header,Present);output(e,pool);publish(*store_,e);
        if(!pool||!game_output::valid(pool->header,session_,GetCurrentProcessId()))return;
        for(auto& slot:pool->slots){if(InterlockedCompareExchange(&slot.state,output_wire::acquired,output_wire::ready)!=output_wire::ready)continue;
            // No GPU resource was read:discard needs no GPU fence or screenshot.
            const auto p=slot.packet;Event discarded=context(store_->header,OutputDiscarded);discarded.outputFrame=static_cast<DWORD>(p.source_frame);
            const auto meta=game_output::metadata(slot);
            discarded.outputSequence=static_cast<DWORD>(p.sequence);discarded.outputQpc=p.published_qpc;
            const bool qualified=output_wire::valid(p,p.session,pool->header.receiver_pid)&&game_output::valid(meta,session_)&&
                p.owner==discarded.owner&&p.revision==discarded.revision&&p.source_frame<=UINT32_MAX;
            discarded.flags=qualified?1u:2u;
            publish(*store_,discarded);if(qualified)++store_->header.outputSamples;InterlockedExchange(&slot.state,output_wire::idle);
        }
    }
};
} // namespace native_insertion
