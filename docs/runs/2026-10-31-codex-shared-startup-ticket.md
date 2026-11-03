# Run244 — shared-memory startup ticket implemented

## Changes

Reviewed Run243's direct WdFilter timing:6.009536s holding open the104-byte activation file,essentially the whole host open. Reviewed published HEAD and local M1StartW:LiveChannel is read from disk configuration before mapping attachment. **That bootstrap is unchanged.** Renderer receives the existing precreated session name through environment and uses a separate cell in that same protected mapping;no dependency on M1 attaching first. [Versioned startup contract](../reconnaissance/startup-ticket-contract.md).

- Added256-byte one-shot startup cell at4096 in unused protocol4 metadata;existing16MiB mapping/four asset slots unchanged. Reuses mapping ACL and native process-handle synchronization/established bounded idle cadence;no new event ACL or global setting.
- Moves activation,private warm-up readiness and idle cancellation to shared memory. Old104-byte packet/checksum/identity/extent validation preserved. Host/supervisor/game/session binding,immutable publication,replay rejection,duplicate-host exclusion,partial publication handling and process-death cleanup qualified.
- Supervisor initializes before host launch;native host publishes ready after GPU warm-up. Enhancement readiness and final warm-up receipts now read memory. No scene/model/material/light/image or game-configuration changes. Source qualification includes the new ticket header and Python producer.
- Changes remain unstaged/uncommitted. No repeat discovery trace,Defender exclusions,security-policy change or SFC gameplay run.

## Validation

-22actual x86/x64 consumer cases through real current-user SceneChannel:normal and early publication;cancel before/after readiness;incomplete publication;CRC/session/game mismatch;replay;duplicate host;game exit;supervisor exit and attempted live mapping reuse. Uses the actual warm_start consumer without a GPU/game.
-5Python startup tests,13existing async-material tests and3native-cohort tests pass. Checks current/bootstrap source ordering and absence of legacy disk activation/readiness/cancel in active host. Native worker and actual host compile /W4 /WX.
- Two normal standalone600-frame GPU checkouts,three retained owners/two unique assets+shared third:Strict `20261101-024857-102527-return-fixture`,ExtraFrame `20261101-025149-322900-return-fixture`. Both verify pixels,physical depth,subsequent native text,zero state errors,normal child/renderer exit and remaining_owned_processes0. Same60s synthetic menu-idle condition as the archived startup baselines;no WPR or external sampler. Strict was the first IPC build;ExtraFrame includes final QPC receipt/unknown-state guard. No renderer-path changes between those builds.
- Existing native-cohort qualification refreshed for both policies;native-light qualification and normal all-ship launcher dry preflight pass. git diff --check passes. No SFC was automatically launched. Normal gameplay remains sponsor checkout,not an automated result.
- Rebuilt the parked legacy1.5.2 diagnostic host against its pinned header as well,so it cannot retain the obsolete file handshake. Compile-only compatibility check;no legacy runtime campaign or runtime upgrade.

## Measured startup:isolated ticket fixed,overall startup still variable

Times are existing QPC startup markers,not physical display/interactive-game appearance. Independent runs differ in cache/system conditions and timing policy;do not present as a controlled FPS benchmark.

| Standalone run | Activation intent to activated | Asset discovery to first completed cohort output |
| --- | --- | --- |
|Old file,untraced Strict baseline `20261031-215931-280933`|5513.97ms|6582.10ms|
|Old file,Defender-traced Strict `20261101-012254-316417`|6040.01ms|8378.44ms|
|New IPC Strict `20261101-024857-102527`|11.03ms|478.03ms|
|New IPC ExtraFrame `20261101-025149-322900`|13.22ms|6088.40ms|

Once the host sees the ticket,validation/environment setup takes1.008ms/0.090ms in the two new checkouts. Final shared receipt in ExtraFrame shows published-to-accepted6.657ms. There is no activation-file access to incur its identified Defender delay.

**Remaining limitation:** ExtraFrame's slow total startup is after activation:scene load~0.339ms,material-enable call~0.158ms,then **5002.19ms between materials_enabled and receiver_started**. That source range contains scene.bin reread/hash and OutputPeer.start (including child process creation). Existing markers do not isolate which call blocked or establish Defender caused this different delay. No CPU/GPU/material inference or unrelated fix is justified. Strict's same interval3.97ms. Preserve this finding as the next narrowly scoped startup investigation;do not claim consistent sub-two-second startup.

## Evidence and storage

`artifacts/player-replacement/run244/startup-transport-tests.json`, `startup-comparison.json` and actual run reports/logs. Shared-memory QPC receipt lives in the final run's live_owner_timing.multi_scene.startup_transport. Existing appearance/config hashes and copied/original client checks remain qualified by normal preflight.

To make room within the existing20GB allowance,35closed successful runs' converted texture packets were archived losslessly,with per-file hashes verified before loose copies were removed (~765MiBreclaimed). Original captures,geometry,logs and game assets unchanged;restoration receipts remain in each run. No evidence limit increased.

**Next:** sponsor can use the existing native multi-ship launcher for gameplay checkout. Further startup optimization should isolate the post-activation receiver-start interval using existing evidence/narrow markers,without changing materials or re-running broad Defender discovery. Ticket replacement itself is implemented and standalone-qualified;overall timing remains a partial performance result.
