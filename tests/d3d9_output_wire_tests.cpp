#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include "../tools/d3d9_proof/output_channel.h"
#include <iostream>
int main(){
 unsigned checks=0;auto test=[&](bool b){++checks;if(!b){std::cerr<<"Wire FAIL "<<checks<<'\n';ExitProcess(1);}};
 test(output_wire::receiver_lifetime_ms(false)==60000);
 test(output_wire::receiver_lifetime_ms(true)==110000);
 test(output_wire::receiver_lifetime_ms(true)>90000&&output_wire::receiver_lifetime_ms(true)<285000);
 test(output_wire::receiver_lifetime_ms(true,true)==130000);
 test(output_wire::receiver_lifetime_ms(true,true)>120000&&output_wire::receiver_lifetime_ms(true,true)<285000);
 output_wire::Packet p{};p.magic_value=output_wire::magic;p.version_value=1;p.bytes=sizeof(p);p.producer_pid=7;p.session=9;p.resource_epoch=1;p.sequence=1;p.source_frame=100;p.owner=4;p.revision=4;p.width=960;p.height=540;p.handles[0]=1;p.handles[1]=2;p.handles[2]=3;p.source_state_hash=p.scene_hash=p.published_qpc=1;p.checksum=output_wire::checksum(p);
 test(output_wire::valid(p,9,7));test(!output_wire::valid(p,8,7));test(!output_wire::valid(p,9,8));
 auto bad=[&](output_wire::Packet q){q.checksum=output_wire::checksum(q);test(!output_wire::valid(q,9,7));};
 auto q=p;q.version_value=2;bad(q);q=p;q.bytes=0;bad(q);q=p;q.width=1921;bad(q);q=p;q.height=0;bad(q);q=p;q.handles[0]=0;bad(q);q=p;q.handles[1]=uint64_t(UINT32_MAX)+1;bad(q);q=p;q.sequence=0;bad(q);q=p;q.source_state_hash=0;bad(q);q=p;q.scene_hash=0;bad(q);q=p;q.checksum^=1;test(!output_wire::valid(q,9,7));
 output_wire::Channel c{};c.ack_session=9;c.ack_epoch=1;c.ack_sequence=1;test(output_wire::valid_ack(c,p));++c.ack_sequence;test(!output_wire::valid_ack(c,p));--c.ack_sequence;++c.ack_epoch;test(!output_wire::valid_ack(c,p));--c.ack_epoch;++c.ack_session;test(!output_wire::valid_ack(c,p));
 test(output_wire::state(&c)==output_wire::idle);test(InterlockedCompareExchange(&c.state,output_wire::ready,output_wire::idle)==output_wire::idle);test(InterlockedCompareExchange(&c.state,output_wire::acquired,output_wire::ready)==output_wire::ready);test(InterlockedCompareExchange(&c.state,output_wire::ready,output_wire::idle)==output_wire::acquired);
 test(output_wire::qualified_extent(1920,1080));test(!output_wire::qualified_extent(1280,360));test(!output_wire::qualified_extent(1280,720));
 std::cout<<"Output wire PASS "<<checks<<" checks pointer_bits="<<sizeof(void*)*8<<" packet="<<sizeof(p)<<" channel="<<sizeof(c)<<'\n';return 0;
}
