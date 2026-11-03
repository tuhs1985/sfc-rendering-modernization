// Remix-only consumption/normalization. Not shared engine light semantics.
#pragma once
#include "remix_light_wire.h"
#include "remix_light_shapes.h"
struct RemixLiveLights {
 remixapi_LightHandle handles[3]{};LiveLightRow previous[3]{};
 remixapi_LightHandle preparedHandle=nullptr;LiveLightRow preparedRow{};LightShapeRow preparedShape{};
 bool created[3]{};unsigned logs=0;uint64_t applied=0,configRevision=0;
 LightShapeRow previousShapes[3]{};
 LiveLightPacket accepted{};LightShapePacket acceptedShapes{};bool acceptedReady=false;
 uint64_t retainedUpdates=0,unavailableUpdates=0;
 bool update(remixapi_Interface& api,const ship_live::Seed& seed,const ship_live::Key& key,uint64_t frequency,const float* model,const LiveLightPacket* loaded=nullptr,const LightShapePacket* loadedShapes=nullptr,LightValidation policy=LightValidation::TimedOwner){
  LiveLightPacket p{};
  if(loaded)p=*loaded;else{std::ifstream file("live-lights.bin",std::ios::binary);
   if(!file||!file.read(reinterpret_cast<char*>(&p),sizeof(p))||file.peek()!=EOF)return false;}
  const auto now=return_path::now();
  if(!validLightPacket(p,key.sourceSession,key.owner,seed.model,seed.source,key.frame,frequency,now,policy))return false;
  LightShapePacket shapes{};
  if(p.rows[0].values[10]||p.rows[1].values[10]){
   if(loaded){if(!loadedShapes)return false;shapes=*loadedShapes;}
   else{std::ifstream sf("light-shapes.bin",std::ios::binary);
    if(!sf||!sf.read(reinterpret_cast<char*>(&shapes),sizeof(shapes))||sf.peek()!=EOF)return false;}
   if(!validShapes(shapes,p.revision))return false;
  }else for(unsigned i=0;i<3;++i)shapes.rows[i].slot=i;
  LiveLightRow added{};added.slot=2;added.enabled=shapes.rows[2].reserved;
  memcpy(added.values,shapes.rows[2].v+18,12);memcpy(added.values+3,shapes.rows[2].v+15,12);
  added.values[6]=shapes.rows[2].v[21];added.values[7]=shapes.rows[2].v[22];
  unsigned domes=0;
  for(unsigned i=0;i<3;++i)if((i<2?p.rows[i].enabled:added.enabled)&&shapes.rows[i].kind==1)++domes;
  if(domes>1)return false;
  LightShapeRow positioned[3]{};
  // Validate every transformed position before modifying existing API lights.
  for(unsigned i=0;i<3;++i){
   auto shape=shapes.rows[i];
   if(shape.ship&&shape.kind>=2){float pos[3]{};for(unsigned j=0;j<3;++j){pos[j]=model[j*4+3]+key.worldOffset[j];for(unsigned k=0;k<3;++k)pos[j]+=model[j*4+k]*shape.v[8+k];}
    for(float value:pos)if(!std::isfinite(value)||std::abs(value)>1e9f)return false;
    memcpy(shape.v+8,pos,12);}positioned[i]=shape;
  }
  for(unsigned i=0;i<3;++i){const auto& r=i<2?p.rows[i]:added;const auto& shape=positioned[i];
   if(i==2&&preparedHandle){
    if(!handles[i]&&r.enabled&&!memcmp(&r,&preparedRow,sizeof(r))&&!memcmp(&shape,&preparedShape,sizeof(shape))){
     handles[i]=preparedHandle;previous[i]=r;previousShapes[i]=shape;created[i]=true;++applied;
     std::cout<<"PREPARED_DOME_ADOPTED slot=2 recreated=0\n";
    }else check(api.DestroyLight(preparedHandle),"retire changed prepared dome");
    preparedHandle=nullptr;
   }
   if(!created[i]||memcmp(&r,&previous[i],sizeof(r))||memcmp(&shape,&previousShapes[i],sizeof(shape))){
    // Called only after previous output fence completes;no outstanding host draw.
    if(handles[i]){check(api.DestroyLight(handles[i]),"retire native mapped light");handles[i]=nullptr;}
    if(r.enabled){
     handles[i]=createShapedLight(api,r,shape);
    }
    previous[i]=r;previousShapes[i]=shape;created[i]=true;++applied;
    if(logs<100)std::cout<<"LIGHT_TYPE_APPLIED slot="<<i<<" type="<<shape.kind<<" revision="<<p.revision<<"\n";
    if(logs++<100)std::cout<<(i<2?"NATIVE_LIGHT_APPLIED slot=":"PROJECT_LIGHT_APPLIED slot=")<<i<<" enabled="<<r.enabled<<" radiance="<<r.values[3]<<","<<r.values[4]<<","<<r.values[5]<<" revision="<<p.revision<<"\n";
   }
  }
  configRevision=p.revision;return true;
 }
 void draw(remixapi_Interface& api){for(auto h:handles)if(h)check(api.DrawLightInstance(h),"mapped native light draw");}
 void close(remixapi_Interface& api,bool retirePrepared=true){for(auto& h:handles)if(h){check(api.DestroyLight(h),"mapped native light destroy");h=nullptr;}
  if(retirePrepared&&preparedHandle){check(api.DestroyLight(preparedHandle),"prepared dome destroy");preparedHandle=nullptr;}}
 bool updateOrRetain(remixapi_Interface& api,const ship_live::Seed& seed,const ship_live::Key& key,uint64_t frequency,const float* model,const LiveLightPacket* next,const LightShapePacket* shapes,bool persistentScene=false){
  if(next&&update(api,seed,key,frequency,model,next,shapes,persistentScene?LightValidation::SceneUpdate:LightValidation::TimedOwner)){accepted=*next;acceptedShapes=shapes?*shapes:LightShapePacket{};acceptedReady=true;return true;}
  // Scene slots0/1 and project fill belong to the session,not the scheduling
  // ship. Keep them through camera gaps/rebinding;never alter observation time.
  // Owner-local/effect callers retain the existing timed policy by default.
  if(acceptedReady&&update(api,seed,key,frequency,model,&accepted,&acceptedShapes,persistentScene?LightValidation::RetainedScene:LightValidation::TimedOwner)){++retainedUpdates;return true;}
  close(api,false);for(auto& value:created)value=false;configRevision=0;++unavailableUpdates;return false;
 }
};
