// Optional renderer-thread service. Never installed in SFC or called in a draw.
// A tick may start nonblocking CPU preparation or admit one completed resource;
// the active output packet/surfaces retain their original ownership and state.
#pragma once
#include <windows.h>
#include <cstdint>
#include <stdexcept>
struct AssetService {
 enum Stage:unsigned {Bootstrap,RenderQuery,Postprocess,Peer,Boundary,Count};
 void (*work)(void*)=nullptr;void* context=nullptr;DWORD owner=0;
 bool enabled=false,active=false;uint64_t calls[Count]{},stageTicks[Count]{},ticks=0;
 void start(bool selected,void (*callback)(void*),void* data){
  enabled=selected;owner=GetCurrentThreadId();work=callback;context=data;
  if(enabled&&!work)throw std::runtime_error("Asset service callback missing");
 }
 void tick(Stage stage){
  if(!enabled)return;
  if(GetCurrentThreadId()!=owner||stage>=Count)throw std::runtime_error("Asset service renderer-thread/stage mismatch");
  if(active)return; // Never recursively service a callback.
  struct Drain {bool& value;~Drain(){value=false;}} drain{active};active=true;
  LARGE_INTEGER begin{},end{};QueryPerformanceCounter(&begin);++calls[stage];
  work(context);QueryPerformanceCounter(&end);const auto elapsed=uint64_t(end.QuadPart-begin.QuadPart);ticks+=elapsed;stageTicks[stage]+=elapsed;
 }
};
