"""Exact existing FNV32 check on immutable packet bytes, external workers only."""
import ctypes
import hashlib
import json
from pathlib import Path
import threading

ROOT=Path(__file__).resolve().parents[2]
BIN=ROOT/'artifacts/d3d9-proof/mesh-checksum'
_lock=threading.Lock()
_function=None
_library=None
_asset_function=None
_texture_function=None


def _load():
    global _function,_library,_asset_function,_texture_function
    with _lock:
        if _function is None:
            receipt=json.loads((BIN/'build.json').read_text(encoding='utf-8-sig'))
            source=ROOT/'tools/d3d9_proof/mesh_checksum.cpp'
            dll=BIN/'mesh_checksum.dll'
            sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
            if (receipt['source_sha256']!=sha(source) or receipt['dll_sha256']!=sha(dll)
                    or receipt.get('xxhash_header_sha256')!=sha(ROOT/'artifacts/remix-runtime/deps/xxhash.h')
                    or receipt['architecture']!='x64' or ctypes.sizeof(ctypes.c_void_p)!=8):
                raise ValueError('Native mesh checksum build/source/architecture mismatch')
            _library=ctypes.CDLL(str(dll))
            function=_library.sfc_mesh_checksum
            function.argtypes=(ctypes.c_char_p,ctypes.c_size_t)
            function.restype=ctypes.c_uint32
            _function=function
            _asset_function=_library.sfc_asset_identity
            _asset_function.argtypes=(ctypes.c_char_p,ctypes.c_size_t)
            _asset_function.restype=ctypes.c_uint64
            _texture_function=_library.sfc_texture_identity
            _texture_function.argtypes=(ctypes.c_char_p,ctypes.c_size_t)
            _texture_function.restype=ctypes.c_uint64
    return _function


def calculate(packet):
    if not isinstance(packet,bytes) or not 256<=len(packet)<=2*1024*1024:
        raise ValueError('Native checksum requires immutable bounded packet bytes')
    # CDLL releases the GIL. packet owns the buffer until this call returns;
    # embedded NUL bytes are not terminators because the byte count is explicit.
    function=_function or _load()
    return function(packet,len(packet))


def asset_identity(payload):
    if not isinstance(payload,bytes) or not 1<=len(payload)<=64*1024*1024+16:
        raise ValueError('Asset identity requires immutable bounded bytes')
    if _asset_function is None:_load()
    return _asset_function(payload,len(payload))


def texture_identity(bgra,width,height):
    if (not isinstance(bgra,bytes) or type(width)is not int or type(height)is not int or not 1<=width<=4096 or not 1<=height<=4096 or len(bgra)!=width*height*4):
        raise ValueError('Texture identity requires bounded BGRA8')
    if _texture_function is None:_load()
    return _texture_function(bgra,len(bgra))
