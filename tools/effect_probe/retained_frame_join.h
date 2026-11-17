#pragma once

#include "../d3d9_proof/multi_scene_wire.h"

namespace effect_probe {

// Capture on the source thread while the retained-frame publisher and the
// native draw observer are in the same session. Manager is a run-local label.
struct FrameStamp {
    DWORD session[4]{};
    DWORD pid = 0, thread = 0, manager = 0, frame = 0;
    uint64_t sequence = 0, checksum = 0, scene_start = 0, observed = 0;
};
constexpr DWORD StampOffset = multi_scene::Offset + sizeof(multi_scene::Store);
struct StampSlot {
    volatile LONG guard = 0;
    FrameStamp stamp{};
};
static_assert(StampOffset + sizeof(StampSlot) <= live_owner::Offset);

inline void publish_stamp(StampSlot& slot, const FrameStamp& stamp) {
    InterlockedIncrement(&slot.guard);
    slot.stamp = stamp;
    MemoryBarrier();
    InterlockedIncrement(&slot.guard);
}

inline bool read_stamp(StampSlot& slot, FrameStamp& stamp) {
    const LONG guard = frame_ingress::state(&slot.guard);
    if (!guard || (guard & 1)) return false;
    stamp = slot.stamp;
    MemoryBarrier();
    return guard == frame_ingress::state(&slot.guard);
}

// The diagnostic producer owns anchor selection. The receiver acknowledges
// only after decoding and validating the asset transfer.
inline bool select_acknowledged_anchor(live_owner::Header& header, DWORD generation,
                                       DWORD acknowledged, DWORD owner, DWORD revision) {
    return generation && generation == acknowledged && owner && revision &&
           !frame_ingress::state(&header.stopped) &&
           InterlockedCompareExchange64(&header.selected,
               static_cast<LONG64>(live_owner::selection(owner, revision)), 0) == 0;
}

inline bool same_frame(const FrameStamp& a, const FrameStamp& b) {
    return live_owner::same_session(a.session, b.session) &&
           a.pid == b.pid && a.thread == b.thread && a.manager == b.manager &&
           a.frame == b.frame && a.sequence == b.sequence &&
           a.checksum == b.checksum && a.scene_start == b.scene_start;
}

// Worker-side verification. Scratch is the same retained packet type the
// consumer reads. A ring rollover or a failed Present makes the proof partial.
inline bool verify_retained_frame(multi_scene::Store& store,
                                  const FrameStamp& published,
                                  const FrameStamp& flushed,
                                  const FrameStamp& presented,
                                  bool present_succeeded,
                                  multi_scene::Frame& scratch) {
    if (!present_succeeded || !published.thread || !published.manager ||
        !published.frame || !published.sequence || !published.checksum ||
        !published.scene_start || published.observed < published.scene_start ||
        flushed.observed < published.observed || presented.observed < flushed.observed ||
        !same_frame(published, flushed) || !same_frame(flushed, presented) ||
        !multi_scene::valid(store.header, published.session, published.pid) ||
        !multi_scene::read(store, published.frame, published.sequence, scratch) ||
        scratch.checksum != published.checksum ||
        scratch.offered < published.scene_start || scratch.offered > published.observed)
        return false;

    for (DWORD i = 0; i < scratch.count; ++i) {
        if (scratch.rows[i][47] != published.thread) return false;
    }
    return true;
}

}
