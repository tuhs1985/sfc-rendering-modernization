# Prepared Remix environment — startup contract v1

Run270 prepares the actual configured project dome through Remix's existing supported API and retains it for validated live adoption. Canonical geometry, UVs, original images, SFC hooks and native light observations remain unchanged.

## Bootstrap

The supervisor initializes the existing startup ticket, validates current lighting controls, builds the existing shape packet and caches its environment images before launching the renderer. It publishes immutable metadata into the existing current-user-only16MiB scene mapping:

| Region | Offset / size |
| --- | --- |
| Existing startup ticket |4096 /256bytes, unchanged |
| Prepared environment store |8192 /1920bytes |
| Existing calibration mailbox |32768, unchanged |
| Asset payload start |65536, unchanged |

The1912-byte packet contains magic/version/size, game PID, session words, producer PID, project-dome flag, config SHA256, bounded UTF-16 cache directory, the unchanged808-byte shape packet and FNV64 checksum. An aligned ready word is written last. Publication cannot be reused. Native validation checks it against the existing startup ticket, validates both checksums/shape data/path padding/flag agreement, and checks producer/game liveness.

There is no new mapping, callback or dependency on ship asset SHA/game-side attachment. `M1StartW` retains its disk `LiveChannel` bootstrap before attachment. Configured resources are not presented as captured native state.

## Preparation and ownership

Before private renderer warm-up/startup readiness, create the configured **project_fill dome** with the existing `CreateLight` adapter and drain the existing GPU query. Keep the unchanged five-second completion guard and check stop/producer/game liveness during this external-host wait. Do not invent early native scene-light values.

Transfer the handle once into the live light cache as pending, not visible. Missing/invalid observations leave it passive. A validated live packet with identical project row/positioned shape adopts the same handle, avoiding light recreation and its image open. Changed/disabled settings retire pending preparation and follow existing live configuration behavior. Cleanup retires pending/adopted resources once; the preparation object owns any handle not transferred. No output resource is reused before GPU completion.

This is a Remix-specific conversion/resource concern. Native scene slots0/1 retain existing processing. A non-dome project light explicitly prepares no project dome. Other/native dome configurations, custom HDR environments and device-loss recovery are not separately qualified by Run270.

## Image cache

`artifacts/d3d9-proof/environment-cache/` stores the exact existing content-named DDS bytes, counted by the existing aggregate evidence inventory. It retains128MiB/256resource bounds, rejects links/corrupt content, atomically publishes new files and never overwrites a resident image. Checks happen during external preparation, not SFC callbacks/per-frame geometry. Existing per-run evidence remains.

The Remix light adapter uses the validated cache directory; a later uncached image uses the existing per-run path. No changes to gamma, image interpretation, lighting strength, materials or Defender settings. Removing this first-live dependency is not a guarantee that every protected operation will be fast.

## Hull admission

Physical first-hit depth/coverage now preallocates `scene_capacity::Owners` submissions, currently256, matching the admitted scene budget rather than imposing a separate32-entry limit. This is an integration memory budget, not an SFC gameplay limit or256-complex-ship FPS claim.

Admit coverage **before** ordinary D3D9 colour and rendered-owner authorization. Overflow/missing coverage omits only that replacement; no unmatched colour/coverage/member receipt is issued. Other owners continue; admission resets next frame. No per-frame allocation or fatal capacity exception remains in this helper. Summary counters record omissions.

## Qualification

Run270 covers x86/x64 packet checks, actual shared-memory bootstrap/cancel/ownership with a mock API, live cache adoption/mismatch/cleanup, and GPU depth/identity pixels for256 independently positioned owners sharing one mesh. Strict and ExtraFrame real native-insertion fixtures complete600frames with colour/depth/text checks and cleanup, including60-second delayed activation. The qualifier requires preparation/adoption evidence and full-capacity GPU test results.

The separate material-publication WinError5/five-second fatal policy remains unchanged and open. See [Run270](../runs/2026-11-02-codex-prepared-dome-and-hull-capacity.md).
