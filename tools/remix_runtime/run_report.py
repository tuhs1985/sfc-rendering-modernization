"""Development import compatibility for application report state."""
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src/session'))
import reports
sys.modules[__name__]=reports
