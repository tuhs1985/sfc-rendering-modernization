# Run213 — automatic return after temporary native fallback

2026-10-27 America/New_York; parent `e4d1e33`. Sponsor reports replacement worked,
then shut off during camera testing, and directs temporary native fallback with
automatic return instead of permanent disable. This supersedes the old ordinary
failure latch, not source identity/GPU safety requirements. No new gameplay was
launched by Codex; current appearance, geometry/UVs and original assets preserved.

## Actual first replacement run

`20261028-012300-684467-in-game` is a UTC artifact name for this local-date run.
Native receipts record2,432suppressed submissions,2,427matching Remix commits,
zero native rejections, four cumulative repeated presentations, peak2, then one
native recovery at source frame2598. Together with sponsor observation, this
supports working initial replacement followed by the version1 permanent latch.
No reason trace was recorded in version1; the exact camera event or assertion
that only one frame was lost is not independently proved by these final counters.

Game exited normally and renderer exited0; accepted critical hashes and launcher
settings unchanged. Controller exited8 because target exited before controlled
component removal; hook unload was not proved. Preserve this as partial duration/
cleanup evidence, not a claim the initial replacement never worked or a clean
controlled-unload PASS. New checkout should keep SFC open through restoration.

## Changes

Version2 [transaction](../reconnaissance/player-replacement-transaction.md):
ordinary gaps recover to NativeFallback, then automatically re-enter Priming when
fresh source/capability data is available. A fresh exact matching output and new
activation generation are required before suppression resumes. There is no fixed
cooldown or model/material reload. Two extra complete-picture presentations remain
the brief hold budget; original rendering continues during longer recovery.
Explicit stop/disable stays off; existing device-recreation restrictions remain.

No old pixels are combined with a new camera/background. Owner/session/revision,
source sequence/checksum, generation/epoch,50ms pending-input age and GPU leases
remain unchanged. Automatic fallback is not a waiver for frequent visible toggles
or poor frame timing; assess the next gameplay result honestly.

Added bounded reactivation/native-fallback/cause counters and supervisor snapshots
at the existing five-second cadence. Protocol stays4,416bytes using former padding;
native peers require version2, while historical version1 receipts remain readable
by the analyzer. No new surface pool, native hook IO/wait/allocation, renderer
architecture change, appearance tuning, alpha-feature work or refresh-rate cap.

Runtime/test files changed:

- `tools/d3d9_proof/replacement_transaction.h`: version2/counters, recoverable versus
  terminal original mode.
- `tools/remix_runtime/d3d9_game_receiver.h`: temporary native state, fresh-output
  re-prime/generation handling, reason classification and stop behavior.
- `tools/remix_runtime/player_replacement.py`: historical decoding, version2
  qualification and retained-single-asset proof.
- `tools/remix_runtime/run_return_game.py`: bounded recovery telemetry.
- `tools/remix_runtime/return_fixture.cpp`: single/prolonged output withholding,
  one invalid source frame, auto-resume and explicit-stop checks.
- `tools/d3d9_proof/build_player_replacement.ps1`: new current native-test output
  directory instead of overwriting Run208 historical proof files.
- `tests/player_replacement_tests.cpp`, `tests/test_player_replacement.py`:
  recoverable/terminal policy and versioned statistics.

README, transaction/probe/readiness/contract, STATUS, handoff and Obsidian tracker
updated. Prior unstaged alpha/BRK documentation preserved; no staging/commit/push.

## Validation

- 579 Python regressions PASS. Strict native/GPU transaction32checks each32/64bit;
  actual x86 recorder12checks PASS, preserving capture and both list paths.
- Full native component/proxy/gate/recorder regressions and dedicated native-light
  observer/worker qualification PASS. Normal/candidate hosts, receiver and return
  builds PASS with the pinned dependencies.
- Actual Remix steady fixture600/600paired frames. Fault fixture proves one miss
  resumes; prolonged missed output displays intact native frame then returns
  automatically at a newer generation; a one-frame invalid source also returns.
  Explicit stop does not resume. Two reactivations, preserved exact native HUD/
  background markers, peak whole-picture hold2, state0, resize/recreation, owned
  exits0. Renderer summary **loads=1**: retained geometry/textures reused.
  Native rejection at deliberate stop is expected refusal, not wrong-owner draw.
- Existing normal, initial-material, late-material and live-tuning fixtures and
  qualifications PASS. Both replacement/tuning read-only preflights PASS. These
  remain offline proofs; revised actual camera recovery/controlled unload pending.

Local logs/index/settings copies and versionable summary identify exact runs and
counts. One late regression was refused **before launch** by the1GiB evidence
reservation within20GB. No threshold changed: reviewed GPU-derived files from the
closed first gameplay run were ZIP archived with decompressed SHA verification,
saving89,782,046bytes. Original gate packets/logs/result stayed in place. Reviewed
standalone bulk likewise archived; restore before image/raw reinspection. No lost
capture or shader/runtime error inferred from this capacity refusal.

Existing90s tactical/285s workflow,128MiB controlled output and image/log limits
retained. Current rendering/lights are byte-identical to before testing; temporary
R3 profile for legacy comparisons was finally restored. No original client files
modified. Source/binary qualification reissued through actual tests, not edited
hashes. No exact live reactivation latency or universally seamless behavior claim.

## Exact next action

Run the **same** launcher from the established elevated parent:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\d3d9_proof\start_d3d9_player_replacement_session.ps1"
```

Use your F-CA versus a different model. Test camera movement and switching freely,
then move/turn and play briefly. A longer gap may briefly show the original ship,
but the enhanced ship should return automatically when fresh output is qualified.
No manual timestamps or repeated on/off sequence. Keep SFC open through restoration
and exit normally when requested. Review telemetry, visible behavior, unload and
hashes before declaring recovery fixed in gameplay or expanding replacement.
