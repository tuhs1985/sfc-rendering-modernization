#include "cohort_contract.h"
#include "callback_policy.h"
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
 malformed=m;malformed.count=multi_scene::Owners+1;malformed.checksum=checksum(malformed);test(!valid(malformed,session));
 malformed=m;++malformed.output;test(!valid(malformed,session));
 malformed=m;++malformed.members[1].source;malformed.checksum=checksum(malformed);test(!qualifies(malformed,*catalog,f));
 malformed=m;malformed.members[1].content[0]^=1;malformed.checksum=checksum(malformed);test(!qualifies(malformed,*catalog,f));
 auto changed=f;changed.rows[1][7]++;changed.checksum=multi_scene::checksum(changed);test(!qualifies(m,*catalog,changed));
 changed=f;changed.count=1;changed.checksum=multi_scene::checksum(changed);m.hash=changed.checksum;m.checksum=checksum(m);test(!qualifies(m,*catalog,changed));
 InterlockedIncrement(&s->upstream.guard);test(!read(s->upstream,out));InterlockedIncrement(&s->upstream.guard);
 t.owner=1;t.revision=2;t.model=20;t.source=30;count(*s,t,true,false);count(*s,t,false,true);test(s->header.inserted==1&&s->header.suppressed==1&&s->owners[0].owner==1);
 ++t.revision;count(*s,t,true,false);test(s->owners[1].owner==1&&s->owners[1].revision==3&&s->owners[0].inserted==1);
 // Retained private snapshot remains valid after the shared frame slot moves on.
 auto retained=f;t.frame=f.frame;t.sequence=f.sequence;t.hash=f.checksum;t.thread=77;t.revision=2;
 retained.rows[0][47]=77;live_owner::Row row{};
 test(retainedRow(retained,t,row)&&row[1]==t.owner);
 for(unsigned field=0;field<8;++field){auto bad=t;
  switch(field){case 0:++bad.frame;break;case 1:++bad.sequence;break;case 2:++bad.hash;break;case 3:++bad.owner;break;
   case 4:++bad.revision;break;case 5:++bad.model;break;case 6:++bad.source;break;case 7:++bad.thread;break;}
  test(!retainedRow(retained,bad,row));}
 auto tooMany=retained;tooMany.count=multi_scene::Owners+1;test(!retainedRow(tooMany,t,row));
 test(!native_insertion::needsDrawObservers(true,true,false));
 test(native_insertion::needsDrawObservers(true,false,false));
 test(native_insertion::needsDrawObservers(true,true,true));
 test(!native_insertion::needsDrawObservers(false,false,true));
 // Large fleets:every owner has independent membership/receipts while sharing content.
 f={};f.frame=20;f.anchor=1;f.revision=1;f.sequence=30;f.count=160;
 m={};memcpy(m.session,session,16);m.frame=20;m.anchor=m.revision=1;m.sequence=30;m.output=40;m.count=160;
 for(DWORD i=0;i<160;++i){auto& r=f.rows[i];r[1]=i+1;r[2]=20;r[5]=100+i;r[6]=200+i;r[7]=i+1;r[47]=77;
  auto& x=m.members[i];x.owner=i+1;x.revision=i+1;x.model=r[5];x.source=r[6];x.asset=i+1;x.content[0]=1;
  auto a=catalog->assets[0].packet;a.id=i+1;a.path_id=1;a.owner=x.owner;a.revision=x.revision;a.model=x.model;a.source=x.source;memcpy(a.content,x.content,32);a.checksum=multi_scene::checksum(a);
  catalog->assets[i].packet=a;catalog->assets[i].guard=2;}
 f.checksum=multi_scene::checksum(f);m.hash=f.checksum;m.checksum=checksum(m);test(qualifies(m,*catalog,f));
 initialize(*s,session,GetCurrentProcessId());
 for(DWORD i=0;i<160;++i){auto ticket=t;ticket.frame=20;ticket.sequence=30;ticket.hash=f.checksum;ticket.owner=ticket.revision=i+1;ticket.model=100+i;ticket.source=200+i;
  test(contains(m,ticket)&&retainedRow(f,ticket,row));count(*s,ticket,true,false);count(*s,ticket,false,true);}
 test(s->header.inserted==160&&s->header.suppressed==160&&!s->header.omitted);
 std::cout<<"Native cohort wire PASS "<<checks<<" checks;membership content identity retirement revision pointer reuse bounded stats retained scene callback policy\n";
}
