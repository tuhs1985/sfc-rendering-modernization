#pragma once
#include <windows.h>
namespace pipeline_mode {
inline bool performance(){
 wchar_t value[16]{};return GetEnvironmentVariableW(L"SFC_PIPELINE_MODE",value,16)==11&&wcscmp(value,L"performance")==0;
}
}
