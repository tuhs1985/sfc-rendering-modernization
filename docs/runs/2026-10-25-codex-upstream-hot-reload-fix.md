# Run192 — upstream non-freezing hot-reload fix found

Sponsor asked whether this issue is known. Read-only research; no game/test launch,
implementation, dependency or configuration change. Fuel Guard attached. Earlier
research covered pinned source and asynchronous settings, but did not identify
this specific upstream fix. This changes the next investigation priority.

## Directly relevant upstream change

NVIDIA's1.6release notes list a runtime optimization for faster, non-freezing USD
updates that processes changed data rather than reconstructing the stage.
[Official runtime performance notes](https://docs.omniverse.nvidia.com/kit/docs/rtx_remix/1.6.1-0/docs/changelog/remix-releasenotes.html#performance-optimizations).
The source change is
[REMIX-5883 — Non-freezing & faster hot reload](https://github.com/NVIDIAGameWorks/dxvk-remix/commit/25d18f6b692ca762d4236ffc6373f1bbd91e7a14), authored2026-09-09.
Its USD rebuild worker prepares changed assets separately; pending results are
applied at frame boundaries, with selective invalidation rather than unconditional
whole-scene clearing on the asynchronous route. This is a runtime change, not
merely a Toolkit UI optimization. Unit tests accompany it.

**CONFIRMED source applicability:** our pinned1.5.2source`b81a7b5` lacks
`rebuildWorkerEntry`/`applyPendingRebuild` and retains the synchronous reload path.
The release-linked1.6.1source`0a6cd5b` contains these facilities and selective scene
invalidation. GitHub compare establishes fix25d18f6is an ancestor of0a6cd5b
(ahead134/behind0). Pin-v-fix histories diverge(ahead216/behind6), so do not report
a simple linear version relationship; inspected source establishes the missing
implementation. Local dependency manifests match both named source commits.

**Important qualification:** candidate source `checkForChanges` requires
`rtx.initializer.asyncAssetLoading=True` and a loaded stage for asynchronous
rebuilding. False deliberately retains synchronous reload behavior. Our Run150/151
candidate workaround set that option False to restore missing material response.
Those runs therefore do not test the asynchronous hot-reload solution. Do not
blindly remove the workaround: the earlier material-response failure remains real.
[Candidate source](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/rtx_render/rtx_mod_usd.cpp).

Run150 records a packaged banner`remix-main+5a7eec84`, whose public source lookup
was unavailable, against release-linked0a6cd5b/API0.6.5. Release documentation and
source support this candidate route; do not assert instruction-level packaged-DLL
parity or that our exact3.42s wait is certainly cured. Verify actual option inputs,
material consumption, full-interval delivery and teardown in the isolated binary.

## Other searches and exclusions

Searched official issue trackers for reload, stutter, material loading and shader
stalls; inspected USD-loader commit history, release notes and both versioned
sources. General bottleneck issue972is tracked as REMIX-5005, but concerns ordinary
game/bridge draw-call scaling, not proof of our specific loading stall. Issue702
requests loading new mod directories during gameplay, not this existing-library
update. Toolkit memory/ingestion reports are not our direct host. No issue was
posted or third party contacted. Do not substitute broad symptom similarity for
a matching diagnosis.

Decision: the **problem class is known and has a directly relevant upstream fix**;
exact SFC resolution remains untested. Qualify that supported route before more
custom loader work or profiling only the obsolete synchronous implementation.
Keep the existing architecture and normal1.5.2baseline unchanged in the meantime.

Validation: source symbols/behavior checked at exact commits, commit ancestry via
GitHub API, local manifests and Run150/151 reviewed, documentation references and
`git diff --check`. No native build/test or performance PASS claimed this run.
HEAD9ff2d3d; prior dirty work preserved, no staging/commit/push. HANDOFF/STATUS and
Obsidian snapshot updated. No runtime process/channel started.

**Exact next action:** prepare an isolated1.6.1ordinary-D3D9 completed-material
checkout with the asynchronous rebuild route actually active, current matching
host/header and material-response checks; retain Run150's failure/workaround as
a regression condition. Compare full-interval delivery/final materials/cleanup
before runtime promotion. Prepare the old-runtime Nsight trace only if this
supported-route test leaves an attribution gap; no architecture/API pivot.
