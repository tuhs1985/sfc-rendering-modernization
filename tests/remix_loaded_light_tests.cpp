// No GPU/game/file input:preloaded cache still uses exact old light validation.
#define REMIX_ALLOW_X86
#include "../artifacts/remix-runtime/deps/remix_c.h"
#include <windows.h>
#include <fstream>
#include <iostream>
#include <stdexcept>
static void check(remixapi_ErrorCode e,const char*){if(e!=REMIXAPI_ERROR_CODE_SUCCESS)throw std::runtime_error("mock API failure");}
namespace return_path{static uint64_t clock=1100;inline uint64_t now(){return clock;}}
namespace ship_live{
struct Seed{uint32_t model=3,source=4;};
struct Key{uint32_t sourceSession[4]{1,2,3,4},owner=2,frame=100;float worldOffset[3]{};};
}
#include "../tools/remix_runtime/remix_live_lights.h"
static unsigned creates=0,destroys=0;
static remixapi_ErrorCode REMIXAPI_CALL create(const remixapi_LightInfo*,remixapi_LightHandle* out){*out=reinterpret_cast<remixapi_LightHandle>(uintptr_t(++creates));return REMIXAPI_ERROR_CODE_SUCCESS;}
static remixapi_ErrorCode REMIXAPI_CALL destroy(remixapi_LightHandle){++destroys;return REMIXAPI_ERROR_CODE_SUCCESS;}
int main(){
 unsigned checks=0;auto test=[&](bool ok){++checks;if(!ok)throw std::runtime_error("loaded light regression");};
 remixapi_Interface api{};api.CreateLight=create;api.DestroyLight=destroy;
 ship_live::Seed seed;ship_live::Key key;float model[16]{1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1};
 LiveLightPacket good{};uint32_t h[12]{0x3154474c,1,200,1,1,2,3,4,2,3,4,100};memcpy(good.h,h,sizeof(h));good.observed=1000;good.revision=1;
 for(unsigned i=0;i<2;++i){auto& r=good.rows[i];r.slot=i;r.enabled=1;r.values[0]=1;r.values[3]=r.values[4]=r.values[5]=.5f;r.values[6]=.53f;}
 good.checksum=lightChecksum(good);RemixLiveLights lights;
 test(lights.update(api,seed,key,1000,model,&good));test(creates==2);
 test(lights.update(api,seed,key,1000,model,&good));test(creates==2&&destroys==0);
 auto bad=good;bad.checksum^=1;test(!lights.update(api,seed,key,1000,model,&bad));
 bad=good;bad.h[11]=101;bad.checksum=lightChecksum(bad);test(!lights.update(api,seed,key,1000,model,&bad));
 bad=good;bad.h[4]=9;bad.checksum=lightChecksum(bad);test(!lights.update(api,seed,key,1000,model,&bad));
 return_path::clock=1501;test(!lights.update(api,seed,key,1000,model,&good));return_path::clock=1100;
 bad=good;bad.rows[0].values[10]=1;bad.checksum=lightChecksum(bad);test(!lights.update(api,seed,key,1000,model,&bad));
 test(creates==2&&destroys==0);lights.close(api);test(destroys==2);
 // Current lights survive a transient missing/newer packet without accepting
 // it as current. Expired/wrong-owner lights are removed;fresh data recovers.
 RemixLiveLights retained;
 test(retained.updateOrRetain(api,seed,key,1000,model,&good,nullptr));
 const auto stableCreates=creates;
 test(retained.updateOrRetain(api,seed,key,1000,model,nullptr,nullptr));test(creates==stableCreates&&retained.retainedUpdates==1);
 bad=good;bad.h[11]=101;bad.checksum=lightChecksum(bad);
 test(retained.updateOrRetain(api,seed,key,1000,model,&bad,nullptr));test(creates==stableCreates);
 return_path::clock=1501;test(!retained.updateOrRetain(api,seed,key,1000,model,nullptr,nullptr));test(!retained.handles[0]&&!retained.handles[1]);
 return_path::clock=1100;test(retained.updateOrRetain(api,seed,key,1000,model,&good,nullptr));
 ++key.owner;test(!retained.updateOrRetain(api,seed,key,1000,model,nullptr,nullptr));test(!retained.handles[0]&&!retained.handles[1]);--key.owner;
 test(retained.updateOrRetain(api,seed,key,1000,model,&good,nullptr));retained.close(api);
 // Scene0/1 plus configured project fill persist through long camera gaps
 // and scheduling-owner changes. Config OFF and a new session still apply.
 RemixLiveLights scene;ship_live::Seed sceneSeed;ship_live::Key sceneKey;
 auto scenePacket=good;for(auto& row:scenePacket.rows)row.values[10]=1;scenePacket.checksum=lightChecksum(scenePacket);
 LightShapePacket shapes{};shapes.h[0]=0x50414853;shapes.h[1]=2;shapes.h[2]=sizeof(shapes);shapes.h[3]=3;shapes.revision=1;
 for(unsigned i=0;i<3;++i){auto& row=shapes.rows[i];row.slot=i;for(unsigned k=0;k<4;++k)row.v[k]=1;row.v[11]=1;}
 shapes.rows[2].reserved=1;shapes.rows[2].v[15]=shapes.rows[2].v[16]=shapes.rows[2].v[17]=.2f;shapes.rows[2].v[18]=1;shapes.rows[2].v[21]=.53f;shapes.checksum=shapeChecksum(shapes);
 test(scene.updateOrRetain(api,sceneSeed,sceneKey,1000,model,&scenePacket,&shapes,true));test(scene.handles[0]&&scene.handles[1]&&scene.handles[2]);
 return_path::clock=100000;sceneKey.frame=9000;
 test(scene.updateOrRetain(api,sceneSeed,sceneKey,1000,model,nullptr,nullptr,true));test(scene.handles[0]&&scene.handles[1]&&scene.handles[2]);
 ++sceneKey.owner;++sceneSeed.model;
 test(scene.updateOrRetain(api,sceneSeed,sceneKey,1000,model,nullptr,nullptr,true));
 scenePacket.h[8]=sceneKey.owner;scenePacket.h[9]=sceneSeed.model;scenePacket.rows[0].enabled=0;scenePacket.checksum=lightChecksum(scenePacket);
 test(scene.updateOrRetain(api,sceneSeed,sceneKey,1000,model,&scenePacket,&shapes,true));test(!scene.handles[0]&&scene.handles[1]&&scene.handles[2]);
 ++sceneKey.sourceSession[0];test(!scene.updateOrRetain(api,sceneSeed,sceneKey,1000,model,nullptr,nullptr,true));test(!scene.handles[0]&&!scene.handles[1]&&!scene.handles[2]);
 // Preparation is not a live observation. Keep pending resource through a
 // missing first packet;adopt only when actual validated values agree.
 RemixLiveLights prepared;prepared.preparedHandle=reinterpret_cast<remixapi_LightHandle>(uintptr_t(900));
 prepared.preparedShape=shapes.rows[2];prepared.preparedRow.slot=2;prepared.preparedRow.enabled=1;
 memcpy(prepared.preparedRow.values,shapes.rows[2].v+18,12);memcpy(prepared.preparedRow.values+3,shapes.rows[2].v+15,12);
 prepared.preparedRow.values[6]=shapes.rows[2].v[21];prepared.preparedRow.values[7]=shapes.rows[2].v[22];
 auto beforeDestroy=destroys;
 test(!prepared.updateOrRetain(api,seed,key,1000,model,nullptr,nullptr,true));test(prepared.preparedHandle&&destroys==beforeDestroy);
 scenePacket=good;for(auto& r:scenePacket.rows)r.values[10]=1;scenePacket.checksum=lightChecksum(scenePacket);
 auto beforeCreate=creates;
 test(prepared.updateOrRetain(api,seed,key,1000,model,&scenePacket,&shapes,true));
 test(!prepared.preparedHandle&&prepared.handles[2]==reinterpret_cast<remixapi_LightHandle>(uintptr_t(900))&&creates==beforeCreate+2);
 prepared.close(api);test(destroys==beforeDestroy+3);
 RemixLiveLights cancelled;cancelled.preparedHandle=reinterpret_cast<remixapi_LightHandle>(uintptr_t(901));beforeDestroy=destroys;
 cancelled.close(api);cancelled.close(api);test(destroys==beforeDestroy+1);
 RemixLiveLights changed;changed.preparedHandle=reinterpret_cast<remixapi_LightHandle>(uintptr_t(902));beforeDestroy=destroys;
 test(changed.updateOrRetain(api,seed,key,1000,model,&scenePacket,&shapes,true));test(!changed.preparedHandle&&destroys==beforeDestroy+1);changed.close(api);
 std::cout<<"Loaded light PASS "<<checks<<" checks;no GPU/file input\n";return 0;
}
