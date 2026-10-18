#include "../tools/m1_component/module_snapshot_retry.h"
#include <iostream>
#include <stdexcept>
int main(){
    unsigned checks=0;
    auto check=[&](bool ok){++checks;if(!ok)throw std::runtime_error("snapshot retry assertion");};
    for(unsigned failures: {0u,1u,99u,100u}){
        unsigned calls=0,pauses=0,attempts=0;DWORD error=0;
        const auto answer=sfc_probe::module_snapshot_retry(
            [&](){return ++calls<=failures?INVALID_HANDLE_VALUE:reinterpret_cast<HANDLE>(1);},
            [](){return DWORD(ERROR_BAD_LENGTH);},[&](DWORD ms){check(ms==10);++pauses;},error,attempts);
        check(calls==(failures==100?100:failures+1));
        check(pauses==(failures==100?99:failures));
        check((answer==INVALID_HANDLE_VALUE)==(failures==100));
    }
    unsigned calls=0,attempts=0,unexpectedPauses=0;DWORD error=0;volatile DWORD fatal=ERROR_ACCESS_DENIED;
    const auto denied=sfc_probe::module_snapshot_retry(
        [&](){++calls;return INVALID_HANDLE_VALUE;},[&](){return DWORD(fatal);},
        [&](DWORD){++unexpectedPauses;},error,attempts);
    check(denied==INVALID_HANDLE_VALUE&&calls==1&&error==ERROR_ACCESS_DENIED&&unexpectedPauses==0);
    std::cout<<"Module snapshot bounded retry PASS "<<checks<<" checks\n";
}
