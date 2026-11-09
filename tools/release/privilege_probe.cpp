// Assessment only. Reuse the production controller's exact remote-operation
// helpers against a disposable child of THIS executable, never SFC.
#define wmain sfc_controller_unused_main
#include "../m1_component/m1_controller.cpp"
#undef wmain
#include <stdexcept>
static DWORD elevated(HANDLE process){HANDLE token=nullptr;TOKEN_ELEVATION value{};DWORD bytes=0;
 if(!OpenProcessToken(process,TOKEN_QUERY,&token))throw std::runtime_error("token query");
 const bool good=GetTokenInformation(token,TokenElevation,&value,sizeof(value),&bytes)!=FALSE;CloseHandle(token);
 if(!good)throw std::runtime_error("token elevation");return value.TokenIsElevated;}
int wmain(int argc,wchar_t** argv){
 if(argc==3&&!wcscmp(argv[1],L"--child")){HANDLE ready=OpenEventW(EVENT_MODIFY_STATE,FALSE,argv[2]);if(!ready)return 98;SetEvent(ready);CloseHandle(ready);Sleep(15000);return 0;}
 PROCESS_INFORMATION child{};HANDLE process=nullptr,ready=nullptr;void* text=nullptr;int result=1;
 try{
  const auto parentElevation=elevated(GetCurrentProcess());if(parentElevation)throw std::runtime_error("probe requires an unelevated token");
  wchar_t self[1024]{};if(!GetModuleFileNameW(nullptr,self,1024))throw std::runtime_error("self path");
  const auto event=L"Local\\SFCPrivilegeProbe_"+std::to_wstring(GetCurrentProcessId())+L"_"+std::to_wstring(GetTickCount64());
  ready=CreateEventW(nullptr,TRUE,FALSE,event.c_str());if(!ready)throw std::runtime_error("owned startup event");
  auto command=L"\""+std::wstring(self)+L"\" --child "+event;STARTUPINFOW startup{};startup.cb=sizeof(startup);
  if(!CreateProcessW(self,command.data(),nullptr,nullptr,FALSE,CREATE_NO_WINDOW,nullptr,nullptr,&startup,&child))throw std::runtime_error("owned child");
  if(WaitForSingleObject(ready,5000)!=WAIT_OBJECT_0)throw std::runtime_error("owned child startup readiness");
  const DWORD rights=PROCESS_CREATE_THREAD|PROCESS_QUERY_INFORMATION|PROCESS_VM_OPERATION|PROCESS_VM_WRITE|PROCESS_VM_READ|SYNCHRONIZE;
  process=OpenProcess(rights,FALSE,child.dwProcessId);if(!process||elevated(process))throw std::runtime_error("production controller access rights");
  const std::wstring name=L"version.dll";text=remote_string(process,name);if(!text)throw std::runtime_error("production remote string");
  wchar_t readback[32]{};SIZE_T bytes=0;if(!ReadProcessMemory(process,text,readback,(name.size()+1)*2,&bytes)||name!=readback)throw std::runtime_error("remote readback");
  DWORD module=0,freed=0;
  if(!remote_call(process,remote_kernel_proc(child.dwProcessId,"LoadLibraryW"),text,5000,module)||!module)throw std::runtime_error("production remote load");
  const auto observed=remote_module_base(child.dwProcessId,L"version.dll");
  std::cout<<"STANDARD_USER_LOADED returned="<<hex32(module)<<" observed="<<hex32(static_cast<DWORD>(observed))<<'\n';
  if(observed!=module)throw std::runtime_error("remote load did not establish verified module identity");
  const bool called=remote_call(process,remote_kernel_proc(child.dwProcessId,"FreeLibrary"),reinterpret_cast<void*>(static_cast<uintptr_t>(module)),5000,freed);
  std::cout<<"STANDARD_USER_RELEASE call_completed="<<called<<" result="<<hex32(freed)<<'\n';
  if(!called||!freed)throw std::runtime_error("production remote release");
  std::cout<<"STANDARD_USER_CONTROLLER_PASS parent_elevated=0 child_elevated=0 exact_access_mask="<<rights<<" remote_allocate_write_read_load_free=1 sfc_started=0 protection_changed=0\n";result=0;
 }catch(const std::exception& e){std::cerr<<"STANDARD_USER_CONTROLLER_PARTIAL "<<e.what()<<" win32="<<GetLastError()<<'\n';}
 if(text&&process)VirtualFreeEx(process,text,0,MEM_RELEASE);if(process)CloseHandle(process);
 if(child.hProcess){TerminateProcess(child.hProcess,0);WaitForSingleObject(child.hProcess,5000);CloseHandle(child.hProcess);}if(child.hThread)CloseHandle(child.hThread);
 if(ready)CloseHandle(ready);
 return result;
}
