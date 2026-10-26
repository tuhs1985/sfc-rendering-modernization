---
title: SFC Modernization — Status Tracker
updated: 2026-10-25
checkpoint: Run193 asynchronous single-file material route works in isolation; startup target remains open
tags:
  - sfc-modernization
  - project-status
---

# SFC Modernization — Status Tracker

> [!summary] Where we are
> We can take live ships, textures, camera and lighting information from SFC, render through Remix, and put the result inside the game window. Original drawing remains intact. The API experiment is parked. Current work reduces loading pauses while preserving the fresh-asset pipeline and accepted appearance.

**Next action:** carry the successful isolated material handoff into a guarded checkout and run its regression checks before gameplay. Fourteen standalone attempts narrowed the problem: the layered handoff lost material settings, while the existing single-file handoff kept them and avoided the long update gap, including a ship arriving later. Startup still misses the two-second target: first returned ship about3.2s, last initial asset admitted about4.0s. Normal gameplay/runtime unchanged; no new launcher yet. [Run193](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-25-codex-candidate-hot-reload-qualification.md>). Checkpoint committed from parent`9ff2d3d`; no runtime promotion or push. Fresh533-test Python regression passed.

This is a readable project tracker, not execution authority. The repository handoff, approved decisions and run records control implementation. Updated through **Run193, October 25, 2026 (America/New_York)**. Status describes recorded evidence, not work currently running.

## Status key

- **NEXT / IN PROGRESS:** current work or its immediate continuation.
- **OPEN:** needed, not resolved.
- **PARKED:** deliberately deferred; restart condition is recorded below.
- **PROVED / LIMITED:** demonstrated within test conditions, not universally finished.
- **FIXED:** the specific defect was corrected and tested; broader issues may remain.

## Current work

### SFC-15 — Remaining rendering families

**ONE REAL EFFECTS CONNECTION CONFIRMED — other effect types remain to identify.**

- **Offline inventory complete:** 64 rendering-related classes, including 37 distinct effects plus their base class. Ten effects types also appear in the recent captures; the other 27 are possibilities, not proven gameplay coverage. Found specific photon/plasma images and shared effect sheets without running SFC again. Organian uses its own named image; the earlier guess about fx4 is superseded. Lighting changes also include drawing-pass overrides, not just physical lights. [Inventory and remaining questions](<C:/Project/SFC-Modernize Engine/docs/reconnaissance/rendering-executable-inventory.md>).

- Survey effects, sprites, beams, shields, explosions, damage, backgrounds and tactical UI. Preserve unknown/unassociated activity instead of assuming the ship hook covers everything.
- Exclude bulk mesh and image payloads; retain resource/lifecycle/state identities and bounded call-origin evidence. Distinguish common graphics paths from genuinely different interface needs.
- **Found:** different triangle, line and point drawing paths, with different blending/depth behavior. The second run has sustained late activity consistent with combat/destruction; exact explosion ownership is not yet proved.
- **Important:** many call sites show where queued drawing was flushed, not which object created it. A shared drawing path does not automatically mean effects work through our ship interface.
- **Bounds:** both256MiB traces filled at about85seconds of the requested90;195/323records dropped. Partial coverage, not failed/no-useful-data runs. Both exited/cleaned up normally and client hashes were unchanged. Mesh/image contents excluded.
- **New:** traced a missile-associated drawing routine to its shared fx0 texture, selected texture coordinates and four-corner drawing path. Confirmed38code/resource anchors against the actual client; no game changes.
- **Prepared:** targeted observer tested through the actual startup-loaded DLL, with clean hook restoration, texture-name association and pointer-reuse handling.44native checks and6parser checks passed; deliberately stalled writing did not hold up original calls.
- **Actual result:** first run linked a fresh effect instance to fx0.bmp and122,820four-corner primitives. It filled the16MiB log after35.2seconds; it did not stop because weapons were absent.
- **Other runs:** both completed90seconds, recording effects-list creation/removal and many native finalizer calls outside the selected routine. Those calls are not a count of visible effects or nonempty drawing. Faster combat does not prove the same path was used. All exits/hash checks passed and sponsor reports no issues.
- **Further analysis:** the captured effect can use both a burst image and a segmented trail from different parts of fx0. Exact image-row orientation is still unproved. Your atlas identifications are preserved as observations, not assumed engine mappings. These three runs did not capture synchronized lights. [Run170 details](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-25-codex-effect-atlas-followup.md>).
- **Prepared broader pull:** up to2GiB total, richer call-origin sampling, direct light definitions/on-off/global-gate changes and a census of concrete effect types. No model or texture-image payloads.21ring/119native/13parser/504existing checks passed; short and90second graphics fixtures passed with zero drops and clean hook restoration. No effects renderer implemented. [Run171](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-25-codex-expanded-survey-with-lights.md>).
- **Storage:** recoverably archived85completed runs' generated-image duplicates, saving3.84GB. Original assets, capture traces and mesh packets preserved. Existing20GB total cap remains.
- **New actual results:** Federation327MiB/Romulan207MiB, both full90seconds/zero dropped records/clean restoration and hashes. Ten named native effect classes identified, including phasers, photons, plasma, disruptor effects and explosions. Same-run light data includes changing temporary lights, but also drawing-time overrides; slot toggles are not automatically physical lights switching on/off. Sponsor confirms normal rendering/HUD/targeting/controls in both runs. [Run172](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-25-codex-expanded-survey-review.md>).
- **Third-launch block:** reproduced worst-case storage reservation over20GB, not leftover hooks/proxy. Archived another296MB of verified old generated-image duplicates; unchanged launcher preflight now passes. No need to rerun gameplay before more offline analysis.
- API development is paused; normal renderer/backend settings remain unchanged.

Map: [rendering families](<C:/Project/SFC-Modernize Engine/docs/reconnaissance/rendering-family-map.md>). Latest: [Run173](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-25-codex-offline-render-inventory.md>).

### SFC-01 — Direct Remix API route

**PARKED — sponsor direction; isolated experiment, not selected for gameplay.**

- We register each ship's geometry and materials directly with Remix, then update its position and camera. D3D9 still supplies the device/presentation connection, but the experimental ship geometry does not use ordinary D3D9 draw calls.
- Four clean GPU controls covered four ship owners, three different model contents, shared geometry and a delayed ship. Illumination affected the first returned image.
- **Remaining:** camera placement/scale does not yet match the accepted D3D9 route; first-image appearance still changes as rendering settles. No complete visual-parity claim.
- **Resume when:** sponsor returns to the API/backend-readiness question after the rendering-family survey.
- **Exact restart action:** compare the API camera/viewport conversion with the existing recorded projection checks. Do not compensate by guessing a scale.
- **Game test needed now?** No.

Evidence: [Run164](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-24-codex-api-scene-proof.md>).

### SFC-02 — Initial loading below two seconds

- **Supported route tested (Run193):** fourteen offline attempts, twelve completed/two partial. The newer runtime can load and update materials asynchronously, but our layered library handoff did not preserve their appearance. The existing single-file publisher fixed that in isolation. Material controls and a later-arriving ship passed; final tests had only1/1/3 isolated returned-image misses, with no long gap. First output3.2–3.5s is not all ships loaded; last initial asset admitted about4.0s. Two-second startup still OPEN. A separate alias-preparation bug was corrected only in the diagnostic; integrate it before checkout. Normal runtime/settings unchanged. [Details](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-25-codex-candidate-hot-reload-qualification.md>).
- **Upstream fix identified (Run192):** NVIDIA's REMIX-5883 addresses freezing USD updates with background rebuilds and selective scene changes. Missing from our normal1.5.2source; included in release-linked1.6.1source. Earlier candidate workaround turns that route off; it also solved a real missing-material problem, so changing it needs an isolated regression test. This supported fix is now the next priority before more custom loader/profiling work. Exact SFC result unproven; normal baseline unchanged.
- **Completed-stage test (Run191):** three material-library writes instead of43; base assets still publish independently, final381assetfiles exact. Startup presentation0.70s but later2.78s gap remains. The diagnostic repeat caught3.42s waiting for queued rendering after a fast Present; it failed to finish resize checks and is partial. This is not a promoted fix. Next: prepare a bounded pinned-runtime NVIDIA trace, not another gameplay run.
- **Presentation investigation (Run190):** issuing draws is fast; material consumption is a strong remaining suspect. Pinned Remix source reloads its library and resets the scene when our master material file changes. A deferred-publication replay shortened bootstrap3.37→0.89s but shifted trouble later:2.8s returned-layer gap and520/600delivery. All381final asset files matched. A new normal-publication control crashed externally with0xC0000005; evidence retained, cause unassigned. Next offline test: one completed enhancement revision publication per asset, retaining immediate base textures. No launcher/default changes or startup target achieved.
- **Live checkout reviewed (Run189):** all61textures use initial pixels,0fallback, matching prior KFF/FCA content/settings. Sponsor sees no appearance-time improvement; measured first matching return3.68s versus3.89s. The specific upload fix works;2.84s startup draw/present remains. Existing standalone marks show individual Present-side waits over2.2s. Next attribution is offline; no more gameplay needed to verify activation.

- **Integrated for explicit checkout (Run188):** initial-pixel staging uses renderer-owned moved buffers; native D3D9/Ex exact-pixel/lifetime/reset tests pass in both architectures, and Remix confirms107fast/0fallback uploads. Normal default retained. Standalone first matching output6.27→6.11s is not a meaningful whole-pipeline speedup; late delivery gaps remain. The known lock is avoided; the larger startup target stays open.

- **Stall located (Run187):** more than99% of one1.48–1.85s resource admission was a16KiB staging texture lock. A documented initial-pixel creation route avoids it in isolated tests (~4ms construction) with accepted asset content. Normal adapter integration/native lifetime checks are next; other queue waits and late-material interruptions remain. One control's491/600 delivery fails qualification, so no overall startup/seamless claim or default change.

- **Latest live result:** faster asset production confirmed, no faster screen arrival. The renderer services new asset admission between render/output cycles, so it cannot admit while blocked in those output waits. That dependency is the next investigation; it does not yet explain every second. Client cleanup/hash checks passed. [Run185](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-25-codex-live-two-phase-result.md>).

- **Base-first split implemented:** no bundle wait for enhancement generation or secondary images; base submission precedes enhancement writes. Existing identity algorithms now run in memory, removing repeated helper launches/rereads. Captured FCA base0.51s; final images/materials unchanged.611checks passed.
- **Renderer limitation remains:** new-model test598/600 and delayed-material test599/600 looked good after settling, but full traces show roughly1–1.3second gaps during updates. No clean streaming claim/default promotion. Same experimental option remains explicit; no extra gameplay needed to diagnose this known issue. [Run184](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-25-codex-base-enhancement-split.md>).

- **Live parallel checkout worked:** correct new-path flags recorded; same ship content as prior stable run. First matching output4.49s→3.49s, both ships admitted by3.37s; sponsor reports~3s and no flicker or other issues. Five post-start omitted outputs versus22previously, with no invalid associations. Clean exit/hashes/settings passed. Materials prepared before first matching output, so the delayed-update stress gate remains open. [Run183](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-25-codex-live-parallel-checkout-result.md>).

- **Explicit experimental checkout ready:** normal launcher plus `-ExperimentalParallelAssets` now enables the new within-ship preparation and progressive materials for your requested live comparison. Known interruptions remain unresolved; default unchanged.521main checks and source/native qualifications passed. The preceding4–5s live run used stable mode with trims enabled, not this new route. [Run182 command and limits](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-25-codex-experimental-parallel-checkout.md>).

- **Parallel preparation implemented:** geometry and image work overlap within a ship as well as across ships. Ready ships no longer wait for the initial batch in the isolated path; completed materials publish by group. Exact final assets retained.600Python tests passed. Single captured-ship preparation2.58s→1.47s; full multi-ship visible loading still exceeds target.
- **Current blocker:** no-delay renderer delivered596/600 checked frames; delaying a material until ships were visible reduced delivery to538/600, below the existing540 minimum. New publication behavior stays offline-only. Stable gameplay path requalified at595/600; no SFC test needed yet. [Run180](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-25-codex-parallel-progressive-assets.md>).

- **Baseline implemented:** SFC's resource associations are authoritative. Performance default is consistent, repeated material source comparisons are Test-only, and bounded input/derivative reuse is in place.508main tests and standalone4-owner rendering check passed; gameplay qualification refreshed. Exact accepted material/image output retained. No overall startup improvement demonstrated yet; remaining rendering wait still needs attribution. [Run179](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-25-codex-performance-baseline.md>).

- **New investigation:** retained accepted run spends about2seconds preparing assets before activation, then another2.16seconds after submitting the first complete scene before its output is ready. The old startup warm-up accounts for only0.55seconds. A captured-FCA CPU replay reproduced the exact accepted materials/images and identified repeated file lookup, image decoding and duplicate encoding. No production optimization implemented yet. [Run178](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-25-codex-downstream-startup-profile.md>).

**OPEN — target not met.**

- **Sponsor priority:** make the complete scene fast first. If necessary, show the correct normally textured ship promptly and apply enhanced materials afterward, rather than leave it absent. This is an allowed fallback, not the primary performance fix or a claim that complete loading meets the target. [Decision](<C:/Project/SFC-Modernize Engine/docs/decisions/2026-10-25-progressive-material-readiness-priority.md>).
- **New earlier-data route:** traced ship creation to its model-name request, shared native cache, geometry/texture preparation and owner attachment. Native cache presence alone is unsafe: objects enter it before loading is complete. The best candidate is after the full loader returns, including optional scaling. We have not changed the rendering pipeline or measured a new speedup. Gameplay timing is next, before early capture. [Findings](<C:/Project/SFC-Modernize Engine/docs/reconnaissance/early-model-availability.md>).
- **Observer ready:** 58 native checks and the actual startup-loaded standalone fixture passed; four complete named model-to-owner timing chains, zero lost records, clean restoration and unchanged files. Ready for one normal gameplay measurement, not proof of faster loading. [Instructions and limits](<C:/Project/SFC-Modernize Engine/tools/early_model_probe/README.md>).
- **Launcher fix:** the first attempt stopped because our launcher read its status incorrectly—not because of SFC or its models. Fixed and requalified; the standalone test now exercises that same startup check. Retry the same command. [Run176](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-25-codex-early-model-launcher-fix.md>).
- **Actual timing result:** clean90second capture,94records/about47KiB. FCA native preparation91ms, KFF14ms; complete data leads their first recorded drawing by117ms/14ms. Normal game behavior confirmed; hooks restored and files unchanged. This supports focusing on our downstream delivery/material-readiness work, not finding more native loading time. Earlier metadata is useful, but no speedup implemented. [Run177](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-25-codex-early-model-timing-result.md>).

- Latest complete API ship set reached GPU output in **4.22–4.24 seconds** from first captured discovery. Earlier accepted D3D9 reference: **5.17 seconds**.
- The faster D3D9 experiment (~2.58 seconds) was not accepted: enhanced materials were missing in its first image.
- File-based material delivery and first-use work are confirmed concerns, but no single cause accounts for every millisecond. Moving to the API does not eliminate all startup costs.
- **API restart action (parked):** establish correct API camera/appearance before comparing quality-equivalent startup timings. Current investigation is the earlier native model-loading route above, independent of backend choice.
- Do not mark complete merely because a model, material handle or texture upload was accepted.

Evidence: [Run163](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-24-codex-initial-material-readiness.md>), [Run164](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-24-codex-api-scene-proof.md>).

### SFC-03 — Flicker and missed returned frames

**OPEN — greatly improved in earlier work, not eliminated.**

- Persistent ship tracking and synchronized whole-frame buffering are implemented. Looking away no longer means a living ship must be discarded and reconstructed.
- Independent hiccups were found outside shuttle arrivals. Late asset introduction can also interrupt the returned scene.
- The API controls still omitted some output frames: normal early windows delivered **592/600 and 594/600**; the delayed-asset control delivered **564/600**. These counts do not describe continuous freezes or original-game failure.
- **Resume:** once the backend choice is qualified, measure the remaining render/transfer/admission delays. Do not blame every interruption on camera movement or new ships.
- NVIDIA recording appeared to stabilize some sponsor tests; its causal effect remains **a hypothesis**, not a required fix.

Evidence: [hiccup review](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-24-codex-steady-hiccup-hypotheses.md>), [Run164](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-24-codex-api-scene-proof.md>).

## Pins — deliberately deferred, not forgotten

| ID | Item / status | Why it is parked | What brings it back |
| --- | --- | --- | --- |
| SFC-04 | **Original-ship replacement — PARKED** | Current proof adds a returned ship; disabling original drawing needs reliable matching output and correct depth/coverage. | Delivery and camera alignment qualified; prove one stationary replacement, safe fallback, then motion. |
| SFC-05 | **Grid, shields, weapons and overlapping objects — OPEN** | A ship image alone does not prove correct visibility against every retained game effect. | Before replacement acceptance: verify depth, grid crossing and effects layering, not just the ship's silhouette. |
| SFC-06 | **Simpler image-return connection — PARKED** | Current ReShade compositor and owned receiver work, but serial copy/acknowledgment may add overhead. Their ownership safeguards cannot simply be deleted. | Measured transport bottleneck or next interface increment; qualify any replacement with synchronization and state-preservation tests. |
| SFC-07 | **Renderer-independent interface / D3D12 — OPEN TECH GATE** | D3D9 is the current standard input route. API submission is a Remix-specific alternative, not the portable interface itself. | Stabilize the chosen current backend; preserve neutral scene data, then qualify another adapter. D3D12 is future work, not an automatic Remix input format. |
| SFC-08 | **Supersampling — PARKED** | You prefer a higher-resolution render reduced to the display size; tested AA looked too soft. | After stable replacement/delivery: qualify resolution, memory and performance. Keep quality settings separate from lighting/material controls. |
| SFC-09 | **Appearance tuning — PARKED for engineering** | Your latest accepted temporary settings remain the comparison baseline. More tweaking must not hide transport, camera or texture faults. | Once delivery/replacement is stable, resume lighting/material/image tuning against a fixed reference. |
| SFC-10 | **Longer identity survey / larger stress mission — PARKED; initial survey now SFC-15** | The prepared90second metadata survey begins broader coverage, but does not establish a whole-mission or universal survey. | Review SFC-15 results, then justify a longer/broader bounded mission if needed. |
| SFC-11 | **Remix1.6.1 candidate — ISOLATED** | Installed Toolkit updates do not automatically upgrade the pinned rendering runtime. Candidate binaries need qualification against current source. | A documented benefit justifies a separately pinned upgrade; rebuild and compare before promotion. Normal path remains1.5.2/API0.6.4. |
| SFC-12 | **Device-loss recovery / vendor shutdown warning — OPEN** | Clean process exits and tested resource rebuilding do not establish automatic renderer-host recovery. Vendor warning also occurs on the normal route. | A lifecycle/recovery increment; preserve ownership rules and qualify restart/resource generations. Do not guess COM reference-count fixes. |
| SFC-13 | **All light types / effects-light coverage — LIMITED** | Qualified native lighting is wired; full coverage of dynamic effects is not implied by editable controls. | Broader scene/effects integration requires measured light identity/state and correspondence. |
| SFC-14 | **Arbitrary dynamic/damage geometry — UNQUALIFIED** | Supported captured rigid meshes and observable revisions work; unannounced in-place deformation is not established. | A mission reveals such changes, or broader model support requires a focused change-detection test. |

References: [interface audit](<C:/Project/SFC-Modernize Engine/docs/reconnaissance/2026-10-24-live-interface-second-audit.md>), [future-renderer gate](<C:/Project/SFC-Modernize Engine/docs/decisions/2026-10-18-renderer-independent-boundary-gate.md>).

## Already demonstrated — do not rediscover blindly

- **PROVED / LIMITED:** semantic ship/model ownership, supported fresh in-memory geometry, original texture associations and live transforms. Geometry is not supplied by exporting installed model files to OBJ.
- **PROVED / LIMITED:** game-camera observation, simulation-driven tracking, geometry reuse and distinguishable retained ship owners. Camera visibility is not object lifetime.
- **PROVED / LIMITED:** multiple different ships through the D3D9 in-game route; supported fighters also appeared. Older single-FCA README statements are historical, not the newest coverage record.
- **PROVED / LIMITED:** genuine Remix pixels returned inside SFC's frame through our ReShade add-on; this is not a desktop overlay. Original gameplay and drawing remain available.
- **PROVED / LIMITED:** adjustable lighting, materials, image controls and quality configuration. Those controls are separate systems; a lighting ratio is not automatically valid for every light type.
- **FIXED:** corrected D3D9Ex resource/upload policy and removed unnecessary live diagnostic work in the interface cleanup.
- **FIXED:** removed the live renderer's6,001-iteration stop; explicit source stop and elapsed safety limits now govern lifetime. This did not resolve startup or every hiccup.

Evidence: [authoritative handoff](<C:/Project/SFC-Modernize Engine/docs/HANDOFF.md>), [Run160](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-24-codex-interface-cleanup-first-pass.md>), [Run162](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-24-codex-live-lifetime-cutoff.md>).

## Milestones and guardrails

- M1's recorded disposition is **technical validation complete; sponsor closure review pending** in the approved plan. Do not infer formal closure from later graphics experiments.
- M1 integration evidence is not overall TRL4. The approved amendment assigns combined enhancement/visual-benefit evidence to the later M2 checkpoint.
- No full renderer replacement, universal model support, seamless delivery or finished graphics mod is claimed.
- Preserve the accepted Community Edition installation and original assets. Use the verified separate test installation.
- Normal gameplay path is unchanged by the isolated experiments. Run163–169 work remains **unstaged and uncommitted** at checkpoint `fd79ce5`; no push.
- Existing evidence cap: **20GB**, with approximately **19.00GB** used by governed evidence plus isolated API/survey/effects builds at Run169 review. This is a dated snapshot, not a live disk gauge; launch checks include archive reservation.

Authority: [M1 plan](<C:/Project/SFC-Modernize Engine/docs/m1/m1-trl4-integrated-component-validation-plan.md>), [approved gate amendment](<C:/Project/SFC-Modernize Engine/docs/decisions/2026-10-14-m1-m2-gate-allocation-amendment.md>).

## How to keep this useful

1. Keep the stable SFC-IDs when an item moves between current, parked and completed.
2. When putting a pin in something, record **why**, **what reopens it**, and **one exact next action**. Link its evidence where available.
3. When closing an item, retain its outcome and evidence; do not delete the history or silently mark related work complete.
4. Update this tracker with the repository handoff after a meaningful result, decision or newly parked item. Keep technical detail in run records.
5. The repository master is `docs/STATUS.md`. The Obsidian note is a copied snapshot, **not automatically synchronized**. Refresh both together; preserve any user notes before replacing the Obsidian copy.

## Checkpoint history

- **2026-10-25 — Run169:** first real effects run proved one native producer/texture/primitive connection and hit its byte cap early. Two faster-combat runs completed but used other, still-unclassified paths. All games normal; no repeat unchanged capture requested.

- **2026-10-25 — Run168:** targeted effects observer implemented/offline-qualified. No proxy or renderer changes; actual game test ready. Fixed a startup-loader export defect in the isolated fixture. No SFC gameplay launched during preparation.

- **2026-10-24 — Run167:** concrete missile-associated effects routine traced to shared fx0 resource selection and four-corner submission.38static anchors verified; live owner/resource join defined but not implemented. API parked, no gameplay required yet.

- **2026-10-24 — Run166:** both actual surveys reviewed, including sponsor-reported enemy destruction in the second. Confirmed graphics-state families and native call sites; producer/owner joins remain open. Both captures reached their byte cap around85s; clean exits/restoration and unchanged hashes. No new broad run required.

- **2026-10-24 — Run165 started:** sponsor parked the API experiment and authorized broader rendering-interface characterization. SFC-15 is current; SFC-01 retains its exact restart point.

- **2026-10-24 — Run164:** API submission proved offline; startup target, camera parity and late-delivery continuity remain open. Normal gameplay backend retained.
- **2026-10-24 — Run163:** confirmed that the fast ordinary-D3D9 first image lacked the enhanced material response. Preserved accepted startup behavior; sponsor then authorized the isolated API experiment.
- **2026-10-24 — Tracker created:** current work and parked decisions consolidated from repository handoff, audits, approved decisions and run evidence. No new rendering work or milestone decision.
