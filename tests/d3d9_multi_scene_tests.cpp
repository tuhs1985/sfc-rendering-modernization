#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include "../tools/d3d9_proof/multi_scene_wire.h"
#include "../tools/d3d9_proof/input_admission.h"
#include <memory>
#include <iostream>
int main(){
 unsigned checks=0;auto test=[&](bool okay){++checks;if(!okay){std::cerr<<"Multi-scene FAIL "<<checks<<'\n';ExitProcess(1);}};
 const DWORD session[]{1,2,3,4};auto store=std::make_unique<multi_scene::Store>();auto& h=store->header;
 h.bytes=sizeof(*store);h.pid=GetCurrentProcessId();memcpy(h.session,session,16);
 test(sizeof(*store)==107072);test(sizeof(multi_scene::FrameSlot)==12352);test(sizeof(multi_scene::AssetSlot)==128);
 test(multi_scene::valid(h,session,GetCurrentProcessId()));test(!multi_scene::valid(h,session,GetCurrentProcessId()+1));
 test(!multi_scene::initial_resolved(*store,3));
 store->assets[0].ack=1;test(!multi_scene::initial_resolved(*store,3));
 store->assets[1].ack=1;test(multi_scene::initial_resolved(*store,3));
 store->assets[1].ack=-1;test(multi_scene::initial_resolved(*store,3));
 test(!multi_scene::initial_resolved(*store,uint64_t(1)<<63));
 store->assets[0].ack=store->assets[1].ack=0;
 multi_scene::Source source;source.store=store.get();source.begin();
 live_owner::Row a{};a[1]=7;a[2]=10;a[4]=a[48]=1;a[5]=70;a[6]=71;a[7]=1;a[89]=100;a[94]=3;
 auto b=a;b[1]=8;b[5]=80;b[6]=81;b[7]=2;b[94]=0;
 source.offer(a);source.offer(b);source.publish(live_owner::selection(7,1));
 auto frame=std::make_unique<multi_scene::Frame>();
 test(multi_scene::read(*store,10,3,*frame));test(frame->count==2&&h.published==1);
 auto check=*frame;check.rows[1][8]++;test(!multi_scene::valid(check));check.checksum=multi_scene::checksum(check);test(multi_scene::valid(check));
 check.rows[1][1]=7;check.checksum=multi_scene::checksum(check);test(!multi_scene::valid(check)); // duplicate owner
 check=*frame;check.rows[1][49]++;check.checksum=multi_scene::checksum(check);test(!multi_scene::valid(check)); // different camera
 check=*frame;check.rows[1][2]++;check.checksum=multi_scene::checksum(check);test(!multi_scene::valid(check));
 check=*frame;check.rows[1][4]=3;check.checksum=multi_scene::checksum(check);test(!multi_scene::valid(check)); // retired
 test(!multi_scene::read(*store,10,4,*frame));test(!multi_scene::read(*store,11,3,*frame));
 auto& slot=store->frames[10%multi_scene::Frames];++slot.guard;test(!multi_scene::read(*store,10,3,*frame));++slot.guard;
 source.begin();source.offer(b);source.publish(live_owner::selection(7,1));test(h.dropped==1&&h.published==1);
 source.begin();for(DWORD i=0;i<40;++i){b[1]=i+1;source.offer(b);}test(source.pending.count==32);
 multi_scene::Asset asset{};asset.id=asset.path_id=1;asset.owner=7;asset.revision=1;asset.model=70;asset.source=71;
 asset.geometry_bytes=1024;asset.image_bytes=4096;asset.content[0]=1;asset.replay_hash=2;asset.textures_hash=3;asset.checksum=multi_scene::checksum(asset);
 test(multi_scene::valid(asset));test(multi_scene::matches(asset,a));b=a;b[7]=2;test(!multi_scene::matches(asset,b)); // pointer reuse/new revision
 auto corrupt=asset;corrupt.id=65;corrupt.checksum=multi_scene::checksum(corrupt);test(!multi_scene::valid(corrupt));
 corrupt=asset;corrupt.geometry_bytes=2*1024*1024+1;corrupt.checksum=multi_scene::checksum(corrupt);test(!multi_scene::valid(corrupt));
 corrupt=asset;corrupt.image_bytes=128*1024*1024+1;corrupt.checksum=multi_scene::checksum(corrupt);test(!multi_scene::valid(corrupt));
 corrupt=asset;corrupt.content[0]=0;corrupt.checksum=multi_scene::checksum(corrupt);test(!multi_scene::valid(corrupt));
 auto& entry=store->assets[0];entry.packet=asset;entry.guard=2;multi_scene::Asset copied{};
 test(multi_scene::read(entry,copied));entry.guard=3;test(!multi_scene::read(entry,copied));entry.guard=2;entry.packet.owner++;test(!multi_scene::read(entry,copied));
 // Deliberately pause the producer between prepare/full-set commit/notification.
 // A consumer must never see a notified input before its full packet exists.
 auto inputs=std::make_unique<live_owner::Store>();auto& ih=inputs->header;ih.bytes=sizeof(*inputs);memcpy(ih.session,session,16);
 live_owner::Source notifier;notifier.store=inputs.get();ih.selected=static_cast<LONG64>(live_owner::selection(7,1));
 a[2]=12;b=a;b[1]=8;b[5]=80;b[6]=81;b[7]=2;b[94]=0;notifier.begin(12);live_owner::Packet prepared{},taken{};uint64_t last=0;DWORD invalid=0;
 test(notifier.prepare(a,prepared));test(ih.published==0);
 test(!live_owner::take(inputs->input,ih,taken,last,invalid));
 source.begin();source.offer(a);source.offer(b);test(source.publish(live_owner::selection(7,1)));
 test(!live_owner::take(inputs->input,ih,taken,last,invalid));
 test(notifier.commit(prepared));test(live_owner::take(inputs->input,ih,taken,last,invalid));
 test(multi_scene::read(*store,taken.row[2],taken.sequence,*frame)&&frame->count==2);
 // The old2ms policy remains for legacy mode;buffered mode closes work only
 // when its matching scene actually reaches the compositor (plus50ms guard).
 taken.offered=1000000;h.closed_frame=10;
 test(live_owner::admission(taken,ih,1100000,10000000,&h.closed_frame)==live_owner::Admission::Accepted);
 test(!live_owner::fresh_input(taken,ih,1100000,10000000));
 ih.frame=13;test(live_owner::admission(taken,ih,1200000,10000000,&h.closed_frame)==live_owner::Admission::Accepted);
 h.closed_frame=12;test(live_owner::admission(taken,ih,1200000,10000000,&h.closed_frame)==live_owner::Admission::Closed);
 h.closed_frame=11;ih.frame=14;test(live_owner::admission(taken,ih,1200000,10000000,&h.closed_frame)==live_owner::Admission::Frame);
 ih.frame=12;test(live_owner::admission(taken,ih,1500001,10000000,&h.closed_frame)==live_owner::Admission::Age);
 ih.bad_frame=12;test(live_owner::admission(taken,ih,1100000,10000000,&h.closed_frame)==live_owner::Admission::BadFrame);
 ih.bad_frame=0;test(live_owner::admission(taken,ih,999999,10000000,&h.closed_frame)==live_owner::Admission::Clock);
 source.close();test(h.stopped&&!multi_scene::valid(h,session,GetCurrentProcessId()));
 std::cout<<"Multi-scene PASS "<<checks<<" checks pointer_bits="<<sizeof(void*)*8<<" store="<<sizeof(*store)<<'\n';
}
