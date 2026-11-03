#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <vector>
#include <string>
#include <iostream>
#include <stdexcept>
static void require(bool okay,const char* why){if(!okay)throw std::runtime_error(why);}
#include "../tools/d3d9_proof/output_channel.h"
#include "../tools/d3d9_proof/texture_memory.h"
int wmain(int argc,wchar_t** argv){try{
 require(argc==4,"arguments");DWORD session[4]{};const std::wstring text=argv[1];require(text.size()==32,"session");
 for(unsigned i=0;i<4;++i)session[i]=wcstoul(text.substr(i*8,8).c_str(),nullptr,16);
 // The fixture passes the expected immutable catalog packet as hex, never an asset file.
 const std::wstring hex=argv[2];require(hex.size()==sizeof(multi_scene::Asset)*2,"catalog");multi_scene::Asset a{};
 for(unsigned i=0;i<sizeof(a);++i)reinterpret_cast<BYTE*>(&a)[i]=BYTE(wcstoul(hex.substr(i*2,2).c_str(),nullptr,16));
 const auto images=texture_memory::receive(session,a,DWORD(_wtoi(argv[3])));
 uint64_t bytes=0;for(const auto& image:images)bytes+=image.size();
 std::cout<<"TEXTURES_PASS count="<<images.size()<<" bytes="<<bytes<<'\n';return 0;
 }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
