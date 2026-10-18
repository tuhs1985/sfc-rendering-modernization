#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include "../tools/remix_runtime/ship_live_camera.h"
#include <iostream>
#include <limits>
using namespace ship_live;
static unsigned checks=0;
static void check(bool b){++checks;if(!b){std::cerr<<"LIVE_REQUEST_FAIL check="<<checks<<"\n";std::exit(1);}}
static void f(DWORD& word,float value){memcpy(&word,&value,4);}
static Seed seed(){Seed s{};s.key.session[0]=1;s.key.sourceSession[0]=2;s.key.sourcePid=55;s.key.owner=s.key.revision=s.key.frame=s.key.resourceEpoch=s.key.depthConvention=1;s.key.pose=s.key.camera=1;s.key.objectId=29;s.key.width=s.key.height=256;s.key.viewport[2]=s.key.viewport[3]=256;s.key.asset[0]=1;s.model=100;s.source=200;s.lod=1;s.meshHash=8;return s;}
static sfc_calibration::Snapshot snapshot(){sfc_calibration::Snapshot s{};s.session[0]=2;s.frame=120;s.rows=1;auto& r=s.owner[0];r[1]=1;r[2]=120;r[4]=1;r[5]=100;r[6]=200;r[7]=1;r[46]=1;r[47]=7;r[48]=1;
 for(unsigned start:{8u,49u}){for(unsigned i=0;i<4;++i)f(r[start+i*4+i],1);r[start+16]=256;}
 f(r[66],1);f(r[71],1);f(r[76],-1.0001f);f(r[77],-2);f(r[80],-1);
 f(r[85],256);f(r[86],256);f(r[87],128);f(r[88],128);return s;}
int main(){
 auto s=seed();auto snap=snapshot();Key key{};std::array<uint32_t,96> row{};
 check(sizeof(Command)==592&&sizeof(Seed)==176&&offsetof(Command,offered)==560&&offsetof(Wire,lease)==112&&offsetof(Wire,sequence)==116&&offsetof(Wire,ack)==120);check(makeKey(s,snap,55,7,key,row));check(key.frame==120&&key.pose&&key.camera);
 Camera c{};check(camera(row,c));check(std::abs(c.nearZ-1.9998f)<.0001f&&c.farZ>19000&&c.farZ<21000);check(c.forward[2]==-1&&c.right[0]==1&&c.up[1]==1);
 for(unsigned field=0;field<14;++field){auto bad=snap;
  switch(field){case 0:bad.frame=121;break;case 1:bad.owner[0][4]=2;break;case 2:bad.owner[0][5]=101;break;case 3:bad.owner[0][6]=201;break;case 4:bad.owner[0][7]=2;break;case 5:bad.owner[0][46]=2;break;case 6:bad.owner[0][47]=8;break;case 7:bad.session[0]=3;break;case 8:bad.owner[0][45]=1;break;case 9:bad.owner[1]=bad.owner[0];break;case 10:f(bad.owner[0][8],std::numeric_limits<float>::infinity());break;case 11:bad.owner[0][48]=0;break;case 12:bad.owner[0][42]=1;break;case 13:bad.rows=33;break;}
  check(!makeKey(s,bad,55,7,key,row));}
 check(!makeKey(s,snap,56,7,key,row));check(makeKey(s,snap,55,7,key,row));const auto previous=key;
 auto malformed=snap;malformed.reserved[0]=1;check(!makeKey(s,malformed,55,7,key,row));
 malformed=snap;malformed.owner[0][1]=2;check(!makeKey(s,malformed,55,7,key,row));
 f(snap.owner[0][11],5);check(makeKey(s,snap,55,7,key,row)&&key.pose!=previous.pose&&key.camera==previous.camera);
 snap=snapshot();f(snap.owner[0][52],5);check(makeKey(s,snap,55,7,key,row)&&key.camera!=previous.camera);
 snap=snapshot();check(makeKey(s,snap,55,7,key,row));auto badRow=row;badRow[65]=512;check(!camera(badRow,c));badRow=row;float offaxis=.1f;memcpy(&badRow[68],&offaxis,4);check(!camera(badRow,c));
 Wire wire{};wire.creator=1;wire.width=wire.height=256;wire.handles[0]=1;wire.handles[1]=2;wire.handles[2]=3;wire.frequency=100;wire.resourceEpoch=1;wire.session[0]=1;wire.ready=1;Command cmd{};
 check(offer(wire,cmd,key,row,100));Key rendering{};std::array<uint32_t,96> received{};
 check(ship_live::begin(wire,cmd,rendering,received,100)&&same(rendering,key)&&row==received);
 uint64_t hashes[3]{};check(publish(wire,rendering,hashes,101));auto newer=key;++newer.frame;
 check(!claim(wire,newer,101)&&wire.ack==1&&wire.rejected==1);check(!offer(wire,cmd,newer,row,200));++row[2];check(offer(wire,cmd,newer,row,200));
 check(ship_live::begin(wire,cmd,rendering,received,200));auto newest=newer;++newest.frame;++row[2];check(offer(wire,cmd,newest,row,201));check(!publish(wire,rendering,hashes,202)&&wire.lease==Idle);
 check(!ship_live::begin(wire,cmd,rendering,received,302));wire.guard=1;check(!offer(wire,cmd,newest,row,202));wire.guard=0;cmd.sequence=UINT32_MAX;check(!offer(wire,cmd,newest,row,202));
 // Deterministic reproduction: GPU finished while consumer holds metadata lock.
 // Use the same completion helper as the host,not a test-only state machine.
 cmd.sequence=0;check(offer(wire,cmd,newest,row,203));
 check(ship_live::begin(wire,cmd,rendering,received,203));bool pending=true;
 const auto seq=wire.sequence;wire.guard=1;
 for(unsigned i=0;i<8;++i)check(publishCompleted(wire,rendering,hashes,204+i,pending)==Publication::Busy&&pending&&wire.lease==Rendering&&wire.sequence==seq);
 wire.guard=0;check(publishCompleted(wire,rendering,hashes,212,pending)==Publication::Published&&!pending&&wire.lease==Ready&&wire.sequence==seq+1);
 check(claim(wire,newest,212));check(!finish(wire,wire.sequence,false)&&wire.lease==Reading);
 check(finish(wire,wire.sequence,true)&&wire.lease==Idle);
 check(offer(wire,cmd,newest,row,213));check(ship_live::begin(wire,cmd,rendering,received,213));pending=true;
 auto changed=newest;++changed.frame;++row[2];check(offer(wire,cmd,changed,row,214));
 check(publishCompleted(wire,rendering,hashes,215,pending)==Publication::Cancelled&&!pending&&wire.lease==Idle);
 check(ship_live::begin(wire,cmd,rendering,received,215));pending=true;wire.stop=1;
 check(publishCompleted(wire,rendering,hashes,216,pending)==Publication::Cancelled&&!pending&&wire.lease==Idle);wire.stop=0;
 pending=true;check(publishCompleted(wire,rendering,hashes,217,pending)==Publication::Invalid&&pending);
 float rect[4]{};auto placement=seed().key;placement.viewport[2]=1920;placement.viewport[3]=1080;
 check(displayRect(placement,1920,1080,rect)&&rect[0]==0&&rect[1]==0&&rect[2]==1920&&rect[3]==1080);
 check(!displayRect(placement,800,600,rect));check(!displayRect(placement,1920,std::numeric_limits<float>::quiet_NaN(),rect));
 placement.viewport[0]=100;placement.viewport[1]=40;placement.viewport[2]=800;placement.viewport[3]=600;
 check(displayRect(placement,1920,1080,rect)&&rect[0]==100&&rect[1]==40&&rect[2]==900&&rect[3]==640);
 check(!displayRect(placement,800,600,rect));check(!displayRect(placement,2560,1440,rect));
 placement.viewport[0]=200;placement.viewport[1]=30;placement.viewport[2]=1720;placement.viewport[3]=1020;
 check(displayRect(placement,1920,1080,rect)&&rect[0]==200&&rect[1]==30&&rect[2]==1920&&rect[3]==1050);
 Wire buffered{};buffered.version=BufferedVersion;buffered.creator=1;buffered.width=buffered.height=256;buffered.handles[0]=1;buffered.handles[1]=2;buffered.handles[2]=3;buffered.frequency=1000;buffered.resourceEpoch=1;buffered.session[0]=1;buffered.ready=1;
 auto captured=seed().key;captured.diagnosticMode=BufferedMode;captured.worldOffset[0]=1;
 check(validKey(captured)&&ship_triplet::valid(buffered));check(request(buffered,captured));Key active{};
 check(ship_triplet::begin(buffered,active));check(publish(buffered,active,hashes,100));
 auto present=captured;present.frame+=2;present.pose+=3;present.camera+=4;
 const auto resources=describe(buffered);
 check(claimBuffered(buffered,present,150,&resources)&&buffered.published.frame==captured.frame&&buffered.published.pose==captured.pose);
 buffered.guard=1;check(!finish(buffered,buffered.sequence,true)&&buffered.lease==Reading);buffered.guard=0;
 check(finish(buffered,buffered.sequence,true));check(request(buffered,captured));check(ship_triplet::begin(buffered,active));check(publish(buffered,active,hashes,200));
 check(!claimBuffered(buffered,present,301,&resources)&&buffered.lease==Idle);
 check(request(buffered,captured));check(ship_triplet::begin(buffered,active));check(publish(buffered,active,hashes,400));
 auto reused=present;++reused.owner;check(!claimBuffered(buffered,reused,410,&resources)&&buffered.lease==Idle);
 check(request(buffered,captured));check(ship_triplet::begin(buffered,active));check(publish(buffered,active,hashes,500));
 auto future=present;future.frame=0;check(!claimBuffered(buffered,future,510,&resources)&&buffered.lease==Idle);
 check(!sourceRecent(100,99,1000)&&!sourceRecent(100,201,1000)&&sourceRecent(100,200,1000));
 std::cout<<"LIVE_REQUEST_PASS checks="<<checks<<" command="<<sizeof(Command)<<"\n";
}
