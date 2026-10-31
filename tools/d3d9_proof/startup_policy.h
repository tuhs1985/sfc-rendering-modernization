// Explicit compatibility toggle; ordinary startup performs one Present.
#pragma once
#include <windows.h>
#include <stdexcept>
namespace startup_policy {
inline unsigned bootstrap_presents(){
 wchar_t value[8]{};const auto n=GetEnvironmentVariableW(L"SFC_D3D9_LEGACY_STARTUP_WARMUP",value,8);
 if(!n||!wcscmp(value,L"0"))return 1;
 if(n==1&&value[0]==L'1')return 24;
 throw std::runtime_error("Legacy startup warmup must be0or1");
}
}
