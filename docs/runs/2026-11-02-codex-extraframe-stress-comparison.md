# Run276 — ExtraFrame stress comparison

Sponsor completed `20261103-015803-512323-in-game` and reports unexpectedly stable appearance. Folder timestamp is UTC; checkout occurred November2 local time. Read-only comparison against Run275 Strict stress; no source/config/default/qualification changes and no new execution campaign.

| Measurement | Strict Run275 | ExtraFrame Run276 |
| --- | ---: | ---: |
| Qualified owner revisions, all inserted at some point |72|63|
| Unique loaded models |17|15|
| Post-startup insertion frames |3,856|4,040|
| Post-startup deadline misses |96|0|
| Other post-startup non-insertion records |0|2|
| Median source-to-presentation callback |19.026ms|18.847ms|
| p99 source-to-presentation callback |25.535ms|23.649ms|
| Median presentation interval |22.298ms|21.949ms|
| p99 presentation interval |29.404ms|27.563ms|
| Maximum presentation interval |104.821ms|82.066ms|
| Maximum outstanding output occupancy |1|1|
| Material publication retries / unresolved updates |0/0|0/0|

## Meaning

ExtraFrame permits admission until33.333ms after the source-frame start, rather than16.667ms. It does not sleep until that limit or always delay a full frame. Output is admitted when valid and ready.54post-startup records in this run have readiness later than the former16.667ms deadline, yet the ExtraFrame run has no timeouts. This supports the deadline-headroom explanation for prior replacement flashes. The63vs72owners/different models and manual gameplay mean it is not an identical-workload performance experiment or a universal zero-flicker claim.

No full-frame increase in typical measured delivery age appears in this pair. Ages remain roughly18–20ms in rolling samples with queue occupancy1; no growing output backlog. These are callback timings, not input-to-photon/scanout measurements.

First insertion is frame44,0.710298s after the first gate record and0.677258s after earliest retained preparation.43records precede first insertion. Of4,042records thereafter,4,040inserted and two acquired output without insertion. The two records are frames2408/2409,51.736/51.766s,owner27; a new unique asset admission occurs in this same interval. Cohort unavailable counter5 is consistent with unready membership; no timeout, invalid gate or terminal failure was recorded. Do not label the entire run zero fallback or claim exact cause beyond the saved admission relationship without further inspection.

Two substantial presentation gaps remain, despite successful replacement in those frames:82.066ms at36.136s(62.395ms before next recorded source start,19.670ms within frame),81.181ms at33.684s(62.427ms before source start,18.754ms within frame). Another64.149ms gap occurs40.401s. Thus ExtraFrame fixes this run's deadline misses, not every whole-game hitch. The between-frame delay is still unattributed; no new trace requested.

## Capacity, resources and cleanup

All63tracked owner/revisions received insertions;15assets loaded and48sharedbindings. Native cohort86,512owner insertions, not displayed frames. No asset rejects or partial results. Renderer omitted634draw attempts before residency; hull capacity256 with0omissions. Existing prepared dome adopted once without recreation. All material updates completed with0retries/0warnings/0pending.

Normal game exit, controlled gate unload, renderer/controller exit0, owned children remaining0. Original client/launcher settings unchanged; complete final report and observation window. No code changes, staging or commit.

## Recommendation

Keep using the existing `-TimingPolicy ExtraFrame` option for further stress/functional checkouts. This is a recommended operating selection, not a changed default. Preserve Strict as the diagnostic comparison. Don't redesign timing or loosen identity/depth checks based on this result. Separate future work: residual initial-asset membership gaps and the unclassified between-frame hitches, only when warranted by priorities.

Evidence: `artifacts/player-replacement/run276/comparison.json`; read-only `artifacts/player-replacement/compare_stress_run276.py` uses the existing gate decoder, preserving original inputs. No additional sponsor action needed to validate these saved results.
