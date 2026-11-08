#pragma once
#include <windows.h>
namespace pipeline_mode {
inline bool play_session(){wchar_t value[2]{};return GetEnvironmentVariableW(L"SFC_PLAY_SESSION",value,2)==1&&value[0]==L'1';}
inline bool performance(){
 wchar_t value[16]{};return GetEnvironmentVariableW(L"SFC_PIPELINE_MODE",value,16)==11&&wcscmp(value,L"performance")==0;
}
}
