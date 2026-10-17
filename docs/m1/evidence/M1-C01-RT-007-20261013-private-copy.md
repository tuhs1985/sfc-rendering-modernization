# RT-007 — one-use private input accepted by SFC

Result: **CONFIRMED one-use private polygon-input handoff; M1 CONTINUES.**
The original renderer consumed our private input without a reported gameplay
regression. This is not a new renderer, repeated substitution proof, or TRL 4 PASS.

## Experiment and direct evidence

[Probe definition](../probes/M1-C01-RT-007.md) governs component 0.10 and the
two-ship fixture. Run `artifacts/m1/runs/20261013-223631-enabled`, PID 29940,
started 2026-10-13T22:36:32.0002800-04:00, completed
2026-10-13T22:38:45.5934111-04:00. Sponsor: game ran as expected, no issues.

- Private-copy summary: attempted true, applied **1**, preparation receipts **2**,
  parent return **1**, failure **0**, intact true, pinned until exit true.
  Two receipts are downstream observations, not two substitutions.
- Handoff at 21,250 ms, following the 20-second setup and completed start cue.
  Owner epoch 1; thread 37568; ship `0AC9A0E0`; visual `0AC91388`;
  model `0FEEC518`; manager `04AA0038`; source `04A4365C`.
- Wrapper `006AC5A0` received original list `0ACA33A0`; the component substituted
  private list `606A63FC`, count 452. Preparation `006ABFC0` observed the copied
  list under matching scoped identity. Mainline return `0042E55D` identifies the
  primary path; parent completion corroborates continued original control flow.
- Complete pointer list copied; first 64 polygon headers/corner payloads copied,
  remaining 388 entries still reference originals. Payload 8,976 bytes; fixed slot
  20,512 bytes. Before/after fingerprint **4131310351**; integrity checks passed.
  Fingerprint is noncryptographic support, not a sole ownership/lifetime proof.
- 5,390 frames observed; 36 valid corner windows. Primary wrapper 10,779;
  secondary 28 (bypassed); unscoped 6,319. Accepted parent closures 10,807;
  preparation entries 34,252. Analyzer issues empty. Generic `006AB410` hot hook
  remained disabled; this run does not add a direct generic-draw transcript.

## Exceptions and limits

Known `00509843` path counted 5,394. Rejections 1,850: 685 visual exclusions at
`004EFC49` (observed first word `007B8D4C`), 240 at `00413B2D` (first word
`0069F280`), and 925 Model0 owner-missing exclusions at `0042FDD5`. Counts are
consistent with paired guarded exclusions; not an exhaustive per-call pairing.
No selected-address match was reported. The second visual caller's category is
**unresolved**; do not infer a ship type or valid vtable from its observed word.
These finite bypasses did not invalidate the selected-copy evidence.

Module pinning intentionally keeps copied data resident until normal process
exit. Hook restoration does not imply DLL unload or permit slot recycling.
No early-free/nonretention, repeat-use, all-owner, or secondary-path claim follows.

## Bounds, preservation and cleanup

90-second observation; 120 detailed-frame / 10,000 event / eight-owner limits;
CSV warning 16 MiB, hard stop 32 MiB; corner output 3 MiB cap. Warning/truncation
false; owner/thread overflow zero. Setup and release cues logged. No geometry
firehose, tint or shading changes. All hooks restored, normal exit classified;
no remaining game/controller or generated game-directory proxy observed.

All 18 raw files total **1,136,545 bytes**, retained ignored. Archive
`artifacts/m1/archives/M1-C01-RT-007-20261013-223631.zip`: **134,641 bytes**;
SHA256 `F8DF5EA688C1B03A2796731251C83B08EB3F767552005698125628C7CBCC21C0`.
Every archive entry was SHA256-checked against its raw source. Nothing deleted.
Evidence sources: summary, private-copy/wrapper/rejection/corner analysis JSON,
metadata, component log, run-result, cues and telemetry in that run directory.

Client SHA256 unchanged:
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`;
MD5 `2BE8F713F81B1C68D50EAD6088C32886`.
Runtime component SHA256
`13D1971C97A0823A9B52D827A3A845DBC5707AE769E2F3E49A2821466D811CA5`;
controller `D6ACC3F428B199B772DBAEE493CAF521DBDD1E83183DDE653E5B54F56063FF3D`.
Entry rebuild hashes supersede preparation-build hashes for this runtime.

Next: sponsor review, then separately authorize the smallest repeat-use/lifetime
proof. No enhancement or further implementation is authorized by this result.
