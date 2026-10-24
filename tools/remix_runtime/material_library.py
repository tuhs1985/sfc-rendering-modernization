"""Offline experiment: compose generated material definitions without USD sublayers.

Images stay in their worker-owned directories, byte-for-byte unchanged. Only
generated asset paths are rebased; no geometry, map roles or shading values change.
"""
import json
import os
from pathlib import Path
from material_binding import shader


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


def flat(root,layers):
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
    text='#usda 1.0\n(defaultPrim = "RootNode")\ndef Xform "RootNode"\n{\n def Scope "Looks"\n {\n'+''.join(blocks.values())+' }\n}\n'
    if len(text.encode())>16*1024*1024:raise ValueError('Material library metadata cap')
    return text,len(blocks)
