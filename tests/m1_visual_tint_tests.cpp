#include "../tools/m1_component/m1_visual_tint.h"

#include <cstdlib>
#include <cstring>
#include <iostream>
#include <map>

namespace {
void require(bool value, const char* message) {
    if (!value) { std::cerr << "FAIL: " << message << '\n'; std::exit(1); }
}
}

int main() {
    std::map<std::uint32_t, std::uint32_t> memory{
        {0x1000, 0x2000}, {0x1004, 0x2100}, {0x2004, 2}, {0x2104, 0}
    };
    std::array<std::uint8_t, 108> original{};
    for (std::size_t i = 0; i < original.size(); ++i)
        original[i] = static_cast<std::uint8_t>(i);
    auto read = [&](std::uint32_t address, std::uint32_t& value) {
        auto it = memory.find(address);
        if (it == memory.end()) return false;
        value = it->second; return true;
    };
    auto copy = [&](std::uint32_t address, void* target, std::uint32_t count) {
        if (address != 0x3000 || count > original.size()) return false;
        std::memcpy(target, original.data(), count); return true;
    };
    sfc_m1::TintSnapshot snapshot;
    require(sfc_m1::prepare_tint_snapshot(0x3000, 2, 0x1000, read, copy, snapshot),
            "referenced sparse indices determine bounded copy size");
    require(snapshot.entries == 3 && snapshot.sample_index == 2,
            "source entry count and sample correspond to polygon index");
    require(snapshot.original_rgb == (76u | (77u << 8) | (78u << 16)),
            "original RGB is retained as evidence");
    for (std::size_t i = 0; i < original.size(); ++i) {
        const auto channel = i % 36;
        const auto expected = channel == 4 || channel == 6 ? 255 :
                              channel == 5 ? 0 : original[i];
        require(snapshot.bytes[i] == expected, "only copied RGB bytes change");
        require(original[i] == static_cast<std::uint8_t>(i), "original remains intact");
    }
    memory[0x2004] = 256;
    require(!sfc_m1::prepare_tint_snapshot(0x3000, 2, 0x1000, read, copy, snapshot),
            "source index overflow fails open");
    require(snapshot.entries == 0, "failed snapshot cannot be applied");
    memory[0x2004] = 255;
    require(!sfc_m1::prepare_tint_snapshot(0x3000, 2, 0x1000, read, copy, snapshot),
            "inaccessible source extent refuses substitution");
    std::array<std::uint8_t, 36 * 256> large_source{};
    auto large_copy = [&](std::uint32_t address, void* target, std::uint32_t count) {
        if (address != 0x3000 || count != large_source.size()) return false;
        std::memcpy(target, large_source.data(), count); return true;
    };
    require(sfc_m1::prepare_tint_snapshot(0x3000, 2, 0x1000, read, large_copy, snapshot) &&
            snapshot.entries == 256 && snapshot.bytes[255 * 36 + 6] == 255,
            "highest supported source index remains bounded and tintable");
    memory[0x2004] = 2;
    require(!sfc_m1::prepare_tint_snapshot(0x3000, 4097, 0x1000, read, copy, snapshot),
            "polygon flood is refused");
    require(!sfc_m1::prepare_tint_snapshot(0x3000, 2, 0xFFFFFFFC, read, copy, snapshot),
            "list arithmetic overflow is refused");
    require(!sfc_m1::prepare_tint_snapshot(0x3000, 0, 0x1000, read, copy, snapshot),
            "empty list is not an intervention");
    require(!sfc_m1::prepare_tint_snapshot(0xFFFFFFF0, 2, 0x1000, read, copy, snapshot),
            "source extent overflow is refused");
    memory.erase(0x2104);
    require(!sfc_m1::prepare_tint_snapshot(0x3000, 2, 0x1000, read, copy, snapshot),
            "unreadable polygon refuses substitution");

    sfc_m1::TintLease lease{0x4000, 0x3000, 0x5000, true};
    memory[0x4558] = 0x5000;
    auto write = [&](std::uint32_t address, std::uint32_t value) {
        memory[address] = value; return true;
    };
    require(sfc_m1::restore_tint_source(lease, read, write) ==
            sfc_m1::TintRestore::Restored && memory[0x4558] == 0x3000 && !lease.active,
            "stop/exit release restores our pointer");
    lease.active = true; memory[0x4558] = 0x6000;
    require(sfc_m1::restore_tint_source(lease, read, write) ==
            sfc_m1::TintRestore::RendererReplaced && memory[0x4558] == 0x6000,
            "renderer-authored replacement is preserved");
    lease.active = true; memory[0x4558] = 0x5000;
    auto no_write = [](std::uint32_t, std::uint32_t) { return false; };
    require(sfc_m1::restore_tint_source(lease, read, no_write) ==
            sfc_m1::TintRestore::Failed && lease.active,
            "failed release remains live and must block hook removal");
    memory.erase(0x4558);
    require(sfc_m1::restore_tint_source(lease, read, write) ==
            sfc_m1::TintRestore::Failed && lease.active,
            "unreadable manager does not falsely certify cleanup");
    require(!sfc_m1::tint_window(4999, 5000, 10000) &&
            sfc_m1::tint_window(5000, 5000, 10000) &&
            sfc_m1::tint_window(14999, 5000, 10000) &&
            !sfc_m1::tint_window(15000, 5000, 10000),
            "baseline/on/off window has exact boundaries");
    std::cout << "All M1 visual tint tests passed.\n";
}
