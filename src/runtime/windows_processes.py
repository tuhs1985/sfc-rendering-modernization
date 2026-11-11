"""Read-only native inventory; enumeration errors are never 'no game running'."""
import ctypes as C
from ctypes import wintypes as W

class Entry(C.Structure):
    _fields_=[('dwSize',W.DWORD),('cntUsage',W.DWORD),('th32ProcessID',W.DWORD),
              ('th32DefaultHeapID',C.c_size_t),('th32ModuleID',W.DWORD),
              ('cntThreads',W.DWORD),('th32ParentProcessID',W.DWORD),
              ('pcPriClassBase',W.LONG),('dwFlags',W.DWORD),('szExeFile',W.WCHAR*260)]

def process_names():
    k=C.WinDLL('kernel32',use_last_error=True)
    k.CreateToolhelp32Snapshot.argtypes=[W.DWORD,W.DWORD];k.CreateToolhelp32Snapshot.restype=W.HANDLE
    for n in ('Process32FirstW','Process32NextW'):
        f=getattr(k,n);f.argtypes=[W.HANDLE,C.POINTER(Entry)];f.restype=W.BOOL
    k.CloseHandle.argtypes=[W.HANDLE]
    handle=k.CreateToolhelp32Snapshot(2,0)
    if not handle or handle==C.c_void_p(-1).value:raise C.WinError(C.get_last_error())
    names=[];entry=Entry();entry.dwSize=C.sizeof(entry)
    try:
        ok=k.Process32FirstW(handle,C.byref(entry))
        while ok:
            names.append(entry.szExeFile)
            ok=k.Process32NextW(handle,C.byref(entry))
        if C.get_last_error()!=18:raise C.WinError(C.get_last_error())
        return names
    finally:k.CloseHandle(handle)

def game_running():return any(n.casefold()=='starfleetop.exe' for n in process_names())
