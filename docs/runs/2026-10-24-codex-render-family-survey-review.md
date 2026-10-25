# Run166 — two rendering-family gameplay surveys reviewed

Date:2026-10-24 America/New_York; raw directories use2026-10-25UTC.
Authority: repository handoff/Run165, RENDER-FAMILY-SURVEY-001 and approved
rendering-interface characterization. API work stays parked. No new renderer,
gameplay run, runtime probe, assets, tuning, staging, commit or push this review.

## Inputs and capture completeness

Sponsor: “two runs, second one i blew up the enemy before time ran out”. This
confirms the action, not its timestamp, exact effect membership or absence of
visible regressions. We have not asked for manual timestamps.

| Run under artifacts/remix-runtime/runs | Retained tactical seconds | Records / bytes | Dropped |
| --- | --- | --- | --- |
| 20261025-031353-637016-in-game |85.3618155|2,097,151 /268,435,456|195|
| 20261025-031610-737979-in-game |85.2026629|2,097,151 /268,435,456|323|

Both final headers status3/error0/reason2/warning1: hard byte cap, not a full90s
observation. Queued0. Aggregate drops do not identify the exact missing events
or exclusively distinguish ring contention from cap rejection. Classification
coverage is **PARTIAL**, not no useful data and not universal effects coverage.

Both result.json reports: normal_game_exit=true, gate_clean_unloaded=true,
controller exit0/not left running, renderer_exit0, final_report_complete=true,
original_critical_unchanged=true, launcher_settings_unchanged=true,
broad_proxy_restored=true. Before/after copied critical hashes match. Client
SHA2564D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.
No original rendering was suppressed. Renderer_exit refers to observer host,
not a Remix renderer: this survey does not launch Remix/Toolkit.

Each survey-control manifest confirms no geometry/image payload. Shader and
constant contents are excluded by the wire. Known ship draws remain as metadata;
no geometry, texture dump or native diagnostic geometry hook was enabled.

## Analysis and supported findings

Added read-only second-pass analyzer `tools/recon/analyze_render_families.py`.
It streams raw records, joins resource/view creation epochs and effective static
plus dynamic depth/blend state, reassembles sampled stacks, and retains per-second
counts/resource history. Tables/output bounded; malformed sequence/header/stack
fails rather than silently inventing associations. Retired pipeline handles
clear matching contexts so recycled handles cannot revive old bindings. This is
an offline helper, not new callback work. Original captures/result files unchanged.

Derived `render-families.review.json` beside each raw capture is503,336/503,493B.
It recovers9,868/9,839stacks,20/21unique SFC chains, no incomplete origins or
unresolved view references reported. Completed-interval native origin_stats says
9,868/9,838; second raw trace includes one additional completed stack before the
final interval statistics could be emitted at the cap. Do not conflate these
different counters. First-pass retained485/512sample examples were bounded
summaries, not all the raw origins. No first-pass family table overflow reported.

Full findings/counts/required state are in the updated
[family map](../reconnaissance/rendering-family-map.md) and
[curated evidence](../reconnaissance/evidence/20261024-render-family-survey-review.json).
CONFIRMED: distinct opaque/modulation-compatible triangle passes, additive
triangles with/without depth testing, point and line families, and no-depth
four-vertex strips. All five static blend descriptors in each run use add op0;
zero/source-color versus one/one factors are not interchangeable. Geometry and
texture payloads are absent, so no model/image content is inferred from counts.

Second run has817additive depth-tested/nonwriting line draws73.79–85.19s,
versus61over72.92–73.91s first. Second-only sampled chain includes
0x0041043B->0x004BA7B8->0x004B9C72->0x0046A55D->0x0069A87Aafter native
state context0x0069E61B. Resources appear near73.72s and81.42s. **STRONG
HYPOTHESIS:** this is useful combat/destruction-related evidence. Exact explosion
label, owner, spawn/death time and individual resource roles remain unproved.
No claim the sponsor's destruction must precede85.2s; final~4.8s are absent.

CONFIRMED important limitation: many downstream draws are observed during native
SetTexture/SetRenderState calls. These are submission/flush contexts, not original
geometry-producer identity. Incoming texture ID need not belong to the flushed
batch. A scene-list/trait dispatcher stack is not a typed effect owner.
The special-case string at0x0083BDE4 is tETrait_DoomsdayMouth, not explosion;
static caller naming by nearest string would misclassify this generic dispatch.
Surface Lock/Flip contexts for tail strips do not establish HUD construction.
Resource cache lifetime does not establish object lifetime. Same low-level path
does not mean the existing retained-ship contract covers effects.

## Source backing and narrow scope

- Actual raw metadata/module ranges and current observer wire; pinned ReShade
  include/reshade_api_pipeline.hpp enumerations and survey_extra.h field layout.
- Existing full client disassembly, extracted only around observed call sites:
  0x006A8860binder,0x0069E5xx–0x0069ECxxstates,0x006A6FxxLock,
  0x006A84xxFlip,0x004103xxchild dispatch,0x004BA7xxscene list,
  0x004ED0xxglobal list,0x00509A/9E/A2scene helpers.
- Installed Windows SDK10.0.26100.0um/d3d.h and ddraw.h vtable declarations;
  existing TEXTURE-EXPORT-001/secondary-texture-role evidence. Exact method here
  is Device3; older high-level D3D7 descriptions are not a reason to change offsets.
- Read exactly the referenced0x0083BDE4string using existing PE section mapping
  from the verified test executable. No broad strings/asset reconnaissance.

No new online/vendor capability claim; local pinned headers/source govern this
read-only interpretation. Translation/batching internal causality remains a
supported interpretation, not proof of every unobserved translator operation.

## Validation and repository state

- Four new offline helper tests PASS: effective static state/dynamic override,
  unknown state, pipeline retirement/recycled handles, non-owner caller labels.
- Existing8survey parser tests PASS0.043s; existing504Python regressions
  PASS8.173s. Existing Pillow deprecation warnings, no failures.
- Both raw second-pass analyses completed without malformed sequence/stack,
  table-bound errors or partial origin. No game/GPU test needed for offline helper.
- Survey and normal multi-ship Performance read-only preflights PASS; no game or
  renderer started. Normal binaries/source/settings and survey lock unchanged.
- JSON parsing, referenced paths, new source compile and git diff --check PASS.

Fuel Guard attached to existing trusted daemon. HEADfd79ce5/indexempty;
Run163–165dirty work preserved. New files: offline analyzer/test, this run and
curated review JSON. Updated family map, STATUS and authoritative HANDOFF;
Obsidian tracker refreshed with reviewed-copy/concurrent-edit guard. All changes
unstaged/uncommitted; no push, no active owned test process/mapping. No deletion.
Governed evidence plus isolated API/survey builds18,958,021,189bytes before small
final docs, below20,000,000,000cap; insufficient headroom for indiscriminate new
captures. Original results/packets retained; compact summaries are versionable,
bulk traces remain ignored. Do not commit proprietary binaries or raw image data.

## Exact next action

Inspect the producer/vtable callers feeding0x0041043B and0x004ED080offline,
joining one transient producer to resource selection before queued submission.
Only if needed, define one bounded default-off producer/resource/lifetime probe.
Recommend ordered draw-state and transient-batch interface support; do not
implement either or resume API work before the characterization is adjudicated.
No duplicate broad sponsor run is requested now. No milestone/TRL/replacement
or all-effects-support claim.
