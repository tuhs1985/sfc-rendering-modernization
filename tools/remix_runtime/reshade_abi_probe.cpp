#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <imgui.h>
#include <reshade.hpp>
#include <iostream>
int wmain(int argc,wchar_t** argv){
  std::cout.setf(std::ios::unitbuf);
  if(argc!=2)return 2;
  auto module=LoadLibraryW(argv[1]);
  if(!module){std::cout<<"load_error="<<GetLastError()<<"\n";return 3;}
  std::cout<<"header_api="<<RESHADE_API_VERSION<<" imgui="<<IMGUI_VERSION_NUM<<"\n";
  const bool registered=reshade::register_addon(GetModuleHandleW(nullptr),module);
  std::cout<<"supported_api_and_imgui="<<registered<<"\n";
  if(registered)reshade::unregister_addon(GetModuleHandleW(nullptr),module);
  FreeLibrary(module);
  return registered?0:4;
}
