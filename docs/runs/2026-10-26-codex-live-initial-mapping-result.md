# Run198 — first mapped ship appears promptly; enhancement still waits for later activity

Date:2026-10-26 America/New_York. Review of sponsor run041742. No implementation/config changes, new game launch, stage, commit or push. Parent93e8dba; accumulated Run194–197 work preserved.

## Sponsor observation and accepted result

Sponsor confirms correct texture mapping from first appearance, about1s to load. Sponsor suspects an enhancement/texture shift when a shuttle launched(estimated about60s) and reports no visible frame loss. The enhancement observation is explicitly uncertain. No additional unreported HUD/control assertions are inferred.

Actual first matched returned image0.9821716s from earliest fresh asset discovery; initial FCA native admission about1.2505378s. These are different completion points and support prompt base-first delivery, not fully enhanced readiness. Original image files/captured geometry/UVs remain unchanged. The first-submission Remix origin correction is now confirmed in actual gameplay, superseding Run197's gameplay-pending qualification.

Three owners/three assets:KFF,FCA,FMS(shuttle), all ACK1. No invalid/rejected/partial assets. Normal game/renderer exit, drained/unloaded gate, proxy restoration, unchanged client hashes and launcher settings passed. User-observed smoothness does not establish zero omitted returned frames:30post-start Remix-image omissions across5185paired returns,longest4consecutive. These are overlay delivery records, not proof that SFC lost frames. Latest-state/coalescing drops likewise are not SFC frame losses.

## Material handoff timing

CPU enhanced master publications occurred at0.4682819s(KFF),0.962811s(FCA),42.2045789s(FMS), measured from the first fresh captured-asset discovery. The sponsor's approximate60s uses an unspecified starting point; do not treat that as contradictory or invent a manual timestamp.

First logged FCA replacement-DDS processing starts00:18:38.874local. The shuttle-triggered master file was finalized00:18:38.804333local, roughly70ms earlier. Initial enhanced FCA stage was finalized00:17:57.515273. CONFIRMED:the initial enhancement was prepared far earlier than its first logged runtime consumption, which follows the later library publication. STRONG HYPOTHESIS:initial change notification/stage consumption was missed or delayed until the later publication. Not yet proved:exact file-watcher defect, runtime material installation time, or the precise rendered-pixel transition. No continuous screenshots and no supported material-ready ACK exist in this path.

The shuttle's native asset CPU preparation also measured5.449451s; retain as an unresolved late-latency case despite smooth game observation. Its generated base/enhanced worker stages were ready quickly. Do not conflate that native interval with game thread stalls or claim arbitrary late models are instant.

## State and next step

Curated metrics/log anchors/provenance: `docs/reconnaissance/evidence/20261026-live-initial-mapping-result.json`. Run197's549tests/normal+candidate graphics gates remain current; not rerun or relabelled as new tests for this review. No source/settings edits, so no qualification invalidation. Useful generated asset copies may be SHA-verified ZIP archived after this review; raw gate packets/logs/receipts remain.

**Exact next action:** isolate first material-library publication/notification and runtime reload using this repeated actual failure plus the retained capture. Keep the working initial mapping/base-first path unchanged; do not wait for enhancements, reintroduce rejected metadata touches, retune appearance or redo seam discovery. No further sponsor gameplay is needed merely to confirm that this issue recurred.
