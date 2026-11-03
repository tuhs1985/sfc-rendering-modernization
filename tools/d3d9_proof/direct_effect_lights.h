// Remix adapter only. Scene light persistence deliberately does not apply here.
#pragma once
#include "effect_light_wire.h"
#include "effect_light_trace.h"
struct DirectEffectLights {
 remixapi_LightHandle handles[62]{};remix_effect_lights::Light previous[62]{};
 sfc_effect_lights::Store* source=nullptr;remix_effect_lights::Store* config=nullptr;
 uint64_t frames=0,active=0,invalid=0,unavailable=0,changes=0;
 bool seen[62]{};
 effect_light_trace::Store* trace=nullptr;effect_light_trace::Frame traceFrame{};bool tracePending=false;
 void attach(BYTE* base){source=reinterpret_cast<sfc_effect_lights::Store*>(base+sfc_effect_lights::Offset);
  config=reinterpret_cast<remix_effect_lights::Store*>(base+remix_effect_lights::Offset);
  trace=reinterpret_cast<effect_light_trace::Store*>(base+effect_light_trace::Offset);}
 void update(remixapi_Interface& api,DWORD frame,const DWORD* session,DWORD pid){
  ++frames;memset(seen,0,sizeof(seen));
  sfc_effect_lights::Frame f{};remix_effect_lights::Config c{};ULONGLONG tick=0,revision=0;
  bool usable=source&&config&&sfc_effect_lights::valid(*source,session,pid)&&
   sfc_light_transport::valid(config->header,remix_effect_lights::Magic,sizeof(*config),session,0)&&
   sfc_light_transport::read(source->frames[frame%4],f,tick)&&f.frame==frame&&tick==f.captured&&
   sfc_light_transport::read(config->cell,c,revision)&&remix_effect_lights::valid(c)&&revision==c.generation;
  if(!usable)++unavailable;
  tracePending=effect_light_trace::enabled(trace,session,pid);
  if(tracePending){traceFrame={};traceFrame.frame=frame;traceFrame.pid=pid;traceFrame.generation=usable?c.generation:0;
   traceFrame.usable=usable?1:0;traceFrame.sourceQpc=usable?f.captured:0;if(usable)traceFrame.native=f;}
  for(unsigned i=0;i<62;++i){remix_effect_lights::Light light{};const int status=usable?remix_effect_lights::convert(f,c,i+2,light):0;
   if(status<0)++invalid;
   if(status==1){seen[i]=true;++active;
    if(!handles[i]||memcmp(&previous[i],&light,sizeof(light))){
     if(handles[i]){check(api.DestroyLight(handles[i]),"retire effect light");handles[i]=nullptr;}
     remixapi_LightInfo info{};info.sType=REMIXAPI_STRUCT_TYPE_LIGHT_INFO;info.hash=0x534643450000ull+i;
     info.radiance={light.radiance[0],light.radiance[1],light.radiance[2]};
     remixapi_LightInfoSphereEXT sphere{};sphere.sType=REMIXAPI_STRUCT_TYPE_LIGHT_INFO_SPHERE_EXT;
     sphere.position={light.position[0],light.position[1],light.position[2]};sphere.radius=light.radius;info.pNext=&sphere;
     check(api.CreateLight(&info,&handles[i]),"game effect sphere proxy");previous[i]=light;++changes;
    }
   }else if(handles[i]){check(api.DestroyLight(handles[i]),"inactive effect light");handles[i]=nullptr;++changes;}
   if(tracePending){traceFrame.status[i]=status;if(status==1)traceFrame.lights[i]=light;}
  }
 }
 void draw(remixapi_Interface& api){for(unsigned i=0;i<62;++i)if(seen[i]&&handles[i])check(api.DrawLightInstance(handles[i]),"game effect light draw");
  if(tracePending){LARGE_INTEGER q{};if(QueryPerformanceCounter(&q)){traceFrame.submittedQpc=q.QuadPart;
   sfc_light_transport::publish(trace->header,trace->cells[traceFrame.frame%effect_light_trace::Frames],traceFrame,traceFrame.submittedQpc);}tracePending=false;}}
 void close(remixapi_Interface& api){for(auto& h:handles)if(h){check(api.DestroyLight(h),"effect light shutdown");h=nullptr;}
  std::cout<<"EFFECT_LIGHT_SUMMARY frames="<<frames<<" active_slots="<<active<<" invalid="<<invalid<<" unavailable="<<unavailable<<" changes="<<changes<<" remaining=0\n";}
};
