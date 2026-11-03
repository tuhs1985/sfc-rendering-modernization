// Reads the already-existing supervisor ticket;never consumes or republishes it.
#pragma once
#include "startup_ticket.h"
#include "../m1_component/m1_present_calibration.h"
struct ReceiverActivation {
 sfc_calibration::Reader bridge;HANDLE game=nullptr,producer=nullptr;startup_ticket::Store* cell=nullptr;DWORD parent=0,pid=0;
 ~ReceiverActivation(){if(game)CloseHandle(game);if(producer)CloseHandle(producer);bridge.close();}
 bool open(DWORD host){
  parent=host;wchar_t text[16]{};const auto n=GetEnvironmentVariableW(L"SFC_D3D9_GAME_PID",text,16);if(!n||n>=16)return false;
  wchar_t* end=nullptr;pid=wcstoul(text,&end,10);if(!pid||!end||*end||!bridge.prepare()||!bridge.requested)return false;
  auto* base=reinterpret_cast<BYTE*>(bridge.mailbox)-sfc_calibration::Offset;cell=reinterpret_cast<startup_ticket::Store*>(base+startup_ticket::Offset);
  if(!startup_ticket::valid(*cell,bridge.session,pid))return false;
  game=OpenProcess(SYNCHRONIZE,FALSE,pid);producer=OpenProcess(SYNCHRONIZE,FALSE,cell->producer);return game&&producer;
 }
 bool alive()const{if(!cell)return false;const HANDLE h[]={game,producer};return WaitForMultipleObjects(2,h,FALSE,0)==WAIT_TIMEOUT&&startup_ticket::load(&cell->state)!=startup_ticket::Cancelled;}
 bool accepted(startup_ticket::Activation& a)const{
  if(!alive()||!startup_ticket::valid(*cell,bridge.session,pid)||startup_ticket::load(&cell->state)!=startup_ticket::Accepted||cell->host!=parent)return false;
  a=cell->ticket;return startup_ticket::valid(a,*cell)&&alive();
 }
};
