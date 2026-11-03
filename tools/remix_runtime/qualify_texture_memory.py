"""Real cross-process native texture consumer; no SFC, GPU or texture files."""
import argparse
import json
import struct
import subprocess as sp
import sys
import uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/remix_ingest'),str(ROOT/'tools/d3d9_proof')]
from texture_memory import Pool
from multi_scene import asset_packet,ASSET
from owner_rebind import fnv


def main():
    parser=argparse.ArgumentParser();parser.add_argument('probe',type=Path);parser.add_argument('--report',type=Path,required=True);args=parser.parse_args()
    session='Local\\SFCBridge_'+uuid.uuid4().hex;pool=Pool(session);results=[]
    images=[struct.pack('<4I',0x31544653,3,2,24)+bytes(range(24)),struct.pack('<4I',0x31544653,1,1,4)+b'\xff\x00\x80\xff']
    row=[0]*96
    for i in (1,5,6,7):row[i]=i
    packet=asset_packet(1,1,row,'ab'*32,b'geometry',images)
    def check(label,expected,raw=packet,count=2,session_hex=None):
        result=sp.run([str(args.probe.resolve()),session_hex or session[-32:],raw.hex(),str(count)],capture_output=True,text=True,timeout=10,creationflags=sp.CREATE_NO_WINDOW)
        assert (result.returncode==0)==expected,(label,result.stdout,result.stderr)
        results.append(dict(case=label,accepted=expected,result=result.stdout.strip() or result.stderr.strip()))
    def altered(index,value):
        fields=list(ASSET.unpack(packet));fields[index]=value;raw=ASSET.pack(*fields)
        return raw[:-8]+struct.pack('<Q',fnv(raw[:-8]))
    try:
        check('missing mapping',False)
        pool.reserve(1,list(map(len,images)),8)
        pool.write_geometry(1,b'geometry')
        for i,image in enumerate(images):pool.write(1,i,image)
        check('unsealed mapping',False)
        pool.seal(1,packet);entry=pool.entries[1];mapping=entry['mapping']
        check('exact bytes with no texture files',True)
        geometry=mapping.read(2176,8);mapping.write(2176,b'corrupt!');check('corrupt geometry',False);mapping.write(2176,geometry)
        mapping.write(4,struct.pack('<I',1));check('old mapping version',False);mapping.write(4,struct.pack('<I',2))
        check('completion-order path reassignment',True,altered(1,2))
        for label,index,value in [('owner',2,99),('revision',3,99),('model',4,99),('source',5,99),('content',8,b'\xcd'*32),('geometry',9,123),('textures hash',10,123)]:
            check('wrong '+label,False,altered(index,value))
        check('wrong session',False,session_hex=uuid.uuid4().hex)
        check('wrong image count',False,count=1)
        original=mapping.read(128,8);mapping.write(128,struct.pack('<2I',2175,40));check('overlapping table',False);mapping.write(128,original)
        offset=entry['table'][0][0];pixel=mapping.read(offset+16,1);mapping.write(offset+16,b'\xff');check('corrupt pixels',False);mapping.write(offset+16,pixel)
        mapping.write(offset+4,struct.pack('<I',4097));check('oversize dimensions',False);mapping.write(offset+4,struct.pack('<I',3))
        check('restored exact bytes',True)
        pool.release(1);check('acknowledged mapping removed',False)
        pool.close()
        try:pool.reserve(1,list(map(len,images)))
        except ValueError:results.append(dict(case='shutdown rejects new reservation',accepted=False))
        else:raise AssertionError('Closed pool accepted reservation')
    finally:pool.close()
    args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(dict(cases=results,texture_files_created=0,peak_bytes=pool.peak),indent=2))
    print('Texture memory PASS',len(results),'real consumer cases')


if __name__=='__main__':main()
