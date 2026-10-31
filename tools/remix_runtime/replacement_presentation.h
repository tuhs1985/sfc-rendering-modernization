// Two pending source pairs + ONE last-complete pre-ReShade image. No readback.
#pragma once
#include "scene_frame_buffer.h"
#include "../d3d9_proof/replacement_transaction.h"
namespace replacement {
class Presentation {
 Microsoft::WRL::ComPtr<ID3D11DeviceContext> context;
 Microsoft::WRL::ComPtr<ID3D11Texture2D> complete;
public:
 scene_frame_buffer::History history;Policy policy;Receipt receipts[2]{};DWORD committedFrame=0;uint64_t committedAt=0;
 Presentation(ID3D11Device* d,ID3D11Texture2D* target,bool foreground=false):history(d,target,true,foreground){
  D3D11_TEXTURE2D_DESC desc{};target->GetDesc(&desc);desc.BindFlags=desc.CPUAccessFlags=desc.MiscFlags=0;desc.Usage=D3D11_USAGE_DEFAULT;
  ship_triplet::checked(d->CreateTexture2D(&desc,nullptr,&complete),"last complete picture");d->GetImmediateContext(&context);
 }
 void native(ID3D11Texture2D* source,DWORD frame,uint64_t time){context->CopyResource(complete.Get(),source);committedFrame=frame;committedAt=time;policy.completed();}
 void commit(unsigned slot,uint64_t /*time*/){auto& f=history.slot(slot);if(!f.valid||f.row[2]<=committedFrame)throw std::runtime_error("Nonmonotonic replacement commit");
  context->CopyResource(complete.Get(),f.color.Get());committedFrame=f.row[2];committedAt=f.captured;policy.completed();
  for(unsigned i=0;i<2;++i)if(history.slot(i).row[2]<=committedFrame)history.slot(i).valid=false;
 }
 void show(ID3D11Texture2D* target){if(!policy.complete)throw std::runtime_error("No complete picture");context->CopyResource(target,complete.Get());}
 unsigned freeSlot(){for(unsigned i=0;i<2;++i)if(!history.slot(i).valid)return i;
  const auto i=history.slot(0).row[2]<history.slot(1).row[2]?0u:1u;history.slot(i).valid=false;return i;
 }
 DWORD oldest() {DWORD frame=0;for(unsigned i=0;i<2;++i){auto& f=history.slot(i);if(f.valid)frame=frame?(std::min)(frame,f.row[2]):f.row[2];}return frame;}
 void discard(){history.reset();}
};
}
