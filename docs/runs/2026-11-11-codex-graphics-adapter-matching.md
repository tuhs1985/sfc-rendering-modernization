# Setup-time GPU matching

November 11, 2026. Based on `3f47ad6` on `codex/tester-graphics-setup`.

```powershell
& .\artifacts\alpha\python-3.12.14\python.exe -I -B .\tools\release\qualify_graphics_adapter.py .\artifacts\alpha\portable-cache-game\SFCRemix --match
```

The development tool verifies the existing package, opens adapter zero using
the pinned Remix runtime's ordinary D3D9Ex path and reads its adapter LUID.
The standalone x86 probe observes the D3D11 device opened through dgVoodoo.
It tries the current setting first, then `all` and the bounded hardware
adapter ordinals as needed. Only a successful draw with one observed matching
LUID produces a staged config. If there is no verified match, it reports
failure and leaves the game copy untouched. The staged file changes only the
adapter setting. The normal launch path and runtime GPU check were preserved.

The real probes matched LUID `0:84705` on the first wrapper attempt using
`Adapters=1`. The staged config was byte-identical to the input. The first
standalone Remix attempt timed out after SDK shutdown while leaving the
adapter result in its log. The final one-shot helper released its device, shut
down the SDK, and kept the module loaded until process exit. It exited zero.
The pinned SDK logged the same class of object-disposal diagnostic already
seen on a successful production-host exit.

All 769 Python regressions passed. The selection tests covered retaining a
matching setting, reordered adapters with identical names, ambiguous and wrong
devices, and changing only the adapter setting in the output config. No SFC
gameplay was started. This PC has one physical GPU, so integrated-plus-discrete
behavior remains a later compatibility check.

Local evidence is in `artifacts/alpha/adapter-probe/20261111-202815-845658`
and `artifacts/alpha/verified-adapter-match-tests.txt`. The ZIP launcher has
yet to apply the matched profile or provide rollback.
