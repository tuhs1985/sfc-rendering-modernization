# M1-C01-OFFLINE-001 — bounded input qualification packet harness

Status: **executed offline 2026-10-11** after sponsor resumed with "start digging".
Five prepared tests passed; packet 49,473 bytes, still INPUT_QUALIFICATION_PENDING.
Earlier preparation was deliberately unexecuted; preserved in its run record.
No live probe/gameplay. See [shading analysis](../m1-c01-existing-shading-analysis.md).

## Question and scope

What exact instructions must be adjudicated to recover normals/positions,
coordinate space, orientation transform, source sharing and legacy lighting
in the known primary Model0 path? Assemble only those static windows and existing
owner evidence. Never infer a normal/matrix from float-looking bytes or names.
Output always says INPUT_QUALIFICATION_PENDING; it cannot qualify shading itself.

Tool: project Python harness `tools/m1_component/prepare_m1_c01_packet.py`, schema
`m1.c01.offline-input-packet.v1`, bundled Python 3.12.14. No new dependency/build.
Retained dumpbin disassembly provenance is in existing reconnaissance records;
its independently recorded hash is not proof of byte-for-byte PE correspondence.

Targets (inclusive VAs): ship handoff 004162B9..00416360; Model0
0042E4B2..0042E650; source init/preparation 006ABF80..006AC600. Known exception
00509843 and unrelated systems are excluded. No process APIs, injection, hook,
memory writes, gameplay, shader, source mutation or administrative privileges.

## Offline launch (resumption authorized and executed)

From repository root in ordinary PowerShell:

```powershell
& 'C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  tools/m1_component/prepare_m1_c01_packet.py `
  --client 'Game Assets/StarFleetOP.exe' `
  --disassembly artifacts/pre-m0/raw/StarFleetOP-2.5.6.4.dumpbin-disasm.txt `
  --events artifacts/m1/runs/20261010-172437-enabled/M1-A-events.csv `
  --output artifacts/m1/c01/20261011-input-packet.json
```

No UAC needed; inputs read-only. Optional --events can be omitted if local
historical CSV is absent (restore from verified archive later, do not silently
change provenance). Historical pointers are never used to access a live process.
Client must match frozen SHA-256. Output is new/exclusive and confined under
ignored artifacts/m1/c01; choose a new filename for another run.

## Gates, limits, output and cleanup

- Start: explicit offline CLI invocation, no tactical trigger.
- Stop: one streaming pass over bounded inputs; error on mismatched client,
  missing instruction windows, malformed CSV or exceeded limits.
- Disassembly input <=128 MiB (existing file 70,181,824 bytes), selected text
  <=1 MiB, lines <=8,192 characters. Instruction continuation lines retained.
- Optional CSV <=32 MiB / 50,000 rows, eight mainline owner epochs, bounded
  field/RGB sample cardinality. Packet <=2 MiB before write.
- Expected output: one JSON packet, normally well under 1 MiB; exact volume
  unmeasured until execution. No multi-GB trace mechanism.
- No persistent server, process, session or game-directory files; no rollback
  required. Preserve packet/hash in run record; archive useful output after
  analysis. Any deletion must target only the exact generated packet.
- Tests prepared: `python -m unittest tests.test_prepare_m1_c01_packet -v`.
  Five tests now passed. This is not runtime readiness or input qualification.

## Narrow static byte-correspondence supplement

`tools/m1_component/verify_m1_c01_shading_bytes.py`, project version in current
tree, Python 3.12.14, reads only the exact hash-verified client (input <=64 MiB).
Command: `python tools/m1_component/verify_m1_c01_shading_bytes.py 'Game Assets/StarFleetOP.exe'`.
Purpose: verify 15 explicitly listed source-lighting control/call/dot-helper
instruction prefixes against file-backed PE offsets. Exact VAs/bytes are in
its versioned ANCHORS table and curated analysis; not a patch list.
Explicit command start, single pass stop, stdout-only JSON normally <8 KiB,
no captures/process attachment/UAC/session/cleanup. Executed twice, all prefixes
matched. A byte match corroborates static instruction provenance, not live
shading semantics or future safe intervention. No broad disassembly generation.

## Analyst adjudication and limitations

Read selected field accesses/call relationships and corroborate against original
PE/static evidence; preserve exact VAs/offsets. Historical two-owner evidence
supplies context, not normal/transform values. Source RGB sample is not a full
distribution. Changed identity can reflect legitimate LOD; investigate rather
than auto-classify a defect. Any required live read-only probe needs a separate
defined field/ABI/capture packet before use; do not guess offsets or repurpose
the visual tint test to gather arbitrary memory. Reuse confirmed seam, keep
high-volume geometry hook disabled. C-02 still requires separate approval.
