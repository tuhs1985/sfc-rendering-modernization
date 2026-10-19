# Run43 — first-pass native steady-light wiring and live ratio controls

SFC-RETURN-20261018-43;2026-10-18 America/New_York. Sponsor authorizes:
(1)normal test harness to check wiring;(2)subsequent minimal-recording tuning
session ending on their normal game exit. **This run prepares FIRST PASS only**;
longer mode deliberately gated on actual wiring result,not quietly enabled.
No new game run or milestone completion claim.

## Baseline / engineering decisions

HEAD2fa8032,indexempty,Run40–42 uncommitted work preserved. Read HANDOFF,actual
native-light evidence/control schema,SDK host/camera/worker/runner and controller
time limits. FuelGuard actual-thread hook attached;no helper/subagent/daemon.
Main/fill visual interpretation is sponsor's useful working inference. Captured
native directions/multipliers/type0response arithmetic are evidence. GI and type5
mapping remain unqualified;no detour to measure speed or native shadow mechanism.

Two **fresh** type0lights replace the provisional inspection light's DRAW in
explicit --light-wiring mode. Legacy path unchanged;provisional light resource
may still be allocated there but is not drawn in wiring mode. Directions use
native scene coordinates matching existing model/view conversion. This is an
experimental adapter mapping,not native pixel/shadow/photometric parity. Unknown
slots/types are not guessed into standard point lights. Existing original ships
and tactical UI remain ON;no suppression or final renderer architecture.

Existing default-off observer variant continues bounded5Hz/2owners/900records.
External Python relay consumes complete appended raw records,checks semantic
session/selected owner/active type0prefix and correlates source age to current
owner elapsed time. Adds34ms conservative margin for sampled row;config saves
never freshen native time. No new IO/allocation/SDK calls in SFC render callback.
Input validation,selected identity and current camera/pose checks retained.

## Controls and transport

Active `tools/remix_runtime/config/lights.toml`,IDs native_directional_0/_1;
strict validator and separate last-good reload state. Effective radiance=native
RGB*native scalar*conversion_scale*master_multiplier*per-light multiplier*RGB
multiplier. Defaults conversion1/master.5 produce.75/.125 for observed1.5/.25;
not calibrated physical units or exactly half the old one-light image.
TOML64KiB cap,poll2Hz;relay10Hz reads5Hzbank. Invalid/partial edits retain last
good whole configuration. Saves accepted config plus first16revisions only
(<=1MiB),bounded100messages then counters. No native data/config writes.
Per-light shadow/non-raytraced toggle remains unsupported,explicitly rejected.

Fixed200B file atomically replaced outside SFC;header version/session/selected
owner/model/source/frame/observedQPC/configrevision,2fixed light rows,FNV64.
SDK host validates checksum/identity/finite/direction/radiance/sourceframeage<=30
and QPCage<=500ms. Stale/missing state stops extra submissions;original game
continues. Existing100ms additive image limit unchanged. Create/update/destroy
lights only after prior output fence completes;both lights SDK drawn each output.
No future D3D9/D3D12 backend automatically inherits these unit/shape policies.

Native light type5/effect sync is NOT implemented in this first pass.5Hz source
is for the two demonstrated steady lights,not a claim of sufficient transient
sampling. Long tuning still needs separate live-state/no-raw-transcript handling,
exit lifecycle and safety qualification;current90s limits are not bypassed.

## Missing-report follow-through

Prior Run42 raw survived but original result.json absent;exact root cause remains
unrecorded. Added atomic early IN_PROGRESS checkpoint and terminal exception
capture,4MiB report cap and nonfinite/serialization fallback to explicit PARTIAL.
This guards against absent evidence;does NOT retroactively recover missing run
state or pretend the original root exception was reproduced. Offline invalid JSON/
exception tests pass. Need actual runtime validation of new finalization path.

## Tools / commands / results

VS2026Community18.7.3,C++20 /EHsc /W4 /WX /Brepro;x86/x64. Python3.12.14,
existing numpy/tomllib;PS7.6.5. No dependency installs or global security changes.

```text
pwsh -NoProfile -File tools/remix_runtime/build_live_return.ps1
python tools/remix_runtime/light_discovery.py
python -m unittest discover -s tests -p test_*.py
python tools/remix_runtime/run_return_game.py --light-wiring
```

Native build PASS,89request+14UV+19light-wire checks eachx86/x64 PASS. Native
packet tests cover500msboundary,stale/future frame/time,wrong session/owner/model/
source,checksum,invalid direction/nonfinite/negative radiance. Python240PASS6.220s,
TEMP/TMP artifacts/test-temp;ratio halves exactly,invalid partial edit preserves
last good,config-only save preserves native timestamp,report fallback PASS.
PowerShell parser/source/diff checks PASS. Accepted observer binary not overwritten.

One preliminary wiring fixture passed before extraction of independently tested
wire validation;superseded by final source-matched9GPU gates. Final fixture
20261018-232537-674923-live-private uses **synthetic** native records with observed
type0values,real recorded mesh/textures and actual public SDK host. It demonstrates
API receipts.75/.125 then hot-reloaded.375/.0625,2accepted configs/65packets,
maskIoU0.99886925795053,host0/native0. Not actual in-game native-light validation.
Eight accepted baseline/slow/disconnect/strict/capture gates also PASS. New
light_wiring_qualified=true required by runner. No GPU-readback volume expansion.

QualificationSHA256
8F15C450C08DE56843AE01488EB780C142682C91C7B87A093C0154C420C0851D;
host AD9A9200AF2171942A2252A47EF2EDB91874CD3ED238CD048F2CD8D594012A17.
Observer source receipt refreshed;actual dedicated DLL remains recorded by
native_lights.qualification.component_sha256. Existing semantic_calibration
component_sha256 is accepted BASELINE pin,not the variant's loaded DLL identity.
All exact9folders/pins in qualification receipt and
[curated summary](../reconnaissance/evidence/20261018-light-wiring-preparation.json).

Archive36,248,117B,CRCverified,raw retained,no deletion:
artifacts/remix-runtime/archives/20261018-native-light-wiring-qualified.zip,
SHA25628CB4069C0A79DC57D9523E62667A0A3C5B15CFFC4D0BAEEBF4F29E286ECEF62.
Existing32MiB nontexture/128MiBimages/10GBaggregate/90s tactical/300s workflow
bounds retained. Accepted componentSHA256BCC3BB19276A740E514D5CA4C0A1CF09ACF0169416251C1F552384AE069B8FE1;
both clientSHA2564D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.

## Changed files / state / next action

Added live_lights.py,remix_light_wire.h,remix_live_lights.h,run_report.py,
start_light_wiring_session.ps1,active lights.toml/configREADME,wire tests,
test_live_light_wiring.py,probe,curated summary,this record. Modified light_controls,
host/fixture/build/qualifier/sourcepins/mainrunner/PowerShell launcher. HANDOFF and
active increment updated. Two initial multi-file patches rejected wrong context
before ANY edits;corrected patch applied,not partial source state. Routine build
escalation used for existing protected output artifacts;no sponsor UAC added.
No source client/asset/reference changes,stage or commit. No active session needed.

**READY FOR SPONSOR FIRST-PASS RUNTIME TEST** via start_light_wiring_session.ps1
from established elevated parent. Usual two-ship skirmish,brief camera/ship motion,
normal operation checklist,exit at two-beep request. Assess SDK light receipts,
source identity/age,final report and cleanup before preparing longer tuning mode.
Do not ask sponsor to tune under this90s deadline;second pass must honor their
minimal-recording/exit-driven request instead.
