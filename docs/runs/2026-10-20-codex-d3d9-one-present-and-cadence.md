# Run75 — one-present correspondence and bounded offline cadence

Date2026-10-20 America/New_York. OFFLINE SUBPROOFS COMPLETE;no SFC launch or milestone claim.
Authority:approved additive execution plan,Run74receiver proof,sponsor continued
credits/work instruction. HEADd29111f7,index0;all prior dirty work preserved.

## Smallest question

Run73/74held every snapshot for24presents. Before live wiring,does ONE present
after a changed pose/camera yield the corresponding output,not a prior frame?
Then measure a bounded60Hz demand schedule without mistaking image-recording
overhead for delivery latency. This is NOT replay at original recorded timing.
Schedule cycles the3actual captured states;no interpolated/guessed movement.

## Changes / procedure

Host default behavior preserved. --single-present warms first snapshot24times,
then presents each changed state once,without10ms steady-state sleep. QPC CSV
records draw/Present,output copy/GPU completion,local readback and receiver ACK
costs. --paced-frames120or300(requires receiver)requests60Hz QPC demand for a
bounded offline stress check. Sequence remains unique;original source-frame and
full-state hash identify which immutable captured state supplied each output.

At paced mode,read back only sequence1and multiples59(to vary across3/4states),
no continuous images. GPU transfer/completion/ACK still happens EVERY update.
Optional --timing-only explicitly disables ALL CPU image verification in both
processes;result is TIMING_RECEIPTS_ONLY,never a passed pixel run. Prior matching
pixel evidence cannot silently become a same-run image assertion. Independent
analyze_schedule.py includes recording stalls and carries no CDD KPP3 claim.

All waits/readbacks/files still OFFLINE helper diagnostics,not SFC callbacks.
One surface set,existing ownership protocol and bounds retained. No change to
SFC hook/proxy,source geometry/UVs,camera,lighting or appearance configuration.

## Current evidence

042131-313260 KFF --single-present:24/1/1presents,all3triplets byte-identical
cross-process,all3projection IoU1,normalized depth error<=3.28e-7. Thus24warmup
presents not needed between these2changed snapshots. Ordinary draw/Present costs
555/355us,output completion5304/3087us;CPU verification dominates remaining time.
Do NOT call2updates sustained throughput or infer original source cadence.

042420-804415 KFF --paced-frames120:120GPU transfers/ACKs;9sampled images exact,
sampled projection IoU1/depth<1e-6. All119steady rows included. Completion from
due p50=11169us,p95=13061us,max35694us;5missed16.667msdeadlines. Local readback
max16291us,receiver including sample verification max13750us. STRONG HYPOTHESIS:
sample recording explains spikes;must compare a no-readback run,not remove rows
from the headline result. 5misses are retained,not a schedule PASS.

These completed payloads ZIP-compacted after decompressed SHA verification.
## Timing comparison and notification change

042605-959671 larger-FCA300updates at960x540,timing-only:299steady rows,0deadline
misses,p50completion11606us,p9513802.5us,max15075us. No CPU Map/image files in
this run;GPU copy/fence/ACK on every update. No same-run pixel claim.

042909-040834 FCA1920x1080,timing-only,receiver private DEFAULT GPU cache:
20/299deadline misses,p9516823.3us,max17764us. Peer stage stays~6ms. This is a
retained short-run miss result,not hidden by the lower-resolution result.

Replaced helper polling sleeps for READY/ACK with two current-user-only,
unique-session auto-reset Windows events. Metadata state and GPU fences remain
authoritative;events only wake workers. No SFC callback waits or security changes.
The native receiver now copies to a private DEFAULT GPU cache;only verification
samples additionally copy to staging/Map. Not direct reading of producer storage
after ACK. Full1080p shared+private+both staging triplets total99,532,800bytes,
within128MiB output-resource bound;ordinary renderer internal allocations separate.

043044-681667 FCA1920x1080,300updates,timing-only,event notification:
0/299misses,p5010902us,p9511979.8us,max14036us. Peer p952121us versus6051.1us
before. These two runs support worker wake-up overhead reduction;they do not
establish SFC GPU contention or source-to-present timing. No optimized engine,
image-quality,texture,source camera or geometry changes.

Final-event source fault rechecks all PASS under direct64-runs:
043220-494860 normal FCA,043244-617410 slow,043308-453207disconnect,
043329-239923exit-acquired,043349-853829stale-ACK,043410-447089invalid.
Normal/slow all9images identical across processes;FCAprojectionIoU>=.9997397866,
depth<1e-6 with24/1/1presents. Expected rejection/retirement behavior unchanged,
all owned jobs0/remaining0/API Shutdown0. Warning40still not leak-qualified.

Exact next action:prepare the smallest read-only source-offer-to-presentation
timing observation. The current
60Hz schedule is artificial demand over repeated recorded snapshots,NOT original
recorded rate or live gameplay. A source frame counter alone is not a seal.
Do not wire image presentation or ask for an additive game run on these results
alone. No original ship suppression or different topology authorized by success.

## Output extent finding / guarded disposition

043452-443042 synthetic640x960:all4independent translation/rotation/camera
controls IoU1,depth error<2e-7,12cross-process images identical. Black provisional
plate still only a geometry/depth control,not texture-color parity.

043513-017654 synthetic1280x360:TRANSFER bytes match,but actual depth is scrambled,
all4IoU0. Exact5184positive geometry values remain but scattered in tile-like
bands;15360unexpected zero-depth pixels also appear. CONFIRMED returned-layout
failure,not a proven camera/UV/geometry error. GPU import/copy-layout issue is a
STRONG HYPOTHESIS only;root cause unisolated. Do not repair source matrices or
silently repack pixels to hide it. This unusual extent is NOT qualified.

Checked actual full1920x1080FCA to avoid mistaking timing-only success for pixels.
043740-344674 then final guarded-source043953-529063:one provenance-identical
captured snapshot,pixel triplets identical across processes,silhouette IoU1,
normalized depth max error1.5770470580545037e-6 (<unchanged1e-5acceptance),4077
distinct covered colors in finalcase. Single-snapshot derived fixture trims only
frame tail/count;raw capture and geometry/UV/groups unchanged. This bounds two
full-resolution verification triplets plus source assets within128MiB scratch.

Adapter admits only measured960x540,640x960,1920x1080extents by default. Other
extents require explicit --investigate-extent OFFLINE opt-in in runner/native
host. Neutral scene format remains unrestricted within original bounds. Future
live resizing to an unqualified extent must report partial/omit extra ship,not
substitute stale or scrambled output. No claim arbitrary output sizes work.
Analyzer previously wrote review-required but returned CLI0;now returns2on
failed pixel adjudication. The wide failure was reviewed/preserved,not accepted.

## Validation / closeout

323Python tests PASS4.446s;24native wire checks PASS;native x86/x64 builds /W4 /WX
PASS. Final host SHA256 D97F7B905F416E728867E615C04A5C6B02030304E8CB12F7690D0E1BA1B5DC84;
receiver5296748E6A5F7E5F868B534C4BC3C2CE84D6034E11F401BD8935CDE3DF8380C5.
Actual per-case source/EXE/runtime hashes remain in result.json;earlier timings
belong to their recorded binary,not silently relabelled as final binary runs.
Final guard adds admission only;final1080p pixels rechecked afterward.

All owned jobs finish0/remaining0;API Shutdown0. Generated payloads ZIP-compacted,
decompressed hashes verified;no source capture or client assets deleted. Counted
outputs9,811,055,015B/10GB. Both client hashes unchanged;four sponsor appearance
TOMLs no diff. git diff --check PASS. No owned host/receiver/bridge/game active.
All source/docs/tests unstaged/uncommitted,index0,HEADd29111f7,no push.

Changes:direct64host/runner/analyzer,receiver/producer/channel headers,
test_d3d9_receiver.py,test_d3d9_schedule.py,native output wire tests,README,
this record,HANDOFF,execution/output contracts. No source hook changed in Run75.
Next unit is source-offer/presentation timing,not game image integration yet.
