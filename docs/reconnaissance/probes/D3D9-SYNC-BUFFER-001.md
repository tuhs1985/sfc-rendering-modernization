# D3D9-SYNC-BUFFER-001 — paired one-frame presentation

Default-off additive player-ship proof. Authority: sponsor's synchronized
buffering instruction; existing [contract](../synchronized-buffer-contract.md).
Preserve old unbuffered launcher and all original drawing. No prediction,
original-ship suppression or new visual tuning.

## Prepared sponsor test

Run from the established elevated parent:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\d3d9_proof\start_d3d9_buffered_scene_session.ps1"
```

Enter the familiar two-ship skirmish. Play normally, switch cameras freely and
move/turn; keep both ships alive for this comparison. No timed movement cues or
manual timestamps. Look for whether the extra textured ship stays present and
whether controls/HUD/cursor feel normal. Exit normally at the final two LOW
beeps after the 90-second tactical window. Report any flicker or sluggishness.
Do not manually change proxies, terminate the game, or launch concurrent tests.

## Collection and adjudication

Runner verifies copied process path, hashes/configuration and source-locked
qualifications; enables buffer only in its children. Capture native input,
output ownership/timing, new `D3D9-SYNC-BUFFER-001.bin` and decoded audit,
existing lifecycle/cleanup/normal-exit/client-hash evidence. At most one adjacent
frame/50 ms, two history slots, 8,192 records and existing run caps. Validate
new audit's scene/output correspondence, not equality to current Present.

PASS for this bounded test requires repeated matching output, no cross-owner or
camera mismatch, acceptable sponsor-reported controls/continuity, bounded
resources, normal exit, controlled unload, proxy restoration and unchanged
clients. Partial if holes remain or control latency is objectionable. Safety
failure/invalid pairing blocks broader use. This is NOT seamless universal
coverage, replacement or formal milestone completion.

Historical Run106 offline prepared evidence: buffered fixture
`artifacts/remix-runtime/runs/20261022-035401-772393-return-fixture`,
593 paired records, zero dropped/failed, exact saved native HUD/scene markers;
subsequent Run107 actual SFC test FAILED with alternating flicker. See Run107;
do not promote the historical offline result into runtime acceptance.

Run108 corrects queued-image protection and worker GPU-fence release. Prepared
retest uses the SAME launcher/instructions above, not the unchanged Run106
binary. Offline early-ready041830-729796=589/600 and late041923-373411=588/600;
both zero overwritten, valid paired provenance and normal fixture cleanup.
Unbuffered042011-310157=595/600. Gates now require BOTH delivery phases and
33actualGPUchecks in each architecture; source/binary locks prevent stale use.
Actual corrected-buffer SFC continuity/control acceptance remains PENDING.
