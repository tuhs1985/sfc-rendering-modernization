#include "../tools/remix_runtime/broad_trace.h"
#include <iostream>
int wmain(){
 using namespace broad_trace;
 unsigned checks=0;
 auto check=[&](bool ok){++checks;if(!ok)throw std::runtime_error("broad native check failed");};
 check(sizeof(Header)==128&&sizeof(Record)==128);
 check(fits(128,128,256));check(!fits(128,129,256));check(!fits(UINT64_MAX,1,2000000000));
 return_path::Mapping mapping(true);auto& s=*mapping.state;
 wchar_t base[1024]{};GetCurrentDirectoryW(1024,base);
 std::wstring path=std::wstring(base)+L"\\broad-native-"+std::to_wstring(GetCurrentProcessId())+L".bin";
 // Process-resident like production; do not destroy storage while worker active.
 auto* trace=new Trace();check(!trace->prepare(&s,path.c_str(),UINT64_MAX));
 check(trace->prepare(&s,path.c_str(),4096,100));
 auto* h=reinterpret_cast<Header*>(reinterpret_cast<BYTE*>(&s)+256);
 auto until=GetTickCount64()+3000;while(h->status==1&&GetTickCount64()<until)Sleep(1);
 check(h->status==2);return_path::write(s.armed,1);
 for(unsigned i=0;i<100000;++i)trace->emit(Draw,i,1);
 until=GetTickCount64()+3000;while(h->status==2&&GetTickCount64()<until)Sleep(1);
 check(h->status==3&&h->error==0);check(h->fileBytes<=4096);check(h->reason==2&&h->dropped>0);
 HANDLE f=CreateFileW(path.c_str(),GENERIC_READ,FILE_SHARE_READ,nullptr,OPEN_EXISTING,0,nullptr);
 check(f!=INVALID_HANDLE_VALUE);LARGE_INTEGER size{};check(GetFileSizeEx(f,&size)&&uint64_t(size.QuadPart)==h->fileBytes);CloseHandle(f);
 // Invalid output path: explicit writer error without a rendering dependency.
 return_path::Mapping missing(true);auto* bad=new Trace();check(bad->prepare(missing.state,L"Z:\\SFC-path-does-not-exist\\broad.bin",4096,100));
 auto* bh=reinterpret_cast<Header*>(reinterpret_cast<BYTE*>(missing.state)+256);
 until=GetTickCount64()+3000;while(bh->status==1&&GetTickCount64()<until)Sleep(1);
 check(bh->status==4&&bh->error==1);
 std::cout<<"Broad native PASS "<<checks<<" checks; retained "<<h->fileBytes<<" bytes, drops "<<h->dropped<<"\n";
 return 0;
}
