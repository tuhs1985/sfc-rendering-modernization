"""Offline maintenance: share reviewed, immutable completed-test image files.

No runtime imports or automatic scanning. Dry-run by default. Apply requires a
reviewed SHA-256 manifest and audit ledger. Files keep their names and bytes;
successful groups become read-only hard links. Never use on live working files.
The evidence budget remains conservative and still counts every logical path.
"""
import argparse
from collections import defaultdict
from datetime import date
import hashlib
import json
import os
from pathlib import Path
import stat
import uuid

ROOT=Path(__file__).resolve().parents[2]

def digest(path):
    result=hashlib.sha256()
    with path.open("rb") as source:
        while block:=source.read(1024*1024):result.update(block)
    return result.hexdigest()

def inventory(root,before):
    """Read-only inventory of frozen successful runs, excluding already shared files."""
    cutoff=date.fromisoformat(before).strftime("%Y%m%d")
    root=Path(root).resolve();base=root/"artifacts/remix-runtime/runs"
    sizes=defaultdict(list)
    for run in base.iterdir():
        if not run.is_dir() or run.is_junction() or run.is_symlink() or not run.name[:8].isdigit() or run.name[:8]>=cutoff:
            continue
        result=run/"result.json"
        if not result.exists():continue
        try:status=json.loads(result.read_text(encoding="utf-8-sig"))
        except (ValueError,UnicodeError):continue
        if "error" not in status or status["error"] is not None or status.get("final_report_complete") is False:continue
        for path in run.rglob("*"):
            if not path.is_file():continue
            if not (path.name.startswith("texture-") and path.suffix==".bin" or path.suffix.lower() in (".bgra",".raw",".dds",".png",".bmp")):continue
            path=checked_path(root,path.relative_to(root))
            info=path.stat()
            if info.st_size>=8192 and info.st_nlink==1:sizes[info.st_size].append(path)
    groups=[]
    for size,paths in sizes.items():
        if len(paths)<2:continue
        hashes=defaultdict(list)
        for path in sorted(paths):hashes[digest(path)].append(path)
        for sha,members in hashes.items():
            if len(members)>1:groups.append(dict(bytes=size,sha256=sha,files=[p.relative_to(root).as_posix() for p in members]))
    return dict(scope="Read-only inventory of immutable images in successful older runs",before=before,groups=groups,
                potential_shared_bytes=sum(g["bytes"]*(len(g["files"])-1) for g in groups))

def checked_path(root,name):
    allowed=(root/"artifacts").resolve()
    path=root/name
    if path.is_symlink() or path.resolve()!=path.absolute() or not path.resolve().is_relative_to(allowed):
        raise ValueError("Evidence path must stay inside artifacts: "+str(path))
    for parent in (path,*path.parents):
        if parent.is_symlink() or parent.is_junction():raise ValueError("Linked path refused: "+str(path))
        if parent==allowed:break
    if not path.is_file():raise ValueError("Missing evidence file: "+str(path))
    return path

def share(root,groups,*,apply=False,ledger=None):
    root=Path(root).resolve()
    report=dict(groups=0,linked=0,already_shared=0,shareable_bytes=0,linked_logical_bytes=0)
    def record(value):
        if ledger:
            ledger.write(json.dumps(value)+"\n");ledger.flush();os.fsync(ledger.fileno())
    for group in groups:
        paths=[checked_path(root,name) for name in group["files"]]
        if len(paths)<2 or len(set(paths))!=len(paths):raise ValueError("Distinct evidence files required")
        expected=group["sha256"];size=group["bytes"]
        if len(expected)!=64 or size<=0:raise ValueError("Invalid evidence identity")
        snapshots={}
        # Validate the entire group before changing any of its paths.
        for path in paths:
            current=path.stat()
            if current.st_size!=size or digest(path)!=expected:raise ValueError("Evidence changed: "+str(path))
            snapshots[path]=(current.st_ino,current.st_size,current.st_mtime_ns)
        canonical=paths[0];report["groups"]+=1
        for path in paths[1:]:
            if os.path.samefile(canonical,path):
                report["already_shared"]+=1;continue
            report["shareable_bytes"]+=size
            if not apply:continue
            for checked in (canonical,path):
                current=checked.stat()
                if (current.st_ino,current.st_size,current.st_mtime_ns)!=snapshots[checked]:
                    raise ValueError("Evidence changed during review: "+str(checked))
            if canonical.stat().st_nlink>=900:raise ValueError("Hard-link count needs another reviewed group")
            temporary=path.with_name(path.name+".sharing-"+uuid.uuid4().hex)
            record(dict(state="intent",path=str(path.relative_to(root)),canonical=str(canonical.relative_to(root)),
                        bytes=size,sha256=expected,original_mtime_ns=path.stat().st_mtime_ns))
            try:
                os.link(canonical,temporary)
                os.replace(temporary,path)  # Same-volume atomic replacement; original survives failure.
            finally:
                if temporary.exists():
                    try:temporary.unlink()
                    except PermissionError:
                        record(dict(state="temporary-retained",path=str(temporary.relative_to(root))))
            report["linked"]+=1;report["linked_logical_bytes"]+=size
            record(dict(state="linked",path=str(path.relative_to(root)),canonical=str(canonical.relative_to(root)),sha256=expected))
        if apply:
            # This is only for reviewed immutable evidence, never active inputs.
            canonical.chmod(stat.S_IREAD)
    return report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest",type=Path,nargs="?");parser.add_argument("--apply",action="store_true")
    parser.add_argument("--scan-before",help="Inventory successful runs older than YYYY-MM-DD")
    parser.add_argument("--write-manifest",type=Path)
    parser.add_argument("--ledger",type=Path)
    args=parser.parse_args()
    if args.scan_before:
        if args.manifest or args.apply or args.ledger or not args.write_manifest:
            parser.error("Inventory requires --write-manifest and is separate from applying")
        destination=args.write_manifest.resolve()
        if not destination.is_relative_to(ROOT/"artifacts"):parser.error("Manifest must be beneath artifacts")
        report=inventory(ROOT,args.scan_before);destination.parent.mkdir(parents=True,exist_ok=True)
        with destination.open("x",encoding="utf-8") as output:json.dump(report,output,indent=2)
        print(json.dumps(dict(groups=len(report["groups"]),potential_shared_bytes=report["potential_shared_bytes"]),indent=2));return
    if args.manifest is None or args.write_manifest:parser.error("Supply a reviewed manifest")
    groups=json.loads(args.manifest.read_text(encoding="utf-8-sig"))["groups"]
    if args.apply:
        if args.ledger is None:parser.error("--apply requires --ledger")
        destination=args.ledger.resolve()
        if not destination.is_relative_to(ROOT/"artifacts"):parser.error("Ledger must be beneath artifacts")
        if any((ROOT/name).resolve()==destination for g in groups for name in g["files"]):parser.error("Ledger overlaps an input")
        destination.parent.mkdir(parents=True,exist_ok=True)
        with destination.open("x",encoding="utf-8") as ledger:result=share(ROOT,groups,apply=True,ledger=ledger)
    else:result=share(ROOT,groups)
    print(json.dumps(result,indent=2))

if __name__=="__main__":main()
