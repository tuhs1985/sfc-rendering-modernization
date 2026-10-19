# NATIVE-LIGHTS-001 — read-only owner-correlated native lighting

Current2026-10-18:dedicated default-off observer variant integrated;offline
qualification and run receipt tracked in Run41. Historical core-only statements
below describe Run40,not a permission to bypass current qualification checks.
Question:which native light slots actually contribute,how do their values vary
with camera/object motion and firing,and what conversion is supported for Remix?
Hypothesis:manager record bank/enables and local derivatives identify useful
directional/point-like light inputs already used by each observed ship.

Targets:existing qualified manager callback/owner context,not new instructions
patched. Bank+778,enable+1778,derived triples+17B8/+1AB8,reciprocal+1DB8,gate+1EB8,
supplied transform+6F4,view+628;manager vtable7B8D4C. Native setter6A9AB0,
enable6A9C40,response6A9790 are supporting static evidence,not new hooks.

## Offline core now

`native_light_snapshot.h` contains only a fixed6156B snapshot and read-double/
memcmp/live-validity routine. No allocation,IO,wait,process open or renderer SDK.
Caller must supply qualified session/owner/model/source/frame/thread and existing
safe-read function. Raw native enums/fields preserved;unknown data not relabelled.
No production header includes it yet. No change to accepted component binaries.

`build_native_light_tests.ps1` uses VS2026Community18.7.3,C++17 /W4 /WX /Brepro,
x86/x64;run with PS7 -NoProfile -File. Output only ignored native-light-tests
directory,2executables plus tiny objects. Expected<2MiB,no capture or game launch.
Test exits immediately;build budget60s. No privileges normally needed;use scoped
build escalation only if sandbox denies writing prior artifacts. No UAC policy
change. Cleanup optional remove only this owned test output;source unchanged.
Python3.12.14/native_light_state.py decodes raw records;tests use synthetic data
ONLY. Synthetic tests are not evidence that any in-game light is active.

## Planned runtime adoption — implement/validate before use

Default-off prepared-runner switch,existing elevated parent,usual two-ship fixture.
Existing automatic tactical gate;90s.5Hz/owner,max2owner epochs,max900snapshots,
8fixed preallocated queue entries. Callback stable double-read/try-queue only;
worker serializes. If queuebusy,invalid identity or inconsistent state:drop/count,
original render unaffected. No viewer/SDK calls from callback. Worker drains/stops
before storage release,following accepted callback shutdown discipline.

Wire each record:16DWORD header(magicNLIT/version1/bytes6156/sequence/session4/
owner/frame/elapsed/manager/model/source/thread/reserved),17DWORD supplied,
17DWORD view,1024DWORD native bank,64enable bytes,192DWORD local point,
192DWORD local direction,64DWORD reciprocal,1DWORD gate(low byte from native).
Max900raw records5,540,400B. New discovery budget16MiB/warn8MiB,existing combined
32MiB nontexture log limit still binding;no duplicated full decoded JSON stream.
No image output,continuous screenshots or diagnostic geometry. Short<200ms lights
can escape5Hz sampling;explicit limitation,not exhaustive light-discovery success.

Expected runtime output:native-lights.bin,small identity/change/slot summary and
run manifest with source/tool hashes. These names/runner NOT implemented yet.
No runtime launch is authorized by running the offline test script.
Actual runtime collector must refuse overwrite and preserve cleanup/hash checks.

Analysis:retain all64enables;first disabled ends native response prefix even if
later slotsenabled. Compare raw/local transforms with native17word arithmetic;
never assume native0=DirectX0 or slot0=sun. Preserve session/bank/owner association;
shared bank under two owners not duplicated into two Remix lights. Nonfinite,
unclassified types or unstable snapshots cannot become active output lights.
Evidence includes native values plus static byte anchors plus controlled motion.
Sponsor only holds still,moves camera/ship,fires when requested and exits at cue.

## Prepared adoption — Run41

`start_light_discovery_session.ps1` calls the existing elevated-parent workflow
with `-CaptureNativeLights`. PS5 automatically delegates to the pinned PS7 as
before;no additional UAC/security changes. Builds a separate x86
`artifacts/remix-runtime/native-light-tests/m1_light_component.dll` using
SFC_NATIVE_LIGHT_DISCOVERY;accepted `artifacts/m1/bin/m1_component.dll` untouched.
The new variant activates only if target inherits SFC_NATIVE_LIGHT_DISCOVERY=1;
runner clears inherited ambient value and sets it only for this explicit mode.
No new hook addresses or register/ABI changes;existing qualified semantic callback
calls the fixed observer and its existing background worker drains the queue.
Same exact-build safeguards/restoration/normal-exit checks remain in effect.

Output new run/gate/native-lights.bin (packed6156Brecords,no per-record images),
native-lights-summary.json,plus compact bank/change analysis inside result.json.
The session matches existing scene mapping;monotonic records,bank<=8 and2owner
identities checked. Limits as above;size itself cannot reach multi-GB output.
Existing rendering stays ON with the accepted textured extra ship/provisional
inspection light. This test DOES NOT apply captured lights or config overrides.

Offline checks:9core checks eachx86/x64;10queue/drop/rate/stop checks eachx86/x64;
actual LiveScene producer+worker test compiled with same production optimization,
both synthetic owners captured and worker drain decoded. Qualification pins every
component header/source and relevant tests/scripts plus dedicated binary;stale
pins abort before game launch. Runner also retains accepted rendering qualification.
Build normally finishes within60s;existing prepared workflow refuses to launch
if insufficient total budget remains. Offline scene subprocess has a10s watchdog;
no game is started during validation. Compiler itself has no separate kill timer.

Sponsor procedure:enter familiar two-ship skirmish,briefly hold camera/ship still,
move camera,move/turn ship,and fire normally when convenient. No exact schedule
needed;capture observes5Hz throughout90s. Exit only at two-beep request. No
guarantee very short weapon pulses are caught;we evaluate actual coverage afterward.

Sponsor's three-lights/global-illumination hypothesis recorded,NOT selection
filter. Full native bank retained. Native ambient/material contributions and
Remix's indirect illumination may not be discrete bank lights;bank capture alone
does not prove or disprove all sources of apparent illumination.

Cleanup:existing runner waits normal game exit,restores hooks/unloads observer,
removes test proxy according to existing workflow,checks accepted/test hashes;
only owned renderer/worker processes cleaned. Never terminate SFC just to finish
collection. Raw evidence retained/archived after analysis;no auto-stage/commit.
