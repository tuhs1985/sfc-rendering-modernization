#pragma once
#include <cstdint>
namespace scene_capacity {
// Preallocated transport memory budgets,not limits on SFC gameplay.
// Overflow leaves affected owners native;it must never stop other objects.
constexpr std::uint32_t StateBytes=128*1024,StateStride=512;
constexpr std::uint32_t CatalogBytes=128*1024,CatalogStride=128;
constexpr std::uint32_t Owners=StateBytes/StateStride,Assets=CatalogBytes/CatalogStride;
constexpr std::uint32_t StateOffset=8*1024*1024+65536;
constexpr std::uint32_t CohortOffset=8*1024*1024+256*1024;
constexpr std::uint32_t SceneOffset=9*1024*1024;
constexpr std::uint32_t Version=4;
static_assert(StateOffset+StateBytes<=CohortOffset);
}
