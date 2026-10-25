// Deterministic owned process only. Never installed in the copied game.
#pragma once
#include <array>
#include "survey_native_contract.h"
namespace survey_native_fixture {
using namespace survey_native;
inline std::array<Word,2048> manager{};
inline std::array<Word,4> tableA{0,0x401111,0,0},tableB{0,0x402222,0,0};
inline std::array<Word,4> a{},b{};inline Word head=0;
__declspec(noinline) inline Word __fastcall set(void* object,void*,Word slot,Word data){
 if(slot==63&&!data){RaiseException(0xE0420042,0,0,nullptr);}
 auto* bytes=static_cast<BYTE*>(object);if(slot<64)std::memcpy(bytes+0x778+slot*64,reinterpret_cast<void*>(data),64);SetLastError(123);return 0x12345678;
}
__declspec(noinline) inline Word __fastcall enable(void* object,void*,Word slot,Word value){
 if(slot<64)static_cast<BYTE*>(object)[0x1778+slot]=static_cast<BYTE>(value);SetLastError(124);return 0x87654321;
}
__declspec(noinline) inline Word __fastcall gate(void* object,void*,Word value){
 auto& target=static_cast<BYTE*>(object)[0x1EB8];const Word before=target;target=static_cast<BYTE>(value);SetLastError(125);return before;
}
__declspec(noinline) inline Word __cdecl dispatch(Word value){SetLastError(126);return value^0xDEADBEEF;}
inline Targets setup(){
 manager={};manager[0]=0x007B8D4C;
 a={reinterpret_cast<Word>(tableA.data()),reinterpret_cast<Word>(b.data()),0,0};
 b={reinterpret_cast<Word>(tableB.data()),0,0,0};head=reinterpret_cast<Word>(a.data());
 return {reinterpret_cast<Set>(&set),reinterpret_cast<Set>(&enable),reinterpret_cast<Gate>(&gate),&dispatch,reinterpret_cast<Word>(&head)};
}
inline bool tick(unsigned frame){
 std::array<Word,16> data{};data[0]=frame%2?5:0;data[4]=frame;data[7]=0x3F800000;data[10]=0x3F000000;
 const auto p=reinterpret_cast<Word>(manager.data());
 const auto setter=reinterpret_cast<Set>(&set);const auto enabler=reinterpret_cast<Set>(&enable);const auto gater=reinterpret_cast<Gate>(&gate);
 const auto dispatcher=static_cast<Dispatch>(&dispatch);
 const auto s=setter(manager.data(),frame%4,reinterpret_cast<Word>(data.data()));const auto se=GetLastError();
 const auto e=enabler(manager.data(),frame%4,frame%2);const auto ee=GetLastError();
 gater(manager.data(),1);const auto ge=GetLastError();
 const auto d=dispatcher(p);const auto de=GetLastError();
 return s==0x12345678&&e==0x87654321&&d==(p^0xDEADBEEF)&&se==123&&ee==124&&ge==125&&de==126;
}
}
