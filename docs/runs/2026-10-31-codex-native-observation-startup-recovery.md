# Run223 — observation startup and interrupted-test recovery repaired

Sponsor reported the new tool failed and did not reset. Reviewed `artifacts/remix-runtime/runs/20261031-041312-132396-in-game` without changing its historical result.

## Cause and evidence

The controller reports `M1StartW failed: 3` and exits7 before tactical activation. The insertion observation header initialized with the expected session/PID, but contains zero events; replacement-ledger decoding failed. This narrows startup past the new observation initialization to the replacement handshake immediately afterward.

Run222 disabled the replacement receiver/presenter for read-only observation, but that same branch had also initialized the shared replacement ledger. Native startup and private output publication still require it. The fresh mapping therefore retained a zero/uninitialized ledger. Native startup correctly refused it. This is a harness defect, not evidence about native scene order or Remix output timing.

The game was still alive when the error handler attempted rollback. The runner deliberately deferred overwriting the loaded test proxy. Subsequent recovery did not recognize `NATIVE-INSERTION-001`: its allowlist included additive/multi-ship, but omitted the new observation and player-replacement probe names. This was a second harness defect. Unknown probe types must continue to be rejected.

## Repairs

- Add a shared, testable passive-ledger preparation function. Initialize only a fresh ledger with the established session/PID, validate existing identity, require Priming mode with zero suppression/commit counts. Construct no replacement presenter and grant no Active authorization. Actual receiver startup now calls this before declaring itself ready.
- Extend only the verified full-support recovery allowlist to observation and player-replacement transactions. Preserve the existing game-absence check, rollback hashes, all other critical input checks and atomic restoration. No broad unknown-transaction recovery.
- Regression reproduces invalid zero ledger, then verifies passive initialization, idempotence, wrong PID/session rejection, native frame receipt availability, no suppression/commit and Active-mode rejection. Recovery tests exercise both additional probe names, refusal while SFC runs, full restoration, and no remaining pending transaction.

## Recovery and checks

Verified no SFC/test-renderer processes remained. Ran exact-run recovery using the existing verified backups. `recovery.json` confirms proxy/config restoration and complete copied critical hashes; historical `result.json` stays PARTIAL. No pending supported transactions remain. Accepted game files/settings unchanged; no gameplay launched during repair. No assertion of normal exit or controlled component unload for the failed run.

Observer native tests295 checks each x86/x64; Python observer6 and startup/recovery13 pass. Actual addon and isolated candidate host rebuilt. Existing light qualification remains valid; distinct metadata-only qualification regenerated from tested inputs. Non-executing observation preflight and `git diff --check` pass. No full rendering campaign added, no appearance/suppression/timing-policy change. Changes remain unstaged/uncommitted.

Next: rerun the same `start_d3d9_native_insertion_observation.ps1` launcher. Original game picture only; usual F-CA, different enemy, camera/weapon/shield activity and brief pause/unpause. Keep SFC open through restoration until the two low beeps. Earlier insertion and matching-output timing remain unmeasured.
