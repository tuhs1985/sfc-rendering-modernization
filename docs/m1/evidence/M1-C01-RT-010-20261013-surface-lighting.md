# RT-010 — sustained owner-specific surface-lighting control

**PASS for the bounded diagnostic. M1 CONTINUES; no formal TRL4 or beneficial
visual-modernization claim.** Static/pure-graph tests, scoped live private-pointer
receipts, integrity counters and sponsor observation corroborate intentional
control of one ship's surface-lighting inputs through the original renderer.
[Definition](../probes/M1-C01-RT-010.md) /
[approved contract](../m1-c01-sustained-lighting-test-contract.md).

## Direct runtime proof

Run `artifacts/m1/runs/20261013-235127-enabled`, PID38996, component0.13.
Start2026-10-13T23:51:27.3588138-04:00;
completion2026-10-13T23:53:26.0464123-04:00. Automatic tactical gate,90s run.
Sponsor: "complete, did as requested, saw magenta ship (enemy) swapped camera to
it, observed color change and ligting change, then return to normal. no other
issues noted". Retain as attestation, not a frame-time measurement.

| Phase from actual marker activation | Observed/applied | Downstream receipts | Parent completions | First/last observed ms |
| --- | --- | --- | --- | --- |
|20s magenta identification |1200/1200 |source lease, not polygon override |1200 |0/19985 |
|5s neutral private mesh, normal color |299/299 |598 |299 |20000/24985 |
|15s reversed lighting vectors, normal color |899/899 |1798 |899 |25000/39985 |
|Original render path restored |1721/0 |0 private |0 private |40000/68688 |

All1,198 eligible neutral/altered graph observations were overridden, no missed
eligible calls in these phase totals. Two prep receipts per graph call are the
native downstream path, not duplicate publication. No interventions in phase3.
Marker duration threshold is20,000ms; last pre-boundary sampled call19,985ms is
normal frame sampling, not an early timer. The phase clock starts at actual
successful source substitution; sponsor had the requested20s identification.

Same owner epoch1/thread33896 throughout: ship`1C53AD88`, visual`1B12D600`,
Model0`14D2C590`, source`048F365C`, manager`04950038`;
original list`1C62D9B0`, neutral`60681F08`, altered`606AA81C`.
All452 primary polygons copied,1356 corner vectors reversed, not the earlier64
prefix. Graph pair332,336bytes, intact and pinned at stop; failure0. Each override
was guarded by current-original full-payload equivalence to the neutral graph.
Altered graph changes only vector sign bits; other payload/culling vectors/UV/
indices/positions preserved by reviewed code and offline exact-byte tests.

Wrapper006AC5A0/primaryreturn0042E55D and prep006ABFC0 retain same scoped
identity and exact private-list receipts. Original Model0/control flow continues.
Generic006AB410/native DIP remain previously established downstream anchors;
the hot geometry hook was disabled, so no new direct generic/native transcript.
Source leases:1200 applied/1200 restored,0 renderer replacements/rejections/
restore failures/active scopes. Legacy standalone tint remains disabled; these
shared lease counters belong to the surface diagnostic's separate20s marker.

**CONFIRMED:** owner-specific copied lighting inputs can deliberately change the
visible ship and then restore original rendering. **Not established:** better
appearance, complete lighting/material abstraction, all-model coverage, safe
mutating buffer reuse/earlyfree, physical identity continuity, or epoch recovery.

## Observer coverage and exceptions

Selected filter0 has18/18 valid corner windows through85s, owner1 unchanged.
Other filter1 has12/18 windows; its epochs2->3->4->5 follow observed gaps, including
an absence across windows7–12 while sponsor followed the marked enemy. Do not
diagnose destruction or sponsor error. General corner analyzer retains its
`Two-owner 18-window observation incomplete` finding; no code or acceptance
threshold was changed to hide it. This is auxiliary two-owner coverage, **not a
missing selected-owner criterion** for RT-010, which expressly asks to follow one
marked ship. Surface/wrapper/rejection analyzers have empty issue lists.

Total5392 rendered frames. Wrapper8620 primary/0secondary/5396unscoped;
accepted parent closures8620. Known00509843 count5396, semantic rejections0,
owner retirements3 affecting the other filter only. Zero rejections is a fixture
observation, not resolution of prior00413B2D/unowned-path questions. No retarget
or fresh-epoch intervention occurred. All existing exclusion/epoch uncertainties
remain scoped as before; no broad reverse engineering needed for this result.

## Safety, bounds, cleanup and preservation

All hooks restored and normal exit confirmed. Installed client independently
hash-checked unchanged; no game/controller or game-directory WINMM proxy observed.
Graphs remained resident/intact until normal process exit by policy; not early
unloaded. Sponsor reports no other issues, not a formal performance/stability
qualification. CSV339,448bytes/1180 detailed events; warning/truncationfalse,
owner/threadoverflow0. Same16/32MiB event and3MiB corner caps,90s runtime,
fixed graph pair<1MiB; no output firehose or dynamic graph growth.

18rawfiles total **985,934bytes**, retained ignored. Verified archive:
`artifacts/m1/archives/M1-C01-RT-010-20261013-235127.zip`, **93,108bytes**;
SHA256`91331EB7D50AE74297EF34E85815DAA7E11BF82F7A309400AE9C52EC40C69027`.
Every ZIP entry count/hash verified against source streams; nothing deleted.
Exact sources: surface summary and analysis, component log, wrapper/rejection/
corner analyses and packet, semantic CSV, metadata/INI, cues, telemetry/exit result.

Client SHA256
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`;
MD5`2BE8F713F81B1C68D50EAD6088C32886`.
Actual runtime component SHA256
`D17552E5B0194C4220EB37DFC48AC8F8A86191A93F57E6310ED587D1C4982F6C`;
controller`9C6CDA3AF6D397F8771C11822A90C2DC135595ED29B0473915FD81A3D29EBD08`.
Runtime rebuild hashes supersede preparation hashes for this capture.

## Decision / next boundary

The deliberately wrong, reversible surface-lighting control is proven for this
selected primary model. Review this checkpoint before any further implementation.
Next justified decision is whether to authorize a narrowly scoped beneficial
shading proposal, grounded in this control evidence. No C-02 implementation or
final technology selected; quality/performance/three-VMES/formal TRL4 evidence
still required. Do not repeat this passed diagnostic merely for more counts.
