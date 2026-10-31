#pragma once
#include "retained_resources.h"

namespace native_foreground {
// One per render thread. Native hook plumbing is deliberately not installed by
// this primitive. The pinned depth-state setter flushes BEFORE changing state.
// Therefore the disable call's flush is excluded, and restore's flush included.
class ProducerScope {
    Identity identity_{};
    unsigned depth_{};
    bool producing_{}, ambiguous_{}, restoring_{};
    uint32_t resource_{};
    unsigned disables_{},restores_{};
public:
    bool enter(const Identity& id, uint32_t shieldResource) noexcept {
        if (depth_++) { ambiguous_ = true; producing_ = false; return false; }
        identity_ = id; resource_ = shieldResource; producing_ = false;
        restoring_ = false; ambiguous_ = !id.valid();
        disables_=restores_=0;
        return !ambiguous_;
    }
    // Invoked before/after the ORIGINAL manager+C4 call, not its downstream draw.
    void beforeDepthWrite(bool enabled) noexcept {
        if (depth_ != 1 || ambiguous_) return;
        restoring_ = enabled;
        if (!enabled) producing_ = false;
    }
    void afterDepthWrite(bool enabled) noexcept {
        if (depth_ != 1 || ambiguous_) return;
        if(enabled)++restores_;else ++disables_;
        producing_ = !enabled; restoring_ = false;
    }
    bool qualifies(const Identity& id, uint32_t selectedResource,
                   bool depthTest, bool depthWrite, bool additiveOneOne,
                   bool indexedTriangleList) const noexcept {
        return depth_ == 1 && !ambiguous_ && producing_ && identity_ == id &&
            resource_ == selectedResource && depthTest && !depthWrite &&
            additiveOneOne && indexedTriangleList;
    }
    bool restoring() const noexcept { return restoring_; }
    bool balanced() const noexcept {return depth_==1&&!ambiguous_&&disables_==restores_;}
    void leave() noexcept {
        if (!depth_) return;
        if (--depth_) return; // An ambiguous nested span stays rejected to exit.
        identity_ = {}; resource_ = 0; producing_ = restoring_ = ambiguous_ = false;
    }
};
} // namespace native_foreground
