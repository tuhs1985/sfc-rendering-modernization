# Run160 — first documentation-backed interface cleanup

## Scope and completed implementation

Sponsor authorizes removal/replacement of audited leftover assumptions. Read
Run159 audit and current handoff, attached trusted Fuel Guard hook, consulted
exact pinned NVIDIA API/initializer source and Microsoft resource/upload rules.
Advisory allowance messages did not stop authorized work. No SFC launch,
helper/subagent, runtime upgrade, appearance retuning, staging, commit or push.

Completed bounded first pass, NOT a full interface-clean signoff:

1. **IF01 corrected:** actual shared renderer uses DEFAULT VB/IB/textures for
   native D3D9 and Ex. Immutable retained scene data rebuilds resources after
   unbind/release/reset/recreation. Textures use SYSTEMMEM -> UpdateTexture ->
   DEFAULT. Native Test verification copies texture to a test render target and
   reads that target back. Performance skips that verification, not upload.
2. **IF06 reduced:** Performance no longer formats OUTPUT_ACK every frame;
   ownership ACK remains. No unused vendor picking-retention request in additive
   mode. Our union-coverage output remains, with corrected non-per-owner wording.
3. **IF04 replacement tested but NOT promoted:** one ordinary bootstrap Present
   produced earlier output, but first-image appearance differed and later output
   gaps appeared. Preserved the experimental binary and restored the accepted
   startup policy, explicitly marked transitional compatibility rather than a
   vendor requirement/readiness guarantee. Existing catalog, GPU completion and
   exact frame/camera/owner checks remain. Live updates remain one Present.
4. Qualification now locks native32/64resource-policy proofs and requires actual
   system-D3D9/Ex, reset and recreation checks before gameplay qualification.

Source changes this increment:

- tools/d3d9_proof/d3d9_replay.cpp
- tools/d3d9_proof/d3d9_direct_host.cpp
- tools/d3d9_proof/output_producer.h
- tools/d3d9_proof/normal_coverage.h
- tools/d3d9_proof/build_resource_policy.ps1 (new)
- tests/d3d9_resource_policy_tests.cpp (new)
- tools/remix_runtime/qualify_multiship.py
- Current retained-multiship/pipeline-mode contracts, this record, curated controls
  and HANDOFF. Existing unrelated dirty work preserved.

## Documentation and boundaries

Microsoft explicitly excludes MANAGED from Ex; DEFAULT texture locking is not
silently substituted. [Pool contract](https://learn.microsoft.com/en-us/windows/win32/direct3d9/d3dpool),
[UpdateTexture contract](https://learn.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-idirect3ddevice9-updatetexture).
Pinned [NVIDIA output implementation](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_remix_api.cpp)
queues output-copy work; actual GPU fences remain. Its picking retention is
unneeded when the third plane is host-generated coverage.

There is NO public universal materials-resident signal established here. Native
one-frame submission is normal draw/Present behavior, NOT a replacement invented
readiness API. Removing24does not mean initial lighting has converged. No shader
compilation/asset streaming switch or vendor code changed. Normal1.5.2 unchanged;
candidate1.6.1 untouched, its source qualification is stale after these edits and
requires rebuild before any future candidate use.

## Native validation

Actual test includes the shared Renderer and loads a capture-derived scene.
Absolute SYSTEM d3d9.dll, no Remix/ReShade/DXVK modules. Both x86 and x64:
255,760 checks each, classic-vs-Ex pixels EXACT, actual destination texture/buffer
pool DEFAULT, GPU texture and VB/IB byte checks, ResetEx/rebuild pixels EXACT,
full Ex device recreation pixels EXACT. Existing example has one scene frame;
do not claim arbitrary motion from this resource test.

Reproduce from an existing unarchived capture-derived scene:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/d3d9_proof/build_resource_policy.ps1 -Scene 'C:\Project\SFC-Modernize Engine\artifacts\remix-runtime\runs\20261024-203405-713587-return-fixture\gpu'
```

Strict /W4/WX optimized host build PASS; loaded lights11, deferred diagnostics,
worker poll and actual combined-post GPU65checks PASS. All504Python tests PASS
6.194s after final source edits. No tests skipped due to missing native helper.

## Standard and first-image controls

All fixtures use original accepted settings/images, four independently ACKed
owners/three contents, no saved Toolkit ship. Original source packets/geometry
preserved; all432generated image hashes identical across controls. Standard
fixtures preserve native HUD/border/state, resize/recreate and clean exit;
owned jobs exit0/remaining0. No original ship suppression.

| Control | Run suffix | First cohort GPU output | Standard delivery window |
| --- | --- | ---: | ---: |
| Previous normal baseline | 203405-713587 | 5.392s | 594/600 |
| Resource/unused-work fix, old24startup | 214803-126987 | 5.380s | 600/600 |
| Same fixes, one-frame startup, Performance | 215013-834823 | 2.661s | 600/600 |
| Same one-frame startup, Test readbacks | 215458-405273 | 5.213s | 600/600 |

These are individual offline controls, not a guaranteed live speedup or2s PASS.
Test overhead is intentionally different. First-use stalls move between present,
copy and initialization boundaries; no simplistic total attribution is made.
Standard window starts after the set is ready, so600/600 does NOT prove seamless
late-arrival handling or fix prior real-game independent hiccups.

Curated comparisons:
reconnaissance/evidence/20261024-interface-cleanup-resource-controls.json,
20261024-interface-cleanup-startup-controls.json,
20261024-interface-cleanup-final-controls.json.

Isolated FIRST-matching-output fixture is explicitly different from standard
settled sampling: production source/binary unchanged; ignored derivative removes
only the +60frame settle criterion. Actual copied fixture and selected host hashes
are in each isolated-first-frame-control.json; never use these as production
qualification. Initial diagnostic link omitted two Windows libraries, corrected
before execution; not a vendor/runtime failure.

- Preserved cleaned24host control215150-246841: first cohort7.482s,595/600.
- One-frame current215247-075468: first cohort2.668s,433/600. First actual matching
  frame shows all three different ship models with recognizable original color
  textures, but initial shading/emission differs visibly. After settling, mean
  ship-region pixel difference2.135RGB/255; first-sample difference24.626.
  First-image screenshots were visually inspected. This is NOT exact material/
  appearance parity. Banner differences outside the ship ROI are not evidence
  of geometry/material changes.
- CORRECTION from closer event inspection: these fixtures have ALL four assets
  in the initial catalog and ONE initial material publication. There is NO late
  asset or material publication in this comparison. Earlier first visibility
  exposes a subsequent stall within the600frame window, unlike the delayed
  control. This is not evidence of a shuttle/reload event. Initial library
  consumption/first-use work is a hypothesis; exact vendor cause remains unproven.
  Do not present433/600as seamless success or claim material-ready from ACK.

First-image evidence:
reconnaissance/evidence/20261024-interface-first-output-controls.json.
Phase split: artifacts/interface-cleanup-startup-split.json.

### Final adjudication — restored stable startup; vendor control not promoted

One-frame Performance repeat215642-292953: first cohort2.659s,593/600 standard
settled window. This reproduces earlier GPU output, not full initial-appearance
or stall-free qualification. Experimental host preserved separately.

Single pinned-NVIDIA initialization control215932-917228 used child-only
DXVK_ASYNC_ASSET_LOADING=0, confirmed by actual runtime options log. No shaders,
textures, material values or parallel preparation changed. First cohort2.615s,
first matching game screenshot later at source frame200287,595/600. Initial
appearance still differs from settled image and24control; no universal public
readiness signal follows from this switch. It is NOT promoted to normal policy.
Report20261024-interface-first-output-sync-control.json; actual screenshots
retained. Pinned NVIDIA initializer source supports synchronous initial loading,
not a guaranteed arbitrary late-USD/material/GPU-residency barrier.

Normal source restores24startup with an explicit transitional-compatibility
comment, not a readiness assertion. Final stable fixture220322-841745: first
cohort5.182s,595/600, all four owners/three contents ACK/draw, no asset partials,
state/HUD/resize/recreation/jobexit0/owned0. Final stable vs original203405
mean pixel difference1.198post/0.749settled RGB/255, same432image hashes/settings.
See20261024-interface-stable-final-control.json. No claim this small difference
is exact parity. Final exact-source qualification and BOTH launcher preflights
PASS. No game started. Source changes correctly invalidated intermediate receipts;
no hand-edited qualification or fallback to an unqualified executable.

## Remaining work / acceptance boundary

IF02separate relay remains: its ACK cannot be removed before a direct host-owned
pool has equivalent producer-completion and consumer-read-lease proof. IF03legacy
single-owner gate/oracle still present; do not weaken transform/source validity
without coherent-scene replacement. IF05material consumption/readiness and late
arrival stalls remain unresolved. Independent steady hiccups NOT claimed fixed.
IF07BGRA/R32interop remains pinned-runtime qualified, not universal native Ex.
Existing vendor40object disposal warning persists; exit0not leak-free proof.

This first pass is suitable for sponsor regression of loading, initial appearance,
camera changes and normal play—not replacement or full-clean-interface claim.
No new broad capture/diagnostic system added. Next smallest action is to qualify
the existing NVIDIA initial-material lifecycle control against first and settled
images before retiring the transitional startup policy; then direct-output-pool
qualification using the existing standalone x86 consumer as a TEST, not blindly
deleting current synchronization. Keep settings/scene input and original drawing.

## Rollback, evidence and repository discipline

Before edits, preserved ignored binaries in artifacts/interface-cleanup-baseline:
original host SHA2e0de844e69faefaa8a0cba8157db2878ee6f63086f380f5f4da6ccda60a1cb9,
original receiver SHA db1fd5b73845886f8d308ecab41b9ec0c0d62a689f5be4e63f0d933390e7dc42.
Also preserved cleaned24host SHA5c06eefb59dd36124ab18c1f4dff00b126f3fee7d438deac6277dee6e0a65820.
Experimental one-present host SHAb701d8856cc5f24b4df016255c4a53f9bc5eb71d53b5f25f1ce2c8dfbb373404;
preserved as experimental-one-present.exe, not gameplay-selected.
Final normal host SHA5c06eefb59dd36124ab18c1f4dff00b126f3fee7d438deac6277dee6e0a65820
(identical machine code to the saved cleaned24control).
These are diagnostic rollback binaries, not authority to bypass source locks.

Thirteen completed432-file image sets recoverably ZIPcompacted this increment:
each162,619,600bytes ->10,051,597bytes, all entries decompressedSHAverified before
exact generated-file removal; net1,983,384,039bytes before receipts. Restore via
perrun generated-images-archive.json. Captures/geometry/comparison BMPs/logs and
partial profiler evidence retained. No original assets or project source deleted.
20GB aggregate cap unchanged. Source changes make old qualifications stale by
design; initial attempt to qualify215013after gate-source edit refused correctly.
Final qualification uses exact-source standard220322-841745, not215458experiment;
no receipt edits to bypass validation. HEADfe2eaf7/indexempty/all changes unstaged
and uncommitted/nopush; previous work preserved.
