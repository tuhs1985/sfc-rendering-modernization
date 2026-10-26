# Run181 — sponsor live run: verify enabled preparation policy

Sponsor reports initial appearance around4–5seconds, no apparent loading-speed
change. No additional visible-behavior answer inferred. Reviewed existing captures
only; no game/renderer launch, settings change, rebuild or implementation edit.

Latest completed run: `artifacts/remix-runtime/runs/20261025-190849-779718-in-game`.
Performance mode recorded in manifest/result/native multi-scene report; detailed
evidence false. Both material reports explicitly record performance mode,
upload_pixel_comparison=false, source_recomparison=false and32MiB decoded cache.
Thus Run179 trims were enabled. Four preparation workers were used. No
parallel_parts flag; legacy identify→prepare spans and initial-batch barrier
confirm Run180's new dependency graph/progressive publication were **not enabled**.
This is the stable launcher supplied explicitly, not a failed activation of the
new path. It cannot assess the new pipeline's loading benefit.

Relative to first observed asset discovery:

| Stage | Asset1 | Asset2 |
| --- | ---: | ---: |
| Identification completed | 60.18ms | 134.78ms |
| Preparation completed | 352.89ms | 1390.75ms |
| Native renderer admitted asset | 4355.95ms | 4398.15ms |

Renderer activation1.5001151s after discovery. First prepared ship therefore
still waited for the initial batch. Device prewarm began about12.26s before
discovery and its ready receipt preceded discovery by about9.91s: prewarm enabled,
not a late process launch. Activation→native admission about2.856s/2.898s remains
downstream. Admission timestamp is not physical display or exact first-output
timing; it is consistent with sponsor4–5s impression. Do not attribute the entire
gap to one runtime operation without further evidence.

Both owners admitted/no asset rejection/partial;5393draws per owner. Normal game
exit, gate unload/controller0, renderer0, restored proxy, original critical hashes
and launcher settings unchanged; final report complete/error null. Latest run
duration147.64s includes preparation/menu time. Earlier190802run ended before the
requested tactical window, with normal owned exit; partial-duration evidence,
not another full performance result or a parallel-path failure.

No new speedup or milestone claimed. Run180 progressive delayed-material gate
remains unresolved and that route stays offline-only. Next action remains supported
non-disruptive material consumption, using retained standalone evidence. Changes
unstaged/uncommitted; HEAD9ff2d3d/no push.
