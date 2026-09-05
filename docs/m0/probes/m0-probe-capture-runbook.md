# M0 Probe and Capture Runbook

## Configuration identity

This runbook controls the shared M0 probe implementation and profiles
M0-RT-001, M0-RT-002, and M0-RT-003. The profile-specific definitions contain
their runtime question, exact addresses, caps, and expected outputs; this file
records the common build, launch, safety, analysis, and cleanup behavior.

| Item | Version or identity |
|---|---|
| Probe source | `tools/m0_probe/m0_probe.cpp`, current M0 probe version 0.4 |
| Executed semantic-probe binary | SHA-256 `AB1E590C3256C0C19875EF4527888D56CE48F790E30235E2F60511BA805135AC` |
| Post-run validated v0.4 build | SHA-256 `41ECA78CFA561981E90EB9B6B0A137EC2EA48C531C6F233B3CF4325BAC407946`; rebuilt and smoke-tested after analysis |
| Executed geometry-probe binary | SHA-256 `1B4FC1859A22EB9395EA1E3FE45D7718C4C81D86A5FA756B302EA405FBECDAD8` |
| Post-run hardened v0.2 build | SHA-256 `ECDB7CE80CEC328082E344E9D1C0D04E6550872B8D8B95A27AA0C617EF6E164E`; adds logged version identity and elevated-wait fix without changing capture fields |
| Probe purpose | Profile-selected exact-address correlation from semantic ship/model/mesh ownership through manager geometry, native D3D3 indexed drawing, and presentation |
| Probe build | `tools/m0_probe/build_probe.ps1`; Microsoft Visual Studio 2026 18.7.3 x86 toolchain; static runtime |
| Probe runner | `tools/m0_probe/run_probe.ps1` |
| Evidence analyzer | `tools/m0_probe/analyze_probe_log.py`; tested with Python 3.14.6 |
| Game launcher | SFCLauncher 2.1.0.22; sponsor selects the already-working configuration |
| Supported client | StarFleetOP.exe 2.5.6.4; MD5 `2BE8F713F81B1C68D50EAD6088C32886`; SHA-256 `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29` |

The probe uses the Windows debugging API and temporary one-byte `INT3`
breakpoints in the running process. It validates the live image MD5 and every
original target byte before arming. It never writes the executable or assets.

## Runtime question

The capture tests whether a stable internal path exists from engine scene
ownership through a geometry-submission entry, batch flush, native
`IDirect3DDevice3::DrawIndexedPrimitive`, and surface presentation. It also
tests whether model, material, or object identity remains in the four arguments
crossing the geometry-submission entry.

## Exact filters and limits

Profiles and governing definitions:

| Profile | Purpose | Maximum samples | Duration | Definition |
|---|---|---:|---:|---|
| M0-RT-001 | scene/batch/draw/present | 22,000 | 300 seconds default | [M0-RT-001.md](M0-RT-001.md) |
| M0-RT-002 | mesh/source owner | 5,212 | 180 seconds | [M0-RT-002.md](M0-RT-002.md) |
| M0-RT-003 | ship/model/mesh correlation | 6,364 | 120 seconds | [M0-RT-003.md](M0-RT-003.md) |

Only the following exact-build addresses are sampled by M0-RT-001:

| Event | Address | Maximum hits |
|---|---:|---:|
| ship_model_init | `0x0041C271` | 2,000 |
| model_parse | `0x0042FEF9` | 500 |
| scene_begin | `0x0069E300` | 4,000 |
| scene_end | `0x0069E3D0` | 4,000 |
| engine_present | `0x0069EB90` | 4,000 |
| surface_present | `0x006A84B0` | 4,000 |
| batch_flush | `0x006AB380` | 1,000 |
| draw_indexed_call | `0x006AB3C0` | 1,000 |
| geometry_submit | `0x006AB410` | 1,500 |

Each point disarms independently at its maximum. Approved duration is 300
seconds by default and never more than 900 seconds. No broad API trace, memory
dump, instruction trace, or unrelated function sampling is enabled.

## Privilege and UAC policy

Routine probe execution uses a narrowly scoped, already-elevated PowerShell
parent session. The analyst or test preparer opens that session before sponsor
gameplay begins; the runner and native probe then inherit its privilege and do
not issue a per-run `runas` request. Keep the elevated session limited to this
workspace and close it when testing ends.

The runner verifies that its parent is elevated and stops before launch when it
is not. `-ElevateProbe` is retained only as an explicit fallback for recovery
or historical reproduction and may display UAC. Do not use it for routine
sponsor-assisted runs. Do not disable UAC, alter global consent policy, create a
broad auto-elevation rule, or grant persistent administrative rights.

## Build and launch

1. Build and smoke-test:

   ```powershell
   .\tools\m0_probe\build_probe.ps1
   .\artifacts\pre-m0\bin\m0_probe.exe --help
   ```

2. Before sponsor involvement, the analyst opens PowerShell as Administrator,
   changes to the workspace, builds/smoke-tests the probe, and starts the
   watcher without `-ElevateProbe`:

   ```powershell
   Set-Location -LiteralPath 'C:\Project\SFC-Modernize Engine'
   .\tools\m0_probe\run_probe.ps1 -ProbeProfile m0-rt-001 -MaxSeconds 300 -WaitForClientSeconds 600
   ```

3. Open SFCLauncher 2.1.0.22 manually and use the same configuration already
   demonstrated to reach gameplay. The runner does not choose or alter the
   renderer configuration.
4. Enter one tactical battle and exercise one camera or ship control.
5. Exit the game normally once the geometry points saturate or the requested
   event is complete.

The runner may also target one unambiguous existing process with
`-TargetPid <pid>`. More than one matching process is a hard stop.

## Start and stop conditions

Capture starts only after the launcher creates one `StarFleetOP.exe`, its
exact MD5 is accepted, the image base is known, and all expected bytes validate.
The preferred stop is normal game exit. The probe also restores every still
armed byte and detaches at the configured timeout.

Do not terminate the probe while the game is still running: forcibly killing a
debugger can leave temporary breakpoints in that process. For emergency
cleanup, close the game first; process exit discards every in-memory change.
There is no persistent client cleanup because no client file is modified.

## Outputs and volume controls

Each run writes ignored, generated evidence beneath:

```text
artifacts/pre-m0/runs/YYYYMMDD-HHMMSS/
  M0-RT-001.csv
  M0-RT-001-summary.json
  M0-RT-001-evidence.md
  loaded-modules.csv
```

The raw CSV contains one row per accepted breakpoint hit plus bounded metadata.
The nine configured caps permit at most 22,000 samples, so expected raw output
is below approximately 6 MB. Observed files were:

- run `20260904-100033`: 3,949,618 bytes, 18,017 samples;
- run `20260904-100901`: 3,569,537 bytes, 16,276 samples.
- M0-RT-002 run `20260904-103417`: 1,155,344 bytes, 5,212 samples;
- M0-RT-003 run `20260904-104217`: 1,412,572 bytes, 6,364 samples.

The continuation profiles use a 2 MB operating safeguard and expected volumes
below 1.5 MB and 1.6 MB respectively. A new profile must document its total hit
cap, duration, expected volume, and file-size stop before it is used.

Per-frame and per-polygon probes can produce multi-GB output rapidly if hit
caps are removed or an unbounded instruction/API trace is substituted. That is
not an approved configuration. Safe operation requires retaining per-point
saturation, a duration limit, exact address filters, and one tactical
reproduction per run. Check file growth during any future filter change and
stop the game if projected output exceeds the documented bound.

Generated bulk files remain ignored. Preserve the versioned probe definition,
scripts, runbook, adjudicated counts, hashes, and report. A raw run directory
may be removed only after sponsor review confirms that its adjudicated evidence
is sufficient.

## Evidence mapping

| Runtime question | Evidence fields |
|---|---|
| Stable frame order | sequence number and event names for scene_begin, scene_end, engine_present, surface_present |
| Same device across scene and draw | manager `+0x7F64` in scene events versus the Device3 argument at `0x006AB3C0` |
| Stable batch owner | geometry manager `ECX`, batch at manager `+0x1F4C`, and batch-flush `ECX` |
| Geometry boundary callers | `return_or_stack0` at `0x006AB410` |
| Semantics crossing geometry boundary | `data1..data4` at `0x006AB410` |
| Geometry submitted downstream | vertex/index pointers and counts at `0x006AB3C0` |
| Model-load timing | model_parse event sequence and elapsed time relative to first geometry event |
| Safe interception | process responsiveness during capture, normal process exit, stop_reason, and restored/disarmed point counts |

## Known operational caveats

The first launcher-aware attempt attached without elevation and logged
`attach_error=5` (access denied), with zero samples. This is a documented
negative control. The original elevated runner then used `Wait-Process`,
which could not wait on the elevated child from the lower-integrity shell even
though capture succeeded. Version 0.2 polls process existence instead; this
does not change capture behavior or evidence.
