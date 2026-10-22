// Worker-only identity adapter for pinned Remix texture upload hashing.
#define XXH_INLINE_ALL
#include <xxhash.h>
#include <fstream>
#include <iostream>
#include <vector>
#include <cstdint>
#include <cstring>
#include <filesystem>
static int hashFile(const std::filesystem::path& path,size_t& total){
 std::ifstream f(path,std::ios::binary|std::ios::ate);
 if(!f||f.tellg()<16||f.tellg()>64*1024*1024+16)return 3;
 const auto n=static_cast<size_t>(f.tellg());f.seekg(0);std::vector<char> b(n);f.read(b.data(),n);
 total+=n;if(total>128*1024*1024)return 5;
 uint32_t h[4]{};memcpy(h,b.data(),16);
 if(!f||h[0]!=0x31544653||!h[1]||h[1]>4096||!h[2]||h[2]>4096||h[3]!=uint64_t(h[1])*h[2]*4||n!=16ull+h[3])return 4;
 std::cout<<std::hex<<XXH3_64bits(b.data()+16,h[3])<<'\n';return 0;
}
int wmain(int argc,wchar_t** argv){
 size_t total=0;if(argc==2)return hashFile(argv[1],total);
 if(argc!=4||wcscmp(argv[1],L"--batch"))return 2;
 wchar_t* end=nullptr;const auto count=wcstoul(argv[3],&end,10);if(!count||count>256||!end||*end)return 2;
 for(unsigned i=0;i<count;++i){const auto status=hashFile(std::filesystem::path(argv[2])/(L"texture-"+std::to_wstring(i)+L".bin"),total);if(status)return status;}
 return 0;
}
