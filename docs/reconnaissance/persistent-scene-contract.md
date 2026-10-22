# Persistent simulation scene — initial D3D9 path

2026-10-21; Run103. Implementation authority: sponsor's persistent,
simulation-driven scene-management request. This is an opt-in implementation,
not a requirements amendment, replacement gate PASS or aggregate TRL claim.

## State and ownership

`tools/scene_bridge/persistent_scene.h` owns a fixed 32-entry, renderer-neutral
registry. Each entry retains the session-local owner epoch, ship/visual/model
identity, source/list/count, LOD, asset revision, display generation, last visible
frame and current simulation-derived world transform. Visibility does not retire
a living entry. Original captured geometry and the resident backend asset are
reused; camera return does not itself recapture or rebind them.

The initial displayed instance is the existing FCA player-fixture selection.
Selection is by qualified model name, NOT a proven native player flag. Other
qualified semantic ships can be registered and updated through the same code;
the current backend still displays one resident asset. Multi-object display,
arbitrary object types, in-place deformation and arbitrary enemy coverage are
not established by this increment. No saved OBJ is consumed by this path.

## Pose source and evidence

CONFIRMED runtime starting evidence: Run101 recorded changing base positions
inside three camera-away/render-observation gaps (24, 28 and 94 changes), with
ship-local cache updates. Do not repeat discovery or interpret additional
translation alone as total position.

Static support: ship getter `0x00419DD2` calls base getter `0x00413B34`, which
uses float translation at ship `+0x34/+0x38/+0x3C` and native angle words. Native
getter arithmetic is reproduced, NOT invoked remotely, and render cache
`+0x9C4` is not the live source:

```text
T(base) * Rx(2048) * Ry(word+90) * Rz(word+94) * Rx(word+92)
        * Rz(word+92E) * Rx(word+92A) * native_matrix(+980)
then add float translation (+E6,+EA,+EE).
```

Native turn period is 8192; native cosine/sine lookup bases are `0x00C6C004`
and `0x00C6A004`. The 17th matrix word's native compact/affine discriminator is
handled explicitly; the payload is not assumed to be an ordinary graphics API
matrix. Inputs are read twice and finite/affine checks applied. First admission
requires agreement with the actual supplied manager `+0x6F4` matrix. The shared
manager is never treated as retained per-ship position.

Offline reconstruction from 3741 prior stable records: 3737 orientation results
within 1e-4; maximum difference 0.00296961557. Four asynchronous update-phase
differences remain. Maximum translation/cache difference 0.0955429077 native
units. These comparisons support the arithmetic, not atomic simulation reads.
Current full-pose runtime corroboration is still required.

## Lifetime and synchronization

The existing render-thread semantic lock serializes registry access. A new,
default-off destruction notification at `0x004158C1` invalidates registry and
source ownership before forwarding the unmodified original destructor. Static
chain: ship vtable `0x00796F0C` -> deleting wrapper `0x00414B8F` -> destructor
call `0x00414B92`; optional allocation release follows at `0x00414B9F`.
The overwritten prefix is one five-byte `mov eax,0x0075BB13`, containing no
relative operand. Existing hook machinery preserves flags, GPR, FPU/SIMD and
original stack/ECX, executes the prefix in the trampoline, then returns to +5.
This is Codex's ABI engineering judgment supported by bytes/static code and
mechanical tests; actual game destruction-hook invocation remains unconfirmed.

Registered live owners are retained across the old visibility timeout. They
are not made immortal: destruction removes them; invalid vtables, links,
model/list/LOD identity quarantine them. A recycled pointer alone cannot revive
the old owner. Synthetic explicit removal and reuse pass. All gameplay death
states and actual destruction still need runtime evidence.

At the first qualified tactical semantic wrapper in each scene frame, current
camera/view/projection/viewport are checked twice, and all living registered
poses are rebuilt from simulation inputs. No fixed-Hz throttle applies to
render-state publication. Existing roughly 30 Hz diagnostic JSONL sampling is
only an evidence-volume bound. If no qualified wrapper/current camera exists,
no new frame is fabricated; old camera pixels are not replayed.

The existing exact-frame D3D9 source, bounded current-user mapping, x64 ordinary
D3D9 -> pinned Remix runtime, GPU surface transfer and game compositor remain.
Source header version 2 explicitly identifies simulation-derived persistent
state; layout is unchanged and version 1 diagnostic mode remains available.
Same-frame rejected/destructed source is rejected by the receiver too. Missing,
late or invalid replacement output never suppresses the original game ship.
Camera tracking does not promise to eliminate all unrelated GPU deadline misses.

## Lighting and limits

Only the already-qualified world-directional light bank, native slots 0/1,
can be associated with a retained offscreen instance. Derived context records
the native bank owner/model and target separately; raw snapshots remain intact,
capture QPC is not refreshed, and native non-directional types are rejected.
No point/effects-light or model-local-vector equivalence is inferred. Existing
light/material/image/quality settings remain unchanged.

Registry: 32 entries. No callback allocation, disk I/O, rendering, image work or
blocking receiver wait. Existing asset slots/cache, 16 MiB scene mapping,
fixed GPU pool, 128 MiB image/output-resource bounds, 32 MiB combined logs and
20 GB aggregate authorization remain. Summary counters continue after detailed
logging saturates. Original rendering ON; high-volume geometry hook OFF.

## Offline result and remaining gate

CONFIRMED synthetic native worker: 120 consecutive frames, changing simulation
pose and camera, no new render observations, one asset capture and one instance
generation; 120 offscreen updates/publications; explicit removal prevents stale
publication; worker joins. x86/x64 registry tests pass 18 checks each.

Actual version-2 ordinary-D3D9/Remix GPU fixture delivers 595/600 fixed-window
frames; state restoration, resize/recreation and normal owned exit pass. It is
synthetic, not SFC camera-switch or destruction proof. The vendor common-device
objects shutdown warning remains an open issue, not a clean-disposal claim.

Next exact action: run `tools/d3d9_proof/start_d3d9_persistent_scene_session.ps1`
with the two-ship fixture and analyze `PERSISTENT-SCENE-001.json`, existing exact
source/GPU timing, identity/revision continuity, cleanup and client hashes.

Run104 now confirms resident identity/geometry across actual sponsor camera
swaps;brief presentation gaps remain,not model reloads. Run105 combines existing
nonneutral grade and depth-derived owner coverage in one backend MRT draw,
with exact GPU equivalence tests. Neutral grade retains coverage-only path.
Frame/lifetime/camera acceptance unchanged. No claim this small-stage saving
cures the short first-launch budget. One sponsor comparison,then evidence
review/move on per bounded-pass direction,not endless harness optimization.
