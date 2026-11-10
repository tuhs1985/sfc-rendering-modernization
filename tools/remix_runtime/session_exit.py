"""Development import compatibility for the application exit monitor."""
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src/session'))
import exit_monitor
sys.modules[__name__]=exit_monitor
