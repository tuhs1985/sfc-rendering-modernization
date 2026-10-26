// Owned renderer/receiver workers ONLY. Never wait from an SFC callback.
// Event completion avoids millisecond query-poll sleeps between GPU stages.
#pragma once
#include <d3d11_4.h>
#include <wrl/client.h>
#include <stdexcept>
#include "asset_service.h"
struct WorkerGpuFence {
 Microsoft::WRL::ComPtr<ID3D11Fence> fence;
 Microsoft::WRL::ComPtr<ID3D11DeviceContext4> context;
 HANDLE event=nullptr;uint64_t sequence=0;
 ~WorkerGpuFence(){if(event)CloseHandle(event);}
 void start(ID3D11Device* device,ID3D11DeviceContext* immediate){
  Microsoft::WRL::ComPtr<ID3D11Device5> modern;
  if(FAILED(device->QueryInterface(IID_PPV_ARGS(&modern)))||FAILED(immediate->QueryInterface(IID_PPV_ARGS(&context)))||
     FAILED(modern->CreateFence(0,D3D11_FENCE_FLAG_NONE,IID_PPV_ARGS(&fence))))throw std::runtime_error("Worker GPU completion event unavailable");
  event=CreateEventW(nullptr,FALSE,FALSE,nullptr);if(!event)throw std::runtime_error("Worker GPU completion event creation");
 }
 void wait(AssetService* service=nullptr){
  if(!fence||!event||sequence==UINT64_MAX)throw std::runtime_error("Worker GPU fence lifecycle");
  ++sequence;
  if(FAILED(context->Signal(fence.Get(),sequence))||FAILED(fence->SetEventOnCompletion(sequence,event)))throw std::runtime_error("Worker GPU fence signal");
  context->Flush();
  if(!service||!service->enabled){
   if(WaitForSingleObject(event,5000)!=WAIT_OBJECT_0)throw std::runtime_error("Worker GPU completion5s deadline");
  }else{
   const auto deadline=GetTickCount64()+5000;
   for(;;){
    const auto ready=WaitForSingleObject(event,0);if(ready==WAIT_OBJECT_0)break;
    if(ready!=WAIT_TIMEOUT||GetTickCount64()>=deadline)throw std::runtime_error("Worker GPU completion5s deadline");
    service->tick(AssetService::Postprocess);
    const auto result=WaitForSingleObject(event,1);if(result==WAIT_OBJECT_0)break;
    if(result!=WAIT_TIMEOUT)throw std::runtime_error("Worker GPU event failure");
   }
  }
  const auto complete=fence->GetCompletedValue();
  if(complete==UINT64_MAX||complete<sequence)throw std::runtime_error("Worker GPU fence incomplete/device removed");
 }
};
