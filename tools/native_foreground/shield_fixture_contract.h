#pragma once
#include <cstdint>
namespace native_foreground::shield_hooks {
using Word=uint32_t;
using Depth=Word(__thiscall*)(void*,Word);
using Verify=void(__cdecl*)(void*,void*,void*,Word,Word,const float*,const float*);
struct FixtureTargets {Word bytes;void* shield;Depth depth;Word caller,resourceAddress;Verify verify;};
}
