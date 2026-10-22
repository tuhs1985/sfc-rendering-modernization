# Run80 — actual live timing; receiver correction; insertion binding blocker

2026-10-20. HEADd29111f7;existing dirty work/index0 preserved. Sponsor completed
the prepared test and reports no issues. Subsequently authorized timeout correction
and offset-ship insertion using existing visual settings,stop only for blocker.
Read current HANDOFF,approved additive plan,raw result/native logs and renderer/
material/image/light source. Fuel Guard attached via trusted hook,no daemon.
No SFC launch,staging,commit,push,helper or agent during this analysis/correction.

## Actual run adjudication — useful evidence retained,not invalidated by harness

Run `artifacts/remix-runtime/runs/20261020-210035-445207-in-game`:
selected fresh `assets/models/kff/kff.mod`,owner1/revision1.1670 GPU-receiver
completed transfers,zero decoder invalid/unqualified records.1673 eligible
current-Present checks:1511 exact,161different/old completions,1completion later
than audit. Exact match90.3168%.5211 total audits over86.8317724s;3538source
ineligible(no selected current owner),NOT1638extra rendering misses. Completed
selected-owner output spans27.867077s,NOT the entire90s. Therefore earlier chat
translation to54ready/6misses per second was illustrative60Hz arithmetic,not an
observed whole-mission rate. Do not claim sustained90s delivery from this run.

Actual offer-to-GPU-receiver ACK:median12.67805ms,p95(sample-index)15.8155ms,
max39.7476ms. No pixel composition into SFC,original suppression or buffering.
Other semantic epochs/revisions continued; cause of selected-owner disappearance
requires lifetime/LOD evidence,not guessed enemy destruction. Miss clustering
has not yet been adjudicated; retain all raw records.

Normal game exit,true;hook bytes restored/unloaded,controller0;original/copied
critical files and launcher settings unchanged. Sponsor normal rendering/control
report accepted as direct human observation.9,782,281B total run evidence at
analysis. Raw audit SHA256:
`8d7e35cd74d9ab532a540d43030950f53c6d5e7168ddb464bbb6dd0f3563af2a`.
Original result SHA256:
`40ed79d9da853ce7193da2a87284887e3969f38a798928c418b46ba3c55da787`.
Raw result is deliberately unchanged,including pending-sponsor placeholder.

## Confirmed harness defect and implemented correction

Receiver log ends `RECEIVER_REJECTED receiver60s timeout`;host reports
`DIRECT64_FAILED unexpected receiver exit code`. Bounded job exit1,stop_reason0,
remaining_owned_processes0;API shutdown0. Thus clean GPU workflow qualification
failed,not source delivery or gameplay safety. Disposal warning40 still unresolved.

Added `output_wire::receiver_lifetime_ms`:offline60s unchanged;explicit live
mode110s to outlast90s source plus margin. Enclosing90s GPU job/source and
285s workflow limits unchanged. Receiver still exits immediately on stop/parent
loss;this is not permission for longer gameplay. No wait added to SFC callbacks.
Files:tools/d3d9_proof/output_channel.h,output_receiver.cpp;
tests/d3d9_output_wire_tests.cpp. Built receiver:27wire checks and18source-timing
checks PASS;344Python regressions PASS. Boundary policy tested natively;actual
full-duration GPU rerun not performed. New source/binary hashes invalidate old
qualification by design:do NOT rerun old live launcher until requalified.

## Insertion blocker — preserve tuned settings without reverting geometry path

CONFIRMED source facts:

- ordinary `d3d9_replay.cpp::Renderer` submits primary textures only,lighting OFF,
  point samplers,secondary stage OFF. scene_bundle currently prepares primary
  images for this ordinary path. The timing configuration is diagnostic defaults.
- Existing `ship_live_host.cpp` applies roughness/metallic/derived roughness maps
  and illumination through `ship_textured_asset.h` SDK-created material handles
  attached to SDK-created mesh surfaces. The ordinary D3D9 draw path does not use
  those surfaces. Reading TOMLs alone cannot apply their material semantics.
- Pinned public remix_c.h provides SDK material creation and D3D9 output/device
  interoperability,but no direct material-handle binding to an ordinary D3D9 draw.
  Cached rtx_remix_api.cpp creates external materials;cached scene manager uses
  those through external submeshes. This is not evidence of a supported bind for
  our ordinary draws. Do not equate matching hashes with a proven binding.

Current baseline requires roughness0.4,metallic0.2,anisotropy0.5,illumination5,
derived roughness enabled,as well as directional/dome controls and image grading.
These four TOMLs were read,not changed. No substitution with diagnostic defaults.
Baseline SHA256s:

|File under tools/remix_runtime/config|SHA256|
|---|---|
|lights.toml|01BB042A29FFE379BF40E5DBD95B11670D2FAC927BEB846375ACFF9BE94240AA|
|materials.toml|E76E67D5E68F3CCBD33EF1EBFBBF048DBFF30F7CEAC6E28A25E9F4604B1F9B02|
|image.toml|C71366DFABC1DB06BA380DC89A392DD3D2611EF579464A3930F90A5634C581CE|
|quality.toml|89FD0A280ACF3D80194A274E3B33BD72CBF29E3D9ED53D453FC45DC4EC526D40|

STRONG HYPOTHESIS: native Remix material-replacement bindings can carry these
maps while retaining ordinary D3D9 geometry. NVIDIA documents hash-based USD
material replacement,not a proof our pinned fresh textures are correctly bound:
https://docs.omniverse.nvidia.com/kit/docs/rtx_remix/1.3.6-2/docs/howto/learning-materials.html
Inspected pinned header/source is authoritative for available current SDK calls;
online/latest APIs must not be spliced into this pinned runtime.

BLOCKED FOR PREPARED INSERTION LAUNCHER,not a failed semantic seam or architecture
infeasibility. No additive compositor enabled or unsafe launcher produced.
Exact next action:qualify one ordinary-D3D9 texture/group to native Remix material
replacement binding,using existing roughness/emission images and settings;verify
pixels and provenance offline without SDK mesh submission. Then carry existing
light/image/quality adapters across,qualify receiver lifetime and exact-frame GPU
composition/state/depth/offset/failure paths,before providing the gameplay script.
No approval is inferred to drop settings,hold stale images or switch geometry paths.

Documentation changed:this run and authoritative HANDOFF. No generated evidence
deleted;no application/client/config changes. Current state remains dirty,
unstaged/uncommitted;old source qualification now stale intentionally.
