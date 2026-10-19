# REMIX-MATERIAL-CONTROLS-001 — illumination and material tuning

Run49,2026-10-18. Same additive return path and light-tuning runner;no new SFC
hooks,client patch,geometry diagnostic or original-ship suppression.

## Adjudication before gameplay

CONFIRMED: current SDK host omitted the secondary image and forced roughness1.
Fresh references retain primary/secondary filenames,hashes,group flags. Existing
[secondary-role evidence](../2026-10-16-secondary-texture-role.md) supports native
primary*clamp(secondary+vertex lighting),not raw secondary-as-glow. Current recorded
fca references also retain the fallback eligibility fields;no new RE is needed.

Selected smallest mapping: preserve original albedo and bake a separate encoded
primary*secondary mask for Remix emission. Formula floor((a*b+127)/255). This is
a STRONG HYPOTHESIS for useful modern appearance,NOT exact legacy clamp/colour-space
or physical-strength equivalence. Missing secondary means no emission,not hull
self-lighting. Alpha remains unsupported. No normal/height reconstruction.

The first standalone test exposed unequal primary/secondary dimensions. Native
stages sample their common captured UV domain,not corresponding pixel indices.
The Remix-only derivative explicitly bilinearly upsamples to componentwise maximum
dimensions before multiplication;never flips,rotates or changes source images/UVs.
This sampler is a documented modern approximation,not a proven native filter match.
Per-pair manifest records both sizes,derived size,formula,sampling and SHA256.

## Tools, configuration and launch

- Pinned Remix1.5.2/SDK0.6.4,VS2026Community18.7.3,x64 host,x86 existing
  observer/display component,Python3.12.14/Pillow/NumPy. No translator changes.
- Build `tools/remix_runtime/build_live_return.ps1`;offline
  `python tools/remix_runtime/qualify_live_return.py --execute --material-controls`.
  The latter starts owned standalone processes,NOT SFC;60s/32MiB plus128MiB image
  cap,owned-process teardown. Normal regression matrix still required afterward.
- Gameplay: existing `start_light_tuning_session.ps1` from validated elevated
  parent. Same process-only execution-policy bypass;no routine new UAC/security
  changes. Enter two-ship skirmish,observe extra ship,save materials.toml while
  playing,exit normally when finished. No timestamps or RE required.
- Config `tools/remix_runtime/config/materials.toml`,separate from lights.toml.
  Applies globally to the selected extra ship,not native SFC or individual groups.
  Roughness1/emission1 provisional baseline;optional metallic0/
  anisotropy0. User light values are untouched.

## Reload contract and bounds

Worker polls at2Hz in wiring/tuning mode.16KiB config,strict known keys/ranges/
finite values. Invalid/partial/unreadable config retains last good;before any
valid config the host's documented defaults apply.256 accepted revisions/session;
first16config snapshots plus overwritten last accepted,100worker messages maximum.
Ordinary textured launcher reads initial config but has no ongoing tuning relay.

Worker atomically replaces material-controls.bin:56B,magic0x3143544d/version1,
10float32 (roughness,emission,metallic,anisotropy,six reserved neutral1s),FNV64 over
first48B. Host independently validates checksum/ranges/exact size and polls500ms.
It creates new materials AND a revision-keyed grouped mesh only after previous GPU
output completion and receiver lease release;no SFC callback IO or new wait.
Old mesh/material handles are retired. Invalid data does not mutate last settings.
SDK failure must leave original SFC drawing intact;it is not a silent success.

Pinned source b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4,
[opaque material shader](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/shaders/rtx/concept/surface_material/opaque_surface_material_interaction.slangh#L567),
lines567–595 confirms loaded texture replaces the colour constant. Colour knobs
were rejected before delivery rather than offered as ineffective texture tints.

live-materials.bin remainsv1;new required live-emissions.bin:24B header
(magic0x314d4553/version1/count/payloadbytes/FNV64),one80B hash+72charDDS row per
material. Allzero means absent. SHA filenames only,no pointers. Material identity
includes primary AND derived mask,so shared albedo cannot cross-associate masks.

Derived DDS are prepared once off the game thread;max4096dimensions,128MiB combined
original/derived output,warn64MiB,256MiB memory including conservative temporary
bake reservation. Source byte/hash/UV provenance stays unchanged. No repeated
image dumps. Existing30minute tuning/33minute workflow,32MiB logs warning16MiB,
10GB aggregate allowance,cleanup and client-hash checks remain.

## Evidence and cleanup

Run folder contains texture-manifest.json,original/derived images and hashes,
live-emissions.bin,config snapshots,material-controls.bin,MATERIAL_APPLIED SDK
receipts and normal result/telemetry. Existing image snapshot stays optional and
one-shot. Runtime question: do illuminated markings appear and do saved roughness/
emission edits affect only the returned ship while SFC stays normal?

Exit game normally;runner stops owned host/removes temporary test setup/checks
hashes. Do not delete live files or kill hook controller. Archive useful evidence
after analysis;no source assets or accepted install cleanup. Normal game exit is
process reclamation,not controlled live-unload proof. Colour/strength remains a
sponsor visual calibration question;no exact native-fidelity/milestone PASS claim.
