// One-shot bootstrap in the existing output channel, before any GPU packet.
#pragma once
#include "output_channel.h"
#include <cstring>
namespace output_startup {
constexpr DWORD Magic=0x3152534f,Version=1,Ticket=1;
constexpr LONG Boot=6,Passive=7,Activate=8;
constexpr uint64_t PassiveLifetime=285000; // enclosing prepared workflow remains authoritative
struct alignas(8) Control {
 DWORD magic=Magic,version=Version,bytes=sizeof(Control),parent=0;
 uint64_t session=0;DWORD flags=0,receiver=0;
 uint64_t readyQpc=0,activatedQpc=0;BYTE asset[32]{};float offset=0;
 DWORD game=0,sourceSession[4]{};uint64_t checksum=0;BYTE padding[16]{};
};
static_assert(sizeof(Control)==128&&offsetof(Control,checksum)==104);
inline void seal(Control& c){c.checksum=output_wire::hash(&c,offsetof(Control,checksum));}
inline bool valid(const Control& c,DWORD parent,uint64_t session){return c.magic==Magic&&c.version==Version&&c.bytes==sizeof(c)&&c.parent==parent&&parent&&c.session==session&&session&&!(c.flags&~Ticket)&&c.checksum==output_wire::hash(&c,offsetof(Control,checksum));}
inline Control read(const output_wire::Channel& c){Control v{};memcpy(&v,&c.packet,sizeof(v));return v;}
inline void write(output_wire::Channel& c,Control& v){seal(v);memcpy(&c.packet,&v,sizeof(v));}
struct Lifetime {
 uint64_t passive=0,active=0;bool activated=false;
 explicit Lifetime(uint64_t now):passive(now+PassiveLifetime){}
 bool activate(uint64_t now,uint64_t duration){if(activated||now>=passive||!duration||now+duration<now)return false;active=now+duration;activated=true;return true;}
 bool expired(uint64_t now)const{return now>=(activated?active:passive);}
};
}
