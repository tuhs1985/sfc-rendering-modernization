// Remix-only resource preparation;existing current-user mapping,no disk bootstrap.
#pragma once
#include "warm_start.h"
#include "prepared_environment_wire.h"
namespace prepared_environment {
struct Resource {
 remixapi_Interface* api=nullptr;remixapi_LightHandle handle=nullptr;LiveLightRow row{};LightShapeRow shape{};
 sfc_calibration::Reader source;HANDLE game=nullptr,producer=nullptr;startup_ticket::Store* ticket=nullptr;
 ~Resource(){if(api&&handle)api->DestroyLight(handle);source.close();if(game)CloseHandle(game);if(producer)CloseHandle(producer);remix_environment::cacheRoot.clear();}
 void check(){if(!ticket)return;HANDLE life[]{game,producer};if(startup_ticket::load(&ticket->state)==startup_ticket::Cancelled||WaitForMultipleObjects(2,life,FALSE,0)!=WAIT_TIMEOUT)throw warm_start::Cancelled{};}
 template<class Wait>void start(remixapi_Interface& external,Wait wait){
  wchar_t enabled[2]{};if(GetEnvironmentVariableW(L"SFC_D3D9_PREPARED_ENVIRONMENT",enabled,2)!=1||enabled[0]!=L'1')return;
  require(warm_start::requested()&&source.prepare()&&source.requested,"prepared environment explicit startup mapping");
  auto* base=reinterpret_cast<BYTE*>(source.mailbox)-sfc_calibration::Offset;
  ticket=reinterpret_cast<startup_ticket::Store*>(base+startup_ticket::Offset);
  wchar_t pidText[16]{};GetEnvironmentVariableW(L"SFC_D3D9_GAME_PID",pidText,16);const DWORD pid=wcstoul(pidText,nullptr,10);
  const auto session=warm_start::session();require(startup_ticket::valid(*ticket,session.data(),pid),"prepared environment startup identity");
  game=OpenProcess(SYNCHRONIZE,FALSE,pid);producer=OpenProcess(SYNCHRONIZE,FALSE,ticket->producer);
  if(!game||!producer)throw warm_start::Cancelled{};check();
  auto* store=reinterpret_cast<Store*>(base+Offset);require(startup_ticket::load(&store->ready)==1&&!store->reserved,"prepared environment publication");
  const Packet p=store->packet;MemoryBarrier();
  require(startup_ticket::load(&store->ready)==1&&valid(p,session.data(),pid,ticket->producer),"prepared environment packet integrity/identity");
  require(fs::is_directory(p.cache)&&!fs::is_symlink(p.cache),"prepared environment cache directory");remix_environment::cacheRoot=p.cache;
  if(!p.flags){std::cout<<"PREPARED_ENVIRONMENT project_dome=0\n";return;}
  shape=p.shapes.rows[2];row.slot=2;row.enabled=1;memcpy(row.values,shape.v+18,12);memcpy(row.values+3,shape.v+15,12);row.values[6]=shape.v[21];row.values[7]=shape.v[22];
  check();require(external.CreateLight&&external.DestroyLight,"prepared environment light API");api=&external;
  handle=createShapedLight(external,row,shape);wait();check();
  std::cout<<"PREPARED_ENVIRONMENT project_dome=1 commands_drained=1 retained=1\n";
 }
 void transfer(RemixLiveLights& target){if(!handle)return;require(!target.preparedHandle&&!target.handles[2],"prepared environment single transfer");
  target.preparedHandle=handle;target.preparedRow=row;target.preparedShape=shape;handle=nullptr;api=nullptr;}
};
}
