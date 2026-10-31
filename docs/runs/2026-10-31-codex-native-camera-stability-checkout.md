# Run234 — multi-ship camera stability checkout

Sponsor aggressively switched cameras and reported no visible switching between native and enhanced ships. Reviewed existing gameplay evidence only; no renderer changes or additional gameplay were performed.

## Evidence and result

- Run: `20261031-201605-812803-in-game`, Strict timing, performance mode, one startup Present. The legacy 24-Present workaround was disabled.
- All six fresh assets reached replacement: KDD, FDD, FFF, FCA, RCL and LFF. Their six asset revisions were loaded once, with no camera-triggered geometry reconstruction. There were 13,809 owner insertions and 13,809 matching suppression receipts.
- First insertion was 0.768 seconds after the first recorded native frame. This is a recording-relative measurement, not total launcher or scenario-loading time.
- After first insertion, 5,321 recorded requests comprised 5,314 inserted frames, two deadline timeouts and five acquired-output frames without an eligible owner insertion. Those five frames occurred during initial RCL admission at about 25.8 seconds; they were not repeated camera reloads. LFF separately had six membership-unavailable observations during admission while other owners still inserted.
- The two deadline misses were isolated at 1.283 and 2.350 seconds. No further deadline misses occurred after 2.4 seconds through the remaining approximately 87 seconds of observation. Four additional deadline misses preceded first insertion. There were no no-request records after first insertion.
- Renderer input/identity/decode rejection counters were zero. Projection comparisons were disabled in performance mode, as intended; their zero audit count is not a claim that every projection comparison passed. There were no light read failures or unavailable updates. Two diagnostic calibration snapshots were missed without rejecting functional scene updates.
- Persistent registry: six admitted, zero destroyed/rejected, 39,673 pose updates/publications, including 32,523 offscreen updates; zero failed functional updates.

## Timing and integrity

- Native frame interval: median 16.719 ms (about 59.8 frames/second), p95 17.932 ms, p99 19.412 ms, maximum 25.540 ms.
- Source-to-display age: median 15.524 ms. Gate wait: median 12.564 ms. Median returned-pool readiness remained approximately 12.413 ms; this was not a large GPU-speed improvement. The results support removal of false submission vetoes as the main improvement, but these are not identical controlled gameplay runs.
- No invalid recorded commit ordering, dropped gate records, invalid gate records, partial commits or accumulating source queue. Maximum output-slot occupancy was one.
- Normal game and renderer exit; hooks unloaded, copied proxy restored, launcher settings and accepted client critical hashes unchanged. Evidence occupies 217,012,753 bytes (about 207 MiB).
- Detailed callback diagnostics reached their existing 32,768-record cap and discarded 25,180 later snapshots; zero malformed diagnostic records. Their camera evidence ends at frame 3269. Full gate records and aggregate functional counters remain available; detailed diagnostic snapshots do not cover every later camera transition.

## Scope and next action

This is a successful sponsor checkout of the qualification/light fixes under this mission's conditions, not a universal zero-fallback guarantee. The newly admitted Romulan was RCL; this does not resolve the earlier RDE cloak-path question. Weapon lighting, damage textures and break-model transitions remain separate alpha requirements. Per-light persistence configuration remains pinned for later.

Analysis, raw-input SHA-256 hashes and bounded diagnostics: `artifacts/player-replacement/run234/review.json` and `analyze.py`. Raw evidence remains local/ignored. Implementation changes remain unstaged and uncommitted. Next action is sponsor choice of the next increment; no additional buffering or renderer changes are justified solely by this checkout.
