// Actual host/output IPC without a GPU or SFC. Test-owned processes only.
#define NOMINMAX
#include <windows.h>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <array>
#include <vector>
#include <algorithm>
namespace fs=std::filesystem;
static void require(bool v,const char* m){if(!v)throw std::runtime_error(m);}
static void ok(HRESULT v,const char* m){require(SUCCEEDED(v),m);}
#include "../tools/d3d9_proof/output_producer.h"
#include "../tools/d3d9_proof/warm_start.h"
int wmain(int argc,wchar_t** argv){std::cout.setf(std::ios::unitbuf);try{
 require(argc==4,"receiver,owned evidence directory,case");const fs::path root=argv[2];const std::wstring test=argv[3];OutputPeer peer;
 peer.start(fs::absolute(argv[1]),root,L"normal",nullptr,true);
 {std::ofstream ready(root/L"probe-ready.txt");ready<<peer.receiverPid;}
 if(test==L"cancel_pre"){peer.finish();return 0;}
 if(test==L"parent_death")ExitProcess(23);
 if(test==L"receiver_failure"){require(TerminateProcess(peer.process,61)!=FALSE,"test receiver exit");WaitForSingleObject(peer.process,5000);peer.check_alive();}
 warm_start::wait(root,[&]{peer.check_alive();},[](const char*,unsigned){});
 if(test==L"receiver_invalid_crc"){
  ReceiverActivation source;require(source.open(GetCurrentProcessId()),"test receiver source");source.cell->ticket.checksum^=1;
  InterlockedExchange(&peer.channel->state,output_startup::Activate);SetEvent(peer.readyEvent);peer.wait_state(output_wire::idle);
  require(false,"receiver accepted invalid ticket");
 }
 if(test.rfind(L"invalid_",0)==0){ReceiverActivation source;require(source.open(GetCurrentProcessId()),"test source");auto& a=source.cell->ticket;
  if(test==L"invalid_session")a.session[0]^=1;
  if(test==L"invalid_asset")memset(a.asset,0,32);
  if(test==L"invalid_asset_changed")memset(a.asset,0x34,32);
  a.checksum=startup_ticket::hash(&a,offsetof(startup_ticket::Activation,checksum));
  if(test==L"invalid_crc")a.checksum^=1;
  if(test==L"invalid_host")source.cell->host^=1;
 }
 peer.activate();const auto receipt=output_startup::read(*peer.channel);
 std::cout<<"PROBE_ACTIVATED receiver="<<receipt.receiver<<" ready="<<receipt.readyQpc<<" active="<<receipt.activatedQpc<<" game="<<receipt.game<<'\n';
 peer.finish();return 0;
 }catch(const warm_start::Cancelled&){std::cout<<"PROBE_CANCELLED\n";return 10;}
 catch(const std::exception& e){std::cerr<<"PROBE_ERROR "<<e.what()<<'\n';return 20;}}
