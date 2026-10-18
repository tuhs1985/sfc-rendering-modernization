#include "../tools/m1_component/m1_present_calibration.h"
#include <iostream>
#include <cstdlib>
static unsigned checks=0;
static void check(bool ok){++checks;if(!ok)std::exit(1);}
int main(){
 using namespace sfc_calibration;Mailbox m;Snapshot out;
 check(!read(&m,out));m.active=1;begin(&m,2);check(!read(&m,out));
 std::array<DWORD,Words> r{};r[1]=7;r[2]=2;r[4]=1;r[5]=99;r[6]=98;r[7]=3;r[48]=1;
 check(offer(&m,1,r));check(read(&m,out)&&out.frame==2&&out.rows==1&&out.owner[1][45]==1);
 check(offer(&m,1,r));check(read(&m,out)&&out.owner[1][4]==1);
 r[5]=100;check(offer(&m,1,r));check(read(&m,out)&&out.owner[1][4]==3);
 r[5]=99;check(offer(&m,1,r));check(read(&m,out)&&out.owner[1][4]==3);
 begin(&m,3);check(!read(&m,out));check(!offer(&m,1,r));r[2]=3;r[1]=8;
 check(offer(&m,1,r));check(read(&m,out)&&out.owner[1][1]==8&&out.owner[1][4]==1);
 m.busy=1;check(!read(&m,out));check(!offer(&m,1,r));begin(&m,4);m.busy=0;
 check(read(&m,out)&&out.frame==3);check(!offer(&m,32,r));
 m.active=0;check(!read(&m,out));check(!offer(&m,1,r));
 Reader reader;SetEnvironmentVariableW(L"SFC_REMIX_CALIBRATION_SCENE",nullptr);
 check(reader.prepare()&&!reader.requested);reader.close();
 SetEnvironmentVariableW(L"SFC_REMIX_CALIBRATION_SCENE",L"invalid");
 check(!reader.prepare()&&reader.requested);reader.close();SetEnvironmentVariableW(L"SFC_REMIX_CALIBRATION_SCENE",nullptr);
 std::cout<<"Present calibration PASS "<<checks<<" checks\n";
}
