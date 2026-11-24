# UE native game-pool boundary — November 23, 2026

Branch codex/ue-native-insertion, parent 1834379; unstaged/uncommitted.
OpenSpec task 4.1 is qualified standalone. No SFC game was launched for this
gate and no native mesh suppression or presentation is established here.

## Implemented

The existing x64 UE receiver accepts explicit --game-pool. Default output
remains private. The adapter reads the existing native source map, selected
owner/revision, immutable asset catalogue and exact source-frame ring entry
independently of the incoming UE descriptor. Admission checks full session,
owner/revision/model/source/content, source frame/sequence, camera/pose and
complete sealed native-frame checksum, target/device generations, projection and tactical bounds.

This is late activation: receiver startup does not require an asset hash.
The first independently qualified output binds its exact source asset once.
Recycled identities or different source sessions cannot silently rebind it.
Replay admission requires the explicit standalone fixture switch.

GameOutputWriter now exposes its existing slot reservation separately from
copying. The ordinary D3D9 copy path still calls prepare/reserve/CopyResource.
UE normalizes directly into those existing six shared surfaces rather than
allocating another six. Its exported NT handles remain 64-bit; publication uses
the pool's actual legacy handles, never truncated UE handles.

The worker waits for actual GPU normalization completion before publishing READY.
UE's raw-pair acknowledgement and the native pool's read lease are independent.
An occupied pool skips publication without overwriting held output or delaying
SFC. Native drain must stop the old pool before resources can retire. Existing
retirement notifications are retriggered by the producer only during the
generation handshake; no new source cadence or synchronization deadline exists.

## Verification

- x86/x64 strict native compilation and source-admission tests pass.
- ue_game_output_gpu_tests.cpp: 6,051 exact pixel checks through an actual
  x64 writer and separate x86 consumer. Checks passive attachment, late asset
  binding, wrong pose, exact source metadata, opaque black, odd viewport margins,
  GPU-complete READY, both held slots/busy skip, drain-before-retire and recreation
  at a different target extent/generation. Uses the production ReadLease.
- Actual packaged Shipping and Development each render six alternating captured
  F-CA poses through the UE exporter, x64 receiver, existing shared native pool
  and separate x86 GPU consumer. Four outputs are independently compared:
  98.895% / 98.810% of stable colour pixels are within three levels of the
  original-image rasterizer; depth p99.5 errors are 3.68e-7 / 5.23e-7. Exact owner
  coverage and empty native margins pass. First/last matching poses have identical
  pixels and alternate poses differ, preventing metadata-only stale-image passes.
- Target is an explicit odd-size 513×289 fixture with a 499×277 tactical viewport
  at 13,9, not a claim of another qualified SFC display resolution.
- Existing Shipping standalone no-readback path completes 12/12 raw leases,
  no diagnostic image folder, observed capture-to-normalized median 5.431 ms,
  p99 9.978 ms, maximum 10.151 ms. These twelve samples are a regression check,
  not a performance claim about SFC or native presentation.
- Existing ordinary game-output tests: 649 checks pass; source-service tests:
  three pass.

Generated local evidence is under artifacts/ue-foundation/gpu-exchange:
native-pool-green-01, native-pool-development-01,
native-pool-default-regression-01 and the native fixture executables. Arrays
and original images are unchanged; readback exists only in these diagnostic
fixtures, not the runtime transfer path.

## Diagnostic findings and limits

The first full fixture failed a native import because UE completed its six
raw acknowledgements and shut the receiver down while the native consumer was
still initializing. Raw-export completion is not native-consumer completion.
The explicit standalone fixture now paces each next test frame with a precreated
read-completion event, signalled only after the x86 consumer's GPU read fence
finishes and its lease is released. This event, synthetic native-frame-checksum field,
bounded CPU fixture readback and pacing are diagnostic only; normal UE output
never opens that event or waits for it. The fixture deliberately tests every
publication; production keeps nonblocking busy skips. No production timing cap
was added. Compile-only fixture errors from UE-hidden Windows macros were
corrected without changing engine headers.

An expanded resize fixture also caught an assertion dereferencing its unmapped
test view; moving the assertion before unmap corrected the test. Runtime source
was unchanged for that failure.

Task 4.2 remains: connect the native pre-effects insertion point with original
drawing enabled and a documented world-space player offset. Actual SFC GPU copy,
graphics-state restoration, later shield/text depth and live cleanup remain
unqualified. No launcher is offered until task 4.3 gates pass.

Before task 4.2, inspection of retainedRow/gateTry confirmed that the native
insertion ticket carries the complete sealed-frame checksum, not a single-row
state hash. The new UE adapter now preserves that existing cohort meaning.
Camera/pose remains independently checked. A same-pose/different-frame-seal
test rejects substitution. The packet wire and native gate remain unchanged.
The initial pool-only comparisons above preceded this integration correction;
final reruns are recorded below.

## Final source and next checkpoint at 5% allowance

Final Shipping and Development packages each repeat the six-export pixel gate
with the native gate's actual complete sealed-frame checksum. Results are in
native-pool-final-shipping-01 and native-pool-final-development-01; accuracy and
depth bounds above are unchanged. The current fresh-source Shipping regression
also passes: 119 native fixture snapshots, one admitted definition, 84 original
images, one geometry build, 20 GPU timing samples and normal UE exit. This is
standalone; no SFC launched.

Task 4.2 is started, not complete:

- Default-off SFC_NATIVE_INSERTION_ADDITIVE is cached at M1 startup. It requires
  the native gate and rejects simultaneous replacement/all-ship mode. The
  existing capture/acquire/flush/commit sequence runs, but returns before
  zero-count writes or suppression receipts. The actual recorder/coordinator
  fixture passes 111 checks, including primary/secondary original arguments,
  timeout, reentrancy, native default replacement and unchanged captured data.
- DiagnosticWorldOffset changes only the adapter model's native-unit world
  translation. 2,820 world-math checks cover camera rotation, basis conversion,
  source preservation and invalid offsets. It does not use camera-left placement.
- source_target_view reads the existing 4352 target notice without interlocked
  writes or model readiness. Native x86/x64 tests and actual read-only mapping/
  child-process tests cover passive/ready target, PID/session, torn/checksum,
  resize/device-generation and stop. No new target wire is introduced.
- Live snapshots now retain the source frame seal, anchor/revision and original
  instance camera/pose hash. The source hash helper is shared by receiver and UE.
- SFCGameOutput compiles in both packages. It primes the existing receiver
  passively, binds an explicitly selected retained anchor, prepares matched
  target generations and exports paired captures. PrepareDiagnosticOwner applies
  the world offset only to the captured owner and filters capture participation.
  These new live component methods are NOT yet wired into InspectionMode's
  TickRegistry or a launch command, and are not qualified end to end.
- Next engineering: connect that opt-in component after implementing the existing
  unique F-CA parent selector; do not use SourceService's current first-live
  scheduling anchor as a player identity. Exercise native compositor state/depth,
  then task 4.3 launcher/checkout. Suppression remains disabled.

Existing Python regressions pass: native gate 9, native insertion 6, source
service 3, definition publisher 5. The actual native light component/worker
qualification was rebuilt and passes; prior development DLL and receipt are
retained in artifacts/ue-foundation/native-pool-pre-additive. Public alpha and
original client assets were untouched.

Read-only launcher preflight currently STOPS at its 20 GB evidence reservation.
No game starts. All earlier package/component checks pass to that point.
Only this increment's obsolete byte-identical intermediate images were pruned:
316 files, 124,261,008 logical bytes. Final complete qualification inputs,
packets, JSON results and canonical images remain. Hash/alias records are in
gpu-exchange/native-pool-intermediate-aliases.json. The reservation still exceeds
the allowance; measure evidence categories and review obsolete generated runs
before the next live checkout. Do not raise the cap silently.

Stopped at requested Fuel Guard 5% threshold. Source stays unstaged/uncommitted.
