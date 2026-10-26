# Run179 — performance baseline, SFC-authoritative asset associations

Sponsor direction: performance is the baseline; the game is the source of truth.
No commit/push requested. Retain Run178 analysis and the earlier9ff2d3d checkpoint.

## Changes

- `tools/remix_runtime/run_return_game.py`: gameplay CLI default now performance.
- `tools/remix_runtime/multi_scene_relay.py`: live relay fallback default now
  performance. Public multi-ship PowerShell launcher already selected performance;
  corrected inconsistent internal defaults rather than claiming the old launcher
  had been running test mode.
- `tools/d3d9_proof/material_binding.py`: performance skips repeated mesh/reference
  SHA comparisons and intermediate primary-image comparisons. Test retains those
  and upload-pixel comparisons. Retain content-derived identities required for
  sharing/generated filenames and the pinned native Remix texture identity.
  Do not confuse those hashes with external model/texture validation.
- Same module reuses decoded inputs through bounded32MiB per-worker LRU and
  role/content/settings-specific output names before generating duplicates.
  Four workers already exist; maximum extra decoded-cache allowance128MiB across
  four. No cross-run cache or mutation of original images. Bounds/path checks,
  current identity, synchronization and conflicting secondary-image rejection
  remain; they are consumer correctness, not validation of SFC's model selection.
- `tests/test_normal_material_binding.py`: performance/test output equality,
  trusted upstream versus test-only source comparison, conflicting image roles,
  small-cache eviction. Updated `tools/d3d9_proof/README.md` policy.

Offline exporters/helpers keep explicit diagnostic defaults; the gameplay relay
passes its performance mode. No native source, protocol, hook, material settings,
UV convention, lighting, SDK/runtime pin or original-ship suppression change.

## Offline evidence

16 focused material checks PASS;508 main Python regression tests PASS. Exact
captured-FCA replay at
`artifacts/initial-readiness/cpu-20261025-180901-800248`: geometry and source image
hashes unchanged; material-stage hash and all derived image metadata/hashes exactly
match accepted reference.77,671,995bytes generated, existing20GB ceiling retained.

Profile: identify409.29ms/bundle333.66ms/extent48.11ms/materials1246.77ms,
total2037.83ms. Ran concurrently with regressions, with profiling/cache/process
startup variation; **no measured overall speedup**. DDS encodes147→142, repeated
image resolution404→399: real but small redundancy reduction for this FCA, which
mostly uses distinct images. First native-hash subprocess626ms versus prior529ms
remains a mixed startup/scheduling measurement. Do not claim removal of diagnostic
comparisons fixes the independently unresolved2.16s complete-output interval.

Standalone fixture20261025-181033-525694-return-fixture PASS:4 owners/3 distinct
contents including a shared asset, no partial admissions,593/600 early delivery,
normal owned exit; fixture reports native HUD/scene exact, resize/recreation,
disable/re-enable and zero source-state errors. This is offline integration,
not actual SFC gameplay or sub-two-second readiness. Native light queue/decoder/
shared-worker qualification rerun PASS; current multiship qualification renewed
through its existing adjudicator/native tests, no lock bypass. Read-only normal
performance gameplay preflight PASS. No currently owned processes/channels remain.
First restricted attempt20261025-181022-506336-return-fixture failed
with WinError5; not a rendering result. Retried the same bounded existing fixture
with appropriate process access; no security-policy or installation changes.

`git diff --check` PASS. Implementation, tests and Run178/179 docs remain
unstaged/uncommitted; no push. Original game installation and sponsor settings
unchanged; standalone fixture uses its owned test directory. No new actual SFC
behavior claim. Existing normal-launch qualification is current again.

Next action: attribute the existing first-complete-output copy/readiness/postprocess
interval with low-volume isolated-host timing; keep full-fast appearance primary
and progressive material readiness secondary. No new gameplay discovery required.
