"""Read-only verification of the Run167 effects/resource anchors in client2.5.6.4.

Checks only explicit addresses; no model/image contents or executable mutation.
Static reachability is not evidence that a particular runtime instance took a branch.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path
from inspect_pe import inspect

CLIENT='4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29'

class Image:
    def __init__(self,path):
        self.meta=inspect(path)
        self.data=path.read_bytes()
        self.base=int(self.meta['image_base'],16)
        if hashlib.sha256(self.data).hexdigest().upper()!=CLIENT:raise ValueError('Client hash mismatch')

    def read(self,address,size):
        if not 0<size<=256:raise ValueError('Explicit read bound')
        rva=address-self.base
        for section in self.meta['sections']:
            offset=rva-section['rva']
            if 0<=offset and offset+size<=section['raw_size']:
                start=section['raw_offset']+offset
                return self.data[start:start+size]
        raise ValueError('Address outside file-backed section')

def verify(path):
    image=Image(path);checks=[]
    def exact(address,expected,label):
        if image.read(address,len(expected))!=expected:raise ValueError(f'Anchor mismatch {address:08X}: {label}')
        checks.append(dict(address=f'0x{address:08X}',label=label,expected_hex=expected.hex().upper()))
    def words(address,values,label):exact(address,struct.pack('<'+'I'*len(values),*values),label)
    def code(address,value,label):exact(address,bytes.fromhex(value),label)
    def string(address,value):exact(address,value.encode('ascii')+b'\0',value)

    words(0x007AA050,[0x004EF160,0x004EFA4A],'Concrete list-object vtable: destroy and draw')
    code(0x004EF0CE,'E8 9F DC FF FF','Constructor calls global-list insertion')
    code(0x004EF0DC,'C7 06 50 A0 7A 00','Constructor installs concrete vtable')
    code(0x004EF0D7,'68 C0 78 85 00','Constructor selects missile-model name')
    string(0x008578C0,'assets/models/missile/missile.mod')
    code(0x004ED07D,'FF 50 04','Global-list dispatch uses draw slot+4')
    code(0x004ECE2C,'BF FC F5 92 00','Texture initialization destination ID table')
    words(0x007A9818,[0x0085775C,0,0],'First texture initializer entry')
    string(0x0085775C,'fx0')
    string(0x00857774,'assets/textures/%s.%s')
    string(0x0083EB78,'bmp');string(0x0083EB74,'pcx')
    code(0x004ECEB4,'8B 0D 20 C6 8C 00','Resource lookup uses established registry')
    code(0x004ECECE,'FF 50 08','Resource acquire slot+8')
    code(0x004ECE44,'89 07','Initializer stores acquired ID')
    code(0x004ECF56,'FF 52 04','Shutdown releases texture ID through registry')
    code(0x004EFC8F,'FF 35 FC F5 92 00','Draw selects live fx0 resource ID')
    code(0x004EFC97,'FF 90 34 01 00 00','Draw calls manager resource-selection slot+134')
    words(0x007B8D4C+0x134,[0x006AD3E0],'Manager resource-selection implementation')
    code(0x006AD3F8,'89 81 24 1F 00 00','Resource ID stored in manager+1F24')
    code(0x006AC90F,'8B 9E 24 1F 00 00','Primitive finalizer reads selected resource ID')
    code(0x004EFCFA,'FF 90 0C 01 00 00','Draw begins native primitive mode7')
    code(0x004EFCF6,'6A 07','Primitive mode7 argument')
    words(0x006AD0FC+7*4,[0x006ACE58],'Mode7 dispatch selects four-corner finalizer')
    code(0x006ACE8A,'E8 A1 F9 FF FF','Four-corner finalizer calls existing polygon submitter')
    code(0x004EFD00,'8B 46 44','Owner+44 selects UV variant')
    code(0x004EFD12,'D9 80 F8 39 93 00','UV coordinate table source')
    code(0x004EFE48,'FF 90 10 01 00 00','Draw ends native primitive batch')
    words(0x007B8D4C+0x110,[0x006AC810],'End implementation')
    code(0x006AC815,'E8 E6 00 00 00','End invokes finalizer')
    code(0x004ECD78,'C7 00 70 98 7A 00','Global-list base constructor')
    code(0x004ECDA9,'A3 70 F4 92 00','List insertion publishes head')
    code(0x004ECDFA,'A3 70 F4 92 00','List unlink updates head')
    code(0x00410438,'FF 50 08','Attached trait dispatch slot+8, not a fixed class')
    code(0x00410454,'FF 50 0C','Separate attached trait slot+0C dispatch')
    code(0x0041E078,'C7 06 FC 78 79 00','Explosion-related constructor vtable')
    words(0x007978FC+8,[0x0041F5F5,0x00413AC3],'Separate attached update/model-render slots')
    string(0x0083D714,'tETrait_Explosion')
    return dict(probe='EFFECT-RESOURCE-JOIN-001',mode='STATIC_ONLY',client_sha256=CLIENT,
                checks=checks,check_count=len(checks),result='PASS',
                limits=['No runtime owner/resource instance join proved','No image contents or geometry captured',
                        'Shared fx0 does not identify one semantic effect','No explosion timestamp inferred'])

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('client',type=Path)
    print(json.dumps(verify(parser.parse_args().client),indent=2))
