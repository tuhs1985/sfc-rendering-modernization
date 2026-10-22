#include "../tools/d3d9_proof/worker_poll.h"
#include <iostream>
int main(){
 try{
  SetEnvironmentVariableW(L"SFC_D3D9_POLL_US",L"250");
  {WorkerPoll poll;if(!poll.timer||poll.microseconds!=250)return 1;for(unsigned i=0;i<4;++i)poll.pause();}
  SetEnvironmentVariableW(L"SFC_D3D9_POLL_US",L"0");
  {WorkerPoll poll;if(poll.timer||poll.microseconds)return 1;poll.pause();}
  for(const wchar_t* value:{L"1",L"250junk",L"12345678901234567890"}){
   SetEnvironmentVariableW(L"SFC_D3D9_POLL_US",value);bool rejected=false;
   try{WorkerPoll poll;}catch(const std::runtime_error&){rejected=true;}if(!rejected)return 1;
  }
  SetEnvironmentVariableW(L"SFC_D3D9_POLL_US",nullptr);
  std::cout<<"Worker poll PASS private_timer/legacy/bounds/cleanup;no global timer change\n";
 }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
