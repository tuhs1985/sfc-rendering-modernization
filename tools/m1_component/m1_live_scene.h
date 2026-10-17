#pragma once
#include "m1_live_bridge.h"

namespace sfc_m1 {
constexpr DWORD kSceneBytes=16*1024*1024,kSceneOwners=32,kSceneRevisions=64;
constexpr DWORD kSceneAssetBytes=2*1024*1024,kSceneAssets=4,kSceneData=65536;
// State table: 4096 + owner*512; guard then original96words (word7 revision).
// Asset descriptors:256 + slot*64; generation,ack,meshbytes,refsbytes,owner,revision.
struct SceneAsset {
    LiveMeshPacket mesh;
    LiveTextureReferences refs;
    DWORD revision=0;
    volatile LONG ready=0;
};
struct SceneOwner {
    MeshIdentity identity{};
    std::array<DWORD,3> lod{};
    DWORD revision=0,last_ms=0,sequence=0;
    bool retired=false,failed=false;
};
struct LiveScene {
    std::array<SceneAsset,kSceneAssets> assets{};
    std::array<SceneOwner,kSceneOwners> owners{};
    std::array<std::array<DWORD,96>,kSceneOwners> pending{};
    SRWLOCK mailbox=SRWLOCK_INIT;
    HANDLE mapping=nullptr,worker=nullptr,stop_event=nullptr;
    BYTE* view=nullptr;
    std::wstring output;
    DWORD owner_count=0,revisions=0,last_capture_frame=0xffffffffu;
    DWORD capture_attempts=0,capture_failures=0,owner_overflow=0,dropped=0,invalid=0;
    LONGLONG max_capture_ticks=0;LARGE_INTEGER frequency{};
    volatile LONG enabled=0;
    bool start(const std::wstring& name,const std::wstring& directory) {
        if(!LiveBridge::name_ok(name) || worker)return false;
        mapping=OpenFileMappingW(FILE_MAP_READ|FILE_MAP_WRITE,FALSE,name.c_str());
        if(!mapping)return false;
        view=static_cast<BYTE*>(MapViewOfFile(mapping,FILE_MAP_READ|FILE_MAP_WRITE,0,0,kSceneBytes));
        if(!view){close();return false;}
        const auto* h=reinterpret_cast<DWORD*>(view);
        if(h[0]!=kLiveMagic || h[1]!=3 || h[2]!=kSceneBytes || h[3]!=0){close();return false;}
        const auto hex=name.substr(name.size()-32);
        for(DWORD i=0;i<4;++i)if(h[4+i]!=std::stoul(hex.substr(i*8,8),nullptr,16)){close();return false;}
        output=directory;stop_event=CreateEventW(nullptr,TRUE,FALSE,nullptr);
        if(!stop_event){close();return false;}
        QueryPerformanceFrequency(&frequency);
        // Fault in fixed storage before hook installation, not during first asset.
        for(auto& a:assets){a.mesh.positions={};a.mesh.corners={};a.mesh.polygons={};a.refs={};}
        InterlockedExchange(&enabled,1);worker=CreateThread(nullptr,0,run,this,0,nullptr);
        if(!worker){enabled=0;close();return false;}return true;
    }
    void close(){if(view){UnmapViewOfFile(view);view=nullptr;}if(mapping){CloseHandle(mapping);mapping=nullptr;}
        if(stop_event){CloseHandle(stop_event);stop_event=nullptr;}}
    bool stop(){InterlockedExchange(&enabled,0);if(!worker){close();return true;}
        SetEvent(stop_event);if(WaitForSingleObject(worker,5000)!=WAIT_OBJECT_0)return false;
        CloseHandle(worker);worker=nullptr;close();return true;}
    void offer(DWORD index,std::array<DWORD,96> r){
        if(!TryAcquireSRWLockExclusive(&mailbox)){++dropped;return;}
        r[0]=++owners[index].sequence;r[45]=index;pending[index]=r;ReleaseSRWLockExclusive(&mailbox);
    }
    void retire(DWORD owner,DWORD frame,DWORD elapsed){
        if(!enabled)return;
        for(DWORD i=0;i<owner_count;++i)if(owners[i].identity.owner==owner){
            auto& o=owners[i];o.retired=true;std::array<DWORD,96> r{};
            r[1]=owner;r[2]=frame;r[3]=elapsed;r[4]=2;r[7]=o.revision;offer(i,r);return;}
    }
    template<class Read,class Validate>
    void observe(const MeshIdentity& id,Read read,Validate valid){
        if(!enabled || id.elapsed>90000 || id.caller!=0x0042E55D)return;
        std::array<DWORD,3> lod{};
        if(!read(id.visual+0x11c,lod.data(),12)){++invalid;return;}
        DWORD index=0;for(;index<owner_count;++index)if(owners[index].identity.owner==id.owner)break;
        if(index==owner_count){
            if(owner_count==kSceneOwners){
                for(index=0;index<owner_count;++index)if(owners[index].retired)break;
                if(index==owner_count){++owner_overflow;return;}
                // Preserve monotonically increasing per-slot sequence across owner epochs.
                const auto seq=owners[index].sequence;owners[index]={};owners[index].sequence=seq;
            }else ++owner_count;
            owners[index].identity=id;owners[index].lod=lod;
        }
        auto& o=owners[index];
        if(o.retired)return; // owner epoch must be newly qualified by existing owner table
        if(!o.identity.same_epoch(id) || o.lod!=lod){o.identity=id;o.lod=lod;o.revision=0;o.failed=false;o.last_ms=0;}
        if(!o.revision && !o.failed && id.frame!=last_capture_frame){
            if(revisions==kSceneRevisions){o.failed=true;++capture_failures;}
            else for(auto& a:assets)if(InterlockedCompareExchange(&a.ready,0,0)==0){
                last_capture_frame=id.frame;++capture_attempts;LARGE_INTEGER before{},after{};QueryPerformanceCounter(&before);
                const auto result=capture_mesh(a.mesh,id,read,valid);
                bool triangles=result==MeshStatus::Complete;
                if(triangles)for(DWORD p=0;p<a.mesh.header[MeshPolygons];++p)triangles &= a.mesh.polygons[p].header[0]==3;
                if(triangles && std::memcmp(a.mesh.header.data()+MeshLodCount,lod.data(),12))triangles=false;
                if(triangles)capture_texture_references(a.refs,a.mesh,read,valid);
                QueryPerformanceCounter(&after);if(after.QuadPart-before.QuadPart>max_capture_ticks)max_capture_ticks=after.QuadPart-before.QuadPart;
                if(!triangles || a.refs.status!=1){o.failed=true;++capture_failures;break;}
                a.revision=++revisions;o.revision=a.revision;MemoryBarrier();InterlockedExchange(&a.ready,1);break;
            }
        }
        if(o.sequence && id.elapsed-o.last_ms<34)return;
        std::array<DWORD,96> r{};r[1]=id.owner;r[2]=id.frame;r[3]=id.elapsed;
        r[4]=o.failed?3:1;r[5]=id.model;r[6]=id.source;r[7]=o.revision;
        std::array<DWORD,34> check{};std::array<DWORD,40> camera{};std::array<DWORD,3> lod_check{};
        if(!read(id.manager+0x6f4,&r[8],68) || !read(id.manager+0x6b0,&r[25],68) ||
           !read(0x00C69FF0,&r[42],4) || !read(0x00C69FF4,&r[43],4) || !read(0x00C74058,&r[44],4) ||
           !read(id.manager+0x628,&r[49],68) || !read(id.manager+0x55c,&r[66],68) || !read(id.manager+0x75c,&r[83],24) ||
           !read(id.manager+0x628,camera.data(),68) || !read(id.manager+0x55c,camera.data()+17,68) ||
           !read(id.manager+0x75c,camera.data()+34,24) || std::memcmp(camera.data(),&r[49],160) ||
           !read(id.manager+0x6f4,check.data(),68) || !read(id.manager+0x6b0,check.data()+17,68) ||
           std::memcmp(check.data(),&r[8],136) || !read(id.visual+0x11c,lod_check.data(),12) || lod_check!=lod || !valid()){++invalid;return;}
        for(DWORD i=8;i<89;++i)if(i!=24 && i!=41 && i!=65 && i!=82 && !(i>=42 && i<=48) &&
            !MeshPacket::finite(r[i])){++invalid;return;}
        r[46]=lod[1]!=0xffffffffu?lod[1]:(lod[0]>1?lod[2]:0);
        r[48]=1;o.last_ms=id.elapsed;offer(index,r);
    }
    static DWORD WINAPI run(void* raw){
        auto& b=*static_cast<LiveScene*>(raw);
        InterlockedExchange(reinterpret_cast<LONG*>(b.view+12),1);
        std::array<DWORD,32> last{},counts{};std::array<DWORD,4> generations{};
        DWORD bytes=0,records=0,transfers=0;bool failed=false,saturated=false;
        std::ofstream log(b.output+L"\\LIVE-SCENE-001-updates.jsonl",std::ios::binary|std::ios::trunc);
        if(!log)failed=true;
        do{
            for(auto& a:b.assets)if(InterlockedCompareExchange(&a.ready,0,0)==1){
                for(DWORD slot=0;slot<4;++slot){
                    auto* d=reinterpret_cast<DWORD*>(b.view+256+slot*64);
                    if(InterlockedCompareExchange(reinterpret_cast<LONG*>(d+1),0,0)!=static_cast<LONG>(generations[slot]))continue;
                    std::ostringstream mesh(std::ios::binary),refs;
                    const bool good=a.mesh.write(mesh) && write_texture_references(refs,a.refs,a.mesh,false);
                    const auto m=mesh.str(),r=refs.str();
                    if(!good || m.size()+r.size()>kSceneAssetBytes){failed=true;InterlockedExchange(&a.ready,0);break;}
                    auto* base=b.view+kSceneData+slot*kSceneAssetBytes;
                    std::memcpy(base,m.data(),m.size());std::memcpy(base+m.size(),r.data(),r.size());
                    d[2]=static_cast<DWORD>(m.size());d[3]=static_cast<DWORD>(r.size());d[4]=a.mesh.header[MeshOwner];d[5]=a.revision;
                    MemoryBarrier();InterlockedExchange(reinterpret_cast<LONG*>(d),++generations[slot]);++transfers;
                    const auto stem=b.output+L"\\LIVE-SCENE-001-asset-"+std::to_wstring(a.revision);
                    std::ofstream mf(stem+L".bin",std::ios::binary),rf(stem+L".json",std::ios::binary);
                    mf.write(m.data(),static_cast<std::streamsize>(m.size()));rf.write(r.data(),static_cast<std::streamsize>(r.size()));
                    if(!mf || !rf)failed=true;
                    InterlockedExchange(&a.ready,0);break;
                }
            }
            for(DWORD i=0;i<32;++i){
                std::array<DWORD,96> r{};
                if(TryAcquireSRWLockExclusive(&b.mailbox)){r=b.pending[i];ReleaseSRWLockExclusive(&b.mailbox);}
                if(r[0]<=last[i])continue;last[i]=r[0];
                auto* guard=reinterpret_cast<LONG*>(b.view+4096+i*512);
                InterlockedIncrement(guard);std::memcpy(b.view+4100+i*512,r.data(),sizeof(r));MemoryBarrier();InterlockedIncrement(guard);
                if(failed || counts[i]>=2700)continue;
                std::ostringstream row;row<<'[';for(DWORD w=0;w<96;++w){if(w)row<<',';row<<r[w];}row<<"]\n";
                const auto text=row.str();
                if(bytes+text.size()>16*1024*1024){saturated=true;continue;}
                log<<text;if(!log)failed=true;bytes+=static_cast<DWORD>(text.size());++counts[i];++records;
            }
        }while(WaitForSingleObject(b.stop_event,10)==WAIT_TIMEOUT);
        log.close();
        DWORD unsent=0;for(const auto& a:b.assets)if(a.ready==1)++unsent;
        std::ofstream summary(b.output+L"\\LIVE-SCENE-001-worker.json");
        summary<<"{\"records\":"<<records<<",\"bytes\":"<<bytes<<",\"warning\":"<<(bytes>=8*1024*1024?"true":"false")
          <<",\"saturated\":"<<(saturated?"true":"false")<<",\"transfers\":"<<transfers<<",\"capture_attempts\":"<<b.capture_attempts
          <<",\"capture_failures\":"<<b.capture_failures<<",\"owner_overflow\":"<<b.owner_overflow<<",\"dropped\":"<<b.dropped
          <<",\"invalid\":"<<b.invalid<<",\"max_capture_ticks\":"<<b.max_capture_ticks<<",\"qpc_frequency\":"<<b.frequency.QuadPart
          <<",\"unsent_assets\":"<<unsent<<",\"io_failed\":"<<(failed?"true":"false")<<",\"stopped\":true}";
        InterlockedExchange(reinterpret_cast<LONG*>(b.view+12),failed?3:2);return 0;
    }
};
}
