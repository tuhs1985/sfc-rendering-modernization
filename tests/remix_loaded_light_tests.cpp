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
 std::cout<<"Loaded light PASS "<<checks<<" checks;no GPU/file input\n";return 0;
}
