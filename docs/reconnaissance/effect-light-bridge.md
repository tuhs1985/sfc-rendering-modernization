# Game-driven transient lights — Run261

## Source and meaning

Reuse the first qualified semantic wrapper of each native scene frame, immediately before persistent scene publication wakes the renderer. Read the confirmed manager light bank at+0x778, enable bytes at+0x1778 and global response gate at+0x1EB8. Double-copy into preallocated scratch and reject inconsistent reads. The game supplies all64records; slot0/1 remain on the accepted scene-light path. No new hook, setter detour, game-memory write, file read, allocation, wait or per-frame SDK call is added to SFC.

The new branch supports native positional types1and5 in slots2..63. Type5 is **not** DirectX type5 or a cylinder. Unused direction/tail fields can contain uninitialized bit patterns, so validate only the position, contribution RGB and positive range actually used by these native branches. Unsupported types remain off in this adapter.

World position is record+0x10 float3; RGB is+0x1C float3. Native+0x28 is range/falloff, **not** a universal power value. In nine retained active type5 samples, transforming this original world position with the established inverse supplied transform reproduces SFC's stored local point within4.166e-7native units. Evidence:`artifacts/player-replacement/run261/native-position-check.json`. This verifies coordinates against actual game data; it does not prove physical intensity/shape equivalence.

Transient activation obeys both the native global gate and contiguous enabled prefix: the first disabled slot terminates the native response. Explicit configuration OFF also wins. Do not retain weapon lights using the scene slots' always-on policy. No light is fabricated for a weapon/effect that does not appear in the bank.

## Transport and timing

Use the existing current-user/session-owned16MiB mapping. Source store starts at15MiB+384KiB:16960bytes comprising a64byte header and four4224byte seqlock cells. Each cell carries one4184byte raw frame: source frame, manager/thread provenance, captured QPC,64original records and64enable bytes. Capture once per native scene frame, without the historical5Hz discovery throttle or two-owner sampling restriction. Existing low-rate scene-light discovery remains independent.

Remix configuration store starts32KiB after the new source store:1600bytes, including a checked1512byte payload for62slot policies. Both additions total18560bytes; existing layouts/offsets and mapping size remain unchanged. Initialization/prefault precedes hooks; the supervisor enables observation after publishing validated configuration. This is fixed-capacity latest-state transport, not a queue that delays the game.

The64-bit renderer requires exact source-frame, session and game PID matching plus a stable cell read. Missing, overwritten, disabled, malformed or stopped input removes the affected transient contributions; it does not stop geometry or alter the persistent scene lights. Raw process-local addresses are evidence only, never dereferenced by the64-bit renderer. No stale observation time is refreshed, and no arbitrary light refresh cap or prediction is introduced.

## Remix adapter and configuration

Use the existing pinned public Remix C API: `CreateLight`, `DrawLightInstance`, `DestroyLight` and `LightInfoSphereEXT`. Official source:[pinned NVIDIA remix_c.h](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/public/include/remix/remix_c.h). Actual runtime remains1.6.1/SDK0.6.5; no Toolkit process, new translator or custom light shader.

Each active slot uses a **sphere proxy** at the native world position. Radiance is native contribution RGB times existing conversion_scale/master_multiplier and the effect intensity/colour multipliers. This is provisional unit conversion. Native range is retained and checked but is not multiplied into power or misused as the emitter radius. Remix's spherical falloff, shadows and specularity differ from SFC's type5 special normal/up-vector response. There is no recovered physical source radius, spot cone, exact native attenuation cutoff or independent universal intensity field here. Do not claim faithful SFC brightness or shape.

Controls are appended to the existing `tools/remix_runtime/config/lights.toml`:

```toml
[effects]
enabled = true
intensity_multiplier = 1.0
color_multiplier = [1.0, 1.0, 1.0]
radius = 2.0

# Optional per-slot override;native OFF and effects.enabled=false still win.
[[effect_lights]]
slot = 2
intensity_multiplier = 1.0
radius = 1.0
```

Radius is the Remix emitter size in existing native world units, not game range. Old configuration without an effects table leaves this addition off. Individual slot overrides2..63 inherit the common values. Native state controls activation regardless of appearance overrides. Normal sessions freeze settings; existing tuning mode reloads the same file and publishes the new checked configuration. Scene light/project fill definitions and material/image controls remain independent and unchanged.

Create/destroy API calls remain on the host render thread at the existing completed-output boundary. Reuse unchanged handles, recreate changing parameters, draw once per scene and retire inactive instances. Existing GPU/resource ownership and shutdown handling remain in force. Log only aggregate frame/active/invalid/unavailable/change/remaining counts at close; no light-image dumps or per-frame light file output.

## Checkout boundary

**Run278 update:** the connection is now enabled for sponsor checkout. Optional `-LightDiagnostics` uses a fixed111,680byte,16cell submission store at source offset+64KiB, within the existing mapping. It records successful Remix draw-submission parameters joined to the original bank/frame/configuration generation; a worker saves meaningful changes up to4MiB and reports gaps/omissions. No new SFC hook or render-thread IO; ordinary runs create no recorder. This supersedes the recorder-pending wording below. See the [current checkout and final tests](../runs/2026-11-02-codex-effect-light-integration-checkout.md). Runtime pixel inclusion and weapon-family attribution still require evidence; API submission alone is not a final-image receipt.

Sponsor follow-up: include targeted **light-emission characterization** in the integration checkout. Before that run, prepare an opt-in, bounded recorder using the existing source/host connection; the current launcher records aggregate counts, not the per-light data needed for this analysis. This is planned work, not an already enabled capture.

Retain native slot/type and all original record words, global gate/enable-prefix state, world position, contribution RGB and range/falloff over activation, movement, fading and deactivation. Join these to source frame/QPC and the actual Remix position/radiance/radius and configuration revision. Correlate weapon launches/impacts/explosions using existing event evidence where available; keep unknown associations explicit. Compare near/far illumination on ships to distinguish source colour, brightness conversion and spatial falloff. Do not infer emitter shape or independent power from an unnamed field, or confuse material emissive maps with these bank lights.

Prefer state-change records and short bounded full-rate bursts so short flashes are represented. Worker-side evidence output only, within existing logging/storage limits; no render-thread files, new broad hooks, continuous image dumps or sponsor timestamps. Keep this diagnostic recorder off in ordinary performance mode. Prepare it before asking for the integration run, then use the results to decide which additional emission/shape relationships need investigation.

Prepared for the current native multi-ship replacement launcher. Fire weapons, let impacts occur and switch cameras normally. Check that flashes illuminate replacement ships at the right positions and disappear with their effects. Brightness/radius can then be tuned. Exact weapon-family identification, effects that never register native lights, multiple unconfirmed manager banks and faithful native type5 attenuation remain unqualified. Synthetic API/GPU checks are not sponsor gameplay acceptance.

Current tentative effect radius is2.0 (Run281). Sponsor saw weapon illumination; slowed photon firing supported projectile-associated lighting. Exact weapon ownership and physical conversion remain unqualified. Historical first-checkout invisibility is superseded.
