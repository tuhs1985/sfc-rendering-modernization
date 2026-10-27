"""Remix-only texture-origin adaptation; canonical capture and images stay intact.

Apply once when constructing a Remix resource, never to canonical UVs. Both the
base BGRA upload and enhanced DDS use the same bottom-row-first image convention.
Plain D3D9/D3D12 consumers must not call this backend conversion implicitly.
"""
POLICY = 'remix-image-origin-v1'


def image(image):
    from PIL import Image
    return image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)


def bgra(data, width, height):
    if not 1 <= width <= 4096 or not 1 <= height <= 4096 or len(data) != width*height*4:
        raise ValueError('Remix BGRA image bounds/layout')
    stride = width*4
    view = memoryview(data)
    return b''.join(view[y*stride:(y+1)*stride] for y in range(height-1,-1,-1))


def base_image(original):
    # Only derived upload bytes change. The PIL image and original content hash
    # remain canonical inputs for material generation and provenance.
    metadata = original['metadata']
    return {**original, 'bgra': bgra(original['bgra'], metadata['width'], metadata['height'])}
