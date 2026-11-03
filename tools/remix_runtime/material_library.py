"""Offline experiment: compose generated material definitions without USD sublayers.

Images stay in their worker-owned directories, byte-for-byte unchanged. Only
generated asset paths are rebased; no geometry, map roles or shading values change.
"""
import json
import os
import ctypes
from functools import lru_cache
from pathlib import Path
from material_binding import shader


@lru_cache(maxsize=1)
def _windows_replace_file():
    api=ctypes.WinDLL('kernel32',use_last_error=True).ReplaceFileW
    api.argtypes=[ctypes.c_wchar_p,ctypes.c_wchar_p,ctypes.c_wchar_p,
                  ctypes.c_uint32,ctypes.c_void_p,ctypes.c_void_p]
    api.restype=ctypes.c_int
    return api


def replace_material_file(pending,target):
    """Exchange a completed generated library without truncating loaded readers.

    Windows ReplaceFileW accepts the packaged USD reader retaining the old file;
    Path.replace/MoveFileExW does not in the qualified held-reader control.
    Flags0 preserves security/attributes;never ignore ACL or read-only failures.
    First creation (and non-Windows tools) retains ordinary rename semantics.
    Runs on the supervisor,not the game's rendering callback.
    """
    pending=Path(pending);target=Path(target)
    if pending.is_symlink() or target.is_symlink():raise ValueError('Material publication symlink')
    if os.name!='nt' or not target.exists():
        pending.replace(target);return 'rename-new' if os.name=='nt' else 'rename'
    if target.stat().st_file_attributes & 1:
        raise PermissionError(13,'Material destination is read-only',str(target))
    # Use extended absolute paths,including UNC paths,without relying on the
    # process's long-path manifest. The source and target stay in one directory.
    def windows_path(path):
        name=str(path.resolve())
        if name.startswith('\\\\?\\'):return name
        return '\\\\?\\UNC\\'+name[2:] if name.startswith('\\\\') else '\\\\?\\'+name
    if _windows_replace_file()(windows_path(target),windows_path(pending),None,0,None,None):
        return 'ReplaceFileW'
    error=ctypes.get_last_error()
    # Microsoft documents1176/1177 as partial exchanges. If the public name
    # disappeared,restore the already completed pending library under that name.
    # Never overwrite an extant target or delete unknown/loaded files. Report the
    # original failure even after repair;do not claim a normal publication ACK.
    if error in (1176,1177) and not target.exists():
        if not pending.is_file() or pending.is_symlink():
            raise RuntimeError(f'Material ReplaceFileW partial failure {error};target absent and pending unavailable')
        try:pending.replace(target)
        except OSError as recovery:
            raise RuntimeError(f'Material ReplaceFileW partial failure {error};target-name recovery failed: {recovery}') from recovery
    raise ctypes.WinError(error)


def publish_remix_revision(root,text):
    """Atomic Remix USD publication, distinguishable by packaged Windows USD.

    OpenUSD25.11 ArchGetModificationTime uses whole-second _wstat64 mtime on
    Windows. A normal atomic rename can therefore be noticed by FileWatch yet
    skipped by SdfLayer::Reload when two revisions share that second. Assign a
    distinct logical timestamp BEFORE exchange; never wait, touch/retry a loaded
    file, or change any material/image content. Explicit async checkout only.
    """
    root=Path(root);target=root/'mod.usda';pending=root/'mod.usda.pending'
    if target.is_symlink() or pending.is_symlink():raise ValueError('Material publication symlink')
    if len(text.encode('utf-8'))>16*1024*1024:raise ValueError('Material library metadata cap')
    previous=target.stat().st_mtime_ns if target.exists() else None
    pending.write_text(text,encoding='utf-8')
    info=pending.stat();natural=info.st_mtime_ns
    published=natural if previous is None else max(natural,(previous//1_000_000_000+1)*1_000_000_000)
    if published!=natural:os.utime(pending,ns=(info.st_atime_ns,published))
    exchange=replace_material_file(pending,target)
    return dict(policy='remix-openusd-windows-second-revision-v1',
        previous_mtime_ns=previous,natural_mtime_ns=natural,published_mtime_ns=published,
        exchange=exchange,
        meaning='Distinct file revision;not runtime material installation ACK')


def streamed_layers(root,layers):
    """Offline-only derivative selecting Remix's existing texture-streaming path.

    Keep each original generated stage and every image unchanged. The sibling
    stage keeps relative texture paths valid; only the preload boolean differs.
    """
    root=Path(root).resolve();gpu=root.parents[2]
    if not 1<=len(layers)<=64:raise ValueError('Material library layer bound')
    outputs=[];count=0
    for layer in layers:
        stage=(root/layer).resolve();stage.relative_to(gpu)
        parts=stage.relative_to(gpu).parts
        if not(len(parts)==6 and parts[0]=='assets' and parts[1].isdigit()
               and parts[2:]==('rtx-remix','mods','sfc-policy','mod.usda')):
            raise ValueError('Unexpected generated material stage')
        if stage.stat().st_size>16*1024*1024:raise ValueError('Material stage metadata cap')
        text=stage.read_text(encoding='utf-8')
        old='bool inputs:preload_textures = true'
        n=text.count(old)
        if not 1<=n<=256 or text.count('inputs:preload_textures')!=n:
            raise ValueError('Unqualified texture preload declarations')
        target=stage.with_name('streamed.usda')
        if target.is_symlink():raise ValueError('Streaming derivative symlink')
        pending=stage.with_name('streamed.pending')
        if pending.is_symlink():raise ValueError('Streaming pending symlink')
        pending.write_text(text.replace(old,'bool inputs:preload_textures = false'),encoding='utf-8')
        pending.replace(target)
        path=os.path.relpath(target,root).replace('\\','/')
        if '@' in path or '\n' in path:raise ValueError('Unsafe streaming stage path')
        outputs.append(path);count+=n
    return outputs,count


def flat(root,layers,overrides=None):
    root=Path(root).resolve();gpu=root.parents[2]
    if not 1<=len(layers)<=64:raise ValueError('Material library layer bound')
    blocks={};identities={}
    for layer in layers:
        stage=(root/layer).resolve();stage.relative_to(gpu)
        # Each stage is worker output at gpu/assets/<revision>/rtx-remix/mods/sfc-policy.
        relative=stage.relative_to(gpu).parts
        if not(len(relative)==6 and relative[0]=='assets' and relative[1].isdigit()
               and relative[2:]==('rtx-remix','mods','sfc-policy','mod.usda')):
            raise ValueError('Unexpected generated material stage')
        report_path=stage.parents[3]/'material-binding.json'
        if report_path.stat().st_size>1024*1024:raise ValueError('Material report bound')
        report=json.loads(report_path.read_text())
        if not 1<=len(report['groups'])<=256:raise ValueError('Material group bound')
        for group in report['groups']:
            name=group['remix_hash'];images=group['images']
            canonical=shader(name,images,report['values'])
            if name in identities:
                if identities[name]!=canonical:raise ValueError('Conflicting flattened material')
                continue
            block=canonical
            for image in images.values():
                target=(stage.parent/image).resolve();target.relative_to(gpu)
                # Worker manifest already carries full content hashes. Do not
                # add another image decode/hash comparison to normal loading.
                if image not in report['images'] or not target.is_file():raise ValueError('Missing generated material image')
                path=os.path.relpath(target,root).replace('\\','/')
                if '@' in path or '\n' in path or '\r' in path:raise ValueError('Unsafe rebased image path')
                block=block.replace('@'+image+'@','@'+path+'@')
            identities[name]=canonical;blocks[name]=block
    if overrides:
        for name,block in overrides.items():
            if name in blocks:blocks[name]=block
    text='#usda 1.0\n(defaultPrim = "RootNode")\ndef Xform "RootNode"\n{\n def Scope "Looks"\n {\n'+''.join(blocks.values())+' }\n}\n'
    if len(text.encode())>16*1024*1024:raise ValueError('Material library metadata cap')
    return text,len(blocks)
