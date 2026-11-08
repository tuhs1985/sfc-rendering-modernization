#include "../tools/scene_bridge/break_piece.h"
#include "../tools/scene_bridge/break_registry.h"
#include "../tools/scene_bridge/break_pose.h"
#include <vector>
#include <iostream>
#include <cstdlib>
#include <bit>
using sfc_break::Word;
static unsigned checks=0;
static void check(bool ok,const char* message){
    ++checks;if(!ok){std::cerr<<message<<'\n';std::exit(1);}
}
struct Memory {
    std::vector<unsigned char> bytes=std::vector<unsigned char>(65536);
    void word(Word at,Word value){std::memcpy(bytes.data()+at,&value,4);}
    bool read(Word at,void* out,std::size_t n){
        if(at>bytes.size()||n>bytes.size()-at)return false;
        std::memcpy(out,bytes.data()+at,n);return true;
    }
    Memory(){
        word(0x100,0x7985a4);word(0x260,0x1000);word(0x258,0x5000);
        word(0x1000,0x7983e8);word(0x1008,6);word(0x100c,0x2000);
        word(0x1010,2);word(0x1014,0x3000);word(0x102c,1);
        word(0x1030,0x4000);word(0x1034,2);word(0x4000,1);word(0x4004,2);
        for(Word i=0;i<2;++i){
            Word polygon=0x6000+i*128,corner=0x7000+i*128;
            word(0x3000+i*4,polygon);word(polygon,3);word(polygon+4,i);
            word(polygon+24,corner);
            for(Word c=0;c<3;++c){word(corner+c*28,i*3+c);word(corner+c*28+4,0x3f800000);}
            word(0x5000+i*36,35);word(0x5000+i*36+20,10+i);
        }
    }
};
static sfc_m1::LiveMeshPacket packet;
int main(){
    Memory m;auto read=[&](Word at,void* out,std::size_t n){return m.read(at,out,n);};
    sfc_break::Layout l;sfc_break::Range r;
    check(sfc_break::layout(0x100,l,read),"partition layout");
    check(sfc_break::range(l,0,r)&&r.first==0&&r.count==1&&r.list==0x3000,"first piece");
    check(sfc_break::range(l,1,r)&&r.first==1&&r.count==1&&r.list==0x3004,"second piece");
    check(!sfc_break::range(l,2,r),"reject invalid index");
    auto capture=[&](Word piece){return sfc_break::capture(packet,l,piece,9,0x900,0x8000,read,[]{return true;});};
    check(capture(1)==sfc_m1::MeshStatus::Complete&&packet.complete,"piece packet");
    check(packet.header[sfc_m1::MeshVertices]==6&&packet.header[sfc_m1::MeshPolygons]==1,"shared positions and selected triangles");
    check(packet.polygons[0].header[1]==1&&packet.corners[0][0]==3,"group and corner membership preserved");
    check(packet.sources[0].index==1&&packet.sources[0].words[5]==11,"material assignment preserved");
    check(packet.checksum()==packet.header[sfc_m1::MeshHash],"packet checksum");
    check(sfc_break::capture(packet,l,0,9,0x900,0x8000,read,[]{return false;})==sfc_m1::MeshStatus::Identity,"lifetime qualification");
    m.word(0x7000+128,6);
    check(capture(1)==sfc_m1::MeshStatus::Index&&!packet.complete,"reject out-of-range corner");
    m.word(0x7000+128,3);m.word(0x4004,1);
    check(!sfc_break::layout(0x100,l,read),"reject nonincreasing boundaries");
    m.word(0x4004,3);check(!sfc_break::layout(0x100,l,read),"reject overflow boundary");
    m.word(0x4004,1);m.word(0x1034,1);
    check(!sfc_break::layout(0x100,l,read),"reject incomplete coverage");
    m.word(0x4004,2);m.word(0x1034,2);m.word(0x102c,0);
    check(!sfc_break::layout(0x100,l,read),"unprepared partition is not a mesh");
    sfc_break::Registry registry;
    const auto born=registry.born(100,1,200,0),sibling=registry.born(101,1,200,1);
    check(born&&sibling&&born!=sibling,"independent child epochs");
    check(registry.asset(100,born,200,0,5),"qualified piece asset");
    check(!registry.asset(100,born,200,1,5),"wrong piece rejected");
    std::array<float,16> world{};
    for(unsigned i=0;i<4;++i)world[i*5]=1;
    check(registry.pose(100,born,1,world),"first pose");
    world[3]=4;
    check(registry.pose(100,born,2,world)&&registry.find(100,born)->revision==5,"pose preserves resident geometry");
    check(!registry.pose(100,born,1,world),"old frame rejected");
    world[0]=std::numeric_limits<float>::infinity();
    check(!registry.pose(100,born,3,world)&&registry.find(100,born)->world[3]==4,"invalid pose retains last valid state");
    check(registry.retire(100,born)&&registry.find(101,sibling),"sibling remains live");
    const auto recycled=registry.born(100,2,200,0);
    check(recycled>born&&!registry.find(100,born),"recycled pointer has fresh epoch");
    check(!registry.retire(100,born)&&registry.find(100,recycled),"stale retirement cannot kill new piece");
    check(!registry.asset(100,born,200,0,5),"stale asset rejected");
    constexpr Word body=0x800;
    for(unsigned i=0;i<16;++i)m.word(body+0xa4+i*4,i%5==0?0x3f800000:0);
    m.word(body+0xa4+64,0x100);m.word(body+0x34,0x41200000);
    const auto simulationRead=[&](Word at,void* out,std::size_t n){
        if(at==0x797278&&n==4){const float bias=12582912;std::memcpy(out,&bias,4);return true;}
        for(Word angle: {0u,2048u}){
            if((at==0xc6c004+angle*4||at==0xc6a004+angle*4)&&n==4){
                const float value=at==0xc6c004+angle*4?(angle?0.f:1.f):(angle?1.f:0.f);
                std::memcpy(out,&value,4);return true;
            }
        }
        return read(at,out,n);
    };
    sfc_break::Pose transformed{};
    check(sfc_break::simulation_pose(body,transformed,simulationRead)&&transformed[3]==10,"simulation-only translation");
    m.word(body+0x150,std::bit_cast<Word>(2048.f));
    check(sfc_break::simulation_pose(body,transformed,simulationRead)&&transformed[6]==-1&&transformed[9]==1,"independent simulation rotation");
    m.word(body+0x148,std::bit_cast<Word>(2.f));
    check(sfc_break::simulation_pose(body,transformed,simulationRead)&&transformed[7]==2&&transformed[11]==-2,"rotation about native piece pivot");
    std::cout<<"Break piece PASS "<<checks<<" checks\n";
}
