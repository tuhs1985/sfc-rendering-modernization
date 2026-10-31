#define NOMINMAX
#include "retained_resources.h"
#include "producer_scope.h"
#include "draw_snapshot.h"
#include "masked_assembly.h"
#include "source_notice.h"
#include "shader_compatibility.h"
#include "../m1_component/m1_present_calibration.h"
#include "../remix_runtime/ship_triplet_compositor.h"
#include "../remix_runtime/scene_frame_buffer.h"
#include <d3dcompiler.h>
#include <chrono>
#include <iostream>
#include <thread>
#include <cstring>
using namespace native_foreground;
static unsigned checks;
static void require(bool b, const char* why) { ++checks; if (!b) throw std::runtime_error(why); }
static void ok(HRESULT h) { if (FAILED(h)) throw std::runtime_error("D3D11 fixture call failed"); }
int main() { SetUnhandledExceptionFilter([](EXCEPTION_POINTERS* e)->LONG {
    fprintf(stderr,"Fixture exception after %u checks: code=%08lx address=%p\n",checks,e->ExceptionRecord->ExceptionCode,e->ExceptionRecord->ExceptionAddress);
    return EXCEPTION_EXECUTE_HANDLER;
}); try {
    ComPtr<ID3D11Device> d; ComPtr<ID3D11DeviceContext> c;
    ok(D3D11CreateDevice(nullptr, D3D_DRIVER_TYPE_HARDWARE, nullptr, 0, nullptr, 0,
        D3D11_SDK_VERSION, &d, nullptr, &c));
    auto makeBuffer = [&](UINT n, UINT bind, const void* p) {
        D3D11_BUFFER_DESC b{}; b.ByteWidth = n; b.BindFlags = bind;
        D3D11_SUBRESOURCE_DATA data{p, 0, 0}; ComPtr<ID3D11Buffer> out;
        ok(d->CreateBuffer(&b, p ? &data : nullptr, &out)); return out;
    };
    const float vertices[]{-1,-1,.5f, 0,1,.5f, 1,-1,.5f};
    const UINT indices[]{0,1,2}; const float tint[]{.25f,.5f,1,1};
    auto vb = makeBuffer(sizeof(vertices), D3D11_BIND_VERTEX_BUFFER, vertices);
    auto ib = makeBuffer(sizeof(indices), D3D11_BIND_INDEX_BUFFER, indices);
    auto cb = makeBuffer(sizeof(tint), D3D11_BIND_CONSTANT_BUFFER, tint);
    D3D11_TEXTURE2D_DESC td{}; td.Width = td.Height = 1; td.MipLevels = td.ArraySize = 1;
    td.SampleDesc.Count = 1; td.Format = DXGI_FORMAT_R8G8B8A8_UNORM;
    td.BindFlags = D3D11_BIND_SHADER_RESOURCE; UINT white = 0xffffffff;
    D3D11_SUBRESOURCE_DATA data{&white, 4, 0}; ComPtr<ID3D11Texture2D> texture;
    ok(d->CreateTexture2D(&td, &data, &texture));
    RetainedResources retained; retained.initialize(d.Get());
    retained.prepareBuffer(d.Get(), 0, sizeof(vertices), D3D11_BIND_VERTEX_BUFFER);
    retained.prepareBuffer(d.Get(), 1, sizeof(indices), D3D11_BIND_INDEX_BUFFER);
    retained.prepareBuffer(d.Get(), 2, sizeof(tint), D3D11_BIND_CONSTANT_BUFFER);
    retained.prepareImage(d.Get(), 0, td);
    require(retained.bytes() == 68, "exact bounded resource accounting");
    Identity key{1,10,3,7}; require(!retained.begin({}), "invalid identity rejected");
    require(retained.begin(key), "begin source frame");
    require(!retained.begin(key), "busy packet not overwritten");
    require(!retained.seal(), "incomplete packet not published");
    require(retained.captureBuffer(c.Get(), 0, vb.Get()), "retain vertices");
    require(retained.captureBuffer(c.Get(), 1, ib.Get()), "retain indices");
    require(retained.captureBuffer(c.Get(), 2, cb.Get()), "retain constants");
    require(retained.captureImage(c.Get(), 0, texture.Get()), "retain texture pixels");
    require(retained.seal(), "complete packet published");
    for (unsigned field = 0; field < 4; ++field) {
        Identity bad = key;
        if (field == 0) ++bad.session; if (field == 1) ++bad.frame;
        if (field == 2) ++bad.ownerEpoch; if (field == 3) ++bad.revision;
        require(!retained.buffer(0, bad) && !retained.image(0, bad), "cross identity rejected");
    }
    // Native buffers and texture are reused after capture, before replay.
    float gone[9]{}; const UINT reversed[]{2,2,2}; float black[4]{}; UINT dark = 0;
    c->UpdateSubresource(vb.Get(), 0, nullptr, gone, 0, 0);
    c->UpdateSubresource(ib.Get(), 0, nullptr, reversed, 0, 0);
    c->UpdateSubresource(cb.Get(), 0, nullptr, black, 0, 0);
    c->UpdateSubresource(texture.Get(), 0, nullptr, &dark, 4, 0);
    const char shader[] =
        "cbuffer Tint:register(b0){float4 tint;} Texture2D tex:register(t0);"
        "float4 vs(float3 p:POSITION):SV_Position{return float4(p,1);}"
        "float4 ps():SV_Target{return tex.Load(int3(0,0,0))*tint;}";
    ComPtr<ID3DBlob> vsCode, psCode, errors;
    ok(D3DCompile(shader, sizeof(shader), nullptr, nullptr, nullptr, "vs", "vs_5_0", 0, 0, &vsCode, &errors));
    ok(D3DCompile(shader, sizeof(shader), nullptr, nullptr, nullptr, "ps", "ps_5_0", 0, 0, &psCode, &errors));
    ComPtr<ID3D11VertexShader> vs; ComPtr<ID3D11PixelShader> ps; ComPtr<ID3D11InputLayout> layout;
    ok(d->CreateVertexShader(vsCode->GetBufferPointer(), vsCode->GetBufferSize(), nullptr, &vs));
    ok(d->CreatePixelShader(psCode->GetBufferPointer(), psCode->GetBufferSize(), nullptr, &ps));
    require(!shader_compatibility::qualified(ps.Get()),"unknown original shader is not silently sample-independent");
    require(shader_compatibility::remember(ps.Get(),psCode->GetBufferPointer(),psCode->GetBufferSize()),"reflection qualifies pixel-frequency original shader");
    require(shader_compatibility::singleSampleReplay(ps.Get(),~0u),"full native sample mask accepted");
    require(!shader_compatibility::singleSampleReplay(ps.Get(),0x55u),"partial MSAA mask cannot become a full single sample");
    require(!shader_compatibility::singleSampleReplay(ps.Get(),0u),"zero sample mask rejected");
    auto rejectShader=[&](const char* source,const char* reason){
        ComPtr<ID3DBlob> code;ok(D3DCompile(source,strlen(source),nullptr,nullptr,nullptr,"main","ps_5_0",0,0,&code,&errors));
        ComPtr<ID3D11PixelShader> candidate;ok(d->CreatePixelShader(code->GetBufferPointer(),code->GetBufferSize(),nullptr,&candidate));
        require(!shader_compatibility::remember(candidate.Get(),code->GetBufferPointer(),code->GetBufferSize()),reason);
        require(!shader_compatibility::qualified(candidate.Get()),"unsupported metadata remains attached to exact shader object");
    };
    rejectShader("float4 main(uint s:SV_SampleIndex):SV_Target{return float4(s*.125,0,0,1);}","sample-frequency shader rejected");
    rejectShader("float4 main(uint c:SV_Coverage):SV_Target{return float4(c*.125,0,0,1);}","input coverage dependency rejected");
    rejectShader("uint main():SV_Coverage{return 1;}","output coverage dependency rejected");
    rejectShader("float main():SV_Depth{return .5;}","shader depth output cannot override qualified hull depth");
    require(!shader_compatibility::remember(ps.Get(),nullptr,0)&&!shader_compatibility::qualified(ps.Get()),"invalid bytecode clears prior qualification");
    require(shader_compatibility::remember(ps.Get(),psCode->GetBufferPointer(),psCode->GetBufferSize()),"known bytecode can requalify same shader");
    D3D11_INPUT_ELEMENT_DESC element{"POSITION",0,DXGI_FORMAT_R32G32B32_FLOAT,0,0,D3D11_INPUT_PER_VERTEX_DATA,0};
    ok(d->CreateInputLayout(&element,1,vsCode->GetBufferPointer(),vsCode->GetBufferSize(),&layout));
    D3D11_RASTERIZER_DESC rd{}; rd.FillMode=D3D11_FILL_SOLID; rd.CullMode=D3D11_CULL_NONE; rd.DepthClipEnable=TRUE;
    ComPtr<ID3D11RasterizerState> raster; ok(d->CreateRasterizerState(&rd,&raster));
    D3D11_BLEND_DESC bd{}; auto& b=bd.RenderTarget[0]; b.BlendEnable=TRUE;
    b.SrcBlend=b.DestBlend=b.SrcBlendAlpha=b.DestBlendAlpha=D3D11_BLEND_ONE;
    b.BlendOp=b.BlendOpAlpha=D3D11_BLEND_OP_ADD; b.RenderTargetWriteMask=D3D11_COLOR_WRITE_ENABLE_ALL;
    ComPtr<ID3D11BlendState> blend; ok(d->CreateBlendState(&bd,&blend));
    td.Width=td.Height=16; td.BindFlags=D3D11_BIND_RENDER_TARGET;
    ComPtr<ID3D11Texture2D> output, staging; ok(d->CreateTexture2D(&td,nullptr,&output));
    ComPtr<ID3D11RenderTargetView> rtv; ok(d->CreateRenderTargetView(output.Get(),nullptr,&rtv));
    td.BindFlags=0; td.Usage=D3D11_USAGE_STAGING; td.CPUAccessFlags=D3D11_CPU_ACCESS_READ;
    ok(d->CreateTexture2D(&td,nullptr,&staging));
    ComPtr<ID3D11ShaderResourceView> srv;
    ok(d->CreateShaderResourceView(retained.image(0,key),nullptr,&srv));
    auto draw = [&](bool snapshot) {
        float background[]{.125f,.125f,.125f,0}; c->ClearRenderTargetView(rtv.Get(),background);
        ID3D11RenderTargetView* target=rtv.Get(); c->OMSetRenderTargets(1,&target,nullptr);
        c->OMSetBlendState(blend.Get(),nullptr,~0u); c->RSSetState(raster.Get());
        D3D11_VIEWPORT view{0,0,16,16,0,1}; c->RSSetViewports(1,&view);
        c->IASetInputLayout(layout.Get()); c->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);
        ID3D11Buffer* v=snapshot?retained.buffer(0,key):vb.Get(); UINT stride=12,offset=0;
        c->IASetVertexBuffers(0,1,&v,&stride,&offset);
        c->IASetIndexBuffer(snapshot?retained.buffer(1,key):ib.Get(),DXGI_FORMAT_R32_UINT,0);
        ID3D11Buffer* constants=snapshot?retained.buffer(2,key):cb.Get();
        c->VSSetShader(vs.Get(),nullptr,0); c->PSSetShader(ps.Get(),nullptr,0);
        c->PSSetConstantBuffers(0,1,&constants); ID3D11ShaderResourceView* image=srv.Get();
        c->PSSetShaderResources(0,1,&image); c->DrawIndexed(3,0,0);
        c->CopyResource(staging.Get(),output.Get()); D3D11_MAPPED_SUBRESOURCE mapped{};
        ok(c->Map(staging.Get(),0,D3D11_MAP_READ,0,&mapped)); UINT pixel;
        std::memcpy(&pixel,static_cast<const char*>(mapped.pData)+8*mapped.RowPitch+8*4,4);
        c->Unmap(staging.Get(),0); return pixel;
    };
    UINT pixel=draw(true);
    require((pixel&255)>=94 && (pixel&255)<=97, "retained texture constants vertices indices survive reuse: red");
    require(((pixel>>8)&255)>=158 && ((pixel>>8)&255)<=161, "native additive contribution green");
    require(((pixel>>16)&255)==255, "native additive saturation blue");
    require((draw(false)&0x00ffffff)==0x00202020, "reused original no longer contains captured draw");
    require(retained.finish(c.Get()), "retire after final replay command");
    require(!retained.buffer(0,key), "submitted packet unavailable for new replay");
    require(!retained.begin({1,11,3,7}), "receiver cannot overwrite in flight");
    c->Flush(); // Fixture only. Capture/recycle uses DONOTFLUSH and never waits.
    auto deadline=std::chrono::steady_clock::now()+std::chrono::seconds(5);
    bool recycled=false;
    while (!(recycled=retained.tryRecycle(c.Get())) && std::chrono::steady_clock::now()<deadline)
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    require(recycled,"GPU completed packet recyclable");
    require(!retained.buffer(0,key),"retired identity inaccessible");
    require(retained.begin({1,11,4,7}),"new owner epoch fresh capture");
    require(!retained.captureBuffer(c.Get(),0,cb.Get()),"wrong buffer layout rejected");
    require(!retained.seal(),"failed packet never published");
    require(retained.finish(c.Get()),"abandoned partial copy retired safely");
    RetainedResources bounded; bounded.initialize(d.Get()); bool capped=false;
    try { bounded.prepareBuffer(d.Get(),0,UINT(RetainedResources::limit+1),D3D11_BIND_VERTEX_BUFFER); }
    catch(const std::exception&) { capped=true; } require(capped,"fixed byte cap");
    td.Usage=D3D11_USAGE_DEFAULT; td.CPUAccessFlags=0; td.Width=512; td.BindFlags=D3D11_BIND_SHADER_RESOURCE;
    bool unsupported=false; try {bounded.prepareImage(d.Get(),0,td);} catch(const std::exception&) {unsupported=true;}
    require(unsupported,"unqualified image layout explicit rejection");
    // Historical native shield resource sizes, with synthetic byte contents.
    // This proves copy/version behavior, not historical shader reconstruction.
    RetainedResources nativeSize; nativeSize.initialize(d.Get());
    nativeSize.prepareBuffer(d.Get(),0,737280,D3D11_BIND_VERTEX_BUFFER);
    nativeSize.prepareBuffer(d.Get(),1,16384,D3D11_BIND_INDEX_BUFFER);
    td.Width=td.Height=256; td.Format=DXGI_FORMAT_R8G8B8A8_TYPELESS;
    nativeSize.prepareImage(d.Get(),0,td);
    auto largeVB=makeBuffer(737280,D3D11_BIND_VERTEX_BUFFER,nullptr);
    auto largeIB=makeBuffer(16384,D3D11_BIND_INDEX_BUFFER,nullptr);
    ComPtr<ID3D11Texture2D> nativeTexture; ok(d->CreateTexture2D(&td,nullptr,&nativeTexture));
    require(nativeSize.bytes()==1015808,"historical VB IB image bounded bytes");
    require(nativeSize.begin({8,99,4,6}),"native-size packet begins");
    require(nativeSize.captureBuffer(c.Get(),0,largeVB.Get()),"native-size VB capture");
    require(nativeSize.captureBuffer(c.Get(),1,largeIB.Get()),"native-size IB capture");
    require(nativeSize.captureImage(c.Get(),0,nativeTexture.Get()),"native typeless image capture");
    require(nativeSize.seal(),"native-size complete packet");
    ComPtr<ID3D11DeviceContext> deferred; ok(d->CreateDeferredContext(0,&deferred));
    require(!nativeSize.finish(deferred.Get()),"deferred-context retirement rejected");
    require(nativeSize.finish(c.Get()),"native-size packet retired");
    ProducerScope scope;
    auto shield=[&] {return scope.qualifies(key,42,true,false,true,true);};
    require(!shield(),"no shield provenance outside native span");
    require(scope.enter(key,42),"qualified native owner span enters");
    scope.beforeDepthWrite(false);
    require(!shield(),"entry state flush is NOT shield geometry");
    scope.afterDepthWrite(false);
    require(shield(),"geometry after completed depth disable qualified");
    require(!scope.qualifies(key,41,true,false,true,true),"wrong resource retained native only");
    require(!scope.qualifies(key,42,true,true,true,true),"opaque state not shield qualified");
    require(!scope.qualifies(key,42,true,false,false,true),"different blend not shield qualified");
    require(!scope.qualifies(key,42,true,false,true,false),"unqualified primitive retained native only");
    scope.beforeDepthWrite(true);
    require(scope.restoring() && shield(),"restore state flush still shield geometry");
    scope.afterDepthWrite(true);
    require(!shield(),"following opaque draws excluded"); scope.leave();
    require(scope.enter(key,42),"next native span enters");
    scope.beforeDepthWrite(false); scope.afterDepthWrite(false);
    require(!scope.enter({1,10,4,7},42),"nested ownership ambiguity rejected");
    require(!shield(),"nested owner cannot acquire outer shield"); scope.leave();
    require(!shield(),"ambiguous outer remains rejected"); scope.leave();
    require(scope.enter(key,42),"fresh span after ambiguity"); scope.leave();
    require(!scope.enter({},42),"invalid owner not qualified"); scope.leave();
    require(scope.enter(key,0),"native resource ID zero is retained without inventing invalid-ID semantics");
    scope.beforeDepthWrite(false);scope.afterDepthWrite(false);
    require(scope.qualifies(key,0,true,false,true,true),"zero native ID still requires exact producer and state");scope.leave();
    c->UpdateSubresource(vb.Get(),0,nullptr,vertices,0,0);
    c->UpdateSubresource(ib.Get(),0,nullptr,indices,0,0);
    c->UpdateSubresource(cb.Get(),0,nullptr,tint,0,0);
    c->UpdateSubresource(texture.Get(),0,nullptr,&white,4,0);
    ComPtr<ID3D11ShaderResourceView> sourceView;ok(d->CreateShaderResourceView(texture.Get(),nullptr,&sourceView));
    auto* sourceSRV=sourceView.Get();c->PSSetShaderResources(0,1,&sourceSRV);
    D3D11_DEPTH_STENCIL_DESC nativeZ{};nativeZ.DepthEnable=TRUE;
    nativeZ.DepthFunc=D3D11_COMPARISON_LESS_EQUAL;nativeZ.DepthWriteMask=D3D11_DEPTH_WRITE_MASK_ZERO;
    ComPtr<ID3D11DepthStencilState> nativeDepthState;ok(d->CreateDepthStencilState(&nativeZ,&nativeDepthState));
    c->OMSetDepthStencilState(nativeDepthState.Get(),0);
    DrawBindings original;require(original.read(c.Get()),"capture actual bound native-style pipeline");
    DrawSnapshot drawSnapshot;drawSnapshot.prepare(d.Get(),original);
    Identity drawKey{8,100,4,6};require(drawSnapshot.capture(c.Get(),drawKey,3,0,0),"capture original draw and resource versions");
    drawSnapshot.prepareViews(d.Get(),drawKey);
    c->UpdateSubresource(vb.Get(),0,nullptr,gone,0,0);
    c->UpdateSubresource(ib.Get(),0,nullptr,reversed,0,0);
    c->UpdateSubresource(cb.Get(),0,nullptr,black,0,0);
    c->UpdateSubresource(texture.Get(),0,nullptr,&dark,4,0);
    float background[]{.125f,.125f,.125f,0};c->ClearRenderTargetView(rtv.Get(),background);
    require(!drawSnapshot.record(deferred.Get(),rtv.Get(),nullptr,key),"draw replay rejects wrong source frame");
    require(drawSnapshot.record(deferred.Get(),rtv.Get(),nullptr,drawKey),"record exact original shaders and bindings");
    ComPtr<ID3D11CommandList> commands;ok(deferred->FinishCommandList(FALSE,&commands));
    c->ExecuteCommandList(commands.Get(),TRUE);
    c->CopyResource(staging.Get(),output.Get());D3D11_MAPPED_SUBRESOURCE readback{};
    ok(c->Map(staging.Get(),0,D3D11_MAP_READ,0,&readback));UINT replayPixel{};
    std::memcpy(&replayPixel,static_cast<const char*>(readback.pData)+8*readback.RowPitch+8*4,4);c->Unmap(staging.Get(),0);
    require(replayPixel==pixel,"exact retained draw pixels survive all original resource reuse");
    ComPtr<ID3D11PixelShader> afterShader;c->PSGetShader(&afterShader,nullptr,nullptr);
    require(afterShader.Get()==ps.Get(),"deferred replay restores native shader state");
    // Native background + native shield, then hull + only overwritten foreground.
    // D24S8 takes the place of the four-byte history depth, not another plane.
    D3D11_TEXTURE2D_DESC zDesc{};zDesc.Width=zDesc.Height=16;zDesc.ArraySize=zDesc.MipLevels=zDesc.SampleDesc.Count=1;
    zDesc.Format=DXGI_FORMAT_R24G8_TYPELESS;zDesc.BindFlags=D3D11_BIND_DEPTH_STENCIL|D3D11_BIND_SHADER_RESOURCE;
    UINT depthData[256],nativePixels[256];
    for(unsigned y=0;y<16;++y)for(unsigned x=0;x<16;++x) {
        const bool occluder=x>=8&&x<10;
        depthData[y*16+x]=UINT((occluder?.2:.9)*16777215.0+.5);
        if(x==6&&y==8)depthData[y*16+x]=0x04000000; // invalid source-depth bit
        nativePixels[y*16+x]=occluder?0xff2020c0:0xff202020;
    }
    D3D11_SUBRESOURCE_DATA zInitial{depthData,64,0};ComPtr<ID3D11Texture2D> historyDepth;
    ok(d->CreateTexture2D(&zDesc,&zInitial,&historyDepth));
    D3D11_DEPTH_STENCIL_VIEW_DESC zView{};zView.Format=DXGI_FORMAT_D24_UNORM_S8_UINT;
    zView.ViewDimension=D3D11_DSV_DIMENSION_TEXTURE2D;ComPtr<ID3D11DepthStencilView> historyDSV;
    ok(d->CreateDepthStencilView(historyDepth.Get(),&zView,&historyDSV));
    c->UpdateSubresource(output.Get(),0,nullptr,nativePixels,64,0);
    auto execute=[&]{ComPtr<ID3D11CommandList> list;ok(deferred->FinishCommandList(FALSE,&list));c->ExecuteCommandList(list.Get(),TRUE);};
    require(drawSnapshot.record(deferred.Get(),rtv.Get(),historyDSV.Get(),drawKey),"native shield baseline with original depth state");execute();
    auto readPixels=[&](UINT* pixels){c->CopyResource(staging.Get(),output.Get());D3D11_MAPPED_SUBRESOURCE m{};
        ok(c->Map(staging.Get(),0,D3D11_MAP_READ,0,&m));for(unsigned y=0;y<16;++y)std::memcpy(pixels+y*16,static_cast<const char*>(m.pData)+y*m.RowPitch,64);c->Unmap(staging.Get(),0);};
    UINT baseline[256],assembled[256];readPixels(baseline);
    UINT colors[256],coverage[256];float depths[256];
    for(unsigned y=0;y<16;++y)for(unsigned x=0;x<16;++x) {
        const auto i=y*16+x;colors[i]=0xff4c3319;depths[i]=x==5?.4f:.6f;
        if(x==6&&y==8)depths[i]=0;
        coverage[i]=x>=4&&x<12&&y>=4&&y<12?1:0;
    }
    auto imageView=[&](DXGI_FORMAT format,const void* bytes){D3D11_TEXTURE2D_DESC t{};t.Width=t.Height=16;
        t.MipLevels=t.ArraySize=t.SampleDesc.Count=1;t.Format=format;t.BindFlags=D3D11_BIND_SHADER_RESOURCE;
        D3D11_SUBRESOURCE_DATA initial{bytes,64,0};ComPtr<ID3D11Texture2D> tex;
        ok(d->CreateTexture2D(&t,&initial,&tex));ComPtr<ID3D11ShaderResourceView> view;ok(d->CreateShaderResourceView(tex.Get(),nullptr,&view));return view;};
    auto returnedColor=imageView(DXGI_FORMAT_R8G8B8A8_UNORM,colors);
    auto returnedDepth=imageView(DXGI_FORMAT_R32_FLOAT,depths);
    auto returnedCoverage=imageView(DXGI_FORMAT_R32_FLOAT,coverage);
    ID3D11ShaderResourceView* hullViews[]{returnedColor.Get(),returnedDepth.Get(),returnedCoverage.Get()};
    MaskedAssembly assembly(d.Get());
    require(assembly.record(deferred.Get(),rtv.Get(),historyDSV.Get(),hullViews,16,16),"compose hull color depth and exact stencil together");execute();
    require(drawSnapshot.record(deferred.Get(),rtv.Get(),historyDSV.Get(),drawKey,assembly.foregroundState(),1),"replay original shield only on replaced pixels");execute();
    readPixels(assembled);
    for(unsigned y=0;y<16;++y)for(unsigned x=0;x<16;++x)if(!coverage[y*16+x])
        require(assembled[y*16+x]==baseline[y*16+x],"outside hull unchanged; no doubled additive shield");
    require(assembled[8*16+8]==baseline[8*16+8],"opaque native occluder remains in front");
    require(assembled[8*16+6]==baseline[8*16+6],"invalid native depth cannot authorize even zero-depth replacement");
    require(assembled[8*16+5]==0xff4c3319,"back shield hidden by nearer replacement hull");
    require((assembled[8*16+7]&255)>=88&&(assembled[8*16+7]&255)<=90,"front shield restored over replacement hull");
    require(((assembled[8*16+7]>>8)&255)>=177&&((assembled[8*16+7]>>8)&255)<=180,"original additive shield colour preserved");
    require(uint64_t(1920)*1080*4*16<=128ull*1024*1024,"packed depth stencil reuses existing output bytes");
    require(drawSnapshot.finish(c.Get()),"retained draw retires after final foreground replay");
    replacement::Store ledger{};DWORD session[]{1,2,3,4};replacement::initialize(ledger,session,GetCurrentProcessId());
    source_notice::Store notices{};source_notice::initialize(notices,session,GetCurrentProcessId());
    replacement::Control ctrl{};ctrl.owner=7;ctrl.revision=9;replacement::write(ledger.control,ctrl);
    source_notice::offer(notices,ledger,12,100,0,8,GetCurrentThreadId());source_notice::Notice notice{};
    require(!source_notice::sample(notices,12,notice),"other owner cannot publish player shield notice");
    source_notice::offer(notices,ledger,12,100,200,7,GetCurrentThreadId());
    require(source_notice::sample(notices,12,notice)&&notice.ship==100&&notice.shield==200,"source parent identity and diagnostic shield field retained");
    source_notice::offer(notices,ledger,76,101,0,7,GetCurrentThreadId());
    require(!source_notice::sample(notices,12,notice),"overwritten old native frame not revived");
    require(source_notice::valid(notices,session,GetCurrentProcessId()),"current-user session source notice valid");
    DWORD wrongSession[]{1,2,3,5};require(!source_notice::valid(notices,wrongSession,GetCurrentProcessId()),"foreign session notice rejected");
    // Exercise the ACTUAL history resolver with eight different float samples,
    // including one invalid sample. No guessed CPU copy of the shader logic.
    D3D11_TEXTURE2D_DESC full{};full.Width=1920;full.Height=1080;full.MipLevels=full.ArraySize=full.SampleDesc.Count=1;
    full.Format=DXGI_FORMAT_B8G8R8A8_UNORM;full.BindFlags=D3D11_BIND_RENDER_TARGET;
    ComPtr<ID3D11Texture2D> nativeBack;ok(d->CreateTexture2D(&full,nullptr,&nativeBack));
    scene_frame_buffer::History actualHistory(d.Get(),nativeBack.Get(),true,true);
    full.Format=DXGI_FORMAT_R32_TYPELESS;full.SampleDesc.Count=8;full.BindFlags=D3D11_BIND_RENDER_TARGET|D3D11_BIND_SHADER_RESOURCE;
    ComPtr<ID3D11Texture2D> sampleSource;ok(d->CreateTexture2D(&full,nullptr,&sampleSource));
    D3D11_RENDER_TARGET_VIEW_DESC floatTarget{};floatTarget.Format=DXGI_FORMAT_R32_FLOAT;floatTarget.ViewDimension=D3D11_RTV_DIMENSION_TEXTURE2DMS;
    ComPtr<ID3D11RenderTargetView> sampleTarget;ok(d->CreateRenderTargetView(sampleSource.Get(),&floatTarget,&sampleTarget));
    D3D11_SHADER_RESOURCE_VIEW_DESC floatSource{};floatSource.Format=DXGI_FORMAT_R32_FLOAT;floatSource.ViewDimension=D3D11_SRV_DIMENSION_TEXTURE2DMS;
    ComPtr<ID3D11ShaderResourceView> sampleView;ok(d->CreateShaderResourceView(sampleSource.Get(),&floatSource,&sampleView));
    const char sampleShader[]="cbuffer Params:register(b0){uint invalid;uint3 pad;} float4 vs(uint i:SV_VertexID):SV_Position{float2 p[3]={float2(-1,-1),float2(-1,3),float2(3,-1)};return float4(p[i],0,1);} float ps(uint s:SV_SampleIndex):SV_Target{return invalid&&s==5?asfloat(0x7fc00000u):(s==3?.25:.75);}";
    ComPtr<ID3DBlob> sampleVSCode,samplePSCode;ok(D3DCompile(sampleShader,sizeof(sampleShader),nullptr,nullptr,nullptr,"vs","vs_5_0",0,0,&sampleVSCode,nullptr));
    ok(D3DCompile(sampleShader,sizeof(sampleShader),nullptr,nullptr,nullptr,"ps","ps_5_0",0,0,&samplePSCode,nullptr));
    ComPtr<ID3D11VertexShader> sampleVS;ComPtr<ID3D11PixelShader> samplePS;
    ok(d->CreateVertexShader(sampleVSCode->GetBufferPointer(),sampleVSCode->GetBufferSize(),nullptr,&sampleVS));
    ok(d->CreatePixelShader(samplePSCode->GetBufferPointer(),samplePSCode->GetBufferSize(),nullptr,&samplePS));
    auto invalidBuffer=makeBuffer(16,D3D11_BIND_CONSTANT_BUFFER,nullptr);
    full.Format=DXGI_FORMAT_R24G8_TYPELESS;full.SampleDesc.Count=1;full.BindFlags=0;full.Usage=D3D11_USAGE_STAGING;full.CPUAccessFlags=D3D11_CPU_ACCESS_READ;
    ComPtr<ID3D11Texture2D> depthReadback;ok(d->CreateTexture2D(&full,nullptr,&depthReadback));
    for(UINT invalid=0;invalid<2;++invalid) {
        c->ClearState();UINT values[]{invalid,0,0,0};c->UpdateSubresource(invalidBuffer.Get(),0,nullptr,values,0,0);
        ID3D11Buffer* parameters=invalidBuffer.Get();c->PSSetConstantBuffers(0,1,&parameters);
        c->VSSetShader(sampleVS.Get(),nullptr,0);c->PSSetShader(samplePS.Get(),nullptr,0);c->RSSetState(raster.Get());
        c->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);D3D11_VIEWPORT v{0,0,1920,1080,0,1};c->RSSetViewports(1,&v);
        auto* target=sampleTarget.Get();c->OMSetRenderTargets(1,&target,nullptr);c->Draw(3,0);c->OMSetRenderTargets(0,nullptr,nullptr);
        live_owner::Row row{};row[1]=7;row[2]=100+invalid;
        actualHistory.captureAt(0,nativeBack.Get(),sampleView.Get(),row,1,0);
        c->CopyResource(depthReadback.Get(),actualHistory.slot(0).depth.Get());D3D11_MAPPED_SUBRESOURCE mapped{};
        ok(c->Map(depthReadback.Get(),0,D3D11_MAP_READ,0,&mapped));DWORD packed{};memcpy(&packed,static_cast<BYTE*>(mapped.pData)+500*mapped.RowPitch+500*4,4);
        c->Unmap(depthReadback.Get(),0);
        if(invalid)require((packed>>24)==4,"actual min8 invalid sample remains stencil-invalid");
        else {require((packed>>24)==0,"actual min8 valid samples clear invalid marker");
            require(std::abs(float(packed&0xffffff)/16777215.f-.25f)<=1.f/16777215.f,"actual min8 retains nearest sample within D24 precision");}
    }
    std::cout<<"Native foreground retained-resource GPU PASS "<<checks<<" checks; historical-size packet 1015808 bytes; no production hooks enabled\n";
    return 0;
} catch(const std::exception& e) { std::cerr<<e.what()<<'\n'; return 1; } }
