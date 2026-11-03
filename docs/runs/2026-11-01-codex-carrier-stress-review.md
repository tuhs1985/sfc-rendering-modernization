# Run259 — Carrier stress review: fast admission, hidden terminal replacement stop

Reviewed `artifacts/remix-runtime/runs/20261101-213029-855985-in-game`, plus the preceding failed startup `20261101-212923-081226-in-game`. No implementation changes or new gameplay. Derived evidence: `artifacts/player-replacement/run259/carrier-analysis.json`.

Sponsor: no long pause and no problems noticed. This supports normal visible gameplay, but does not override the terminal-stop evidence below.

## Coverage and loading

- First queued native insertion: **850.7366 ms** after the first recorded native source-frame start. This excludes scenario selection and renderer prewarming, and is not measured physical display latency.
- **29 object identities**, **12 unique content assets**, all 29 catalog associations acknowledged; no asset rejects, preparation partials or invalid live updates. Repeated ships share content. Model families: KCA, GFA, FCV (three), FFT, GFT, KFT, RFT, KCL, HDD, HFT, LPFT and LDD.
- Persistent registry: 169,027 pose updates, 162,131 offscreen updates, seven destruction retirements, no failed updates. These are cumulative run identities, not 29 proven simultaneously visible ships. Grouped fighter drawings can contain several physical hulls per owner; counts are not interchangeable.
- 27 identities have owner-specific insertion receipts; the last two FFT identities were renderer-drawn/accepted but have no native insertion receipt. Do not claim every accepted object was replaced on screen.
- Native asset preparation: 0.687–24.547 ms per unique asset; GPU admission 0.006–4.144 ms. Protected scene/image mapping peak 37,084,320 bytes; all mappings released. Twelve unique memory transfers acknowledged versus 29 catalog references is expected sharing, not 17 lost models.

## Stability: partial, not full-run success

Native gate header ends with **partial=1, stop=1**. Last newly initialized replacement source frame is **4395**, starting **78.284 seconds** after the first recorded source start. The following 714 saved presentation records reuse that same frame, sequence, hash, outcome and start timestamp until 90.190 seconds.

Offline code inspection explains the misleading tail: `native_gate::begin` stops resetting `current` after header.stop; `d3d9_game_receiver::step` can still append `current` while return-path armed and not globally stopped. Therefore raw analysis counting 5,052 commits and reporting 11.9-second frame age is not proof of continued fresh insertion or an accumulating renderer queue. There are **4,395 distinct source-frame records, 4,338 committed**. Terminal replacement disable means subsequent ordinary drawing remains native; stale log outcomes are not evidence of stale pixels being inserted.

There were 57 original/missed frames across distinct records: 43 before a request, 14 admission misses. Nine misses follow the first commit: four during immediate initial settling (0.905–0.989 seconds), then five isolated frames around 7.077, 8.169, 8.327, 12.741 and 40.478 seconds. Twenty owner-unavailable observations occurred among later arrivals. No evidence-ring overflow or omitted owner receipts.

Advancing-source native duration: median 13.563 ms, p95 18.879 ms, p99 19.969 ms, max 27.801 ms. Presentation intervals: median 17.200 ms, p95 20.685 ms, p99 22.253 ms. One 187.404 ms gap occurs between frames2186/2187, around41.3seconds. The next frame begins late and commits normally; max measured coordinator wait is17.008ms. This gap is not explained by a187ms insertion wait. Underlying game/OS/renderer scheduling cause is unresolved.

GPU resource failures, invalid output, busy-slot failures and depth-missing counters are zero. Consequently the terminal partial flag is consistent with one of the native hook's terminal consistency/reentrancy branches or a dispatch exception; available counters cannot identify the exact branch. Destruction/secondary-submission changes are candidates, not established causes. No reason code is recorded for those branches. Do not weaken checks based on this run alone.

## Cleanup and separate startup attempt

Completed carrier run: error null; game, controller and renderer exited normally; controlled hook restoration/unload and proxy/config restoration confirmed; original/copied critical hashes unchanged. No owned named processes remain. It completed the timed observation, so it **does not validate early-exit cleanup** from Run258.

Preceding attempt failed before tactical capture: `M1StartW failed:5`; its thread-transaction receipt identifies `SuspendThread`, error5 (access denied), thread30992, rollback-resume failures0. This was a hook-installation failure, not excessive carrier assets or a late asset-load failure. Game was still alive when that attempt reported deferred proxy rollback. The subsequent completed run verifies restored baseline. No new Windows/Defender attribution is established.

## Next exact work

Investigate terminal stop at frame4395 first: add a bounded, one-shot reason/frame/owner record to existing terminal-stop branches and exclude repeated stopped-source records from timing/commit analysis. Do not rebuild the asset system or run a broad discovery trace. Keep that work separate from the pre-tactical SuspendThread denial and cold dome preparation. No runtime fixes performed in this analysis; changes remain unstaged/uncommitted.
