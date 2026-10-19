"""Small atomic checkpoints; interruption must not leave an absent run report."""
import json
from pathlib import Path
current_folder=None


def save(folder, result):
    global current_folder
    folder=Path(folder)
    current_folder=folder
    try:
        data=json.dumps(result,indent=2,allow_nan=False).encode('utf-8')
        if len(data)>4*1024*1024:raise ValueError('Run report4MiB cap')
    except (ValueError,TypeError) as exc:
        data=json.dumps(dict(result='PARTIAL',error='Report serialization: '+str(exc),
                             original_status=str(result.get('result','unknown')))).encode()
    pending=folder/'result.pending.json'
    pending.write_bytes(data);pending.replace(folder/'result.json')


def failure(exc):
    if current_folder is None:return
    path=current_folder/'result.json'
    old=json.loads(path.read_text()) if path.exists() else {}
    old.update(result='PARTIAL',runner_exception=type(exc).__name__+': '+str(exc))
    save(current_folder,old)
