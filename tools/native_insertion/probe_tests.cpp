#include "observer.h"
#include <iostream>
#include <memory>
#include <thread>
using namespace native_insertion;
static unsigned checks=0;
static void test(bool value){++checks;if(!value){std::cerr<<"Insertion check "<<checks<<" failed\n";std::exit(1);}}
static void ok(HRESULT h){test(SUCCEEDED(h));}
int main(){
 AddVectoredExceptionHandler(1,[](EXCEPTION_POINTERS* e)->LONG{
     std::cerr<<"Native fault at check "<<checks<<" rva="<<std::hex<<
         reinterpret_cast<uintptr_t>(e->ExceptionRecord->ExceptionAddress)-reinterpret_cast<uintptr_t>(GetModuleHandleW(nullptr))<<'\n';
     return EXCEPTION_CONTINUE_SEARCH;
 });
 DWORD session[]{11,22,33,44};const DWORD pid=GetCurrentProcessId();
 std::unique_ptr<BYTE,decltype(&_aligned_free)> memory(static_cast<BYTE*>(_aligned_malloc(16*1024*1024,64)),&_aligned_free);
 test(memory!=nullptr);memset(memory.get(),0,16*1024*1024);auto& s=*reinterpret_cast<Store*>(memory.get()+Offset);
 auto* ledger=reinterpret_cast<replacement::Store*>(memory.get()+replacement::Offset);
 test(!replacement::valid(ledger,session,pid)); // Reproduce the missing startup handshake.
 test(preparePassiveLedger(memory.get(),session,pid)&&replacement::valid(ledger,session,pid));
 replacement::Control control{};test(replacement::read(ledger->control,control)&&control.mode==replacement::Priming);
 test(preparePassiveLedger(memory.get(),session,pid));test(!preparePassiveLedger(memory.get(),session,pid+1));
 DWORD foreign[]{44,33,22,11};test(!preparePassiveLedger(memory.get(),foreign,pid));
 replacement::begin(*ledger,20,GetCurrentThreadId());replacement::Receipt receipt{};
 test(replacement::sample(*ledger,20,receipt)&&receipt.frame==20); // Private output producer can publish without suppressing.
 test(!ledger->suppressed&&!ledger->committed);control.mode=replacement::Active;replacement::write(ledger->control,control);
 test(!preparePassiveLedger(memory.get(),session,pid));control.mode=replacement::Priming;replacement::write(ledger->control,control);
 initialize(s,session,pid);test(valid(s.header,session,pid));auto other=session[0];session[0]++;test(!valid(s.header,session,pid));session[0]=other;
 begin(s,10,(uint64_t(4)<<32)|7);model(s,true,7,100,200,300);offered(s,10,12345);offered(s,10,12346);
 test(s.header.written==3&&s.header.phase==InsideSelected&&s.header.sourceQpc==12345);
 model(s,false,7,100,200,300);test(s.header.phase==AfterSelected&&s.events[3].kind==ModelEnd);
 std::thread wrong([&]{model(s,true,7,101,200,300);});wrong.join();test(s.header.wrongThread==1&&s.header.model==100);
 for(unsigned i=4;i<Capacity;++i)test(publish(s,context(s.header,Present)));
 test(!publish(s,context(s.header,Present))&&s.header.dropped==1&&s.events[0].frame==10);
 InterlockedExchange(&s.header.read,1);test(publish(s,context(s.header,Present))&&s.events[0].committed==257);
 s.header.stopped=1;test(!publish(s,context(s.header,Present)));initialize(s,session,pid);begin(s,20,(uint64_t(4)<<32)|7);
 ComPtr<ID3D11Device> d;ComPtr<ID3D11DeviceContext> c;D3D_FEATURE_LEVEL level{};
 ok(D3D11CreateDevice(nullptr,D3D_DRIVER_TYPE_WARP,nullptr,0,nullptr,0,D3D11_SDK_VERSION,&d,&level,&c));
 D3D11_TEXTURE2D_DESC shape{};shape.Width=64;shape.Height=32;shape.MipLevels=shape.ArraySize=1;
 shape.Format=DXGI_FORMAT_R8G8B8A8_TYPELESS;shape.SampleDesc.Count=8;shape.Usage=D3D11_USAGE_DEFAULT;shape.BindFlags=D3D11_BIND_RENDER_TARGET;
 ComPtr<ID3D11Texture2D> colour,z;ok(d->CreateTexture2D(&shape,nullptr,&colour));
 D3D11_RENDER_TARGET_VIEW_DESC rv{};rv.Format=DXGI_FORMAT_R8G8B8A8_UNORM;rv.ViewDimension=D3D11_RTV_DIMENSION_TEXTURE2DMS;
 ComPtr<ID3D11RenderTargetView> target;ok(d->CreateRenderTargetView(colour.Get(),&rv,&target));
 shape.Format=DXGI_FORMAT_R32_TYPELESS;shape.BindFlags=D3D11_BIND_DEPTH_STENCIL;ok(d->CreateTexture2D(&shape,nullptr,&z));
 D3D11_DEPTH_STENCIL_VIEW_DESC zv{};zv.Format=DXGI_FORMAT_D32_FLOAT;zv.ViewDimension=D3D11_DSV_DIMENSION_TEXTURE2DMS;
 ComPtr<ID3D11DepthStencilView> depth;ok(d->CreateDepthStencilView(z.Get(),&zv,&depth));
 D3D11_DEPTH_STENCIL_DESC zd{};zd.DepthEnable=TRUE;zd.DepthWriteMask=D3D11_DEPTH_WRITE_MASK_ZERO;zd.DepthFunc=D3D11_COMPARISON_LESS_EQUAL;
 ComPtr<ID3D11DepthStencilState> state;ok(d->CreateDepthStencilState(&zd,&state));c->OMSetDepthStencilState(state.Get(),13);
 ID3D11RenderTargetView* r=target.Get();c->OMSetRenderTargets(1,&r,depth.Get());float blue[]{0,0,1,1};c->ClearRenderTargetView(target.Get(),blue);
 game_output::Pool pool{};pool.header={game_output::Magic,game_output::Version,sizeof(pool),pid,{11,22,33,44},pid,pid};
 auto& slot=pool.slots[0];auto& p=slot.packet;p.magic_value=output_wire::magic;p.version_value=1;p.bytes=sizeof(p);p.producer_pid=pid;
 p.session=55;p.resource_epoch=1;p.sequence=9;p.source_frame=20;p.owner=7;p.revision=4;p.width=64;p.height=32;
 p.handles[0]=1;p.handles[1]=2;p.handles[2]=3;p.source_state_hash=4;p.scene_hash=5;p.published_qpc=6;p.checksum=output_wire::checksum(p);
 game_output::Metadata m{1,{11,22,33,44},0};m.checksum=game_output::checksum(m);game_output::metadata(slot,m);slot.state=output_wire::ready;
 Observer observer(d.Get(),memory.get(),session);observer.draw(reinterpret_cast<uintptr_t>(c.Get()),&pool);
 auto e=s.events[1];test(e.kind==NativeDraw&&e.target&&e.depth&&e.width==64&&e.height==32&&e.samples==8);
 test(e.targetFormat==DXGI_FORMAT_R8G8B8A8_TYPELESS&&e.viewFormat==DXGI_FORMAT_R8G8B8A8_UNORM&&e.depthFormat==DXGI_FORMAT_D32_FLOAT);
 test(e.depthEnabled&&e.depthWrite==0&&e.depthFunc==D3D11_COMPARISON_LESS_EQUAL&&e.outputFrame==20);
 observer.draw(reinterpret_cast<uintptr_t>(c.Get()),&pool);observer.draw(reinterpret_cast<uintptr_t>(c.Get()),&pool);test(s.header.written==3);
 ComPtr<ID3D11RenderTargetView> gotR;ComPtr<ID3D11DepthStencilView> gotZ;ComPtr<ID3D11DepthStencilState> gotState;UINT stencil{};
 c->OMGetRenderTargets(1,&gotR,&gotZ);c->OMGetDepthStencilState(&gotState,&stencil);test(gotR==target&&gotZ==depth&&gotState==state&&stencil==13);
 observer.present(&pool);test(slot.state==output_wire::idle&&s.header.outputSamples==1&&pool.stats.drawn==0);
 test(s.events[3].kind==Present&&s.events[4].kind==OutputDiscarded);
 p.checksum++;slot.state=output_wire::ready;observer.present(&pool);test(s.header.outputSamples==1&&slot.state==output_wire::idle);
 test(s.events[6].kind==OutputDiscarded&&s.events[6].flags==2);p.checksum--;
 p.owner=99;p.checksum=output_wire::checksum(p);slot.state=output_wire::ready;observer.present(&pool);
 test(s.header.outputSamples==1&&s.events[7].flags==0&&s.events[8].flags==2);p.owner=7;p.checksum=output_wire::checksum(p);
 // Pixel readback is offline-test-only. Production observer never copies pixels.
 D3D11_TEXTURE2D_DESC read{};colour->GetDesc(&read);read.Format=DXGI_FORMAT_R8G8B8A8_UNORM;read.SampleDesc.Count=1;read.BindFlags=0;
 ComPtr<ID3D11Texture2D> resolved,staging;ok(d->CreateTexture2D(&read,nullptr,&resolved));c->ResolveSubresource(resolved.Get(),0,colour.Get(),0,read.Format);
 read.Usage=D3D11_USAGE_STAGING;read.CPUAccessFlags=D3D11_CPU_ACCESS_READ;ok(d->CreateTexture2D(&read,nullptr,&staging));c->CopyResource(staging.Get(),resolved.Get());
 D3D11_MAPPED_SUBRESOURCE mapped{};ok(c->Map(staging.Get(),0,D3D11_MAP_READ,0,&mapped));test(*static_cast<const DWORD*>(mapped.pData)==0xffff0000);c->Unmap(staging.Get(),0);
 model(s,true,99,999,999,999);test(s.header.phase==OtherModel);observer.draw(reinterpret_cast<uintptr_t>(c.Get()),&pool);test(s.events[9].phase==OtherModel);
 const auto written=s.header.written;slot.state=output_wire::ready;pool.header.session[0]++;observer.present(&pool);test(slot.state==output_wire::ready&&s.header.outputSamples==1);
 test(s.header.written==written+1);s.header.stopped=1;observer.present(&pool);test(s.header.written==written+1);
 std::cout<<"Insertion observer PASS "<<checks<<" checks;8MSAA RGBA8/D32 state and pixels unchanged;no suppression or GPU output read\n";
}
