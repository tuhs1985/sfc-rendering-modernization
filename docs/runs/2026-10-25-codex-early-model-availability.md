# Run174 — earlier model identity and completion investigation

Date:2026-10-25 America/New_York. Sponsor requested this targeted read-only
investigation after Run173 publication. Started clean at6d847dd; API remains
PARKED. Deferred exact effects UV/state extraction, not abandoned. No new game,
renderer, hooks, settings, native binary or assets changed. No commit/push.

[Findings and confidence](../reconnaissance/early-model-availability.md),
[defined next probe](../reconnaissance/probes/EARLY-MODEL-AVAILABILITY-001.md),
[curated evidence](../reconnaissance/evidence/20261025-early-model-availability.json).

## Completed

Traced original semantic visual path backward through model parser/cache/factory
to ship creation. The first input's inline+38name reaches004156F9 before its
common factory request0042F39A→004304E4→0042F51A. Loader cache008F5974 shares
visuals by name. Cache miss parses geometry/groups, requests primary/conditional
secondary textures, optionally scales positions, returns visual, then owner
attachment00413A8D writes ship+88. _BRK.mod is requested separately.

Important verified hazards: constructor publishes before initialization; parser
return is before texture acquisition and optional position-pointer replacement;
successful outer return may contain unsupported/null child or missing resources.
Earlier asset snapshot therefore needs structural/lifetime qualification and cannot
pretend render-manager provenance is present. No polling raw cache or guessing a
mission roster proposed. Candidate successful outer-loader return is not a proven
thread-safe snapshot or GPU-readiness event.

Added offline verifier tools/recon/verify_early_model_path.py and9tests in
tools/recon/tests/test_early_model_path.py.49instruction anchors/5vtable targets/
2196byte-verified instructions/52direct factory callers. Explicit bounded output
and changed-input rejection. Frozen client SHA matches accepted2.5.6.4.

Read existing M0 traces20260904-100033/100901:17/16parser entry samples, all
return0042F5DC. First parser entries14828/11391ms; first indexed draw15250/11563ms.
Second first generic geometry11563ms. These are original breakpoint-probe timings,
not contemporary named-asset completion or tactical readiness intervals; don't
claim422/172ms of useful prewarming. Exact capture hashes in curated evidence.

Generated authoritative report:
artifacts/render-survey/early-model-path-20261025-final.json, SHA256
7D56C358225860106DE7FE43F74DF79ABDE1737A11546704A2E78C82CA6643AD.
Preliminary early-model-path-20261025.json is superseded by full source-register
range/filename-getter/conditional-creation qualification. Original evidence intact.

First old-log parser rejected repeated META probe_point rows as conflicting;
limited conflict rejection to client identity/base fields, preserving intended
multiple probe declarations. Added positive/negative identity/sequence/origin tests;
no game or runtime fault. No output overwritten.

## Validation / repository state

36recon tests PASS0.039s, including9new cases;504existing Python regressions
PASS7.583s (540total). Existing Pillow deprecation warnings unchanged. Survey and
multi-ship Performance read-only preflights PASS; no game/renderer started.
AST/JSON/report SHA/local referenced paths/git diff --check PASS; index empty.
No native rebuild needed for offline tools/docs.
Exact changed files: two new tool/test files; new findings/probe/curated JSON/this
run; updated docs/HANDOFF.md and docs/STATUS.md. No runtime source/lock changes.
All changes unstaged/uncommitted; existing published HEAD6d847dd. Existing20GBcap
retained, small metadata only, no deletion. FuelGuard existing trusted hook
attached; no daemon/helper/agent/new owned process/channel. No hidden session state.
Obsidian tracker diff reviewed as Run174-only and synchronized with a concurrent-
edit SHA guard; destination contents verified identical to repository STATUS.

**Exact next action:** implement/offline-qualify the separately defined bounded
request/completion/owner/first-draw timing observer, armed before loading. Preserve
both direct and cached cases; no early geometry capture or new gameplay until
safe lifecycle/timing and original-flow preservation are qualified.
