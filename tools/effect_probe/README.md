# Targeted effects/resource observation

Isolated default-off x86 startup component. **No Remix renderer, extra ship,
replacement, model/image dump or ReShade/proxy change.** Original game rendering
continues. Authority: [probe](../../docs/reconnaissance/probes/EFFECT-RESOURCE-JOIN-001.md),
[static path](../../docs/reconnaissance/2026-10-24-effect-resource-path.md),
[Run168](../../docs/runs/2026-10-25-codex-targeted-effect-probe.md).

## Sponsor test

Use the established Administrator PowerShell:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\effect_probe\start_effect_resource_session.ps1"
```

Enter the usual skirmish within120seconds. Fight normally, fire weapons and
allow incoming hits; an enemy explosion is useful if practical. Nothing new
should appear.90seconds starts at the automatic tactical gate, not ship selection.
Two beeps and the console ask you to exit normally after hooks have been restored.
No timestamps, manual RE, routine UAC prompts or build steps. Report visible
problems and whether combat/destruction occurred. Not every weapon is proved to
use the target path; no qualifying instance yields an explicit partial result.

`-CheckOnly` verifies source/dependency qualification, hashes and output reservation
without launching SFC. It does not need an elevated window. Do not launch the
ordinary multi-ship renderer or broad survey at the same time.

## What is hooked

Pinned Microsoft Detours e4bfd6b03e50de46b47abfbd1e46b384f0c5f833, x86 library.
Existing verified startup launcher preloads this DLL into the copied executable;
the worker verifies six entry instruction spans and the fixed image base before
one transaction installs detours. Other process threads are enrolled through
DetourUpdateThread; library handles relocation/suspend/resume and transaction
abort. Existing pinned src/detours.cpp is the implementation reference; no manual
relative-instruction trampoline or vtable replacement.

| Entry | Purpose |
| --- | --- |
|0x004ECD72|Global-list construction/epoch, after original call|
|0x004ECDD6|Explicit unlink/retirement, before original call|
|0x004EFA4A|Concrete0x007AA050effect draw entry/exit scope|
|0x006AD3E0|Selected texture ID, after original setter|
|0x006AC900|Primitive mode/count/current texture before finalization|
|0x006AC830|Native polygon metadata/resource/count, without array reads|

Native thiscall arguments/EAX return, nonvolatile compiler ABI, LastError and
FPU/SSE control are preserved. `/EHa` plus scope destructors unwind metadata and
active-callback counters if an original SEH exception propagates. The original
exception is not swallowed. The fixture proves synthetic ABI cases, not every
undocumented SFC assumption. Entry spans/client hash remain strict admission.

Epoch registry4096slots; nested scopes8. Missed lifecycle bookkeeping poisons
subsequent identity qualification rather than associating recycled pointers.
No age-based retirement. A missing constructor is explicitly late/unqualified.
Only scoped native metadata is retained; unscoped finalizers are counted, not
assigned an owner. Native resource/count scope is **not** proof of one-to-one
ownership of translated D3D11 draw calls or previously queued geometry.

## Transport and bounds

Existing current-user-only unique return-control mapping, identifier explicitly
passed to component. No shared GPU/image resource. Effects wire at offset256:
magic0x45524631/version1,128byte header/records; events64–76 in effect_core.h.
Control padding offset184 first DWORD is this probe's worker/file-closed flag,
not an image presentation counter. Session and process identity scope all labels.
Native frame correspondence is unqualified: records carry ordered sequence/QPC/
thread/caller, not a fabricated render-frame number.

Preallocated8192record/1MiBring;16MiB output warning8MiB;32MiB ancillary cap;
4096resource-name cache entries/256ASCII bytes per name. Static storage also holds
registry/resource cache; no callback allocation, file access, decoding, waits,
viewer calls, geometry arrays or texture pixels. Producer lock is try-only; busy/
full storage increments loss counters and returns to original execution. Background
worker handles disk and filename snapshot/rechecks against live registry/object/
manager-entry/surface identities. It does not open the image file. Cache compares
full filename as well as identities, not merely a filename hash. Resource identity
is an observed snapshot, not an unobserved allocation epoch/ABA guarantee.

At cap/time/stop the worker disables observation, transactionally restores hooks,
drains active callbacks (2s maximum), drains evidence and closes the file. Startup
DLL/control storage remains process-owned until normal exit; **no hot-unload or
early storage release**. Controlled hook removal and normal process exit are
reported separately. Error/cap/loss/unjoined scopes stay partial. No forced game
termination; setup/presentation DLLs/configuration are not modified on disk.

90s tactical/285s prepared supervision/300s existing owned game launcher. Cap
admission reserves source+archive coexistence against20GB aggregate; includes
effect-probe, API and survey outputs plus existing governed evidence. No automatic
cleanup/deletion at launch. Evidence under artifacts/remix-runtime/runs/effect-*.

## Developer validation / qualification

- build.ps1 strictly builds separate effect_component.dll and native tests;44
  native checks include actual Detours install/restore, nested scopes/exception,
  pointer reuse, mismatch, uncertain lifecycle, bounds and deliberately stalled
  writer. In that negative test record loss is expected and checked, not hidden.
- `python -B -m unittest discover -s tools/effect_probe/tests`: six parser tests.
- `python -B tools/effect_probe/run_probe.py --qualify`: replays native tests,
  then starts a verified standalone fixture with the **actual startup-loaded
  DLL/private mapping/worker/parser**. Explicit fixture export only works in the
  owned fixture executable/path, never arbitrary addresses from environment.
  It deliberately raises one original exception: parser reports partial for that
  negative event while qualification checks recovery plus four normal joined
  polygons, pointer reuse, all hook bytes restored and normal exit. Not gameplay.
- Qualification freezes all effect sources/tests/native binaries, pinned Detours
  header/library and reused launcher/channel/gate dependencies. Changed source
  refuses gameplay until requalification. No native rebuild at sponsor launch.

First injected fixture failed0xC000007B: corrected missing required startup import
ordinal1. Failure retained as setup evidence, not an SFC regression. Sandbox
launcher-registry inspection initially denied; scoped outside-sandbox fixture
repeat passed without UAC/security-policy changes. No actual SFC launched offline.
