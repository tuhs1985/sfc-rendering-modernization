# Codex Run Record — CODEX-20260904-M0-001

## Run identity

- **Date:** 2026-09-04 (America/New_York)
- **Active milestone:** M0 / TRL 3 Critical Function Proof
- **Task:** Identify and dynamically exercise a useful internal rendering
  boundary in Starfleet Command: Orion Pirates 2.5.6.4.
- **Final result:** PARTIAL

## Technical question and hypothesis

The run tested whether the exact client contains a stable rendering seam
upstream of the translated graphics stream, where scene, object, model, or
material meaning remains available. The working hypothesis was:

```text
engine scene ownership
  -> internal graphics manager / geometry submission
  -> batch flush
  -> native D3D3 draw
  -> DirectDraw presentation
```

The critical follow-up question was whether model, material, or ship identity
survives through the internal geometry-submission entry.

## Starting baseline

- Pre-M0 reconnaissance was complete and was not repeated.
- The exact supported client was StarFleetOP.exe 2.5.6.4:
  - MD5 `2BE8F713F81B1C68D50EAD6088C32886`
  - SHA-256 `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`
- Existing evidence already established DirectDraw/D3D7-era rendering,
  downstream D3D9 translation, indexed mesh drawing, and discrete textures.
- Existing maps identified graphics-manager, wrapper, model, material, camera,
  sprite, and z-buffer candidates, but no rendering function had been
  dynamically correlated from the engine manager to native drawing.
- No M0 runtime probe, renderer hook, or architecture selection existed.

## Tools, scripts, and configuration

| Tool or configuration | Use |
|---|---|
| Exact-build dumpbin disassembly | Static address, call-site, GUID, and COM-vtable reconstruction |
| `rg` and PowerShell | Bounded searches, evidence extraction, process checks, hashes, and validation |
| `tools/m0_probe/m0_probe.cpp` v0.2 | External x86 Windows debugger using temporary exact-address `INT3` probes |
| `tools/m0_probe/build_probe.ps1` | x86 static-runtime build with Visual Studio 2026 18.7.3 |
| `tools/m0_probe/run_probe.ps1` | Wait for launcher-created client, validate target, request UAC elevation, and bound capture |
| `tools/m0_probe/analyze_probe_log.py` | Generate JSON and Markdown evidence summaries; Python 3.14.6 |
| SFCLauncher 2.1.0.22 | Launch the sponsor-confirmed working game configuration |
| Probe runbook | `docs/m0/probes/m0-probe-capture-runbook.md` |
| Probe definition | `docs/m0/probes/M0-RT-001.md` |

The runtime probe used only the nine exact addresses and per-point limits
defined in the probe runbook. No broad instruction trace, API trace, memory
dump, or unbounded capture was used.

## Material commands and parameters

```powershell
.\tools\m0_probe\build_probe.ps1
.\artifacts\pre-m0\bin\m0_probe.exe --help

.\tools\m0_probe\run_probe.ps1 -MaxSeconds 600 -WaitForClientSeconds 600

# Successful elevated scene/draw correlation:
m0_probe.exe --pid 9064 --log <run-20260904-100033> --max-seconds 600

# Successful launcher-aware geometry-boundary correlation:
.\tools\m0_probe\run_probe.ps1 -MaxSeconds 300 -WaitForClientSeconds 600 -ElevateProbe

python .\tools\m0_probe\analyze_probe_log.py <M0-RT-001.csv>
```

Static work used exact-address searches around `0x0069E300`,
`0x0069E3D0`, `0x0069EB90`, `0x006A84B0`, `0x006AB380`,
`0x006AB3C0`, `0x006AB410`, and their dynamically observed callers.

## Files created or modified

Versionable files created or modified:

- `tools/m0_probe/m0_probe.cpp`
- `tools/m0_probe/build_probe.ps1`
- `tools/m0_probe/run_probe.ps1`
- `tools/m0_probe/analyze_probe_log.py`
- `docs/m0/probes/M0-RT-001.md`
- `docs/m0/probes/m0-probe-capture-runbook.md`
- `docs/m0/m0-trl3-critical-function-proof.md`
- this run record

Generated and ignored local outputs:

- `artifacts/pre-m0/bin/m0_probe.exe`
- `artifacts/pre-m0/runs/20260904-094709/`
- `artifacts/pre-m0/runs/20260904-095959/`
- `artifacts/pre-m0/runs/20260904-100033/`
- `artifacts/pre-m0/runs/20260904-100901/`
- `artifacts/pre-m0/runtime-native-windowed/`

Reference originals were not intentionally edited. The approved client hashes
were rechecked after testing and remained unchanged.

## Evidence generated

### Static evidence

- Reconstructed wrapper ownership:
  - `+0x30` primary Surface4
  - `+0x34` back-buffer Surface4
  - `+0x38` active render target
  - `+0x3C` z-buffer Surface4
  - `+0x40` IDirect3DDevice3
  - `+0x44` IDirect3DViewport3
  - `+0x48` IDirectDraw4
  - `+0x4C` IDirect3D3
- Corrected `0x006A8500`: it is a FlipToGDISurface path, not BeginScene.
- Identified engine scene begin/end, manager present, wrapper present, batch
  flush, native indexed-draw call site, and geometry accumulation.
- Identified geometry-submission callers at `0x006AC503`,
  `0x006AC520`, and `0x006AC8EB`.

### Runtime evidence

Run `20260904-100033`:

- 18,017 samples over 51.766 seconds;
- 4,000 each of scene begin/end, engine present, and surface present;
- 1,000 batch flushes and 1,000 indexed-draw call-site hits;
- 17 model-parser hits;
- same Device3 pointer `0x127E8B38` at scene and indexed draw;
- raw CSV size 3,949,618 bytes;
- normal process exit.

Run `20260904-100901`:

- 16,276 samples over 40.094 seconds;
- 1,500 geometry submissions;
- 1,000 batch flushes and 1,000 indexed-draw call-site hits;
- stable manager `0x04980038`, Device3 `0x127E7F70`, and batch
  `0x04981F84`;
- geometry callers: `0x006AC503` (1,238), `0x006AC520` (258), and
  `0x006AC8EB` (4);
- four captured arguments were generic polygon count/selector/flag values,
  not ship, model, or material pointers;
- raw CSV size 3,569,537 bytes;
- normal process exit.

Negative and operational evidence:

- Direct native launch reached window creation but failed during Device3 setup
  at `0x0069D782`.
- A non-elevated attachment to the launcher-created client correctly failed
  with `attach_error=5`; the documented runner now requests UAC elevation.
- The sponsor exercised tactical rendering and normal control while probes were
  active; the client remained responsive.
- All capture output was bounded by exact filters, duration, and hit
  saturation. Multi-GB output risk and safe operation are documented in the
  probe runbook.

## Result and confidence

| Conclusion | Confidence |
|---|---|
| Stable engine scene-to-present path exists | CONFIRMED |
| Manager batch flush reaches native Device3 indexed drawing | CONFIRMED |
| `0x006AB410` is a stable internal generic geometry boundary | CONFIRMED |
| Interception can observe the pathway without destroying tactical control | CONFIRMED |
| Ship/model/material identity crosses `0x006AB410` | REJECTED for captured arguments |
| `0x006AB410` alone is a useful modernization seam | NOT DEMONSTRATED |
| A higher semantic owner remains identifiable | STRONG HYPOTHESIS |

The M0 gate result is PARTIAL because the dynamically proven boundary is
already below the loss of the semantics needed by the intended modernization.
The full adjudication is in
`docs/m0/m0-trl3-critical-function-proof.md`.

## Unresolved blockers

1. No known ship/model instance has been correlated to a finite set of polygon
   submissions or draw calls.
2. The higher function where model/material/LOD identity collapses into generic
   manager state remains unidentified.
3. Tactical ships, sprites/effects, and UI have not been separated above the
   common geometry boundary.
4. World/view/projection and lighting ownership relative to the higher
   render-object owner remains unconfirmed.

Before M1 planning, the project needs a qualitatively different targeted
technique: semantic tag propagation or call-stack/data-flow correlation from a
known ship/model render invocation into the three proven polygon callers.

## Repository state at run completion

- No files were staged.
- No commit was created.
- Sponsor review remains required before any commit.
- `git status --short` reported the workspace content as untracked:

```text
?? .gitignore
?? README.md
?? artifacts/
?? docs/
?? src/
?? tests/
?? tools/
```

Generated binaries, raw logs, and runtime copies remain ignored by repository
policy even though the top-level `artifacts/` directory is shown because it
contains its versionable policy/readme material.
