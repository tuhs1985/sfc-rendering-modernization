"""Runner-only normal-exit detection and owned-controller retirement.

No game hooks or per-frame file reads. A retained verified-process handle also
detects exit before the launcher parent has finished writing its final receipt.
"""
import ctypes as C
from ctypes import wintypes as W
import json
import subprocess as sp
from pathlib import Path


class NormalGameExit(Exception):
    pass


class Monitor:
    def __init__(self,launcher,log):
        self.launcher=launcher;self.log=Path(log);self.handle=None;self.kernel=None

    def attach(self,pid):
        k=C.WinDLL('kernel32',use_last_error=True)
        k.OpenProcess.argtypes=[W.DWORD,W.BOOL,W.DWORD];k.OpenProcess.restype=W.HANDLE
        k.WaitForSingleObject.argtypes=[W.HANDLE,W.DWORD];k.CloseHandle.argtypes=[W.HANDLE]
        self.handle=k.OpenProcess(0x100000,False,pid)
        if not self.handle:raise C.WinError(C.get_last_error())
        self.kernel=k

    def check(self):
        code=self.launcher.poll()
        if code is None:
            if not self.handle:return
            state=self.kernel.WaitForSingleObject(self.handle,0)
            if state==258:return
            if state!=0:raise RuntimeError('Verified game exit handle failed')
            try:code=self.launcher.wait(timeout=5)
            except sp.TimeoutExpired:raise RuntimeError('Game exited but launcher did not retire within5s')
        if code==0 and 'CHILD_EXIT code=0' in self.log.read_text(errors='replace'):raise NormalGameExit()
        raise RuntimeError('Copied game exited abnormally;launcher exit='+str(code))

    def close(self):
        if self.handle:self.kernel.CloseHandle(self.handle);self.handle=None


def retire_controller(controller,game_exited):
    """A controller may be retired forcibly only after verified game exit."""
    if not controller or not game_exited or controller.poll() is not None:return False
    try:controller.wait(timeout=5);return False
    except sp.TimeoutExpired:
        controller.terminate();controller.wait(timeout=5);return True


def early_without_output(relay):
    if not relay.process or not relay.selected:return True
    return relay.additive and relay.receiver.channel.read(11*1024*1024+128*1024,4)==bytes(4)


def partial_live_result(relay):
    if getattr(relay,'error',None):raise RuntimeError('Early-exit worker failure: '+str(relay.error))
    process=relay.process or getattr(relay,'prewarm_process',None)
    if process:
        if process.poll()!=0:raise RuntimeError('Early-exit renderer did not retire normally')
        job=json.loads((relay.folder/'gpu/job-result.json').read_text())
        if job['exit_code'] or job['stop_reason'] or job['remaining_owned_processes']:raise RuntimeError('Early-exit owned GPU cleanup failed')
    return dict(result='PARTIAL_NORMAL_EXIT_BEFORE_OUTPUT',normal_owned_exit=True,
                reason='Sponsor exited before qualified live output;completed evidence retained')
