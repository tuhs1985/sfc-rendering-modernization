"""Read published settings only; do not confuse Kit state with native GPU state."""
import re

ROOTS = ('/rtx', '/rtx-transient', '/renderer',
         '/persistent/exts/lightspeed.hdremix.renderer_settings')
MATCH = re.compile(r'mip|filter|anisotrop|upscal|dlss|resolution|denois|tonemap|exposure|sharp|texture|integrat', re.I)


def collect(settings, resolution):
    values = {}; visited = 0; truncated = False

    def walk(path, value, depth=0):
        nonlocal visited, truncated
        visited += 1
        if visited > 8192 or depth > 16 or len(values) >= 256:
            truncated = True
            return
        if isinstance(value, dict):
            for key, child in value.items():
                walk(path+'/'+str(key), child, depth+1)
                if truncated: break
        elif MATCH.search(path) and (value is None or isinstance(value, (bool, int, float, str))):
            values[path] = value[:256] if isinstance(value, str) else value

    roots = {}
    for root in ROOTS:
        value = settings.get(root)
        roots[root] = value is not None
        walk(root, value)
    return dict(schema='sfc.preview.sampling-audit.v1', published_kit_values=values,
                queried_roots_present=roots, viewport_requested_resolution=list(resolution),
                truncated=truncated, visited_nodes=visited, settings_written=False,
                native_gpu_sampled_mip='NOT_EXPOSED_BY_THIS_OBSERVATION',
                warning='Published Kit values are not proof of effective native Remix options or per-pixel GPU mip selection.')
