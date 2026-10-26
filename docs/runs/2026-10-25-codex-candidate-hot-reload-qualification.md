# Run193 — qualify the NVIDIA asynchronous material-update route

Local date October 25, 2026; generated run names use October 26 UTC. M1 ordinary
D3D9 performance work continues. The API experiment remains parked. Sponsor
authorized diagnosis and at least two further attempts before requesting direction.
Fuel Guard attached. Fourteen actual standalone GPU attempts were made: twelve
completed and two partial/failed. Three additional launches stopped at the existing
storage-reservation check, before a renderer was started. No SFC gameplay launched.

## Decision

**A useful isolated solution was demonstrated; normal defaults are not promoted.**
Candidate 1.6.1 asynchronous loading plus the existing single-file material publisher
restores material response and avoids the long returned-layer interruption seen with
synchronous reload. The layered-library variant gives smooth delivery but misses
the accepted material response. It must not be accepted on timing alone.

Initial loading below two seconds remains OPEN. The successful initial flat test
first matched output at 3.208 seconds, with its last distinct asset admitted at
3.957 seconds. First matching output does not prove every ship was already visible.
No complete-scene startup or seamless gameplay PASS is claimed.

## Reference note — practical benefits and the two-second goal

The useful change is a reliable handoff of finished materials while the retained
scene continues displaying. A ship can first use its base textures, then gain its
enhanced materials without rebuilding its geometry or waiting for every other
ship. Later-arriving ships use that same handoff. This complements the earlier
parallel preparation and initial-pixel upload work; it does not replace them.

The tests resolve a specific integration choice: asynchronous loading with our
layered publication missed the accepted material response; the existing single-file
publisher preserved that response without the long returned-image interruption.
That is evidence for using the supported runtime facilities through a qualified
publication route, rather than writing a new material loader. It is not proof of
the exact internal vendor fault, universal flicker elimination, or live-game PASS.

This helps the sub-two-second objective by removing a blocking material-update
operation and retaining base-first display. It does not yet meet that objective.
Measure both first useful output and completion of the initial distinct assets;
do not report the 3.208-second first match as all ships loaded. Further reductions
must target measured remaining startup work after the corrected route is integrated.
Do not substitute the slow complete-library-before-device control as a shortcut.

Sponsor subsequently requested a commit with reference notes. The accumulated
implementation, tests and Run177–193 records are checkpointed together; normal
candidate promotion and the production alias-lifetime correction remain future
work. Raw generated assets, vendor binaries and runtime evidence stay excluded
from Git. Earlier unstaged/HEAD statements below describe the execution-time state;
the checkpoint commit supersedes that repository-state description only. A fresh
pre-commit main Python regression passed533tests in10.470s; test output is retained
at `artifacts/candidate-hot-reload/commit-regressions.txt`. No game or GPU run was
repeated for this documentation/commit step.

## Source-backed experiment definition

Used the supported route identified in [Run192](2026-10-25-codex-upstream-hot-reload-fix.md):
[NVIDIA REMIX-5883](https://github.com/NVIDIAGameWorks/dxvk-remix/commit/25d18f6b692ca762d4236ffc6373f1bbd91e7a14).
The release-linked [USD implementation](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/rtx_render/rtx_mod_usd.cpp)
uses worker rebuilds when asynchronous asset loading is enabled and the stage is
loaded; synchronous loading retains the blocking reload route. It distinguishes
structural material changes from edits to existing materials. That justified
separate initial-load, existing-material-edit, and new-library-publication controls.
NVIDIA's documented preserve-path debugging switch was also tested, unsuccessfully.

**CONFIRMED:** actual candidate startup logs show the requested True/False option;
the package contains rebuild-worker diagnostic strings. **Unresolved:** package
banner `remix-main+5a7eec84` versus public release-linked source `0a6cd5b` is not
instruction-level source parity. Do not claim an upstream internal defect proved.

Rebuilt the isolated candidate host from current source with its verified matching
header, x64 `/O2 /fp:precise /W4 /WX`. Candidate runtime SHA256
`c05c552e3f44597960891eff6c8482efcbde8573b15c2b900d3dc360e6cc1ad9`;
host `cda23a9e6bce90eed53186198bd74536a92332946ab934830d51bfe0b9919f59`;
header `26a5607a07e8718298c35519e53bbc71d526186a947e5a2a5b613a0d6db04f3a`.
An isolated handoff host additionally called supported SetConfigVariable after
device registration. API success is request acceptance, not a getter proving the
option's final effective value.

## Attempts and full-interval results

All rows are under `artifacts/remix-runtime/runs/`, suffix `-return-fixture`.
First-match times are from earliest asset discovery. Omission counts start at the
first matched output and cover the full remaining recording, not only the settled
600-frame window. These measure omitted returned images, not SFC frame loss.

| Attempt / UTC run prefix | Change | First match | Post-start omissions / longest consecutive | Result |
|---|---|---:|---:|---|
| 1 / 20261026-005109-470034 | Async, layered, accepted materials | 3.438s | 3 / 1 | Clean fixture; material response missing |
| 2 / 20261026-005345-379946 | Async, emission zero | — | — | Alias dependency KeyError; failed preparation/forced supervisor cleanup |
| 3 / 20261026-005717-886433 | Same negative, probe alias correction | 3.366s | 2 / 1 | Clean; little emission response on layered route |
| 4 / 20261026-005852-224913 | Sync positive control | 3.226s | 82 / 49 | Correct response; long update gap remains |
| 5 / 20261026-010038-016869 | Async, one delayed metadata-only master notification | 3.218s | 3 / 1 | No material recovery |
| 6 / 20261026-010339-774851 | Sync device start then API async request | — | — | 35.872s startup draw/Present outlier; incomplete resize/recreate checks |
| 7 / 20261026-010538-056057 | Exact handoff repeat | 4.026s | 6 / 1 | Clean; no accepted material recovery |
| 8 / 20261026-010841-367818 | Async, preserve path False | 3.541s | 2 / 1 | Clean; no accepted material recovery |
| 9 / 20261026-011212-992730 | Complete layered library before device | 8.406s | 2 / 1 | Correct response; diagnosis only, sacrifices early display |
| 10 / 20261026-011354-044126 | Same initial-load control, emission zero | 8.536s | 3 / 1 | Confirms initial async emission response |
| 11 / 20261026-011956-871319 | Initially complete; edit existing materials after first snapshot | 8.333s | 5 / 1 | Existing-material hot edit works |
| 12 / 20261026-012445-679174 | Async, existing flat publisher; no complete-library barrier | 3.208s | 1 / 1 | Correct response; settled 596/600 |
| 13 / 20261026-012653-054882 | Flat negative, emission zero | 3.237s | 1 / 1 | Real material response confirmed; settled 595/600 |
| 14 / 20261026-012743-548152 | Flat, third distinct asset arrives after 120 returned frames | 3.466s | 3 / 1 | Four owner ACKs; no rejection/partial; settled 595/600 |

Attempt6 native child exited zero with no owned children, but the fixture failed
to reach all required end checks. Its outlier cause is unassigned; do not call it
a native crash or attribute it to shaders/cache without evidence. Attempt2 lacked
a normal native receipt; later explicit process inventory was empty. Preserve that
distinction. All other twelve fixtures completed normal exits, exact native
HUD/scene checks, zero graphics-state errors, resize and device recreation checks.
The package's existing internal disposal warnings remain a separate limitation.

## Pixel and content controls

Same fixed synthetic poses, union ship-pixel masks, RGB mean absolute error on
0–255 channels; this is not bit-exact visual equivalence or complete PBR validation.

- Layered async full versus emission-zero: FCA/RCA/FDD errors
  1.000 / 0.633 / 1.057. Against synchronous positive: 14.791 / 38.462 / 11.458.
- Metadata-only retouch versus initial async full: 0.073 / 0.047 / 0.072;
  no supported recovery. Preserve-path False and API handoff also fail recovery.
- Complete-before-device full versus emission-zero: 4.696 / 5.222 / 2.398.
  This confirms initial async loading can apply emission; waiting for all assets
  before device creation is not the proposed performance solution.
- Existing-material edit, same run first versus late snapshot:
  6.280 / 5.976 / 3.845. Its late output is close to the initial zero-emission
  control, not merely a file-update acknowledgement.
- Flat full versus flat emission-zero: 5.765 / 5.656 / 3.235, with
  1464 / 1643 / 326 ship pixels changing more than ten channel levels.
  Flat full versus synchronous positive: 2.588 / 1.454 / 2.464.
  The late-asset flat run is similarly close: 2.679 / 1.402 / 2.545.
  Final flat positive image was inspected; original textures and distinct ship
  markings are visible. No lighting or material retuning was used.

All 381 selected geometry/image/per-asset material files in flat positive attempt12
are exact against the archived accepted reference. Flattening uses the existing
`material_library.flat` to rebase image paths and combine definitions into the
master; it does not replace image contents or geometry. Attempt13 intentionally
differs only in three emission-stage files. Attempt14 differs only at the captured
frame field in `assets/3/scene.bin`: 200001→200318, offset498456. All other bytes
of that 498672-byte packet, all images and material stages match.

**CONFIRMED:** existing-material edits and flat new-material publication work in
this fixture; the layered dynamic route does not preserve the accepted response.
**STRONG HYPOTHESIS:** structural layered publication/change handling explains the
candidate failure. The exact packaged-runtime branch/cache/notice cause remains
unproved. This does not prove every asynchronous reload or all sublayers are broken.

## Harness defect, boundaries and validation

Attempt2 exposed a separate deterministic preparation bug: alias completion releases
shared derived dependencies while queued per-owner material consumers still refer
to them. The diagnostic cancels those queued alias consumers before release;
already-running consumers retain submitted arguments. Three self-checks reproduce
the original failure and verify queued/running lifetimes. **Production is not fixed
by this probe**; integrate and regression-test it before promotion.

The probe changes only its own Python process, owned candidate child inputs and
generated fixture files. It freezes/asserts the normal host/runtime, relay and
native source hashes; retains atomic publication, actual output fence/ACK checks,
owned-process deadlines and caps. Single-file mode deliberately remains diagnostic;
the normal CLI's candidate+parallel/flat restrictions are not silently removed.
`result.runtime_candidate` may be null because the normal CLI was not promoted;
the explicit `candidate_hot_reload_probe` receipt identifies the actual binary,
header and options. Production qualification locks are removed from diagnostic
results and marked ineligible, with originals preserved as references.

Validation this run: 22 parallel-asset, 11 candidate and 5 material-library Python
tests passed; alias three-case and completed-transaction self-checks passed;
candidate and handoff native builds passed `/WX`; 14 actual GPU attempts as above.
No full 615-test rerun is claimed. Final AST/JSON/path/diff checks recorded in the
evidence receipt. No new game/client hash result is claimed: no game launched or
client artifacts touched. Normal binaries and settings remain unchanged.

## Evidence, cleanup and handoff

- Versioned [evidence summary](../reconnaissance/evidence/20261025-candidate-hot-reload-qualification.json),
  [probe](../reconnaissance/probes/20261025_candidate_hot_reload_probe.py),
  [analyzer](../reconnaissance/probes/20261025_candidate_hot_reload_analysis.py).
- Raw results, logs, sync traces and first/late BMPs remain in the 14 named run
  directories. `artifacts/candidate-hot-reload/analysis.json` carries all timings,
  mask comparisons and content checks. Do not substitute settled-window success
  for full-interval delivery.
- SHA-verified ZIP archives preserve every run's generated duplicate asset tree,
  including failed output, plus six older completed duplicate trees. About
  2.862GB raw became 177.9MB ZIP. No original packet/evidence screenshot, accepted
  current normal fixture `20261025-221209-968233`, or golden fixture was removed.
- Aggregate ledger plus diagnostic extras: 18,826,181,177 bytes before final small
  documentation writes, below20GB. Existing1GiB prelaunch reservation retained;
  three reservation stops were followed by verified archival, not relaxed limits.
- No active owned renderer, fixture, bounded job or SFC process at final inventory.
  CIM inventory was unavailable; Get-Process and owned job receipts confirmed
  cleanup. No session connection should be reused after restart.
- HEAD `9ff2d3d`; this run adds two probes, this record and its evidence, updates
  HANDOFF/STATUS and the checked Obsidian snapshot. Prior implementation/test dirty
  work is preserved. Nothing staged, committed or pushed.

**Exact next action:** integrate an explicitly isolated candidate+flat+parallel
qualification path with the alias-consumer lifetime correction, then run its normal
material/delivery/cleanup regression gates before offering a gameplay checkout.
Keep normal1.5.2 unchanged until qualification; do not redo discovery, introduce a
custom loader, promote the eight-second ordering control, or unpark the API path.
