#include "../tools/m1_component/m1_contract.h"

#include <cstdlib>
#include <iostream>
#include <vector>

namespace {

void require(bool condition, const char* message) {
    if (!condition) {
        std::cerr << "FAIL: " << message << "\n";
        std::exit(1);
    }
}

}  // namespace

int main() {
    sfc_m1::OwnerTable<2> owners;
    auto first = owners.observe(0x1000, 0x2000, 1);
    require(first.id == 1 && first.first_seen && !first.overflow,
            "first observation assigns identity");

    auto repeated = owners.observe(0x1000, 0x2000, 2);
    require(repeated.id == 1 && !repeated.first_seen,
            "active pointer keeps its epoch identity");

    auto second = owners.observe(0x3000, 0x4000, 2);
    require(second.id == 2 && owners.find_by_visual(0x4000) == 2,
            "second owner remains distinguishable");

    auto overflow = owners.observe(0x5000, 0x6000, 2);
    require(overflow.overflow && overflow.id == 0,
            "active-capacity overflow fails open");

    std::vector<std::uint32_t> retired;
    owners.retire_before(3, [&](const auto& slot) { retired.push_back(slot.id); });
    require(retired.size() == 2 && owners.active_count() == 0,
            "age rule retires inactive epochs");

    auto reused = owners.observe(0x1000, 0x2000, 4);
    require(reused.id == 3 && reused.first_seen,
            "retired raw pointer receives a new epoch identity");

    sfc_m1::BoundedBuffer<int, 2> buffer;
    require(buffer.push(10) && buffer.push(20), "buffer accepts capacity");
    require(!buffer.push(30) && buffer.saturated() && buffer.size() == 2,
            "buffer rejects overflow without growing");

    std::cout << "All M1 contract tests passed.\n";
    return 0;
}
