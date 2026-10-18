#pragma once
#include <windows.h>
namespace sfc_probe {
// Controller thread only. Retry transient loader-list mutation, never an
// injection/remote call whose side effects could already have occurred.
template<class Take,class Error,class Pause>
HANDLE module_snapshot_retry(Take take,Error error,Pause pause,
                             DWORD& lastError,unsigned& attempts) {
    lastError=ERROR_SUCCESS;
    for(attempts=1;attempts<=100;++attempts){
        HANDLE snapshot=take();
        if(snapshot!=INVALID_HANDLE_VALUE)return snapshot;
        lastError=error();
        if(lastError!=ERROR_BAD_LENGTH||attempts==100)break;
        pause(10);
    }
    return INVALID_HANDLE_VALUE;
}
}
