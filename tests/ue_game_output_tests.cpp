#include "../src/rendering/ue/ue_game_output_contract.h"
#include "../tools/d3d9_proof/live_owner_wire.h"
#include <cstdio>
#include <stdexcept>
void need(bool value,const char* why){if(!value)throw std::runtime_error(why);}
int main(){try{
    using namespace sfc_ue_game;
    Activation a{};a.session={1,2,3,4};a.game=17;a.owner=3;a.revision=5;a.model=53;a.source=59;
    a.asset[0]=7;a.generation=1;
    sfc_source_view::Frame f{};f.frame=47;f.sequence=41;f.offered=43;f.anchor=3;f.revision=5;f.count=1;
    auto& r=f.rows[0];r[1]=3;r[2]=47;r[4]=1;r[5]=53;r[6]=59;r[7]=5;r[48]=1;r[94]=41;
    for(unsigned offset:{8u,49u}){r[offset]=r[offset+5]=r[offset+10]=r[offset+15]=0x3f800000;r[offset+16]=0x100;}
    float projection[16]{2,0,0,0,0,3,0,0,0,0,-1,-2,0,0,-1,0};std::memcpy(r.data()+66,projection,64);
    const float viewport[6]{200,30,1720,1020,860,510};std::memcpy(r.data()+83,viewport,24);
    f.checksum=sfc_source_view::hash(&f,offsetof(sfc_source_view::Frame,checksum));
    output_target::Notice target{};target.pid=17;std::memcpy(target.session,a.session.data(),16);
    target.width=1920;target.height=1080;target.device=1;target.generation=1;target.observed=43;output_target::seal(target);
    sfc_ue_export::Packet p{};p.flags=sfc_ue_output::SourceFrame|sfc_ue_output::SourceSequence;
    p.producer=19;p.consumer=23;p.width=1720;p.height=1020;p.target_width=1920;p.target_height=1080;p.viewport_x=200;p.viewport_y=30;
    p.identity.session=session64(a.session);p.identity.asset=a.asset;p.identity.owner_epoch=3;p.identity.revision=5;
    p.identity.frame=47;p.identity.sequence=41;p.identity.camera_pose=camera_hash(r);p.identity.cohort=f.checksum;
    p.identity.activation=p.identity.device=p.identity.target=p.identity.output=p.resource_epoch=1;p.p22=-1;p.p23=-2;
    need(qualifies(p,a,f,target),"Exact independent source admission failed");
    auto bad=p;bad.identity.sequence++;need(!qualifies(bad,a,f,target),"Stale source sequence accepted");
    bad=p;bad.identity.asset[0]++;need(!qualifies(bad,a,f,target),"Wrong source content accepted");
    bad=p;bad.identity.camera_pose++;need(!qualifies(bad,a,f,target),"Wrong camera/pose accepted");
    bad=p;bad.identity.device++;need(!qualifies(bad,a,f,target),"Wrong device accepted");
    bad=p;bad.identity.target++;need(!qualifies(bad,a,f,target),"Wrong target generation accepted");
    bad=p;bad.identity.session[0]++;need(!qualifies(bad,a,f,target),"Foreign session accepted");
    bad=p;bad.p23=-3;need(!qualifies(bad,a,f,target),"Wrong depth projection accepted");
    bad=p;bad.flags=sfc_ue_output::Replay;need(!qualifies(bad,a,f,target),"Replay accepted in normal output");
    need(qualifies(bad,a,f,target,true),"Explicit replay fixture rejected");
    auto changed=f;changed.offered++;changed.checksum=sfc_source_view::hash(&changed,offsetof(sfc_source_view::Frame,checksum));
    need(!qualifies(p,a,changed,target),"Same pose from a different sealed native frame accepted");
    auto legacy=packet(p);need(legacy.owner==3&&legacy.revision==5&&legacy.source_frame==47&&legacy.source_state_hash==p.identity.cohort,"Legacy packet identity lost");
    const auto meta=metadata(p);need(game_output::valid(meta,a.session.data())&&meta.source_sequence==41,"Source metadata lost");
    game_output::Pool layout{};
    layout.header.version=game_output::Version;layout.reserved[2]=game_output::CohortFlag;
    need(game_output::valid_layout(layout)&&!game_output::native_pixels(layout),"Legacy camera layout changed");
    layout.header.version=game_output::NativeTargetVersion;layout.reserved[2]|=game_output::NativePixelsFlag;
    need(game_output::valid_layout(layout)&&game_output::native_pixels(layout),"Explicit native pixel layout missing");
    layout.reserved[2]=game_output::CohortFlag;need(!game_output::valid_layout(layout),"Unmarked version4 accepted");
    layout.reserved[2]=game_output::NativePixelsFlag;layout.header.version=game_output::Version;need(!game_output::valid_layout(layout),"Native pixels silently accepted as legacy");
    layout.header.version=99;need(!game_output::valid_layout(layout),"Unknown pool version accepted");
    std::puts("PASS UE/native pool admission, exact source/asset/camera/target/depth identity and unchanged legacy metadata");return 0;
}catch(const std::exception& e){std::fprintf(stderr,"%s\n",e.what());return 1;}}
