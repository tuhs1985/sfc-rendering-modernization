#define main legacy_mesh_tests_main
#include "m1_mesh_export_tests.cpp"
#undef main
#include "../tools/m1_component/m1_live_scene.h"
#include "../tools/d3d9_proof/live_owner_decode.h"
static LiveScene scene;
struct Frame {DWORD owner=0,revision=0,frame=0,active=0;float model[16]{},view[16]{},projection[16]{},viewport[6]{};};
int wmain(int argc,wchar_t** argv){
 check_mesh(argc==3,"persistent channel/output");check_mesh(scene.start(argv[1],argv[2])&&scene.persistent,"persistent native worker start");
 Memory x;x.id.frame=1;x.id.elapsed=34;x.id.thread=GetCurrentThreadId();
 x.word(0x1000,0x796f0c);x.word(0x2000,0x7985a4);x.word(0x2154,0x50000);x.word(0x8000,0x21);x.word(0x8014,1);x.word(0x8018,0);x.word(0x801c,2);x.word(0x8020,8);
 memcpy(x.data.data()+0x2014,"Assets/Models/test/test.mod",27);memcpy(x.data.data()+0x50000,"test_a\0\0test_ai",15);
 x.word(0x60000,0x795c54);x.word(0x6000c,0x70000);x.word(0x60020,0x71000);
 memcpy(x.data.data()+0x70008,"Assets/Models/test/test_a.bmp",29);memcpy(x.data.data()+0x71008,"Assets/Models/test/test_ai.bmp",30);
 x.word(0x7f60,0x72000);x.word(0x7f64,0x73000);x.word(0x72004,123);x.word(0x73004,456);x.word(x.id.manager+0x1ed0,1);
 auto ident=sfc_scene::identity();memcpy(x.data.data()+x.id.ship+0x980,ident.data(),64);x.word(x.id.ship+0x980+64,0x100);
 float position[3]{0,0,-10};memcpy(x.data.data()+x.id.ship+0x34,position,12);
 memcpy(x.data.data()+x.id.manager+0x628,ident.data(),64);x.word(x.id.manager+0x628+64,0x100);
 auto projection=sfc_scene::Matrix{};projection[0]=1;projection[5]=1920.f/1080;projection[10]=-1.0002f;projection[11]=-2.0002f;projection[14]=-1;
 memcpy(x.data.data()+x.id.manager+0x55c,projection.data(),64);
 const float viewport[]{0,0,1920,1080,960,540};memcpy(x.data.data()+x.id.manager+0x75c,viewport,24);
 auto read=[&](auto a,auto* dst,auto n){
  if(a==0x008cc620&&n==4){DWORD registry=0x60000;memcpy(dst,&registry,4);return true;}
  if(a>=0xc6a004&&a<0xc74004&&n==4){const bool cosine=a>=0xc6c004;const auto index=(a-(cosine?0xc6c004:0xc6a004))/4;
   const float value=float(cosine?cos(double(index)*6.283185307179586/8192):sin(double(index)*6.283185307179586/8192));memcpy(dst,&value,4);return true;}
  return x.read(a,dst,n);
 };
 sfc_scene::Matrix world{};check_mesh(sfc_scene::pose(x.id.ship,world,read),"fresh simulation builder");memcpy(x.data.data()+x.id.manager+0x6f4,world.data(),64);x.word(x.id.manager+0x6f4+64,0x100);
 scene.observe(x.id,read,[]{return true;});check_mesh(scene.registry.contains(1)&&scene.capture_attempts==1,"native capture seeds resident instance");
 scene.directSource.store->header.selected=static_cast<LONG64>(live_owner::selection(1,1));
 uint64_t watermark=0;DWORD malformed=0;LARGE_INTEGER start{},end{},frequency{};QueryPerformanceFrequency(&frequency);QueryPerformanceCounter(&start);
 for(DWORD frame=2;frame<=121;++frame){
  position[0]=float(frame)*.1f;memcpy(x.data.data()+x.id.ship+0x34,position,12);
  const std::uint16_t angle=static_cast<std::uint16_t>(frame*8);memcpy(x.data.data()+x.id.ship+0x94,&angle,2);
  auto view=ident;view[3]=frame>=60?3.f:0.f;memcpy(x.data.data()+x.id.manager+0x628,view.data(),64);
  scene.directSource.begin(frame);sfc_calibration::begin(scene.calibration,frame);
  scene.updatePersistent(x.id.manager,frame,frame*16,read);
  live_owner::Packet published{};Frame decoded{};
  check_mesh(live_owner::take(scene.directSource.store->input,scene.directSource.store->header,published,watermark,malformed)&&!malformed,"full-rate offscreen native publication");
  check_mesh(live_owner::decode(published,decoded)&&decoded.frame==frame&&decoded.owner==1&&decoded.revision==1,"stable instance and current pose");
  check_mesh(fabs(decoded.model[3]-position[0])<1e-5&&decoded.view[3]==view[3],"fresh simulation position and current camera");
  const float point[3]{};check_mesh(live_owner::projection_matches(published,decoded,point),"current composed projection oracle");
 }
 QueryPerformanceCounter(&end);
 check_mesh(scene.capture_attempts==1&&scene.registry.admitted==1&&scene.registry.offscreen==120,"no recapture or epoch churn during camera/pose updates");
 scene.retire(1,122,2000);scene.directSource.begin(122);sfc_calibration::begin(scene.calibration,122);scene.updatePersistent(x.id.manager,122,2000,read);
 live_owner::Packet old{};check_mesh(!scene.registry.contains(1)&&!live_owner::take(scene.directSource.store->input,scene.directSource.store->header,old,watermark,malformed),"removed instance cannot publish stale pose");
 check_mesh(scene.stop(),"persistent worker joins and storage stops");
 std::cout<<"Persistent native scene PASS frames=120 captures=1 instance_generations=1 offscreen=120 mean_update_us="<<double(end.QuadPart-start.QuadPart)*1e6/double(frequency.QuadPart)/120<<"\n";
}
