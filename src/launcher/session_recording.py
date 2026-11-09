"""Installed play retention. Working files are not a permanent run archive."""
import json
from pathlib import Path
import re
import shutil

REPORT_BYTES=64*1024
REPORT_COUNT=5
MARKER='release-recording.json'


def mark(work,mode):
    if mode not in ('off','minimal'):raise ValueError('Unknown recording mode')
    pending=Path(work)/(MARKER+'.pending')
    pending.write_text(json.dumps(dict(schema=1,mode=mode)))
    pending.replace(Path(work)/MARKER)


def read_record(path,limit):
    try:
        if path.stat().st_size>limit:return {}
        value=json.loads(path.read_text())
        return value if isinstance(value,dict) else {}
    except (OSError,ValueError):return {}


def remove_work(context,work):
    folder=context.artifact('remix-runtime/runs')
    if context.data_root.is_symlink() or context.data_root.is_junction() or folder.is_symlink() or folder.is_junction():
        raise ValueError('Linked session root')
    root=folder.resolve()
    work=Path(work)
    if work.parent.resolve()!=root or not work.name.endswith('-in-game') or work.is_symlink() or work.is_junction():
        raise ValueError('Unexpected session directory')
    for path in work.rglob('*'):
        if path.is_symlink() or path.is_junction():raise ValueError('Linked session data')
    # Checked absolute path stays within the session root. No shell deletion.
    shutil.rmtree(work)


def summary(context,work,result):
    value={key:result.get(key) for key in (
        'result','normal_game_exit','exit_stage','broad_proxy_restored','play_session')}
    text=str(result.get('error') or '')[:4096]
    for root,label in ((context.package_root,'<package>'),(context.game_root,'<game>')):
        for variant in (str(root),str(root).replace('\\','/'),str(root).replace('\\','\\\\')):
            text=text.replace(variant,label)
    # Do not retain absolute paths from other applications or user folders.
    text=re.sub(r'[A-Za-z]:[\\/][^\r\n;]*','<path>',text)
    value.update(schema='sfc.troubleshooting.v1',session=work.name,error=text[:1024] or None)
    raw=json.dumps(value,indent=2).encode('utf-8')
    if len(raw)>REPORT_BYTES:raise ValueError('Troubleshooting summary limit')
    return raw


def finish(context,game_running):
    """Only finalized/restored owned sessions; never remove recovery inputs early.

    An interrupted session is kept until the existing recovery code restores its
    transaction. Retention limits rotate reports; they never stop a live game.
    """
    if game_running():return dict(deferred=True,removed=0)
    if context.data_root.is_symlink() or context.data_root.is_junction():raise ValueError('Linked data directory')
    removed=0;reports=context.data_root/'troubleshooting'
    for work in context.artifact('remix-runtime/runs').glob('*-in-game'):
        marker=work/MARKER
        if not marker.is_file():continue # Historical evidence is not ours to purge.
        policy=read_record(marker,256)
        if policy.get('schema')!=1 or policy.get('mode') not in ('off','minimal'):continue
        path=work/'result.json'
        result=read_record(path,4*1024*1024)
        restored=(result.get('final_report_complete') is True and result.get('broad_proxy_restored') is True)
        if (work/'recovery.json').is_file():
            restored=read_record(work/'recovery.json',64*1024).get('proxy_restored') is True
        if not restored:continue
        if policy['mode']=='minimal':
            reports.mkdir(parents=True,exist_ok=True)
            if reports.is_symlink() or reports.is_junction():raise ValueError('Linked report directory')
            target=reports/(work.name+'.json')
            if target.is_symlink():raise ValueError('Linked report file')
            target.write_bytes(summary(context,work,result))
            files=sorted(reports.glob('*-in-game.json'),key=lambda p:p.name,reverse=True)
            for old in files[REPORT_COUNT:]:
                if old.is_symlink():raise ValueError('Linked report file')
                old.unlink()
        remove_work(context,work);removed+=1
    return dict(deferred=False,removed=removed)
