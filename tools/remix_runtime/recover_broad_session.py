"""Development recovery CLI/import compatibility for application recovery."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src/runtime'))
import session_recovery
if __name__=='__main__':session_recovery.cli()
else:sys.modules[__name__]=session_recovery
