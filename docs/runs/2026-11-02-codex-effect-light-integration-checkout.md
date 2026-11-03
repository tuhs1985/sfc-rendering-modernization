# Run278 — game-driven effect lights enabled; checkout prepared

## Delivered

Sponsor authorized the previously prepared transient-light connection. Enabled `[effects].enabled` in the existing lights.toml. All other parsed lighting values, including scene slots0/1 and project fill, match the accepted configuration. Materials, images, geometry capture, presentation/depth, ExtraFrame default and cleanup behavior are retained.

The existing semantic observation already captures the native light bank before scene publication. Its exact-frame/session/PID-qualified data feeds the existing pinned Remix `CreateLight`, `DrawLightInstance`, `DestroyLight` and `LightInfoSphereEXT` path. No new game hook, translator, shader, Toolkit process or weapon renderer. Supported native positional types1/5 in slots2–63 use game world position, RGB and gate/enable-prefix state. Inactive, unsupported, invalid or missing inputs remove transient lights without clearing the persistent scene lights. Unchanged handles are reused; motion/parameter changes replace the slot handle at the established renderer boundary.

Shape remains the explicit sphere approximation. Native range/falloff is recorded, not repurposed as light power or source radius. Brightness is provisional native RGB multiplied by the existing global and effect ratios. Faithful native type5 attenuation, weapon-family names and emitter shape require gameplay evidence. Native weapons/shields/explosions continue drawing normally; the addition illuminates Remix-rendered ships.

Official interface: [pinned NVIDIA public SDK0.6.5](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/public/include/remix/remix_c.h). Runtime remains1.6.1. No dependency upgrade or runtime-internal patch.

## Opt-in emission evidence

Added `-LightDiagnostics` to the existing launcher, forwarded on both PowerShell versions. Ordinary runs leave it off. The first integration checkout should enable it.

At the successful light draw-submission boundary, an enabled diagnostic records original64slot bank words/enables/gate, source frame/QPC, configuration generation and the actual converted position/radiance/radius/status passed to successful Remix calls. Fixed preallocated store, no file access/allocation/wait. It does not claim these lights reached final pixels or a presented SFC frame: join frame identity with the existing insertion records for that question.

New local-only store offset is native effect-source offset+64KiB (`16,187,392`),111,680bytes inside the existing current-user16MiB mapping. Sixteen seqlock cells, each6,976bytes with6,944byte payload. Existing source/config/geometry layouts and four-cell native source ring remain unchanged. Source session/gamePID and monotonic frame associations are checked; native32/64bit layouts agree.

A separate optional worker drains changed frames and emits only meaningful slot/state changes. It skips old cells before decoding, ignores changes in unused garbage words when deciding whether a record is needed, and retains full original slot words when an event is logged. No worker/files/payload copies are active when diagnostics are off. Ring overwrites never wait on SFC. Missing frame numbers are reported without claiming they necessarily represent recorder loss; frames not rendered may also be absent.

`effect-light-submissions.jsonl` is capped at4MiB; after saturation, aggregate counters continue and omission is explicit. Summary records observations, errors/unstable reads, active slots, omitted records and byte count. Diagnostic read/write failure is recorded separately; it does not disable valid effect rendering. The recorder drains after renderer/service stop and before releasing its mapping. No new safety shutdown or light refresh cap.

## Validation

-37native lifecycle/submission checks per architecture: exact bank/session/frame, on/off, motion, colour conversion, unsupported/invalid input, source prefix, SDK handle reuse and teardown, submitted raw/converted association, recorder disable. Native emitted trace bytes decode in Python for both architectures.
-104focused Python checks pass, including fixed-store actual-memory reader, source/session/malformed rejection, bounded output, unchanged-state suppression, diagnostic shutdown and existing asset/material/insertion/cleanup regressions. Lighting comparison confirms effects.enabled is the ONLY lighting-data change.
- Authoritative Strict `20261103-024041-572265-return-fixture`:600frames, diagnosticsOFF;585effect updates/292active observations/302handle changes, invalid0/unavailable0/remaining0. Optional recording is null. Median presentation interval16.858ms.
- Authoritative ExtraFrame `20261103-024157-959277-return-fixture`:600frames, diagnosticsON;601effect updates/300active observations/310changes, invalid0/unavailable0/remaining0. Recorder601frames,311,563bytes,0omitted/invalid/unstable/unobserved frames.300active events independently compared against native words and accepted configuration: positions exact, radiance error0, native range preserved and radius matches.20different synthetic positions; one fixture colour, not a spectrum/fade characterization. Median interval16.857ms,p9934.461ms includes existing deliberately injected deadline overruns; no clean stress-overhead conclusion from this fixture.
- Both tests: three owners/two unique+shared assets, colour/depth/text readbacks0mismatches, graphics-state errors0, no asset partial results, material retries0, normal exits and owned children remaining0. Fixture slow-deadline injections remain intentional.
- Final host SHA256 `DCCE358A2AAE81E16C55B3463496CE2BC74EFF2D0209A9DEFAE4862DD36025FD`. Cohort qualification refreshed from both tests. Existing native-light observer qualifier detected only the supervisor argument-source change; native observer binary/source unchanged. Reran its actual queue/worker/decoder qualification. Normal and LightDiagnostics read-only gameplay preflights PASS.
- Prototype ExtraFrame `023755` also passed but predates final recorder polling optimization; do not use it as the authoritative final source receipt. No SFC launched. No changes to Defender, source assets or original client binaries. Whitespace/parser checks pass. No stage/commit.

Compact evidence and trace comparison: `artifacts/player-replacement/run278/summary.json` and `trace-comparison.json`.

## Sponsor checkout

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\native_insertion\start_native_multiship_session.ps1" -LightDiagnostics
```

Use a familiar skirmish. Fire weapons, take impacts, launch fighters if useful, and change camera angles. Look for flashes/coloured illumination moving with effects and disappearing afterward, while replacement, shields, HUD and controls stay normal. Existing90second tactical window, normal exit and cleanup. No manual timestamps, on/off cycle or extra CompletionDiagnostics requirement. User can exit early normally.

Common brightness, colour and emitter radius plus per-slot overrides are already in lights.toml. A slot is not a permanent weapon identity; reuse during a mission is expected. Current normal sessions freeze configuration; tune between checkouts or through the existing tuning workflow. Gameplay visibility, practical strength/radius, all manager banks and weapon-specific mappings remain unqualified until the run. Alpha weapon-lighting acceptance is not claimed solely from synthetic checks.
