#define REMIX_ALLOW_X86
#include "../artifacts/remix-runtime/deps/remix_c.h"
#include <windows.h>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <fstream>
static void check(remixapi_ErrorCode code,const char*){if(code!=REMIXAPI_ERROR_CODE_SUCCESS)throw std::runtime_error("effect API failure");}
#include "../tools/d3d9_proof/direct_effect_lights.h"
static unsigned checks=0,creates=0,destroys=0,draws=0;
static remixapi_Float3D lastPosition{},lastRadiance{};
static void test(bool b){++checks;if(!b)throw std::runtime_error("effect check "+std::to_string(checks));}
static remixapi_ErrorCode REMIXAPI_CALL create(const remixapi_LightInfo* info,remixapi_LightHandle* out){
 const auto* sphere=static_cast<const remixapi_LightInfoSphereEXT*>(info->pNext);test(sphere->sType==REMIXAPI_STRUCT_TYPE_LIGHT_INFO_SPHERE_EXT);
 lastPosition=sphere->position;lastRadiance=info->radiance;*out=reinterpret_cast<remixapi_LightHandle>(uintptr_t(++creates));return REMIXAPI_ERROR_CODE_SUCCESS;}
static remixapi_ErrorCode REMIXAPI_CALL destroy(remixapi_LightHandle){++destroys;return REMIXAPI_ERROR_CODE_SUCCESS;}
static remixapi_ErrorCode REMIXAPI_CALL draw(remixapi_LightHandle){++draws;return REMIXAPI_ERROR_CODE_SUCCESS;}
int main(int argc,char** argv){
 DWORD session[]{1,2,3,4};auto source=std::make_unique<sfc_effect_lights::Store>();auto config=std::make_unique<remix_effect_lights::Store>();
 auto init=[&](sfc_light_transport::Header& h,DWORD magic,DWORD size){h.magic=magic;h.bytes=size;memcpy(h.session,session,16);h.pid=GetCurrentProcessId();};
 init(source->header,sfc_effect_lights::Magic,sizeof(*source));init(config->header,remix_effect_lights::Magic,sizeof(*config));source->header.reserved[0]=1;
 remix_effect_lights::Config settings{};for(auto& row:settings.rows){row.enabled=1;row.radius=2;row.gain[0]=row.gain[1]=row.gain[2]=3;}
 settings.checksum=remix_effect_lights::checksum(settings);test(remix_effect_lights::valid(settings));
 sfc_light_transport::publish(config->header,config->cell,settings,1);
 sfc_effect_lights::Frame bank{},a{},b{};bank.gate=1;for(unsigned i=0;i<4;++i)bank.enables[i]=1;
 auto set=[&](unsigned slot,DWORD type,float x){bank.records[slot][0]=type;float p[]{x,20,30},rgb[]{.5f,.25f,0},range=100;
  memcpy(bank.records[slot]+4,p,12);memcpy(bank.records[slot]+7,rgb,12);memcpy(bank.records[slot]+10,&range,4);
  bank.records[slot][1]=0x7fc00000;}; // native type5 unused direction NaN must not reject position/RGB
 set(2,5,10);set(3,1,40);
 auto read=[&](DWORD at,void* out,DWORD bytes){const void* p=at==0x1778?static_cast<const void*>(bank.enables):at==0x1eb8?static_cast<const void*>(&bank.gate):static_cast<const void*>(bank.records);memcpy(out,p,bytes);return true;};
 test(sfc_effect_lights::capture(*source,0,10,a,b,read));
 remixapi_Interface api{};api.CreateLight=create;api.DestroyLight=destroy;api.DrawLightInstance=draw;
 auto trace=std::make_unique<effect_light_trace::Store>();init(trace->header,effect_light_trace::Magic,sizeof(*trace));trace->header.reserved[0]=1;
 DirectEffectLights lights;lights.source=source.get();lights.config=config.get();lights.trace=trace.get();
 lights.update(api,10,session,GetCurrentProcessId());lights.draw(api);test(creates==2&&draws==2&&lastPosition.x==40&&lastRadiance.x==1.5f);
 effect_light_trace::Frame observed{};ULONGLONG stamp=0;
 test(sfc_light_transport::read(trace->cells[10%effect_light_trace::Frames],observed,stamp));
 test(observed.frame==10&&observed.native.frame==10&&observed.sourceQpc==observed.native.captured&&observed.submittedQpc==stamp);
 test(observed.status[0]==1&&observed.status[1]==1&&observed.lights[1].position[0]==40&&observed.lights[1].radiance[0]==1.5f);
 test(effect_light_trace::enabled(trace.get(),session,GetCurrentProcessId()));
 if(argc==2){std::ofstream out(argv[1],std::ios::binary);out.write(reinterpret_cast<const char*>(&observed),sizeof(observed));test(bool(out));}
 lights.update(api,10,session,GetCurrentProcessId());test(creates==2&&destroys==0);
 set(2,5,11);test(sfc_effect_lights::capture(*source,0,11,a,b,read));lights.update(api,11,session,GetCurrentProcessId());test(creates==3&&destroys==1);
 // First disabled native slot terminates response:later enabled slots cannot leak.
 bank.enables[2]=0;test(sfc_effect_lights::capture(*source,0,12,a,b,read));lights.update(api,12,session,GetCurrentProcessId());test(destroys==3);
 bank.enables[2]=1;test(sfc_effect_lights::capture(*source,0,13,a,b,read));lights.update(api,13,session,GetCurrentProcessId());test(creates==5);
 bank.gate=0;test(sfc_effect_lights::capture(*source,0,14,a,b,read));lights.update(api,14,session,GetCurrentProcessId());test(destroys==5);
 lights.draw(api);test(sfc_light_transport::read(trace->cells[14%effect_light_trace::Frames],observed,stamp)&&observed.status[0]==0&&observed.status[1]==0);
 trace->header.reserved[0]=0;test(!effect_light_trace::enabled(trace.get(),session,GetCurrentProcessId()));
 bank.gate=1;test(sfc_effect_lights::capture(*source,0,15,a,b,read));lights.update(api,15,session,GetCurrentProcessId());test(creates==7);
 lights.update(api,16,session,GetCurrentProcessId());test(destroys==7); // missing exact frame never retains an effect
 test(sfc_effect_lights::capture(*source,0,17,a,b,read));DWORD other[]{9,2,3,4};lights.update(api,17,other,GetCurrentProcessId());test(creates==7);
 source->header.reserved[0]=0;test(!sfc_effect_lights::capture(*source,0,18,a,b,read));source->header.reserved[0]=1;
 auto unstable=[&](DWORD at,void* out,DWORD bytes){read(at,out,bytes);if(at==0x1778)bank.enables[3]^=1;return true;};
 test(!sfc_effect_lights::capture(*source,0,19,a,b,unstable));
 bank.enables[3]=1;bank.records[2][7]=0x7fc00000;test(sfc_effect_lights::capture(*source,0,20,a,b,read));lights.update(api,20,session,GetCurrentProcessId());test(lights.invalid==1&&creates==8);
 lights.close(api);test(creates==destroys);
 std::cout<<"Effect lights PASS "<<checks<<" checks;frame source on_off motion color prefix session malformed shutdown\n";
}
