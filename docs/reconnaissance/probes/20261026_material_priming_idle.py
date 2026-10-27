"""Bounded actual-renderer menu-idle/cancel test. Never launches SFC.

The only synthetic process is an owned sleeping liveness target. No assets,
activation, output consumer, manual reload or notification retries are supplied.
"""
import argparse
import ctypes as C
from ctypes import wintypes as W
import datetime as dt
import json
from pathlib import Path
import struct
import subprocess as sp
import sys
import time

ROOT=Path(__file__).resolve().parents[3]
for name in ('remix_runtime','d3d9_proof','scene_bridge'):
    sys.path.insert(0,str(ROOT/'tools'/name))


class Memory(C.Structure):
    _fields_=[('cb',W.DWORD),('PageFaultCount',W.DWORD)]+[
        (name,C.c_size_t) for name in ('PeakWorkingSetSize','WorkingSetSize',
        'QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage',
        'QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage','PrivateUsage')]


class ThreadEntry(C.Structure):
    _fields_=[(name,W.DWORD) for name in ('dwSize','cntUsage','tid','pid')]+[
        ('base',W.LONG),('delta',W.LONG),('flags',W.DWORD)]


class Sampler:
    def __init__(self,pid):
        self.k=C.WinDLL('kernel32',use_last_error=True)
        self.k.OpenProcess.argtypes=[W.DWORD,W.BOOL,W.DWORD];self.k.OpenProcess.restype=W.HANDLE
        self.k.CloseHandle.argtypes=[W.HANDLE]
        self.k.GetProcessTimes.argtypes=[W.HANDLE,*([C.POINTER(W.FILETIME)]*4)]
        self.k.GetProcessHandleCount.argtypes=[W.HANDLE,C.POINTER(W.DWORD)]
        self.k.CreateToolhelp32Snapshot.argtypes=[W.DWORD,W.DWORD];self.k.CreateToolhelp32Snapshot.restype=W.HANDLE
        self.k.Thread32First.argtypes=[W.HANDLE,C.POINTER(ThreadEntry)]
        self.k.Thread32Next.argtypes=[W.HANDLE,C.POINTER(ThreadEntry)]
        self.k.OpenThread.argtypes=[W.DWORD,W.BOOL,W.DWORD];self.k.OpenThread.restype=W.HANDLE
        self.k.GetThreadTimes.argtypes=[W.HANDLE,*([C.POINTER(W.FILETIME)]*4)]
        self.k.GetThreadDescription.argtypes=[W.HANDLE,C.POINTER(C.c_wchar_p)]
        self.k.LocalFree.argtypes=[C.c_void_p]
        self.pid=pid
        self.memory=C.WinDLL('psapi',use_last_error=True).GetProcessMemoryInfo
        self.memory.argtypes=[W.HANDLE,C.POINTER(Memory),W.DWORD]
        self.handle=self.k.OpenProcess(0x410,False,pid)
        if not self.handle:raise C.WinError(C.get_last_error())

    def sample(self):
        times=[W.FILETIME() for _ in range(4)];memory=Memory();memory.cb=C.sizeof(memory);handles=W.DWORD()
        if (not self.k.GetProcessTimes(self.handle,*[C.byref(x) for x in times])
                or not self.memory(self.handle,C.byref(memory),memory.cb)
                or not self.k.GetProcessHandleCount(self.handle,C.byref(handles))):
            raise C.WinError(C.get_last_error())
        cpu=sum((x.dwHighDateTime<<32)|x.dwLowDateTime for x in times[2:])/10_000_000
        return dict(at=time.monotonic(),cpu_seconds=cpu,private_bytes=memory.PrivateUsage,
                    working_set_bytes=memory.WorkingSetSize,handles=handles.value)

    def close(self):self.k.CloseHandle(self.handle)

    def threads(self):
        snapshot=self.k.CreateToolhelp32Snapshot(4,0);out={};entry=ThreadEntry();entry.dwSize=C.sizeof(entry)
        if snapshot==C.c_void_p(-1).value:raise C.WinError(C.get_last_error())
        try:
            more=self.k.Thread32First(snapshot,C.byref(entry))
            while more:
                if entry.pid==self.pid:
                    handle=self.k.OpenThread(0x800,False,entry.tid)
                    if handle:
                        try:
                            times=[W.FILETIME() for _ in range(4)];name=C.c_wchar_p()
                            if self.k.GetThreadTimes(handle,*[C.byref(x) for x in times]):
                                cpu=sum((x.dwHighDateTime<<32)|x.dwLowDateTime for x in times[2:])/10_000_000
                                description=''
                                if self.k.GetThreadDescription(handle,C.byref(name))==0 and name:
                                    description=name.value;self.k.LocalFree(C.cast(name,C.c_void_p))
                                out[entry.tid]=dict(cpu_seconds=cpu,name=description)
                        finally:self.k.CloseHandle(handle)
                more=self.k.Thread32Next(snapshot,C.byref(entry))
        finally:self.k.CloseHandle(snapshot)
        return out


def main(seconds,cancel_early,unprimed_control):
    import async_material_checkout
    if unprimed_control:
        original=async_material_checkout.configure_child
        def control(backend,env):
            text,report=original(backend,env);env.pop('SFC_D3D9_RENDER_PREWARM',None)
            report['diagnostic_unprimed_control']=True
            return text.replace('rtx.enableReplacementAssets = True\n',''),report
        async_material_checkout.configure_child=control
    from async_material_checkout import Relay,backend_inputs
    from present_calibration import Receiver
    from run_return_fixture import TEST
    from run_offline import storage,AGGREGATE_BYTES
    if storage()+192*1024*1024>AGGREGATE_BYTES:raise ValueError('Idle test192MiB reservation within20GB')
    folder=ROOT/'artifacts/remix-runtime/runs'/('prime-idle-'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f'))
    folder.mkdir();receiver=Receiver();relay=None;target=None;sampler=None;error=None;samples=[]
    result=dict(scope='Actual primed renderer;synthetic liveness only;no SFC/scene submitted',
                production_qualification_eligible=False,cancel_early=cancel_early,
                unprimed_control=unprimed_control)
    print('Evidence:',folder,flush=True)
    try:
        target=sp.Popen([sys.executable,'-B','-c','import time;time.sleep(180)'],creationflags=sp.CREATE_NO_WINDOW)
        relay=Relay(folder,receiver,TEST,additive=True,offline_fixture=True,persistent=True,
                    buffered=True,pipeline_mode='performance',checkout_backend=backend_inputs())
        relay.start_on_launch(target.pid)
        if cancel_early:
            time.sleep(.1)
        else:
            deadline=time.monotonic()+30;path=folder/'gpu/renderer-ready.bin'
            while not path.is_file() or path.stat().st_size!=16:
                if relay.prewarm_process.poll() is not None:raise ValueError('Renderer exited before priming readiness')
                if time.monotonic()>deadline:raise ValueError('Priming readiness30s diagnostic bound')
                time.sleep(.05)
            qpc,pid=struct.unpack('<2Q',path.read_bytes());sampler=Sampler(pid)
            result.update(native_pid=pid,ready_qpc=qpc)
            start=time.monotonic();first_threads=None;thread_start=None
            while time.monotonic()-start<seconds:
                if relay.prewarm_process.poll() is not None:raise ValueError('Renderer exited while idle')
                samples.append(sampler.sample())
                if first_threads is None and time.monotonic()-start>=5:
                    first_threads=sampler.threads();thread_start=time.monotonic()
                if any(receiver.channel.read(11*1024*1024+128*1024,576)):
                    raise ValueError('Unexpected public image output before activation')
                time.sleep(.5)
            steady=[x for x in samples if x['at']>=start+5]
            if len(steady)<4:raise ValueError('Insufficient settled idle measurements')
            a,b=steady[0],steady[-1]
            cpu=100*(b['cpu_seconds']-a['cpu_seconds'])/(b['at']-a['at'])
            growth=max(x['private_bytes'] for x in steady)-a['private_bytes']
            handle_growth=max(x['handles'] for x in steady)-a['handles']
            end_threads=sampler.threads();thread_elapsed=time.monotonic()-thread_start
            busy=[dict(tid=tid,name=t['name'],cpu_percent_one_core=100*(t['cpu_seconds']-first_threads[tid]['cpu_seconds'])/thread_elapsed)
                  for tid,t in end_threads.items() if tid in first_threads]
            result['busy_threads']=sorted(busy,key=lambda t:t['cpu_percent_one_core'],reverse=True)[:10]
            result.update(samples=samples,settled_cpu_percent_one_core=cpu,
                          settled_private_growth_bytes=growth,settled_handle_growth=handle_growth,
                          output_published=False,idle_seconds=time.monotonic()-start)
            if cpu>5 or growth>64*1024*1024 or handle_growth>8:
                raise ValueError('Idle CPU/memory/handles exceeded diagnostic bounds')
    except Exception as exc:error=str(exc)
    finally:
        if sampler:sampler.close()
        if relay:
            try:relay.stop()
            except Exception as exc:error=error or str(exc)
        if target and target.poll() is None:target.terminate();target.wait(timeout=5)
        receiver.close()
        if (folder/'gpu/job-result.json').is_file():
            job=json.loads((folder/'gpu/job-result.json').read_text());result['native_job']=job
            if job['exit_code'] or job['stop_reason'] or job['remaining_owned_processes']:
                error=error or 'Owned renderer cancellation incomplete'
        else:error=error or 'Missing native job receipt'
        if (folder/'gpu/job-console.log').is_file():
            log=(folder/'gpu/job-console.log').read_text(errors='replace')
            result['private_warm_passes']=log.count('RENDER_PREWARM mode=triangle frames=56')
            if (result['private_warm_passes']!=(0 if unprimed_control else 1) or 'WARM_CANCELLED no_scene_submitted=1' not in log
                    or 'OUTPUT_API_SHUTDOWN 0' not in log or 'WARM_ACTIVATED' in log):
                error=error or 'Priming once/no activation/normal shutdown evidence incomplete'
        result['error']=error;(folder/'idle-result.json').write_text(json.dumps(result,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k!='samples'},indent=2))
    if error:raise RuntimeError(error)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--seconds',type=int,choices=(15,60),default=60)
    parser.add_argument('--cancel-early',action='store_true')
    parser.add_argument('--unprimed-control',action='store_true');args=parser.parse_args()
    main(args.seconds,args.cancel_early,args.unprimed_control)
