#pragma once
#include "output_target.h"
// External renderer thread only. Existing mapping is created before hooks;
// target discovery never depends on a ship, texture or disk configuration.
class NativeTargetReader {
 sfc_calibration::Reader source;DWORD pid=0;HANDLE game=nullptr;
public:
 output_target::Notice current{};
 ~NativeTargetReader(){if(game)CloseHandle(game);source.close();}
 bool latest(output_target::Notice& out){
  if(!source.mailbox){if(!source.prepare()||!source.requested)return false;
   wchar_t text[16]{};GetEnvironmentVariableW(L"SFC_D3D9_GAME_PID",text,16);pid=wcstoul(text,nullptr,10);}
  auto* base=reinterpret_cast<BYTE*>(source.mailbox)-sfc_calibration::Offset;
  const auto& store=*reinterpret_cast<output_target::Store*>(base+output_target::Offset);
  return output_target::read(store,out)&&output_target::valid(out,source.session,pid)&&output_extent::alpha_supported(out.width,out.height);
 }
 template<class Pump> void wait(Pump pump){
  const auto limit=GetTickCount64()+180000;
  for(;;){pump();if(latest(current))return;
   if(source.mailbox){auto* base=reinterpret_cast<BYTE*>(source.mailbox)-sfc_calibration::Offset;
    auto& cell=*reinterpret_cast<startup_ticket::Store*>(base+startup_ticket::Offset);
    if(startup_ticket::load(&cell.state)==startup_ticket::Cancelled)throw warm_start::Cancelled{};
    if(!game)game=OpenProcess(SYNCHRONIZE,FALSE,pid);if(!game)throw warm_start::Cancelled{};
    if(WaitForSingleObject(game,10)!=WAIT_TIMEOUT)throw warm_start::Cancelled{};
   }else Sleep(10);
   require(GetTickCount64()<limit,"Native target discovery180s limit");
  }
 }
};
