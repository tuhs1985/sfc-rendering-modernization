#pragma once
// Consumer-only access to the established native scene mapping. No acknowledgements,
// asset decoding, pointer dereference or UObject access happens here.
#include "source_scene_view.h"
#include "source_target_view.h"
#include <windows.h>
#include <memory>
#include <string>

namespace sfc_source_view {
class Reader {
public:
    Reader()=default;
    Reader(const Reader&)=delete;
    Reader& operator=(const Reader&)=delete;
    ~Reader(){close();}
    bool open(const std::wstring& name,const std::array<uint32_t,4>& session,uint32_t pid){
        close();if(!pid||name.rfind(L"Local\\",0)!=0)return false;
        process_=OpenProcess(SYNCHRONIZE,FALSE,pid);if(!process_)return false;
        mapping_=OpenFileMappingW(FILE_MAP_READ,FALSE,name.c_str());
        if(mapping_)base_=MapViewOfFile(mapping_,FILE_MAP_READ,0,0,MappingBytes);
        if(!base_){close();return false;}
        session_=session;pid_=pid;
        const auto* h=static_cast<const uint32_t*>(base_);
        if(h[0]!=0x31424c53||h[1]!=scene_capacity::Version||h[2]!=MappingBytes||
           std::memcmp(h+4,session_.data(),16)||h[3]>1||!read_only()){
            close();return false;
        }
        return true;
    }
    Status poll(Frame& frame){
        if(!base_||!process_)return Status::InvalidHeader;
        if(WaitForSingleObject(process_,0)!=WAIT_TIMEOUT)return Status::Stopped;
        const auto status=snapshot(base_,MappingBytes,session_,pid_,last_,frame);
        if(status==Status::Ready)last_=frame.sequence;
        return status;
    }
    bool read_only()const{
        MEMORY_BASIC_INFORMATION info{};
        return base_&&VirtualQuery(base_,&info,sizeof(info))==sizeof(info)&&
            (info.Protect&0xff)==PAGE_READONLY&&info.RegionSize>=MappingBytes;
    }
    Status target(NativeTarget& value)const{
        if(!base_||!process_)return Status::InvalidHeader;
        if(WaitForSingleObject(process_,0)!=WAIT_TIMEOUT)return Status::Stopped;
        return sfc_source_view::target(base_,MappingBytes,session_,pid_,value);
    }
    Status catalog(uint32_t index,Asset& result)const{return sfc_source_view::catalog(base_,MappingBytes,index,result);}
    Status owner_state(uint32_t index,Row& result)const{return sfc_source_view::owner_state(base_,MappingBytes,index,result);}
    uint32_t owner_count()const{
        if(!base_)return 0;
        return load(static_cast<const volatile uint32_t*>(base_)[32]);
    }
    void close(){
        if(base_)UnmapViewOfFile(base_);base_=nullptr;
        if(mapping_)CloseHandle(mapping_);mapping_=nullptr;
        if(process_)CloseHandle(process_);process_=nullptr;
        pid_=0;last_=0;session_={};
    }
private:
    HANDLE process_=nullptr,mapping_=nullptr;
    const void* base_=nullptr;
    std::array<uint32_t,4> session_{};
    uint32_t pid_=0;
    uint64_t last_=0;
};
}
