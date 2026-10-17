#pragma once
// Existing hook calls only nonwaiting fixed-storage methods. Worker owns IPC/I/O.
#include <windows.h>
#include <array>
#include <cstring>
#include <fstream>
#include <sstream>
#include "m1_texture_references.h"

namespace sfc_m1 {
constexpr DWORD kLiveBytes=2*1024*1024,kLiveAssetStride=512*1024;
constexpr DWORD kLiveMagic=0x31424c53,kLiveRecordWords=96; // protocol2: camera block follows original48words
struct LiveAsset {
    MeshPacket mesh;
    TextureReferences refs;
    volatile LONG ready=0;
    MeshIdentity identity{};
};
struct LiveBridge {
    std::array<LiveAsset,2> assets{};
    std::array<DWORD,kLiveRecordWords> pending{};
    SRWLOCK mailbox=SRWLOCK_INIT;
    HANDLE mapping=nullptr,worker=nullptr,stop_event=nullptr;
    BYTE* view=nullptr;
    std::wstring output;
    DWORD active_slot=0,epochs=0,last_ms=0,sequence=0;
    volatile LONG enabled=0;
    DWORD dropped=0,invalid=0,asset_rejections=0;
    bool retired=true;
    static bool name_ok(const std::wstring& name) {
        const std::wstring prefix=L"Local\\SFCBridge_";
        if(name.size()!=prefix.size()+32 || name.compare(0,prefix.size(),prefix)!=0)return false;
        for(std::size_t i=prefix.size();i<name.size();++i)
            if(!((name[i]>=L'0'&&name[i]<=L'9')||(name[i]>=L'a'&&name[i]<=L'f')))return false;
        return true;
    }
    bool start(const std::wstring& name,const std::wstring& directory) {
        if(!name_ok(name) || worker)return false;
        mapping=OpenFileMappingW(FILE_MAP_READ|FILE_MAP_WRITE,FALSE,name.c_str());
        if(!mapping)return false;
        view=static_cast<BYTE*>(MapViewOfFile(mapping,FILE_MAP_READ|FILE_MAP_WRITE,0,0,kLiveBytes));
        if(!view){close();return false;}
        auto* h=reinterpret_cast<DWORD*>(view);
        if(h[0]!=kLiveMagic || h[1]!=2 || h[2]!=kLiveBytes || h[3]!=0){close();return false;}
        // Verify UUID words, not merely the user-supplied object name.
        const auto hex=name.substr(name.size()-32);
        for(DWORD i=0;i<4;++i)if(h[4+i]!=std::stoul(hex.substr(i*8,8),nullptr,16)){close();return false;}
        output=directory; stop_event=CreateEventW(nullptr,TRUE,FALSE,nullptr);
        if(!stop_event){close();return false;}
        InterlockedExchange(&enabled,1);
        worker=CreateThread(nullptr,0,run,this,0,nullptr);
        if(!worker){InterlockedExchange(&enabled,0);close();return false;}
        return true;
    }
    void close() {
        if(view){UnmapViewOfFile(view);view=nullptr;}
        if(mapping){CloseHandle(mapping);mapping=nullptr;}
        if(stop_event){CloseHandle(stop_event);stop_event=nullptr;}
    }
    bool stop() {
        InterlockedExchange(&enabled,0);
        if(!worker){close();return true;}
        SetEvent(stop_event);
        if(WaitForSingleObject(worker,5000)!=WAIT_OBJECT_0)return false;
        CloseHandle(worker);worker=nullptr;close();return true;
    }
    void offer(std::array<DWORD,kLiveRecordWords> record) {
        if(!TryAcquireSRWLockExclusive(&mailbox)){++dropped;return;}
        record[0]=++sequence;pending=record;
        ReleaseSRWLockExclusive(&mailbox);
    }
    void retire(DWORD owner,DWORD frame,DWORD elapsed) {
        if(!enabled || retired || !epochs || assets[active_slot].identity.owner!=owner)return;
        retired=true;
        std::array<DWORD,kLiveRecordWords> r{};
        r[1]=owner;r[2]=frame;r[3]=elapsed;r[4]=2;r[45]=active_slot;offer(r);
    }
    template<class Read,class Validate>
    void observe(const MeshIdentity& id,Read read,Validate valid) {
        if(!enabled || id.elapsed>90000 || id.caller!=0x0042E55D)return;
        if(retired) {
            if(epochs>=2 || id.count!=452)return;
            std::array<char,256> name{};
            if(!read(id.visual+0x14,name.data(),256) || !std::memchr(name.data(),0,256))return;
            const char* expected="assets/models/kff/kff.mod";
            for(auto& c:name){if(c=='\\')c='/';if(c>='A'&&c<='Z')c=static_cast<char>(c+32);}
            if(std::strcmp(name.data(),expected)!=0)return;
            // Exactly two immutable attempts; failures never read again by worker.
            active_slot=epochs++;
            auto& a=assets[active_slot];a.identity=id;
            if(capture_mesh(a.mesh,id,read,valid)!=MeshStatus::Complete ||
               a.mesh.header[MeshVertices]!=254 || a.mesh.header[MeshCorners]!=1356 ||
               a.mesh.header[MeshSources]!=5){++asset_rejections;return;}
            capture_texture_references(a.refs,a.mesh,read,valid);
            if(a.refs.status!=1){++asset_rejections;return;}
            InterlockedExchange(&a.ready,1);retired=false;last_ms=0;
        }
        const auto& a=assets[active_slot];
        if(!a.identity.same_epoch(id)) {
            if(id.owner==a.identity.owner)retire(id.owner,id.frame,id.elapsed);
            return;
        }
        if(id.elapsed-last_ms<34)return;
        std::array<DWORD,kLiveRecordWords> r{};
        r[1]=id.owner;r[2]=id.frame;r[3]=id.elapsed;r[4]=1;r[5]=id.model;r[6]=id.source;r[45]=active_slot;
        std::array<DWORD,34> check{};
        if(!read(id.manager+0x6f4,&r[8],68) || !read(id.manager+0x6b0,&r[25],68) ||
           !read(0x00C69FF0,&r[42],4) || !read(0x00C69FF4,&r[43],4) || !read(0x00C74058,&r[44],4) ||
           !read(id.manager+0x6f4,check.data(),68) || !read(id.manager+0x6b0,check.data()+17,68) ||
           std::memcmp(check.data(),&r[8],136)!=0 || !valid()){++invalid;return;}
        for(DWORD i=8;i<42;++i)if(i!=24 && i!=41 && !MeshPacket::finite(r[i])){++invalid;return;}
        std::array<DWORD,40> camera_check{};
        if(!read(id.manager+0x628,&r[49],68) || !read(id.manager+0x55c,&r[66],68) ||
           !read(id.manager+0x75c,&r[83],24) ||
           !read(id.manager+0x628,camera_check.data(),68) ||
           !read(id.manager+0x55c,camera_check.data()+17,68) ||
           !read(id.manager+0x75c,camera_check.data()+34,24) ||
           std::memcmp(camera_check.data(),&r[49],160)!=0 ||
           !read(id.manager+0x6f4,check.data(),68) || !read(id.manager+0x6b0,check.data()+17,68) ||
           std::memcmp(check.data(),&r[8],136)!=0 || !valid()){++invalid;return;}
        for(DWORD i=49;i<89;++i)if(i!=65 && i!=82 && !MeshPacket::finite(r[i])){++invalid;return;}
        r[48]=1;
        last_ms=id.elapsed;offer(r);
    }
    static DWORD WINAPI run(void* raw) {
        auto& b=*static_cast<LiveBridge*>(raw);
        auto* h=reinterpret_cast<DWORD*>(b.view);
        InterlockedExchange(reinterpret_cast<LONG*>(h+3),1);
        DWORD last=0,records=0;std::array<bool,2> sent{};
        std::ofstream log(b.output+L"\\LIVE-BRIDGE-001-updates.jsonl",std::ios::binary|std::ios::trunc);
        bool failed=!log;
        do {
            for(DWORD i=0;i<2;++i)if(!sent[i] && InterlockedCompareExchange(&b.assets[i].ready,0,0)==1){
                const auto& a=b.assets[i];std::ostringstream mesh(std::ios::binary),refs;
                const bool good=a.mesh.write(mesh) && write_texture_references(refs,a.refs,a.mesh,false);
                const auto m=mesh.str(),r=refs.str();
                if(!good || m.size()+r.size()>kLiveAssetStride){failed=true;continue;}
                BYTE* base=b.view+4096+i*kLiveAssetStride;
                std::memcpy(base,m.data(),m.size());std::memcpy(base+m.size(),r.data(),r.size());
                auto* d=reinterpret_cast<DWORD*>(b.view+128+i*32);
                d[1]=static_cast<DWORD>(m.size());d[2]=static_cast<DWORD>(r.size());d[3]=a.identity.owner;
                MemoryBarrier();InterlockedExchange(reinterpret_cast<LONG*>(d),1);sent[i]=true;
                const auto stem=b.output+L"\\LIVE-BRIDGE-001-asset-"+std::to_wstring(i);
                std::ofstream mf(stem+L".bin",std::ios::binary),rf(stem+L".json",std::ios::binary);
                mf.write(m.data(),static_cast<std::streamsize>(m.size()));rf.write(r.data(),static_cast<std::streamsize>(r.size()));
                if(!mf || !rf)failed=true;
            }
            std::array<DWORD,kLiveRecordWords> r{};
            if(TryAcquireSRWLockExclusive(&b.mailbox)){
                r=b.pending;ReleaseSRWLockExclusive(&b.mailbox);
            }
            if(r[0]>last && records<2700){
                auto* guard=reinterpret_cast<LONG*>(b.view+256);
                InterlockedIncrement(guard);std::memcpy(b.view+260,r.data(),sizeof(r));MemoryBarrier();InterlockedIncrement(guard);
                last=r[0];++records;
                if(!failed){log<<'[';for(std::size_t i=0;i<r.size();++i){if(i)log<<',';log<<r[i];}log<<"]\n";if(!log)failed=true;}
            }
        }while(WaitForSingleObject(b.stop_event,10)==WAIT_TIMEOUT);
        log.close();
        std::ofstream summary(b.output+L"\\LIVE-BRIDGE-001-worker.json");
        summary<<"{\"records\":"<<records<<",\"io_failed\":"<<(failed?"true":"false")
               <<",\"dropped\":"<<b.dropped<<",\"invalid\":"<<b.invalid
               <<",\"asset_rejections\":"<<b.asset_rejections<<",\"asset_attempts\":"<<b.epochs
               <<",\"stopped\":true}\n";
        InterlockedExchange(reinterpret_cast<LONG*>(h+3),failed?3:2);
        return 0;
    }
};
}
