"""Actual early-receiver IPC/lifetime checks without SFC or GPU rendering."""
import ctypes as C
import json,os,struct,subprocess as sp,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/remix_ingest'),str(ROOT/'tools/d3d9_proof')]
from live_scene import SceneChannel
from warm_start import initialize,activate,cancel,ready
from qualify_startup_ticket import environment

def wait_ready(c,p):
 end=time.monotonic()+30
 while ready(c) is None:
  if p.poll() is not None or time.monotonic()>end:raise AssertionError('Host/receiver failed passive startup')
  time.sleep(.005)

def wait_process(pid):
 k=C.WinDLL('kernel32',use_last_error=True);k.OpenProcess.argtypes=[C.c_uint32,C.c_int,C.c_uint32];k.OpenProcess.restype=C.c_void_p
 k.WaitForSingleObject.argtypes=[C.c_void_p,C.c_uint32];k.GetExitCodeProcess.argtypes=[C.c_void_p,C.POINTER(C.c_uint32)];k.CloseHandle.argtypes=[C.c_void_p]
 h=k.OpenProcess(0x101000,False,pid)
 if not h:return None # Already reaped;no live object to wait on.
 try:
  assert k.WaitForSingleObject(h,5000)==0,'Receiver leaked after host retirement'
  code=C.c_uint32();assert k.GetExitCodeProcess(h,C.byref(code));return code.value
 finally:k.CloseHandle(h)

def run():
 out=ROOT/'artifacts/player-replacement/receiver-startup';out.mkdir(exist_ok=True,parents=True);results=[]
 receiver=ROOT/'artifacts/d3d9-proof/receiver-bin/output_receiver.exe'
 cases=('normal','immediate','poison_environment','cancel_pre','cancel_wait','invalid_crc','invalid_session','invalid_asset','invalid_asset_changed','invalid_host','receiver_invalid_crc','receiver_failure','parent_death','game_exit')
 for arch in ('x86','x64'):
  exe=out/arch/'receiver_startup_probe.exe'
  for case in cases+(('delayed61',) if arch=='x64' else ()):
   folder=out/f'{arch}-{case}';folder.mkdir(exist_ok=True);(folder/'probe-ready.txt').unlink(missing_ok=True)
   game=sp.Popen([sys.executable,'-c','import time;time.sleep(100)'],creationflags=sp.CREATE_NO_WINDOW) if case=='game_exit' else None
   c=SceneChannel(create=True);pid=game.pid if game else os.getpid();initialize(c,pid);late=environment(c,pid);late['SFC_D3D9_OFFSET_X']='-3.125'
   env=dict(late,SFC_D3D9_PREWARM='1',SFC_D3D9_GAME_OUTPUT='0' if case=='delayed61' else '1',SFC_DIRECT64_TIMING_ONLY='1',SFC_D3D9_LIVE_TIMING='0',SFC_D3D9_PLAYER_REPLACEMENT='0')
   env.pop('SFC_D3D9_ASSET_SHA256',None);env.pop('SFC_D3D9_OFFSET_X',None)
   if case=='poison_environment':env.update(SFC_D3D9_ASSET_SHA256='ff'*32,SFC_D3D9_OFFSET_X='-999')
   p=None;start=time.monotonic()
   try:
    if case=='immediate':activate(c,late,c.name)
    with (folder/'probe.log').open('wb') as log:
     p=sp.Popen([str(exe),str(receiver),str(folder),case],env=env,stdout=log,stderr=sp.STDOUT,creationflags=sp.CREATE_NO_WINDOW)
     if case not in ('cancel_pre','receiver_failure','parent_death'):
      wait_ready(c,p)
      if case=='cancel_wait':cancel(c)
      elif case=='game_exit':game.terminate();game.wait(timeout=5)
      elif case!='immediate':
       if case=='delayed61':
        time.sleep(61);assert p.poll() is None,'Passive receiver spent the old active60s deadline'
       activate(c,late,c.name)
     code=p.wait(timeout=30)
    expected=23 if case=='parent_death' else 20 if case.startswith('invalid_') or case in ('receiver_failure','receiver_invalid_crc') else 10 if case in ('cancel_wait','game_exit') else 0
    assert code==expected,(arch,case,code,(folder/'probe.log').read_text(errors='replace'))
    child=int((folder/'probe-ready.txt').read_text());child_exit=wait_process(child)
    text=(folder/'receiver.log').read_text(errors='replace')
    if case=='receiver_invalid_crc':assert 'RECEIVER_REJECTED receiver accepted asset/session activation required' in text
    assert 'RECEIVED sequence=' not in text
    if expected==0 and case!='cancel_pre':assert 'RECEIVER_ACTIVATED' in text and 'PROBE_ACTIVATED' in (folder/'probe.log').read_text()
    assert c.read(11*1024*1024+128*1024,576)==bytes(576),'No GPU pool may exist before first valid output'
    results.append(dict(arch=arch,case=case,exit=code,child_exit=child_exit,seconds=time.monotonic()-start,pool_unpublished=True))
    print('Receiver startup PASS',arch,case,flush=True)
   finally:
    if p and p.poll() is None:p.terminate();p.wait(timeout=5)
    if game and game.poll() is None:game.terminate();game.wait(timeout=5)
    c.close()
 (out/'qualification.json').write_text(json.dumps(dict(result='PASS',scope='Real receiver IPC,lifetime and late identity;no GPU/SFC',cases=results),indent=2),encoding='utf-8')

if __name__=='__main__':run()
