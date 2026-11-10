"""Compatibility CLI: normal play stays in the app; diagnostics load on request."""
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src/session'))
import coordinator

def normal_play(arguments):
    allowed={'--execute','--budget-seconds','--play-session','--native-all-ships',
             '--native-insertion-policy','--pipeline-mode','--native-resolution',
             '--break-models','--damage-textures','--no-damage-textures'}
    names={argument.split('=',1)[0] for argument in arguments if argument.startswith('--')}
    return ('--play-session' in names and '--native-all-ships' in names and names<=allowed
            and 'Strict' not in arguments and '--native-insertion-policy=Strict' not in arguments
            and 'test' not in arguments and '--pipeline-mode=test' not in arguments)

def diagnostics():
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'session_diagnostics'))
    import modes
    return modes

if __name__=='__main__':
    (coordinator if normal_play(sys.argv[1:]) else diagnostics()).cli()
else:
    # Probe imports are explicitly development use; preserve their shared helpers.
    sys.modules[__name__]=diagnostics()
