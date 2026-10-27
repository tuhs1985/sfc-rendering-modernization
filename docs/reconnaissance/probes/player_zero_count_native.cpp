// Offline x86 ONLY. Execute pinned client instruction excerpts in a test process.
// No game launch/injection/patching. State vtable calls are explicit test doubles.
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <array>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <vector>
#include <cstring>

static_assert(sizeof(void*)==4,"x86 qualification required");
static unsigned checks=0;
static DWORD flagsValue=0,branchValue=0,availableValue=0,modeValue=0,state90=1,stateA0=0;
static unsigned modeCalls=0,prepareCalls=0;static DWORD observedCount=~0u;
static void* prepareCode=nullptr;static void* callCode=nullptr;static void* object=nullptr;
static void* polygonList=nullptr;static DWORD callCount=0,callFlag=1,callResult=0;
static DWORD stackBefore=0,abiGood=0;
static void test(bool b){++checks;if(!b){std::cerr<<"check="<<checks<<" bits="<<flagsValue<<" branch="<<branchValue<<" prepares="<<prepareCalls<<" modes="<<modeCalls<<" abi="<<abiGood<<" state90="<<state90<<" stateA0="<<stateA0<<" result="<<(callResult&255)<<'\n';throw std::runtime_error("zero-count check failed");}}
static DWORD __fastcall flags(void*,void*){return flagsValue;}
static DWORD __fastcall branch(void*,void*){return branchValue;}
static DWORD __fastcall available(void*,void*){return availableValue;}
static DWORD __fastcall lighting(void* self,void*,DWORD value){
 auto* p=static_cast<BYTE*>(self)+0x1ed8;const DWORD old=*p;*p=static_cast<BYTE>(value);return old;
}
static DWORD __fastcall mode(void*,void*,DWORD value){const auto old=modeValue;modeValue=value;++modeCalls;return old;}
static DWORD __fastcall set90(void*,void*,DWORD value){const auto old=state90;state90=value&255;return old;}
static DWORD __fastcall setA0(void*,void*,DWORD value){const auto old=stateA0;stateA0=value&255;return old;}
static DWORD __fastcall setA4(void*,void*,DWORD,DWORD){return 1;}
static DWORD __fastcall restoreLight(void* self,void*,DWORD value){
 static_cast<BYTE*>(self)[0x1ed8]=static_cast<BYTE>(value);return 1;
}
static void __declspec(naked) prepareGateway(){__asm{
 inc prepareCalls
 mov eax,[esp+8]
 mov observedCount,eax
 jmp prepareCode
}}
// Check the real excerpt's callee-saved registers and exact stack cleanup.
static void __declspec(naked) invoke(){__asm{
 push ebp
 push ebx
 push esi
 push edi
 mov stackBefore,esp
 mov ebp,11223344h
 mov ebx,22334455h
 mov esi,33445566h
 mov edi,44556677h
 push callFlag
 push polygonList
 push callCount
 mov ecx,object
 call callCode
 mov callResult,eax
 mov abiGood,0
 cmp esp,stackBefore
 jne failed
 cmp ebp,11223344h
 jne failed
 cmp ebx,22334455h
 jne failed
 cmp esi,33445566h
 jne failed
 cmp edi,44556677h
 jne failed
 mov abiGood,1
failed:
 mov esp,stackBefore
 pop edi
 pop esi
 pop ebx
 pop ebp
 ret
}}
static void* load(const char* file){
 std::ifstream f(file,std::ios::binary);if(!f)throw std::runtime_error("Missing pinned excerpt");
 std::vector<char> bytes((std::istreambuf_iterator<char>(f)),{});
 if(bytes.empty()||bytes.size()>4096)throw std::runtime_error("Excerpt size");
 auto* p=VirtualAlloc(nullptr,bytes.size(),MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);
 if(!p)throw std::runtime_error("Excerpt allocation");memcpy(p,bytes.data(),bytes.size());DWORD old=0;
 if(!VirtualProtect(p,bytes.size(),PAGE_EXECUTE_READ,&old))throw std::runtime_error("Excerpt protection");
 FlushInstructionCache(GetCurrentProcess(),p,bytes.size());return p;
}
int main(){try{
 callCode=load("wrapper.bin");prepareCode=load("prepare.bin");
 std::array<DWORD,128> table{};std::array<BYTE,0x2400> manager{};object=manager.data();
 *reinterpret_cast<DWORD*>(manager.data())=reinterpret_cast<DWORD>(table.data());
 *reinterpret_cast<DWORD*>(manager.data()+4)=0x1234;
 *reinterpret_cast<DWORD*>(manager.data()+0x554)=1;
 *reinterpret_cast<DWORD*>(manager.data()+0x558)=1;
 table[0x17c/4]=reinterpret_cast<DWORD>(&flags);table[0x180/4]=reinterpret_cast<DWORD>(&prepareGateway);
 table[0xbc/4]=reinterpret_cast<DWORD>(&lighting);table[0x24/4]=reinterpret_cast<DWORD>(&branch);
 table[0xd0/4]=reinterpret_cast<DWORD>(&available);table[0xd4/4]=reinterpret_cast<DWORD>(&mode);
 table[0x90/4]=reinterpret_cast<DWORD>(&set90);table[0xa0/4]=reinterpret_cast<DWORD>(&setA0);
 table[0xa4/4]=reinterpret_cast<DWORD>(&setA4);table[0xb8/4]=reinterpret_cast<DWORD>(&restoreLight);
 polygonList=VirtualAlloc(nullptr,4096,MEM_COMMIT|MEM_RESERVE,PAGE_NOACCESS);test(polygonList!=nullptr);
 for(DWORD bits=0;bits<4;++bits)for(DWORD branchFlags:{0u,0x20u})for(BYTE light:{BYTE(0),BYTE(1)})for(DWORD ready:{0u,1u}){
  flagsValue=bits;branchValue=branchFlags;availableValue=ready;modeCalls=prepareCalls=0;observedCount=~0u;
  manager[0x1ed8]=light;const auto before=manager;modeValue=0;state90=1;stateA0=0;
  invoke();test(abiGood==1);test((callResult&255)==1);test(observedCount==0);
  test(prepareCalls==1||prepareCalls==2);test(branchFlags&&ready?modeCalls==0:modeCalls>=1);
  test(manager==before);test(state90==1&&stateA0==0);
 }
 VirtualFree(polygonList,0,MEM_RELEASE);VirtualFree(prepareCode,0,MEM_RELEASE);VirtualFree(callCode,0,MEM_RELEASE);
 std::cout<<"Pinned x86 zero-count PASS checks="<<checks
 <<" wrapper_cases=32 unreadable_polygon_list=1 callee_saved_stack=1 manager_bytes_unchanged=1 state_methods=STUBBED not_gameplay=1\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}return 0;}
