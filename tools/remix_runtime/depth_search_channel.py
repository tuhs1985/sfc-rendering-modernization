"""Fixed expanded-search metadata. No external pointer dereference or images."""
import ctypes as C

MAGIC=0x53445031
PHASES=('scene_begin','scene_end_pre_flush','scene_end_post_flush',
        'engine_present','dxgi_present','overlay')
class Counts(C.Structure):
    _fields_=[(n,C.c_int32) for n in ('calls','noContext','wrongThread','missing','found','invalid','busy')]+[('lastTick',C.c_uint32)]
class Resource(C.Structure):
    _fields_=[(n,C.c_uint32) for n in ('epoch','resourceLabel','viewLabel','width','height','format','viewFormat','flags','samples','phaseMask','firstTick','lastTick','observations')]+[('reserved',C.c_uint32*3)]
class Data(C.Structure):
    _fields_=[(n,C.c_uint32) for n in ('magic','version','bytes','capacity')]+[(n,C.c_int32) for n in ('status','installedMask','restoredMask','error','resourceCount','overflow')]+[(n,C.c_uint32) for n in ('contextThread','epoch','startTick','endTick')]+[(n,C.c_int32) for n in ('seenMask','reserved')]+[('phases',Counts*6),('resources',Resource*32)]
assert C.sizeof(Data)==2304 and C.sizeof(Resource)==64
def snapshot(address):
    # Copy fixed metadata before parsing; counts are live/approximate until stop.
    s=Data.from_buffer_copy(C.string_at(address+256,C.sizeof(Data)))
    if (s.magic,s.version,s.bytes,s.capacity)!=(MAGIC,1,C.sizeof(Data),32):
        raise ValueError('Expanded-search header mismatch')
    if not 0<=s.resourceCount<=32:raise ValueError('Expanded-search table size invalid')
    out={n:int(getattr(s,n)) for n,_ in Data._fields_ if n not in ('phases','resources')}
    out['phases']={name:{n:int(getattr(s.phases[i],n)) for n,_ in Counts._fields_ if n!='reserved'} for i,name in enumerate(PHASES)}
    out['resources']=[{n:int(getattr(s.resources[i],n)) for n,_ in Resource._fields_ if n!='reserved'} for i in range(s.resourceCount)]
    out['captureWindowMs']=((s.endTick-s.startTick)&0xFFFFFFFF) if s.endTick and s.startTick else None
    return out
def verdict(s):
    if s['error'] or s['status']!=4 or s['restoredMask']!=15:return 'PARTIAL_CLEANUP_OR_HOOK_ERROR'
    if any(not p['calls'] for p in s['phases'].values()):return 'PARTIAL_UNOBSERVED_PHASE'
    if any(p['wrongThread'] or p['noContext'] or p['invalid'] or p['busy'] for p in s['phases'].values()) or s['overflow']:return 'PARTIAL_COVERAGE_LIMIT'
    if s['endTick'] and any(not p['lastTick'] or ((s['endTick']-p['lastTick'])&0xFFFFFFFF)>2000 for p in s['phases'].values()):return 'PARTIAL_PHASE_NOT_ACTIVE_NEAR_STOP'
    return 'DEPTH_DESCRIPTORS_FOUND_UNQUALIFIED' if s['resourceCount'] else 'NO_BOUND_DSV_AT_SIX_ENGINE_PRESENTATION_PHASES'
