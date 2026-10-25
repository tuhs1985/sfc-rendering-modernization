#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <bcrypt.h>
#include <detours.h>
#include <iostream>
#include <string>
#include <vector>
#include <stdexcept>
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
    if(!fixture)throw std::runtime_error("survey standalone fixture only");
    const auto client=full(argv[2]),component=full(argv[3]);
    const auto slash=client.find_last_of(L"\\/");if(slash==std::wstring::npos)throw std::runtime_error("launcher directory");const auto directory=client.substr(0,slash);
    if(fixture){if(client.substr(slash+1)!=L"d3d11_return_fixture.exe"||client.find(L"\\artifacts\\remix-runtime\\runs\\")==std::wstring::npos)throw std::runtime_error("not an owned fixture");}
    else if(CompareStringOrdinal(client.c_str(),-1,L"C:\\Project\\SFC-Remix-Return-Test\\StarFleetOP.exe",-1,TRUE)!=CSTR_EQUAL)throw std::runtime_error("not the approved copied client");
    const auto expectedClient=ascii(argv[4]),expectedComponent=ascii(argv[5]);
    if(expectedClient.size()!=64||expectedComponent.size()!=64||sha256(client)!=expectedClient||sha256(component)!=expectedComponent)throw std::runtime_error("launcher SHA mismatch");
    auto command=L"\""+client+L"\"";const auto dll=ascii(component.c_str());STARTUPINFOW startup{};startup.cb=sizeof(startup);
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
    const auto waited=WaitForSingleObject(child.hProcess,fixture?(idleExperiment?100000:100000):lightTuning?1980000:300000);
    if(waited==WAIT_OBJECT_0){DWORD code=1;GetExitCodeProcess(child.hProcess,&code);std::cout<<"CHILD_EXIT code="<<code<<"\n";result=static_cast<int>(code);}
    else{std::cout<<"CHILD_WAIT_LIMIT original_game_left_running="<<!fixture<<"\n";result=120;}
  }catch(const std::exception& e){std::cout<<"LAUNCH_FAILED "<<e.what()<<" win32="<<GetLastError()<<"\n";if(child.hProcess&&!resumed)TerminateProcess(child.hProcess,97);}
  if(child.hThread)CloseHandle(child.hThread);if(child.hProcess)CloseHandle(child.hProcess);if(job)CloseHandle(job);return result;
}
