// Immutable bootstrap metadata in existing scene-map spare space.
#pragma once
#include "startup_ticket.h"
#include "../remix_runtime/remix_light_shapes.h"
namespace fs=std::filesystem;
namespace prepared_environment {
constexpr DWORD Offset=8192,Magic=0x31564e45;
struct Packet {DWORD magic,version,bytes,pid,session[4],producer,flags;BYTE config[32];
 wchar_t cache[512];LightShapePacket shapes;uint64_t checksum;};
struct Store {volatile LONG ready;DWORD reserved;Packet packet;};
static_assert(sizeof(Packet)==1912&&sizeof(Store)==1920&&Offset+sizeof(Store)<32768);
inline bool valid(const Packet& p,const uint32_t* session,DWORD pid,DWORD producer){
 if(p.magic!=Magic||p.version!=1||p.bytes!=sizeof(p)||p.pid!=pid||!pid||p.producer!=producer||!producer||memcmp(p.session,session,16)||p.flags>1||
    p.checksum!=startup_ticket::hash(&p,offsetof(Packet,checksum))||!validShapes(p.shapes,1))return false;
 bool config=false;for(auto b:p.config)config|=b!=0;if(!config)return false;
 unsigned end=0;while(end<512&&p.cache[end])++end;if(!end||end==512)return false;
 for(unsigned i=end;i<512;++i)if(p.cache[i])return false;
 const fs::path path(p.cache);if(!path.is_absolute()||path.has_root_name()==false)return false;
 for(const auto& part:path)if(part==L"..")return false;
 const auto& project=p.shapes.rows[2];return p.flags==DWORD(project.kind==1&&project.reserved==1);
}
}
