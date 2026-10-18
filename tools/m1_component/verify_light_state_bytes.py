"""Read-only exact-build lighting anchors; no process access, hooks or patches."""
import argparse
import json
from pathlib import Path
import verify_m1_c01_shading_bytes as engine

ANCHORS={
    0x007B8DC8:'A0 9A 6A 00', # manager+7C capacity
    0x007B8DCC:'B0 9A 6A 00', # manager+80 record setter
    0x007B8DD0:'A0 9B 6A 00', # manager+84 record getter
    0x007B8DDC:'20 9C 6A 00', # manager+90 global response gate setter
    0x007B8DE4:'40 9C 6A 00', # manager+98 slot enable setter
    0x006A9AA0:'B8 40 00 00 00',
    0x006A9AC1:'C1 E0 06',
    0x006A9ACD:'89 BA 78 07 00 00',
    0x006A9AF1:'89 BA 88 07 00 00',
    0x006A9B0C:'89 BA 94 07 00 00',
    0x006A9B27:'89 BA A0 07 00 00',
    0x006A9B54:'89 BA B4 07 00 00',
    0x006A9B85:'D8 B2 A0 07 00 00',
    0x006A9B8B:'D9 9C B1 B8 1D 00 00',
    0x006A9BB3:'8D 84 08 78 07 00 00',
    0x006A9C2A:'88 91 B8 1E 00 00',
    0x006A9C4D:'88 94 08 78 17 00 00',
    0x006AA61A:'8D B3 88 07 00 00',
    0x006AA624:'8A 8C 03 78 17 00 00',
    0x006AA649:'E8 72 25 FF FF',
    0x006AA657:'E8 E4 25 FF FF',
    0x006AA674:'E8 C7 25 FF FF',
    0x006AA681:'83 C6 40',
    0x006A97BF:'8D A9 B8 1D 00 00',
    0x006A97C5:'8D B9 A0 07 00 00',
    0x006A97CB:'8D B1 C0 17 00 00',
    0x006A97DB:'8A 94 01 78 17 00 00',
    0x006A97E4:'0F 84 24 02 00 00', # first inactive terminates response loop
    0x006A97F6:'FF 24 85 7C 9A 6A 00',
    0x006A9A7C:'FD 97 6A 00 16 98 6A 00 CB 99 6A 00 CB 99 6A 00 CB 99 6A 00 F3 98 6A 00 CB 99 6A 00',
    0x006AA698:'3F A6 6A 00 50 A6 6A 00 3F A6 6A 00 50 A6 6A 00 3F A6 6A 00 50 A6 6A 00',
    0x006A9802:'8D 8E F8 02 00 00',
    0x006A980D:'D8 0F D9 E0',
    0x006A9833:'D8 66 F8',
    0x006A9896:'E8 F5 18 FF FF',
    0x006A98C6:'D8 2D CC 59 79 00',
    0x006A99DD:'8D 4F F4',
    0x006A99E0:'E8 8B 18 FF FF',
    0x006A99EE:'E8 6D 17 FF FF',
    0x006A99FE:'83 C7 40',
    0x006A9A01:'83 F8 40',
}

def verify(client):
    previous=engine.ANCHORS
    try:
        engine.ANCHORS=ANCHORS
        result=engine.verify(Path(client))
    finally:engine.ANCHORS=previous
    result['scope']='Static light bank/setter/transform/response anchors only; active scene lights not sampled'
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('client',type=Path)
    p.add_argument('--output',type=Path);a=p.parse_args();r=verify(a.client)
    if a.output:
        with a.output.open('x') as f:json.dump(r,f,indent=2);f.write('\n')
    print(json.dumps(r,indent=2) if not a.output else f"{len(r['anchors'])} STATIC_PREFIXES_MATCH")
