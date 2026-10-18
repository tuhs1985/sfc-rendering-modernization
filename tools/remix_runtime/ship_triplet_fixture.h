// Standalone-only producer/owned child harness. Never linked into SFC.
#pragma once
#include "ship_triplet_wire.h"
#include <memory>
#include <fstream>
#include <iostream>
namespace ship_triplet {
struct OwnedHandle {HANDLE value=nullptr;~OwnedHandle(){if(value)CloseHandle(value);}};
class Publisher {
 return_path::Mapping mapping{true};Wire* wire=nullptr;
 OwnedHandle job,process;
 Key key{};
 bool reserved=false;
public:
 explicit Publisher(ID3D11Device* device,const uint64_t (&handles)[3]){
  wire=reinterpret_cast<Wire*>(reinterpret_cast<BYTE*>(mapping.state)+Offset);*wire={};
  std::ifstream f("ship-return-request.bin",std::ios::binary);f.read(reinterpret_cast<char*>(&key),sizeof(key));
  if(!f||f.peek()!=EOF)throw std::runtime_error("triplet fixed key input");
  sessionKey(mapping.name,key);if(!validKey(key))throw std::runtime_error("triplet key input");
  std::memcpy(wire->session,key.session,16);wire->creator=GetCurrentProcessId();wire->width=key.width;wire->height=key.height;wire->resourceEpoch=key.resourceEpoch;
  std::memcpy(wire->handles,handles,sizeof(handles));LARGE_INTEGER frequency{};QueryPerformanceFrequency(&frequency);wire->frequency=frequency.QuadPart;
  Microsoft::WRL::ComPtr<IDXGIDevice> dx;Microsoft::WRL::ComPtr<IDXGIAdapter> adapter;DXGI_ADAPTER_DESC desc{};
  if(FAILED(device->QueryInterface(IID_PPV_ARGS(&dx)))||FAILED(dx->GetAdapter(&adapter))||FAILED(adapter->GetDesc(&desc)))throw std::runtime_error("triplet producer LUID");
  wire->adapterLow=desc.AdapterLuid.LowPart;wire->adapterHigh=static_cast<uint32_t>(desc.AdapterLuid.HighPart);
  if(!request(*wire,key))throw std::runtime_error("triplet initial request");store(wire->ready,1);
  job.value=CreateJobObjectW(nullptr,nullptr);if(!job.value)throw std::runtime_error("triplet owned job");
  JOBOBJECT_EXTENDED_LIMIT_INFORMATION limits{};limits.BasicLimitInformation.LimitFlags=JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
  if(!SetInformationJobObject(job.value,JobObjectExtendedLimitInformation,&limits,sizeof(limits)))throw std::runtime_error("triplet job policy");
  wchar_t path[32768]{};const auto n=GetModuleFileNameW(nullptr,path,32768);if(!n||n==32768)throw std::runtime_error("triplet own path");
  std::wstring exe(path);exe.resize(exe.find_last_of(L"\\/")+1);exe+=L"ship_triplet_consumer_x86.exe";
  auto command=L"\""+exe+L"\" \""+mapping.name+L"\"";STARTUPINFOW si{};si.cb=sizeof(si);PROCESS_INFORMATION pi{};
  if(!CreateProcessW(exe.c_str(),command.data(),nullptr,nullptr,FALSE,CREATE_SUSPENDED|CREATE_NO_WINDOW,nullptr,nullptr,&si,&pi))throw std::runtime_error("triplet owned x86 consumer");
  process.value=pi.hProcess;OwnedHandle thread;thread.value=pi.hThread;
  if(!AssignProcessToJobObject(job.value,process.value)){TerminateProcess(process.value,98);throw std::runtime_error("triplet child job");}
  if(ResumeThread(thread.value)==static_cast<DWORD>(-1))throw std::runtime_error("triplet resume");
  wait(wire->consumerPid,-1);std::cout<<"TRIPLET_X86_READY pid="<<load(wire->consumerPid)<<" session_bound=1\n";
 }
 ~Publisher(){if(wire){std::cout<<"TRIPLET_RELEASE published="<<load(wire->sequence)<<" ack="<<load(wire->ack)<<" accepted="<<load(wire->accepted)<<" lease="<<load(wire->lease)<<"\n";store(wire->stop,1);store(mapping.state->stop,1);}
  if(process.value&&WaitForSingleObject(process.value,2000)==WAIT_TIMEOUT&&job.value)TerminateJobObject(job.value,99);}
 void wait(volatile LONG& field,LONG wanted){const auto deadline=GetTickCount64()+5000;
  while(wanted==-1?load(field)==0:load(field)!=wanted){
   if(load(wire->error)||GetTickCount64()>deadline||WaitForSingleObject(process.value,0)==WAIT_OBJECT_0)throw std::runtime_error("triplet child timeout/disconnect");Sleep(1);}}
 // Fixture calls this after the SDK's all-three-output GPU event,not before.
 void reserve(){Key requested{};if(reserved||!begin(*wire,requested)||!same(requested,key))throw std::runtime_error("triplet producer ownership");reserved=true;}
 void offset(float* transform)const{for(unsigned i=0;i<3;++i)transform[i*4+3]+=key.worldOffset[i];}
 void transfer(const uint64_t (&hashes)[3]){
  if(!reserved)throw std::runtime_error("triplet unreserved output");
  if(!publish(*wire,key,hashes,return_path::now()))throw std::runtime_error("triplet publish");
  const auto sequence=load(wire->sequence);wait(wire->ack,sequence);
  if(std::memcmp(wire->consumed,hashes,sizeof(hashes))||load(wire->lease)!=Idle)throw std::runtime_error("triplet consumer differs");
  reserved=false;
  std::cout<<"TRIPLET_X86_EXACT seq="<<sequence<<" owner="<<key.owner<<" revision="<<key.revision<<" frame="<<key.frame<<" outputs=3\n";
 }
 void finish(){store(wire->stop,1);
  if(WaitForSingleObject(process.value,5000)!=WAIT_OBJECT_0)throw std::runtime_error("triplet consumer shutdown");
  DWORD code=1;if(!GetExitCodeProcess(process.value,&code)||code||load(wire->accepted)!=2||load(wire->rejected))throw std::runtime_error("triplet normal exit/counts");
  std::cout<<"TRIPLET_X86_NORMAL_EXIT packets=2 outputs=6 rejected=0 masked_composite=exact state_restored=1\n";}
};
}
