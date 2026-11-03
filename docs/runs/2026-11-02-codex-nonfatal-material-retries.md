# Run274 — delayed material updates no longer terminate rendering

## Behavior

Sponsor explicitly requested removal of the five-second material-publication stop rule after Run273's Windows replacement fix. `progressive_scene_relay.Relay.retry_publication` now treats access-denied publication as pending work for as long as the session remains active. It retains the last accepted materials and continues ordinary base-mesh, transform and output processing. Once publication succeeds, the latest available stage/library is delivered and pending completion storage is released normally.

The existing set of pending asset IDs and single pending-library flag coalesce repeated updates instead of appending retry jobs. Existing scene/resource budgets still apply. A blocked asset does not prevent another asset's publication. No sleep, rendering callback, blocking retry loop, new thread, image reconstruction or additional refresh limit is introduced.

Five seconds now triggers one short warning per continuous denied-publication episode, not shutdown. Cumulative retries/warnings and a single capped latest-error record identify operation, asset, errno, Windows code and message. Final evidence records unresolved pending counts and duration. It does not claim that file publication proves runtime consumption. Unresolved enhancements on exit remain a documented partial result.

This change handles `PermissionError` only. It does not hide malformed material definitions, disk exhaustion, lost renderer, broken output ownership or failed partial-exchange recovery. Existing stop/cancel/process-exit paths remain unchanged; pending updates cannot keep an ended session alive.

## Verification

-80 targeted regressions pass. New cases simulate denial beyond five seconds through a full day of monotonic time, verify one warning/coalesced latest generation/no early storage release/recovery, prove another asset can publish independently, and preserve serious non-permission errors.
- Strict fixture `20261102-225158-762744-return-fixture` deliberately denies the master publication for seven seconds while retaining the normal production retry coordinator and GPU renderer.256denials across6.984s; successful publication7.078s after first denial. Exactly one warning, no unresolved stages/library or asset partial results,600frames, three owners, correct colour/depth/text and graphics state, normal exits and owned children remaining0. Fault injection lives only in the ignored artifact supervisor; it is not in normal code or configuration.
- Ordinary ExtraFrame fixture `20261102-225256-523588-return-fixture` also passes600frames with zero retries/warnings, no pending materials/partial results, correct rendering/state and owned children remaining0. Existing cohort qualification refreshed from these two passing results; read-only normal gameplay preflightPASS. No game was launched.
- Production `ReplaceFileW` change remains active. Appearance and original assets are unchanged. No SFC launch, new discovery trace, security change, staging or commit.

Evidence: `artifacts/player-replacement/run274/`, including focused test output, fault-injection supervisor/receipt and fixture console records.

The existing `start_native_multiship_session.ps1 -CompletionDiagnostics` command is ready for sponsor stress checkout. Keep changes unstaged and uncommitted.
