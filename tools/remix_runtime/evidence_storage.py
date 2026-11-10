"""Existing disk inventory without importing an offline replay/renderer tool."""
from pathlib import Path
from runtime_context import CONTEXT
ROOT=CONTEXT.code_root

def storage():
    total=0
    if CONTEXT.release:
        for p in CONTEXT.data_root.rglob('*'):
            try:
                if p.is_file():total+=p.stat().st_size
            except FileNotFoundError:pass
        return total
    for sub in ('remix-runtime/runs','remix-runtime/archives','d3d9-proof','d3d9-intercept/runs','d3d9-intercept/reference','d3d9-intercept/capabilities','d3d9-intercept/direct64-runs','player-replacement'):
        for p in (CONTEXT.artifact_root/sub).rglob('*'):
            try:
                if p.is_file():total+=p.stat().st_size
            except FileNotFoundError:pass # Native latest-light packets are atomically renamed.
    return total
