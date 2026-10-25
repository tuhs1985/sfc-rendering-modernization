# EARLY-MODEL-AVAILABILITY-001 — offline-qualified, default off

Run177 actual capture reviewed: [result](../../runs/2026-10-25-codex-early-model-timing-result.md).
Both named native ship loads measured; normal gameplay/cleanup/hashes, zero loss.
No further run needed for this initial timing question. Below launcher-ready and
pending-gameplay statements are historical; runtime code/qualification unchanged.

Run176: [parent-side startup polling defect fixed and requalified](../../runs/2026-10-25-codex-early-model-launcher-fix.md).
Same sponsor command, native observer and limits; current qualification supersedes
Run175source receipt. No completed SFC timing run yet.

Run175 update: [implementation/wire/operations](../../../tools/early_model_probe/README.md),
[offline qualification](../../runs/2026-10-25-codex-early-model-timing-observer.md).
**READY FOR SPONSOR RUNTIME TEST**, not gameplay executed. Nine owned hooks
include the established tactical anchor; no competing gate/controller hook.
Worker-ready, not guaranteed process entry, starts coverage. Counts through256
source groups with first8IDpairs sampled; no geometry/images. Historical design
below is superseded by the implementation contract where details differ.

Sponsor action:start_early_model_session.ps1 in established elevated PowerShell,
familiar multi-ship skirmish within120seconds, normal gameplay, exit at two-beep
request after90stactical capture. No extra Remix ship/visual change expected.

## Historical definition — Run174

Authority:2026-10-25 sponsor requested tracing earlier model availability.
Current product is [static qualification](../early-model-availability.md), not a
runtime implementation or prepared launcher. API/effects implementation parked.

## Completed read-only qualification

`tools/recon/verify_early_model_path.py`: pinned client, existing disassembly,
explicit ranges,49expected instructions/5vtable targets/_BRK.mod suffix. Checks
all2196selected instruction bytes and52direct factory call sites. No guesses at
indirect callers or general mission roster. At most4096selected instructions,
128factory callers,128MiBdisassembly,8MiB/100000rows per old trace,256KiBoutput.
Fail on changed bytes/anchors/vtable/client, conflicting historical identity,
invalid sequence or different parser origin. Exclusive-create output; no overwrite.

```powershell
python -B tools/recon/verify_early_model_path.py --historical-trace artifacts/pre-m0/runs/20260904-100033/M0-RT-001.csv --historical-trace artifacts/pre-m0/runs/20260904-100901/M0-RT-001.csv --output artifacts/render-survey/early-model-path-new.json
```

Omit historical arguments for static-only reproduction. No game assets opened,
code executed in SFC, hooks installed or native source/build qualification changed.

## Smallest runtime extension to qualify next

Default-off isolated observer in copied game only, prepared before launch through
the existing startup mechanism/private current-user channel. Do NOT modify or
arm normal renderer/survey builds. Tactical gate marks progress; it must not be
the point at which model-loading observation first starts.

Record ordered session/sequence/QPC/thread/caller metadata for:

1.004156F9/request: owner, bounded inline input filename, no asset contents.
2.0042F51A entry/exit: request correlation, cache reuse versus parse, returned
  visual or failure. Observe exact success/failure without guessing a single
  convenient return instruction. Preserve nested requests and original exceptions.
3.00413A8D attachment after original call: ship+88/current visual and bounded
  scalar Model0/source/count/texture-ID status. Mark unsupported/special visual.
4.Existing semantic seam's first actual selected-child draw: same live owner/visual/
  model identity. This is eligibility evidence, not necessarily a visible pixel.
5.Qualified destruction/unlink markers if pointers are retained across events;
  otherwise label uncertain identity rather than recycle a pointer as a new epoch.

No geometry, texture image or continuous transform payload. No filename file-open,
hashing/decoding/allocation/wait on callbacks. Fixed preallocated counters/try-only
ring; worker serialization; drops explicit. Include cache hit, cache miss, failed
parse, nested request, secondary _BRK and unsupported formats as separate outcomes.
No new native refcount/load/graphics calls from the worker.

Admission retains existing20GBaggregate reservation,120sentry/90stactical/285s
prepared/300sowned-launcher bounds. Proposed metadata cap16MiB/warn8MiB,
1MiBring/4096request identities/256-byte name bound,32MiBancillary. No parallel
full broad pull or model/image export. Saturation is partial, not silent success.
Must document final exact wire/limits and qualify implementation before use.

Offline tests must cover actual detours/state/ABI/SEH restoration, all exit paths,
concurrent/nested requests, cache hit before/after completion, parse and allocation
failure, post-parse scaling/pointer replacement, destroyed/reused owner/visual,
secondary asset, stopped worker and clean normal exit. Preserve original client,
launch/proxy/hash checks; no forced game termination or security-policy changes.

Only after qualification prepare one sponsor run with existing familiar multi-
ship fixture. Sponsor launches, enters gameplay and exits normally; no timestamps,
manual RE or new visual actions. Compare named request→native completion→owner
attachment→first semantic draw, and distinguish loading time from actual renderer
preparation. Missing exact joins remain partial. At Run174 no launcher was ready;
superseded by the Run175prepared workflow above.
