#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0A00
#include <windows.h>
#include <filesystem>
#include <fstream>
#include <string>
#include <vector>
#include <thread>
#include <atomic>
#include <iostream>
#include <algorithm>

namespace fs=std::filesystem;
struct Handle {
    HANDLE h=nullptr;
    explicit Handle(HANDLE value=nullptr):h(value){}
    ~Handle(){if(h && h!=INVALID_HANDLE_VALUE)CloseHandle(h);}
    Handle(const Handle&)=delete;Handle& operator=(const Handle&)=delete;
};
std::wstring quote(const std::wstring& s){
    std::wstring out=L"\"";std::size_t slashes=0;
    for(auto c:s){
        if(c==L'\\'){++slashes;continue;}
        out.append(slashes*(c==L'"'?2:1),L'\\');slashes=0;
        if(c==L'"')out+=L'\\';out+=c;
    }
    out.append(slashes*2,L'\\');return out+L'"';
}
int wmain(int argc,wchar_t** argv){
    if(argc<7){std::cerr<<"workdir seconds scratch_bytes log_bytes exe [args...]\n";return 2;}
    try{
        const fs::path work=fs::absolute(argv[1]);
        const auto seconds=std::stoul(argv[2]);const auto max_bytes=std::stoull(argv[3]);
        const auto log_limit=std::stoull(argv[4]);
        // Offline entry still requests180; approved live workflow requests<=300.
        wchar_t tuning[2]{};const bool longTuning=GetEnvironmentVariableW(L"SFC_D3D9_LIVE_TUNING",tuning,2)==1&&tuning[0]==L'1';
        if(seconds<1 || seconds>(longTuning?1980u:300u) || max_bytes<65536 || max_bytes>20000000000ull ||
           log_limit<1024 || log_limit>8ull*1024*1024 || !fs::is_directory(work) || !fs::is_regular_file(argv[5]))return 2;
        const auto log_path=work/L"job-console.log",result_path=work/L"job-result.json";
        if(fs::exists(log_path) || fs::exists(result_path))return 2;
        Handle job(CreateJobObjectW(nullptr,nullptr));if(!job.h)return 3;
        JOBOBJECT_EXTENDED_LIMIT_INFORMATION limits{};
        limits.BasicLimitInformation.LimitFlags=JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
        if(!SetInformationJobObject(job.h,JobObjectExtendedLimitInformation,&limits,sizeof(limits)))return 3;
        SECURITY_ATTRIBUTES sa{sizeof(sa),nullptr,TRUE};HANDLE r=nullptr,w=nullptr;
        if(!CreatePipe(&r,&w,&sa,0))return 3;
        Handle reader(r),writer(w);SetHandleInformation(reader.h,HANDLE_FLAG_INHERIT,0);
        Handle input(CreateFileW(L"NUL",GENERIC_READ,FILE_SHARE_READ|FILE_SHARE_WRITE,&sa,OPEN_EXISTING,0,nullptr));
        if(input.h==INVALID_HANDLE_VALUE)return 3;
        SIZE_T size=0;InitializeProcThreadAttributeList(nullptr,2,0,&size);
        std::vector<unsigned char> storage(size);
        auto* attrs=reinterpret_cast<LPPROC_THREAD_ATTRIBUTE_LIST>(storage.data());
        if(!InitializeProcThreadAttributeList(attrs,2,0,&size))return 3;
        HANDLE inherited[]{writer.h,input.h};
        const bool configured=UpdateProcThreadAttribute(attrs,0,PROC_THREAD_ATTRIBUTE_JOB_LIST,&job.h,sizeof(job.h),nullptr,nullptr) &&
            UpdateProcThreadAttribute(attrs,0,PROC_THREAD_ATTRIBUTE_HANDLE_LIST,inherited,sizeof(inherited),nullptr,nullptr);
        if(!configured){DeleteProcThreadAttributeList(attrs);return 3;}
        STARTUPINFOEXW start{};start.StartupInfo.cb=sizeof(start);start.lpAttributeList=attrs;
        start.StartupInfo.dwFlags=STARTF_USESTDHANDLES|STARTF_USESHOWWINDOW;start.StartupInfo.wShowWindow=SW_HIDE;
        start.StartupInfo.hStdInput=input.h;start.StartupInfo.hStdOutput=writer.h;start.StartupInfo.hStdError=writer.h;
        std::wstring cmd;
        for(int i=5;i<argc;++i){if(i>5)cmd+=L' ';cmd+=quote(argv[i]);}
        PROCESS_INFORMATION process{};
        const auto began=GetTickCount64();
        const BOOL created=CreateProcessW(argv[5],cmd.data(),nullptr,nullptr,TRUE,
            EXTENDED_STARTUPINFO_PRESENT|CREATE_NO_WINDOW,nullptr,work.c_str(),&start.StartupInfo,&process);
        const DWORD launch_error=created?0:GetLastError();DeleteProcThreadAttributeList(attrs);
        if(!created){std::cerr<<"CreateProcess error "<<launch_error<<'\n';return 4;}
        Handle child(process.hProcess),thread(process.hThread);
        CloseHandle(writer.h);writer.h=nullptr;
        std::atomic<unsigned> reason{0};std::atomic<unsigned long long> logged{0};
        std::thread drain([&]{
            std::ofstream out(log_path,std::ios::binary);char buffer[4096];DWORD n=0;
            while(ReadFile(reader.h,buffer,sizeof(buffer),&n,nullptr) && n){
                const auto keep=(std::min)(static_cast<unsigned long long>(n),log_limit-logged.load());
                if(keep)out.write(buffer,static_cast<std::streamsize>(keep));logged+=keep;
                if(!out || keep<n){unsigned expected=0;reason.compare_exchange_strong(expected,!out?24u:20u);TerminateJobObject(job.h,20);}
            }
            out.flush();if(!out){unsigned expected=0;reason.compare_exchange_strong(expected,24);TerminateJobObject(job.h,24);}
        });
        unsigned long long peak=0;bool warning=false;
        for(;;){
            JOBOBJECT_BASIC_ACCOUNTING_INFORMATION accounting{};
            if(!QueryInformationJobObject(job.h,JobObjectBasicAccountingInformation,&accounting,sizeof(accounting),nullptr)){
                reason=24;TerminateJobObject(job.h,24);break;
            }
            unsigned long long bytes=0;
            try{
                for(const auto& entry:fs::recursive_directory_iterator(work)){
                    if(entry.is_symlink())throw std::runtime_error("scratch symlink");
                    if(entry.is_regular_file())bytes+=entry.file_size();
                }
            }catch(...){reason=24;TerminateJobObject(job.h,24);break;}
            peak=(std::max)(peak,bytes);warning|=bytes>=max_bytes*4/5;
            unsigned expected=0;
            if(bytes>max_bytes)reason.compare_exchange_strong(expected,21);
            expected=0;
            if(GetTickCount64()-began>=seconds*1000ull)reason.compare_exchange_strong(expected,22);
            if(reason){TerminateJobObject(job.h,reason);break;}
            if(!accounting.ActiveProcesses)break;
            Sleep(25);
        }
        WaitForSingleObject(child.h,5000);
        // Closing the job kills any remaining owned descendants, never other Kit instances.
        TerminateJobObject(job.h,reason.load());
        drain.join();DWORD code=STILL_ACTIVE;GetExitCodeProcess(child.h,&code);
        JOBOBJECT_BASIC_ACCOUNTING_INFORMATION final{};
        QueryInformationJobObject(job.h,JobObjectBasicAccountingInformation,&final,sizeof(final),nullptr);
        std::ofstream result(result_path);
        result<<"{\"schema\":\"remix.job.v1\",\"pid\":"<<process.dwProcessId
            <<",\"exit_code\":"<<code<<",\"stop_reason\":"<<reason.load()<<",\"elapsed_ms\":"<<GetTickCount64()-began
            <<",\"console_bytes\":"<<logged.load()<<",\"peak_scratch_bytes\":"<<peak
            <<",\"scratch_warning\":"<<(warning?"true":"false")<<",\"remaining_owned_processes\":"<<final.ActiveProcesses<<"}";
        result.flush();return result.good() && !reason && code==0?0:1;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 2;}
}
