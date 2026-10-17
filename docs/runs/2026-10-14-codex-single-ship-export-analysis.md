# Codex run — complete selected mesh export analysis

- Run ID/date: `2026-10-14-single-ship-export-analysis`, America/New_York.
  Sponsor "Go" to stated inspection/contract task; no implementation/gameplay.
  Active work: post-M1 integration research; closure acceptance remains pending,
  aggregate TRL unchanged. No M2 plan/implementation or renderer selection.
- Start: HEAD `fee152f`, 129 inherited pending Git paths, cached diff empty.
  Existing work left untouched. Fuel Guard attach verified recent trusted hook;
  direct access denied, quota health unknown; no sandbox daemon started.
  No root AGENTS.md exists; supplied global instruction applied.
- Read HANDOFF operating convention, current M1 plan disposition, readiness/
  enhancement gap assessments, M0 ownership map, field/transform qualification,
  isolated-list feasibility and RT-010 evidence. Read actual corner sampler,
  private/whole graph/source copies, component capture sites and byte verifier.
- Technical question: can the known seam supply one complete independently
  readable primary ship mesh, and what must be preserved versus qualified?

## Tools / material checks

- PowerShell Get-Content/rg, bundled Python, bundled Git, apply_patch. No external
  lookup required: this task adjudicates local evidence, not changing SDK facts.
- `PYTHONDONTWRITEBYTECODE=1`; existing
  `tools/recon/extract_disasm_ranges.py` on ignored
  `artifacts/pre-m0/raw/StarFleetOP-2.5.6.4.dumpbin-disasm.txt`, narrow ranges
  `006AC299:006AC310`, `0042E4B2:0042E640`, `006ABF80:006ABFC0`,
  `006AC010:006AC16C`, `0042FD3F:0042FDF0` (0x-prefixed arguments).
- Existing Python `verify(Path('Game Assets/StarFleetOP.exe'))` from
  `verify_m1_c01_shading_bytes`: 42 anchors PASS, exact SHA256 matched.
- Additional inline read-only Python PE32 section mapping: locate PE at DWORD
  offset 0x3C, image base at optional header +28, map each checked VA through
  section RVA/raw spans and compare bytes. Eight VA/byte pairs retained in the
  new contract; all PASS. No generated disassembly or executable writes.
- `Get-FileHash -Algorithm SHA256` on installed
  `C:\Games\Taldren Software Inc\Starfleet Command Orion Pirates\StarFleetOP.exe`.
  Reference and installed hash both
  `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.

## Adjudication

- CONFIRMED static: full position/primary list access, 36-byte source indexing,
  per-corner +10/+14 copying, selected child/source passage. Prior runtime proves
  whole 452-polygon graph intervention, not independent complete mesh export.
- Defined complete selected primary mesh, not all passes/LODs/whole physical ship.
  Candidate capture at existing owner-scoped wrapper avoids stale manager caches
  at Model0 entry. No ABI/hook change implemented or delegated.
- Preserve per-corner UV/vector splits, raw source records/transform payload and
  provenance. Source +14/+1C semantics remain UNKNOWN. Model-local interpretation
  remains STRONG HYPOTHESIS; no external world/camera convention inferred.
- Rejected: position-only welding, guessed texture pointers, blanket n-gon fan
  triangulation, treating pointer-bearing native copies as independent exports,
  repeated tint tests, broad material/engine archaeology and backend selection.
- Proposed bounded one-packet collection: 512 polygons/8 corners/65,536 positions,
  943,240-byte worst-case raw reservation, 1 MiB storage, 2 MiB packet-file cap,
  64 KiB summary; two attempts, <=90s, existing geometry hook off/log caps intact.
  Calculated limits only: no new runtime size behavior observed or probe armed.

## Files / validation / final state

- Added `docs/reconnaissance/2026-10-14-single-ship-export-contract.md`.
- Added this run record; prepended HANDOFF checkpoint, preserved prior history.
- Documentation validation: local Markdown links and bundled Git diff whitespace
  check PASS, including no-index whitespace checks on the two new documents.
  Line-ending conversion warnings only. All links in the three touched documents
  resolve. Final status: 131 pending paths, cached diff empty, HEAD `fee152f`.
  Source checks above PASS.
  No build needed: no code change. No new tests, raw capture, installation,
  game/config/requirements change, stage/commit or cleanup/deletion.
- No runtime tool/session launched; do not assume elevated parent or game state
  persists. Future capture must have its own definition and offline tests.
- Final Git: inherited dirty work plus two new docs and HANDOFF update, all
  unstaged/uncommitted at `fee152f`; no inherited changes cleaned or adjudicated.
- Exact next action: implement/offline-test the proposed read-only complete mesh
  packet collector/serializer/analyzer and probe definition before gameplay.
