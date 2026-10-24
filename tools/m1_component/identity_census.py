"""Bounded post-stop identity evidence;never assigns or repairs game ownership."""
import hashlib
import json
from pathlib import Path

COLUMNS=('kind','caller','ship','visual','model','source','chosen_owner','context_ship',
         'context_visual','context_owner','ship_owner','context_ship_owner','visual_first_owner',
         'visual_owner_count','reason','ship_vtable','visual_vtable','model_vtable','thread')


def analyze(data):
    if data.get('schema')!='m1.identity-census.v1' or data.get('capacity')!=256 or data.get('columns')!=list(COLUMNS):
        raise ValueError('Identity census schema/columns/capacity')
    entries=data.get('entries');total=data.get('observations');omitted=data.get('omitted_observations');storage=data.get('storage_bytes')
    if (not isinstance(entries,list) or len(entries)>256 or type(total) is not int or type(omitted) is not int
            or not 0<=omitted<=total or type(storage) is not int or not 0<storage<32768 or type(data.get('enabled')) is not bool):
        raise ValueError('Identity census bounds/counters')
    tuples=set();observations=0;ships={};mismatches=[];unqualified=0;first=None;last=None
    for e in entries:
        key=e.get('key')
        if not isinstance(key,list) or len(key)!=19 or any(type(x) is not int or not 0<=x<=0xffffffff for x in key):
            raise ValueError('Identity census tuple')
        if tuple(key) in tuples:raise ValueError('Duplicate census tuple')
        tuples.add(tuple(key));row=dict(zip(COLUMNS,key));count=e.get('observations')
        for f in ('first_frame','last_frame','first_ms','last_ms'):
            if type(e.get(f)) is not int or not 0<=e[f]<=0xffffffff:raise ValueError('Identity census timestamp')
        if (type(count) is not int or not 0<count<=total or e['first_frame']>e['last_frame'] or e['first_ms']>e['last_ms']
                or row['kind'] not in (1,2,3,6,9) or row['reason']>12 or row['visual_owner_count']>32):
            raise ValueError('Identity census event/range')
        observations+=count;first=e['first_ms'] if first is None else min(first,e['first_ms']);last=e['last_ms'] if last is None else max(last,e['last_ms'])
        if row['kind']==1 and not row['reason'] and row['chosen_owner'] and row['ship'] and row['visual']:
            ships.setdefault(row['visual'],set()).add((row['chosen_owner'],row['ship']))
        if row['kind']==3:
            contextual=(row['context_ship_owner'] and row['context_owner']==row['context_ship_owner']
                        and row['context_visual']==row['visual'])
            if not contextual:unqualified+=count
            elif row['chosen_owner']!=row['context_ship_owner']:
                mismatches.append(dict(frame=e['first_frame'],elapsed_ms=e['first_ms'],observations=count,
                    context_owner=row['context_ship_owner'],chosen_owner=row['chosen_owner'],context_ship=row['context_ship'],
                    visual=row['visual'],model=row['model'],source=row['source'],reason=row['reason']))
    if observations+omitted!=total or (not data['enabled'] and total):raise ValueError('Identity census accounting')
    shared=[dict(visual=v,owners=[dict(owner=o,ship=s) for o,s in sorted(values)]) for v,values in sorted(ships.items()) if len({s for _,s in values})>1]
    return dict(result='IDENTITY_CENSUS_PARTIAL' if omitted else 'IDENTITY_CENSUS_OBSERVATIONS_READY' if data['enabled'] else 'IDENTITY_CENSUS_INACTIVE',
        enabled=data['enabled'],unique_tuples=len(entries),observations=total,omitted_observations=omitted,
        first_ms=first,last_ms=last,native_ship_epoch_pairs=len({pair for values in ships.values() for pair in values}),
        shared_visuals=shared,context_choice_mismatches=mismatches,model_observations_without_qualified_context=unqualified,
        scope='Observed native associations and existing choices;no ownership correction or complete simulation census claim')


def analyze_summary(path):
    path=Path(path)
    if path.stat().st_size>1024*1024:raise ValueError('Native summary1MiB analysis cap')
    raw=path.read_bytes();data=json.loads(raw)
    report=analyze(data['identity_census']);report['summary_sha256']=hashlib.sha256(raw).hexdigest();return report
