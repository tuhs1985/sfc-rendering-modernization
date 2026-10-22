"""Owned synthetic memory process ONLY;never imports/starts SFC."""
import ctypes as C
import json
import struct
import sys

def main():
    k=C.WinDLL('kernel32',use_last_error=True)
    k.VirtualAlloc.argtypes=[C.c_void_p,C.c_size_t,C.c_ulong,C.c_ulong];k.VirtualAlloc.restype=C.c_void_p
    ship=0x20000000;visual=ship+0x1000;model=ship+0x2000
    if k.VirtualAlloc(ship,0x4000,0x3000,4)!=ship or k.VirtualAlloc(0x00C70000,0x10000,0x3000,4)!=0x00C70000:
        raise RuntimeError('Synthetic fixture low-address allocation failed')
    def put(address,raw):C.memmove(address,raw,len(raw))
    def word(address,value):put(address,struct.pack('<I',value))
    def matrix(address,pos=0):
        words=[0.0]*16
        for i in (0,5,10,15):words[i]=1
        words[3]=pos;put(address,struct.pack('<16fI',*words,0x100))
    word(ship,0x00796F0C);word(ship+0x88,visual);word(visual,0x007985A4);word(model,0x007983E8)
    matrix(ship+0x98);matrix(ship+0x980);matrix(ship+0x9C4)
    position=0.0;tick=1
    put(ship+0xE6,struct.pack('<3f',position,200,0));word(0x00C7C140,tick)
    print(json.dumps(dict(ship=ship,visual=visual,model=model)),flush=True)
    for line in sys.stdin:
        command=line.strip()
        if command=='exit':break
        if command=='move':
            position+=1;put(ship+0xE6,struct.pack('<3f',position,200,0));tick+=1;word(0x00C7C140,tick)
        elif command=='render':matrix(ship+0x9C4,position)
        elif command=='reuse':word(ship,0)
        elif command=='nan':put(ship+0xE6,struct.pack('<f',float('nan')))
        else:raise ValueError('Unknown fixture command')
        print('OK',flush=True)

if __name__=='__main__':main()
