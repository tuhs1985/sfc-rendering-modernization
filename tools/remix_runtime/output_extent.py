"""Resolution budget only. Does not qualify or enable a new GPU output layout."""
MAX_WIDTH,MAX_HEIGHT=3840,2160
PLANES,BYTES_PER_PIXEL=16,4
MAX_BYTES=MAX_WIDTH*MAX_HEIGHT*PLANES*BYTES_PER_PIXEL


def requirements(width,height):
    if type(width) is not int or type(height) is not int or not 1<=width<=MAX_WIDTH or not 1<=height<=MAX_HEIGHT:
        raise ValueError('Unsupported native output dimensions (maximum3840x2160)')
    return dict(width=width,height=height,planes=PLANES,pool_slots=2,
                bytes=width*height*PLANES*BYTES_PER_PIXEL,maximum_bytes=MAX_BYTES,
                includes='Existing controlled output resources; excludes game and internal Remix allocations')
