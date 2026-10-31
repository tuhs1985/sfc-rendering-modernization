// Offline only: execute the pinned client's small batch flush against a fake COM sink.
// Client bytes are loaded locally into test memory; no game process or client edits.
#include <windows.h>
#include <array>
#include <fstream>
#include <vector>
#include <iostream>
#include <cstring>
static unsigned checks=0,calls=0;static DWORD abiErrors=0;
static std::array<DWORD,8> args{};
static void test(bool value){++checks;if(!value){std::cerr<<"Flush check "<<checks<<" failed\n";std::exit(1);}}
static HRESULT WINAPI indexed(DWORD self,DWORD type,DWORD fvf,DWORD vertices,DWORD count,DWORD indices,DWORD indexCount,DWORD flags){
 ++calls;args={self,type,fvf,vertices,count,indices,indexCount,flags};return S_OK;
}
static HRESULT WINAPI primitive(DWORD self,DWORD type,DWORD fvf,DWORD vertices,DWORD count,DWORD flags){
 ++calls;args={self,type,fvf,vertices,count,0,0,flags};return S_OK;
}
extern "C" __declspec(naked) void __cdecl invoke(void*,void*){
 __asm{push ebx}
 __asm{push esi}
 __asm{push edi}
 __asm{push ebp}
 __asm{mov ebp,esp}
 __asm{mov eax,[ebp+20]}
 __asm{mov ecx,[ebp+24]}
 __asm{mov ebx,11112222h}
 __asm{mov esi,33334444h}
 __asm{mov edi,55556666h}
 __asm{call eax}
 __asm{cmp esp,ebp}
 __asm{je stack_ok}
 __asm{or abiErrors,1}
 __asm{mov esp,ebp}
 stack_ok:
 __asm{cmp ebx,11112222h}
 __asm{je ebx_ok}
 __asm{or abiErrors,2}
 ebx_ok:
 __asm{cmp esi,33334444h}
 __asm{je esi_ok}
 __asm{or abiErrors,4}
 esi_ok:
 __asm{cmp edi,55556666h}
 __asm{je edi_ok}
 __asm{or abiErrors,8}
 edi_ok:
 __asm{pop ebp}
 __asm{pop edi}
 __asm{pop esi}
 __asm{pop ebx}
 __asm{ret}
}
int wmain(int argc,wchar_t** argv){
 test(argc==2);std::ifstream file(argv[1],std::ios::binary);std::vector<BYTE> bytes((std::istreambuf_iterator<char>(file)),{});
 test(bytes.size()>0x1000);auto* dos=reinterpret_cast<const IMAGE_DOS_HEADER*>(bytes.data());test(dos->e_magic==IMAGE_DOS_SIGNATURE);
 auto* nt=reinterpret_cast<const IMAGE_NT_HEADERS32*>(bytes.data()+dos->e_lfanew);test(nt->Signature==IMAGE_NT_SIGNATURE&&nt->OptionalHeader.ImageBase==0x400000);
 auto* section=IMAGE_FIRST_SECTION(nt);const BYTE* original=nullptr;
 for(unsigned i=0;i<nt->FileHeader.NumberOfSections;++i)if(0x2ab380>=section[i].VirtualAddress&&0x2ab402<=section[i].VirtualAddress+section[i].SizeOfRawData){
  const auto offset=section[i].PointerToRawData+0x2ab380-section[i].VirtualAddress;test(offset+0x82<=bytes.size());original=bytes.data()+offset;}
 test(original&&original[0]==0x56&&original[1]==0x8b&&original[2]==0xf1&&original[0x80]==0x5e&&original[0x81]==0xc3);
 test(original[0x40]==0xff&&original[0x41]==0x52&&original[0x42]==0x74&&original[0x59]==0xff&&original[0x5b]==0x70);
 auto* code=static_cast<BYTE*>(VirtualAlloc(nullptr,4096,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE));test(code!=nullptr);memcpy(code,original,0x82);
 DWORD prior{};test(VirtualProtect(code,4096,PAGE_EXECUTE_READ,&prior)!=FALSE);FlushInstructionCache(GetCurrentProcess(),code,0x82);
 std::array<DWORD,32> table{};table[0x74/4]=reinterpret_cast<DWORD>(&indexed);table[0x70/4]=reinterpret_cast<DWORD>(&primitive);
 DWORD device=reinterpret_cast<DWORD>(table.data());std::array<DWORD,2048> manager{};
 for(DWORD mode:{4u,1u,0xffffffffu})for(bool available:{false,true}){
  manager.fill(0x12345678);manager[0x1cc0/4]=available?reinterpret_cast<DWORD>(&device):0;
  manager[0x1cb0/4]=9;manager[0x1cb4/4]=3;manager[0x1cbc/4]=mode;const auto before=manager;calls=0;
  invoke(code,manager.data());test(!abiErrors);test(calls==((available&&(mode==1||mode==4))?1u:0u));
  test(manager[0x1cb0/4]==0&&manager[0x1cb4/4]==0&&manager[0x1cb8/4]==reinterpret_cast<DWORD>(manager.data())&&manager[0x1cbc/4]==0xffffffff);
  for(unsigned i=0;i<manager.size();++i)if(i<0x1cb0/4||i>0x1cbc/4)test(manager[i]==before[i]);
  if(calls){test(args[0]==reinterpret_cast<DWORD>(&device)&&args[1]==mode&&args[2]==0x1c4&&args[3]==reinterpret_cast<DWORD>(manager.data())&&args[4]==9&&args[7]==0x1c);
   if(mode==4)test(args[5]==reinterpret_cast<DWORD>(manager.data())+0x1b00&&args[6]==9);}
  // Repeat after closure: the original routine still forwards a zero-count draw
  // when the device/mode say so. The coordinator must skip an already empty batch.
  const auto empty=manager;calls=0;invoke(code,manager.data());test(!abiErrors&&calls==0&&manager==empty);
 }
 VirtualFree(code,0,MEM_RELEASE);
 std::cout<<"Pinned native flush PASS "<<checks<<" checks;ABI counters prior indexed/nonindexed batch preserved;zero batch must be skipped by coordinator\n";
}
