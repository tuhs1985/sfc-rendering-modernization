// Standalone actual native coordinator consumer. Never hooks or launches SFC.
#include <d3d11_4.h>
#include <dxgi1_6.h>
#include <wrl/client.h>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <memory>
#include <vector>
#include "../tools/remix_runtime/return_wire.h"
#include "../tools/remix_runtime/d3d9_game_receiver.h"
#include "../tools/remix_runtime/source_timing_fixture.h"
#include "../tools/native_insertion/gate_fixture.h"
using Microsoft::WRL::ComPtr;
static d3d9_game::Receiver* fixtureReceiver=nullptr;
static DWORD WINAPI dispatch(DWORD action,const native_gate::Ticket* t,native_gate::Reply* r){return fixtureReceiver?fixtureReceiver->nativeInsertion(action,t,r):DWORD(native_gate::Result::Original);}
static void need(bool ok,const char* why){if(!ok)throw std::runtime_error(why);}
int wmain(int argc,wchar_t** argv){try{
 need(argc==2,"Fixture output directory required");std::filesystem::path output(argv[1]);std::filesystem::create_directories(output);
 need(native_gate::additive()&&!replacement::requested()&&!native_cohort::requested(),"Explicit one-player additive fixture required");
 ComPtr<ID3D11Device> device;ComPtr<ID3D11DeviceContext> context;
 need(SUCCEEDED(D3D11CreateDevice(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,0,nullptr,0,D3D11_SDK_VERSION,&device,nullptr,&context)),"Native D3D11 device");
 SourceTimingFixture source;need(source.enabled&&source.cohort.store,"Existing source fixture required");
 auto* base=reinterpret_cast<BYTE*>(source.source.mailbox)-sfc_calibration::Offset;
 auto fixture=std::make_unique<native_gate::Fixture>();fixture->w=1280;fixture->h=720;fixture->init(device.Get(),context.Get(),base,source.source.session,nullptr,dispatch);
 D3D11_TEXTURE2D_DESC desc{};desc.Width=1280;desc.Height=720;desc.MipLevels=desc.ArraySize=1;desc.SampleDesc.Count=8;desc.Format=DXGI_FORMAT_R32_TYPELESS;desc.BindFlags=D3D11_BIND_DEPTH_STENCIL;
 ComPtr<ID3D11Texture2D> depth;ComPtr<ID3D11DepthStencilView> depthView;
 D3D11_DEPTH_STENCIL_VIEW_DESC dv{};dv.Format=DXGI_FORMAT_D32_FLOAT;dv.ViewDimension=D3D11_DSV_DIMENSION_TEXTURE2DMS;
 need(SUCCEEDED(device->CreateTexture2D(&desc,nullptr,&depth))&&SUCCEEDED(device->CreateDepthStencilView(depth.Get(),&dv,&depthView)),"Native D32 target");
 return_path::Mapping mapping(true);InterlockedExchange(&mapping.state->armed,1);InterlockedExchange(&mapping.state->enabled,1);
 auto receiver=std::make_unique<d3d9_game::Receiver>(mapping,device.Get(),fixture->colour.Get());fixtureReceiver=receiver.get();
 auto& gate=*reinterpret_cast<native_gate::Store*>(base+native_gate::Offset);
 auto& ledger=*reinterpret_cast<replacement::Store*>(base+replacement::Offset);
 const auto end=GetTickCount64()+60000;unsigned frames=0,committed=0,missesAfterReady=0,longest=0,currentMiss=0;uint64_t first=0;std::vector<double> elapsed;
 while(GetTickCount64()<end&&committed<60){
  const auto start=native_gate::now();source.publish(++frames);
  const bool inserted=fixture->frame(source.cohort.pending,depthView.Get(),fixture->target.Get(),fixture->verified<2);
  receiver->step(fixture->target.Get());fixture->verify(source.rows[0][1]);
  if(frames%120==0)std::cout<<"GATE_PROGRESS frame="<<frames<<" commits="<<gate.header.commits<<" requests="<<gate.header.requests<<" outcome="<<gate.current.outcome<<" invalid="<<gate.header.invalid<<" ready="<<fixture->pool->header.ready<<" output="<<fixture->pool->header.published<<" source="<<source.cohort.pending.sequence<<" selected="<<source.live.store->header.selected<<std::endl;
  if(inserted){if(!first)first=GetTickCount64();++committed;currentMiss=0;}
  else if(first){++missesAfterReady;++currentMiss;longest=(std::max)(longest,currentMiss);}
  const auto duration=double(native_gate::now()-start)*1000/gate.header.frequency;elapsed.push_back(duration);
  // Synthetic source cadence only; production waits exclusively on gate events.
  const auto target=start+gate.header.frequency/60;while(native_gate::now()<target)Sleep(1);
 }
 std::ofstream report(output/L"result.json");
 report<<"{\"frames\":"<<frames<<",\"commits\":"<<committed<<",\"verified\":"<<fixture->verified<<",\"misses_after_first\":"<<missesAfterReady<<",\"longest_misses\":"<<longest<<",\"suppressed\":"<<ledger.suppressed<<",\"pool_version\":"<<fixture->pool->header.version<<",\"partial\":"<<gate.header.partial<<",\"requests\":"<<gate.header.requests<<",\"invalid\":"<<gate.header.invalid<<",\"timing_ms\":[";
 for(size_t i=0;i<elapsed.size();++i){if(i)report<<',';report<<elapsed[i];}report<<"]}";report.close();
 receiver->stop();fixtureReceiver=nullptr;receiver.reset();
 need(committed==60&&fixture->verified==2&&!ledger.suppressed&&!gate.header.partial,"Native coordinator completion/ownership");
 std::cout<<"PASS actual native Acquire/Commit, UE output leases, native effects and additive originals\n";return 0;
}catch(const std::exception& e){std::cerr<<"UE native gate fixture: "<<e.what()<<'\n';return 1;}}
