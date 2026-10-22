// A game-thread Signal and worker-only completion poll. The worker NEVER uses
// the game's immediate context. No event waits,flushes or extra image surfaces.
#pragma once
#include <d3d11_4.h>
#include <wrl/client.h>
#include <atomic>
#include <cstdint>
#include <stdexcept>
namespace game_gpu {
class ReadLease {
 Microsoft::WRL::ComPtr<ID3D11Fence> fence;
 std::atomic<uint64_t> expected{0};uint64_t next=0;
public:
 void prepare(ID3D11Device* device){Microsoft::WRL::ComPtr<ID3D11Device5> d;
  if(FAILED(device->QueryInterface(IID_PPV_ARGS(&d)))||FAILED(d->CreateFence(0,D3D11_FENCE_FLAG_NONE,IID_PPV_ARGS(&fence))))throw std::runtime_error("Buffered GPU read fence unsupported");}
 bool pending()const{return expected.load(std::memory_order_acquire)!=0;}
 void signal(ID3D11DeviceContext4* context){
  if(!fence||pending()||next>=UINT64_MAX-1)throw std::runtime_error("Buffered GPU read lease invalid");
  const auto value=++next;if(FAILED(context->Signal(fence.Get(),value)))throw std::runtime_error("Buffered GPU read signal failed");
  expected.store(value,std::memory_order_release);
 }
 // Exactly one polling worker owns completion/slot release.
 bool retire(){const auto value=expected.load(std::memory_order_acquire);if(!value)return false;
  const auto completed=fence->GetCompletedValue();if(completed==UINT64_MAX)throw std::runtime_error("Buffered GPU read device removed");
  if(completed<value)return false;expected.store(0,std::memory_order_release);return true;
 }
};
}
