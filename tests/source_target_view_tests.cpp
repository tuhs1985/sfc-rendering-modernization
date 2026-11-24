#include "../src/transport/source_target_view.h"
#include "../tools/d3d9_proof/output_target.h"
#include <memory>
#include <cstdio>
#include <stdexcept>
void need(bool value,const char* why){if(!value)throw std::runtime_error(why);}
int main(){try{
    using namespace sfc_source_view;
    auto bytes=std::make_unique<uint8_t[]>(MappingBytes);const std::array<uint32_t,4> session{1,2,3,4};
    NativeTarget result{};need(target(bytes.get(),MappingBytes,session,17,result)==Status::Empty,"Passive target requires assets");
    auto* native=new(bytes.get()+TargetOffset)output_target::Store();
    output_target::Notice n{};n.pid=17;std::memcpy(n.session,session.data(),16);n.observed=1;n.width=1920;n.height=1080;n.device=n.generation=1;
    static_assert(sizeof(NativeTarget)==sizeof(output_target::Notice)&&sizeof(TargetSlot)==sizeof(output_target::Store)&&TargetOffset==output_target::Offset);
    output_target::publish(*native,n);need(target(bytes.get(),MappingBytes,session,17,result)==Status::Ready&&result.width==1920&&result.generation==1,"Actual native notice not decoded");
    ++native->sequence;need(target(bytes.get(),MappingBytes,session,17,result)==Status::Retry,"Torn target accepted");++native->sequence;
    auto wrong=session;wrong[0]++;need(target(bytes.get(),MappingBytes,wrong,17,result)==Status::InvalidHeader,"Wrong target session accepted");
    need(target(bytes.get(),MappingBytes,session,18,result)==Status::InvalidHeader,"Wrong target PID accepted");
    n.width=1280;n.height=720;++n.generation;output_target::publish(*native,n);
    need(target(bytes.get(),MappingBytes,session,17,result)==Status::Ready&&result.width==1280&&result.generation==2,"Resize/target generation lost");
    native->notice.width=1920;need(target(bytes.get(),MappingBytes,session,17,result)==Status::InvalidFrame,"Corrupt extent/checksum accepted");
    n.width=n.height=0;output_target::publish(*native,n);need(target(bytes.get(),MappingBytes,session,17,result)==Status::Stopped,"Native stop target ignored");
    need(target(bytes.get(),TargetOffset,session,17,result)==Status::InvalidHeader,"Short map accepted");
    std::puts("PASS passive/ready native target notice, exact layout, session/PID, torn/changed/corrupt generation and stop");return 0;
}catch(const std::exception& e){std::fprintf(stderr,"%s\n",e.what());return 1;}}
