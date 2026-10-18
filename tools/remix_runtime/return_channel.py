"""Version2 diagnostic-image metadata only: no CPU image payload transport."""
import ctypes as C
import os
import re

MAGIC, VERSION, FORMAT = 0x53465232, 2, 87
class State(C.Structure):
    _fields_ = [(n,C.c_uint32) for n in ('magic','version','bytes','creatorPid','gamePid','width','height','format')] + [
        (n,C.c_uint64) for n in ('sharedHandle','qpcFrequency','renderedAt','renderFrame')] + [
        (n,C.c_int32) for n in ('epoch','ready','armed','enabled','stop','produced','acknowledged','presented','error','copyCount','drawCount','staleCount','skipCount','clearCount','lastWidth','lastHeight','startupRestored','startupVerified','renderEpoch','presentedEpoch','visibilityVersion','visibilitySamples','depthPresentSamples','depthWidth','depthHeight','depthFormat','depthBindFlags','depthMultisamples','visibilityScope','depthViewFormat')] + [('padding',C.c_ubyte*72)]
assert C.sizeof(State)==256 and State.epoch.offset==64 and State.sharedHandle.offset==32
def valid(s):
    return s.magic==MAGIC and s.version==VERSION and s.bytes==256 and s.creatorPid!=0 and s.width==s.height==256 and s.format==FORMAT and s.qpcFrequency!=0
def valid_name(name):
    return bool(re.fullmatch(r'Local\\SFC-Remix-Return-\{[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\}',name))
def visibility_result(s):
    """Never promote a bound descriptor into proven scene depth or occlusion."""
    if s.visibilityVersion==0:return 'NOT_REQUESTED'
    if (s.visibilityVersion!=1 or s.visibilityScope not in (0,1,2) or not 0<=s.visibilitySamples<=8 or
            not 0<=s.depthPresentSamples<=s.visibilitySamples):return 'INVALID_OBSERVATION'
    if s.visibilitySamples<8:return 'INCOMPLETE'
    if s.visibilityScope==2:
        return 'EARLY_DSV_DESCRIPTOR_ONLY_UNQUALIFIED' if s.depthPresentSamples else 'NO_DSV_AT_EARLY_PRESENT'
    return 'DSV_DESCRIPTOR_ONLY_UNQUALIFIED' if s.depthPresentSamples else 'NO_DSV_AT_LATE_INSERTION'
class Channel:
    def __init__(self,name):
        if os.name!='nt' or not valid_name(name):raise ValueError('Invalid Windows return session')
        k=self.k=C.WinDLL('kernel32',use_last_error=True)
        k.OpenFileMappingW.argtypes=[C.c_uint32,C.c_int,C.c_wchar_p];k.OpenFileMappingW.restype=C.c_void_p
        k.MapViewOfFile.argtypes=[C.c_void_p,C.c_uint32,C.c_uint32,C.c_uint32,C.c_size_t];k.MapViewOfFile.restype=C.c_void_p
        k.UnmapViewOfFile.argtypes=[C.c_void_p];k.CloseHandle.argtypes=[C.c_void_p]
        self.handle=k.OpenFileMappingW(0xF001F,False,name)
        if not self.handle:raise C.WinError(C.get_last_error())
        self.address=k.MapViewOfFile(self.handle,0xF001F,0,0,4096)
        if not self.address:k.CloseHandle(self.handle);raise C.WinError(C.get_last_error())
        self.state=State.from_address(self.address)
        if not valid(self.state):self.close();raise ValueError('Return protocol header mismatch')
    def set(self,name,value):
        if name not in ('armed','enabled','stop'):raise ValueError('Not a runner-controlled flag')
        # On the supported Windows x86/x64 pair an aligned32-bit store is atomic.
        # These are independent control flags, never publication of pixel metadata.
        C.c_int32.from_address(self.address+getattr(State,name).offset).value=int(value)
    def snapshot(self):
        return {n:int(getattr(self.state,n)) for n,_ in State._fields_ if n!='padding'}
    def close(self):
        if getattr(self,'address',None):self.k.UnmapViewOfFile(self.address);self.address=None
        if getattr(self,'handle',None):self.k.CloseHandle(self.handle);self.handle=None
