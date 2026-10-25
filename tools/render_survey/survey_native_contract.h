#pragma once
#include <windows.h>
#include <cstdint>
namespace survey_native {
using Word=uint32_t;
using Set=Word(__thiscall*)(void*,Word,Word);
using Gate=Word(__thiscall*)(void*,Word);
using Dispatch=Word(__cdecl*)(Word);
struct Targets {Set set=nullptr,enable=nullptr;Gate gate=nullptr;Dispatch dispatch=nullptr;Word head=0;};
enum Event:Word {LightPart=35,LightControl,EffectCensus,NativeStatus};
}
