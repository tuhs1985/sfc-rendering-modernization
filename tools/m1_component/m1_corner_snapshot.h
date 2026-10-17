#pragma once
#include "m1_visual_tint.h"

namespace sfc_m1 {
constexpr std::size_t kCornerPolygonLimit = 64;
constexpr std::size_t kCornersPerPolygon = 8;
constexpr std::uint32_t kCornerAdvertisedPolygonLimit = 65536;
constexpr std::uint32_t kCornerWindows = 18;
constexpr std::uint32_t kCornerWindowMs = 5000;
constexpr std::uint32_t kCornerPacketBytes = 3 * 1024 * 1024;
struct CornerInput {
    std::uint32_t polygon = 0, index = 0;
    std::array<std::uint32_t, 3> vector{}, position{};
};
struct PolygonInput {
    std::uint32_t address = 0, source_index = 0, count = 0, source_flags = 0;
    std::array<std::uint32_t, 3> vector{};
};
struct CornerSnapshot {
    std::uint32_t elapsed_ms = 0, window = 0, owner = 0, thread = 0;
    std::uint32_t filter = 0;
    std::uint32_t ship = 0, visual = 0, model = 0, manager = 0, source = 0;
    std::uint32_t vertex_count = 0, vertex_base = 0, polygon_count = 0;
    std::uint32_t polygons = 0, corners = 0, status = 0;
    bool truncated = false;
    std::array<std::uint32_t, 17> object_transform{}, position_transform{};
    std::array<std::uint32_t, 3> dispatch{};
    std::array<PolygonInput, kCornerPolygonLimit> polygon_data{};
    std::array<CornerInput, kCornerPolygonLimit * kCornersPerPolygon> corner_data{};
};

// Status 0 complete; 1 unreadable/overflow; 2 unsupported counts/indices.
// Raw float bits are preserved, not guessed, normalized, or written to SFC.
template <typename Read32, typename Copy>
bool capture_corner_inputs(CornerSnapshot& out, Read32 read, Copy copy) {
    auto word = [&](std::uint32_t base, std::uint32_t offset, std::uint32_t& value) {
        std::uint32_t address = 0;
        return tint_address(base, offset, address) && read(address, value);
    };
    auto block = [&](std::uint32_t base, std::uint32_t offset, void* target, std::uint32_t size) {
        std::uint32_t address = 0, end = 0;
        return tint_address(base, offset, address) && tint_address(address, size - 1, end) &&
            copy(address, target, size);
    };
    out.polygons = out.corners = out.status = 0; out.truncated = false;
    std::uint32_t vtable = 0, list = 0;
    if (!word(out.manager, 0, vtable) || vtable != 0x007B8D4C ||
        !word(out.model, 8, out.vertex_count) || !word(out.model, 12, out.vertex_base) ||
        !word(out.model, 16, out.polygon_count) || !word(out.model, 20, list) ||
        !block(out.manager, 0x6F4, out.object_transform.data(), 68) ||
        !block(out.manager, 0x6B0, out.position_transform.data(), 68) ||
        !read(0x00C69FF0, out.dispatch[0]) || !read(0x00C69FF4, out.dispatch[1]) ||
        !read(0x00C74058, out.dispatch[2])) { out.status = 1; return false; }
    if (!out.vertex_count || out.vertex_count > 65536 || !out.vertex_base || !list ||
        !out.source || !out.polygon_count || out.polygon_count > kCornerAdvertisedPolygonLimit) {
        out.status = 2; return false;
    }
    out.truncated = out.polygon_count > kCornerPolygonLimit;
    for (std::uint32_t p = 0; p < out.polygon_count && p < kCornerPolygonLimit; ++p) {
        auto& polygon = out.polygon_data[p];
        std::uint32_t corner_base = 0;
        if (!word(list, p * 4, polygon.address) || !word(polygon.address, 0, polygon.count) ||
            !word(polygon.address, 4, polygon.source_index) ||
            !word(polygon.address, 0x18, corner_base) ||
            !block(polygon.address, 8, polygon.vector.data(), 12)) { out.status = 1; return false; }
        if (!polygon.count || polygon.count > 256 || polygon.source_index >= kTintSourceCapacity) {
            out.status = 2; return false;
        }
        if (!word(out.source, polygon.source_index * kTintSourceStride, polygon.source_flags)) {
            out.status = 1; return false;
        }
        ++out.polygons;
        if (polygon.count > kCornersPerPolygon) out.truncated = true;
        for (std::uint32_t c = 0; c < polygon.count && c < kCornersPerPolygon; ++c) {
            auto& corner = out.corner_data[out.corners];
            std::uint16_t index = 0;
            corner.polygon = p;
            if (!block(corner_base, c * 28, &index, 2) ||
                !block(corner_base, c * 28 + 4, corner.vector.data(), 12)) {
                out.status = 1; return false;
            }
            corner.index = index;
            if (corner.index >= out.vertex_count) { out.status = 2; return false; }
            if (!block(out.vertex_base, corner.index * 12, corner.position.data(), 12)) {
                out.status = 1; return false;
            }
            ++out.corners;
        }
    }
    return true;
}
} // namespace sfc_m1
