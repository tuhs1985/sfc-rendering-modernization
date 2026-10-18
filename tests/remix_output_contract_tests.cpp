#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include "../tools/remix_runtime/output_channel.h"
#include <aclapi.h>
#include <iostream>
static unsigned checks=0;
static void test(bool good){++checks;if(!good)throw std::runtime_error("contract test");}
int main(){
  using namespace output_probe;
  try{
    State s{};s.magic=kMagic;s.version=kVersion;s.bytes=sizeof(s);s.creatorPid=1;s.width=s.height=256;s.format=DXGI_FORMAT_B8G8R8A8_UNORM;
    test(valid(s));test(canPublish(s,1));test(!canPublish(s,0));test(!canPublish(s,3));
    auto bad=s;bad.magic=0;test(!valid(bad));bad=s;bad.version=2;test(!valid(bad));bad=s;bad.bytes=4096;test(!valid(bad));
    bad=s;bad.width=0;test(!valid(bad));bad=s;bad.height=8192;test(!valid(bad));bad=s;bad.format=DXGI_FORMAT_UNKNOWN;test(!valid(bad));
    bad=s;bad.reserved=1;test(!valid(bad));bad=s;bad.creatorPid=0;test(!valid(bad));
    store(s.produced,1);test(!canPublish(s,2));test(canConsume(s,0,1));test(!canConsume(s,1,1));test(!canConsume(s,0,2));
    store(s.consumed,1);test(canPublish(s,2));store(s.error,1);test(!canPublish(s,2));store(s.error,0);store(s.stop,1);test(!canPublish(s,2));
    Channel channel(true);test(valid(*channel.state));
    PSECURITY_DESCRIPTOR sd=nullptr;PACL acl=nullptr;
    test(GetSecurityInfo(channel.mapping.value,SE_KERNEL_OBJECT,DACL_SECURITY_INFORMATION,nullptr,nullptr,&acl,nullptr,&sd)==ERROR_SUCCESS);
    test(acl&&acl->AceCount==1);void* ace=nullptr;test(GetAce(acl,0,&ace)!=FALSE);
    auto* allow=static_cast<ACCESS_ALLOWED_ACE*>(ace);test(allow->Header.AceType==ACCESS_ALLOWED_ACE_TYPE);
    Handle token;test(OpenProcessToken(GetCurrentProcess(),TOKEN_QUERY,&token.value)!=FALSE);
    alignas(TOKEN_USER) std::array<unsigned char,1024> user{};DWORD count=0;
    test(GetTokenInformation(token.value,TokenUser,user.data(),static_cast<DWORD>(user.size()),&count)!=FALSE);
    test(EqualSid(&allow->SidStart,reinterpret_cast<TOKEN_USER*>(user.data())->User.Sid)!=FALSE);LocalFree(sd);
    {Channel sameUser(false,channel.name.c_str());test(sameUser.state->creatorPid==GetCurrentProcessId());}
    bool rejected=false;try{Channel wrong(false,L"Local\\UnrelatedMapping");}catch(...){rejected=true;}test(rejected);
    store(channel.state->error,1);rejected=false;try{channel.wait(channel.state->ready,1,1);}catch(...){rejected=true;}test(rejected);
    std::cout<<"Output contract tests PASS: "<<checks<<" checks; no GPU/runtime loaded\n";
    return 0;
  }catch(const std::exception& e){std::cout<<"FAILED "<<e.what()<<"\n";return 1;}
}
