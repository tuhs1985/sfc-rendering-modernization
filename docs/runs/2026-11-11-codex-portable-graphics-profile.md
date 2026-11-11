# Portable graphics profile qualification

November 11, 2026. Private cache-only candidate on `codex/tester-graphics-setup`.
The regular package and accepted game copies retain their existing graphics profile.

## ReShade cache

`tools/release/stage_preflight_fixture.py --functional --portable-cache` staged
a fresh private game copy and changed one value in `ReShade.ini`. The candidate
uses a game-relative cache path. The installed ReShade helper still places
actual cache, screenshot and add-on output under the session data directory.
The installed helper produced equivalent settings for the original and candidate
after accounting for their different session directories. All 128 preset,
shader and texture input files retained their hashes.

The package passed at its first location, after a move through a path
containing spaces and a non-ASCII character, and at the short checkout path.
All 765 Python tests passed. A standalone installed Remix activation and
receiver transfer produced three byte-identical planes. The production host
exited normally and left zero owned processes. These checks establish
configuration and standalone GPU behavior.

## Adapter comparison

`tools/release/qualify_graphics_adapter.py` built an x86 DirectDraw 7 fixture
against the pinned dgVoodoo DLLs and observed the resulting D3D11 device with
the pinned ReShade API. The fixture ran with `Adapters=1` and with
`Adapters=all` in separate directories. Both drew successfully and reported
adapter LUID `0:89240`, the RTX 4070 Ti. The standalone Remix sharing probe
reported the same LUID and transferred 16,384 pixels without mismatches.
That sharing fixture timed out during SDK teardown and retired all owned
processes. The separate production-host check completed normally.

The workstation has one physical GPU and two virtual display drivers. DXGI
reported three entries with the same RTX model name and different LUIDs, plus
the Microsoft software adapter. Compare device LUIDs within the same boot.
The DXGI [enumeration API](https://learn.microsoft.com/en-us/windows/win32/api/dxgi1_6/nf-dxgi1_6-idxgifactory6-enumadapterbygpupreference)
can reorder adapters by preference, so this result does not establish the
behavior of either dgVoodoo setting on a hybrid system. Keep the accepted
adapter policy until the native game device and Remix are verified together
on integrated-plus-discrete hardware.

## Vendor inputs

The preserved dgVoodoo 2.86.5 archive and full ReShade 6.7.1 add-on installer
reproduced the qualified x86 hashes. The separate baseline ReShade 6.7.1.2133
hash is verified in the copied game. Its official standard installer URL
returned HTTP 403 during the provenance check. Independent acquisition of
that baseline remains unresolved. The current [dgVoodoo readme](https://dege.freeweb.hu/dgVoodoo2/ReadmeGeneral/)
describes redistribution conditions. Retain the version-specific archive
provenance and complete release notices before shipping.

## Private gameplay checkout

```cmd
cmd.exe /d /c call "C:\Project\SFC-Modernize Engine\artifacts\alpha\portable-cache-game\SFCRemix-Launch.cmd"
```

The checkout instructions covered replacement, familiar ReShade appearance
and normal exit. The sponsor reports the checkout complete and requests the
commit. Individual observations and timings were not reported. The private
candidate retains `Adapters=1`. Reversible preparation and clean-machine
checkout remain pending the profile and vendor-input qualifications.

Local receipts are under `artifacts/alpha/portable-cache-*`,
`portable-profile-vendor-receipt.json` and
`adapter-probe/20261111-060431-641161`. The Remix comparison is in
`share-probe/20261111-060441-094922-128x128`.
