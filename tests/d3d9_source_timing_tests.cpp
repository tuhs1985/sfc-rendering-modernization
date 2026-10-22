#include "../tools/d3d9_proof/source_timing.h"
#include <memory>
#include <iostream>
int main(){
 unsigned checks=0;auto test=[&](bool b){++checks;if(!b){std::cerr<<"Source timing FAIL "<<checks<<'\n';ExitProcess(1);}};
 const DWORD session[]={1,2,3,4};auto storage=std::make_unique<source_timing::Store>();source_timing::initialize(*storage,7,9,1000,session);
 sfc_calibration::Mailbox mailbox;mailbox.active=1;memcpy(mailbox.snapshot.session,session,16);sfc_calibration::begin(&mailbox,11);
 std::array<DWORD,96> row{};row[1]=4;row[2]=11;row[4]=1;row[5]=99;row[6]=98;row[7]=1;row[47]=9;row[48]=1;
 sfc_calibration::stamp(row,100);test(sfc_calibration::offer(&mailbox,0,row));sfc_calibration::stamp(row,120);test(sfc_calibration::offer(&mailbox,0,row));
 sfc_calibration::Snapshot snap;test(sfc_calibration::read(&mailbox,snap));test(snap.owner[0][89]==100&&snap.owner[0][91]==120&&snap.reserved[0]==0);
 source_timing::append(*storage,snap,1,9,150);test(storage->header.count==1);const auto& r=storage->records[0];test(r.first_qpc==100&&r.last_qpc==120&&r.observed_qpc==150&&r.frame==11&&r.owner==4&&r.stage==1);
 source_timing::append(*storage,snap,2,9,160);test(storage->header.count==2&&storage->records[1].stage==2);
 source_timing::append(*storage,snap,1,8,170);test(storage->header.wrong_thread==1&&storage->header.count==2);
 source_timing::append(*storage,snap,1,9,110);test(storage->header.invalid==1&&storage->header.count==2);
 snap.owner[0][93]=0;source_timing::append(*storage,snap,1,9,200);test(storage->header.missing_stamp==1);
 snap.owner[0][93]=sfc_calibration::TimingMagic;snap.owner[0][4]=3;source_timing::append(*storage,snap,1,9,200);test(storage->header.ambiguous==1);
 snap.owner[0][4]=1;storage->header.count=source_timing::Capacity;source_timing::append(*storage,snap,1,9,200);test(storage->header.dropped==1&&storage->header.count==source_timing::Capacity);
 storage->header.count=2;snap.session[0]=5;source_timing::append(*storage,snap,1,9,200);test(storage->header.invalid==2);
 sfc_calibration::begin(&mailbox,12);row[2]=12;sfc_calibration::stamp(row,300);test(sfc_calibration::offer(&mailbox,0,row));test(sfc_calibration::read(&mailbox,snap));test(snap.owner[0][89]==300&&snap.owner[0][91]==300);
 row[5]=100;sfc_calibration::stamp(row,310);test(sfc_calibration::offer(&mailbox,0,row));test(sfc_calibration::read(&mailbox,snap)&&snap.owner[0][4]==3);
 std::cout<<"Source timing PASS "<<checks<<" checks record="<<sizeof(source_timing::Record)<<" store="<<sizeof(source_timing::Store)<<'\n';return 0;
}
