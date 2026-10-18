#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include "../tools/remix_runtime/return_wire.h"
#include <aclapi.h>
#include <limits>
#include <iostream>
static unsigned count=0;
static void test(bool value){++count;if(!value)throw std::runtime_error("return wire test");}
int main(){
  using namespace return_path;
  try{
    test(sizeof(State)==256);test(offsetof(State,sharedHandle)==32);test(offsetof(State,epoch)==64);test(offsetof(State,renderEpoch)==136);test(offsetof(State,visibilityScope)==176);
    State s{};s.magic=Magic;s.version=Version;s.bytes=sizeof(State);s.creatorPid=1;s.width=s.height=256;s.format=Format;s.qpcFrequency=1000;test(valid(s));
    auto bad=s;bad.magic=0;test(!valid(bad));bad=s;bad.version=1;test(!valid(bad));bad=s;bad.bytes=128;test(!valid(bad));bad=s;bad.width=4096;test(!valid(bad));bad=s;bad.height=0;test(!valid(bad));bad=s;bad.qpcFrequency=0;test(!valid(bad));bad=s;bad.creatorPid=0;test(!valid(bad));bad=s;bad.format=0;test(!valid(bad));
    test(fresh(1000,1000,1000));test(fresh(1000,2000,1000));test(!fresh(1000,2001,1000));test(!fresh(1000,999,1000));test(!fresh(0,100,1000));test(!fresh(1,100,0));
    test(displaySupported(800,600));test(displaySupported(1920,1080));test(!displaySupported(1921,1080));test(!displaySupported(544,383));test(!displaySupported(543,384));test(!displaySupported(std::numeric_limits<float>::quiet_NaN(),600));test(!displaySupported(800,std::numeric_limits<float>::infinity()));
    Mapping channel(true);test(valid(*channel.state));
    PSECURITY_DESCRIPTOR sd=nullptr;PACL acl=nullptr;test(GetSecurityInfo(channel.handle,SE_KERNEL_OBJECT,DACL_SECURITY_INFORMATION,nullptr,nullptr,&acl,nullptr,&sd)==ERROR_SUCCESS);test(acl&&acl->AceCount==1);void* ace=nullptr;test(GetAce(acl,0,&ace)!=FALSE);
    auto* allowed=static_cast<ACCESS_ALLOWED_ACE*>(ace);test(allowed->Header.AceType==ACCESS_ALLOWED_ACE_TYPE);
    HANDLE token=nullptr;test(OpenProcessToken(GetCurrentProcess(),TOKEN_QUERY,&token)!=FALSE);alignas(TOKEN_USER) std::array<unsigned char,1024> user{};DWORD size=0;
    test(GetTokenInformation(token,TokenUser,user.data(),static_cast<DWORD>(user.size()),&size)!=FALSE);CloseHandle(token);test(EqualSid(&allowed->SidStart,reinterpret_cast<TOKEN_USER*>(user.data())->User.Sid)!=FALSE);LocalFree(sd);
    {Mapping peer(false,channel.name.c_str());test(peer.state->creatorPid==GetCurrentProcessId());}
    bool rejected=false;try{Mapping invalid(false,L"Local\\SFCBridge_other");}catch(...){rejected=true;}test(rejected);
    std::cout<<"Return wire PASS "<<count<<" checks, size="<<sizeof(State)<<"\n";return 0;
  }catch(const std::exception& e){std::cout<<"FAILED "<<e.what()<<"\n";return 1;}
}
