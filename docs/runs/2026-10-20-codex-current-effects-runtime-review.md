# Run84 — current lighting/material runtime review; startup and fast-camera defects

Local date2026-10-20 America/New_York;raw run folder uses UTC20261021.
Active M1 ordinary-D3D9 additive proof,not replacement/formal TRL PASS.
Read HANDOFF,Run83,latest actual records before analysis. Fuel Guard attached.
HEADd29111f7,index empty,existing dirty work preserved. No new SFC run/helper/
agents/staging/commit/push. No renderer implementation or visual-policy changes.

## Sponsor observations and disposition

CONFIRMED sponsor observation:copy is at correct scene height;current settings
come through with good texture appearance;fast camera adjustments still flicker;
initial~20s load is unacceptable as an operating baseline. Accept demonstrated
height/appearance behavior,not steady delivery or acceptable startup. No fresh
explicit HUD/control attestation in this message;do not invent one.

`artifacts/remix-runtime/runs/20261021-024303-198180-in-game` ran full90s formal
tactical capture after20.047s preparation. Selected player-fixture FCA owner2/
revision2,matching accepted asset hash. Relay preparation29.344s includes earlier
workflow waiting and is NOT the pure initial-load number. Full workflow146.953s.

Actual component cleanup CONFIRMED:duration stop,component removed,hook bytes
restored,unloaded,controller0;normal game exit0,renderer0,GPU job0,no owned
processes remain. Accepted/copied critical hashes and launcher settings unchanged,
temporary proxy restored. Client SHA256 remains
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.
Native source timing16354records,no invalid/drop/wrong-thread/snapshot failures.
Raw-owner channel separately reports one source rejection;retain as distinct
counter,not contradictory evidence that every source path was perfect.

Presentation admission4956matching/5430eligible checks (~91.27%);474old/different,
2other audits.4965actual image submissions,431stale-image rejections,no invalid/
resource/depth/pool-busy failures.5983publications include583unclaimed overwrites
and work continuing while display is intentionally disabled during teardown;
4965/5983 (~83%) is NOT the formal presentation success fraction. Last displayed
source frame6616versus7189last timed output is consistent with that teardown phase,
not by itself evidence of a ten-second unexpected dropout.6000input cap reached
near source shutdown;do not assume it caused sponsor's camera flicker.

All5983timed outputs:median13.218ms,p9515.753ms,max36.374ms. Through last displayed
source frame6616:5415outputs,median13.091ms,p9515.783ms,max35.170ms. Different
denominators must remain explicit. Typical source-to-Present budget~15.5ms,so
tail misses remain plausible and actual stale counts confirm deadline failures.
Specific miss-by-miss correlation with fast camera input is not established;
sponsor observation is direct,exact mechanism association remains STRONG HYPOTHESIS.

Current effects preserved:three configured light descriptors,854fresh native-light
relay packets,10transient source-busy reads,zero invalid;17light-input omissions.
Background host cache9139reads/18failures,existing expiry/identity checks retained.
Light stage median.004ms,p95.005ms,max.290ms;GPU rendering/transfer median11.890ms,
p9514.562ms,max29.085ms. Light-file critical-path delay improved;remaining cost is
not per-frame texture regeneration. Mesh and original textures are uploaded once;
existing roughness/illumination/material mappings remain cached/prepared resources.

## Durable next-work boundaries

Two separate OPEN defects:initial asset/runtime preparation latency (~20.05s),
and current-frame delivery tails/fast-camera flicker. Do not call satisfactory
fallback baseline or move directly to all-model stress/identity survey yet.
Next smallest action:profile initial preparation stages offline,cold versus warm,
to distinguish image preparation/material generation/runtime initialization and
first-ready delay. Reuse captured evidence;no identical gameplay rerun requested.
Do not silently hold old ship pixels,reduce current effects or add whole-frame
buffering;that synchronization expansion needs separate sponsor approval.

Sponsor's agreed direction:after single-ship path is satisfactory,test all supported
on-scene models in one shared scene,then use findings for identity survey. Adapter
interface gates are separate from Remix appearance/game-composition gates;trace
renderer substitutability to CDD RISK-7/KSA-3 and render access to CTE-1/REQ-REN-001,
not a new capability requirement or automatic gate closure. No CDD changes here.

## Evidence preservation/validation/final state

Extended archive_fixture_binaries.ps1 only for explicit CompletedGame additive runs:
require completed normal exit,controlled unload,original/launcher integrity,proxy
restoration,copied critical equality,normal owned GPU job and no active processes.
Only manifest-hashed generated GPU scene/image INPUTS archived;not raw source
packets/logs or any installation files. Reject actual-game paths without explicit
switch and fixture paths with it. Source change makes old additive qualification
stale;do not give/reuse old launcher until next bounded work is qualified.

Archive196entries/4,627,680B:
`artifacts/remix-runtime/archives/20261021-024303-198180-in-game-generated-inputs.zip`,
SHA256352091B340CF7E613DB7452ECC5570950EF81F3443BDAE3C1AD54D0CAFD4C20B.
77,337,848B exact generated copies removed ONLY after every decompressed hash
matched. Fully recoverable;raw gate packets,light records,manifests,timings/logs
remain. Aggregate9,770,159,898B/10GB;no cap increase. No game files removed.

Validation:machine result/manifest/controller/launcher/GPU receipts reviewed;
timing CSV quantiles independently calculated;archive integrity/guard negatives,
PowerShell parsing,JSON/links and git diff --check PASS. No new native build or
gameplay test needed for this evidence-review/compaction change. Earlier360Python
and native tests are historical,not falsely rerun. Vendor disposal warning40 remains.
Files:this record,HANDOFF,curated runtime receipt,archive helper. Current source
files remain unstaged/uncommitted,index empty,no owned process/tool session active.
