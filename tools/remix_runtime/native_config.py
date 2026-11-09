"""Windows native INI boundary: Unicode paths require a UTF-16 BOM."""
from pathlib import Path


def write(path,text):
    Path(path).write_text(text,encoding='utf-16')
