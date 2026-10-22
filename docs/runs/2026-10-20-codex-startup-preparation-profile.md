# Run85 — offline startup preparation bottleneck

Local2026-10-20;artifact folders UTC20261021. M1 CONTINUES,ordinary-D3D9
additive proof. Sponsor challenges20s initial preparation. Diagnosis only;no
rendering fix/gameplay run. Read HANDOFF/Run84;Fuel Guard attached through trusted
recent-hook receipt,no daemon started. HEADd29111f7,index empty,prior dirty work
preserved. No helper/agents/stage/commit/push.

## Method and evidence

New default-off tools/d3d9_proof/profile_preparation.py replays Run84 fresh packet
and contemporaneous identity row from retained gpu/scene.json. Uses copied test
installation only as read-only original image source. No OBJ/template substitute.
Measures scene_bundle.prepare,output extent,material_binding.prepare separately.
No SFC/Remix launch,OS cache flush or cold-boot claim. First/repeat labels mean
within this profiling process,not guaranteed cold/warm disk caches.

Reproduce using the bundled Python with:

```powershell
python tools/d3d9_proof/profile_preparation.py --execute --samples 2
python tools/d3d9_proof/profile_preparation.py --execute --timing-only --samples 1
```

Source:artifacts/remix-runtime/runs/20261021-024303-198180-in-game,
gate/LIVE-SCENE-001-asset-2.bin and gpu/scene.json fresh_preparation_row.
Actual previous gameplay prep20.047s remains the runtime measurement.

Profiled samples under artifacts/d3d9-proof/material-runs:

-20261021-025445-862242:geometry0.340705s,extent0.050235s,materials38.116658s.
-20261021-025526-783058:geometry0.326555s,extent0.048411s,materials38.172323s.
-20261021-025857-973940:UNPROFILED geometry0.247860s,extent0.020182s,
 materials16.401657s,total16.669700s. Material pass~98.4%of this offline preparation.

CONFIRMED implementation/runtime attribution:material_binding.py nested save
reopens each generated DDS for exact RGBA equality. Installed Pillow
DdsImagePlugin.DdsRgbDecoder.decode is a pure-Python per-pixel reader/channel
unpacker.139decoder calls consume36.186/36.332s cumulative in the two profiles;
~56million o8 channel calls per pass. Profiling overhead inflates these totals;
do not report38s as ordinary startup. Geometry/original image handling is cheap.
STRONG HYPOTHESIS:this validation dominates the20.047s actual gameplay preparation;
offline unprofiled16.402s corroborates but does not separately time every remaining
runtime startup/first-ready component. No evidence that Remix rebuilds geometry
for20s or that textures are uploaded repeatedly per frame.

## Bounded execution and preservation

Each sample reserves192MiB within existing aggregate10GB cap. Existing material
archive helper compresses exact generated texture/DDS copies,checks decompressed
hashes,then removes only those copies. Sources,scene records,manifests,result.json
and profiles remain;ZIP is adjacent with -generated.zip,receipt generated-archive.json.
Successful samples each compact76,648,704B of generated copies. No game files removed.
An initial timing-only harness bug attempted pstats on a disabled profiler after
geometry:sample025640-211912 retains IN_PROGRESS failure report;20,583,296B generated
texture copies archived recoverably. Fixed stage to return direct timings without
pstats when profiling disabled;successful plain timing follows. This is a diagnostic
tool defect,not game/asset failure.

## Decision and next action

Do not accept20s as fallback baseline. Next bounded correction:strict bulk validation
for our generated uncompressed32-bitDDS format,retaining exact header/dimensions/
channel masks/pixels and identical produced bytes/hashes. Test corruption/truncation
and asymmetric RGBA fixtures against existing reference;do not simply remove checks
or change installed Pillow. Cache optimization is not needed to establish this cause.
No correction implemented here. Fast-camera delivery remains separate OPEN issue;
no buffering,quality change,all-model stress or replacement authorized by diagnosis.

Files:new profiling tool,this record,curated profile receipt,HANDOFF. Validation:
two complete cProfile passes,one complete unprofiled pass,archive hash verification;
syntax/default-off invocation,diff and client-hash checks recorded at close. No new
native build/full regression required for diagnosis-only tool;earlier tests historical.
Index empty,all work unstaged/uncommitted,no active game/runtime session. Existing
launcher qualification remains stale. Exact next action:implement/test bulk DDS
validation before another gameplay run.
