"""Exact-build, read-only camera/projection/viewport anchors. No patch/hook list."""
import argparse
import json
from pathlib import Path
import verify_m1_c01_shading_bytes as engine

ANCHORS={
    0x007B8D8C:'00 A0 6A 00', # viewport setter
    0x007B8D90:'80 A0 6A 00', # viewport getter
    0x007B8E24:'A0 A4 6A 00', # view setter
    0x007B8E28:'D0 A4 6A 00', # view getter
    0x007B8E38:'F0 A3 6A 00', # projection setter
    0x007B8E3C:'90 A4 6A 00', # projection getter
    0x007B8E4C:'E0 A0 6A 00', # perspective builder
    0x006AA004:'D9 91 5C 07 00 00',
    0x006AA018:'D9 91 64 07 00 00',
    0x006AA032:'D9 99 6C 07 00 00',
    0x006AA042:'D9 99 70 07 00 00',
    0x006AA3F8:'8D 93 5C 05 00 00',
    0x006AA406:'F3 A5',
    0x006AA408:'8D B3 A0 05 00 00',
    0x006AA43F:'D9 E0',
    0x006AA470:'E8 DB 0F FF FF',
    0x006AA475:'8D 93 28 06 00 00',
    0x006AA47B:'81 C3 E4 05 00 00',
    0x006AA485:'E8 66 16 FF FF',
    0x006AA4A8:'8D 90 28 06 00 00',
    0x006AA4B8:'8D 88 E4 05 00 00',
    0x006AA4BF:'8D 88 A0 05 00 00',
    0x006AA4C5:'E8 26 16 FF FF',
    0x006AA570:'F3 A5',
    0x006AA57C:'E8 6F 15 FF FF',
    0x006AA58F:'E8 5C 15 FF FF',
    0x0069BAF0:'A1 F4 9F C6 00',
    0x0069CA95:'8A 59 41',
    0x0069CAA7:'D9 41 38',
    0x006AC2C9:'8D 8F B0 06 00 00',
    0x006AB5BA:'D8 70 10',
    0x006AB5C7:'D8 48 04',
    0x006AB5CF:'D8 48 08',
    0x006AB5D7:'D8 48 0C',
    0x007959C8:'00 00 00 3F', # .5
    0x007959CC:'00 00 80 3F', # 1
}


def verify(client):
    # Reuse exact hash/PE bounds checks without changing their normal anchor set.
    original=engine.ANCHORS
    try:
        engine.ANCHORS=ANCHORS
        result=engine.verify(Path(client))
    finally:engine.ANCHORS=original
    result['scope']='Camera-path static byte anchors; interpretation supported separately by inspected instructions and runtime algebra'
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('client',type=Path);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();result=verify(args.client)
    with args.output.open('x') as out:json.dump(result,out,indent=2);out.write('\n')
    print(len(result['anchors']),result['result'])
