# Run239 — detailed fighter-heavy stress review

Read-only analysis of `20261031-212549-867833-in-game`, extending Run238's preliminary checkpoint. No new gameplay,builds or pipeline/configuration changes.

## Delivery and coverage

-26owner identities across the session,all26 eventually inserted. Catalog:KDD1,KCV2,FCV3,FFT4,KFT14,KCA1,KCL1. These are identity/model assignments,not the number of visible fighter bodies. Sampled renderer frame2369 contains25distinct tracked owners together,establishing a lower bound on concurrent tracking,not the exact peak or visible count.
-7unique renderer assets,19shared-content reuses.26captures/ACKs,no capture failures,owner overflow,rejected assets,partial preparation results,unfinished jobs or unsent transfers. Retained ship asset cache49,143,288bytes (~46.9MiB);this is not total Remix VRAM.
- After first insertion,**5,006/5,006 recorded frame requests inserted**,with no no-request gaps,invalid commit ordering,deadline misses or accumulating source queue. Maximum output occupancy1. The complete header records5,025requests and37,579owner insertions;earlier preparation requests are separate from steady delivery.
- All gate deadline/stale/invalid/partial/dropped counters are zero. Median gate wait8.639ms,p9510.875ms,max13.986ms. Median source-to-display age11.789ms,p9514.220ms,max19.532ms. These gameplay runs are not identical controlled comparisons with earlier missions.
- Native frame interval:median16.691ms (~60FPS),p9517.833ms,p9918.717ms,max30.895ms. Zero admission misses does not mean perfectly flat presentation;the maximum is nearly two60Hz periods. Sponsor visual feedback has not yet established whether those long frames were noticed.

## Missing-draw counters explained

The342renderer `omitted` increments occur only when a tracked owner has no resident asset yet (`MultiSceneRuntime::draw`);they are asset-readiness omissions,not projection rejections or GPU deadline misses. Per-owner game-side membership-unavailable receipts total25:19for FFT owner8 and6for KCL owner26. Other owners still inserted in those frames. Exact per-owner duration for all342omissions is not retained in performance mode;do not claim they were all invisible or convert them into342whole-scene dropouts.

Suppressions total92,124because the native hook counts suppressed wrapper/list submissions,while insertion counts committed owner operations. Native source increments suppression after each qualified zero-count submission. All non-fighter catalog owners have equal insertion/suppression totals in this run;fighter owners have more suppression receipts. This is a useful retained clue for SFC-22,but does not establish whether the game draws1–4bodies,submodels or repeated passes. That investigation remains deferred.

## Startup remains the main concern

- First successful insertion:frame407,**6.7605seconds after the first recorded native frame**. This is not launcher startup time,and does not meet the intended sub-two-second appearance target.
- Renderer warm-up completed ~71.886seconds before first asset discovery. Startup policy was onePresent,legacy24off. Device initialization was therefore not the source of the six-second tactical delay.
- Initial unique base preparation from discovery:KCV157ms,KDD214ms,FCV398ms,FFT721ms. Their enhanced stages completed within571–907ms. The coordinator's activation-intent timestamp is217.9ms after first discovery.
- Host `activated` marker occurs5.8654seconds after discovery:an **observed5.6475second gap** after coordinator intent. The exact delay between entering launch,publishing the activation file and the host observing it is not separately recorded. Do not attribute it conclusively to the file signal,OS scheduling,material loading or GPU rendering without narrower evidence.
- After host activation,the first bootstrap output completed~63ms later;its first receiver ACK took another~167ms. First recorded multi-owner output followed shortly afterward. Those do not account for the preceding5.65second activation gap.
- Later entirely new KCA/KCL content reached GPU admission~105ms/~75ms after discovery. These are admission timestamps,not measured first visible pixels. Their base preparation was53ms/41ms and enhanced preparation104ms/48ms. KFT discovery occurred during the startup backlog,so its initial~4.72second discovery-to-admission delay must not be presented as a normal later-arrival cost.

## Tracking,diagnostics and cleanup

Persistent tracking published118,137poses,including110,941offscreen;26admitted,15destroyed,zero rejected/failed functional updates. Three diagnostic calibration misses and18nonwaiting mailbox drops did not cause functional gate rejection. Lights:5,025cache reads,zero failures/unavailable updates.

Detailed source diagnostics filled32,768records by frame2055,discarded53,726later snapshots,and recorded24diagnostic-invalid observations. These are separate from the zero invalid scene decode/gate records. The detailed diagnostic covers only the first eight tracked identities;it cannot establish later camera/owner behavior for the whole fleet. Gate timing records and aggregate registry/renderer counters remain available throughout.

Normal game/renderer/controller exit,controlled unload,proxy rollback and unchanged accepted client/launcher hashes all pass. No owned game/renderer processes remained at the prior checkpoint. Original settings/assets untouched. Analysis and raw-input hashes: `artifacts/player-replacement/run239/review.json`, `additional-review.json`, `analyze.py`.

**Assessment:** successful sustained replacement with shared fighter assets at the observed population. Not100-object gameplay proof or universal model coverage. **Smallest next performance investigation:** timestamp activation-file publication and host observation separately to isolate the5.65second gap;first inspect existing signal/file evidence before requesting another gameplay run. Collect sponsor visual observations for this run. No appearance changes,new buffering or fighter-multiplicity fix justified by this review. Changes remain unstaged/uncommitted.
