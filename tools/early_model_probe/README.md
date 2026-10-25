# Early model timing — separate metadata observer

Run176 fixes parent-side dictionary status polling and requalifies the actual
fixture through the same startup wait as gameplay. [Fix record](../../docs/runs/2026-10-25-codex-early-model-launcher-fix.md).
Previous Run175receipt is historical; launcher command/bounds/native hooks unchanged.

Default-off x86 startup DLL in copied test installation. **No Remix renderer,
extra ship, geometry/image export or original suppression.** Normal components,
proxies, settings and accepted installation remain unchanged.
[Probe](../../docs/reconnaissance/probes/EARLY-MODEL-AVAILABILITY-001.md),
[Run175](../../docs/runs/2026-10-25-codex-early-model-timing-observer.md).

## Sponsor workflow

Use the established Administrator PowerShell:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\early_model_probe\start_early_model_session.ps1"
```

Enter a familiar multi-ship skirmish within120seconds of ready. Play normally;
**there is no extra Remix ship to look for.** Loading metadata is already recorded
before tactical entry. The90second tactical window starts automatically; exit
normally at the two-beep/console request. No timestamps, camera routine, build or
routine UAC prompt. `-CheckOnly` is read-only. Do not run another renderer/native
observer/gate controller alongside this one. Actual SFC gameplay still pending.

## Hooks and preservation

Pinned2.5.6.4client/base00400000, ten checked entry bytes each. Single pinned
Detours transaction with other-thread enrollment/relocation; no bespoke trampoline.

| Entry | Observation | ABI |
| --- | --- | --- |
|004156F9|Ship visual request/name|thiscall1word/ret4|
|0042F51A|Full loader/cache entry/result|cdecl1word/caller cleanup|
|0042FEF9|Parser entry/ALresult/pre-postprocessing position pointer|thiscall1word/ret4|
|00413A8D|Owner+88 attachment after original|thiscall1word/ret4|
|004162B9|Ship render scope/automatic tactical gate|thiscall1word/ret4|
|0042E4B2|First selected-child entry per attachment/LOD|thiscall4words/ret10h|
|0042F918|Visual destructor entry|thiscall0words|
|004146A7|Ship constructor return|thiscall0words|
|004158C1|Ship destructor entry|thiscall0words|

Original called once; integral return bits/AL, nonvolatile compiler ABI and explicit
LastError restoration retained. Integer-only metadata preserves floating controls;
native tests check FPU/SSE. `/EHa` scopes propagate original SEH and unwind counters.
8-deep TLS; overflow/unqualified nested renders cannot inherit outer identity.
First draw requires caller0042FDD5, correct vtables, live owner/visual epochs,
actual child and matching source. It is eligibility at entry, not visible pixels.

Two fixed4096-entry epoch books/64hash probes maximum. Shared cache return retains
asset epoch; cache hit before observed completed parse is unqualified. Destructor
entry conservatively retires identity; new construction creates a new epoch.
Attachment resets first-child markers. Try-lock failure poisons identity confidence
rather than blocking. No worker-side native loader/refcount/render calls or raw
pointer queue for later copying.

## Wire and bounds

Existing unique current-user-only4096byte control mapping; explicit session/PID
and manifest. Header at offset256:128bytes, magic0x454D4131/version1; records512B.
Control padding offset184 signals finalized file/worker completion. Layout is NOT
interchangeable with broad/effects formats. Records:4uint64 sequence/QPC/token/
parent,8uint32 kind/thread/owner/visual/mesh/flags/depth/caller,40uint32 data,
256ASCII-name bytes,8zero reserved words. Kinds80–94 are defined in early_core.h.

LoadEnd/Attach/FirstDraw data:0owner epoch/1asset epoch/2visual vtable/3LODcount/
4source count/5source pointer/6string table/7raw scale/8override/9selectedLOD;
10–13child pointers;14position count/15current position pointer/16polygon count/
17polygon list/18original positions;19nonzero primary IDs/20secondary groups/
21missing IDs/22out-of-range IDs;24–39first8primary/secondary ID pairs. Counts
cover at most256groups, not image contents. data23:LoadEnd parse-call count,
Attach actual owner+88. ParseEnd data2ALsuccess/3first child/4pre-scale positions.
Stopped data0error/1active/2restored count/3hooked. Statistics data0faults/1busy/
2uncertain/3owner epochs/4asset epochs; token is scoped elapsed ticks INCLUDING
original/nested calls, **not observer overhead or frame time**.

Fixed1MiBring,16MiBtrace/warn8MiB,32MiBancillary, existing20GBaggregate plus
source/archive reservation. Outputs are in existing governed render-survey and
remix-runtime/runs/early-* roots. Reserve2ring/disk records for terminal footer.
Loss/cap/unknown association remains partial.120sentry/90stactical/285sprepared/
300sowned launcher retained. First-child events only, no full-rate frame transcript.

Worker installs before menus/scenario loading after ready; not guaranteed process-
entry coverage. The owned004162B9hook marks the established tactical gate; **do
not install competing m1_gate.dll/controller there.** No artificial refresh cap.
Callbacks only bounded native scalar/name reads, QPC, atomics and try-bookkeeping;
no files/images/decoding/allocation/waits/GPU work. Worker writes/drains/restores.
Stop transaction restores all9hooks, drains originals up to2s, verifies16bytes
per entry and closes evidence. DLL/storage stay process-owned until normal exit;
no hot unload/free. Parent/observer-host cleanup never kills SFC.

## Offline qualification

build.ps1: strict isolated x86 DLL/native tests. Run
`python -B -m unittest discover -s tools/early_model_probe/tests` and
`python -B tools/early_model_probe/run_probe.py --qualify` before gameplay.
58native checks cover actual9hooks, ABI/LastError/FPU/SSE, original SEH, nested/
concurrent cache loads, early cache, parse/allocation failure, reuse, malformed/
capped metadata, writer saturation and stopping with a load in flight. Negative
trace deliberately partial; all9-restored/active0footer must survive. Separate
actual startup-loaded DLL fixture must have zero issues/loss and named joins.

Owned fixture records explicitly flagged FIXTURE and bypass ONLY the SFC-specific
caller-address comparison; native mainline predicate separately tested positive/
negative. No GPU/gameplay claim. Qualification freezes all source/tests/binaries,
shared launcher/channel/dependencies and pinned Detours; changed source refuses
launch until requalified. No routine rebuild or policy changes at sponsor launch.

This measures request→native completion→attachment→first semantic entry. It does
not prove faster loading, Remix residency, early geometry capture or mission-roster
coverage. Review actual game evidence before changing the asset pipeline.
