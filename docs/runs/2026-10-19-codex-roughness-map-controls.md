# Run59 — optional texture-derived roughness controls

Date2026-10-19 America/New_York. Sponsor asks to expose discussed material
controls. Starting HEAD357bc703e3dc0923cd4c7801ec87e99abc01f157,
codex/github-sanitized tracking private origin/master. Run57/58 and sponsor's
appearance tuning already unstaged/uncommitted. No staging/commit/push authorized.
Fuel Guard attached existing hook;no daemon/helper. No SFC session active at
initial process check;none launched by this work.

## Baseline / authority / technical question

Read HANDOFF, Run58, approved M1 disposition, existing material relay/host and
pinned SDK. Separate additive rendering work;no original suppression, gameplay,
CDD/REQ or milestone gate changes. User screenshots and roughness observations
suggest a material-lighting interaction, NOT proven texture loss or its cause.
No screenshot/chat desktop content copied into version control.

Can we expose independent reflection strength or another actually supported
surface adjustment without misleading controls or source-asset changes?

CONFIRMED static: pinned SDK opaque material has no independent specular strength
or reflectivity field. roughnessTexture is present. Thin film, metallic,
translucent IoR and ray-sampling probabilities rejected as falsely equivalent
substitutes. Public pinned material implementation consulted read-only:
https://raw.githubusercontent.com/NVIDIAGameWorks/dxvk-remix/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_materials.h
Local pinned header remains authoritative for this ABI.

Implemented optional texture-derived roughness instead. Default OFF preserves
current sponsor roughness0.2,illumination5,metallic0,anisotropy0. Existing lights,
image and quality tuning untouched. No claim independent specular was delivered.

## Implementation / files

New tools/remix_runtime/roughness_maps.py:worker-only encoded-luminance levels,
gamma,inversion,strength blend,immutable derivative DDS,provenance hashes/dimensions.
Source files unchanged. Six new controls in config/materials.toml,comments explain
approximation,restore and missing specular field. Header/material binding uses
SDK roughnessTexture;uniform scalar remains fallback. Material packet56bytes v2
reuses formerly reserved floats;native reader retains strict v1 compatibility.
Finite/range/boolean/white>black checks and float32-level distinction guard.

Modified tools/remix_runtime/{material_controls.py,remix_material_controls.h,
ship_textured_asset.h,ship_live_host.cpp,live_return.py,qualify_live_return.py,
build_live_return.ps1,config/materials.toml,config/README.md};
tests/{test_material_controls.py,remix_material_control_tests.cpp}.
New tests/test_roughness_maps.py;this run record;
docs/reconnaissance/probes/REMIX-ROUGHNESS-MAP-001.md;HANDOFF update.
New tools/remix_runtime/{archive_fixture_textures.ps1,qualify_material_pipeline.py}
keep required source-matched regression rerun within existing10GB budget,without
deleting original assets or losing recoverable fixture derivatives.

## Reproduction / bounds

VS2026 C++20 x86/x64 through bundled pwsh:
`tools/remix_runtime/build_live_return.ps1`.
Bundled Python/Pillow12.3.0/NumPy2.3.5:
`-m unittest discover -s tests` with TEMP/TMP=artifacts/readme-validation-temp.
`tools/remix_runtime/qualify_live_return.py --execute --material-controls`.
`tools/remix_runtime/qualify_material_pipeline.py` repeats14 return gates and
revalidates unchanged source/executable-matched Run58 image/quality pixel proofs.
It does NOT relabel old whole-host proofs as current or launch SFC.

Probe REMIX-ROUGHNESS-MAP-001 documents all triggers,tools,limits and cleanup.
Existing60s/32MiB fixture,75s/32MiB pixel probes,128MiB combined images,
4096-square dimensions,256material edits. Derivative about4*w*h bytes per image
per revision;never per-frame image generation.128-row float strips bound working
memory. At128MiB output saturation retains last good. No callback waits/IO.
Config16KiB,existing500ms polling/16snapshots/100messages retained.

Initial retained runtime evidence9,478,432,460B/10GB. Per-fixture compression
stores generated textures in an external-to-Git ignored archive, fully
decompresses and SHA-verifies EVERY entry against originals before exact native
PowerShell deletion of only generated textures. Logs/manifests/packets remain;
texture-archive.json records ZIP hash/bytes and recoverability. No original game,
reference source or captured packet removed. Initial targeted fixture
20261019-052028-390253-live-private passed,then82,302,266B generated derivatives
recoverably compacted into6,372,788B ZIP,SHA256
044347317F74DDE2AB2726F819AF18F3F4FBB3E0E6BF9CF2C505243F902FDC59.

## Validation / adjudication

Initial275Python tests PASS;native material v1/v2 parser20checks each x86/x64
PASS,existing quality14/image22/request89/UV14/light25checks each architecture
PASS. Actual pinned SDK accepts enabled map,continues full-resolution output,
rejects invalid edit and restores uniform roughness:3accepted/1rejected,
fixture_exit0,failed0,API shutdown0. Existing SDK40device-object warning persists.
No image-quality improvement or washout fix is yet claimed from API acceptance.

Final source-matched qualification:all14return gates PASS,refreshed receipt
artifacts/remix-runtime/deps/live-return-qualification.json. Unchanged independent
Run58 image17cases/quality10cases revalidated against their own exact source and
executable hashes;not needlessly rerun or relabelled as new pixel observations.
Exact paths/results in
[curated evidence](../reconnaissance/evidence/20261019-roughness-map-controls.json).
Final275Python tests PASS4.773s;native build exits0;PowerShell parser/local paths
and git diff --check PASS. Only normal LF/CRLF Git notices. Read-only
run_return_game.py --light-tuning preflight PASS;no game/renderer started.
No active SFC/host/fixture/probe left at final process check.

Final material fixture20261019-052703-695898-live-private:33.531seconds,56map
images,82,302,266Bcombined image output (64MiB warning recorded),3accepted edits,
1invalid rejected,map0→1→0,fixture_exit0,failed0,API shutdown0.
This confirms SDK binding/reload/output,not artistic usefulness or washout cause.

Nine new matrix texture ZIPs48,042,348Breplace576,004,170Bgenerated copies.
Also compacted exact completed historical private fixtures
20261019-003942-434249,004004-667321,004028-261005 (all suffix-live-private)
to restore room for the normal tuning runner's384MiB reservation. Each46,367,290B
generated set replaced by4,730,177BZIP. Receipts include exact archive hashes;
all files fully decompressed/hash-verified before native deletion,fully recoverable.
Final retained evidence9,537,199,254B/10GB;384MiB next-run reservation PASS.
No original/reference assets or useful logs/manifests/packets removed.

Final Git:HEAD357bc70unchanged,all prior work and this increment UNSTAGED and
UNCOMMITTED,nothing pushed. Source-matched launcher is ready for optional sponsor
comparison;no milestone advancement. Existing sponsor light/image/quality files
not edited in this run. Their final SHA256 respectively:
2CAF223FD32F29BE88D052C7A4132EA0FF7D68E6290394D45350B20BF27A345D,
3BEC592A9D279259607F41CF7D6CA44E4E40703018DDF39465E41057D2F79AA1,
89FD0A280ACF3D80194A274E3B33BD72CBF29E3D9ED53D453FC45DC4EC526D40.
Both SFC client hashes checked unchanged:
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.

## Remaining limitation / next action

Independent specular strength requires a genuinely supported API/renderer change,
not a hidden metallic workaround. Generated roughness is artistic approximation;
brightness does not prove paint roughness. Visual benefit and cause of previous
washout remain unresolved. No normal/specular/clearcoat maps invented.
After offline qualification,sponsor may use existing light-tuning launcher,save
roughness_map_enabled=true and compare at strength0.25 with fixed camera;disable
to restore uniform surface. Do not reset tuning or start appearance archaeology.
