#pragma once
#include <d3d11.h>
#include <d3dcompiler.h>
#include <wrl/client.h>
#include <cstring>

namespace native_foreground::shader_compatibility {
// Metadata belongs to the actual immutable shader object, not a recyclable
// pointer-keyed cache. Reflection runs at creation, never at observed draws.
inline constexpr GUID key{0x9868ab58,0x56c7,0x47f8,{0xa1,0xe4,0x39,0xf4,0x8a,0x18,0x02,0xbb}};
inline bool remember(ID3D11PixelShader* shader,const void* code,SIZE_T bytes) noexcept {
    if(!shader)return false;
    UINT allowed=0;
    Microsoft::WRL::ComPtr<ID3D11ShaderReflection> reflection;
    if(code&&bytes&&SUCCEEDED(D3DReflect(code,bytes,IID_PPV_ARGS(&reflection)))) {
        D3D11_SHADER_DESC desc{};
        if(SUCCEEDED(reflection->GetDesc(&desc))&&!reflection->IsSampleFrequencyShader()) {
            allowed=1;
            for(UINT i=0;i<desc.InputParameters;++i) {
                D3D11_SIGNATURE_PARAMETER_DESC p{};
                if(FAILED(reflection->GetInputParameterDesc(i,&p))||p.SystemValueType==D3D_NAME_COVERAGE||
                   p.SystemValueType==D3D_NAME_SAMPLE_INDEX||(p.SemanticName&&
                   (!_stricmp(p.SemanticName,"SV_Coverage")||!_stricmp(p.SemanticName,"SV_SampleIndex"))))allowed=0;
            }
            // Coverage/depth outputs cannot be substituted by our hull mask.
            for(UINT i=0;i<desc.OutputParameters;++i) {
                D3D11_SIGNATURE_PARAMETER_DESC p{};
                if(FAILED(reflection->GetOutputParameterDesc(i,&p))||p.SystemValueType!=D3D_NAME_TARGET)allowed=0;
            }
        }
        // SV_Coverage input is a special operand and may be absent from the
        // reflected input signature. Inspect the compiler's own disassembly,
        // at creation only, rather than silently treating it as independent.
        Microsoft::WRL::ComPtr<ID3DBlob> assembly;
        if(FAILED(D3DDisassemble(code,bytes,0,nullptr,&assembly)))allowed=0;
        else {
            const auto* text=static_cast<const char*>(assembly->GetBufferPointer());
            if(strstr(text,"vCoverage")||strstr(text,"oMask"))allowed=0;
        }
    }
    return SUCCEEDED(shader->SetPrivateData(key,sizeof(allowed),&allowed))&&allowed;
}
inline bool qualified(ID3D11PixelShader* shader) noexcept {
    UINT allowed=0,size=sizeof(allowed);
    return shader&&SUCCEEDED(shader->GetPrivateData(key,&size,&allowed))&&size==sizeof(allowed)&&allowed==1;
}
inline bool singleSampleReplay(ID3D11PixelShader* shader,UINT mask) noexcept {
    return mask==~0u&&qualified(shader);
}
} // namespace native_foreground::shader_compatibility
