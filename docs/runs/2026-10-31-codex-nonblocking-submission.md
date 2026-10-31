# Run232 — nonblocking scene submission; startup workaround disabled by default

Sponsor authorized increment1 of the checks audit and explicitly requested a toggle for the24-render startup workaround,with removal as the desired baseline. Implemented without changing appearance settings,source geometry,UVs,images,identity/frame matching or GPU ownership rules. Changes remain unstaged/uncommitted.

## Changes

- Anchor and per-owner screen-position comparisons no longer reject scene inputs or owners. In performance mode those vertex comparisons do not run. Test mode can count disagreements as evidence without stopping submission. Matrix decoding,finiteness,coherent source identity and supported-format checks remain. The old `projection` rejection field remains0 for compatibility;optional disagreements have a separate `projection_audit` field.
- A missing/invalid/in-progress light update no longer causes the host to skip the entire scene. The last successfully accepted packet may be reused only if it still passes the existing session/owner/model/source and30-frame/500ms freshness rules. Observations are never re-stamped. When no valid packet remains,API lights are removed and geometry continues;fresh valid data recreates the lights. This also prevents stale lights carrying across owner reuse. All transformed light positions are checked before modifying API handles. No native API errors or malformed light values are ignored.
- Failure to update the optional calibration mirror increments `calibrationMisses` instead of rejecting a valid functional publication. Actual missing owner association,invalid simulation pose and coherent transport failures remain functional failures. Summary JSON includes the separate diagnostic count.
- Startup now performs **one Present by default**,with no old ten-millisecond-per-iteration sleeps. `SFC_D3D9_LEGACY_STARTUP_WARMUP=1` explicitly restores24Presents and their sleeps;the normal runner supplies0 rather than accidentally inheriting the old behavior. The flag is recorded in fixture/game results and the host logs `STARTUP_POLICY`. Actual output copies,fences,frame membership and material publication remain intact. The old repetition was a compatibility workaround from earlier material-readiness experiments,not an NVIDIA requirement.

The current launcher exposes `-LegacyStartupWarmup`. The Python fixture/game runner exposes `--legacy-startup-warmup`. Prewarm and later activation child environments both carry the chosen policy. Default launch performs the new one-Present path. Ordinary live frames still use one Present;no refresh cap or new delay was added.

## Validation

- x86/x64 submission policy:12checks each,covering default1/explicit24/invalid toggle values,undefined screen positions,nonblocking diagnostic disagreement and retained nonfinite rejection.
- x86/x64 loaded-light tests:22checks each,including missing/newer packet retention,unchanged-handle reuse,expiry removal,wrong-owner removal and fresh recovery. Existing malformed packet checks remain.
- Actual native persistent worker:120pose publications,120offscreen updates,one deliberately blocked calibration mirror,zero functional failures;normal stop. Built/run with the multi-scene channel enabled.
- Existing native gate/core/membership/corner/flush tests and dedicated native-light observer qualification pass;actual capture/coordinator59checks pass. Python native suite32and light suite45pass. Initial Python light-suite failures came from the sandbox temporary-directory permissions;the successful rerun uses an owned workspace temp directory. Initial failure output retained.
- Actual ordinary-D3D9/Remix/GPU-transfer/native insertion fixture:600measured frames each,with two distinct meshes and a third shared-model owner:

| Folder under `artifacts/remix-runtime/runs/` | Policy | Startup Presents | Owner insertions |
|---|---|---:|---:|
| `20261031-181635-554753-return-fixture` | Strict | 1 | 1,614 |
| `20261031-181703-113012-return-fixture` | ExtraFrame | 1 | 1,754 |
| `20261031-181730-262347-return-fixture` | Strict | 24,explicit toggle | 1,613 |

All three finish normally with exit0,zero exact-pixel mismatches and state errors,two colour/depth/native effects/text readbacks each,and all three owners inserted independently. The24-render run also exercises one accepted-light retention without withholding geometry. Fault injection remains part of these standalone fixtures;insertion counts are not seamless-gameplay rates or a controlled speed comparison.

An initial standalone run `20261031-181454-718378-return-fixture` passed its600frame GPU checks but post-analysis failed because an added diagnostic field interrupted the existing completion-line parser. The field was moved after the established prefix;raw partial evidence was retained and all final runs repeated successfully. Do not silently promote that initial run or rewrite its log.

Current multi-ship qualification is refreshed from the three final runs and focused tests. Non-executing preflight passes both default and legacy-toggle settings. PowerShell/Python parsing and `git diff --check` pass. Accepted/copied client and rendering/light configuration hashes remain unchanged. No SFC gameplay was launched by the agent. Other historical workflow qualifications were not renewed merely to make their old receipts look current.

Local evidence: `artifacts/player-replacement/submission-tests/`, `artifacts/player-replacement/run232/review.json`, and current `native-cohort-tests/qualification.json`. Resource/log/evidence and runtime bounds remain unchanged. No continuous readbacks or new broad capture were added.

## Sponsor checkout

Use the heavier skirmish and repeat the Lyran camera swaps:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\native_insertion\start_native_multiship_session.ps1"
```

To compare the old startup workaround explicitly,append `-LegacyStartupWarmup`. It is **off** in the command above. Continue using the established elevated parent and exit at the normal cue.

Gameplay must establish whether visible camera-switch fallback improves and whether first appearance/material arrival is satisfactory without24startup renders. This increment removes known rejection dependencies;it does not prove every timing miss resolved. Cloak compatibility and audit increments2–5 remain separate. Do not change appearance settings or add prediction/buffering to conceal remaining delivery problems during this checkout.
