# Run49 — restore illumination contribution and expose Remix material settings

Date2026-10-18 America/New_York (standalone folders20261019UTC).
Active work: bounded in-game Remix return-path material/light tuning;no gate
advancement,renderer replacement,new requirements or broad RE. HEAD2fa8032;
existing Run40–48 changes unstaged/untracked,index empty. Preserve them and the
sponsor's current lights.toml edits. No helper/subagents/game launch/stage/commit.

## Question, starting evidence and adjudication

Can the extra returned ship use its associated illumination images and allow
roughness/emission adjustment independently of the captured light controls?
Starting host forced roughness1 and emitted nothing. Fresh group associations
already retain original primary/secondary images. Read ship_live_host.cpp,
ship_textured_asset.h,textured_asset.py,live_scene.ImageStore/qualify_mesh,
live_lights.py,light_controls.py,qualify_live_return.py,pinnedSDKOpaqueEXT,
tests/test_textured_asset.py,secondary-role note,texture-eligibility run,
provisional_lighting.py,configREADME,Run48 and HANDOFF.

CONFIRMED static native relationship remains primary*clamp(secondary+lighting).
Do not bind raw secondary or primary as whole-hull emission. Reuse encoded
primary*secondary as an explicitly provisional modern emissive contribution.
The first standalone fixture rejected unequal dimensions;inspection of fresh
fca associations showed this is a legitimate input,not corruption. Both native
stages use the same normalized UV domain. Remix-only bake now uses documented
bilinear upsampling to componentwise maximum dimensions before multiplication.
No source flip/rotation/resizing,UV/geometry change or guessed substitute image.
This does NOT establish native sampler,colour-space,clamp or physical-unit fidelity.

## Implementation

- New config/materials.toml: roughness1,illumination_strength1;optional
  metallic0,anisotropy0. Comments and README order optional controls
  by likely usefulness and explain departures from defaults. Remix-only/global
  selected extra-ship controls. User's separate light settings untouched.
- textured_asset.py derives one bounded DDS per content pair,hash/provenance,
  dimensions,sampling,round-trip verification,combined image/memory accounting.
  Materials deduplicate by albedo+mask pair,not albedo alone. Missing secondary
  means no emission;unsupported alpha fails explicit. live-materials staysv1;
  new checksummed80B/row live-emissions companion carries only safe SHA DDS names.
- material_controls.py strict16KiB TOML→56B checksummed packet,atomic replacement,
  last-good handling,2Hz poll in existing light worker,256revisions/session,
  first16snapshots plus last accepted,100worker messages. Initial defaults when
  no valid config. No render-callback IO,allocation,conversion or new hooks.
- Host validates fixed packet,loads derived masks,sets pinned SDK material fields.
  Every live edit builds new material handles AND grouped mesh/revision hash only
  after completed output fence/idle receiver lease. Old handles retired;failed
  preparation keeps old material. Retirement failure stops optional renderer,
  never continues a partly destroyed mesh or suppresses native SFC drawing.
- Source-matched qualification now requires separate material hot-reload gate.
  Ordinary textured launcher loads initial config;ongoing edits need wiring/tuning.

Exact files this run: tools/remix_runtime/{textured_asset.py,ship_textured_asset.h,
ship_live_host.cpp,live_return.py,live_lights.py,qualify_live_return.py,
material_controls.py,remix_material_controls.h,config/materials.toml,config/README.md};
tests/{test_textured_asset.py,test_material_controls.py,test_live_light_wiring.py,
remix_material_control_tests.cpp};new probe REMIX-MATERIAL-CONTROLS-001,this run,
docs/HANDOFF.md. Prior changes to shared files retained,not rewritten wholesale.

One old regression used the sponsor's mutable light settings as its fixture and
failed after their second-light multiplier changed. Test now uses deterministic
validated defaults;no sponsor setting was reset to satisfy a test.

Final source check against pinned runtime commit's opaque material shader
lines567–595 rejected initially proposed colour tints:constants are fallback-only
when textures are absent,not multipliers. Removed those knobs before delivery;
six wire floats remain reserved neutral1s. Primary/secondary textures stay intact.
SDK emission fallback is explicitly black if texture loading fails,never a white
whole-hull lamp. This final safety check is included in the delivered source pin.
Earlier first material gate remains preliminary after this final schema tightening;
all twelve cases rerun against the final source,binaries and configuration.

## Reproduction, safety and evidence

Probe [REMIX-MATERIAL-CONTROLS-001](../reconnaissance/probes/REMIX-MATERIAL-CONTROLS-001.md)
defines protocol,launch,start/stop,tools/versions,bounds,cleanup and question map.
Existing light-tuning launch/elevated-parent policy remains. No UAC/security/ACL
changes or additional sponsor steps. Build tools/remix_runtime/build_live_return.ps1
with PS7;VS2026Community18.7.3/C++20/W4/WX/Brepro,pinnedRemix1.5.2/SDK0.6.4.
Python3.12.14;TEMP/TMP=artifacts/test-temp. Full Python unittest discovery under
tests/test_*.py. Material native unit:vcvars32/64 then cl /std:c++20 /EHsc /W4 /WX
tests/remix_material_control_tests.cpp /Fe:material_control32/64.exe /link /Brepro,
from artifacts/remix-runtime/live-return-bin;execute each. Own PID-specific directory
only,removed after test;no game assets touched.

Initial unrestricted-temp unittest invocation failed sandbox temp-directory access;
rerun used project-local temp with scoped tool elevation. No global permissions
changed. FuelGuard attached using current thread;advisory hook verified,daemon not
spawned. No external package updates/network dependencies.

Preliminary standalone020339-402543PARTIAL:unequal pair dimensions intentionally
rejected.020445-171886PARTIAL:actual initial material loaded .4/0 but fixture waited
for a reload receipt not emitted on initial creation. Added explicit initial SDK
receipt;not attributed to rendering failure. Both retained,never counted as PASS.

Final source-frozen matrix commands,each `python tools/remix_runtime/qualify_live_return.py
--execute` plus these exact argument sets,in order:
`--material-controls`;none;`--addon`;`--slow`;`--disconnect`;`--addon --visible`;
`--addon --textured --capture-image`;`--addon --textured --slow`;
`--addon --textured --disconnect`;`--light-wiring`;`--light-types`;`--project-fill`.
Then `--qualify` with the twelve exact emitted run folders. Standalone only,no SFC.
60s/32MiB plus128MiB image cap each;owned-process shutdown. Existing game tuning
30min/33min ceiling,128MiB image warning64/32MiB logs warning16/10GB aggregate.
No full geometry logging,image stream or new source-asset capture frequency.

## Validation and outcome

257Python tests PASS3.603s. Native request89/UV14/light-wire25 eachx86/x64 PASS;
new material parser14checks eachx86/x64 PASS,including truncated/nonfinite/bad
checksum/range/duplicate/last-good/recovery. git diff --check PASS (line-ending
notices only). Both client hashes match expected
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.

Preliminary material gate020736-930151PASS:SDK receipts .4roughness/0illumination,
.7/2then .5/1;invalid99roughness rejected,last good retained;fresh fca group/pair
illumination present,continued1920x1080 returned output,normal host/fixture exits.
This corroborates field wiring/derivative provenance and runtime SDK application,
not yet sponsor appearance/native-fidelity confirmation. Full matrix/preflight/
archive pins and final state appended after completion below.

The first twelve-case matrix020736-930151through021153-776971passed all gates.
It is superseded,not rewritten. Second matrix021533-463417through021950-529990
also passed all twelve runtime cases,then receipt issuance correctly rejected
source mismatch because the final fail-dark fallback changed during that batch.
No guard bypass/relabeling:rebuild and rerun all twelve on frozen final source.
No failed gameplay is inferred from these precautionary qualification reruns.

Development archive20261018-material-controls-development.zip:26completed runs,
551entries,13,486,488B,SHA256
A78D07E2B5A78FF9E295B85C6CCF95E99AFFA992E115A17DDAC4E7479406204F,
CRCverified. Includes JSON/logs/TOML/packets/seed/INI;repeated image copies and
generated binaries excluded,raw retained. First broader archive selection exceeded
the1GiB conservative source reservation and stopped BEFORE creating a ZIP;no data
deleted. Final qualification archive/pins below. No unbounded archive output.

Known issues remain:SDK40shutdown diagnostic despite APIshutdown0;no original
ship suppression,frame/depth-correct replacement or universal asset coverage.
Existing014955-223784-in-game evidence (pre-task) reports normal game exit,
4912drawn/failed0,unchanged files,but runner classified optional renderer exit
unexpected. Do not overwrite that PARTIAL or silently claim it was fixed here.
Current task has no actual gameplay evidence. No changes to source light physics.

Exact next action after final qualification: sponsor uses SAME light-tuning
launcher,compares illuminated markings on the extra ship and adjusts materials.toml
while playing;exit normally. No need to repeat light alignment or RE first.

## Final qualified checkpoint — READY FOR SPONSOR TUNING

Twelve final source-frozen cases022120-968869through022538-965332(20261019UTC,
all suffix-live-private) PASS. Exact list is in source-matched receipt
artifacts/remix-runtime/deps/live-return-qualification.json,SHA256
3DEA262623CC30990F0C506C58DC9F0689B9F70DD20BC3BAE25E17985598FCD1.
All flags including material_controls_qualified,project_fill_qualified and
light_types_qualified true. Final hostSHA256
795357FED1E96A689B3CD6BA2EC2BD7FBA464230B7AEF3BBF0087E18311CC4A1.

Final material case022120-968869uses recorded fca fixture geometry/fresh simulated
transfer,NOT new gameplay.58groups/56materials/30derived illumination pairs;
61,712,698B images/no64MiB warning,101,556,224B conservative image memory.
Raw UV/source pixels unchanged. SDK .4/0→.7/2→.5/1 receipts,one invalid edit
rejected,continued1920x1080 output. All texture/slow/disconnect/camera/lifecycle/
native-light/type/dome gates pass with normal owned-process cleanup. Shader black
fallback retained. Actual SFC visual/native-strength validation remains pending.

Final257Python tests PASS3.853s;native89request/14UV/25light-wire plus14material
parser checks eacharchitecture PASS. Parser/TOML/diff/path checks PASS.
Read-only `run_return_game.py --light-tuning` preflight PASS,no game/renderer start.
No StarFleetOP/ship_live_host/d3d11fixture process remains after final check.
Both clients still match the SHA above. Existing lights.toml preservedSHA256
210A85B39F7CEA1731D35195FBB4AC5434FF3D20640231D9A00376F116028437;
new materials.toml defaultsSHA256
009A2C83CA33E9624ACED0B2D8A92F7A13ACE35DD1E4586F981320E4E003242E.

Final archive artifacts/remix-runtime/archives/20261018-material-controls-qualified.zip,
6,290,069B,SHA256688C2D06A0CD276D8012D588121F35261B555B5D695975D37D92CD773609C5D9,
260entries,CRCverified. Includes receipt/configs/provenance/packets/logs and one
prepared-image PNG;repeated DDS/original-image copies/generated binaries excluded.
Raw retained,not deleted. Total retained runtime evidence8,601,092,811B,within10GB.
Development ZIP separately preserved above. No uncontrolled multi-GB capture.

Final HEAD2fa8032 unchanged,index empty;15tracked modified entries/48untracked
entries (Git collapses config directory). All prior work retained;no stage/commit.
CONFIRMED:offline implementation/provenance/SDK-field/transport safety checks.
STRONG HYPOTHESIS:useful modern illumination appearance. Exact native lighting
fidelity remains PARTIAL. No new milestone completion/replacement claim.

Next exact action: run existing start_light_tuning_session.ps1;observe extra ship's
illumination,save materials.toml roughness/illumination edits,exit normally. No
new camera exercise,timestamp,manual RE,UAC prompt or renderer-tech decision.
