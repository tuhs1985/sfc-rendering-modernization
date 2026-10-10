#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <limits>

namespace sfc_m1 {

constexpr std::uint32_t kTintSourceStride = 36;
constexpr std::uint32_t kTintSourceCapacity = 256;
constexpr std::uint32_t kTintPolygonLimit = 4096;

inline bool tint_address(std::uint32_t base, std::uint32_t offset,
                         std::uint32_t& result) {
    if (!base || offset > (std::numeric_limits<std::uint32_t>::max)() - base)
        return false;
    result = base + offset;
    return true;
}

struct TintSnapshot {
    std::array<std::uint8_t, kTintSourceStride * kTintSourceCapacity> bytes{};
    std::uint32_t entries = 0;
    std::uint32_t sample_index = 0;
    std::uint32_t original_rgb = 0;
};

// Read/copy callbacks are guarded by SEH in the live component. They are
// injectable here so bounds and non-mutation can be verified without SFC.
template <typename Read32, typename Copy>
bool prepare_tint_snapshot(std::uint32_t source, std::uint32_t polygon_count,
                           std::uint32_t polygon_list, Read32 read, Copy copy,
                           TintSnapshot& snapshot) {
    snapshot.entries = 0;
    if (!source || !polygon_list || !polygon_count ||
        polygon_count > kTintPolygonLimit) return false;
    std::uint32_t maximum = 0;
    for (std::uint32_t i = 0; i < polygon_count; ++i) {
        std::uint32_t address = 0, polygon = 0, index = 0;
        if (!tint_address(polygon_list, i * 4, address) ||
            !read(address, polygon) || !tint_address(polygon, 4, address) ||
            !read(address, index) || index >= kTintSourceCapacity) return false;
        if (!i) snapshot.sample_index = index;
        if (index > maximum) maximum = index;
    }
    const std::uint32_t length = (maximum + 1) * kTintSourceStride;
    std::uint32_t last = 0;
    if (!tint_address(source, length - 1, last) ||
        !copy(source, snapshot.bytes.data(), length)) return false;
    const std::size_t sample = snapshot.sample_index * kTintSourceStride + 4;
    snapshot.original_rgb = snapshot.bytes[sample] |
        (std::uint32_t(snapshot.bytes[sample + 1]) << 8) |
        (std::uint32_t(snapshot.bytes[sample + 2]) << 16);
    for (std::uint32_t i = 0; i <= maximum; ++i) {
        const std::size_t offset = i * kTintSourceStride + 4;
        snapshot.bytes[offset] = 255;
        snapshot.bytes[offset + 1] = 0;
        snapshot.bytes[offset + 2] = 255;
    }
    snapshot.entries = maximum + 1;
    return true;
}

struct TintLease {
    std::uint32_t manager = 0;
    std::uint32_t original = 0;
    std::uint32_t effective = 0;
    bool active = false;
};

enum class TintRestore : std::uint32_t { None, Restored, RendererReplaced, Failed };

template <typename Read32, typename Write32>
TintRestore restore_tint_source(TintLease& lease, Read32 read, Write32 write) {
    if (!lease.active) return TintRestore::None;
    std::uint32_t address = 0, current = 0;
    if (!tint_address(lease.manager, 0x558, address) ||
        !read(address, current)) return TintRestore::Failed;
    if (current != lease.effective) {
        lease.active = false;
        return TintRestore::RendererReplaced;
    }
    if (!write(address, lease.original)) return TintRestore::Failed;
    lease.active = false;
    return TintRestore::Restored;
}

inline bool tint_window(std::uint64_t elapsed_ms, std::uint32_t delay_ms,
                        std::uint32_t duration_ms) {
    return elapsed_ms >= delay_ms && elapsed_ms - delay_ms < duration_ms;
}

} // namespace sfc_m1
