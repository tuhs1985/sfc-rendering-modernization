#!/usr/bin/env python3
"""Print selected address ranges from dumpbin disassembly without copying the full file."""
import argparse, re
from pathlib import Path

ADDRESS_RE=re.compile(r"^\s*([0-9A-F]{8}):",re.I)

def number(value):
    return int(value,0)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("disassembly",type=Path)
    parser.add_argument("ranges",nargs="+",help="start:end addresses")
    args=parser.parse_args()
    ranges=[]
    for value in args.ranges:
        start,end=value.split(":",1); ranges.append((number(start),number(end)))
    for raw in args.disassembly.read_text(errors="replace").splitlines():
        match=ADDRESS_RE.match(raw)
        if match and any(start<=int(match.group(1),16)<=end for start,end in ranges):
            print(raw)

if __name__=="__main__": main()
