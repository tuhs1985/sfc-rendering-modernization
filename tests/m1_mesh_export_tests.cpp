#include "../tools/m1_component/m1_mesh_export.h"
#include "../tools/m1_component/m1_texture_references.h"
#include <vector>
#include <iostream>
#include <fstream>
#include <sstream>
#include <cstdlib>

using namespace sfc_m1;
void check_mesh(bool ok,const char* what){if(!ok){std::cerr<<what<<'\n';std::exit(1);}}
MeshPacket packet;
struct Memory {
    std::vector<unsigned char> data=std::vector<unsigned char>(2*1024*1024);
    MeshIdentity id;
    bool changed=false,unreadable=false;unsigned position_reads=0;
    void word(std::uint32_t address,std::uint32_t v){std::memcpy(data.data()+address,&v,4);}
    Memory() {
        id={1,2,3,0,0x1000,0x2000,0x3000,0x4000,0x8000,0x0042E55D,0x10000,2};
        word(0x1088,0x2000);word(0x211c,1);word(0x2120,0xffffffff);word(0x2124,99);
        word(0x2158,0x8000);word(0x2160,0x3000);
        word(0x3000,0x007983E8);word(0x3008,3);word(0x300c,0x40000);word(0x3010,2);word(0x3014,0x10000);
        word(0x4000,0x007B8D4C);word(0x4554,0x40000);word(0x4558,0x8000);
        word(0x40000+12,0x3f800000);word(0x40000+28,0x3f800000);
        for(std::uint32_t p=0;p<2;++p){
            word(0x10000+p*4,0x11000+p*28);
            word(0x11000+p*28,3);word(0x11004+p*28,p?255:0);
            word(0x11010+p*28,0x3f800000); // face Z
            word(0x11018+p*28,0x15000+p*84);
            for(std::uint32_t c=0;c<3;++c){
                const auto a=0x15000+p*84+c*28;
                word(a,c);word(a+12,p?0xbf800000:0x3f800000);
                word(a+16,p?0x40000000:0); // same position, different UV/vector
            }
        }
    }
    bool read(std::uint32_t a,void* dst,std::uint32_t n) {
        if(a==0x00C69FF0 || a==0x00C69FF4 || a==0x00C74058){std::memset(dst,0,n);return true;}
        if(unreadable && a==0x15000)return false;
        if(a>data.size() || n>data.size()-a)return false;
        std::memcpy(dst,data.data()+a,n);
        if(a==0x40000 && changed && ++position_reads>1)static_cast<unsigned char*>(dst)[0]^=1;
        return true;
    }
    MeshStatus capture(){return capture_mesh(packet,id,[&](auto a,auto* d,auto n){return read(a,d,n);},[]{return true;});}
};
int main(int argc,char** argv) {
    {
        Memory x;x.word(0x2154,0x50000);x.word(0x8000,0x23);
        x.word(0x8014,1);x.word(0x8018,0);x.word(0x801c,2);x.word(0x8020,8);
        std::memcpy(x.data.data()+0x2014,"Assets/Models/test/test.mod",27);
        std::memcpy(x.data.data()+0x50000,"test_a\0\0test_ai",15);
        x.word(0x60000,0x00795C54);x.word(0x6000c,0x70000);x.word(0x60020,0x71000);
        std::memcpy(x.data.data()+0x70008,"Assets/Models/test/test_a.bmp",29);
        std::memcpy(x.data.data()+0x71008,"Assets/Models/test/test_ai.bmp",30);
        x.word(0x7f60,0x72000);x.word(0x7f64,0x73000);x.word(0x72004,123);x.word(0x73004,456);
        check_mesh(x.capture()==MeshStatus::Complete,"texture fixture mesh");
        const auto before_texture=x.data;
        TextureReferences refs;
        const auto read=[&](auto a,auto* dst,auto n){
            if(a==0x008CC620 && n==4){std::uint32_t registry=0x60000;std::memcpy(dst,&registry,4);return true;}
            return x.read(a,dst,n);
        };
        capture_texture_references(refs,packet,read,[]{return true;});
        check_mesh(refs.status==1 && refs.count==2 && refs.resources[1].id==2,"two registry filenames resolved");
        check_mesh(x.data==before_texture,"reference collector does not mutate native bytes");
        std::ostringstream json;check_mesh(write_texture_references(json,refs,packet,true) && json.str().size()<65536,"bounded JSON");
        check_mesh(refs.multitexture_flag==0 && json.str().find("\"manager_multitexture_flag\":0")!=std::string::npos,
                   "zero multitexture flag is retained, not assumed enabled");
        x.data[0xc009]=1;
        capture_texture_references(refs,packet,read,[]{return true;});
        check_mesh(refs.status==1 && refs.multitexture_flag==1,"live multitexture flag captured");
        unsigned flag_reads=0;
        capture_texture_references(refs,packet,[&](auto a,auto* dst,auto n){
            if(!read(a,dst,n))return false;
            if(a==0xc009 && ++flag_reads==2)*static_cast<unsigned char*>(dst)=0;
            return true;
        },[]{return true;});
        check_mesh(refs.status==4,"changed multitexture flag rejects association");
        capture_texture_references(refs,packet,[&](auto a,auto* dst,auto n){
            return a!=0xc009 && read(a,dst,n);
        },[]{return true;});
        check_mesh(refs.status==2,"unreadable multitexture flag is not guessed");
        x.word(0x7d58,0x12345678);
        capture_texture_references(refs,packet,read,[]{return true;});
        check_mesh(refs.status==1 && refs.secondary_path_word==0x12345678,"second branch predicate captured independently");
        unsigned path_reads=0;
        capture_texture_references(refs,packet,[&](auto a,auto* dst,auto n){
            if(!read(a,dst,n))return false;
            if(a==0x7d58 && ++path_reads==2)*static_cast<unsigned char*>(dst)^=1;
            return true;
        },[]{return true;});
        check_mesh(refs.status==4,"changed second branch predicate rejects association");
        x.word(0x7d58,0);
        x.word(0xc00c,3);x.data[0x7f54]=1;
        capture_texture_references(refs,packet,read,[]{return true;});
        check_mesh(refs.status==1 && refs.fallback_validation_mask==3 && refs.previous_alpha_test_flag==1,
                   "both fallback eligibility inputs captured");
        unsigned eligibility_reads=0;
        capture_texture_references(refs,packet,[&](auto a,auto* dst,auto n){
            if(!read(a,dst,n))return false;
            if(a==0xc00c && ++eligibility_reads==2)*static_cast<unsigned char*>(dst)^=1;
            return true;
        },[]{return true;});
        check_mesh(refs.status==4,"changed fallback mask rejects association");
        unsigned blend_reads=0;
        capture_texture_references(refs,packet,[&](auto a,auto* dst,auto n){
            if(!read(a,dst,n))return false;
            if(a==0x7f54 && ++blend_reads==2)*static_cast<unsigned char*>(dst)=0;
            return true;
        },[]{return true;});
        check_mesh(refs.status==4,"changed previous alpha-test state rejects association");
        x.data[0xc009]=0;
        capture_texture_references(refs,packet,read,[]{return false;});check_mesh(refs.status==2,"retired identity rejected");
        x.word(0x72004,0);capture_texture_references(refs,packet,read,[]{return true;});check_mesh(refs.status==2,"unbound resource rejected");
        x.word(0x72004,123);x.word(0x8000,0);capture_texture_references(refs,packet,read,[]{return true;});check_mesh(refs.status==4,"changed source rejected");
        x.word(0x8000,0x23);
        unsigned validations=0;
        capture_texture_references(refs,packet,read,[&]{return ++validations==1;});
        check_mesh(refs.status==4,"retirement during association rejected");
        for(std::uint32_t i=0;i<12;++i){
            x.word(0x6000c+i*20,0x70000);x.word(0x7f60+i*4,0x72000);
        }
        packet.header[MeshSources]=6;
        for(std::uint32_t i=0;i<6;++i){
            packet.sources[i].index=i;packet.sources[i].words={0x23,0,0,0,0,i*2+1,0,i*2+2,0};
        }
        capture_texture_references(refs,packet,read,[]{return true;});
        check_mesh(refs.status==3 && refs.count==10,"eleventh unique resource stops within fixed ten-entry storage");
        std::memset(x.data.data()+0x2014,'A',256);
        capture_texture_references(refs,packet,read,[]{return true;});
        check_mesh(refs.status==2 && refs.model_filename.back()==0,"unterminated string bounded and safe to serialize");
    }
    Memory m;const auto before=m.data;
    check_mesh(m.capture()==MeshStatus::Complete,"complete capture");
    check_mesh(m.data==before,"native bytes not modified");
    check_mesh(packet.header[MeshCorners]==6 && packet.header[MeshSources]==2,"all corners and sparse sources");
    check_mesh(packet.polygons[1].header[6]==3 && packet.corners[3][4]==0x40000000,"portable corner ordinal and UV seam retained");
    check_mesh(packet.header[MeshActualChild]==0,"single LOD does not trust stale cached selection");
    std::ostringstream stream(std::ios::binary);check_mesh(packet.write(stream),"serializer");
    check_mesh(stream.str().size()==packet.byte_size(),"exact byte size");
    if(argc>1){std::ofstream file(argv[1],std::ios::binary);check_mesh(packet.write(file),"fixture output");}
    packet.corners[0][4]^=1;check_mesh(!packet.write(stream),"corrupt packet rejected");
    {Memory x;x.id.owner=0;check_mesh(x.capture()==MeshStatus::Identity,"missing identity");}
    {Memory x;x.word(0x2160,0x3333);check_mesh(x.capture()==MeshStatus::Identity,"wrong selected child");}
    {Memory x;x.word(0x211c,2);x.word(0x2120,1);x.word(0x2164,0x3000);
     check_mesh(x.capture()==MeshStatus::Complete && packet.header[MeshActualChild]==1,"LOD override used instead of cached selection");}
    {Memory x;x.word(0x15000,3);check_mesh(x.capture()==MeshStatus::Index,"index bound");}
    {Memory x;x.word(0x15010,0x7fc00000);check_mesh(x.capture()==MeshStatus::Nonfinite,"nonfinite UV");}
    {Memory x;x.word(0x40000,0x7f800000);check_mesh(x.capture()==MeshStatus::Nonfinite,"nonfinite referenced position");}
    {Memory x;x.word(0x11000,9);check_mesh(x.capture()==MeshStatus::Count,"no corner truncation");}
    {Memory x;x.word(0x3008,65537);check_mesh(x.capture()==MeshStatus::Count,"position ceiling");}
    {Memory x;x.word(0x300c,0xfffffff0);x.word(0x4554,0xfffffff0);check_mesh(x.capture()==MeshStatus::Read,"overflow guarded");}
    {Memory x;x.unreadable=true;check_mesh(x.capture()==MeshStatus::Read,"read fault");}
    {Memory x;x.changed=true;check_mesh(x.capture()==MeshStatus::Changed,"second-pass mutation");}
    {Memory x;unsigned calls=0;check_mesh(capture_mesh(packet,x.id,[&](auto a,auto* d,auto n){return x.read(a,d,n);},[&]{return ++calls==1;})==MeshStatus::Changed,"identity retirement during copy");}
    {Memory x;x.word(0x3008,65536);x.word(0x15000,65535);check_mesh(x.capture()==MeshStatus::Complete,"WORD boundary index");}
    {Memory x;x.id.count=512;x.word(0x3010,512);x.word(0x3008,65536);
     x.word(0x11000,8);for(unsigned c=0;c<8;++c)x.word(0x15000+c*28,c);
     for(unsigned i=0;i<512;++i)x.word(0x10000+i*4,0x11000);
     check_mesh(x.capture()==MeshStatus::Complete && packet.byte_size()<1024*1024 && packet.header[MeshCorners]==4096,"maximum positions/polygons/corners bounded");
     std::ostringstream maximum(std::ios::binary);
     check_mesh(packet.write(maximum) && maximum.str().size()==packet.byte_size(),"maximum packet serializes within bound");
     std::ostringstream bad;bad.setstate(std::ios::badbit);check_mesh(!packet.write(bad),"output failure bounded and reported");
     std::cout<<"Maximum synthetic packet bytes="<<packet.byte_size()<<", storage bytes="<<sizeof(packet)<<'\n';}
    {MeshCaptureBudget b;check_mesh(b.admit(m.id),"first attempt");b.status=MeshStatus::Changed;
     check_mesh(!b.admit(m.id),"no same-frame retry");auto next=m.id;++next.frame;
     auto wrong=next;++wrong.owner;check_mesh(!b.admit(wrong),"no epoch retarget");
     check_mesh(b.admit(next),"second frame retry");++next.frame;check_mesh(!b.admit(next),"two attempts maximum");
     MeshCaptureBudget r;r.retired=true;check_mesh(!r.admit(m.id),"retired no retry");
     MeshCaptureBudget t;auto late=m.id;late.elapsed=90001;check_mesh(!t.admit(late),"time bound");}
    std::cout<<"Mesh collector/serializer bounds, identity and nonmutation checks passed.\n";
    return 0;
}
