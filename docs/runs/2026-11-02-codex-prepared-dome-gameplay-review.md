# Run272 — gameplay checkout and material-publication recurrence

Read-only review. No production code, settings, launcher, hooks or active processes changed. Sponsor says the first run was not the full stress test; do not label it maximum-load qualification.

## Completed first run

`artifacts/remix-runtime/runs/20261102-223035-971545-in-game`:

- Sponsor: fast onscreen loading, one barely noticeable blip.
-26 qualified owner/revision entries, nine distinct model paths, no rejected assets or partial asset results.26 owners have insertion records;60,852owner insertions and124,320native-list suppressions. These are not per-frame totals or26 simultaneously visible ships.
- Physical hull helper reports capacity256, omitted0. Prepared project dome adopted once, recreated0. Material publication retries0. New effect lights remain outside this checkout.
- First insertion at frame55,0.9654103s after first gate record;0.5929915s after earliest retained asset-preparation span. These are specific measured boundaries, not time from clicking Start or first visibility of every enhanced material.
-4,805gate-frame records:4,746insertion frames,59original frames overall.54original frames precede the first insertion; only five follow it. Each of those five is an isolated timeout(frame56,61,1594,1604,1700). No consecutive post-startup timeout streak. Their start times relative to first gate record:0.990s,1.103s,29.496s,29.723s,31.598s.
- Longest of these frames is36.692ms from source-frame start to recorded presentation callback; largest consecutive presentation interval38.848ms. Typical frame interval18.640ms, p9520.289ms, p9922.058ms. Typical source-to-presentation age16.875ms. No claim of actual scanout/input latency.
- Later admissions occur around29.57–29.70s and material publications29.63–29.80s, near two timeouts. This is correlation, not attribution to asset work/camera/sponsor's exact observed blip. No manual timestamp was requested. Five timeouts alone cannot identify which one was seen.
- Queue maximum1; source-to-presentation age remains roughly16–18ms across the run. Reference drift against ideal60Hz grows because actual rate is lower, not evidence of an accumulating output queue.
- Source-timing diagnostic ring saturates(32,768retained), with its historical diagnostic owner limit counter120,790. This is partial diagnostic coverage, not26accepted assets being rejected or the removed hull32limit recurring. Gate evidence has0dropped records. Do not use the partial source log for whole-run absence claims.
- Normal exit, renderer/controller exit0, controlled gate unload verified, owned GPU children remaining0, original client/launcher configuration unchanged.

Compact derived receipt: `artifacts/player-replacement/run272/review.json`; read-only analyzer `artifacts/player-replacement/review_latest_game.py` calls the established gate-record parser. Raw records and original result are preserved.

## Second run — startup positive, later publication failure

`20261102-223621-511623-in-game` completed while the first was being reviewed. Sponsor explicitly confirms enhanced assets appeared quickly even in this failed run. Preserve that positive startup/appearance observation separately from overall result.

The error is the known `Material atomic publication sharing-busy for5s;preserve existing base`. No production ReplaceFileW change was active: Run271 remains an artifact-only proposal/control. Thus this is a repeat of the unchanged publisher/termination issue, not evidence that the proposed fix failed or that enhanced assets never appeared.

Renderer exit0, owned children remaining0, normal game exit and unchanged original client/settings verified. Gate controller exits8: target exited before controlled component removal, so gate_clean_unloaded=false. Do not call the second run's cleanup fully qualified; the process exit removed the component but controlled unload was not observed.

## Decision / next step

First run supports the Run270 dome/capacity fixes in ordinary multi-model gameplay, with rare isolated deadline misses. Full stress test still pending. Second run confirms fast initial enhancement delivery and reproduces the separate publication failure. Next implementation candidate remains Run271's standard Windows existing-file replacement plus nonfatal pending enhancement handling and documented partial-error recovery. Do not re-run startup discovery or change appearance based on these results. User has not yet requested production implementation of the material publisher fix in this review.
