#include "../src/transport/source_scene_view.h"
#include "../tools/d3d9_proof/multi_scene_wire.h"
#include <cstdio>
#include <memory>
#include <stdexcept>
#include <algorithm>
#include <vector>
namespace view=sfc_source_view;
static_assert(sizeof(view::Header)==sizeof(multi_scene::Header));
static_assert(sizeof(view::Frame)==sizeof(multi_scene::Frame));
static_assert(sizeof(view::FrameSlot)==sizeof(multi_scene::FrameSlot));
static_assert(sizeof(view::Store)==sizeof(multi_scene::Store));
static_assert(offsetof(view::Frame,rows)==offsetof(multi_scene::Frame,rows));
static_assert(offsetof(view::Frame,damage)==offsetof(multi_scene::Frame,damage));
static_assert(offsetof(view::Store,assets)==offsetof(multi_scene::Store,assets));
static_assert(sizeof(view::Asset)==sizeof(multi_scene::Asset));
void need(bool value,const char* why){if(!value)throw std::runtime_error(why);}
int main(int argc,char**){try{
    auto memory=std::make_unique<uint8_t[]>(view::MappingBytes);
    const std::array<uint32_t,4> session{1,2,3,4};
    auto* header=reinterpret_cast<uint32_t*>(memory.get());
    header[0]=0x31424c53;header[1]=scene_capacity::Version;header[2]=view::MappingBytes;
    std::memcpy(header+4,session.data(),16);
    auto* native=reinterpret_cast<multi_scene::Store*>(memory.get()+multi_scene::Offset);
    new(native)multi_scene::Store();native->header.bytes=sizeof(*native);std::memcpy(native->header.session,session.data(),16);
    auto result=std::make_unique<view::Frame>();
    auto read=[&](uint64_t last=0){return view::snapshot(memory.get(),view::MappingBytes,session,19,last,*result);};
    need(read()==view::Status::Empty,"Passive source required an active game");
    native->header.stopped=1;
    need(read()==view::Status::Stopped,"Cancelled unattached source ignored stop");
    header[3]=1;
    need(read()==view::Status::Stopped,"Cancelled source without producer PID ignored stop");
    native->header.pid=23;
    need(read()==view::Status::InvalidHeader,"Wrong PID accepted during cancellation");
    native->header.stopped=0;
    header[3]=1;native->header.pid=19; // Native LiveScene worker status, not PID.
    need(read()==view::Status::Empty,"No source frame yet");
    multi_scene::Frame f{};f.sequence=41;f.offered=43;f.frame=47;f.anchor=3;f.revision=5;f.count=1;
    auto& r=f.rows[0];r[1]=3;r[2]=47;r[4]=1;r[5]=53;r[6]=59;r[7]=5;r[48]=1;r[94]=41;
    r[8]=r[13]=r[18]=r[23]=0x3f800000;r[24]=0x100;
    f.checksum=multi_scene::checksum(f);need(multi_scene::valid(f),"Native fixture invalid");
    auto& slot=native->frames[47%8];slot.packet=f;slot.guard=2;native->header.frame=47;
    need(read()==view::Status::Ready&&std::memcmp(result.get(),&f,sizeof(f))==0,"Reader changed native source words");
    need(read(41)==view::Status::Unchanged,"Duplicate frame not recognized");
    need(view::find(*result,3,5,53,59)&&!view::find(*result,3,6,53,59),"Owner/revision association");
    std::array<double,16> model{};need(view::matrix(result->rows[0],8,model)&&model[0]==1&&model[15]==1,"Native affine decode");
    view::Pose pose{};need(!view::pose(result->rows[0],pose),"Zero camera/viewport accepted");
    auto& pr=result->rows[0];
    for(unsigned offset:{49u,66u}){pr[offset]=pr[offset+5]=pr[offset+10]=pr[offset+15]=0x3f800000;pr[offset+16]=0x100;}
    const float viewport[6]{200,30,1720,1020,860,510};std::memcpy(pr.data()+83,viewport,sizeof(viewport));
    need(view::pose(pr,pose)&&pose.viewport[0]==200&&pose.viewport[2]==1720&&pose.model[0]==1,"Original native camera/pose decode");
    pr[42]=1;need(!view::pose(pr,pose),"Unsupported source pose accepted");pr[42]=0;
    slot.guard=3;need(read()==view::Status::Retry,"Accepted writing frame");slot.guard=4;
    slot.packet.frame+=8;slot.packet.rows[0][2]+=8;slot.packet.checksum=multi_scene::checksum(slot.packet);
    need(read()==view::Status::Retry,"Slot publication overtaking header caused a fatal source rejection");slot.packet=f;
    slot.packet.rows[0][1]++;need(read()==view::Status::InvalidFrame,"Torn/bad frame accepted");slot.packet=f;
    native->header.pid=23;need(read()==view::Status::InvalidHeader,"Recycled process accepted");native->header.pid=19;
    native->header.stopped=1;need(read()==view::Status::Stopped,"Stopped source not reported");
    native->header.stopped=0;
    header[3]=2;need(read()==view::Status::Stopped,"Common worker stop not reported");
    header[3]=3;need(read()==view::Status::InvalidHeader,"Failed worker accepted");
    header[3]=19;need(read()==view::Status::InvalidHeader,"PID in worker status accepted");header[3]=1;
    multi_scene::Asset asset{};asset.id=1;asset.path_id=1;asset.owner=3;asset.revision=5;asset.model=53;asset.source=59;
    asset.geometry_bytes=256;asset.image_bytes=4;asset.content[0]=1;asset.replay_hash=7;asset.textures_hash=11;asset.checksum=multi_scene::checksum(asset);
    native->assets[0].packet=asset;native->assets[0].guard=2;
    view::Asset descriptor{};
    need(view::catalog(memory.get(),view::MappingBytes,0,descriptor)==view::Status::Ready&&std::memcmp(&descriptor,&asset,sizeof(asset))==0,"Original catalog association");
    native->assets[0].guard=3;need(view::catalog(memory.get(),view::MappingBytes,0,descriptor)==view::Status::Retry,"Read writing asset catalog");native->assets[0].guard=4;
    native->assets[0].packet.owner++;need(view::catalog(memory.get(),view::MappingBytes,0,descriptor)==view::Status::InvalidFrame,"Read corrupt catalog");
    auto* state=memory.get()+scene_capacity::StateOffset;
    uint32_t ready=2;std::memcpy(state,&ready,4);auto retired=f.rows[0];retired[4]=2;retired[45]=0;std::memcpy(state+4,retired.data(),384);
    view::Row retiredCopy{};need(view::owner_state(memory.get(),view::MappingBytes,0,retiredCopy)==view::Status::Ready&&std::memcmp(retiredCopy.data(),retired.data(),384)==0,"Original retirement row");
    if(argc>1){
        native->header.stopped=0;LARGE_INTEGER frequency{};QueryPerformanceFrequency(&frequency);
        for(uint32_t count:{1u,6u,100u,256u}){
            f.count=count;
            for(uint32_t i=0;i<count;++i){f.rows[i]=f.rows[0];f.rows[i][1]=3+i;f.rows[i][7]=5+i;}
            f.checksum=multi_scene::checksum(f);slot.packet=f;
            std::vector<double> timing;timing.reserve(1000);
            for(unsigned iteration=0;iteration<1000;++iteration){
                LARGE_INTEGER start{},end{};QueryPerformanceCounter(&start);
                need(read()==view::Status::Ready,"Representative owner frame rejected");QueryPerformanceCounter(&end);
                timing.push_back(double(end.QuadPart-start.QuadPart)*1e6/double(frequency.QuadPart));
            }
            std::sort(timing.begin(),timing.end());
            std::printf("owners=%u snapshot_us median=%.3f p95=%.3f p99=%.3f max=%.3f bytes=%zu\n",count,timing[500],timing[950],timing[990],timing.back(),sizeof(view::Frame));
        }
    }
    std::puts("PASS existing native ABI layout, passive startup, exact source bytes, identity, seqlock, checksum and affine matrix");return 0;
}catch(const std::exception& e){std::fprintf(stderr,"%s\n",e.what());return 1;}}
