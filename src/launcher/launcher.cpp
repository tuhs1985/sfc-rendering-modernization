// Application entry point. No PowerShell, PATH lookup or system installation.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <shellapi.h>
#include <shlobj.h>
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>

namespace {
constexpr wchar_t ReadyVariable[]=L"SFC_RELEASE_STARTUP_EVENT";
// Wait in this order so readiness and newer stages take precedence.
constexpr const wchar_t* StartupEvents[]{
 ReadyVariable,L"SFC_RELEASE_STARTUP_STAGE_4",L"SFC_RELEASE_STARTUP_STAGE_3",L"SFC_RELEASE_STARTUP_STAGE_2"
};
constexpr const wchar_t* StageLabels[]{
 L"Checking package files",L"Preparing the game copy",L"Starting Remix",L"Waiting for SFC graphics"
};

class StartupStatus {
 HANDLE events_[4]{};
 HWND window_=nullptr;
 unsigned stage_=1;
 ULONGLONG stageStart_=0;

 void hide(){
  if(window_){DestroyWindow(window_);window_=nullptr;}
 }

 void refresh(ULONGLONG seconds){
  const auto label=L"SFCRemix   |   Step "+std::to_wstring(stage_)+L" of 4   |   "+
                   StageLabels[stage_-1]+L" ("+std::to_wstring(seconds)+L"s)";
  SetWindowTextW(window_,label.c_str());
 }

public:
 explicit StartupStatus(bool show){
  if(!show)return;
  MONITORINFO monitor{};
  monitor.cbSize=sizeof(monitor);
  const auto display=MonitorFromWindow(GetForegroundWindow(),MONITOR_DEFAULTTOPRIMARY);
  if(!GetMonitorInfoW(display,&monitor)&&!SystemParametersInfoW(SPI_GETWORKAREA,0,&monitor.rcWork,0))return;
  const auto& work=monitor.rcWork;
  constexpr int width=400,height=56;
  const auto instance=GetModuleHandleW(nullptr);
  window_=CreateWindowExW(WS_EX_TOOLWINDOW|WS_EX_TOPMOST|WS_EX_NOACTIVATE,L"STATIC",
                         nullptr,WS_POPUP|WS_BORDER|SS_CENTER|SS_CENTERIMAGE,
                         work.left+(work.right-work.left-width)/2,work.top+(work.bottom-work.top-height)/2,
                         width,height,nullptr,nullptr,instance,nullptr);
  if(!window_)return;
  SECURITY_ATTRIBUTES security{sizeof(security),nullptr,TRUE};
  for(unsigned i=0;i<4;++i){
   events_[i]=CreateEventW(&security,FALSE,FALSE,nullptr);
   if(!events_[i]){hide();return;}
   const auto handle=std::to_wstring(reinterpret_cast<UINT_PTR>(events_[i]));
   if(!SetEnvironmentVariableW(StartupEvents[i],handle.c_str())){hide();return;}
  }
  stageStart_=GetTickCount64();
  refresh(0);
  SendMessageW(window_,WM_SETFONT,reinterpret_cast<WPARAM>(GetStockObject(DEFAULT_GUI_FONT)),TRUE);
  ShowWindow(window_,SW_SHOWNOACTIVATE);
  UpdateWindow(window_);
 }
 ~StartupStatus(){
  hide();
  for(const auto event:events_)if(event)CloseHandle(event);
 }
 void clearChildEnvironment(){
  for(unsigned i=0;i<4;++i)if(events_[i])SetEnvironmentVariableW(StartupEvents[i],nullptr);
 }
 void wait(HANDLE child){
  if(window_){
   const HANDLE handles[]{child,events_[0],events_[1],events_[2],events_[3]};
   ULONGLONG shownSeconds=0;
   for(;;){
    const auto elapsed=GetTickCount64()-stageStart_;
    if(elapsed/1000!=shownSeconds){shownSeconds=elapsed/1000;refresh(shownSeconds);}
    const auto state=MsgWaitForMultipleObjects(5,handles,FALSE,static_cast<DWORD>(1000-elapsed%1000),QS_ALLINPUT);
    if(state==WAIT_TIMEOUT)continue;
    if(state==WAIT_OBJECT_0+5){
     MSG message{};
     while(PeekMessageW(&message,nullptr,0,0,PM_REMOVE))DispatchMessageW(&message);
     continue;
    }
    if(state<WAIT_OBJECT_0+2||state>WAIT_OBJECT_0+4)break;
    const auto stage=6-(state-WAIT_OBJECT_0);
    if(stage>stage_){stage_=stage;stageStart_=GetTickCount64();shownSeconds=0;refresh(0);}
   }
   hide();
  }
  WaitForSingleObject(child,INFINITE);
 }
};
}

int wmain(int argc,wchar_t** argv){
 try{
  std::wstring option;
  if(argc==2){
   if(!_wcsicmp(argv[1],L"-Preflight")||!wcscmp(argv[1],L"--preflight"))option=L"--preflight";
   else if(!_wcsicmp(argv[1],L"-Restore")||!wcscmp(argv[1],L"--restore"))option=L"--restore";
   else if(!wcscmp(argv[1],L"--prepare"))option=L"--prepare";
   else if(!wcscmp(argv[1],L"--troubleshoot"))option=L"--troubleshoot";
   else if(!_wcsicmp(argv[1],L"--help")){std::cout<<"SFCRemix-Launch.cmd [--preflight | --prepare | --restore | --troubleshoot]\nDefault: no saved run history. Troubleshooting: up to 5 short reports, 320 KiB total.\n";return 0;}
   else throw std::runtime_error("Unknown option. Use --help for launch options.");
  }else if(argc!=1)throw std::runtime_error("Only one launcher option is supported.");
  wchar_t self[32768]{};const auto count=GetModuleFileNameW(nullptr,self,32768);
  if(!count||count>=32768)throw std::runtime_error("Cannot locate launcher.");
  namespace fs=std::filesystem;const auto package=fs::path(self).parent_path();
  if(CompareStringOrdinal(package.filename().c_str(),-1,L"SFCRemix",-1,TRUE)!=CSTR_EQUAL)throw std::runtime_error("Extract the complete SFCRemix folder beside StarFleetOP.exe.");
  const auto python=package/L"python/python.exe",entry=package/L"code/src/launcher/bootstrap.py";
  if(!fs::is_regular_file(python)||!fs::is_regular_file(entry))throw std::runtime_error("Incomplete package. Extract the complete release again.");
  if(option!=L"--preflight"&&!IsUserAnAdmin()){
   SHELLEXECUTEINFOW elevated{};elevated.cbSize=sizeof(elevated);elevated.fMask=SEE_MASK_NOCLOSEPROCESS|SEE_MASK_NOASYNC|SEE_MASK_FLAG_NO_UI;
   elevated.lpVerb=L"runas";elevated.lpFile=self;elevated.lpParameters=option.c_str();elevated.lpDirectory=package.c_str();elevated.nShow=SW_SHOWNORMAL;
   if(!ShellExecuteExW(&elevated))throw std::runtime_error(GetLastError()==ERROR_CANCELLED?"Administrator request cancelled. No game started.":"Could not start the elevated launcher.");
   WaitForSingleObject(elevated.hProcess,INFINITE);DWORD code=1;GetExitCodeProcess(elevated.hProcess,&code);CloseHandle(elevated.hProcess);
   if(code)std::wcerr<<L"SFCRemix could not finish. Use Troubleshoot.cmd to save a short report.\n";
   return static_cast<int>(code);
  }
  if(!SetEnvironmentVariableW(L"SFC_RELEASE_ROOT",package.c_str()))throw std::runtime_error("Cannot set package context.");
  auto command=L"\""+python.wstring()+L"\" -I -B \""+entry.wstring()+L"\"";
  if(!option.empty())command+=L" "+option;
  STARTUPINFOW startup{};startup.cb=sizeof(startup);PROCESS_INFORMATION child{};
  const bool interactivePlay=option.empty()||option==L"--troubleshoot";
  StartupStatus status(interactivePlay);
  const BOOL created=CreateProcessW(python.c_str(),command.data(),nullptr,nullptr,TRUE,0,nullptr,package.c_str(),&startup,&child);
  status.clearChildEnvironment();
  if(!created)throw std::runtime_error("Could not start the bundled runtime.");
  CloseHandle(child.hThread);status.wait(child.hProcess);DWORD code=1;GetExitCodeProcess(child.hProcess,&code);CloseHandle(child.hProcess);
  if(code)std::cerr<<"SFCRemix could not finish. Check the message above.\n";
  return static_cast<int>(code);
 }catch(const std::exception& e){std::cerr<<"SFCRemix: "<<e.what()<<'\n';return 1;}
}
