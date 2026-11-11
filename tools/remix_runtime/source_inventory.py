"""Development build-input fingerprinting, independent of GPU diagnostic runners."""
from pathlib import Path
import hashlib
from runtime_context import CONTEXT
ROOT=CONTEXT.code_root

def digest(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest().upper()

def sources():
    result={}
    for directory in ('tools/d3d9_proof','tools/remix_runtime','tools/scene_bridge','tools/m1_component','tools/native_foreground','tools/native_insertion','src/session','src/runtime','src/assets','src/transport','src/rendering','tools/renderer_diagnostics','tools/asset_diagnostics','tools/session_diagnostics','tests'):
        for p in (ROOT/directory).iterdir():
            if p.is_file() and p.suffix in ('.h','.cpp','.py','.ps1','.def'):result[str(p.relative_to(ROOT)).replace('\\','/')]=digest(p)
    return result
