"""Standalone fresh-source registry -> UE additive capture -> real x86 GPU reader."""
import argparse,copy,ctypes as C,json,os,struct,subprocess,sys,time
from pathlib import Path
import numpy as np
from qualify_registry import ROOT,source_row,publish_frame,publish_state,runtime_exe
from qualify_stream import reference
for part in ("src/rendering/ue","src/rendering","src/transport","src/assets","src/runtime"):
    sys.path.insert(0,str(ROOT/part))
from scene_receiver import Receiver
from live_owner_timing import initialize
from owner_rebind import fnv
from runtime_context import CONTEXT
from native_output_service import AdditiveSourceService,additive_environment
import multi_scene as wire

def run(exe,scene,consumer,reader_exe,output,*,native_insertion=False):
    output=output.resolve();output.mkdir(parents=True,exist_ok=False)
    definition=json.loads(scene.read_text(encoding="utf-8-sig"));packet=ROOT/definition["source_packet"]
    mesh=packet.read_bytes();refs=packet.with_suffix(".json").read_bytes();header=struct.unpack_from("<64I",mesh)
    receiver=Receiver(retain_assets=False);service=None;native=None
    kernel=C.WinDLL("kernel32",use_last_error=True)
    kernel.CreateEventW.argtypes=[C.c_void_p,C.c_int,C.c_int,C.c_wchar_p];kernel.CreateEventW.restype=C.c_void_p
    kernel.WaitForSingleObject.argtypes=[C.c_void_p,C.c_uint32];kernel.CloseHandle.argtypes=[C.c_void_p]
    event_name=receiver.name+"-native-fixture-complete";event=kernel.CreateEventW(None,False,False,event_name)
    if not event:raise OSError(C.get_last_error(),"Fixture read event")
    try:
        c=receiver.channel;initialize(c,persistent=True);wire.initialize(c)
        c.write(12,struct.pack("<I",1));c.write(wire.OFFSET+12,struct.pack("<I",os.getpid()));c.write(10*1024*1024+28,struct.pack("<I",os.getpid()))
        revision=definition["asset"]["revision"];c.write(65536,mesh+refs);c.write(256,struct.pack("<6I",1,0,len(mesh),len(refs),header[4],revision))
        definition["source_binding"]=dict(pid=os.getpid(),model=header[10],source=header[12])
        words=[int(receiver.name[-32:][n:n+8],16) for n in range(0,32,8)]
        notice=struct.pack("<8IQ4IQ",0x31544754,1,64,os.getpid(),*words,1,513,289,1,1,0)
        c.write(4352,struct.pack("<I",1));c.write(4416,notice[:-8]+struct.pack("<Q",fnv(notice[:-8])));c.write(4352,struct.pack("<I",2))
        first=copy.deepcopy(definition["frames"][0]);second=copy.deepcopy(first);second["model"][0][3]+=24
        for pose in (first,second):pose["viewport"]=[13,9,499,277]
        offset=(-15.897722721099854,0,0)
        env={k:v for k,v in os.environ.items() if not k.startswith("SFC_")}
        env.update(SFC_REMIX_CALIBRATION_SCENE=receiver.name,SFC_D3D9_MULTISCENE="1")
        service=AdditiveSourceService(receiver,CONTEXT.game_root,os.getpid(),output/"service",runtime_exe(exe),
                                      consumer=consumer,world_offset=offset,environment=env)
        # Explicit standalone boundary, not a native gate or SFC claim.
        service.environment["SFC_NATIVE_INSERTION_GATE"]="0"
        args=service.arguments()+["-SFCDiagnostics",f"-SFCOutput={output}"]
        native=subprocess.Popen([str(reader_exe.resolve()),receiver.name,str(os.getpid()),str(output/"native"),"6",event_name]+(["--native-insertion"] if native_insertion else []),
                                stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        service.process=subprocess.Popen(args,env=service.environment,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        expected={};step=1
        def publish(index):
            pose=copy.deepcopy((first,second)[(index-1)%2]);row=source_row(definition,pose,100+index,200+index,0)
            publish_state(c,row,0);c.write(128,struct.pack("<I",1));publish_frame(c,[row],100+index,200+index,offered=1)
            expected[index]=pose
        publish(step);deadline=time.monotonic()+60
        while native.poll() is None:
            if time.monotonic()>deadline:raise TimeoutError("Live UE output fixture timed out")
            if service.process.poll() is not None:
                detail=(output/"rejected.txt").read_text(encoding="utf-8-sig") if (output/"rejected.txt").exists() else str(service.process.returncode)
                raise RuntimeError("UE live output: "+detail)
            service.poll()
            if step<6 and kernel.WaitForSingleObject(event,0)==0:step+=1;publish(step)
            time.sleep(.001)
        text=native.communicate()[0].decode(errors="replace")
        if native.returncode:raise RuntimeError(text)
        service.stop()
        if service.process.returncode:raise ValueError("UE live output did not exit normally")
        fresh_path=next(service.publisher.folder.glob("*.json"));fresh=json.loads(fresh_path.read_text(encoding="utf-8-sig"))
        for key in ("positions","corners","indices"):
            if fresh[key]!=definition[key]:raise ValueError("Neutral arrays/UVs were modified")
        checks=[];images=[]
        for index in (1,2,5,6):
            record=(output/"native"/f"{index}.packet").read_bytes();meta=(output/"native"/f"{index}.metadata").read_bytes()
            if struct.unpack_from("<Q",record,40)[0]!=100+index or struct.unpack_from("<Q",meta)[0]!=200+index:raise ValueError("Native output source identity mismatch")
            colour=np.fromfile(output/"native"/f"{index}-0.raw",np.uint8).reshape(289,513,4)
            depth=np.fromfile(output/"native"/f"{index}-1.raw",np.float32).reshape(289,513)
            owners=np.fromfile(output/"native"/f"{index}-2.raw",np.uint32).reshape(289,513)
            source=copy.deepcopy(fresh);pose=copy.deepcopy(expected[index])
            for a in range(3):pose["model"][a][3]+=offset[a]
            source["frames"]=[pose]
            rgb,covered,interior,z=reference(source,fresh_path.parent,include_depth=True)
            area=np.s_[9:286,13:512];stable=covered&interior
            errors=np.max(np.abs(colour[area][:,:,2::-1].astype(np.int16)-rgb.astype(np.int16)),axis=2)
            accurate=float(np.mean(errors[stable]<=3));z_error=float(np.quantile(np.abs(depth[area][stable]-z[stable]),.995))
            if accurate<.97 or z_error>1e-4 or np.mean(owners[area][stable]==header[4])<.999:raise ValueError(f"Live output pixels/depth/owner mismatch: {accurate}, {z_error}")
            checks.append(dict(output=index,source_frame=100+index,colour_within_three=accurate,depth_error_p995=z_error));images.append(colour)
        if not np.array_equal(images[0],images[2]) or not np.array_equal(images[1],images[3]) or np.sum(np.any(images[0]!=images[1],axis=2))<20:
            raise ValueError("Live output is stale or source poses were not deterministic")
        result=dict(scope="Actual fresh source/retained registry/additive component/export/native pool; optional standalone native composition, no SFC hooks",checks=checks,
                    native_insertion=native_insertion,native_log=text,world_offset=list(offset),original_geometry_uvs_unchanged=True,original_suppressed=False,summary=service.summary())
        (output/"qualified.json").write_text(json.dumps(result,indent=2));return result
    except Exception as exc:
        (output/"failure.json").write_text(json.dumps(dict(error=str(exc),step=locals().get("step")),indent=2));raise
    finally:
        if service:service.stop()
        if native is not None and native.poll() is None:native.terminate();native.wait(timeout=5)
        receiver.close();kernel.CloseHandle(event)

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    for k in ("exe","scene","consumer","reader","output"):p.add_argument(k,type=Path)
    p.add_argument("--native-insertion",action="store_true")
    a=p.parse_args();print(json.dumps(run(a.exe,a.scene,a.consumer,a.reader,a.output,native_insertion=a.native_insertion),indent=2))
