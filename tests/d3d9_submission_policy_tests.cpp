#include "../tools/d3d9_proof/live_owner_decode.h"
#include "../tools/d3d9_proof/startup_policy.h"
#include "../tools/scene_bridge/persistent_scene.h"
#include <vector>
#include <iostream>
struct Frame{DWORD owner=0,revision=0,frame=0,active=0;float model[16]{},view[16]{},projection[16]{},viewport[4]{};};
struct Vertex{float p[3]{};};
int main(){unsigned checks=0;auto test=[&](bool x){++checks;if(!x)throw std::runtime_error("Submission policy regression");};
 SetEnvironmentVariableW(L"SFC_D3D9_LEGACY_STARTUP_WARMUP",nullptr);test(startup_policy::bootstrap_presents()==1);
 SetEnvironmentVariableW(L"SFC_D3D9_LEGACY_STARTUP_WARMUP",L"1");test(startup_policy::bootstrap_presents()==24);
 SetEnvironmentVariableW(L"SFC_D3D9_LEGACY_STARTUP_WARMUP",L"0");test(startup_policy::bootstrap_presents()==1);
 SetEnvironmentVariableW(L"SFC_D3D9_LEGACY_STARTUP_WARMUP",L"invalid");bool invalid=false;try{startup_policy::bootstrap_presents();}catch(...){invalid=true;}test(invalid);
 SetEnvironmentVariableW(L"SFC_D3D9_LEGACY_STARTUP_WARMUP",nullptr);
 live_owner::Packet packet{};auto& r=packet.row;r[1]=r[2]=r[4]=r[5]=r[6]=r[7]=r[48]=1;
 auto model=sfc_scene::identity(),view=model,projection=sfc_scene::Matrix{};model[11]=-4;
 projection[0]=1;projection[5]=1920.f/1080;projection[10]=-1.02f;projection[11]=-2.02f;projection[14]=-1;
 memcpy(r.data()+8,model.data(),64);r[24]=0x100;memcpy(r.data()+49,view.data(),64);r[65]=0x100;memcpy(r.data()+66,projection.data(),64);
 const float viewport[]{0,0,1920,1080,960,540};memcpy(r.data()+83,viewport,24);
 auto screen=sfc_scene::identity();screen[0]=960;screen[5]=-540;screen[3]=960;screen[7]=540;
 auto composed=sfc_scene::multiply(screen,sfc_scene::multiply(projection,sfc_scene::multiply(view,model)));memcpy(r.data()+25,composed.data(),64);
 Frame frame{};test(live_owner::decode(packet,frame));std::vector<Vertex> points{{{0,0,4}}};
 test(!live_owner::projection_matches(packet,frame,points[0].p)); // Undefined screen position,valid finite geometry.
 test(live_owner::audit_projection(packet,frame,points,false)==0);
 test(live_owner::audit_projection(packet,frame,points,true)==1);
 test(live_owner::decode(packet,frame)); // Optional evidence does not poison eligibility.
 points[0].p[2]=0;test(live_owner::audit_projection(packet,frame,points,true)==0);
 float shifted=0;memcpy(&shifted,r.data()+28,4);shifted+=10;memcpy(r.data()+28,&shifted,4); // Real mismatch remains detectable as evidence.
 test(live_owner::audit_projection(packet,frame,points,true)>0);
 r[8]=0x7fc00000;test(!live_owner::decode(packet,frame));
 std::cout<<"Submission policy PASS "<<checks<<" checks;startup1or24 projection_nonblocking finite_required=1\n";
}
