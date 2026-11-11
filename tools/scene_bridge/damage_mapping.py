"""Development compatibility for application asset preparation."""
from pathlib import Path
import importlib.util
import sys
application=Path(__file__).resolve().parents[2]/'src/assets'
sys.path.insert(0,str(application))
spec=importlib.util.spec_from_file_location(__name__,application/'damage_mapping.py')
module=importlib.util.module_from_spec(spec)
sys.modules[__name__]=module
spec.loader.exec_module(module)
globals().update(module.__dict__) # Preserve existing explicit spec-loader tools.
