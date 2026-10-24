"""Worker-only output protection: use the authorized project disk allowance,
not the retired small-scene128MiB image-export test budget.
Per-asset decode/wire and GPU residency bounds remain independent.
"""
import shutil
import threading
from contextlib import contextmanager
from pathlib import Path
from evidence_budget import AGGREGATE_BYTES

ROOT=Path(__file__).resolve().parents[2]
EVIDENCE_RESERVE=32*1024*1024


class Reservations:
    def __init__(self,inventory=None):
        # One snapshot BEFORE tactical loading. Never enumerate history under
        # the admission lock. All concurrent asset writers use this session ledger.
        if inventory is None:
            from run_offline import storage
            inventory=storage()
        require_capacity(0,inventory=inventory)
        self.lock=threading.Lock();self.bytes=0;self.inventory=inventory;self.committed=0

    @contextmanager
    def asset(self,folder=None):
        # At most4workers;each converter independently limits primary and derived
        # images to128MiB. Hold this reservation until its files are finalized.
        amount=256*1024*1024
        with self.lock:
            require_capacity(self.bytes+amount,inventory=self.inventory+self.committed);self.bytes+=amount
        try:yield
        finally:
            # Count only this bounded worker output, including partial failures.
            # No whole-session/history walk; disk reservations remain live until
            # finalized bytes replace them atomically in the ledger.
            used=0
            if folder is not None:
                for p in Path(folder).rglob('*'):
                    if p.is_file():used+=p.stat().st_size
            with self.lock:
                self.bytes-=amount;self.committed+=used
                require_capacity(self.bytes,inventory=self.inventory+self.committed)


def require_capacity(additional=0,*,inventory=None,free=None):
    if type(additional) is not int or additional<0:raise ValueError('Invalid image output reservation')
    if inventory is None:
        from run_offline import storage
        inventory=storage()
    if free is None:free=shutil.disk_usage(ROOT).free
    if inventory+additional+EVIDENCE_RESERVE>AGGREGATE_BYTES:
        raise ValueError('Authorized20GB project output allowance;asset postponed')
    if free<additional+EVIDENCE_RESERVE:raise ValueError('Insufficient disk space;asset postponed')


def policy():
    return dict(legacy_scene_image_cap_removed=True,aggregate_cap_bytes=AGGREGATE_BYTES,
                evidence_reserve_bytes=EVIDENCE_RESERVE,per_asset_decode_bytes=128*1024*1024,
                image_dimension_max=4096,per_asset_images=256,resident_backing_bytes=256*1024*1024)
