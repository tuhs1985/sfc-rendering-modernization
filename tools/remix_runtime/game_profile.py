"""Read the SFC and dgVoodoo settings needed by the graphics integration."""
import hashlib
import re

SIZES=((1024,768),(1280,720),(1366,768),(1440,900),(1600,900),(1920,1080))
D3D11_BACKENDS = (b'd3d11_fl10_1', b'd3d11_fl11_0', b'd3d11_fl11_1')


def canonical(raw, fields, *, insert_missing=False):
    if len(raw)>1024*1024:raise ValueError('Graphics settings exceed1MiB')
    section=b'';seen={};out=[];sections={}
    for line in raw.splitlines(keepends=True):
        text=line.strip()
        if text.startswith(b'[') and text.endswith(b']'):
            section=text[1:-1].strip().lower()
            sections[section]=len(out)+1
        match=re.fullmatch(rb'([ \t]*)([^=\r\n]+?)([ \t]*=[ \t]*)([^\r\n]*)(\r?\n)?',line)
        key=(section,match[2].strip().lower()) if match else None
        if key in fields:
            if key in seen:raise ValueError('Ambiguous graphics dimension setting')
            seen[key]=match[4].strip()
            out.append(match[1]+match[2]+match[3]+fields[key]+(match[5] or b''))
        else:out.append(line)
    missing = [(section, key, value) for (section, key), value in fields.items() if (section, key) not in seen]
    if missing:
        if not insert_missing:
            raise ValueError('Missing graphics dimension setting')
        newline = b'\r\n' if b'\r\n' in raw else b'\n'
        for section, key, value in reversed(missing):
            index = sections.get(section)
            if index is None:
                index = len(out)+1
                out.append(newline+b'['+section+b']'+newline)
            entry = key+b'='+value+newline
            if not out[index-1].endswith(b'\n'):
                entry = newline+entry
            out.insert(index, entry)
            sections = {name: offset+(offset>index) for name, offset in sections.items()}
            sections[section] = index
    return b''.join(out),seen


def sfc_profile(raw):
    from copied_preferences import protected_ini_sha256
    native,values=canonical(raw,{(b'3d',b'width'):b'<width>',(b'3d',b'height'):b'<height>'})
    try:size=tuple(int(values[b'3d',k]) for k in (b'width',b'height'))
    except ValueError as exc:raise ValueError('Invalid native dimensions') from exc
    if size not in SIZES:raise ValueError('Unsupported SFC alpha resolution')
    return protected_ini_sha256(native),size


def wrapper_profile(raw):
    graphics,values=canonical(raw,{(b'generalext',b'desktopresolution'):b'<desktop>',(b'directx',b'resolution'):b'<output>'})
    return hashlib.sha256(graphics).hexdigest().upper(),values[b'generalext',b'desktopresolution'],values[b'directx',b'resolution']


def prepare_wrapper(raw, size):
    """Derive the insertion profile from the copy's configured SFC resolution."""
    width, height = size
    backend = (b'general', b'outputapi')
    adapter = (b'general', b'adapters')
    fields = {
        backend: D3D11_BACKENDS[0],
        adapter: b'all',
        (b'generalext', b'desktopresolution'): f'{width}x{height}'.encode(),
        (b'directx', b'resolution'): f'h:{width}, v:{height}'.encode(),
        (b'directx', b'antialiasing'): b'8x',
    }
    prepared, original = canonical(raw, fields, insert_missing=True)
    output = original.get(backend, b'').lower()
    preferred = original.get(adapter, b'').lower()
    if output in D3D11_BACKENDS:
        fields[backend] = output
    if re.fullmatch(rb'all|[1-9][0-9]?', preferred):
        fields[adapter] = preferred
    if fields[backend] != D3D11_BACKENDS[0] or fields[adapter] != b'all':
        prepared = canonical(prepared, fields)[0]
    return prepared


def wrapper_requirements(raw):
    backend = (b'general', b'outputapi')
    samples = (b'directx', b'antialiasing')
    _, values = canonical(raw, {backend: b'', samples: b''})
    if values[backend].lower() not in D3D11_BACKENDS:
        raise ValueError('OutputAPI must select hardware Direct3D 11 at feature level 10.1 or higher')
    if values[samples].lower() != b'8x':
        raise ValueError('DirectX Antialiasing must be 8x for native ship insertion')


def matching_dimensions(size,desktop,output):
    w,h=size
    return desktop==f'{w}x{h}'.encode() and output==f'h:{w}, v:{h}'.encode()


def signature(sfc,dg):
    sfc_hash,size=sfc_profile(sfc)
    dg_hash,desktop,output=wrapper_profile(dg)
    if not matching_dimensions(size,desktop,output):
        raise ValueError('SFC and qualified wrapper dimensions must agree')
    return dict(schema='sfc.alpha.graphics-dimensions.v1',sfc_sha256=sfc_hash,dg_sha256=dg_hash)
