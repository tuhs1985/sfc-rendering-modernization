"""Recognize the qualified graphics profile with only its output size varied.

All other bytes remain protected. This does not edit a user's game settings.
"""
import hashlib
import re

SIZES=((1024,768),(1280,720),(1366,768),(1440,900),(1600,900),(1920,1080))


def canonical(raw, fields):
    if len(raw)>1024*1024:raise ValueError('Graphics settings exceed1MiB')
    section=b'';seen={};out=[]
    for line in raw.splitlines(keepends=True):
        text=line.strip()
        if text.startswith(b'[') and text.endswith(b']'):section=text[1:-1].strip().lower()
        match=re.fullmatch(rb'([ \t]*)([^=\r\n]+?)([ \t]*=[ \t]*)([^\r\n]*)(\r?\n)?',line)
        key=(section,match[2].strip().lower()) if match else None
        if key in fields:
            if key in seen:raise ValueError('Ambiguous graphics dimension setting')
            seen[key]=match[4].strip()
            out.append(match[1]+match[2]+match[3]+fields[key]+(match[5] or b''))
        else:out.append(line)
    if set(seen)!=set(fields):raise ValueError('Missing graphics dimension setting')
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


def matching_dimensions(size,desktop,output):
    w,h=size
    return desktop==f'{w}x{h}'.encode() and output==f'h:{w}, v:{h}'.encode()


def signature(sfc,dg):
    sfc_hash,size=sfc_profile(sfc)
    dg_hash,desktop,output=wrapper_profile(dg)
    if not matching_dimensions(size,desktop,output):
        raise ValueError('SFC and qualified wrapper dimensions must agree')
    return dict(schema='sfc.alpha.graphics-dimensions.v1',sfc_sha256=sfc_hash,dg_sha256=dg_hash)
