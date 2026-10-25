# OFFLINE-RENDER-INVENTORY-001 — targeted executable inventory

Sponsor authorized2026-10-25 following Run172's RTTI identifications. No game,
GPU renderer, hook, injected code, asset-file reads or client writes. API parked.

Inputs:hash-verified2.5.6.4client, existing frozen dumpbin disassembly and optional
explicit Run172 native review/raw trace pairs. Script validates runtime trace
SHA against its prior review; every indexed/reported instruction matches actual
PE bytes. Reconstruct wrapped dumpbin continuation bytes before CFG traversal.

Scope:explicit rendering-related type families only. Find TypeDescriptors, qualify
MSVC x86 complete-object locators/base hierarchies/vtable executable entries.
Reject incidental networking/Flight strings containing "light". Preserve secondary
vtable offsets and non-render/unknown method roles. No generic engine scrape.

Bounded effects graph:37derived primary slot+4candidates; exclude shared Base
stub from effects code-window selection. Max128selected classes/128methods per
vtable/32direct functions pergraph/4096instructions perfunction/64KiBfunction span/
direct call depth2/150000indexed effects instructions. Indirect calls are records,
not guessed targets. Candidate texture bindings retain unresolved receiver/index
range. Direct literal acquisitions require exact registry receiver, last pushed
literal; an associated result slot additionally requires an unclobbered return-value store. Do not mistake a formatting string
or nearby literal for the acquired file. No dynamic branch/UV-origin claim.

Output8MiBmax; refuses to overwrite prior output. Versionable metadata contains
names/addresses/provenance/references, not proprietary PE/disassembly/image bytes.
Full generated inventory ignored; original inputs unchanged. No new large evidence
or deletion; existing20GBaggregate remains. Optional raw capture reads stay within
the existing metadata wire and do not request excluded resource contents.

Reproduce from repository root using bundled Python:

```powershell
python -B tools/recon/inventory_render_types.py --client "C:\Project\SFC-Remix-Return-Test\StarFleetOP.exe" --disassembly artifacts/pre-m0/raw/StarFleetOP-2.5.6.4.dumpbin-disasm.txt --runtime-run artifacts/remix-runtime/runs/20261025-141338-349874-in-game --runtime-run artifacts/remix-runtime/runs/20261025-141645-535316-in-game --output artifacts/render-survey/offline-render-inventory-new.json
```

Omit both `--runtime-run` options for a purely static inventory. Existing binary
and disassembly are local prerequisites, not distributed assets. Do not run a
different game build or silently substitute an unverified disassembly. No native
build or sponsor gameplay action required.

Tests cover selection false positives, namespace filtering, RTTI/self/base checks,
executable method pointers, malformed/stale disassembly, wrapped instruction
length/fallthrough, unresolved indirect jumps, explicit call-depth limit and
false filename/indexed-binding associations. Keep CONFIRMED/static relationships,
runtime membership, STRONG HYPOTHESIS/role interpretations and remaining unknowns
separate. No milestone or universal renderer coverage inferred.
