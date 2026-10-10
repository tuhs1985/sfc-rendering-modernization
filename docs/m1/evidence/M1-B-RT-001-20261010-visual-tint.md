# M1-B-RT-001 — runtime visual-control evidence

## Result — 2026-10-10

**M1 CONTINUES — bounded reversible visual-control proof demonstrated.**
Semantic integration sub-gate remains PASS; formal TRL 4 remains incomplete.
This is not a renderer choice or comprehensive visual-equivalence proof.

**CONFIRMED:** target-owner instrumentation plus sponsor observation establish
an intentional reversible visible intervention via the semantic component.
Sponsor: "the klingon enemy ship was magenta, then the color returned to
normal"; "everything seemed functional". No screenshot/video captured.
Klingon is sponsor identification, not decoded model classification. Sponsor
did not separately attest every other surface unchanged; logs establish owner
2 was not selected for tint. Do not silently promote that narrower evidence.

## Configuration and exact evidence

[Runbook](../probes/M1-B-RT-001.md); component 0.3, two-ship skirmish, automatic
ship-render gate, five-second delay / ten-second effect; copied source RGB only.
Geometry hook disabled. Bounds: 60 active seconds, 3,000 detailed scene epochs,
50,000 events, eight owners, 16/32 MiB warning/hard cap, 600-second gate wait.
Windows PowerShell entry re-executed in bundled PowerShell 7 after compatibility
correction; inherited sponsor's elevated parent, no new UAC request by tooling.

Run folder: `artifacts/m1/runs/20261010-172437-enabled`; PID 32896.
Start `2026-10-10T17:24:37.5490454-04:00`, normal exit completed
`2026-10-10T17:25:36.1115824-04:00`.
3,000 detailed scene epochs spanning 25.343 seconds; these are instrumentation
epochs, not independently measured displayed frames. Stop trigger `detail_bound`.

| Owner | Ship | Visual | Model0 | Original source |
| --- | --- | --- | --- | --- |
| 1, tint target | `0x1D3FF0B8` | `0x1D3FDC88` | `0x1FE5C590` | `0x0493365C` |
| 2, untinted | `0x1FF17FF0` | `0x1FF10620` | `0x1FE5C20C` | `0x1D277598` |

Target thread 33472; 589 before-window original-source Model0 events,
1,179 substitutions, 1,232 after-window original-source events. All 1,179
restored; zero rejected tint/semantics, thread mismatches, restoration failures,
renderer replacements, owner/thread overflows or active tint scopes at stop.
Original sampled RGB `0x00FFFFFF`, copied RGB magenta. Both owner chains coherent.
Tint analyzer `TARGETED_TINT_INSTRUMENTATION_COHERENT`, no review reasons.

General M1-A analyzer remains `PARTIAL_OR_REVIEW_REQUIRED`: its integration
decision requires downstream geometry evidence, deliberately absent here.
No new direct `0x006AB410`/DIP correlation is claimed. Prior confirmed path
and static color-copy relationships support this bounded interpretation.
Known `0x00509843` exception count 3,004, outside tint targeting. No retirement
or reappearance event; no new lifetime or performance claim.

## Safety, cleanup and artifact handling

- CSV 29,989 rows, 8,717,242 bytes (8.31 MiB), untruncated, below warning cap.
- Component/controller confirm hook restoration. Zero active tint scopes.
  Controller says `component_state=removed`: hooks removed/restored; not a
  claim that DLL buffers were unmapped before normal process exit.
- `run-result.json`: normal exit `exited`, `client_unchanged=true`.
  Before/after MD5 `2BE8F713F81B1C68D50EAD6088C32886`; SHA-256 independently
  rechecked on installed and reference client:
  `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
- DLL SHA-256: `5D5398D723561C45522F1987B99AAEEA5F20EEC81F6220C47AD5B929E1D764A3`.
- CSV SHA-256: `41D6CE29790A23ED92EA44BFCA9A07E58DC996294EBE0B59B61D478982AD2F92`.
- Verified compressed archive:
  `artifacts/m1/archives/M1-B-RT-001-20261010-172437.zip`, 210,587 bytes,
  13 entries; archived CSV hash matches raw. ZIP SHA-256:
  `1B6460209AC33C2AE6FFF4D995FB56441805FC9D69945C50451A6DAA7F876443`.
  Small raw capture retained alongside archive, both ignored/local; no deletion.

Sources: metadata, component summary/log, CSV, both analyzers, controller
stdout/stderr, process telemetry, run result and sponsor observations above.
This curated record preserves key findings when ignored raw files are absent.
Remaining: comprehensive other-surface verification, repeat fixture, formal
performance, retirement/reappearance, remaining CTE/three-VMES evidence.
Next action: sponsor review of this evidence and uncommitted tooling before
authorizing a commit or next increment.
