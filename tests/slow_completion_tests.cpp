#define NOMINMAX
#include <windows.h>
#include <algorithm>
#include <sstream>
#include "../tools/d3d9_proof/slow_completion.h"
int main(){unsigned checks=0;const auto test=[&](bool value){++checks;if(!value)ExitProcess(1);};
 slow_completion::Recorder r;r.enabled=false;slow_completion::Record record;record.total=r.frequency;
 r.retain(record);test(r.used==0);r.enabled=true;record.total=r.frequency/100;r.retain(record);test(r.used==0);
 record.total=r.frequency/10;record.frame=77;r.retain(record);test(r.used==1);
 record.total=1;record.failed=true;r.retain(record);test(r.used==2);
 for(unsigned i=0;i<100;++i)r.retain(record);test(r.used==64&&r.dropped==38);
 std::ostringstream out;r.flush(out);test(out.str().find("source_frame=77")!=std::string::npos);test(out.str().find("SLOW_COMPLETION_DROPPED count=38")!=std::string::npos);test(r.used==0&&r.dropped==0);
 auto& active=slow_completion::recorder();active.enabled=true;
 {slow_completion::Scope scope(123);const auto at=scope.clock();Sleep(110);scope.service(at);}
 test(active.used==1&&active.records[0].service>=active.frequency/10&&active.records[0].frame==123);
 try{slow_completion::Scope scope(456);throw 1;}catch(int){}
 test(active.used==2&&active.records[1].failed);active.flush(out);
 std::cout<<"Slow completion PASS "<<checks<<" checks\n";return 0;
}
