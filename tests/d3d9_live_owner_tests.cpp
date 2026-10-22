#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include "../tools/d3d9_proof/live_owner_decode.h"
#include "../tools/d3d9_proof/owner_rebind.h"
#include "../tools/d3d9_proof/input_admission.h"
#include <iostream>
#include <memory>
#include <fstream>
using namespace live_owner;
struct Frame {DWORD owner,revision,frame,active;float model[16],view[16],projection[16],viewport[4];};
int wmain(int argc,wchar_t** argv){
 unsigned checks=0;auto test=[&](bool ok){++checks;if(!ok){std::cerr<<"Live owner FAIL "<<checks<<'\n';ExitProcess(1);}};
 const DWORD session[4]{1,2,3,4};auto store=std::make_unique<Store>();store->header.bytes=sizeof(Store);memcpy(store->header.session,session,16);
 test(header_valid(store->header,session));test(sizeof(Store)==1154688);
 Source source;source.store=store.get();InterlockedExchange64(&store->header.selected,static_cast<LONG64>(selection(7,1)));source.begin(5);
 Row r{};r[1]=7;r[2]=5;r[4]=1;r[5]=99;r[6]=98;r[7]=1;r[47]=GetCurrentThreadId();r[48]=1;
 source.offer(r);test(sequence(r)==1);Packet p{};uint64_t last=0;DWORD invalid=0;
 test(take(store->input,store->header,p,last,invalid));test(valid(p,store->header));test(p.row==r);
 test(matches_asset(p,7,1,99,98));test(!matches_asset(p,8,1,99,98));test(!matches_asset(p,7,2,99,98));test(!matches_asset(p,7,1,100,98));test(!matches_asset(p,7,1,99,100));
 auto r2=r;r2[3]=100;r2[45]=3;r2[89]=33;r2[94]=999;test(row_hash(r)==row_hash(r2));++r2[49];test(row_hash(r)!=row_hash(r2));
 Completion c{};memcpy(c.session,session,16);c.sequence=p.sequence;c.offered=p.offered;c.completed=p.offered+1;c.state_hash=p.state_hash;c.frame=5;c.owner=7;c.revision=1;c.checksum=checksum(c);
 DWORD replaced=0;test(publish(store->output,c,replaced));PresentObserver observer;observer.store=store.get();observer.observe(&r,5,GetCurrentThreadId(),p.offered+2);test(store->audits[0].status==1);
 observer.observe(&r,5,GetCurrentThreadId(),p.offered);test(store->audits[1].status==6);
 r[4]=3;observer.observe(&r,5,GetCurrentThreadId(),p.offered+2);test(store->audits[2].status==5);r[4]=1;
 source.begin(6);observer.observe(&r,5,GetCurrentThreadId(),p.offered+2);test(store->audits[3].status==5);source.begin(5);
 auto wrong=r;wrong[94]=2;observer.observe(&wrong,5,GetCurrentThreadId(),p.offered+2);test(store->audits[4].status==2);
 wrong=r;wrong[8]++;observer.observe(&wrong,5,GetCurrentThreadId(),p.offered+2);test(store->audits[5].status==3);
 source.reject(5);observer.observe(&r,5,GetCurrentThreadId(),p.offered+2);test(store->audits[6].status==5);
 store->header.source_rejected=0;source.retire(7,5);test(store->header.source_rejected==0&&store->header.bad_frame==5);
 store->header.bad_frame=0;wrong=r;wrong[1]=8;source.offer(wrong);test(sequence(wrong)==sequence(r));test(store->header.published==1);
 c.checksum^=1;test(publish(store->output,c,replaced));observer.observe(&r,5,GetCurrentThreadId(),p.offered+2);test(store->header.completion_invalid==1);
 float native[16]{1,0,0,3,0,1,0,4,0,0,1,5,9,8,7,6};DWORD words[17]{};memcpy(words,native,64);words[16]=0x100;float decoded[16]{};
 test(matrix(words,decoded));test(decoded[3]==3&&decoded[7]==4&&decoded[11]==5&&decoded[12]==0&&decoded[15]==1);words[16]=0x200;test(!matrix(words,decoded));
 // Real camera/mesh conversion is corroborated separately against captured rows.
 Frame f{};test(!decode(p,f));
 owner_rebind::Control binding;binding.pid=store->header.pid;memcpy(binding.session,session,16);
 owner_rebind::Target target{};target.generation=1;target.owner=9;target.revision=2;target.model=199;target.source=198;target.cookie=123;
 target.checksum=checksum(target);binding.request=target;binding.guard=2;owner_rebind::Target copied{};DWORD generation=0;
 test(owner_rebind::read(binding,store->header,copied));test(owner_rebind::valid(copied,123,0));
 binding.guard=3;test(!owner_rebind::read(binding,store->header,copied));binding.guard=2;
 binding.session[0]++;test(!owner_rebind::read(binding,store->header,copied));binding.session[0]--;
 test(!owner_rebind::valid(target,124,0));test(!owner_rebind::valid(target,123,1));
 auto damaged=target;damaged.owner++;test(!owner_rebind::valid(damaged,123,0));
 test(owner_rebind::apply(binding,*store,target,123,generation));test(generation==1&&binding.acknowledged==1&&static_cast<uint64_t>(store->header.selected)==selection(9,2));
 source.retire(7,5);auto fresh=r;fresh[1]=9;fresh[7]=2;fresh[5]=199;fresh[6]=198;fresh[2]=6;fresh[94]=fresh[95]=0;
 source.begin(6);source.offer(fresh);test(sequence(fresh)>sequence(r));
 test(take(store->input,store->header,p,last,invalid)&&matches_asset(p,9,2,199,198));
 // Delayed old completion can never claim the new owner's current frame.
 const auto nextAudit=store->header.audits;observer.observe(&fresh,6,GetCurrentThreadId(),p.offered+2);test(store->audits[nextAudit].status!=1);
 target.generation=3;target.checksum=checksum(target);test(!owner_rebind::apply(binding,*store,target,123,generation));
 target.generation=2;target.owner=10;target.revision=3;target.checksum=checksum(target);
 test(owner_rebind::apply(binding,*store,target,123,generation));test(binding.acknowledged==2);
 auto admission=p;admission.offered=1000000;store->header.frame=admission.row[2];store->header.bad_frame=0;
 test(fresh_input(admission,store->header,1001000,10000000));
 test(!fresh_input(admission,store->header,1020001,10000000));
 test(!fresh_input(admission,store->header,999999,10000000));
 ++store->header.frame;test(!fresh_input(admission,store->header,1001000,10000000));--store->header.frame;
 store->header.bad_frame=admission.row[2];test(!fresh_input(admission,store->header,1001000,10000000));
 source.close();test(store->header.stopped==1);
 std::cout<<"Live owner PASS "<<checks<<" checks pointer_bits="<<sizeof(void*)*8<<" raw="<<sizeof(Packet)<<" store="<<sizeof(Store)<<'\n';
 if(argc==3){
  std::ifstream input(argv[1],std::ios::binary|std::ios::ate);const auto bytes=input.tellg();test(bytes>0&&bytes<=384*128&&bytes%384==0);input.seekg(0);
  std::ofstream output(argv[2],std::ios::binary|std::ios::trunc);
  for(std::streamoff offset=0;offset<bytes;offset+=384){Packet q{};input.read(reinterpret_cast<char*>(q.row.data()),384);Frame converted{};const DWORD accepted=decode(q,converted)?1u:0u;
   output.write(reinterpret_cast<const char*>(&accepted),4);output.write(reinterpret_cast<const char*>(&converted),sizeof(converted));}
  test(bool(input)&&bool(output));
 }else test(argc==1);
}
