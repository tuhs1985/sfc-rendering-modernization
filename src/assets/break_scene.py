"""Dedicated decoder for qualified native indexed break-piece captures."""
import json
import struct
from pathlib import Path
from mesh_decode import _decode_mesh


def decode_runtime_piece(packet,references,*,checksum=None):
    """Dedicated live admission. Native child/partition evidence is mandatory."""
    data=_decode_mesh(packet,references,checksum=checksum,origin=0x0042EA92)
    h=data['header'];meta=data['refs'].get('break_piece')
    required={'schema','owner_epoch','parent_owner_epoch','index','piece_count','first','count','total','primary_base'}
    if not isinstance(meta,dict) or set(meta)!=required or meta['schema']!='sfc.break.piece.v1':
        raise ValueError('Fresh break partition evidence missing')
    if any(type(meta[k]) is not int or not 0<=meta[k]<=0xffffffff for k in required-{'schema'}):
        raise ValueError('Fresh break partition word')
    owner=meta['owner_epoch'];parent=meta['parent_owner_epoch']
    if (not owner&0x80000000 or owner!=h[4] or not parent or parent&0x80000000 or
            not 1<=meta['piece_count']<=256 or meta['index']>=meta['piece_count'] or
            not 0<=meta['first']<meta['total']<=8192 or meta['count']!=h[17] or
            meta['count']>meta['total']-meta['first'] or not meta['primary_base'] or
            meta['primary_base']+meta['first']*4!=h[14] or h[20:24]!=(1,0,0,0) or
            not h[8]):
        raise ValueError('Fresh break partition identity/range')
    if not data['refs']['model_filename'].replace('\\','/').lower().endswith('_brk.mod'):
        raise ValueError('Fresh break model filename')
    data['piece']=dict(meta,child=h[8]);data['source_kind']='break_piece'
    return data


def decode_runtime_mesh(packet,references,*,checksum=None,allow_break=False):
    from mesh_decode import decode_mesh
    if allow_break and len(packet)>=256 and struct.unpack_from('<I',packet,13*4)[0]==0x0042EA92:
        return decode_runtime_piece(packet,references,checksum=checksum)
    return decode_mesh(packet,references,checksum=checksum)






def __getattr__(name):
    if name not in {'decode_piece','decode_capture'}:raise AttributeError(name)
    from scene_bundle import _development_review
    return getattr(_development_review(),name)
