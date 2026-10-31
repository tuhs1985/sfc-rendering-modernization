#include "cohort_contract.h"
#include <iostream>
#include <memory>
using namespace native_cohort;
unsigned checks=0;
void test(bool b){++checks;if(!b){std::cerr<<"Cohort check "<<checks<<" failed\n";std::exit(1);}}
int main(){
 DWORD session[]{1,2,3,4};auto s=std::make_unique<Store>();initialize(*s,session,GetCurrentProcessId());test(valid(s->header,session,GetCurrentProcessId()));
 multi_scene::Frame f{};f.frame=8;f.anchor=1;f.revision=2;f.sequence=10;f.offered=20;f.count=3;
 auto catalog=std::make_unique<multi_scene::Store>();memcpy(catalog->header.session,session,16);
 Manifest m{};memcpy(m.session,session,16);m.frame=f.frame;m.anchor=f.anchor;m.revision=f.revision;m.count=3;m.sequence=f.sequence;m.output=100;
 for(unsigned i=0;i<3;++i){auto& r=f.rows[i];r[1]=i+1;r[2]=8;r[4]=1;r[7]=2;r[5]=20+i;r[6]=30+i;r[48]=1;
  auto& member=m.members[i];member.owner=r[1];member.revision=r[7];member.model=r[5];member.source=r[6];member.asset=i+1;member.content[0]=BYTE(i==2?1:i+1);
  multi_scene::Asset a{};a.id=i+1;a.path_id=i+1;a.owner=r[1];a.revision=r[7];a.model=r[5];a.source=r[6];a.geometry_bytes=64;a.image_bytes=64;a.replay_hash=1;a.textures_hash=2;memcpy(a.content,member.content,32);a.checksum=multi_scene::checksum(a);
  auto& slot=catalog->assets[i];slot.packet=a;slot.guard=2;
 }
 f.checksum=multi_scene::checksum(f);m.hash=f.checksum;m.checksum=checksum(m);
 test(valid(m,session));test(qualifies(m,*catalog,f));write(s->upstream,m);Manifest out{};test(read(s->upstream,out)&&out.checksum==m.checksum);
 native_gate::Ticket t{};t.frame=8;t.sequence=10;t.hash=m.hash;t.owner=2;t.revision=2;t.model=21;t.source=31;
 test(contains(m,t));++t.revision;test(!contains(m,t));--t.revision;++t.owner;test(!contains(m,t));
 auto malformed=m;malformed.members[2].owner=malformed.members[1].owner;malformed.checksum=checksum(malformed);test(!valid(malformed,session));
 malformed=m;malformed.count=33;malformed.checksum=checksum(malformed);test(!valid(malformed,session));
 malformed=m;++malformed.output;test(!valid(malformed,session));
 malformed=m;++malformed.members[1].source;malformed.checksum=checksum(malformed);test(!qualifies(malformed,*catalog,f));
 malformed=m;malformed.members[1].content[0]^=1;malformed.checksum=checksum(malformed);test(!qualifies(malformed,*catalog,f));
 auto changed=f;changed.rows[1][7]++;changed.checksum=multi_scene::checksum(changed);test(!qualifies(m,*catalog,changed));
 changed=f;changed.count=1;changed.checksum=multi_scene::checksum(changed);m.hash=changed.checksum;m.checksum=checksum(m);test(!qualifies(m,*catalog,changed));
 InterlockedIncrement(&s->upstream.guard);test(!read(s->upstream,out));InterlockedIncrement(&s->upstream.guard);
 t.owner=1;t.revision=2;t.model=20;t.source=30;count(*s,t,true,false);count(*s,t,false,true);test(s->header.inserted==1&&s->header.suppressed==1&&s->owners[0].owner==1);
 ++t.revision;count(*s,t,true,false);test(s->owners[1].owner==1&&s->owners[1].revision==3&&s->owners[0].inserted==1);
 std::cout<<"Native cohort wire PASS "<<checks<<" checks;membership content identity retirement revision pointer reuse bounded stats\n";
}
