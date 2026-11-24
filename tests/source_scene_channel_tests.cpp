#include "../src/transport/source_scene_channel.h"
#include "../tools/d3d9_proof/multi_scene_wire.h"
#include "../tools/d3d9_proof/output_target.h"
#include <cstdio>
#include <memory>
#include <stdexcept>
using namespace sfc_source_view;
void need(bool value,const char* why){if(!value)throw std::runtime_error(why);}
int wmain(int argc,wchar_t** argv){try{
    const std::array<uint32_t,4> session{1,2,3,4};
    if(argc==5&&std::wstring(argv[1])==L"--producer"){
        HANDLE map=OpenFileMappingW(FILE_MAP_READ|FILE_MAP_WRITE,FALSE,argv[2]);need(map!=nullptr,"Producer mapping");
        auto* data=static_cast<uint8_t*>(MapViewOfFile(map,FILE_MAP_READ|FILE_MAP_WRITE,0,0,MappingBytes));need(data!=nullptr,"Producer view");
        reinterpret_cast<uint32_t*>(data)[3]=1;
        reinterpret_cast<Store*>(data+SceneOffset)->header.pid=GetCurrentProcessId();
        HANDLE ready=OpenEventW(EVENT_MODIFY_STATE,FALSE,argv[3]);HANDLE stop=OpenEventW(SYNCHRONIZE,FALSE,argv[4]);
        need(ready&&stop,"Producer notifications");SetEvent(ready);need(WaitForSingleObject(stop,5000)==WAIT_OBJECT_0,"Producer stop");
        CloseHandle(ready);CloseHandle(stop);UnmapViewOfFile(data);CloseHandle(map);return 0;
    }
    if(argc==3){
        Reader reader;need(reader.open(argv[1],session,uint32_t(std::stoul(argv[2]))),"Open read-only source");
        auto frame=std::make_unique<Frame>();need(reader.poll(*frame)==Status::Ready&&frame->sequence==41,"Cross-process native frame");
        need(reader.read_only(),"Source mapping permits writes");reader.close();reader.close();return 0;
    }
    const std::wstring name=L"Local\\SFCSourceReadTest-"+std::to_wstring(GetCurrentProcessId());
    HANDLE mapping=CreateFileMappingW(INVALID_HANDLE_VALUE,nullptr,PAGE_READWRITE,0,MappingBytes,name.c_str());
    need(mapping!=nullptr,"Create fixture mapping");
    auto* base=static_cast<uint8_t*>(MapViewOfFile(mapping,FILE_MAP_WRITE|FILE_MAP_READ,0,0,MappingBytes));
    need(base!=nullptr,"Map fixture");
    auto* common=reinterpret_cast<uint32_t*>(base);common[0]=0x31424c53;common[1]=scene_capacity::Version;common[2]=MappingBytes;
    std::memcpy(common+4,session.data(),16);
    auto* native=new(base+SceneOffset)multi_scene::Store();native->header.bytes=sizeof(*native);std::memcpy(native->header.session,session.data(),16);
    Reader reader;need(reader.open(name,session,GetCurrentProcessId())&&reader.read_only(),"Read-only attach failed");
    auto frame=std::make_unique<Frame>();need(reader.poll(*frame)==Status::Empty,"Passive source required assets");
    NativeTarget targetNotice{};need(reader.target(targetNotice)==Status::Empty,"Passive native target");
    auto* targetStore=new(base+output_target::Offset)output_target::Store();
    output_target::Notice target{};target.pid=GetCurrentProcessId();std::memcpy(target.session,session.data(),16);
    target.width=1920;target.height=1080;target.device=target.generation=1;target.observed=1;output_target::publish(*targetStore,target);
    need(reader.target(targetNotice)==Status::Ready&&targetNotice.width==1920&&reader.read_only(),"Target waits on ships or maps writable");
    common[3]=1;native->header.pid=GetCurrentProcessId();
    multi_scene::Frame f{};f.sequence=41;f.offered=43;f.frame=47;f.anchor=3;f.revision=5;f.count=1;
    auto& r=f.rows[0];r[1]=3;r[2]=47;r[4]=1;r[5]=53;r[6]=59;r[7]=5;r[48]=1;r[94]=41;
    f.checksum=multi_scene::checksum(f);auto& slot=native->frames[47%8];slot.packet=f;slot.guard=2;native->header.frame=47;
    need(reader.poll(*frame)==Status::Ready&&frame->sequence==41,"Source frame not delivered");
    need(reader.poll(*frame)==Status::Unchanged,"Duplicate source delivered");
    need(reader.read_only(),"Reader changed access rights");
    wchar_t executable[MAX_PATH]{};need(GetModuleFileNameW(nullptr,executable,MAX_PATH)>0,"Locate consumer fixture");
    std::wstring command=L"\""+std::wstring(executable)+L"\" \""+name+L"\" "+std::to_wstring(GetCurrentProcessId());
    STARTUPINFOW startup{sizeof(startup)};PROCESS_INFORMATION process{};
    need(CreateProcessW(executable,command.data(),nullptr,nullptr,FALSE,CREATE_NO_WINDOW,nullptr,nullptr,&startup,&process),"Start read-only consumer");
    CloseHandle(process.hThread);
    need(WaitForSingleObject(process.hProcess,5000)==WAIT_OBJECT_0,"Read-only consumer timed out");
    DWORD code=1;GetExitCodeProcess(process.hProcess,&code);CloseHandle(process.hProcess);need(code==0,"Read-only consumer failed");
    auto wrong=session;wrong[0]++;Reader invalid;need(!invalid.open(name,wrong,GetCurrentProcessId()),"Cross-session attach accepted");
    native->header.stopped=1;need(reader.poll(*frame)==Status::Stopped,"Stopped source still active");
    reader.close();need(reader.poll(*frame)==Status::InvalidHeader,"Closed reader still active");
    native->header.stopped=0;
    const auto readyName=name+L"-ready",stopName=name+L"-stop";
    HANDLE ready=CreateEventW(nullptr,TRUE,FALSE,readyName.c_str());HANDLE stop=CreateEventW(nullptr,TRUE,FALSE,stopName.c_str());
    need(ready&&stop,"Lifetime fixture events");
    command=L"\""+std::wstring(executable)+L"\" --producer \""+name+L"\" \""+readyName+L"\" \""+stopName+L"\"";
    need(CreateProcessW(executable,command.data(),nullptr,nullptr,FALSE,CREATE_NO_WINDOW,nullptr,nullptr,&startup,&process),"Start lifetime producer");CloseHandle(process.hThread);
    need(WaitForSingleObject(ready,5000)==WAIT_OBJECT_0,"Producer readiness");
    need(reader.open(name,session,process.dwProcessId)&&reader.poll(*frame)==Status::Ready,"Bind producer lifetime");
    SetEvent(stop);need(WaitForSingleObject(process.hProcess,5000)==WAIT_OBJECT_0,"Producer normal exit");
    need(reader.poll(*frame)==Status::Stopped,"Producer death left source reader active");reader.close();
    CloseHandle(process.hProcess);CloseHandle(ready);CloseHandle(stop);
    UnmapViewOfFile(base);CloseHandle(mapping);
    std::puts("PASS read-only Windows mapping, separate consumer, passive attachment, source identity, duplicate suppression, producer death and close");return 0;
}catch(const std::exception& e){std::fprintf(stderr,"%s\n",e.what());return 1;}}
