#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <bcrypt.h>
#include <detours.h>
#include <iostream>
#include <string>
#include <vector>
#include <stdexcept>
#include "launch_paths.h"
#include "../d3d9_proof/pipeline_mode.h"
static std::wstring full(const wchar_t* input){wchar_t value[1024]{};const auto n=GetFullPathNameW(input,1024,value,nullptr);if(!n||n>=1024)throw std::runtime_error("launcher path bound");return value;}
static std::string sha256(const std::wstring& path){
  HANDLE file=CreateFileW(path.c_str(),GENERIC_READ,FILE_SHARE_READ,nullptr,OPEN_EXISTING,FILE_FLAG_SEQUENTIAL_SCAN,nullptr);
  if(file==INVALID_HANDLE_VALUE)throw std::runtime_error("launcher hash file");
  BCRYPT_ALG_HANDLE algorithm=nullptr;BCRYPT_HASH_HANDLE hash=nullptr;std::string result;
  try{
    if(BCryptOpenAlgorithmProvider(&algorithm,BCRYPT_SHA256_ALGORITHM,nullptr,0)<0)throw std::runtime_error("SHA algorithm");
    DWORD size=0,n=0;if(BCryptGetProperty(algorithm,BCRYPT_OBJECT_LENGTH,reinterpret_cast<PUCHAR>(&size),sizeof(size),&n,0)<0||size>1024*1024)throw std::runtime_error("SHA object");
    std::vector<unsigned char> object(size),buffer(65536);unsigned char digest[32]{};
    if(BCryptCreateHash(algorithm,&hash,object.data(),size,nullptr,0,0)<0)throw std::runtime_error("SHA create");
    do{if(!ReadFile(file,buffer.data(),static_cast<DWORD>(buffer.size()),&n,nullptr))throw std::runtime_error("SHA read");if(n&&BCryptHashData(hash,buffer.data(),n,0)<0)throw std::runtime_error("SHA update");}while(n);
    if(BCryptFinishHash(hash,digest,sizeof(digest),0)<0)throw std::runtime_error("SHA finish");
    constexpr char hex[]="0123456789ABCDEF";for(const auto byte:digest){result.push_back(hex[byte>>4]);result.push_back(hex[byte&15]);}
  }catch(...){if(hash)BCryptDestroyHash(hash);if(algorithm)BCryptCloseAlgorithmProvider(algorithm,0);CloseHandle(file);throw;}
  BCryptDestroyHash(hash);BCryptCloseAlgorithmProvider(algorithm,0);CloseHandle(file);return result;
}
static std::string ascii(const wchar_t* value){std::string out;for(;*value;++value){if(*value>127)throw std::runtime_error("loader requires bounded ASCII DLL/hash path");out.push_back(static_cast<char>(*value));}return out;}
int wmain(int argc,wchar_t** argv){
  std::cout.setf(std::ios::unitbuf);if(argc!=6)return 2;
  PROCESS_INFORMATION child{};HANDLE job=nullptr;bool resumed=false;int result=1;
  try{
    const bool fixture=!wcscmp(argv[1],L"--fixture");
    const bool checkOnly=!wcscmp(argv[1],L"--check-game");
    if(!fixture&&!checkOnly&&wcscmp(argv[1],L"--game"))throw std::runtime_error("launcher mode");
    const auto client=full(argv[2]),component=full(argv[3]);
    const auto slash=client.find_last_of(L"\\/");if(slash==std::wstring::npos)throw std::runtime_error("launcher directory");const auto directory=client.substr(0,slash);
    wchar_t root[1024]{},self[1024]{};const auto rootSize=GetEnvironmentVariableW(L"SFC_RELEASE_ROOT",root,1024);
    if(rootSize>=1024||!GetModuleFileNameW(nullptr,self,1024))throw std::runtime_error("launcher package path bound");
    launch_paths::validate(client,component,self,root,fixture);
    const auto expectedClient=ascii(argv[4]),expectedComponent=ascii(argv[5]);
    if(expectedClient.size()!=64||expectedComponent.size()!=64||sha256(client)!=expectedClient||sha256(component)!=expectedComponent)throw std::runtime_error("launcher SHA mismatch");
    if(!fixture&&expectedClient!="4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29")throw std::runtime_error("unsupported SFC executable pin");
    if(rootSize&&!fixture&&sha256(full((std::wstring(root)+L"/runtime/remix-runtime/return-bin/SFCRemixReturn.dll").c_str()))!=expectedComponent)throw std::runtime_error("mutable component differs from package input");
    const auto dll=launch_paths::preload_name(component,directory);
    if(checkOnly){std::cout<<"LAUNCH_PREFLIGHT_PASS no_process_created=1 package_bound="<<bool(rootSize)<<"\n";return 0;}
    auto command=L"\""+client+L"\"";STARTUPINFOW startup{};startup.cb=sizeof(startup);
    startup.dwFlags=STARTF_USESTDHANDLES;startup.hStdInput=GetStdHandle(STD_INPUT_HANDLE);startup.hStdOutput=GetStdHandle(STD_OUTPUT_HANDLE);startup.hStdError=GetStdHandle(STD_ERROR_HANDLE);
    if(!DetourCreateProcessWithDllExW(client.c_str(),command.data(),nullptr,nullptr,TRUE,CREATE_SUSPENDED,nullptr,directory.c_str(),&startup,&child,dll.c_str(),nullptr))throw std::runtime_error("startup component preload");
    wchar_t observed[1024]{};DWORD count=1024;
    if(!QueryFullProcessImageNameW(child.hProcess,0,observed,&count)||CompareStringOrdinal(client.c_str(),-1,observed,-1,TRUE)!=CSTR_EQUAL||sha256(client)!=expectedClient)throw std::runtime_error("suspended client path/hash verification");
    if(fixture){
      job=CreateJobObjectW(nullptr,nullptr);JOBOBJECT_EXTENDED_LIMIT_INFORMATION limits{};limits.BasicLimitInformation.LimitFlags=JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
      if(!job||!SetInformationJobObject(job,JobObjectExtendedLimitInformation,&limits,sizeof(limits))||!AssignProcessToJobObject(job,child.hProcess))throw std::runtime_error("fixture owned job");
    }
    std::cout<<"VERIFIED_CHILD pid="<<child.dwProcessId<<" suspended_path_match=1 disk_sha_match=1 startup_import_only=1\n";
    if(ResumeThread(child.hThread)==static_cast<DWORD>(-1))throw std::runtime_error("resume verified client");resumed=true;CloseHandle(child.hThread);child.hThread=nullptr;
    wchar_t tuning[4]{};
    const bool lightTuning=GetEnvironmentVariableW(L"SFC_LIGHT_TUNING",tuning,4)==1&&tuning[0]==L'1';
    // Only the explicit standalone menu-idle experiment needs a longer fixture
    // watchdog. Never extend the game or ordinary fixture deadline implicitly.
    wchar_t idle[16]{};const bool idleExperiment=fixture&&GetEnvironmentVariableW(L"SFC_FIXTURE_MENU_IDLE_MS",idle,16)&&!wcscmp(idle,L"60000");
    const auto waited=WaitForSingleObject(child.hProcess,launch_paths::wait_limit(fixture,idleExperiment,lightTuning,pipeline_mode::play_session()));
    if(waited==WAIT_OBJECT_0){DWORD code=1;GetExitCodeProcess(child.hProcess,&code);std::cout<<"CHILD_EXIT code="<<code<<"\n";result=static_cast<int>(code);}
    else{std::cout<<"CHILD_WAIT_LIMIT original_game_left_running="<<!fixture<<"\n";result=120;}
  }catch(const std::exception& e){std::cout<<"LAUNCH_FAILED "<<e.what()<<" win32="<<GetLastError()<<"\n";if(child.hProcess&&!resumed)TerminateProcess(child.hProcess,97);}
  if(child.hThread)CloseHandle(child.hThread);if(child.hProcess)CloseHandle(child.hProcess);if(job)CloseHandle(job);return result;
}
