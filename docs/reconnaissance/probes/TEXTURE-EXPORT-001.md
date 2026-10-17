# TEXTURE-EXPORT-001 — same-epoch original image references

## 2026-10-16 actual fallback result / final eligibility observation prepared

Run20261016-165955-enabled, component0.16, confirms +3D58=511, +8009=0,
textures_enabled1, same kff model and five image pairs (IDs174–183 this process).
Thus combined multi-texture mode0 is NOT selected at that snapshot; fallback
family is selected. Original packet/OBJ/images validate; hooks restored/normal
exit/client unchanged. Do not label fallback two-pass itself dynamically observed.

Narrow static follow-up: manager+17C getter0069F270 returns +800C validation mask;
wrapper006AC63F–6AC checks its bit1/bit2 according to previous +3F54 state returned
by setter0069E9C0. Eligibility ->mode2 then mode1; otherwise primary-only mode1.
Those two inputs were NOT in0.16. Record this instrumentation gap honestly.
Two-pass static sequence sets secondary+vertex color first, then ZERO/SRCCOLOR
framebuffer blending multiplies by primary; algebra is consistent with the
existing provisional product, not proof that these passes ran or match modern
physical emission. No preview changed/promoted from this result.

Prepared0.17 adds read/recheck of +800C DWORD and +3F54 byte alongside existing
fields: manager_fallback_validation_mask, manager_previous_alpha_test_flag. Ten bytes
total read twice; same fixed storage, one attempt/default-off reference gate,
no new hook/ABI/COM/API/native writes/render-thread work of substance. Recovery
keeps old absent fields unknown. Analyzer predicts conditional pass requests only,
never GPU state/pass completion. Unreadable/change causes status2/4, not game
failure. Same existing90s fixture/gate/log/image/storage/cleanup/privilege limits;
no capture-size increase beyond tiny JSON fields or multi-GB mechanism. Future
run only after offline validation, when gameplay is convenient; do not request a
new sponsor run merely to repeat already-confirmed family/image associations.

Getter/setter follow-up0069EA19–98 confirms state15 ALPHATESTENABLE and state25
ALPHAFUNC; +3F54 is alpha-test cache, not blend enable. Corrected temporary naming
before any0.17 execution; old0.16 never recorded either version of that field.

## 2026-10-16 secondary-image role checkpoint / minimal path observation

Question: does the selected mesh use the multi-texture branch whose combiner
adds the secondary image to vertex lighting before multiplication by the primary?
This is not the same as blindly wiring the secondary bitmap directly to emission.

Exact-build static evidence: source+0x1C is selected at006AC0F2. Wrapper006AC610
calls manager vtable+D0 (007B8E1C ->0069F260), which returns manager+8009.
An earlier gate006AC5D8 tests feature bit20 from manager vtable+24. Getter
0069D3B0–3C4 sets that bit iff manager+3D58 DWORD is nonzero. Capture/recheck
that DWORD too (`manager_secondary_path_word`); mode0 inference requires BOTH
it and +8009 nonzero. Zero +3D58 selects mode1 before +8009 is consulted.
Both predicates were adjudicated offline before runtime; neither may be omitted.
Nonzero +8009 after that gate takes006AC61C–631, preparation mode0.006AC522–53A passes primary ID as
first texture argument and secondary as second;006AB44F–490 binds first at stage1
and second at stage0 when +8009 is nonzero. Device3 SetTextureStageState is
vtable+A0 (Windows SDK10.0.26100.0 d3d.h); initialization0069D9A9–DA47 sets
stage0 COLORARG1=TEXTURE(2), COLORARG2=DIFFUSE(0), COLOROP=ADD(7), and stage1
COLORARG1=TEXTURE(2), COLORARG2=CURRENT(1), COLOROP=MODULATE(4).
Thus intended color is primary * clamp(secondary + lit vertex color), not
uncolored secondary emission. API enums corroborated in installed d3dtypes.h
and Microsoft D3DTEXTUREOP/D3DTA documentation. Static intended relationship
CONFIRMED; actual active branch in accepted capture UNOBSERVED (old collector
did not record +8009), current hardware/API state and physical emission strength
not proven. ModelBrowser emissive toggle/image suffix is not a substitute.

Minimal collector extension0.16: read manager+8009 and +3D58 alongside the selected
mesh/resource association, re-read at final identity validation, serialize
`manager_multitexture_flag` and `manager_secondary_path_word`. Additive optional JSON fields; old captures remain
valid but do not retroactively acquire this observation. No new hook, ABI change,
COM/API/engine call, image copy, disk I/O, allocation or native write. One byte
read twice; same default-off EnableTextureReferences gate, fixed <8KiB storage,
one attempt/no retarget. Additional +3D58 DWORD read/recheck is likewise fixed,
so five bytes read twice total. Unreadable ->status2; changed ->status4; neither changes
game rendering. Value zero is valid evidence of fallback, NOT missing/true.
No glow applied until fresh evidence adjudication; this flag selects a code path,
not a GPU-state readback or proof every SetTextureStageState call succeeded.

Launch unchanged prepared start_texture_export_session.ps1 from already elevated
parent. Usual two-ship fixture, normal appearance/play, automatic tactical gate,
90s max then two exit cues and normal exit. No maneuvers/timestamps/comparison
needed. Existing build/privilege, logging16/32MiB,120frames/10000events, ten
resources/4096²/64MiB warning/128MiB image cap, cleanup/hash checks below retained;
diagnostic geometry hook OFF. Expected reference JSON <8KiB; ordinary event log
<1MiB, no rapid multi-GB mechanism. Existing collector output may be larger only
within established hard bounds. Offline inspect flag plus same-epoch IDs, never
reuse old live pointers after exit. Preserve packet/JSON/source hashes and useful
archive before any optional exact generated-run cleanup; no original/cache deletion.

Status: fresh runtime association and primary textured preview CONFIRMED;
overall PARTIAL pending placement comparison/secondary role. Exact client2.5.6.4.
See [actual result](../2026-10-16-texture-recovery-result.md).
This extends MESH-EXPORT-001, not a new graphics hook or GPU readback.

## Pre-implementation relationship checkpoint (2026-10-16)

Static instruction evidence in the exact-build dump under
`artifacts/pre-m0/raw/StarFleetOP-2.5.6.4.dumpbin-disasm.txt`:

- 0x0042F617–0x0042F647: visual+0x158 is the 36-byte source table;
  source+0x18 is an offset into visual+0x154's STRS bytes. The loader resolves
  that string and writes its returned resource ID to source+0x14.
- 0x0042F65F–0x0042F68B: flag 0x20 enables the second relationship,
  source+0x20 string offset -> source+0x1C resource ID. Neither ID is a pointer.
- 0x004301BD loads STRS; 0x004301E9 loads MATS; 0x00430149 copies the
  model filename into visual+0x14. 0x0042F756 tries BMP then PCX; constants
  0x0083EB78/74 are `bmp`/`pcx`. Do not infer filenames from ship appearance.
- Global 0x008CC620 points to the resource registry (vtable 0x00795C54).
  0x0040EEDD searches 4096 entries of 20 bytes starting at registry+4;
  entry+8 holds a resource object. It compares resource+8 to the requested
  filename (0x0040EEF2–0x0040EEFF), returns index+1, and reuses that ID.
  0x006A07D0 independently compares that same inline filename; 0x006A0920
  returns the live resource object for an ID. These corroborate filename identity.
- 0x006A8860 checks ID-1 <4096, reads manager+0x3F60+4*(ID-1), and binds
  entry+4 at device slot+0x98. 0x006AC0E2/F2 reads the two source IDs;
  0x006AC505/522 selects submission arguments. Manager vtable
  0x007B8D4C slot+0x184 resolves to 0x006AB410.
- 0x006AC130–0x006AC168 checks manager+0x1ED0 and source flag1 before
  retaining either ID. Snapshot/recheck that enable byte; a disabled or
  unqualified value cannot establish an actively textured primary assignment.

Historical preparation checkpoint: CONFIRMED static relationships. At that time runtime
readability and actual image assignments remain STRONG HYPOTHESIS pending a
fresh capture. A secondary pass is supported; **glow/emission and alpha roles
are not yet proven**, and no filename suffix alone authorizes emission.

## Safe observation / execution contract

Question: can each selected source group be joined to the *live registry's*
filename in the same epoch as the portable mesh packet?

Default-off `EnableTextureReferences` requires exclusive read-only mesh mode.
Use the existing validated primary wrapper recorder; no added hook, engine
function calls, COM calls, writes, allocations, disk access or image decoding
on the render thread. Copy bounded printable strings and registry identity into
fixed storage after successful mesh capture; re-read registry/source identities
and reject changes. At most one association attempt; failure preserves the mesh
and produces PARTIAL, never retargets or reuses previous-run IDs.

Toolchain: VS2026 Community18.7.3/MSVC14.51 x86 C++17; PowerShell7.6.5;
Python3.12.14/Pillow12.3.0. Build `tools/m1_component/build_m1_component.ps1`.
Launch prepared `tools/m1_component/start_texture_export_session.ps1` from the
existing elevated parent shell. PS5 entry hands off to bundled PS7; process-only
execution-policy bypass, no security changes or routine extra UAC prompts.

Fixture: usual two-ship skirmish, initially both visible; normal play. Automatic
0x004162B9 tactical gate; 90s maximum, then two exit cues: exit normally.
Mesh limits/cleanup/hash checks from MESH-EXPORT-001 remain unchanged.
Diagnostic geometry hook OFF; 120 detailed frames/10000 events, log16MiB warning/
32MiB stop; summary counters thereafter. Associations: <=10 unique resources,
<=256 source groups, strings <=255 printable ASCII characters, fixed reference storage
<8KiB, JSON <=512KiB, written only after recorder drain/hook restoration.
This mechanism cannot generate multi-GB output; do not substitute unbounded API
tracing. Original+derived images <=128MiB total/warn64MiB; dimensions <=4096².
Limits cause documented PARTIAL. No per-frame image dumps.

Expected outputs: existing run directory plus `TEXTURE-EXPORT-001.json`,
and a separate `textured/` derivative/association manifest produced offline.
Expected normal images: ten small source images plus lossless PNG derivatives;
volume measured after capture, not presumed. No reference/original overwrites.
Offline analysis verifies packet checksum/receipt, same-epoch IDs/source words,
registry filenames, hashes, image decoding and untouched OBJ geometry/UVs.
Only unique exact relative paths beneath the installed game Assets directory are
accepted; ambiguous/missing files remain unresolved. No substitute images.

Cleanup: existing runner removes its owned proxy/config after normal exit and
checks client hash. Keep original packets/assets and grey preview. Archive useful
run evidence after review; generated images/binaries stay ignored. Do not delete
game assets, shared caches or unrelated files. Preview uses existing process-local
NRC-off settings and bounded owned process runner. Visual fidelity/any glow role
requires separate evidence and sponsor comparison; offline preparation is not PASS.

## Actual execution — 2026-10-16

Run20261016-010112-enabled completed90s normally; sponsor reported no issues.
One snapshot, five groups/ten256² BMP originals,1177434 original+PNG bytes;
status1/native identity checks passed. Primary images imported/rendered in separate
bounded Remix jobs;452triangle geometry/UV/group comparison passed. Runtime
CSV339469bytes, all-stage images2829304bytes. No cap warning/overflow, multi-GB
trace, game modification, new wrapper or geometry hot hook. Raw/caches not deleted;
useful evidence archived per linked result. Secondary roles remain unproven.
