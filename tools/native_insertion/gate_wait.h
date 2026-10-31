#pragma once
#include "gate_events.h"
namespace native_gate {
// Invoked only by the separate game-thread coordinator, never the recorder or
// graphics notification. A stale/spurious wake never renews the absolute deadline.
template<class TryAcquire> Result acquire(const Ticket& ticket,Store& store,Events& events,HANDLE renderer,TryAcquire tryAcquire){
 auto& h=store.header;auto& r=store.current;
 if(!valid(ticket,h)||ticket.thread!=GetCurrentThreadId()||ticket.frame!=DWORD(h.frame)||!renderer)return Result::Invalid;
 const auto active=InterlockedIncrement(&h.active);struct Drain{Header& h;~Drain(){InterlockedDecrement(&h.active);}}drain{h};
 if(active>h.maxActive)InterlockedExchange(&h.maxActive,active);
 if(active!=1){InterlockedIncrement(&h.invalid);return Result::Invalid;}
 InterlockedIncrement(&h.requests);r.owner=ticket.owner;r.revision=ticket.revision;r.sequence=ticket.sequence;r.hash=ticket.hash;r.offered=ticket.offered;r.entered=now();
 auto finish=[&](Result result){r.outcome=static_cast<DWORD>(result);r.ended=now();
  if(result==Result::Timeout)InterlockedIncrement(&h.misses);
  if(result==Result::Stopped)InterlockedIncrement(&h.stopWakes);return result;};
 HANDLE waits[]{events.stop,renderer,events.ready};
 for(;;){
  if(h.stop||WaitForSingleObject(events.stop,0)==WAIT_OBJECT_0)return finish(Result::Stopped);
  if(!valid(ticket,h)||ticket.frame!=DWORD(h.frame)||ticket.thread!=DWORD(h.thread))return finish(Result::Invalid);
  if(WaitForSingleObject(renderer,0)!=WAIT_TIMEOUT)return finish(Result::Disconnected);
  const auto time=now();if(time>=ticket.deadline)return finish(Result::Timeout);
  if(tryAcquire()){
   // Import/validation itself can overrun. The caller must cancel that lease if
   // the deadline elapsed before the commit decision.
   return finish(now()<ticket.deadline?Result::Acquired:Result::Timeout);
  }
  const auto checked=now();if(checked>=ticket.deadline)return finish(Result::Timeout);const auto remaining=ticket.deadline-checked;
  const auto wake=WaitForMultipleObjects(3,waits,FALSE,waitMilliseconds(remaining,h.frequency));
  if(wake==WAIT_FAILED){InterlockedIncrement(&h.invalid);return finish(Result::Invalid);}
 }
}
}
