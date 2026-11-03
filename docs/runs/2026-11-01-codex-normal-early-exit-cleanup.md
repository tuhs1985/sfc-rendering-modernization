# Run258 — Normal early exit owns cleanup

## Request and change

Sponsor may exit SFC normally at any time, without waiting for the recording cue. The runner now recognizes that exit during graphics startup, mission selection, asset preparation, tactical observation and component removal. It stops collection and immediately enters its existing cleanup path instead of reporting a shortened observation as a game failure or waiting for the observation watchdog.

`tools/remix_runtime/session_exit.py` keeps a synchronization-only handle to the verified copied game process. Running checks perform no file reads; after exit, the launcher must retire within five seconds and provide its normal `CHILD_EXIT code=0` receipt. Wrong-path validation remains mandatory. A nonzero exit, missing normal-exit receipt or failed cleanup remains an error.

Cleanup stops the relay/service/preparation workers before analysis or shared-memory release. The controller can be retired after confirmed game exit only; it is never forcibly stopped while it owns hooks in a live game. Existing renderer stop/cancel deadlines, owned-process guard and GPU-resource lifetime rules remain unchanged. Proxy/config rollback still requires the game to have exited, and client hashes are checked afterward.

Shortened runs retain completed evidence and receive `PARTIAL_DURATION_NORMAL_EXIT`, with exit stage and observation-complete fields. Pre-output exits use a specific partial result rather than requiring a nonexistent output-pool receipt. GPU job cleanup and worker errors remain checked. Process-exit reclamation is recorded separately from controlled live hook restoration; this change does not claim Windows reclaimed hooks were explicitly unloaded.

## Validation

- Ten focused exit tests: live polling without file access/waits; normal versus abnormal receipts; launcher/process-exit race; actual Windows child-process handle lifetime; startup-wait propagation; cleanup-before-analysis ordering; controller retirement only after game exit; partial pre-output versus genuine worker/GPU cleanup errors.
- Existing controller shutdown (5), graphics startup safety (13), and warm-start (5) tests pass.
- No native renderer source change. Rebuild reproduces SHA256 `B0A157DE420975E7C199DC440E51204C797A7A7AEA44E20CF446F8A8A0E16D3C`. Existing same-renderer Strict/ExtraFrame GPU qualification evidence is reused; no new GPU campaign or SFC launch required.
- Launcher preflight initially exposed insufficient evidence reservation. Closed successful-run converted DDS copies are losslessly archived with per-file hash verification and recovery manifests; source captures, logs and original game assets remain intact. See `artifacts/player-replacement/run258` for local verification receipts.
- Final actual launcher preflight passes after restoring reservation and refreshing the existing standalone light-worker receipt. No SFC started. `git diff --check` passes. User-edited lighting file remains untouched (current SHA256 `F6CC60D4C2671E8876820BD3A8CAEFB0740EFF64383C4CB15208AF27CD68D4DD`). Obsidian tracker updated only after its previous contents matched exactly.

## Limits and next action

No sponsor gameplay early-exit checkout has been performed for this increment. Use the same native multi-ship launcher and exit normally whenever finished; confirm the next launch starts without manual cleanup. Cleanup can take its existing bounded drain time; it does not wait for the remaining 90-second observation duration. Crashes or failed restoration still need review. Cold dome-image preparation remains a separate pending issue. Changes are unstaged and uncommitted.
