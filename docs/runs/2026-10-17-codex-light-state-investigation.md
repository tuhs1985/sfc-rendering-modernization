# Codex run — native light-state investigation

Run SFC-RETURN-20261017-18,2026-10-17. Sponsor requests locating game lights
while away;static investigation only,no gameplay or new rendering implementation.
Active approved return-path work,not milestone completion. Starting HEAD e96765a,
indexempty,prior dirty/untracked implementation/evidence preserved. FuelGuard
attached current thread via trusted recent-hook receipt;no daemon/helper/delegation.

## Question / baseline / sources

Where are the light inputs used by SFC's proven semantic render-owner path?
Read HANDOFF/Run17,existing RT-010/shading analysis,corner-transform qualification,
input-gap assessment,secondary-image role/material review,active-camera map,
M0 manager vtable evidence. Existing lighting interventions prove visible native
response,not actual scene light parameters. Exact retained dumpbin is starting
source;no broad new disassembly or unrelated engine reconstruction.

## Result / confidence

CONFIRMED static:manager64×64byte light bank at+778,enable bytes+1778,setter
006A9AB0/getter006A9BA0/enable006A9C40,derived light triples+17B8/+1AB8,
reciprocal+1DB8,global gate+1EB8. Object-transform setter006AA550 derives local
light coordinates consumed by already-known shading routine006A9790.
Recovered native type0 directional-like and type1 point-like arithmetic;type5
special positional response remains unnamed. Type0/1 physical interpretation is
STRONG HYPOTHESIS;branch arithmetic/table routing CONFIRMED static. No live
lights sampled. Type numbers are NOT DirectX light enums. Record+28 is not one
universal intensity. Actual mission sun/main source,ambient,color space,intensity,
light lifecycle and scene-populating caller remain unproven.

Material finding:first inactive slot terminates the response loop at006A97E4,
whereas transform preparation skips inactive slots. Future capture must preserve
enables and consumed prefix,not assume all enabled slots contribute. This narrow
result is enough to specify the next light-value observation without more caller
enumeration. A few generic virtual-call examples were rejected as unrelated
object traversal/DirectDraw COM;no manager-caller conclusion from slot equality.

Detailed map/addresses/interpretation/remaining questions:
[native light state](../reconnaissance/2026-10-17-native-light-state-map.md).

## Tools / material commands / evidence

Bundled Python3.12.14,existing extract_disasm_ranges.py,read-only inspect_pe.py,
PowerShell/rg. Selected windows006A9790..9C59,006AA550..68D,reverse-vector/point
helpers0069CBC0/CC40,plus a few rejected potential callers. No mass renaming,
patching,injection,wrappers or generated disassembly written. Existing70MB bulk
disassembly remains ignored. Terminal truncation led to smaller selected windows;
first attempted composed inspection call had a JavaScript quoting syntax error
before execution,then corrected. Missing guessed glob/catalog paths were not
treated as absence of evidence. Nothing modified in reference originals.

New tool tools/m1_component/verify_light_state_bytes.py reuses exact client-hash,
PE bounds and byte verifier;41selected code/vtable/jump-table anchors match
independently. It opens no process. Default stdout;--output creates a NEW file
only,never overwrites. Input cap64MiB inherited;output41small rows (<16KiB).

```text
python tools/recon/extract_disasm_ranges.py artifacts/pre-m0/raw/StarFleetOP-2.5.6.4.dumpbin-disasm.txt 0x006A9AA0:0x006A9C65 0x006A97FD:0x006A9858
python tools/m1_component/verify_light_state_bytes.py "C:\Games\Taldren Software Inc\Starfleet Command Orion Pirates\StarFleetOP.exe" --output artifacts/remix-runtime/light-state-static-20261017.json
python -m unittest discover -s tests -p test_*.py
python tools/remix_runtime/run_return_game.py --depth-snapshots --observation-only --calibration
git diff --check
```

TEMP/TMP artifacts/test-temp for tests.41STATIC_PREFIXES_MATCH;173Python tests
PASS2.936s,including restoration of ordinary verifier anchor set on success/failure
and unsupported-client rejection without writes. Static JSON ignored/generated,
curated address interpretation versionable in map. No new raw capture/archive
needed;reuses existing disassembly. Fast final preflight checks existing prepared
calibration qualification,does NOT launch game without --execute.

## Changes / final repository state

Added tools/m1_component/verify_light_state_bytes.py,tests/test_light_state_bytes.py,
docs/reconnaissance/2026-10-17-native-light-state-map.md,this record.
Modified docs/HANDOFF.md only to retain this result and existing next action.
Generated artifacts/remix-runtime/light-state-static-20261017.json ignored.
No capture/component/runner/build/configuration changes;Run17 qualifications stay
valid. Both client hashes unchanged;no game/renderer/controller session started.
HEAD e96765a,indexempty,prior dirty work plus these unstaged/untracked files;
nothing staged/committed. Known native67/SDK40cleanup warnings unchanged.

No blocker requiring sponsor input while away. A future default-off bounded light
snapshot needs its own documented probe before use,not guessed live lighting.
**Exact next action:**perform already prepared -Calibration run when sponsor
returns;do not mix new lighting fields into its offline-qualified binary.
