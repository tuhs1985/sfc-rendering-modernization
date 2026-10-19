// Offline parser/last-good checks. Uses only its own process-specific directory.
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <fstream>
#include <cmath>
#include <cstring>
#include <filesystem>
#include <iostream>
#include <limits>
namespace ship_triplet {
inline uint64_t hash(const void* raw,size_t size){const auto* p=static_cast<const unsigned char*>(raw);uint64_t h=14695981039346656037ull;for(size_t i=0;i<size;++i)h=(h^p[i])*1099511628211ull;return h;}
}
#include "../tools/remix_runtime/remix_material_controls.h"
int main(){
 const auto original=std::filesystem::current_path();const auto directory=original/("material-unit-"+std::to_string(GetCurrentProcessId()));
 if(!std::filesystem::create_directory(directory))return 2;std::filesystem::current_path(directory);
 unsigned checks=0;bool pass=true;auto require=[&](bool yes){++checks;pass&=yes;};
 RemixMaterialControls state;require(!state.read());require(state.values[0]==1&&state.values[1]==1);
 std::array<BYTE,56> bytes{};uint32_t h[2]{0x3143544d,1};memcpy(bytes.data(),h,8);
 std::array<float,10> values{.4f,2,.2f,0,1,1,1,1,1,1};
 auto write=[&](size_t count=56){memcpy(bytes.data()+8,values.data(),40);const auto digest=ship_triplet::hash(bytes.data(),48);memcpy(bytes.data()+48,&digest,8);std::ofstream f("material-controls.bin",std::ios::binary);f.write(reinterpret_cast<const char*>(bytes.data()),count);};
 write();require(state.read());require(state.values[0]==.4f&&state.values[1]==2);const auto accepted=state.revision;require(!state.read());
 values[0]=2;write();require(!state.read());require(state.revision==accepted&&state.values[0]==.4f);
 values[0]=std::numeric_limits<float>::quiet_NaN();write();require(!state.read());
 values[0]=.5f;write(55);require(!state.read());
 write();bytes[55]^=1;{std::ofstream f("material-controls.bin",std::ios::binary);f.write(reinterpret_cast<const char*>(bytes.data()),bytes.size());}require(!state.read());
 write();require(state.read());require(state.values[0]==.5f);
 values[4]=.5f;write();require(!state.read());require(state.values[4]==0.f);
 h[1]=2;memcpy(bytes.data(),h,8);values={.2f,5,0,0,1,.5f,0,1,0,1};write();require(state.read());require(state.values[4]==1);
 values[7]=0;write();require(!state.read());require(state.values[7]==1);
 values[7]=1;values[8]=.5f;write();require(!state.read());
 values[8]=0;values[9]=0;write();require(!state.read());
 require(materialReceipt(123,123,1));require(std::filesystem::file_size("material-receipt.bin")==40);
 require(materialReceipt(456,123,2));require(std::filesystem::file_size("material-receipt.bin")==40);
 std::filesystem::remove("material-receipt.bin");std::filesystem::remove("material-controls.bin");std::filesystem::current_path(original);std::filesystem::remove(directory);
 std::cout<<"REMIX_MATERIAL_CONTROL_"<<(pass?"PASS":"FAIL")<<" checks="<<checks<<" bytes=56\n";return pass?0:1;
}
