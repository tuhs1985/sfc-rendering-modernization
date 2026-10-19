#include "../tools/remix_runtime/remix_light_wire.h"
#include <iostream>
#include <limits>
#define REMIX_ALLOW_X86
#include "../artifacts/remix-runtime/deps/include/remix/remix_c.h"
static void check(remixapi_ErrorCode e,const char*){if(e!=REMIXAPI_ERROR_CODE_SUCCESS)throw "SDK shape test";}
#include "../tools/remix_runtime/remix_light_shapes.h"
int main(){
 LiveLightPacket good{};const uint32_t session[4]={1,2,3,4};
 const uint32_t h[12]={0x3154474c,1,200,1,1,2,3,4,2,3,4,100};memcpy(good.h,h,sizeof(h));good.observed=1000;good.revision=1;
 for(unsigned i=0;i<2;++i){auto& r=good.rows[i];r.slot=i;r.enabled=1;r.values[i?2:0]=1;r.values[3]=r.values[4]=r.values[5]=.5f;r.values[6]=.53f;}
 good.checksum=lightChecksum(good);
 unsigned checks=0;auto check=[&](bool ok){++checks;if(!ok)throw "light wire failure";};
 const auto valid=[&](const LiveLightPacket& p,uint64_t now=1100){return validLightPacket(p,session,2,3,4,100,1000,now);};
 check(valid(good));check(valid(good,1500));check(!valid(good,1501));check(!valid(good,999));
 auto bad=good;bad.checksum^=1;check(!valid(bad));
 for(unsigned field:{0u,1u,2u,3u,4u,8u,9u,10u}){bad=good;bad.h[field]=0;bad.checksum=lightChecksum(bad);check(!valid(bad));}
 bad=good;bad.h[11]=101;bad.checksum=lightChecksum(bad);check(!valid(bad));
 bad=good;bad.h[11]=69;bad.checksum=lightChecksum(bad);check(!valid(bad));
 bad=good;bad.rows[0].values[0]=0;bad.checksum=lightChecksum(bad);check(!valid(bad));
 bad=good;bad.rows[0].values[3]=std::numeric_limits<float>::quiet_NaN();bad.checksum=lightChecksum(bad);check(!valid(bad));
 bad=good;bad.rows[1].enabled=2;bad.checksum=lightChecksum(bad);check(!valid(bad));
 bad=good;bad.rows[1].values[3]=-1;bad.checksum=lightChecksum(bad);check(!valid(bad));
 LightShapePacket shapes{};shapes.h[0]=0x50414853;shapes.h[1]=2;shapes.h[2]=sizeof(shapes);shapes.h[3]=3;shapes.revision=1;
 for(unsigned i=0;i<3;++i){auto& r=shapes.rows[i];r.slot=i;for(unsigned j=0;j<4;++j)r.v[j]=1;r.v[12]=1;}
 shapes.rows[2].v[19]=-1;
 shapes.checksum=shapeChecksum(shapes);check(validShapes(shapes,1));check(!validShapes(shapes,2));
 auto altered=shapes;altered.rows[1].kind=7;altered.checksum=shapeChecksum(altered);check(!validShapes(altered,1));
 altered=shapes;altered.rows[1].kind=1;altered.checksum=shapeChecksum(altered);check(!validShapes(altered,1));
 altered=shapes;altered.rows[1].v[12]=0;altered.checksum=shapeChecksum(altered);check(!validShapes(altered,1));
 remixapi_Float3D x{},y{};lightBasis({0,1,0},37,x,y);check(std::abs(x.x*y.x+x.y*y.y+x.z*y.z)<1e-5f);
 std::cout<<"REMIX_LIGHT_WIRE_PASS checks="<<checks<<" bytes="<<sizeof(good)<<"\n";
}
