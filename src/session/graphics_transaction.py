"""Verified graphics-file transaction. No capture, decoding or diagnostic imports."""
from pathlib import Path
import hashlib
import os
import shutil
from runtime_context import CONTEXT

ROOT=CONTEXT.code_root
FULL=CONTEXT.artifact('remix-runtime/deps/reshade-full-6.7.1/extracted/ReShade32.dll')
FULL_SHA='A1BA732B5E31E0405CDE322CC5EC62CF972B3FBAEFBB6CBDC8A24DA00D58AE24'
OLD_SHA='E35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7'

def digest(path):
    with open(path,'rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest().upper()

def qualified_full():
    if digest(FULL)!=FULL_SHA:raise ValueError('Full-support dependency hash mismatch')
    return FULL

def install_test_proxy(target,backup):
    target,backup=Path(target),Path(backup)
    if digest(target)!=OLD_SHA:raise ValueError('Isolated proxy baseline changed; no overwrite')
    qualified_full()
    if backup.exists():raise ValueError('Rollback file already exists; no overwrite')
    shutil.copyfile(target,backup)
    if digest(backup)!=OLD_SHA:raise ValueError('Rollback verification failed')
    atomic_copy(FULL,target,FULL_SHA)
    if digest(target)!=FULL_SHA:raise ValueError('Installed full-support proxy verification failed')

def restore_test_proxy(target,backup):
    target,backup=Path(target),Path(backup)
    if digest(backup)!=OLD_SHA:raise ValueError('Rollback hash mismatch; no restore')
    if digest(target) not in (FULL_SHA,OLD_SHA):raise ValueError('Proxy changed independently; no overwrite')
    atomic_copy(backup,target,OLD_SHA)
    if digest(target)!=OLD_SHA:raise ValueError('Proxy restoration verification failed')

def atomic_copy(source,target,expected):
    stage=target.with_name(target.name+'.sfc-broad-stage')
    if stage.exists():raise ValueError('Staged proxy already exists; review interrupted transaction')
    # Stage only beside the validated isolated target, never in accepted install.
    with stage.open('xb') as dst,Path(source).open('rb') as src:shutil.copyfileobj(src,dst)
    if digest(stage)!=expected:raise ValueError('Staged proxy verification failed; target untouched')
    os.replace(stage,target)
