# Run57 — separate live Remix image controls

Date2026-10-18 America/New_York (qualification UTC2026-10-19). Active task:
sponsor-authorized image-control increment, no milestone advancement or gameplay.
Starting clean357bc703e3dc0923cd4c7801ec87e99abc01f157 on codex/github-sanitized.
Fuel Guard attached existing trusted hook; no daemon. No helper/delegation.

## Question and baseline

Which native brightness/exposure/tone-mapping controls actually affect the SDK
FINAL_COLOR returned by our current textured additive path? Add only missing
local grading/gamma and keep source lights/materials/default image unchanged.
Reviewed newest handoff, production host/worker/config/qualification/build source,
Run49–56 records, dependency manifest and current light/material baseline.
No original client/asset edits, no original suppression or new renderer design.

Pinned official source confirms separate local/global paths and automatic exposure
defaulttrue. Native global grading is not used in local mode. Associated source
nominal brightness key is absent from actual DLL's SDK lookup (error1), despite
mode and auto keys succeeding. Native exposure and global grading options do work.
Exact references, probe configuration and limits: REMIX-IMAGE-CONTROLS-001.

## Implementation

Default-disabled config/image.toml plus restore example, bounded500ms worker relay,
48byte checksummed packet, native host validation and last-good application.
Brightness0..100 maps public slider's3-stop-span EV formula through working native
exposure, independently summed with exposure_ev. Native exposure/auto/mode in both
paths; native contrast/saturation in global. Only missing local contrast/saturation
and display gamma use a small host-owned GPU pass. Neutral bypass exact; disabled
restores tested startup local/auto defaults. New8.29MB private scratch, same shared
output; native event fence before publication and bounded retirement drain.
Original SFC callback/compositor, textures, lights and material files unchanged.

## Investigation and validation chronology

- Sandbox compiler import-library overwrite denied; rebuilt using scoped approved
  compiler execution outside sandbox. No permission/security setting weakened.
- First GPU probe caught HLSL reserved identifier `linear`; corrected to toLinear.
- Next probe pinpointed rejected rtx.userBrightness; removed unsupported option
  and used validated native exposure mapping instead of silently ignoring failure.
- All image cases then produced valid pixels but probe exited0xC0000409 after SDK
  shutdown. Matched existing host's WNDPROC restoration before Shutdown, then probe
  exits normally. Existing unrelated SDK cleanup warning remains a separate issue.
- Standalone actual-runtime case20261019-034903-325774-image-controls PASS:
  23.625s,7,690B output,15case statistics. Actual GPU oracle confirms neutral bypass,
  gamma direction/value, grey saturation, BGRA order and alpha preservation.
  Local manual RGB≈121.98/35.51/25.47, EV-2≈44.81/13.63/10.37,
  auto≈214.40/100.86/72.98. Global manual≈126.94/55.96/44.97,
  saturation0≈77.54 each; contrast0≈116.92 each. Disabled restoration within
  <1RGB level of startup. These are synthetic fixed-scene pixels, not new gameplay.

Additional final source-matched return matrix, tests, actual sizes, hashes and
preflight result are appended after completion. No unsupported success claim.
Changes remain unstaged/uncommitted; no push authorized. Exact next action after
offline qualification: sponsor may use existing tuning launcher and edit image.toml;
no timestamps, manual RE, new UAC sequence or light/material reset required.

## Final qualified result — READY FOR SPONSOR TUNING

CONFIRMED offline: thirteen source-frozen production-return fixtures from
20261019-035047-156728 through035541-157497-live-private PASS, followed by final
20261019-035615-182507-image-controls PASS (17cases,26.157s,8,673B before JSON
receipt). Boosted1.5contrast/saturation also measurably work in BOTH modes.
All return cases have failed=0; image reload applies4valid profiles, rejects one
invalid gamma, restores disabled baseline and exits normally. Actual production
host shader preserves normal camera/silhouette and cleanup behavior in fixtures.
Full paths, source/binary hashes, case statistics and sizes:
docs/reconnaissance/evidence/20261018-remix-image-controls.json.

Current source/binary-matched receipt
artifacts/remix-runtime/deps/live-return-qualification.json has all flags true,
including image_controls_qualified. Final hostSHA256
1569626B011525F5A73A4571851DBCC3099383A21387AF0D7CDEABE0A9A0D26B.
Final267Python tests PASS4.726s; native image22/request89/UV14/light-wire25 checks
per x86/x64 PASS. Python/TOML parsing, local documentation links and diff checks
PASS. No CDD edits or claims of native lighting parity/frame-exact replacement.

Read-only tuning preflight initially correctly rejected stale native-light
discovery receipt because it includes run_return_game.py. Rebuilt/retested that
dedicated observer with existing build_light_discovery.ps1, not a bypass:
core9/observer13checks per architecture plus actual synthetic scene/worker tests
PASS. Updated receiptSHA256
05581DD6EF9727A2E224EBE49B8672A882E5DCB5979107F066793CB2F9FDAD60.
Final `python tools/remix_runtime/run_return_game.py --light-tuning` PASS,
explicitly no game/renderer start. No owned probe/fixture/SFC processes remain.

Lights unchangedSHA256 FC55CE88326AC4D544D166D42882540C257B2E54671517F9F6CD2F93B3F70E2F;
materials unchangedSHA256 5AF94EE33CA8B2A658802D4B23D4BFBCE8A7D5D7AB93ED6DCD56BF14996BAD31.
Both original/test clients remain
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.
No executable/reference originals or accepted game proxy changed. Existing SDK40
shutdown warning persists in production fixtures; not reclassified as resolved.
Earlier failed standalone probe receipts retained as historical diagnostic evidence.

Archive: artifacts/remix-runtime/archives/20261018-image-controls-qualified.zip,
708,860B,183entries,CRCverified,SHA256
6DEBA224CC67DFF9188973DEFA2BF3B309807BBA43CC38DC252EBB5575D11094.
Preserves logs/results/manifests/config snapshots/packets, not repeated full image
derivatives/binaries. Raw evidence retained locally, no deletion. Overall retained
runtime evidence9,341,971,742B remains below sponsor10GB allowance; do not repeat
the whole matrix casually. Existing32MiB logs/image-budget controls remain.

### Exact repository change scope

Modified: README.md; docs/HANDOFF.md; tools/remix_runtime/{build_live_return.ps1,
config/README.md,live_lights.py,live_return.py,qualify_live_return.py,
run_return_game.py,ship_live_host.cpp}.
Created: docs/reconnaissance/evidence/20261018-remix-image-controls.json;
docs/reconnaissance/probes/REMIX-IMAGE-CONTROLS-001.md; this run record;
tests/{remix_image_controls_tests.cpp,test_image_controls.py};
tools/remix_runtime/{build_image_probe.ps1,config/image.toml,
config/image.example.toml,image_controls.py,image_controls_probe.cpp,
qualify_image_pipeline.py,remix_image_adjust.h,remix_image_controls.h,
run_image_probe.py}.

Final Git: starting357bc70 unchanged, all23 source/doc/test entries unstaged or
untracked; nothing staged, committed or pushed. Native/generated results ignored.
CONFIRMED: tested native option behavior, GPU fallback and runtime-host reload,
source/binary checks, safety/restore fixtures. Actual in-game image tuning remains
for sponsor observation; no gameplay was requested or fabricated this run.
Exact next action: use existing start_light_tuning_session.ps1, set image.toml
enabled=true, edit/save one image control at a time, exit SFC normally when done.
