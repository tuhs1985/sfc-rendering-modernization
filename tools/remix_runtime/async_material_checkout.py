"""Compatibility import for application renderer orchestration."""
import importlib.util
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[2]
for area in ('runtime', 'assets', 'transport', 'rendering'):
    directory = str(root / 'src' / area)
    if directory not in sys.path:
        sys.path.insert(0, directory)
spec = importlib.util.spec_from_file_location(__name__, root / 'src/rendering/async_material_checkout.py')
module = importlib.util.module_from_spec(spec)
sys.modules[__name__] = module
spec.loader.exec_module(module)
globals().update(module.__dict__)
