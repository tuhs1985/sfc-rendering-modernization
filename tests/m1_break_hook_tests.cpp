// Exercise actual x86 hook signatures/trampoline forwarding without SFC.
#include "../tools/m1_component/m1_component.cpp"
#include <iostream>
#include <cstdlib>
static unsigned calls=0;
static void checkBreak(bool value,const char* message){if(!value){std::cerr<<message<<'\n';std::exit(1);}}
static DWORD __cdecl factory(DWORD ship,DWORD visual){
 checkBreak(ship==11&&visual==12&&!g_break_factory_scope.parent,"factory arguments and unknown-caller isolation");
 checkBreak(g_in_hook_spans==1&&GetLastError()==321,"factory lifetime and incoming error");++calls;SetLastError(789);return 123;
}
static DWORD __fastcall child(void* self,void*,DWORD visual,DWORD index,DWORD initial,DWORD mode){
 checkBreak(self==reinterpret_cast<void*>(13)&&visual==14&&index==15&&initial==16&&mode==17,"constructor register/stack arguments");
 checkBreak(g_in_hook_spans==1&&GetLastError()==321,"constructor lifetime/error");++calls;SetLastError(789);return 13;
}
static void __fastcall draw(void* self,void*,DWORD manager){
 checkBreak(self==reinterpret_cast<void*>(18)&&manager==19&&!g_break_draw_scope.child,"draw register/stack arguments and isolated scope");
 checkBreak(g_in_hook_spans==1&&GetLastError()==321,"draw lifetime/error");++calls;SetLastError(789);
}
static DWORD __fastcall retire(void* self,void*){
 checkBreak(self==reinterpret_cast<void*>(20)&&GetLastError()==321&&g_in_hook_spans==1,"destructor this/error/lifetime");
 ++calls;SetLastError(789);return 20;
}
int main(){
 for(const auto& hook:g_hooks)if(!strncmp(hook.name,"break_",6)){
  const auto* bytes=static_cast<const BYTE*>(hook.destination);bool bounded=false;
  for(unsigned i=0;i+10<128;++i)if(bytes[i]==0xf0&&bytes[i+1]==0xff&&bytes[i+2]==0x0d){
   DWORD counter=0;memcpy(&counter,bytes+i+3,4);
   if(counter==reinterpret_cast<DWORD>(&g_in_hook_spans)&&(bytes[i+7]==0xc3||bytes[i+7]==0xc2))bounded=true;
  }
  checkBreak(bounded,"guard counter exit/return fits actual unload EIP range");
 }
 g_tramp_break_factory=reinterpret_cast<void*>(&factory);g_tramp_break_child=reinterpret_cast<void*>(&child);
 g_tramp_break_draw=reinterpret_cast<void*>(&draw);g_tramp_break_retire=reinterpret_cast<void*>(&retire);
 g_break_factory_scope={7,8};g_break_draw_scope={9,10,11};
 DWORD before=0,after=0;__asm mov before,esp
 SetLastError(321);checkBreak(HookBreakFactory(11,12)==123&&GetLastError()==789,"factory return/error preservation");
 SetLastError(321);checkBreak(HookBreakChild(reinterpret_cast<void*>(13),nullptr,14,15,16,17)==13&&GetLastError()==789,"constructor return/error preservation");
 SetLastError(321);HookBreakDraw(reinterpret_cast<void*>(18),nullptr,19);checkBreak(GetLastError()==789,"draw error preservation");
 SetLastError(321);checkBreak(HookBreakRetire(reinterpret_cast<void*>(20),nullptr)==20&&GetLastError()==789,"destructor return/error preservation");
 __asm mov after,esp
 checkBreak(before==after&&!g_in_hook_spans&&calls==4,"x86 stack balance and drained callbacks");
 checkBreak(g_break_factory_scope.parent==7&&g_break_draw_scope.child==9&&g_break_draw_scope.epoch==11,"enclosing scopes restored");
 std::cout<<"Break hook ABI/lifetime PASS\n";
 return 0;
}
