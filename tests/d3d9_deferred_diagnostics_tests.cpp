#include "../tools/d3d9_proof/deferred_diagnostics.h"
#include <iostream>
#include <sstream>
#include <stdexcept>
static void need(bool ok){if(!ok)throw std::runtime_error("Deferred diagnostic test");}
int main(){
 std::ostringstream out;out<<"before";
 {DeferredDiagnostics buffer(out,true,16);out<<"abc"<<7<<std::flush;need(out.str()=="before");need(buffer.retained()==4);need(!buffer.discarded());}
 need(out.str()=="beforeabc7");out<<"after";need(out.str()=="beforeabc7after");
 std::ostringstream capped;
 {DeferredDiagnostics buffer(capped,true,4);capped<<"123456";need(buffer.retained()==4);need(buffer.discarded()==2);need(capped.good());}
 need(capped.str().find("1234\nDIAGNOSTICS_TRUNCATED") ==0);
 std::ostringstream immediate;{DeferredDiagnostics buffer(immediate,false);immediate<<"now";need(immediate.str()=="now");}
 try{DeferredDiagnostics bad(immediate,true,0);return 1;}catch(const std::invalid_argument&){}
 std::cout<<"Deferred diagnostics PASS bounded/no-write/flush/overflow/disabled/restoration\n";
}
