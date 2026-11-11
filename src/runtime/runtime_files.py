"""Production paths and file helpers, independent of offline launchers."""
import hashlib
from runtime_context import CONTEXT

ROOT=CONTEXT.code_root
BIN=CONTEXT.artifact('remix-runtime/return-bin')
TEST=CONTEXT.game_root
DLL=CONTEXT.artifact('remix-runtime/deps/remix-1.5.2/.trex/d3d9.dll') # Development modes only.
ENV={'DXVK_LOG_LEVEL':'error','DXVK_GRAPHICS_PRESET_TYPE':'4','RTX_INTEGRATE_INDIRECT_MODE':'0',
     'DXVK_UPSCALER_TYPE':'0','DXVK_RAY_RECONSTRUCTION':'False','RTX_DLSS_PRESET':'0','RTX_ENABLE_ASYNC_COMPILATION':'False'}


def digest(path):
    with open(path,'rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest().upper()


def capture_file_bytes(path):
    try:return path.stat().st_size if path.is_file() else 0
    except FileNotFoundError:return 0 # Producer may atomically rename a packet.
