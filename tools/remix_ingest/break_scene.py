"""Dedicated decoder for qualified native indexed break-piece captures."""
import json
import struct
from pathlib import Path
from live_scene import _decode_mesh


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
    from live_scene import decode_mesh
    if allow_break and len(packet)>=256 and struct.unpack_from('<I',packet,13*4)[0]==0x0042EA92:
        return decode_runtime_piece(packet,references,checksum=checksum)
    return decode_mesh(packet,references,checksum=checksum)


def decode_piece(packet, references, handoff, observation):
    """Preserve native arrays and qualify the separate indexed-draw origin."""
    data = _decode_mesh(packet, references, checksum=None, origin=0x0042EA92)
    h = data['header']
    if (not handoff.get('owner_epoch') or not handoff.get('asset_epoch')
            or not handoff.get('owner') or not observation.get('child')
            or observation.get('mesh_status') != 1
            or observation.get('references_status') != 1
            or not isinstance(observation.get('index'), int)
            or not 0 <= observation['index'] < observation.get('piece_count', 0)
            or observation.get('count') != h[17]
            or h[4] != handoff['owner_epoch'] or h[8] != observation['child']
            or h[9] != handoff.get('visual') or h[20:24] != (1, 0, 0, 0)):
        raise ValueError('Break-piece observation identity')
    name = data['refs'].get('model_filename', '').replace('\\', '/')
    if (name.lower() != handoff.get('model', '').replace('\\', '/').lower()
            or not name.lower().endswith('_brk.mod')):
        raise ValueError('Break visual resource identity')
    data['piece'] = dict(index=observation['index'], first=observation['first'],
                         count=observation['count'], child=observation['child'],
                         parent_owner_epoch=handoff['owner_epoch'],
                         visual_epoch=handoff['asset_epoch'])
    data['source_kind']='break_piece'
    return data


def decode_capture(folder):
    """Offline handoff to scene preparation, without changing normal admission."""
    folder = Path(folder)
    result = json.loads((folder / 'result.json').read_text())
    report = result['report']
    if (report.get('issues') or not report.get('finalized')
            or report.get('restored') not in ([0, 0, 14, 0], [0, 0, 16, 0])):
        raise ValueError('Break capture integrity is incomplete')
    observations = report['geometry']
    if not 1 <= len(observations) <= 4:
        raise ValueError('Diagnostic break snapshot capacity')
    pieces, slots, children = {}, set(), set()
    for observation in observations:
        slot = observation['slot']
        if (type(slot) is not int or not 0 <= slot < 4 or slot in slots
                or observation['index'] in pieces or observation['child'] in children):
            raise ValueError('Duplicate break capture identity')
        packet = (folder / f'break-piece-{slot}.bin').read_bytes()
        refs = (folder / f'break-piece-{slot}.json').read_bytes()
        pieces[observation['index']] = decode_piece(packet, refs, report['handoff'], observation)
        slots.add(slot)
        children.add(observation['child'])
    total = len(pieces)
    if set(pieces) != set(range(total)) or any(row['piece_count'] != total for row in observations):
        raise ValueError('Incomplete break model')
    first = 0
    points = pieces[0]['points']
    for index in range(total):
        piece = pieces[index]
        if piece['piece']['first'] != first or piece['points'] != points:
            raise ValueError('Break partition continuity or shared positions')
        first += piece['piece']['count']
    return dict(handoff=report['handoff'], pieces=pieces, triangles=first,
                points=points, poses=report['pieces'])
