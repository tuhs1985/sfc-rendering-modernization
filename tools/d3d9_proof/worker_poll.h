// Renderer worker only. Private high-resolution wait,not busy spin/global timer.
// Completion still requires the actual D3D9 query;timer is never a GPU fence.
#pragma once
#include <windows.h>
#include <stdexcept>
struct WorkerPoll {
 HANDLE timer=nullptr;unsigned microseconds=250;
 WorkerPoll(){
  wchar_t value[16]{};const auto n=GetEnvironmentVariableW(L"SFC_D3D9_POLL_US",value,16);
  if(n){if(n>=16)throw std::runtime_error("Worker poll option");
   if(wcscmp(value,L"0")==0)microseconds=0;
   else if(wcscmp(value,L"250")!=0)throw std::runtime_error("Worker poll must be0or250us");}
  if(microseconds){timer=CreateWaitableTimerExW(nullptr,nullptr,0x2,TIMER_ALL_ACCESS);
   if(!timer)throw std::runtime_error("Private high-resolution worker timer unavailable");}
 }
 WorkerPoll(const WorkerPoll&)=delete;WorkerPoll& operator=(const WorkerPoll&)=delete;
 ~WorkerPoll(){if(timer)CloseHandle(timer);}
 void pause(){
  if(!microseconds){Sleep(1);return;}
  LARGE_INTEGER due{};due.QuadPart=-static_cast<LONGLONG>(microseconds)*10;
  if(!SetWaitableTimer(timer,&due,0,nullptr,nullptr,FALSE)||WaitForSingleObject(timer,5000)!=WAIT_OBJECT_0)
   throw std::runtime_error("Private worker timer failure");
 }
};
