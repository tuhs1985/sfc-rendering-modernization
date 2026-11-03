# Run257 — Subsecond first replacement; relaunch guard corrected

## Sponsor run

Reviewed `20261101-195450-903512-in-game`. Sponsor reported loading appeared under two seconds, then clarified that “didn't end clean” meant the next test would not launch.

- First recorded native insertion: **882.0924 ms** after the first recorded native frame start, **864.3751 ms** after asset discovery. These are queued native insertion timings, not a physical display measurement or the entire SFC scenario-loading interval.
- KFF and F-CA both qualified and were acknowledged. Native preparation took **1.933 ms / 28.825 ms**, GPU admission **0.007 ms / 5.466 ms** respectively.
- After the first insertion, all **5,340** recorded frames committed replacement; no subsequent recorded fallback. The earlier 49 original frames were startup: 42 without a request and seven missed admissions. Do not count those as later camera-switch failures.
- 9,341 owner-specific insertion/suppression receipts, two owner identities, zero unavailable/omitted owners, zero invalid live updates and no partial asset preparation. Asset mappings were fully released.
- Normal game exit, renderer exit 0, controller exit 0, hook restoration/unload, proxy restoration, unchanged original/copied critical client files and completed final report are all recorded. No owned game/renderer/controller processes remained when inspected.
- Existing Remix common-device-disposal and ReShade reference-count warnings remain in logs. Recorded successful process cleanup does not establish warning-free internal COM disposal. Those warnings were not the reproduced relaunch blocker.

The sponsor did not separately reconfirm all HUD/control behavior in this feedback; no new broad gameplay acceptance claim is inferred.

## Relaunch cause

Read-only preflight reproduced:

`ValueError: Native cohort inputs changed: tools/remix_runtime/config/lights.toml`

The lighting profile had changed from the earlier qualified appearance hash. The code/binary gate treated that intentionally editable profile as an immutable input. The run itself had exited; this was a preflight rejection, not a stuck renderer.

## Fix

`native_cohort.require_qualification` now treats only these two established visual profiles as editable between sessions:

- `tools/remix_runtime/config/lights.toml`
- `tools/remix_runtime/config/rendering.toml`

All source, binary, dependency, evidence, placement and other file hashes remain checked exactly as before. Current visual profiles pass the existing runtime validators once during preflight: byte caps, TOML/schema, known light IDs and both required scene controls, numeric/type/shape bounds, and material/image/quality settings. Their actual validated SHA256 values are returned as `active_visual_inputs` for the next run's evidence. Historical qualified visual hashes remain historical evidence.

This admits user appearance edits, not arbitrary code changes or invalid values. Normal session-frozen configuration and explicit live-tuning behavior are unchanged. No file was rewritten to restore an older appearance; the sponsor's lighting hash `948B141511C31AA83EEF9546D8EA8A4BDBA2DB23D26ED840C99BF201EBE77EE2` is preserved.

## Validation and state

- Six native-cohort Python tests pass, including valid visual edits, immutable-code rejection and invalid light/material rejection.
- Four existing rendering-profile tests pass.
- The rebuilt renderer is byte-identical: `B0A157DE420975E7C199DC440E51204C797A7A7AEA44E20CF446F8A8A0E16D3C`. No renderer code or light settings changed.
- Preparation receipt refreshed from the existing same-renderer GPU fixtures plus the new Python guard tests. No additional GPU campaign or SFC launch was needed.
- Actual read-only preflight passes with the current edited lighting profile and completion diagnostics enabled. Whitespace checks pass.

Use the same native multi-ship launch command. No manual cleanup or setting rollback is required. The separately identified cold dome-environment file-opening wait remains pending preparation work; this fast run does not establish that it cannot recur. Changes remain unstaged and uncommitted.
