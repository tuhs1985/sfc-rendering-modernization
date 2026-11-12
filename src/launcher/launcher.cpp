// Application entry point. No PowerShell, PATH lookup or system installation.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <shellapi.h>
#include <shlobj.h>
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>
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
  if(!CreateProcessW(python.c_str(),command.data(),nullptr,nullptr,TRUE,0,nullptr,package.c_str(),&startup,&child))throw std::runtime_error("Could not start the bundled runtime.");
  CloseHandle(child.hThread);WaitForSingleObject(child.hProcess,INFINITE);DWORD code=1;GetExitCodeProcess(child.hProcess,&code);CloseHandle(child.hProcess);
  if(code)std::cerr<<"SFCRemix could not finish. Check the message above.\n";
  return static_cast<int>(code);
 }catch(const std::exception& e){std::cerr<<"SFCRemix: "<<e.what()<<'\n';return 1;}
}
