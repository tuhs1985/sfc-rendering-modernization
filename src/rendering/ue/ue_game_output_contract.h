#pragma once
// UE front-end admission into the versioned native game-pool protocol.
// Expected source/activation data is obtained independently of the incoming GPU packet.
#include "ue_export_channel.h"
#include "ue_source_identity.h"
#include "../../transport/source_scene_view.h"
#include "../../../tools/d3d9_proof/game_output_wire.h"
#include "../../../tools/d3d9_proof/output_target.h"
namespace sfc_ue_game {
struct Activation {
    std::array<DWORD,4> session{};
    uint32_t game{},owner{},revision{},model{},source{};
    std::array<uint8_t,32> asset{};
    uint64_t generation{};
};
inline std::array<uint64_t,2> session64(const std::array<DWORD,4>& words){
    return {uint64_t(words[0])|(uint64_t(words[1])<<32),uint64_t(words[2])|(uint64_t(words[3])<<32)};
}
inline bool qualifies(const sfc_ue_export::Packet& p,const Activation& a,const sfc_source_view::Frame& f,
                      const output_target::Notice& target,bool replay=false){
    const auto& i=p.identity;
    if(!a.game||!a.owner||!a.revision||!a.model||!a.source||!a.generation||i.session!=session64(a.session)||i.asset!=a.asset||
       i.owner_epoch!=a.owner||i.revision!=a.revision||i.activation!=a.generation||
       ((p.flags&sfc_ue_output::Replay)&&!replay)||(!(p.flags&sfc_ue_output::Replay)&&
       (p.flags&(sfc_ue_output::SourceFrame|sfc_ue_output::SourceSequence))!=(sfc_ue_output::SourceFrame|sfc_ue_output::SourceSequence))||
       !output_target::valid(target,a.session.data(),a.game)||i.device!=target.device||i.target!=target.generation||
       p.resource_epoch!=target.generation||p.target_width!=target.width||p.target_height!=target.height||
       !sfc_source_view::valid(f)||f.checksum!=sfc_source_view::hash(&f,offsetof(sfc_source_view::Frame,checksum))||
       i.frame!=f.frame||i.sequence!=f.sequence||f.anchor!=a.owner||f.revision!=a.revision)return false;
    const auto* row=sfc_source_view::find(f,a.owner,a.revision,a.model,a.source);if(!row)return false;
    sfc_source_view::Pose pose;if(!sfc_source_view::pose(*row,pose))return false;
    return i.camera_pose==camera_hash(*row)&&i.cohort==f.checksum&&i.cohort&&
        p.viewport_x==pose.viewport[0]&&p.viewport_y==pose.viewport[1]&&p.width==pose.viewport[2]&&p.height==pose.viewport[3]&&
        p.p22==pose.projection[10]&&p.p23==pose.projection[11];
}
inline output_wire::Packet packet(const sfc_ue_export::Packet& p){
    output_wire::Packet result{};result.magic_value=output_wire::magic;result.version_value=output_wire::version;result.bytes=sizeof(result);
    result.producer_pid=p.producer;result.session=sfc_ue_output::hash(p.identity.session.data(),sizeof(p.identity.session));
    result.resource_epoch=p.resource_epoch;result.sequence=p.identity.output;result.source_frame=p.identity.frame;
    result.owner=uint32_t(p.identity.owner_epoch);result.revision=uint32_t(p.identity.revision);
    result.width=p.target_width;result.height=p.target_height;result.luid_low=uint32_t(p.adapter_luid);result.luid_high=int32_t(p.adapter_luid>>32);
    result.source_state_hash=p.identity.cohort;result.scene_hash=sfc_ue_output::hash(p.identity.asset.data(),p.identity.asset.size());
    result.published_qpc=sfc_ue_export::now();result.checksum=output_wire::checksum(result);
    // Legacy resource handles stay empty until GameOutputWriter supplies its
    // actual legacy-compatible handles. Never truncate UE NT export handles.
    return result;
}
inline game_output::Metadata metadata(const sfc_ue_export::Packet& p){
    game_output::Metadata result{};result.source_sequence=p.identity.sequence;
    std::memcpy(result.source_session,p.identity.session.data(),16);result.checksum=game_output::checksum(result);return result;
}
}
