#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include "../tools/d3d9_proof/game_output_wire.h"
#include "../tools/d3d9_proof/worker_gpu_fence.h"
#include "../tools/d3d9_proof/camera_left.h"
#include "../tools/remix_runtime/native_viewport_mapping.h"
#include <iostream>
int main(){unsigned checks=0;auto test=[&](bool ok){++checks;if(!ok){std::cerr<<"Game output FAIL "<<checks<<'\n';ExitProcess(1);}};
 WorkerGpuFence fence;bool rejected=false;try{fence.wait();}catch(const std::runtime_error&){rejected=true;}test(rejected);
 native_viewport::Mapping map{};uint32_t viewport[4]{200,30,1720,1020};
 test(native_viewport::mapping(1920,1080,viewport,map));
 test(map.origin[0]==200&&map.origin[1]==30);
 test(std::abs(map.scale[0]-1920.f/1720)<1e-6f&&std::abs(map.scale[1]-1080.f/1020)<1e-6f);
 for(unsigned axis=0;axis<2;++axis)for(float ndc:{-.7f,0.f,.7f}){
  const float full=(ndc+1)*float(axis?1080:1920)/2;
  const float native=float(viewport[axis])+(ndc+1)*viewport[axis+2]/2;
  test(std::abs((native-map.origin[axis])*map.scale[axis]-full)<.001f);
 }
 viewport[2]=0;test(!native_viewport::mapping(1920,1080,viewport,map));
 viewport[2]=1920;test(!native_viewport::mapping(1920,1080,viewport,map));
 viewport[0]=0;viewport[1]=0;viewport[3]=1080;test(native_viewport::mapping(1920,1080,viewport,map));
 test(map.scale[0]==1&&map.scale[1]==1&&map.origin[0]==0&&map.origin[1]==0);
 float view[16]{1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1},offset[3]{};
 test(diagnostic_offset::camera_left(view,5,offset));test(offset[0]==-5&&offset[1]==0&&offset[2]==0);
 view[0]=0;view[2]=-1;view[8]=1;view[10]=0;
 test(diagnostic_offset::camera_left(view,5,offset));test(offset[0]==0&&offset[1]==0&&offset[2]==5);
 for(unsigned i=0;i<3;++i){float projected=0;for(unsigned j=0;j<3;++j)projected+=view[4*i+j]*offset[j];test(std::abs(projected-(i?0.f:-5.f))<1e-5f);}
 test(!diagnostic_offset::camera_left(view,-5,offset));view[2]=2;test(!diagnostic_offset::camera_left(view,5,offset));
 game_output::Pool p{};test(sizeof(p)==576);test(game_output::Offset>=10*1024*1024+1154688);
 test(game_output::reserve(p)==0);test(game_output::reserve(p)==1);test(game_output::reserve(p)==-1);test(p.header.busy==1);
 p.slots[0].state=output_wire::ready;test(game_output::reserve(p)==0);test(p.header.overwritten==1);
 p.slots[0].state=output_wire::acquired;test(game_output::reserve(p)==-1);test(p.slots[0].state==output_wire::acquired);
 p.slots[1].state=output_wire::idle;test(game_output::reserve(p)==1);
 p.header.stopped=1;p.slots[0].state=output_wire::idle;test(game_output::reserve(p)==-1);
 DWORD session[4]{1,2,3,4};game_output::Metadata m{};m.source_sequence=7;memcpy(m.source_session,session,16);m.checksum=game_output::checksum(m);
 test(game_output::valid(m,session));game_output::metadata(p.slots[0],m);test(game_output::metadata(p.slots[0]).source_sequence==7);
 auto bad=m;bad.checksum^=1;test(!game_output::valid(bad,session));bad=m;bad.source_session[0]=9;bad.checksum=game_output::checksum(bad);test(!game_output::valid(bad,session));
 DWORD row[96]{};row[1]=2;row[2]=3;row[7]=4;output_wire::Packet packet{};packet.owner=2;packet.source_frame=3;packet.revision=4;packet.source_state_hash=5;
 test(game_output::matches(packet,m,row,session,5,7));test(!game_output::matches(packet,m,row,session,5,8));test(!game_output::matches(packet,m,row,session,6,7));
 packet.owner=3;test(!game_output::matches(packet,m,row,session,5,7));packet.owner=2;++packet.revision;test(!game_output::matches(packet,m,row,session,5,7));
 std::cout<<"Game output wire PASS "<<checks<<" checks pointer_bits="<<sizeof(void*)*8<<'\n';return 0;
}
