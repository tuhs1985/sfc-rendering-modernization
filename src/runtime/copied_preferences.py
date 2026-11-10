"""Allow game-owned preferences without dropping protected copied-file checks."""
import hashlib
from pathlib import Path


def protected_ini_sha256(raw):
    if len(raw)>1024*1024:raise ValueError('Copied INI exceeds1MiB')
    section=b'';names=0;network_sections=0;protected=[]
    for line in raw.splitlines(keepends=True):
        text=line.strip()
        if text.startswith(b'[') and text.endswith(b']'):
            section=text[1:-1].strip().lower()
            if section==b'network':network_sections+=1
        if section==b'network' and b'=' in text and text.split(b'=',1)[0].strip().lower()==b'playername':
            names+=1
            continue
        protected.append(line)
    if names>1 or network_sections>1:raise ValueError('Ambiguous copied INI preference')
    return hashlib.sha256(b''.join(protected)).hexdigest().upper()


def prepared_ini_signature(path,expected_sha):
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest().upper()!=expected_sha.upper():
        raise ValueError('Prepared INI reference hash mismatch')
    return protected_ini_sha256(raw)


def changed_protected_files(before,after,ini_raw,ini_signature):
    changed={name for name in set(before)|set(after) if before.get(name)!=after.get(name)}
    if 'sfc.ini' in changed and ini_signature and protected_ini_sha256(ini_raw)==ini_signature:
        changed.remove('sfc.ini')
    return sorted(changed)
