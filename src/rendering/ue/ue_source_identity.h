#pragma once
#include "ue_output_contract.h"
#include "../../transport/source_scene_view.h"
namespace sfc_ue_game {
inline uint64_t camera_hash(const sfc_source_view::Row& row){
    sfc_source_view::Pose pose;if(!sfc_source_view::pose(row,pose))return 0;
    const std::array<double,4> viewport{pose.viewport[0],pose.viewport[1],pose.viewport[2],pose.viewport[3]};
    uint64_t value=sfc_ue_output::hash(pose.model.data(),sizeof(pose.model));
    for(uint64_t part:{sfc_ue_output::hash(pose.view.data(),sizeof(pose.view)),sfc_ue_output::hash(pose.projection.data(),sizeof(pose.projection)),
                      sfc_ue_output::hash(viewport.data(),sizeof(viewport))})value=(value^part)*1099511628211ull;
    return value;
}
}
