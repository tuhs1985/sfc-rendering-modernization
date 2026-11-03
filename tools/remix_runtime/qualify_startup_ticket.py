"""Actual x86/x64 shared-memory startup consumer;never launches SFC or GPU."""
import ctypes as C
import json
import os
from pathlib import Path
import struct
import subprocess as sp
import sys
import time
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/remix_ingest'),str(ROOT/'tools/d3d9_proof')]
from live_scene import SceneChannel
from warm_start import initialize,activate,cancel,ready,OFFSET
from owner_rebind import fnv

def environment(c,pid):
 return dict(os.environ,SFC_REMIX_CALIBRATION_SCENE=c.name,SFC_D3D9_GAME_PID=str(pid),SFC_D3D9_EXPECTED_MODEL='456',SFC_D3D9_EXPECTED_SOURCE='789',SFC_D3D9_INITIAL_ASSET_MASK='f',SFC_D3D9_REBIND_COOKIE='abc',SFC_D3D9_ASSET_SHA256='12'*32,SFC_D3D9_OFFSET_X='0')
def wait_ready(c,p):
 end=time.monotonic()+5
 while ready(c) is None:
  if p.poll() is not None or time.monotonic()>end:raise ValueError('Worker failed readiness')
  time.sleep(.001)
def producer_exit(exe):
 code="""import sys,subprocess as sp,json,os
sys.path.insert(0,sys.argv[1]);from qualify_startup_ticket import SceneChannel,initialize,environment
c=SceneChannel(create=True);initialize(c,int(sys.argv[3]))
p=sp.Popen([sys.argv[2]],env=environment(c,int(sys.argv[3])),stdout=sp.DEVNULL,stderr=sp.DEVNULL,creationflags=sp.CREATE_NO_WINDOW)
print(json.dumps(dict(name=c.name,pid=p.pid)),flush=True)
sys.stdin.readline()
c.close()
"""
 creator=sp.Popen([sys.executable,'-c',code,str(ROOT/'tools/remix_runtime'),str(exe),str(os.getpid())],stdin=sp.PIPE,stdout=sp.PIPE,stderr=sp.PIPE,text=True,creationflags=sp.CREATE_NO_WINDOW)
 row=json.loads(creator.stdout.readline());c=SceneChannel(row['name']);end=time.monotonic()+5
 try:
  while struct.unpack('<i',c.read(OFFSET+44,4))[0]!=1:
   if time.monotonic()>end:raise ValueError('Producer-death fixture readiness')
   time.sleep(.001)
  try:SceneChannel(row['name'],create=True)
  except ValueError:pass
  else:raise AssertionError('Live session mapping reused')
  k=C.WinDLL('kernel32',use_last_error=True)
  k.OpenProcess.argtypes=[C.c_uint32,C.c_int,C.c_uint32];k.OpenProcess.restype=C.c_void_p
  k.WaitForSingleObject.argtypes=[C.c_void_p,C.c_uint32]
  k.GetExitCodeProcess.argtypes=[C.c_void_p,C.POINTER(C.c_uint32)];k.CloseHandle.argtypes=[C.c_void_p]
  h=k.OpenProcess(0x101000,False,row['pid']);assert h
  try:
   creator.communicate('exit\n',timeout=5);assert creator.returncode==0
   assert k.WaitForSingleObject(h,5000)==0
   status=C.c_uint32();assert k.GetExitCodeProcess(h,C.byref(status)) and status.value==10
  finally:k.CloseHandle(h)
 finally:
  c.close()
  if creator.poll() is None:creator.terminate();creator.wait(timeout=5)

def run():
 results=[]
 for arch in ('x86','x64'):
  exe=ROOT/f'artifacts/player-replacement/startup-ticket/{arch}/startup_ticket_worker.exe'
  for case in ('normal','early','cancel_before','cancel_wait','incomplete','duplicate_host','game_exit'):
   game=sp.Popen([sys.executable,'-c','import time;time.sleep(20)'],creationflags=sp.CREATE_NO_WINDOW) if case=='game_exit' else None
   c=SceneChannel(create=True);pid=game.pid if game else os.getpid();initialize(c,pid);env=environment(c,pid);p=None
   try:
    if case=='early':activate(c,env,c.name)
    if case=='cancel_before':cancel(c)
    p=sp.Popen([str(exe)],env=env,stdout=sp.PIPE,stderr=sp.PIPE,creationflags=sp.CREATE_NO_WINDOW)
    if case!='cancel_before':wait_ready(c,p)
    if case=='duplicate_host':
     duplicate=sp.run([str(exe)],env=env,capture_output=True,timeout=5,creationflags=sp.CREATE_NO_WINDOW)
     assert duplicate.returncode==20
    if case in ('normal','duplicate_host'):activate(c,env,c.name)
    if case in ('cancel_wait','incomplete'):
     if case=='incomplete':C.c_int32.from_address(c.view+OFFSET+36).value=1
     time.sleep(.03);assert p.poll() is None;cancel(c)
    if case=='game_exit':game.terminate();game.wait(timeout=5)
    stdout,stderr=p.communicate(timeout=5)
    expected=10 if case in ('cancel_before','cancel_wait','incomplete','game_exit') else 0
    assert p.returncode==expected,(arch,case,p.returncode,stderr)
    if expected==0:
     assert struct.unpack('<i',c.read(OFFSET+36,4))[0]==3
     try:activate(c,env,c.name)
     except ValueError:pass
     else:raise AssertionError('Replay accepted')
    results.append(dict(arch=arch,case=case,exit=p.returncode))
   finally:
    if p and p.poll() is None:p.terminate();p.wait(timeout=5)
    if game and game.poll() is None:game.terminate();game.wait(timeout=5)
    c.close()
  producer_exit(exe);results.append(dict(arch=arch,case='producer_exit_and_live_mapping_reuse',exit=10))
  for field,offset in (('checksum',160),('session',80),('game',76)):
   c=SceneChannel(create=True);initialize(c,os.getpid());env=environment(c,os.getpid());activate(c,env,c.name)
   raw=bytearray(c.read(OFFSET+64,104));raw[offset-64]^=1
   if field!='checksum':raw[-8:]=struct.pack('<Q',fnv(raw[:-8]))
   c.write(OFFSET+64,bytes(raw))
   p=sp.run([str(exe)],env=env,capture_output=True,timeout=5,creationflags=sp.CREATE_NO_WINDOW)
   assert p.returncode==20 and struct.unpack('<i',c.read(OFFSET+36,4))[0]==5,(field,p.stderr)
   results.append(dict(arch=arch,case='reject_'+field,exit=p.returncode));c.close()
 folder=ROOT/'artifacts/player-replacement/run244';folder.mkdir(exist_ok=True)
 (folder/'startup-transport-tests.json').write_text(json.dumps(results,indent=2))
 print('Startup transport PASS',len(results),'actual consumer cases')
if __name__=='__main__':run()
