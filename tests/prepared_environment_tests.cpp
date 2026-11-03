#define REMIX_ALLOW_X86
#include "../artifacts/remix-runtime/deps/remix_c.h"
#include <windows.h>
#include <iostream>
#include <stdexcept>
#include <cmath>
#include <cstddef>
static void check(remixapi_ErrorCode,const char*){}
#include "../tools/remix_runtime/remix_light_wire.h"
#include "../tools/d3d9_proof/prepared_environment_wire.h"
static unsigned checks=0;
static void test(bool value){++checks;if(!value)throw std::runtime_error("prepared environment check "+std::to_string(checks));}
int main(){try{
 using namespace prepared_environment;
 Packet p{};uint32_t session[]{1,2,3,4};p.magic=Magic;p.version=1;p.bytes=sizeof(p);p.pid=123;p.producer=456;memcpy(p.session,session,16);p.config[0]=1;wcscpy_s(p.cache,L"C:\\EnvironmentCache");
 auto& shapes=p.shapes;shapes.h[0]=0x50414853;shapes.h[1]=2;shapes.h[2]=808;shapes.h[3]=3;shapes.revision=1;
 for(unsigned i=0;i<3;++i){auto& s=shapes.rows[i];s.slot=i;for(unsigned k=0;k<4;++k)s.v[k]=1;s.v[11]=1;}
 shapes.rows[2].v[18]=1;
 auto seal=[](Packet& x){x.shapes.checksum=shapeChecksum(x.shapes);x.checksum=startup_ticket::hash(&x,offsetof(Packet,checksum));};
 seal(p);test(valid(p,session,123,456));test(sizeof(Packet)==1912&&sizeof(Store)==1920);
 test(!valid(p,session,124,456));test(!valid(p,session,123,457));auto other=session[0];session[0]=5;test(!valid(p,session,123,456));session[0]=other;
 auto bad=p;bad.checksum^=1;test(!valid(bad,session,123,456));
 bad=p;bad.shapes.rows[1].v[0]=NAN;seal(bad);test(!valid(bad,session,123,456));
 bad=p;bad.shapes.rows[1].slot=0;seal(bad);test(!valid(bad,session,123,456));
 bad=p;bad.cache[0]=0;seal(bad);test(!valid(bad,session,123,456));
 bad=p;wcscpy_s(bad.cache,L"C:\\cache\\..\\elsewhere");seal(bad);test(!valid(bad,session,123,456));
 bad=p;memset(bad.config,0,32);seal(bad);test(!valid(bad,session,123,456));
 bad=p;bad.flags=1;seal(bad);test(!valid(bad,session,123,456));
 auto& dome=p.shapes.rows[2];dome.kind=1;dome.reserved=1;memset(dome.texture,'a',64);memcpy(dome.texture+64,".dds",4);p.flags=1;seal(p);test(valid(p,session,123,456));
 p.flags=0;seal(p);test(!valid(p,session,123,456));
 std::cout<<"Prepared environment PASS "<<checks<<" checks\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
