# Run86 — remove expensive per-load texture pixel verification

Local2026-10-20 America/New_York;UTC artifact folders20261021. M1 CONTINUES.
Sponsor instruction:annotate and fix texture verification,next issue flickering.
Read HANDOFF/Run85 and relevant implementation/tests. Fuel Guard trusted-hook
receipt attached,no sandbox daemon. HEADd29111f7,index empty,existing dirty work
preserved. No helper/agents/gameplay/SDK or rendering-architecture changes.

## Decision and implementation

SFC already uses original source images;revalidating their appearance per load is
not necessary. Our DDS conversion still needs correctness coverage,but its complete
pixel readback belongs in offline regression tests,not the game preparation path.
This supersedes Run85's proposed runtime bulk pixel comparison. Sponsor explicitly
authorized this narrower runtime policy;requirements and appearance unchanged.

material_binding.py now encodes the same RGBA DDS bytes without reopening/decoding
the saved DDS or comparing every pixel. Cheap checks enforce dimensions1..4096,
RGBA input,exact128+width*height*4byte output,expected DDS header,size,pitch,
uncompressed32-bit BGRA masks,single surface/no unsupported fields. Original source
association/upload checks,hashes,128MiB cumulative cap and64MiB warning remain.
Manifest annotates header/bounds-only validation with offline pixel roundtrip.
No change to mesh,UVs,orientation,lighting,materials,texture content or Pillow install.

## Validation and performance

Bundled Python commands:

```powershell
python -m unittest discover -s tests -p test_normal_material_binding.py
python tools/d3d9_proof/profile_preparation.py --execute --timing-only --samples 2
python -m unittest discover -s tests -p "test_*.py"
git diff --check
```

11material tests PASS,364totalPython tests PASS. New coverage:small asymmetric
RGBA offline DDS encode/decode exact equality and unchanged encoder bytes,runtime
encode cannot reopen images,wrong modes/dimensions/truncation/trailing bytes,
changed dimensions and each of32DDS header words rejected. Existing suite emits
Pillow getdata deprecation warnings;no failures. Native unchanged/not rebuilt.

Same Run84 fresh FCA source/identity/settings as Run85,unprofiled offline:

- Before025857-973940:geometry0.247860s,extent0.020182s,materials16.401657s;
  total16.669700s.
- After030338-715972:geometry0.238832s,extent0.019045s,materials1.096771s;
  total1.354648s.
- After030342-849559:geometry0.227803s,extent0.019025s,materials0.983236s;
  total1.230063s.

All folders under artifacts/d3d9-proof/material-runs/20261021-<suffix>.
Both after manifests match before exactly for image hashes/dimensions/bytes,group
assignments,material values/config hash,USD hash,total image bytes. CONFIRMED:
removed readback eliminates~15.3s of offline material preparation without changing
generated content. Not a new full-workflow/gameplay startup measurement,not a
cold-boot benchmark,and not a claim all remaining initial-display delay is gone.

Existing helper archived and decompressed-hash-verified76,648,704B generated copies
per after sample before exact-file removal. Adjacent -generated.zip and
generated-archive.json retain recoverability;source packets/manifests/logs retained.
Aggregate9,799,270,644B/10GB,no budget increase. No installation files removed.
Original/copied StarFleetOP.exe SHA256 unchanged:
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.

## Final state / next action

Files:tools/d3d9_proof/material_binding.py,tests/test_normal_material_binding.py,
this record,HANDOFF. Git diff --check PASS,index empty,all implementation/evidence
unstaged/uncommitted. No active game/renderer/session,no commits/push. Existing
launcher qualification stale;no new launcher issued. Frame-delivery flicker is
unchanged and independent. No stale-output hold,buffering or replacement introduced.
Exact next action:investigate Run84 frame-delivery tails and stale-output rejection
offline before choosing a correction or asking sponsor for another gameplay test.
