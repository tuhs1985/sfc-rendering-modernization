# Run184 — base display admission independent of enhanced assets

Sponsor clarification controls this increment: fully prepared appearance remains
preferred, but a model with geometry and base textures ready proceeds immediately.
Enhancement work must neither gate that base nor wait for bundle completion.
Timing examples are not an added requirement. Preserve Run183's working opt-in.

## Implementation

- `parallel_assets.py`: schedule enhanced image derivation from its own ready
  primary/secondary images while base bundle construction continues. Shader
  identities join later; no bundle/renderer dependency for pixel generation.
  Primary image tasks and base assembly take precedence over queued enhancement
  work; existing four-worker/four-context/64asset/output limits remain.
- Base no longer waits for secondary-image reads/decodes. Missing/failed required
  secondary data produces an explicit enhancement partial after base readiness,
  not a missing base or guessed glow. Base native residency identity now covers
  geometry, LOD, primary image content and declared enhancement association names
  (`sfc.base-asset.v1`); enhanced pieces retain actual primary/secondary content
  hashes and conflict checks. No pointers/resource IDs as reusable identity.
  Original images are assumed immutable during the live session; mid-session
  on-disk asset mutation remains unsupported. Identical base/declared associations
  reuse the existing canonical geometry and material policy; conflicting material
  roles remain explicit partials under the unchanged Remix primary-hash contract.
- `progressive_scene_relay.py`: collect/admit all ready bases before enhancement
  filesystem writes. After base submission, apply up to four already-complete
  groups per coordinator cycle, then yield to new base/state work. No gathering
  timer. Complete materials apply to retained instances; no mesh reconstruction
  or base-texture reload is requested. Pending enhancements keep reservations
  until applied; shutdown reports unfinished enhancement work rather than success.
- `scene_bundle.py` and `multi_scene.py`: derive the existing catalog identity
  from the exact immutable bytes being written. The consumer still independently
  validates the same files/FNV64 protocol. No producer process launch or file
  rereads for catalog identity, and no new wire layout or weakened checksum.
- Existing `mesh_checksum.cpp/.py` worker DLL gains the **same** FNV1a64 and pinned
  Remix XXH3 implementations used by existing command-line utilities. Existing
  FNV32 captured-packet check unchanged. ctypes releases the GIL and keeps immutable
  buffers alive. No new DLL deployed to SFC; no game-process call to these helpers.
  `build_mesh_checksum.ps1` now freezes the same pinned xxhash.h used by the
  material helper (FDBF70C5F5CCFFED18A1CF82B635799CA5128743DB8746076AA136A5AA4BC467).
  XXH3 here is Remix binding-specific, not an adapter-neutral material identity.

Added `tests/test_asset_identity.py`; extended `tests/test_parallel_assets.py` and
CPU checker. Existing stable mode, experimental opt-in flag, native semantic seam,
camera/light/appearance configuration, runtime/SDK and original drawing unchanged.
Initial restricted linker overwrite failed; same build succeeded with appropriate
process access, no permission-policy changes or source workaround.

## Attribution and CPU verification

Retained-FCA replay193934 split the earlier broad base stage into:
base identity0.072ms, bundle assembly/write93.409ms, **catalog helper691.834ms**.
After in-memory catalog identity, replay194136 showed base469.780ms but the second
native texture-hash process then took~616ms. Reusing its exact pinned algorithm
through the same DLL removes that process too; no diagnostic validation removed.

Final captured-FCA replay:
`artifacts/initial-readiness/parallel-cpu-20261025-194725-550969`:

| Milestone from discovery | Recorded |
| --- | ---: |
| Base ready | 514.373ms |
| First enhanced stage publication | 550.196ms |
| All enhancement pieces ready | 1139.282ms |

Base assembly/write230.165ms (includes native identities/concurrent-worker load),
catalog assembly from prepared identities0.0294ms. Total CPU-control elapsed1.282s
includes publication and comparison; not first visible pixels. Earlier final
identity implementation replay194259 had base556.089ms. These are bounded retained
FCA examples, not universal sub-second loading. Original geometry, original image
hashes, all derived image metadata/hashes and final material-stage hash equal the
accepted reference exactly. Independent legacy native helper verifies byte-exact
new catalog packets and odd-width/NUL-containing texture hash parity offline.

Tests prove secondary decode can remain stalled while base completes; derived maps
can finish while base assembly is deliberately stalled; absent secondary produces
base plus partial; ready-base publication precedes enhancement IO; enhancement
drain yields after four groups. 611Python checks PASS (529main plus82other suites),
including18parallel and3new native-identity regressions.

## Actual standalone renderer checks — streaming limitation remains

All controls use the ordinary D3D9 path/current settings and exit normally, with
four independently acknowledged owners/three contents/shared geometry, no rejected
assets/partials, native HUD/scene exact and resize/recreation checks. Full final
FCA/RCA/FDD material stages and every derived image metadata/hash match reference.

- **194803-242751-return-fixture**, newly arriving third asset: initial RCA base
  ~253ms/FCA894ms; new FDD base1409.6ms after its own discovery. Steady delivery
 598/600. However, full buffered evidence has159post-start omissions, including
  79records at9.305–10.624s and77 at11.643–12.919s. Material stages publish after
  initial output (24after first cohort). This does **not** establish uninterrupted
  streaming, despite its good later steady window.
- **194859-535640-return-fixture**, deliberate5s group delay: steady599/600, but
  full evidence has63post-start omissions, longest62records at8.537–9.570s.
  Final enhanced publication6.818s, first full cohort output7.517s. It must not be
  advertised as a clean late-material consumption pass based on the steady window.
- **195237-468848-return-fixture**, unchanged stable-mode final-source control:
 595/600 and normal cleanup. Existing normal multiship qualification refreshed
  through its original native tests/adjudicator with current DLL/source locks.
  Experimental read-only preflight prints enabled banner and PASS. No lock bypass.

These are omitted returned-ship layers, not measured SFC frame losses or game
freezes. Material publication correlates with interruptions; internal cause and
per-material GPU consumption remain unproved. Pinned runtime watcher/reload source
in Run163 remains relevant. No continuous screenshots or new discovery run used.

## Adjudication and next action

**Two-phase producer implemented; sub-second base readiness demonstrated for the
captured FCA. Seamless live enhancement application remains unresolved.**
Do not confuse CPU base-ready/admitted with physical display or mark the full
scene<2s target complete. The experimental opt-in remains explicit and sponsor
authorized; stable default unchanged. Known late-material interruptions persist.

Next exact action: investigate supported non-disruptive Remix material consumption
using the full retained streaming interval, not just the post-load600frame window.
Preserve base-first submission and new in-memory identities. Do not silently
resume the parked geometry API route, patch runtime internals or add stale frames.

No SFC launch, client/runtime/SDK/settings changes, staging, commit or push in this
increment; HEAD9ff2d3d. Prior work preserved. Current qualification/preflight and
diff checks pass; no owned test process/channel remains. Generated CPU duplicate
outputs archived separately after SHA verification; original capture/analyses and
actual renderer evidence retained. `run184-cpu-generated.zip` compressed387655204B
to28749053B with1005files SHA-verified before removal; archive SHA256
6b5d762f3ca51cf17724f6e068503b306d2f765478abd304d02a04f08e8532db.
Archive receipt is in artifacts/initial-readiness; curated versionable evidence is
`docs/reconnaissance/evidence/20261025-base-enhancement-split.json`.
