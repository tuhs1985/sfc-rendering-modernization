#pragma once
// Standalone D3D11 fixture ONLY. This header is never included in the SFC DLL.
#include "shield_fixture_contract.h"
#include "source_notice.h"
#include <array>
#include <cmath>
namespace foreground_fixture {
using Microsoft::WRL::ComPtr;
using Word=native_foreground::shield_hooks::Word;
inline DWORD ship[112]{},shield[1]{},manager[1]{},resource=42,caller{};
inline ComPtr<ID3D11Device> device;
inline ComPtr<ID3D11DeviceContext> context;
inline ComPtr<ID3D11Texture2D> nativeColor;
inline ComPtr<ID3D11RenderTargetView> nativeTarget;
inline ComPtr<ID3D11DepthStencilView> nativeDepth;
inline ComPtr<ID3D11VertexShader> vertex;
inline ComPtr<ID3D11PixelShader> pixel;
inline ComPtr<ID3D11InputLayout> layout;
inline ComPtr<ID3D11Buffer> vertices,indices,constants;
inline ComPtr<ID3D11ShaderResourceView> white;
inline ComPtr<ID3D11BlendState> blend;
inline ComPtr<ID3D11RasterizerState> raster;
inline ComPtr<ID3D11DepthStencilState> depthOff,depthOn;
inline unsigned verified{};inline DWORD verifiedFrame{},candidateX{},candidateY{};
inline bool initialized=false;
inline void check(HRESULT h){if(FAILED(h))throw std::runtime_error("native foreground fixture graphics");}
inline Word __declspec(noinline) __fastcall sourceDepth(void*,void*,Word enabled) {
    if(context){if(enabled)context->DrawIndexed(3,3,0);context->OMSetDepthStencilState(enabled?depthOn.Get():depthOff.Get(),0);}
    return enabled;
}
inline Word __declspec(noinline) __fastcall sourceShield(void*,void*,Word nativeManager) {
    if(!context)return 0;
    auto* target=nativeTarget.Get();context->OMSetRenderTargets(1,&target,nativeDepth.Get());
    context->VSSetShader(vertex.Get(),nullptr,0);context->PSSetShader(pixel.Get(),nullptr,0);
    context->IASetInputLayout(layout.Get());context->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);
    auto* vb=vertices.Get();UINT stride=32,offset=0;context->IASetVertexBuffers(0,1,&vb,&stride,&offset);
    context->IASetIndexBuffer(indices.Get(),DXGI_FORMAT_R32_UINT,0);
    auto* cb=constants.Get();context->PSSetConstantBuffers(0,1,&cb);auto* image=white.Get();context->PSSetShaderResources(0,1,&image);
    context->OMSetBlendState(blend.Get(),nullptr,~0u);context->RSSetState(raster.Get());D3D11_VIEWPORT v{0,0,1920,1080,0,1};context->RSSetViewports(1,&v);
    sourceDepth(reinterpret_cast<void*>(nativeManager),nullptr,0);context->DrawIndexed(3,0,0);
    sourceDepth(reinterpret_cast<void*>(nativeManager),nullptr,1);return 1;
}
inline Word __declspec(naked) invoke(Word,Word,Word) {
    __asm {
        push ebx
        mov ebx,[esp+8]
        mov ecx,[esp+12]
        lea eax,returned
        mov caller,eax
        push dword ptr[esp+16]
        xor edx,edx
        call sourceShield
    returned:
        pop ebx
        ret
    }
}
struct TargetsInit {TargetsInit(){ship[0]=0x00796F0C;ship[0x1BC/4]=reinterpret_cast<DWORD>(shield);manager[0]=0x007B8D4C;
    invoke(reinterpret_cast<Word>(ship),reinterpret_cast<Word>(shield),reinterpret_cast<Word>(manager));}};
inline TargetsInit targetsInit;
inline std::array<float,4> tint(DWORD frame){const float f=.02f+.025f*(frame%8);return {f*.5f,f,.02f,1};}
inline void initialize(ID3D11Device* d,ID3D11DeviceContext* c,ID3D11DepthStencilView* z) {
    device=d;context=c;nativeDepth=z;
    D3D11_TEXTURE2D_DESC td{};td.Width=1920;td.Height=1080;td.MipLevels=td.ArraySize=1;td.SampleDesc.Count=8;
    td.Format=DXGI_FORMAT_B8G8R8A8_UNORM;td.BindFlags=D3D11_BIND_RENDER_TARGET;
    check(d->CreateTexture2D(&td,nullptr,&nativeColor));check(d->CreateRenderTargetView(nativeColor.Get(),nullptr,&nativeTarget));
    const char* shader="cbuffer Params:register(b0){float4 tint;} Texture2D image:register(t0); float4 vs(float3 p:POSITION):SV_Position{return float4(p,1);} float4 ps():SV_Target{return image.Load(int3(0,0,0))*tint;}";
    ComPtr<ID3DBlob> vs,ps;check(D3DCompile(shader,strlen(shader),nullptr,nullptr,nullptr,"vs","vs_4_1",0,0,&vs,nullptr));
    check(D3DCompile(shader,strlen(shader),nullptr,nullptr,nullptr,"ps","ps_4_1",0,0,&ps,nullptr));
    check(d->CreateVertexShader(vs->GetBufferPointer(),vs->GetBufferSize(),nullptr,&vertex));check(d->CreatePixelShader(ps->GetBufferPointer(),ps->GetBufferSize(),nullptr,&pixel));
    D3D11_INPUT_ELEMENT_DESC e{"POSITION",0,DXGI_FORMAT_R32G32B32_FLOAT,0,0,D3D11_INPUT_PER_VERTEX_DATA,0};
    check(d->CreateInputLayout(&e,1,vs->GetBufferPointer(),vs->GetBufferSize(),&layout));
    float data[32]{};const float positions[12]{-1,-1,0,-1,1,0,1,-1,0,1,1,0};
    for(unsigned i=0;i<4;++i)memcpy(data+i*8,positions+i*3,12);
    auto buffer=[&](UINT bytes,UINT flags,const void* initial){D3D11_BUFFER_DESC b{};b.ByteWidth=bytes;b.BindFlags=flags;
        D3D11_SUBRESOURCE_DATA p{initial,0,0};ComPtr<ID3D11Buffer> out;check(d->CreateBuffer(&b,initial?&p:nullptr,&out));return out;};
    vertices=buffer(sizeof(data),D3D11_BIND_VERTEX_BUFFER,data);const UINT ids[6]{0,1,2,2,1,3};indices=buffer(sizeof(ids),D3D11_BIND_INDEX_BUFFER,ids);
    D3D11_BUFFER_DESC cb{};cb.ByteWidth=16;cb.BindFlags=D3D11_BIND_CONSTANT_BUFFER;cb.Usage=D3D11_USAGE_DYNAMIC;cb.CPUAccessFlags=D3D11_CPU_ACCESS_WRITE;
    check(d->CreateBuffer(&cb,nullptr,&constants));
    td.Width=td.Height=td.SampleDesc.Count=1;td.BindFlags=D3D11_BIND_SHADER_RESOURCE;td.Format=DXGI_FORMAT_R8G8B8A8_UNORM;
    DWORD whitePixel=0xffffffff;D3D11_SUBRESOURCE_DATA wp{&whitePixel,4,0};ComPtr<ID3D11Texture2D> wt;
    check(d->CreateTexture2D(&td,&wp,&wt));check(d->CreateShaderResourceView(wt.Get(),nullptr,&white));
    D3D11_BLEND_DESC b{};auto& blendTarget=b.RenderTarget[0];blendTarget.BlendEnable=TRUE;
    blendTarget.SrcBlend=blendTarget.DestBlend=blendTarget.SrcBlendAlpha=blendTarget.DestBlendAlpha=D3D11_BLEND_ONE;
    blendTarget.BlendOp=blendTarget.BlendOpAlpha=D3D11_BLEND_OP_ADD;blendTarget.RenderTargetWriteMask=15;check(d->CreateBlendState(&b,&blend));
    D3D11_RASTERIZER_DESC r{};r.FillMode=D3D11_FILL_SOLID;r.CullMode=D3D11_CULL_NONE;r.DepthClipEnable=TRUE;r.MultisampleEnable=TRUE;
    check(d->CreateRasterizerState(&r,&raster));
    D3D11_DEPTH_STENCIL_DESC depth{};depth.DepthEnable=TRUE;depth.DepthFunc=D3D11_COMPARISON_LESS_EQUAL;depth.DepthWriteMask=D3D11_DEPTH_WRITE_MASK_ZERO;
    check(d->CreateDepthStencilState(&depth,&depthOff));depth.DepthWriteMask=D3D11_DEPTH_WRITE_MASK_ALL;check(d->CreateDepthStencilState(&depth,&depthOn));
    initialized=true;
}
inline void draw(BYTE* base,ID3D11Texture2D* back) {
    if(!initialized)return;auto& ledger=*reinterpret_cast<replacement::Store*>(base+replacement::Offset);
    auto& notices=*reinterpret_cast<native_foreground::source_notice::Store*>(base+native_foreground::source_notice::Offset);
    if(!notices.magic)native_foreground::source_notice::initialize(notices,ledger.session,GetCurrentProcessId());
    const DWORD frame=static_cast<DWORD>(InterlockedCompareExchange(&ledger.native_frame,0,0));replacement::Control ctrl{};replacement::read(ledger.control,ctrl);
    native_foreground::source_notice::offer(notices,ledger,frame,reinterpret_cast<DWORD>(ship),reinterpret_cast<DWORD>(shield),ctrl.owner,GetCurrentThreadId());
    auto value=tint(frame);D3D11_MAPPED_SUBRESOURCE mapped{};check(context->Map(constants.Get(),0,D3D11_MAP_WRITE_DISCARD,0,&mapped));
    memcpy(mapped.pData,value.data(),16);context->Unmap(constants.Get(),0);
    const float blue[]{.02f,.05f,.3f,1};context->ClearRenderTargetView(nativeTarget.Get(),blue);
    invoke(reinterpret_cast<Word>(ship),reinterpret_cast<Word>(shield),reinterpret_cast<Word>(manager));
    context->OMSetRenderTargets(0,nullptr,nullptr);context->ResolveSubresource(back,0,nativeColor.Get(),0,DXGI_FORMAT_B8G8R8A8_UNORM);
    ID3D11Buffer* noBuffer=nullptr;ID3D11ShaderResourceView* noView=nullptr;UINT zero=0;
    context->IASetVertexBuffers(0,1,&noBuffer,&zero,&zero);context->IASetIndexBuffer(nullptr,DXGI_FORMAT_UNKNOWN,0);context->IASetInputLayout(nullptr);
    context->PSSetConstantBuffers(0,1,&noBuffer);context->PSSetShaderResources(0,1,&noView);context->VSSetShader(nullptr,nullptr,0);context->PSSetShader(nullptr,nullptr,0);
}
inline DWORD readPixel(ID3D11Texture2D* texture,UINT x,UINT y) {
    D3D11_TEXTURE2D_DESC td{};texture->GetDesc(&td);td.Width=td.Height=1;td.MipLevels=td.ArraySize=td.SampleDesc.Count=1;
    td.BindFlags=td.MiscFlags=0;td.Usage=D3D11_USAGE_STAGING;td.CPUAccessFlags=D3D11_CPU_ACCESS_READ;
    ComPtr<ID3D11Texture2D> staging;check(device->CreateTexture2D(&td,nullptr,&staging));D3D11_BOX box{x,y,0,x+1,y+1,1};
    context->CopySubresourceRegion(staging.Get(),0,0,0,0,texture,0,&box);D3D11_MAPPED_SUBRESOURCE mapped{};check(context->Map(staging.Get(),0,D3D11_MAP_READ,0,&mapped));
    DWORD value;memcpy(&value,mapped.pData,4);context->Unmap(staging.Get(),0);return value;
}
inline void __cdecl verify(void* targetValue,void* colorValue,void* coverageValue,Word frame,Word owner,const float* origin,const float* scale) {
    if(verified>=3||frame==verifiedFrame)return;
    auto* target=static_cast<ID3D11RenderTargetView*>(targetValue);auto* color=static_cast<ID3D11ShaderResourceView*>(colorValue);
    auto* coverage=static_cast<ID3D11ShaderResourceView*>(coverageValue);
    ComPtr<ID3D11Resource> r;target->GetResource(&r);ComPtr<ID3D11Texture2D> output;check(r.As(&output));
    r.Reset();color->GetResource(&r);ComPtr<ID3D11Texture2D> returned;check(r.As(&returned));
    r.Reset();coverage->GetResource(&r);ComPtr<ID3D11Texture2D> picking;check(r.As(&picking));
    UINT qx{},qy{};
    if(!verified){
        // Fixture-only bounded readback. No such callback exists in SFC.
        D3D11_TEXTURE2D_DESC d{};picking->GetDesc(&d);d.BindFlags=d.MiscFlags=0;d.Usage=D3D11_USAGE_STAGING;d.CPUAccessFlags=D3D11_CPU_ACCESS_READ;
        ComPtr<ID3D11Texture2D> staging;check(device->CreateTexture2D(&d,nullptr,&staging));context->CopyResource(staging.Get(),picking.Get());
        D3D11_MAPPED_SUBRESOURCE m{};check(context->Map(staging.Get(),0,D3D11_MAP_READ,0,&m));bool found=false;
        for(UINT y=8;y<1072&&!found;y+=3)for(UINT x=8;x<1912;x+=3){
            const UINT nx=UINT(origin[0]+(x+.5f)/scale[0]),ny=UINT(origin[1]+(y+.5f)/scale[1]);
            const float fx=(nx+.5f-origin[0])*scale[0],fy=(ny+.5f-origin[1])*scale[1];
            const UINT xx=UINT(floor(fx)),yy=UINT(floor(fy));
            if(fx-floor(fx)<.1f||fx-floor(fx)>.9f||fy-floor(fy)<.1f||fy-floor(fy)>.9f)continue;
            if(nx>=1920||ny>=1080||xx>=1920||yy>=1080)continue;
            DWORD tag;memcpy(&tag,static_cast<BYTE*>(m.pData)+yy*m.RowPitch+xx*4,4);
            if(tag==owner){candidateX=nx;candidateY=ny;found=true;break;}
        }
        context->Unmap(staging.Get(),0);if(!found)return;
    }
    qx=UINT(floor((candidateX+.5f-origin[0])*scale[0]));qy=UINT(floor((candidateY+.5f-origin[1])*scale[1]));
    if(readPixel(picking.Get(),qx,qy)!=owner)return;
    const DWORD source=readPixel(returned.Get(),qx,qy),actual=readPixel(output.Get(),candidateX,candidateY);
    D3D11_SHADER_RESOURCE_VIEW_DESC sourceDesc{};color->GetDesc(&sourceDesc);
    const bool bgra=sourceDesc.Format==DXGI_FORMAT_B8G8R8A8_UNORM||sourceDesc.Format==DXGI_FORMAT_B8G8R8A8_UNORM_SRGB;
    const bool srgb=sourceDesc.Format==DXGI_FORMAT_B8G8R8A8_UNORM_SRGB||sourceDesc.Format==DXGI_FORMAT_R8G8B8A8_UNORM_SRGB;
    const auto t=tint(frame);
    for(unsigned channel=0;channel<3;++channel){float src=float((source>>(8*(bgra?2-channel:channel)))&255)/255.f;
        if(srgb)src=src<=.04045f?src/12.92f:std::pow((src+.055f)/1.055f,2.4f);
        const unsigned got=(actual>>(8*(2-channel)))&255;const unsigned expected=UINT(std::min(255.f,(src+t[channel])*255.f)+.5f);
        if(std::abs(int(got)-int(expected))>2)throw std::runtime_error("Native foreground returned hull pixels differ from matching-frame additive contribution");}
    const DWORD outside=readPixel(output.Get(),1,1);const float blue[]{.02f,.05f,.3f};
    for(unsigned channel=0;channel<3;++channel){const unsigned got=(outside>>(8*(2-channel)))&255;
        const unsigned expected=UINT((blue[channel]+t[channel])*255.f+.5f);
        if(std::abs(int(got)-int(expected))>2)throw std::runtime_error("Native foreground doubled or wrong source frame outside hull");}
    ++verified;verifiedFrame=frame;std::cout<<"NATIVE_FOREGROUND_PIXELS_PASS frame="<<frame<<" sample="<<candidateX<<','<<candidateY<<" count="<<verified<<'\n';
}
inline void shutdown(){initialized=false;nativeTarget.Reset();nativeColor.Reset();nativeDepth.Reset();vertex.Reset();pixel.Reset();layout.Reset();
    vertices.Reset();indices.Reset();constants.Reset();white.Reset();blend.Reset();raster.Reset();depthOff.Reset();depthOn.Reset();context.Reset();device.Reset();}
} // namespace foreground_fixture
extern "C" __declspec(dllexport) BOOL __cdecl SFCNativeForegroundFixture(native_foreground::shield_hooks::FixtureTargets* out) {
    if(!out||out->bytes!=sizeof(*out))return FALSE;
    *out={sizeof(*out),reinterpret_cast<void*>(foreground_fixture::sourceShield),
        reinterpret_cast<native_foreground::shield_hooks::Depth>(foreground_fixture::sourceDepth),
        foreground_fixture::caller,reinterpret_cast<native_foreground::shield_hooks::Word>(&foreground_fixture::resource),foreground_fixture::verify};return TRUE;
}
