"""One editable rendering profile; section projections avoid unrelated rebuilds."""
from pathlib import Path
import json
import tomllib

DEFAULT=Path(__file__).parent/'config/rendering.toml'
EXAMPLE=DEFAULT.with_name('rendering.example.toml')
SECTIONS={'material','image','quality','remix'}


def parse(raw):
    if len(raw)>16384:raise ValueError('Rendering config16KiB limit')
    data=tomllib.loads(raw.decode('utf-8'))
    if set(data)-SECTIONS:raise ValueError('Unknown rendering section')
    if any(not isinstance(value,dict) for value in data.values()):raise ValueError('Rendering sections must be tables')
    return data


def section(raw,name):
    return parse(raw).get(name,{})


def scoped(raw,*names):
    """Stable TOML for just the relevant controls,not a second editable profile."""
    data=parse(raw);lines=[]
    for name in names:
        if name not in SECTIONS:raise ValueError('Unknown projection section')
        if name not in data:continue
        lines.append('['+name+']')
        for key,value in sorted(data[name].items()):
            if type(value) not in (bool,int,float,str):raise ValueError('Rendering values must be scalar')
            text=('true' if value else 'false') if type(value) is bool else json.dumps(value) if isinstance(value,str) else repr(value).lower()
            lines.append(json.dumps(key)+' = '+text)
    return ('\n'.join(lines)+'\n').encode('utf-8')
