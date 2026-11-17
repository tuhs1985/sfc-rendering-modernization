#pragma once

#include <windows.h>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstring>

namespace transient_draw {
constexpr uint32_t Magic = 0x31544645;
constexpr uint32_t MaxVertices = 16, MaxIndices = 42;

struct Vertex {
    uint32_t batch_index;
    float x, y, z, rhw;
    uint32_t diffuse, specular;
    float u, v;
};

// One captured, pretransformed triangle-list span and its native state.
// The adapter frame key is supplied independently of capture Present identity.
struct Packet {
    uint32_t magic, version, bytes, source_frame;
    uint32_t session[4];
    uint64_t source_sequence, frame_checksum;
    uint8_t trace_sha256[32];
    uint64_t flush_order, present_ordinal;
    uint32_t owner_epoch, resource_id, first_index, vertex_count, index_count, reserved;
    char texture[256];
    uint32_t render_state[11], stage_state[11];
    Vertex vertices[MaxVertices];
    uint32_t indices[MaxIndices];
    uint64_t checksum;
};
static_assert(sizeof(Vertex) == 36 && sizeof(Packet) == 1216);

struct Slot {
    enum State : LONG { Empty, Writing, Ready, Reading };
    volatile LONG state = Empty;
    Packet packet{};
};

inline uint64_t checksum(const Packet& packet) {
    uint64_t hash = 14695981039346656037ull;
    const auto* bytes = reinterpret_cast<const uint8_t*>(&packet);
    for (size_t i = 0; i < offsetof(Packet, checksum); ++i) {
        hash ^= bytes[i];
        hash *= 1099511628211ull;
    }
    return hash;
}

inline bool valid(const Packet& packet) {
    if (packet.magic != Magic || packet.version != 1 || packet.bytes != sizeof(Packet) ||
        !packet.source_frame || !packet.source_sequence || !packet.frame_checksum ||
        !packet.owner_epoch || !packet.resource_id || packet.resource_id > 4096 ||
        !packet.flush_order || !packet.present_ordinal ||
        packet.reserved || !packet.texture[0] || !memchr(packet.texture, 0, sizeof(packet.texture)) ||
        packet.vertex_count < 3 || packet.vertex_count > MaxVertices ||
        !packet.index_count || packet.index_count > MaxIndices || packet.index_count % 3 ||
        packet.first_index > 216 - packet.index_count || packet.first_index % 3 ||
        packet.checksum != checksum(packet)) return false;
    bool has_session = false, has_provenance = false;
    for (auto word : packet.session) has_session |= word != 0;
    for (auto byte : packet.trace_sha256) has_provenance |= byte != 0;
    if (!has_session || !has_provenance) return false;

    for (uint32_t i = 0; i < packet.vertex_count; ++i) {
        const auto& vertex = packet.vertices[i];
        if (vertex.batch_index >= 216 || (i && packet.vertices[i - 1].batch_index >= vertex.batch_index) ||
            !std::isfinite(vertex.x) || !std::isfinite(vertex.y) || !std::isfinite(vertex.z) ||
            !std::isfinite(vertex.rhw) || !std::isfinite(vertex.u) || !std::isfinite(vertex.v)) return false;
    }
    for (uint32_t i = 0; i < packet.index_count; ++i) {
        bool found = false;
        for (uint32_t j = 0; j < packet.vertex_count; ++j)
            found |= packet.vertices[j].batch_index == packet.indices[i];
        if (!found) return false;
    }
    return true;
}

// One producer, newest observation only. Readers make one attempt and use
// only a companion that matches the independently acquired retained frame.
inline bool publish(Slot& slot, const Packet& packet) {
    if (!valid(packet)) return false;
    if (InterlockedCompareExchange(&slot.state, Slot::Writing, Slot::Ready) != Slot::Ready &&
        InterlockedCompareExchange(&slot.state, Slot::Writing, Slot::Empty) != Slot::Empty)
        return false;
    slot.packet = packet;
    InterlockedExchange(&slot.state, Slot::Ready);
    return true;
}

inline bool read(Slot& slot, const DWORD* session, uint32_t frame, uint64_t sequence,
                 uint64_t frame_checksum, Packet& out) {
    if (InterlockedCompareExchange(&slot.state, Slot::Reading, Slot::Ready) != Slot::Ready)
        return false;
    const auto snapshot = slot.packet;
    InterlockedExchange(&slot.state, Slot::Ready);
    if (memcmp(snapshot.session, session, sizeof(snapshot.session)) ||
        snapshot.source_frame != frame || snapshot.source_sequence != sequence ||
        snapshot.frame_checksum != frame_checksum || !valid(snapshot)) return false;
    out = snapshot;
    return true;
}
}
