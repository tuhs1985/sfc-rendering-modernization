# Pre-M0 Evidence Notes

## Evidence rules

- **CONFIRMED** means direct static evidence or multiple independent
  corroborators identify the behavior.
- **STRONG HYPOTHESIS** means substantial evidence identifies a likely role, but
  one or more critical identities or links remain unresolved.
- **SPECULATIVE** is reserved for plausible questions or interpretations that
  lack enough support to guide implementation.

All addresses below are virtual addresses in the exact supported client unless
identified otherwise. Retained diagnostic text is treated as strong evidence
only when aligned function boundaries and relevant imports/COM calls corroborate
it. COM method names are not asserted solely from a vtable offset.

## Landmark normalization

- The hash-bound SFC Editor maps contain 259 rows: 253 for StarFleetOP.exe
  (245 active, 8 commented candidates) and 6 for ServerPlatform.exe (5 active,
  1 commented candidate).
- The exact supported client matches the map’s MD5, so its 253 locations and
  baseline bytes are CONFIRMED for this build. Of these, 92 are in .text
  (84 active, 8 candidates), 76 active are in .rdata, 84 active are in
  .data, and 1 active is in .rsrc.
- The inspected server does not match the map’s expected hash. Its six rows are
  retained as community knowledge, but byte/build correlation is not confirmed.
- The compiled launcher contains 14 additional service-redirection offset
  templates. They are cataloged separately because they lack target hashes and
  baseline bytes: 5 EAW client, 3 EAW server, 5 OP server, and 1 SFC3 server.
- Replacement bytes are blank in the editor catalog because the declarative
  maps describe typed editable values, not one canonical replacement. For the
  exact client, original_bytes records the observed hash-matched baseline.

The client editor map is overwhelmingly gameplay/data oriented. Its 28 tabs
include phasers (37 rows), missiles (21), plasma range (19), photons (15),
disruptors (13), AMD (12), hellbores (12), cloak (11), damage allocation (11),
and smaller weapon/movement/sensor/shield/camera groups. It is valuable as a
build-locked address grid even where it does not identify rendering code.

## Confirmed graphics evidence

- 0x006B35C0 is the display-mode enumeration method: exact diagnostics name
  tDDSurfMgr::mEnumDispModes; it calls the DirectDrawCreate thunk at
  0x006F283A, queries the corroborated legacy interface, and invokes a COM
  enumeration method with callback 0x006B3570.
- 0x006B38C0 is mSwapBuffers: exact flip-failure text, front/back surface
  members, a flip-like COM call, and explicit lost-surface recovery.
- 0x006B3A30 is mCopyToFront: exact BitBlt-failure text, a blit-like COM
  method, and lost-surface recovery.
- 0x006B3BC0, 0x006B3E10, 0x006B4360, 0x006B4460, and 0x006B4540
  establish surface creation, DirectDraw interface setup, display-mode
  set/restore, and persistent buffer setup. 0x006B4540 also calls the
  DirectDrawCreateClipper thunk at 0x006F2840.
- Import thunk 0x006F2846 resolves DDRAW!DirectDrawEnumerateA.
- 0x0069CDA0 maps legacy Direct3D errors. It is diagnostic support, not proof
  of scene submission.
- 0x006A7C20/0x006A7C60 construct and release a 0x170-byte wrapper containing
  multiple COM interface pointers.

## Strong graphics hypotheses

- 0x0069D2B0 is the central D3D/render-manager constructor. It initializes
  state through at least +0x800C, including repeated arrays and a large cache.
  The exact member meanings are not yet known.
- 0x0069D3F0 is the main D3D-manager initialization routine. It calls
  DirectDrawCreate, allocates the wrapper, and stores it at manager +0x3C54.
  The full device creation chain needs interface reconstruction.
- 0x006A8500 is the best BeginScene candidate because it invokes wrapper
  +0x48 vtable +0x28, and it has direct callers at 0x0069EE7B and
  0x0069EF6A. The name remains a hypothesis until the interface at +0x48
  is identified.
- 0x0069EB90–0x0069EFFF is the strongest current scene/primitive submission
  region. Nearby code dereferences manager +0x3C54, then wrapper +0x44 or
  +0x48, and invokes COM methods. Exact draw methods are unresolved.
- 0x006B2520–0x006B2FFF is a GDI/software surface cluster. The relationship
  to the Software3D configuration is plausible but unconfirmed.

## Content-to-render correlations

- 0x0042FEF9 is a strong model-parser candidate because it contains the exact
  version diagnostic and is called by 0x0042F5D7.
- 0x0042D6EC references assets/models/model.siz.
- 0x0042DEF5 references light/medium/heavy damage textures plus SI
  luminance variants for ordinary, starbase, and organic models.
- 0x0041C271 references assets/models/%cms/%cms.mod and contains seven
  hash-bound cloak landmarks, making it a strong ship/entity-to-model candidate.
- The 0x0044C185–0x0044DEFF cluster consumes HardPoint%d and subsystem
  hardpoint semantics. This correlates .mod structure with gameplay attachment
  selection but does not identify geometry submission.
- 0x006770A0 is the confirmed Q3 sprite-read/error path with eleven direct
  callers.
- The camera patch at file offset 0x0008CBFF maps to 0x0048CBFF inside
  0x0048CA35–0x0048CC22, alongside camera-lock strings. This confirms a
  camera control region, not camera-matrix construction.

## Explicitly unconfirmed

No conclusion about renderer architecture, hook placement, replacement
technology, stable render-object identity, ship geometry submission, material
binding layout, scene traversal, camera matrices, or lighting ownership is
CONFIRMED. These are experiment targets, not implementation assumptions.
