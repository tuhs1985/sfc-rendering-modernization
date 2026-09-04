# Pre-M0 Engine Reconnaissance Report

Date: 2026-09-03  
Scope: bounded static reconnaissance against the preserved SFC OP 2.5.6.4
installation. No executable patching, game execution, runtime probing, wrapper
installation, hook implementation, renderer selection, or gameplay change was
performed.

## Executive result

The community material provides a reliable build-locked landmark grid but not a
reconstructed engine. A total of **273 community landmarks** were normalized:

- **259 hash-bound SFC Editor rows**: 253 client rows and 6 server rows.
- **14 compiled launcher service-redirection offsets**, cataloged separately
  because they do not include target hashes or original bytes.

The exact supported StarFleetOP.exe has MD5
2BE8F713F81B1C68D50EAD6088C32886 and exactly matches the editor definition.
Its **253 landmarks are confirmed for this build**: 245 active and 8 commented
candidates. Ninety-two occur in code (.text), while the remainder provide
data/string/resource anchors. The inspected server does not match its editor
definition hash; its six offsets are retained as community evidence only.

Static analysis identified a confirmed DirectDraw surface-manager region,
confirmed flip and blit presentation endpoints, a strong Direct3D
manager/wrapper/submission cluster, strong model/material and ship/model
clusters, a confirmed Q3 sprite-read boundary, and a confirmed camera-control
region. It did **not** establish the ship-geometry submission function, stable
render-object identity, scene traversal, material binding layout, camera matrix
assembly, or lighting/transform ownership.

The best next investigation after CDD baseline is to reconstruct the legacy
graphics wrapper’s COM interface identities and establish frame call order
between candidate scene submission and confirmed presentation. That is the
smallest experiment that can determine whether CTE-1 has a stable Legacy Render
Access boundary without preselecting an architecture.

## Observed Facts

### Landmark inventory

| Source | Count | Build correlation | Primary categories |
|---|---:|---|---|
| StarFleetOP.txt | 253 | exact client MD5 match; 245 active, 8 commented candidates | 28 gameplay/data tabs; phasers 37, missiles 21, plasma range 19, photons 15, disruptors 13, AMD 12, hellbores 12, cloak 11, damage allocation 11, plus movement, sensors, shields, camera, and other systems |
| ServerPlatform.txt | 6 | inspected server MD5 does not match expected definition MD5 | network/GameSpy |
| SFCLauncher 2.1.0.22.exe templates | 14 | target build/hash not encoded | 12 GameSpy endpoint substitutions and 2 HTTP/MOTD substitutions across EAW client/server, OP server, and SFC3 server blocks |

The exact client landmark distribution is:

| PE section | Active | Commented candidate | Total |
|---|---:|---:|---:|
| .text | 84 | 8 | 92 |
| .rdata | 76 | 0 | 76 |
| .data | 84 | 0 | 84 |
| .rsrc | 1 | 0 | 1 |

The editor definitions encode editable typed values, not canonical patches.
Accordingly, the catalog records observed baseline bytes for the hash-matched
client but leaves replacement bytes blank. The separate launcher catalog
records textual substitution intent while explicitly marking original and
replacement bytes unknown.

### Static-analysis coverage

- 1,262,760 instructions were parsed from the ignored static disassembly.
- 14,636 heuristic function-start candidates were indexed.
- 92 client code landmarks were correlated with containing function candidates.
- 342 selected graphics/model/camera/sprite string cross-references were found.
- 15 graphics-import cross-references were indexed.
- 159 high-relevance automatic function rows were retained; 26 major regions
  were separately lead-adjudicated in the curated map.
- The client imports DDRAW, including DirectDrawCreate,
  DirectDrawCreateClipper, and DirectDrawEnumerateA, and also contains a distinct
  GDI/DIB import cluster.

Automatic function boundaries and proposed names remain heuristic. They are not
recovered symbols and are not promoted to confirmed findings without additional
corroboration.

## Confirmed Findings

### DirectDraw ownership and presentation

The region 0x006B3570–0x006B4A0F is a confirmed DirectDraw surface-manager
cluster. Exact retained method diagnostics, aligned boundaries, relevant
imports, and matching COM calls corroborate:

| Address | Confirmed role | Re-check evidence |
|---|---|---|
| 0x006B3570 | display-mode enumeration callback | passed by 0x006B35C0 to the enumeration COM call |
| 0x006B35C0 | tDDSurfMgr::mEnumDispModes | exact diagnostics; calls DirectDrawCreate thunk 0x006F283A; interface query and mode enumeration |
| 0x006B38C0 | tDDSurfMgr::mSwapBuffers | exact flip-failure text; front/back members; flip-like COM call; surface-lost recovery |
| 0x006B3A30 | tDDSurfMgr::mCopyToFront | exact BitBlt-failure text; blit-like COM call; surface-lost recovery |
| 0x006B3BC0 | tDDSurfMgr::mCreateSurface | exact create/GetSurfaceDesc diagnostics and corresponding COM calls |
| 0x006B3E10 | tDDSurfMgr::mInitInterfaces | DirectDrawCreate, interface, and cooperative-level diagnostics |
| 0x006B4360 | tDDSurfMgr::mSetDisplayMode | exact method diagnostics and display-mode COM calls |
| 0x006B4460 | tDDSurfMgr::mRestoreDisplayMode | exact restore diagnostics; direct callers at 0x006B34D8, 0x006B3842, 0x006B3E40, and 0x006B3F30 |
| 0x006B4540 | tDDSurfMgr::mInitBuffers | persistent primary/back surfaces, clipper, palette, and description setup; called at 0x006B42D6 |

No static direct callers were found for mSwapBuffers or mCopyToFront, consistent
with method-table dispatch. This confirms presentation endpoints but leaves the
per-frame scheduling owner open.

### Legacy graphics wrapper

0x006A7C20 and 0x006A7C60 construct and release a 0x170-byte legacy graphics
wrapper with COM pointer slots at +0x30 through +0x4C. Wrapper ownership is
confirmed by constructor/release symmetry and repeated interface calls. The
individual interface types and most method identities are not confirmed.

### Content anchors

- 0x006770A0 is a confirmed Q3 sprite-read/error path. The exact
  tQ3Error_Q3CAST_ReadSprite string and eleven direct call sites corroborate it.
- 0x0048CA35–0x0048CC22 is a confirmed camera control region. It contains the
  exact hash-bound overhead-camera landmark at 0x0048CBFF plus camera-lock and
  CameraRadio strings.
- The hardpoint-selection cluster corroborates that documented .mod hardpoint
  semantics are consumed by gameplay selection. It does not confirm a rendering
  function.

## Strong Hypotheses

### Direct3D manager and submission

- 0x0069D2B0 is the likely central D3D/render-manager constructor. It initializes
  an object through at least +0x800C, including three 63-dword arrays and a large
  cache-like region.
- 0x0069D3F0 is the likely main D3D-manager initializer. It calls
  DirectDrawCreate, allocates the confirmed wrapper, and stores it at manager
  +0x3C54. Direct callers occur at 0x0069E1D0 and 0x0069E244.
- 0x006A8500 is the strongest current BeginScene candidate: it invokes vtable
  +0x28 on wrapper member +0x48 and is called at 0x0069EE7B and 0x0069EF6A.
  The name cannot be confirmed until +0x48’s interface is identified.
- 0x0069EB90–0x0069EFFF is the strongest scene/primitive submission candidate.
  It gates calls into wrapper helpers and dereferences manager +0x3C54 to reach
  COM members +0x44/+0x48.
- 0x006B2520–0x006B2FFF is a probable GDI/software surface path based on
  CreateDIBSection, BitBlt, StretchBlt, color-table, and device-capability calls.

### Model, material, ship, and z-buffer regions

- 0x0042FEF9 is a likely model parser. It contains the exact “format less than
  version 2” diagnostic and is called by 0x0042F5D7.
- 0x0042D6EC likely handles model metadata/indexing because it references
  assets/models/model.siz.
- 0x0042DEF5 likely selects damage materials/textures because it references
  light/medium/heavy diffuse and SI luminance variants for ordinary, starbase,
  and organic models.
- 0x0041C271 is a likely ship/entity-to-model acquisition region. It references
  assets/models/%cms/%cms.mod and contains seven exact cloak landmarks.
- 0x0040AD35–0x0040AE0A is a z-buffer-related anchor, but format, ownership,
  attachment, and lifetime are unresolved.

These clusters corroborate documented Model Browser and Materials Editor
semantics, but no static call chain yet joins a gameplay ship or parsed model to
the candidate D3D submission region.

## Speculation / Open Questions

The following remain deliberately unasserted:

- whether wrapper +0x48 is the expected legacy Direct3D device interface;
- whether 0x006A8500 is BeginScene and where EndScene occurs;
- whether manager cache arrays hold transforms, materials, lights, or unrelated
  state;
- where scene/object traversal begins;
- where a gameplay ship becomes a render object;
- whether render-object identity persists across frames;
- where model/material pointers are attached;
- where camera matrices are assembled;
- which function submits ship geometry;
- where Q3 sprite instances become render batches;
- how z-buffer and software/GDI paths are selected and owned.

These are runtime questions, not design assumptions.

## Implications for CTE-1 Legacy Render Access

1. **A stable legacy presentation boundary is evidenced.** Flip and blit
   endpoints, surface setup, mode changes, and recovery are concrete and
   build-specific. CTE-1 can use them as observation landmarks.
2. **Presentation is not equivalent to scene access.** Intercepting only
   mSwapBuffers or mCopyToFront would expose a completed surface, not necessarily
   ships, materials, depth, camera, or object identity.
3. **The strongest candidate for richer access is one layer earlier.** The
   manager + wrapper region around 0x0069D3F0 and
   0x0069EB90–0x0069EFFF probably contains device/scene calls, but interface and
   method identity must be resolved before evaluating any access strategy.
4. **Content-side anchors make a two-ended trace feasible.** The ship/model,
   parser/material, hardpoint, sprite, and camera anchors give future work
   concrete places to trace forward while graphics calls are traced backward.
5. **No architecture decision follows from this evidence.** A wrapper,
   translation layer, in-process hook, external capture path, or renderer change
   may expose materially different information. The CDD must define required
   access before those options are compared.

## Prioritized runtime questions

Priority 0:

1. Identify every COM interface at wrapper +0x30..+0x4C and map its vtable.
2. Establish the exact per-frame order of BeginScene/EndScene, primitive calls,
   mSwapBuffers/mCopyToFront, and recovery paths.
3. Resolve method-table callers of the two confirmed presentation functions.
4. Trace one known ship instance from 0x0041C271/model parsing to an actual
   geometry submission call.

Priority 1:

5. Test whether stable ship/render-object identity persists across frames.
6. Locate model/material attachment and LOD selection.
7. Locate world/view/projection matrix assembly from camera control through
   device state.
8. Determine z-buffer creation, attachment, format, and lifetime.
9. Trace one Q3 sprite from 0x006770A0 to batching and draw submission.

Priority 2:

10. Map hardware/software and flip/blit selection conditions.
11. Characterize display-change and lost-surface recovery lifetimes.
12. Classify the large manager’s transform/light/material/texture caches.

No runtime experiment was performed in this phase.

## Recommended next investigation after CDD baseline

Run one narrowly scoped Legacy Render Access experiment:

1. finish static IID/vtable reconstruction for the 0x170-byte wrapper;
2. in an approved disposable copy, observe call order and object pointers only
   at the candidate scene methods and confirmed presentation endpoints;
3. trace a single known ship and a single sprite forward to those calls;
4. record which data demanded by the baselined CDD is actually visible at each
   boundary.

Stop there and use the result to evaluate architecture candidates. Do not begin
renderer replacement until that access evidence and the baselined capability
requirements are reviewed together.

## Artifact index

- data/community-landmarks.csv and .json — normalized hash-bound editor catalog.
- data/launcher-embedded-landmarks.csv — separate compiled launcher offsets.
- data/pre-m0/major-function-map.csv — curated address/function evidence.
- data/pre-m0/function-map.csv — automatic heuristic function/call/data map.
- pre-m0-subsystem-map.md — subsystem boundaries and working chains.
- pre-m0-evidence-notes.md — exact evidence and confidence discipline.
- pre-m0-runtime-questions.md — experiment-ready backlog.
- pre-m0-raw-analysis-references.md — raw-output policy and reproduction guide.
- tools/recon — repeatable read-only static-analysis helpers.

The ignored full disassembly remains under artifacts/pre-m0/raw. Original game
assets and reference archives remain excluded from Git and unmodified.
