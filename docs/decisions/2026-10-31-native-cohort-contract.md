# Native multi-ship insertion — membership extension v1

Extends the [native insertion contract](2026-10-31-native-gate-contract.md). Default off; copied installation only. The existing same-process Acquire → Commit interface and original capture format are unchanged. No Toolkit, shield replay, appearance changes or alternate renderer is introduced.

Run232 update:screen-position agreement is diagnostic evidence,never a scene/owner admission gate. Transient light-update or calibration-mirror loss does not veto valid geometry publication/rendering. Last accepted lights retain their existing identity/freshness bounds;expired lights are removed. Startup uses one Present;`-LegacyStartupWarmup` explicitly restores the old24-Present workaround. [Implementation and checkout](../runs/2026-10-31-codex-nonblocking-submission.md).

Run233 scene-light clarification supersedes the timed-retention clause for the current encoded scene0/1+project-fill channel:accepted values persist for the scene session and scheduling-owner changes,with explicit config OFF still honoured. No timestamp refresh or cross-session reuse. Temporal validation remains the default for other callers. [Policy and evidence](../runs/2026-10-31-codex-persistent-scene-lights.md).

## What is shared, and what is separate

One completed Remix scene serves a native source frame. The first eligible ship may wait until the existing Strict or ExtraFrame deadline. Later ships reuse that already admitted immutable image; they do not start another wait, renew the deadline or request another render. Each ship still inserts at its own qualified original mesh boundary, before its later native effects and text. Unsupported invocations remain native.

Colour remains genuine Remix output. The existing physical hull pass writes native depth and owner identity together into the existing R32 depth/coverage images. Depth testing selects the nearest submitted hull at every pixel. This replaces the diagnostic union mask only in multi-ship replacement mode. An owner's insertion reads only pixels labelled with that owner's epoch. Shared geometry does not imply shared ownership or suppression permission. Captured geometry, UVs, normals and images are unchanged.

The renderer records only members whose mesh was actually submitted. A fixed versioned manifest binds session, full source frame/sequence/cohort hash, output sequence, anchor identity and up to 32 owner/revision/model/source/asset/content-hash tuples. The GPU copy worker validates each member against the source cohort and asset catalog. It publishes the corresponding slot's manifest before signalling READY, after the GPU copy fence completes. Missing members are not authorized merely because their assets exist.

## Storage and lifetime

`native_cohort::Store` occupies 6,464 bytes at replacement reservation +58,880, ending at +65,344 inside the existing 65,536-byte reservation. It does not overlap the older native gate store. It contains one upstream manifest, two game-slot manifests and 32 bounded owner/revision counters. There is no additional shared image or mapping. Existing two-slot output resources and the 128 MiB envelope remain.

The game adapter holds the shared output slot for the entire native frame. Every successful owner insertion extends its GPU-read fence. The release worker cannot retire a held slot. Present, or the next native source frame, releases the frame hold; the worker then waits for the last queued GPU read to complete before recycling. A failed later owner cannot cancel resources already used by an earlier owner. Existing stop/drain and terminal retention rules still apply.

The native capture component maintains 32 independent owner/frame decisions. Original observations precede coordination, outside the observation lock. A successful commit authorizes count-zero primary and secondary submissions only for that owner/revision/frame and original list identity. Retirement, unsupported geometry, changed revisions, stale tickets, unknown callers and nested ambiguity do not borrow another owner's decision.

## Reporting and qualification

`NATIVE-COHORT-001` saves the bounded membership/counter sidecar at exit. Per-owner counters distinguish insertions, suppressed lists and unavailable output. Suppressed counts are list counts, not necessarily frame counts. A slot reused by multiple owners still represents one scene output. The older native gate ring remains one record per native frame; its last owner fields are not a complete list of owners. Use the cohort receipts for owner totals.

The standalone fixture uses two distinct captured meshes plus a third owner sharing one mesh. Synthetic owner/state metadata is explicit; this is not a fresh gameplay capture. It checks actual returned pixels, native near/far effects and depth-disabled text, plus shared geometry reuse. Deterministic worker delays intentionally exercise unavailable output. These counts do not establish seamless normal gameplay.

Prepare with the existing native/receiver/candidate-host builds and `tools/native_insertion/qualify_cohort.py`. Qualification freezes inputs and standalone evidence, never sponsor acceptance. Launch `tools/native_insertion/start_native_multiship_session.ps1`; Strict is the default, ExtraFrame remains explicit. The old player-only and offset launchers remain separate. No user settings file is edited.

Limits remain: 32 active owners, 64 qualified revisions, established rigid triangular path, two output slots, 32 MiB logs, 20 GB aggregate evidence, 90-second tactical capture and 285-second prepared workflow. Damage substitutions, break models, unknown draw families, transparent hull coverage and arbitrary deformation are not newly qualified by this extension.
