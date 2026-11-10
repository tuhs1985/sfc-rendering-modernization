"""Development compatibility entry; implementation lives in src/session."""
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src/session'))
import coordinator

if __name__=='__main__':
    coordinator.cli()
else:
    # Preserve legacy import/patch identity; never copy module globals.
    sys.modules[__name__]=coordinator
