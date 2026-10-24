// Admission worker utility. Hash bounded prepared bytes in native code instead
// of a Python byte loop that monopolizes the light/receiver worker's GIL.
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <Windows.h>
#include <filesystem>
#include <fstream>
#include <array>
#include <iostream>
#include <stdexcept>
namespace fs=std::filesystem;
static uint64_t hash(const fs::path& path,uint64_t limit,uint64_t& bytes){
 const auto length=fs::file_size(path);if(!length||length>limit)throw std::runtime_error("file bound");
 std::ifstream in(path,std::ios::binary);if(!in)throw std::runtime_error("file open");
 uint64_t value=14695981039346656037ull;std::array<char,65536> block{};uint64_t total=0;
 while(in){in.read(block.data(),block.size());const auto n=in.gcount();total+=static_cast<uint64_t>(n);
  for(std::streamsize i=0;i<n;++i){value^=static_cast<BYTE>(block[static_cast<size_t>(i)]);value*=1099511628211ull;}}
 if(total!=length||!in.eof())throw std::runtime_error("file changed/read failure");bytes=total;return value;
}
int wmain(int argc,wchar_t** argv){try{
 if(argc!=3)throw std::runtime_error("folder and texture count required");
 wchar_t* end=nullptr;const auto count=wcstoul(argv[2],&end,10);if(*end||!count||count>256)throw std::runtime_error("image count");
 const fs::path root(argv[1]);uint64_t geometry=0,images=0;
 const auto replay=hash(root/L"scene.bin",2*1024*1024,geometry);uint64_t textures=14695981039346656037ull;
 for(unsigned i=0;i<count;++i){uint64_t bytes=0;const auto h=hash(root/(L"texture-"+std::to_wstring(i)+L".bin"),64*1024*1024+16,bytes);
  images+=bytes;if(images>128*1024*1024)throw std::runtime_error("aggregate image bound");textures^=h;textures*=1099511628211ull;}
 std::cout<<geometry<<' '<<images<<' '<<replay<<' '<<textures<<'\n';return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
