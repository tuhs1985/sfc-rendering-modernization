# Run266 — Compare the dome stall with the pre-light setup

## Result

The dome-file stall demonstrably predates the effect-light update. Its underlying Windows wait remains unresolved. No production fix or renderer/configuration changes were made in this investigation.

The isolated renderer previously described as merely “current minus effects” has SHA256 `b0a157de420975e7c199dc440e51204c797a7a7aea44e20cf446f8a8a0e16d3c`. This exactly matches the recorded Run260 pre-effect renderer, and the Run256 normal renderer. This is executable byte identity, not just similar source or rendering behavior. The complete historical Python/native-game environment was not rolled back.

Run256 already sampled the same 160-byte dome image opening on `dxvk-cs`, over 2.923 seconds, before the effect integration. Therefore the failure was not newly introduced by that update. The historical handoff explicitly parked this unresolved cold-dome issue. Later successful runs did not establish its elimination.

## Checked differences

Compared the Run260 Strict fixture with the new historical-renderer control:

- The recorded and actual renderer hashes match exactly.
- `loading-inputs.json` matches byte-for-byte, including pinned runtime/header hashes, async loading policy and private triangle preparation.
- Image, quality, material settings and `rtx.conf` match byte-for-byte.
- Parsed existing scene-light settings match after removing the newly added effects sections. Those additions remain disabled.
- The dome generation/path code, supported API light conversion and private-render prewarm code have no working-tree differences from HEAD.
- No changes to SFC, assets, protection settings or driver/runtime version were made.

This rules out a changed renderer executable, changed existing lighting settings or changed recorded runtime loading inputs as necessary explanations for the reproduced failure. It does not prove every historical environmental variable unchanged.

## Controlled resource-access trials

Each standalone test used the exact historical renderer, 60-second delayed activation and eight actual captured model families from the failed carrier run. Geometry and images came from the captured packets; owner identity and layout are synthetic. No game was launched, no worker sampler attached, and no completion guard was raised.

| Trial | Dome access | First live completion | Other outcome |
| --- | --- | --- | --- |
| `20261102-051936-589295-return-fixture` | Fresh generated image, diagnostic early content read | 8.522 ms query wait | Later material publication failed with `sharing-busy for5s` |
| `20261102-052117-302518-return-fixture` | Fresh generated image, no early content read | Failed at 4.985 seconds | Same first-live completion failure reproduced without sampling |
| `20261102-052241-588879-return-fixture` | Hard link to an existing identical dome image, diagnostic early content read | 9.535 ms query wait | Later material publication failed with `sharing-busy for5s` |

The hard-linked file retained the exact 160 bytes/SHA256 and the light settings. Preparing the link/environment took 38.036 ms; the diagnostic read took 0.117 ms. The first trial's diagnostic early read was not individually timed. These are one trial per condition, with potentially changing caches/security/file state: early reading or reuse is a useful lead, **not a proved cure or root cause**. Hard links are diagnostic only and not a proposed delivery design.

All three trials are partial/failed overall. The new material-publication sharing failures are real, separate observed failures; do not claim successful full rendering qualifications. The earlier Run265 extended fixture also has a known final three-owner expectation incompatible with this eight-asset replay. First-live timing is taken directly from the GPU-host evidence, not inferred from the supervisor exit code.

## NVIDIA source check

The [pinned public CreateLight implementation](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/rtx_render/rtx_remix_api.cpp#L1066) copies the supplied dome filename into an owned filesystem path before queuing work. Its command worker then resolves and preloads the image and tracks its residency. This supports the observed command-thread location and does not support blaming our local temporary filename string's lifetime. Public source/package instruction parity remains unverified; this is source-level corroboration, not private binary symbol attribution.

## Remaining blocker and next exact action

User-mode stacks identify the blocked file-opening operation, but not the kernel/filter component holding it up. Current execution has no Administrator token, including through the available elevated tool request. A short local Windows wait trace is needed to distinguish a Defender/filter reply wait, file lock or another kernel wait. Do not assert which one caused this dome wait based on the older, separately attributed activation/process-creation traces.

Prepared `artifacts/player-replacement/run266/start_dome_wait_trace.ps1` for the sponsor's existing Administrator PowerShell. It launches only the historical standalone renderer replay, not SFC. The existing current-user startup mapping supplies host identity and readiness. The trace begins at readiness age 58 seconds, before 60-second activation, and ends seven seconds after activation or at a 12-second trace bound. The passive receiver's existing log does **not** stop this trace prematurely. The full observer is capped at 150 seconds; the fixture retains its watchdog/cleanup. Existing WPR sessions are left untouched. Circular buffers are 256 MiB; final trace bound 128 MiB, within the unchanged 20 GB allowance. Defender stays enabled. No additional symbols are downloaded.

Python syntax, timing-trigger assertions, WPR profile XML and launcher PowerShell parser were checked. Actual trace execution requires the sponsor's administrator window; no trace was collected or claimed here. No owned rendering/game processes remain after the completed tests.

Review the resulting trace's exact host command-thread switch-out/reply stacks and first-live interval. If a filter is responsible, preserve protection and select a supported resource-delivery solution based on that evidence. Do not replace this diagnosis with speculative dome warm-up, GI disablement, longer timeouts or a renderer architecture change. The separate 32-entry physical-hull defect remains open. Effects and emission collection remain parked/off.

Evidence, diagnostic helpers and comparison receipts: `artifacts/player-replacement/run266`. Changes remain unstaged and uncommitted.
