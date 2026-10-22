#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include "../tools/m1_component/m1_light_transport.h"
#include <iostream>
#include <memory>
int main(){
 using namespace sfc_light_transport;unsigned checks=0;auto test=[&](bool ok){++checks;if(!ok)ExitProcess(1);};
 const DWORD session[4]{1,2,3,4};auto store=std::make_unique<Raw>();store->header.magic=RawMagic;store->header.bytes=sizeof(Raw);store->header.pid=77;memcpy(store->header.session,session,16);
 test(valid(store->header,RawMagic,sizeof(Raw),session,77));test(!valid(store->header,RawMagic,sizeof(Raw),session,78));
 auto& cell=store->cells[3];sfc_native_lights::Snapshot p{},out{};ULONGLONG tick=0;
 test(!read(cell,out,tick));p.header[8]=3;publish(store->header,cell,p,123);
 test(read(cell,out,tick)&&tick==123&&out.header[8]==3&&store->header.published==1);
 InterlockedIncrement(&cell.guard);test(!read(cell,out,tick));InterlockedIncrement(&cell.guard);
 p.header[8]=35;publish(store->header,cell,p,124);test(read(cell,out,tick)&&out.header[8]==35&&tick==124);
 InterlockedExchange(&store->header.stopped,1);test(!valid(store->header,RawMagic,sizeof(Raw),session,77));
 Encoded e;e.header.magic=EncodedMagic;e.header.bytes=sizeof(e);e.header.pid=77;memcpy(e.header.session,session,16);
 EncodedPayload body{},copy{};body.packet[199]=42;body.shapes[807]=43;publish(e.header,e.cell,body,456);
 test(read(e.cell,copy,tick)&&tick==456&&copy.packet[199]==42&&copy.shapes[807]==43);
 test(sizeof(e)==1088&&sizeof(*store)==198720);std::cout<<"Shared lights PASS "<<checks<<" checks pointer_bits="<<sizeof(void*)*8<<'\n';
}
