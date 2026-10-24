// Worker lifetime only: live input owns stop/deadline; replay owns frame count.
#pragma once
#include <cstddef>
#include <cstdint>
namespace run_lifetime {
constexpr bool iteration(bool live,std::size_t frame,std::size_t replayFrames){
 return live||frame<replayFrames;
}
constexpr bool within_window(uint64_t now,uint64_t started,uint64_t limit){
 return now-started<limit;
}
}
