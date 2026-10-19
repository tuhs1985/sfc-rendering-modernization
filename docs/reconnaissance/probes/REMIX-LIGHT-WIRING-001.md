# REMIX-LIGHT-WIRING-001 — native steady lights and hot config wiring

Sponsor2026-10-18 authorizes first normal harness check,then a separate longer
minimal-recording tuning pass ending on normal game exit. **This increment prepares
the FIRST90second wiring pass only.** Tuning activation is gated by its result;
do not silently extend90s observer/controller/host limits or claim tuning ready.

Question:can two freshly observed native type0lights drive SDK lights with
explicit ratio controls reloaded outside SFC's render callback? No weapon/type5
mapping,GI/native lighting parity,original suppression or renderer architecture.

Use existing NATIVE-LIGHTS-001 dedicated observer,2owners/5Hz/900raw6156Brecords,
automatic tactical gate and accepted textured additive path. A Python worker
outside SFC reads complete appended records,qualifies session/selected owner/
model/source,then emits fixed200B atomic light packet for x64 host. No old native
IDs reused after exit. Only consumed type0slots0/1 qualify;unknown state fails
closed for extra copy,never SFC. Stable native directions use existing common
scene coordinates;sign/SDK mapping remains experimental pending runtime review.

Controls `tools/remix_runtime/config/lights.toml`,poll<=2Hz,64KiB maximum.
Effective radiance=native RGB * native type0 multiplier * conversion_scale *
master_multiplier * per-light intensity_multiplier * RGB multiplier.
Initial conversion1/master.5 gives provisional radiances.75/.125 for observed
white1.5/.25,not calibrated parity or exactly half the old one-light picture.
No provisional inspection light drawn in wiring mode. No other backend inherits
this unit/sign/shape policy. Source assets/UVs and native lighting untouched.

Invalid/partial edits keep last valid controls;missing/stale/mismatched native
state omits extra output. Config reload retains native observation timestamp,
never rebrands old native values as fresh. Host validates fixed packet/session/
identity/frame/checksum/finite values and500ms maximum relay-observation age.
Native source5Hz is adequate for this two-steady-light proof,NOT weapon sync.
No per-light nonraytraced toggle silently faked;renderer_default only.

90s tactical,5minute workflow,existing32MiB nontexture/128MiB images/10GB aggregate
caps;no new image dumps. Existing native raw<=5.54MB;light packet200B overwrites
atomically,not appends. Config/error/application summaries capped100messages,
then counters. External file reads/validation/conversion/SDK calls never run in
SFC callback. Game exit/hook restoration/proxy cleanup/client hashes unchanged.
Retain native packet and applied config provenance;do not destroy original captures.

Offline validation must cover ratios,invalid/partial edits,last-good behavior,
stale session/owner/frame/checksum,packet atomicity,actual SDK light creation/
updates and accepted return-path regressions. Standalone native fixture may write
synthetic bank records solely for testing;label that evidence NOT in-game capture.
Document exact tools/hashes/launch command once qualification completes.

Sponsor first-pass procedure:usual skirmish,wait for normal textured copy,brief
camera/ship movement. Save one small config multiplier edit when directed to
check wiring;exit at two-beep request. Appearance tuning is second pass,not the
goal of this short check. No manual timestamps/UAC/RE work. Default-off mode.
