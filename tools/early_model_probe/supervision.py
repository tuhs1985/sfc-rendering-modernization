"""Bounded parent-side polling using the shared channel's dictionary contract."""
import time


def wait_for(predicate, seconds, message, *, deadline, enforce, snapshot=None,
             poll=None, clock=time.monotonic, pause=time.sleep):
    end=min(deadline,clock()+seconds)
    while clock()<end:
        enforce()
        # Channel.snapshot() returns a dict, including during startup. Do not
        # use ctypes-State attribute access or skip this check in fixtures.
        if snapshot is not None and snapshot()['error']:
            raise RuntimeError('Native observer reported setup/cleanup error')
        if predicate():
            return
        if poll is not None and poll() is not None:
            raise RuntimeError('Game/fixture exited before observation completed')
        pause(.05)
    raise RuntimeError(message)
