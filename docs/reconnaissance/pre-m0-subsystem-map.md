# Pre-M0 Subsystem Map

This is a static, build-specific working map for StarFleetOP.exe 2.5.6.4
(MD5 2BE8F713F81B1C68D50EAD6088C32886). Names ending in “candidate”
are analytic shorthand, not recovered symbols.

| Region | Probable subsystem | Confidence | Boundary evidence | Important links |
|---|---|---|---|---|
| 0x006B3570–0x006B4A0F | DirectDraw surface manager | CONFIRMED | Exact retained tDDSurfMgr method diagnostics, DirectDraw imports, COM calls, aligned function boundaries | mode enumeration → interface setup → display mode → surface/buffer creation → flip/blit presentation |
| 0x006B2520–0x006B2FFF | GDI/software surface path | STRONG HYPOTHESIS | CreateDIBSection, BitBlt, StretchBlt, color-table and device-capability imports | likely alternate/fallback path; configuration linkage is not proven |
| 0x0069CDA0–0x0069EFFF | Direct3D manager and submission region | STRONG HYPOTHESIS | D3D HRESULT map, very large manager state, DirectDraw creation, wrapper allocation, calls into wrapper methods | manager +0x3C54 → 0x170-byte wrapper → COM members +0x30..+0x4C |
| 0x006A7C20–0x006A853F | Legacy graphics COM wrapper | CONFIRMED as a wrapper; method identities are hypotheses | constructor/release symmetry and repeated COM vtable calls | wrapper +0x48 vtable +0x28 is the strongest current BeginScene candidate |
| 0x0040AD35–0x0040AE0A | Z-buffer anchor | STRONG HYPOTHESIS | exact ZBuffer string and graphics helper calls | needs ownership, format, and surface-attachment mapping |
| 0x0042D6EC–0x00430367 | Model metadata, parsing, and damage material selection | STRONG HYPOTHESIS | model.siz, model-version diagnostic, damage diffuse/luminance texture names | likely feeds model objects; no confirmed connection to submission yet |
| 0x0041C271–0x0041CAFF | Ship entity/model acquisition | STRONG HYPOTHESIS | ship .mod path plus hash-bound cloak landmarks | probable gameplay/entity-to-model boundary; function is multi-role |
| 0x0044C185–0x0044DEFF | Hardpoint consumption/selection | STRONG HYPOTHESIS | hardpoint strings and documented .mod semantics | proves model hardpoints affect gameplay attachment/selection, not rendering |
| 0x006770A0–0x006775FF | Q3 sprite read/error path | CONFIRMED | exact tQ3Error_Q3CAST_ReadSprite string and eleven direct caller sites | downstream sprite lifetime, batching, and rendering remain unknown |
| 0x0048CA35–0x0048CC22 | Camera mode/lock control | CONFIRMED | exact overhead-camera patch byte at 0x0048CBFF, camera-lock strings, local function boundary | renderer-facing camera/matrix construction remains unknown |

## Working boundary chains

The strongest graphics chain is:

tD3DMgr candidate (0x0069D2B0) → initialization (0x0069D3F0) →
wrapper (manager +0x3C54, constructor 0x006A7C20) → candidate scene/device
methods (0x006A84B0, 0x006A8500) → DirectDraw presentation
(0x006B38C0 flip or 0x006B3A30 blit).

Only the initialization, wrapper lifetime, and presentation endpoints have
directly corroborated identities. The middle scene/device method identities and
the scheduling relationship between submission and presentation remain open.

The strongest content chain is:

ship/entity path (0x0041C271) → model parser/material cluster
(0x0042D6EC–0x00430367) → **unknown scene/render-object construction** →
candidate D3D submission (0x0069EB90–0x0069EFFF).

The missing middle is the highest-value boundary for post-baseline work.

## Format correlations

- Model Browser documentation describes LODs, materials, diffuse/emissive
  textures, damage points, hardpoints, break parts, and pivots. Executable
  anchors corroborate model-version parsing, .mod paths, damage diffuse/SI
  luminance names, and hardpoint consumption.
- Materials Editor’s missing/incorrect luminance checks align with the paired
  ordinary and SI strings in the 0x0042DEF5 cluster.
- Q3 Editor proves community knowledge of the packed sprites.q3 format;
  0x006770A0 independently anchors the executable’s sprite-read/error path.
- Mission and campaign formats are useful gameplay/content evidence but did not
  produce a renderer boundary in this pass.

No static evidence yet confirms a stable per-frame render-object identity, the
ship-geometry submission function, material binding layout, camera matrix
assembly, or lighting/transform state ownership.
