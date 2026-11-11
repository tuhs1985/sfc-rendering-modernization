"""Cached source image and mesh identity for retained assets."""
import hashlib
import json
from pathlib import Path


class Content:
    def __init__(self,root):self.root=Path(root).resolve();self.images={};self.signatures={}

    def image(self,filename):
        from scene_bundle import resolve_image
        path=resolve_image(self.root,filename);stat=path.stat()
        stamp=(stat.st_size,stat.st_mtime_ns,stat.st_ctime_ns,stat.st_ino)
        cached=self.images.get(path)
        if not cached or cached[0]!=stamp:
            cached=(stamp,hashlib.sha256(path.read_bytes()).hexdigest());self.images[path]=cached
        return cached[1]

    def signature(self,mesh):
        cached=self.signatures.get(mesh.get('packet_sha256'))
        if cached:return cached
        refs=mesh['refs'];resources={r['id']:r for r in refs['resources']}
        groups=[]
        for g in mesh['groups']:
            images=[]
            for key in ('primary','secondary'):
                if key=='secondary' and not g[key]:images.append(None);continue
                resource=resources.get(g[key])
                if not resource:raise ValueError('Unresolved rebind image')
                images.append(self.image(resource['filename']))
            groups.append([g['group'],g['flags'],*images])
        # Captured geometry+LOD+group image CONTENT, not resource IDs or pointers.
        value=[mesh['geometry_sha256'],list(mesh['header'][20:23]),groups,refs.get('secondary_role')]
        result=hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        if mesh.get('packet_sha256'):self.signatures[mesh['packet_sha256']]=result
        return result
