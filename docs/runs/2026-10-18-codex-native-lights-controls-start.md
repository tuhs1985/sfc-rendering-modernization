# Run40 — native-light identification and editable controls begun

SFC-RETURN-20261018-40;2026-10-18 America/New_York. Sponsor explicitly requests:
(1)identify SFC lights and add them to Remix;(2)per-light config controls including
intensity and requested raytracing participation. Both recorded durably in
[active increment](../reconnaissance/native-lights-and-remix-controls.md).
No new requirements,renderer architecture or milestone-success declaration.

## Baseline / evidence / decisions

Clean2fa8032 at start,indexempty. Read HANDOFF,Run18/light map/static verifier,
current scene observer/calibration/host/runner,approved milestone disposition.
FuelGuard attached actual thread through hook;no new daemon/helper/subagent.
Confirmed existing broad/presentation captures do NOT contain native light bank.
Do not recycle old process pointers or infer slot0=sun. No broad RE restarted.

Re-ran exact-client verifier41STATIC_PREFIXES_MATCH;ignored evidence
`artifacts/remix-runtime/light-state-static-20261018.json`. Manager64records,
enables,derived triples,reciprocal/global gate and native type-specific response
retain static support. Active lights,physical units,world/camera independence,
scene/effect classification and lifetime still require runtime evidence.

Pinned SDK0.6.4 header SHA256
`E623E4956A76894EEEF02361334C7C0458D4EC8BF49F729EC9038C36128BBF47`:
LightInfo/shape/USDEXT expose radiance,intensity/exposure,location/direction,
shape dimensions,volumetric scale;inspected public ABI exposes no per-light
shadow/non-raytraced illumination switch. **CONFIRMED interface gap in current
direct SDK path**,not a claim all future versions/backends lack it. Config request
off rejected explicitly;enabled=false removes ALL contribution,not shadow-only.
No silent no-op,global toggle masquerading as per-light,or patching Remix internals.

## Completed smallest unit — offline core, NOT a prepared gameplay probe

- Renderer-neutral6156B raw native snapshot definition/read-double/memcmp/live-
  validity core;all offsets asserted and safe manager vtable checked. Preallocated
  scratch supplied by caller;no IO,allocation,wait,SDK or process-open operations.
  No production hook includes this header yet;no active collector/worker built.
- Python decoder preserves64enable bytes and entire original16DWORD light
  payloads. First disabled slot terminates consumed prefix;later enabled slots
  retained without claiming contribution. Gate/type5/nonfinite handling explicit.
  Raw transforms retained,not silently treated as standard graphics matrices.
- Editable TOML example and strict validator with reviewed logical-ID registry:
  enable,intensity/RGB multipliers,position/direction,size/angular-size and
  volumetric controls. Schema example explicitly NOT active;runner option/runtime
  binding do not exist yet. No fake scene/effect IDs or unobserved native values.
  NaN/infinity/bools-as-numbers,bad ranges,duplicate/unknownIDs,unknown controls,
  incompatible shapes and unsupported raytracing policies rejected.
- Probe NATIVE-LIGHTS-001 documented before adoption:proposed5Hz/2owner epochs/
  900snapshots90s,8slot fixed queue,raw<=5,540,400B,new16MiB hard/warn8MiB,existing
  combined32MiB nontexture/five-minute bounds still binding. No images/geometry
  transcript. Sub200ms transients may be missed;do not claim complete weapons
  coverage. Actual queue,worker,runner still to implement/qualify before gameplay.

**CONFIRMED:**offline core/config behavior and existing static anchors.
**STRONG HYPOTHESIS:**bank captures at proven owner seam support useful native
directional/point-like light identification. Runtime mapping/controls not proven.

## Commands / validation / changed files

```text
pwsh -NoProfile -File tools/m1_component/build_native_light_tests.ps1
python -m unittest discover -s tests -p test_*.py
python tools/m1_component/verify_light_state_bytes.py CLIENT --output artifacts/remix-runtime/light-state-static-20261018.json
python tools/remix_runtime/run_return_game.py --capture-ship-image
```

VS2026Community18.7.3,C++17 /W4 /WX /Brepro,x86/x64:9native checks each PASS,
including stable capture,inconsistent bank,invalid owner/context,vtable,address
and failed-read handling. Independent struct offsets/size compile assertions.
Python3.12.14 existing Pillow/numpy/tomllib;232tests PASS4.384s,synthetic only;
TEMP/TMP artifacts/test-temp. Accepted textured workflow read-only preflight PASS.
No production binary/header included in accepted source-hash set changed;existing
qualification stays valid. Client verifier rechecks exact unchanged hash.
No game launched,no new UAC/security change,source/reference originals untouched.

Files added:active increment,probe,native_light_snapshot.h,
build_native_light_tests.ps1,native_light_snapshot_tests.cpp,native_light_state.py,
light_controls.py,config/lights.example.toml,test_native_light_controls.py,this
record. Updated native-light map and HANDOFF. Generated standalone tests/static
JSON ignored. No staging/commit;worktree contains only this scoped new work.
No active process/server/session needed to resume. No capture evidence to archive.

## Exact next action

Integrate this read-only core as default-off,rate-limited fixed queue at existing
MeshIdentity observation;add worker/output/runner and offline cleanup qualification.
Then prepare actual familiar skirmish light-discovery test. No sponsor gameplay
needed until runner is ready. Native-to-Remix conversion/config binding follows
observed classification,not guessed values. Per-light raytracing capability remains
an explicitly unresolved backend requirement for this implementation increment.
