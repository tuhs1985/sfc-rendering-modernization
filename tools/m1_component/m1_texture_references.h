#pragma once
#include "m1_mesh_export.h"

namespace sfc_m1 {
struct TextureReference {
    std::uint32_t id=0,object=0,entry=0,surface=0;
    std::array<char,256> filename{};
    std::array<char,256> requested{};
};
template<std::size_t Resources=10> struct BasicTextureReferences {
    std::uint32_t status=0,count=0,registry=0,packet_hash=0;
    std::uint32_t secondary_path_word=0,fallback_validation_mask=0;
    std::uint8_t textures_enabled=0,multitexture_flag=0,previous_alpha_test_flag=0;
    std::array<char,256> model_filename{};
    std::array<TextureReference,Resources> resources{};
};
using TextureReferences=BasicTextureReferences<>;
using LiveTextureReferences=BasicTextureReferences<256>;
static_assert(sizeof(TextureReferences)<8192,"Bounded reference storage");

// Called once in the accepted mesh epoch. No allocation, I/O, COM or native calls.
// Status: 1 complete, 2 unreadable/invalid, 3 resource limit, 4 changed.
template<class References,class Packet,class Read,class Validate>
void capture_texture_references(References& out,const Packet& mesh,Read read,Validate valid) {
    out={};out.status=2;out.packet_hash=mesh.header[MeshHash];
    const auto block=[&](std::uint32_t base,std::uint32_t offset,void* dst,std::uint32_t n){
        std::uint32_t address=0,end=0;
        return base && n && tint_address(base,offset,address) && tint_address(address,n-1,end) && read(address,dst,n);
    };
    const auto word=[&](std::uint32_t base,std::uint32_t offset,std::uint32_t& dst){return block(base,offset,&dst,4);};
    const auto text=[&](std::uint32_t base,std::uint32_t offset,std::array<char,256>& dst){
        for(std::uint32_t i=0;i<256;++i){
            if(offset>0xffffffffu-i || !block(base,offset+i,&dst[i],1))return false;
            const auto c=static_cast<unsigned char>(dst[i]);
            if(!c)return i>0;
            if(c<32 || c>126){dst[i]=0;return false;}
        }dst.back()=0;return false;
    };
    std::uint32_t vt=0,strings=0,linked=0;
    if(!mesh.complete || !mesh.bounds() || !valid() ||
       !word(0x008CC620,0,out.registry) || !word(out.registry,0,vt) || vt!=0x00795C54 ||
       !word(mesh.header[MeshVisual],0x154,strings) || !strings ||
       !word(mesh.header[MeshVisual],0x158,linked) || linked!=mesh.header[MeshSource] ||
       !block(mesh.header[MeshManager],0x1ed0,&out.textures_enabled,1) ||
       !block(mesh.header[MeshManager],0x8009,&out.multitexture_flag,1) ||
       !word(mesh.header[MeshManager],0x3d58,out.secondary_path_word) ||
       !word(mesh.header[MeshManager],0x800c,out.fallback_validation_mask) ||
       !block(mesh.header[MeshManager],0x3f54,&out.previous_alpha_test_flag,1) ||
       !text(mesh.header[MeshVisual],0x14,out.model_filename))return;
    for(std::uint32_t s=0;s<mesh.header[MeshSources];++s){
        const auto& source=mesh.sources[s];
        for(std::uint32_t role=0;role<2;++role){
            if(role && !(source.words[0]&0x20))continue;
            const auto id=source.words[role?7:5];
            if(!id)continue; // retained as unresolved/off, not declared untextured
            if(id>4096)return;
            std::array<char,256> requested{};
            if(source.words[role?8:6]>65535 || !text(strings,source.words[role?8:6],requested))return;
            bool found=false;
            for(std::uint32_t r=0;r<out.count;++r)found|=out.resources[r].id==id;
            if(found)continue;
            if(out.count==out.resources.size()){out.status=3;return;}
            auto& r=out.resources[out.count];r.id=id;r.requested=requested;
            if(!word(out.registry,12+(id-1)*20,r.object) || !r.object ||
               !text(r.object,8,r.filename) ||
               !word(mesh.header[MeshManager],0x3f60+(id-1)*4,r.entry) || !r.entry ||
               !word(r.entry,4,r.surface) || !r.surface)return;
            ++out.count;
        }
    }
    for(std::uint32_t s=0;s<mesh.header[MeshSources];++s){
        const auto& source=mesh.sources[s];std::array<std::uint32_t,9> current{};
        if(!block(mesh.header[MeshSource],source.index*36,current.data(),36) || current!=source.words){out.status=4;return;}
    }
    for(std::uint32_t i=0;i<out.count;++i){
        const auto& r=out.resources[i];std::uint32_t object=0,entry=0,surface=0;std::array<char,256> name{};
        if(!word(out.registry,12+(r.id-1)*20,object) || object!=r.object ||
           !word(mesh.header[MeshManager],0x3f60+(r.id-1)*4,entry) || entry!=r.entry ||
           !word(entry,4,surface) || surface!=r.surface || !text(object,8,name) || name!=r.filename){out.status=4;return;}
    }
    for(std::uint32_t s=0;s<mesh.header[MeshSources];++s){
        const auto& source=mesh.sources[s];
        for(std::uint32_t role=0;role<2;++role){
            if(role && !(source.words[0]&0x20))continue;
            const auto id=source.words[role?7:5];if(!id)continue;
            std::array<char,256> requested{};
            if(!text(strings,source.words[role?8:6],requested)){out.status=4;return;}
            for(std::uint32_t r=0;r<out.count;++r)
                if(out.resources[r].id==id && out.resources[r].requested!=requested){out.status=4;return;}
        }
    }
    std::uint32_t registry=0,table=0,path_word=0,validation_mask=0;
    std::uint8_t enabled=0,multitexture=0,previous_alpha_test=0;
    std::array<char,256> model_name{};
    if(!word(0x008CC620,0,registry) || registry!=out.registry ||
       !word(mesh.header[MeshVisual],0x154,table) || table!=strings ||
       !block(mesh.header[MeshManager],0x1ed0,&enabled,1) || enabled!=out.textures_enabled ||
       !block(mesh.header[MeshManager],0x8009,&multitexture,1) || multitexture!=out.multitexture_flag ||
       !word(mesh.header[MeshManager],0x3d58,path_word) || path_word!=out.secondary_path_word ||
       !word(mesh.header[MeshManager],0x800c,validation_mask) || validation_mask!=out.fallback_validation_mask ||
       !block(mesh.header[MeshManager],0x3f54,&previous_alpha_test,1) || previous_alpha_test!=out.previous_alpha_test_flag ||
       !text(mesh.header[MeshVisual],0x14,model_name) || model_name!=out.model_filename || !valid()){out.status=4;return;}
    out.status=1;
}
inline void texture_json_string(std::ostream& out,const char* text){
    out<<'"';for(;*text;++text){if(*text=='"' || *text=='\\')out<<'\\';out<<*text;}out<<'"';
}
template<class References,class Packet>
bool write_texture_references(std::ostream& out,const References& refs,const Packet& mesh,bool restored){
    out<<"{\"schema\":\"sfc.texture.references.v1\",\"status\":"<<refs.status
       <<",\"hooks_restored\":"<<(restored?"true":"false")<<",\"packet_fnv1a\":"<<refs.packet_hash
       <<",\"owner_epoch\":"<<mesh.header[MeshOwner]<<",\"frame\":"<<mesh.header[MeshFrame]
       <<",\"model\":"<<mesh.header[MeshModel]<<",\"source\":"<<mesh.header[MeshSource]
       <<",\"textures_enabled\":"<<static_cast<unsigned>(refs.textures_enabled)
       <<",\"manager_multitexture_flag\":"<<static_cast<unsigned>(refs.multitexture_flag)
       <<",\"manager_secondary_path_word\":"<<refs.secondary_path_word
       <<",\"manager_fallback_validation_mask\":"<<refs.fallback_validation_mask
       <<",\"manager_previous_alpha_test_flag\":"<<static_cast<unsigned>(refs.previous_alpha_test_flag)
       <<",\"model_filename\":";texture_json_string(out,refs.model_filename.data());
    out<<",\"resources\":[";
    for(std::uint32_t i=0;i<refs.count;++i){const auto& r=refs.resources[i];if(i)out<<',';
        out<<"{\"id\":"<<r.id<<",\"registry_object\":"<<r.object<<",\"manager_entry\":"<<r.entry
           <<",\"surface_identity\":"<<r.surface<<",\"filename\":";texture_json_string(out,r.filename.data());
        out<<",\"requested\":";texture_json_string(out,r.requested.data());out<<'}';}
    out<<"],\"groups\":[";
    for(std::uint32_t i=0;i<mesh.header[MeshSources] && i<MeshPacket::kSources;++i){const auto& s=mesh.sources[i];if(i)out<<',';
        out<<"{\"group\":"<<s.index<<",\"flags\":"<<s.words[0]<<",\"primary\":"<<s.words[5]
           <<",\"secondary\":"<<s.words[7]<<",\"primary_name_offset\":"<<s.words[6]
           <<",\"secondary_name_offset\":"<<s.words[8]<<'}';}
    out<<"],\"secondary_role\":\"UNPROVEN_NOT_APPLIED_AS_EMISSION\"}\n";return out.good();
}
}
