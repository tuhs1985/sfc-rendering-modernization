# Run173 — offline executable rendering inventory

Date:2026-10-25 America/New_York. Sponsor authorized targeted executable
characterization following Run172. Current SFC-15; API remains PARKED. No game,
GPU renderer, hook, native build, assets or settings changed. No milestone claim.

## Result and provenance

[Canonical inventory](../reconnaissance/rendering-executable-inventory.md),
[curated versionable evidence](../reconnaissance/evidence/20261025-offline-render-inventory.json),
[reproducible probe](../reconnaissance/probes/OFFLINE-RENDER-INVENTORY-001.md).

Pinned copied client SHA256:
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
Read existing70,181,824-byte dumpbin disassembly; each indexed/reported instruction
is checked against PE bytes. No binary/disassembly bytes copied into documentation.
Optional runtime inputs are the two existing Run172 broad.bin/native review pairs:
20261025-141338-349874-in-game and20261025-141645-535316-in-game. Their raw hashes
are rechecked against the reviews; original evidence is unchanged.

Authoritative generated output:
`artifacts/render-survey/offline-render-inventory-20261025-final.json`, SHA256
`7DCF78AC5F59962EFD43E93A1B0435E1B8BE20C8B2A1C325F3AFDFD11E5286A3`.
Earlier preliminary files in that folder are historical, not authoritative.

64qualified classes/65vtables/908virtual-method entries, not908distinct render
functions.38effects includes37derived classes plus base; remaining categories:
4attached traits/creators,2light creators,5semantic-model types,6sprite/UI,
8tactical camera/manager types,1dust-cloud entity. Ten derived effects have actual
Run172 list-membership evidence;27are static possibilities, not gameplay coverage.
37bounded draw graphs,40,486byte-verified indexed instructions,41literal registry
acquisition sites/38distinct filename literals. All21observed native light-call
return sites match byte-verified original operations.

## Useful findings / limits

- Phaser has an fx1-or-untextured branch and native quad path. Its exact width,
  UV and branch-state contract is still to extract.
- Photon requests photons-2.bmp. Plasma initializes seven named images and selects
  through owner+3C; indexed variant bounds/current value remain unproved. Core and
  auxiliary plasma drawing must remain distinct.
- Organian requests Organian.bmp. This supersedes the tentative artwork-based
  fx4=Organian suggestion; examined Hellbore paths reference fx4 instead.
- Atlas references are shared and branch-dependent. No image placement, successful
  live file load or exclusive pixel owner is inferred from a static filename.
- Scene slot0/1 setup and effects-pass overrides explain rapid native light state
  changes. Global lighting-response gates are not physical lights being born or
  destroyed. Exact temporary weapon-light ownership/physical conversion remain open.
- Class names do not inventory every UI/background function. Indirect calls,
  external helpers, runtime branches and unobserved attached paths remain partial.
  Phaser helper004F24DF is explicitly beyond the configured direct-call depth.

## Implementation and failed attempts retained

New offline-only tools/recon/inventory_render_types.py qualifies MSVC x86 RTTI,
base chains and executable vtables; follows bounded direct effects paths; records
resource references and exact observed light callers. New
tools/recon/tests/test_render_inventory.py adds15tests. Output refuses overwrite;
8MiBmax,128classes/128methods,32functions pergraph,4096instructions/function,
64KiBspan/depth2; no guessed indirect targets or render-thread work.

Initial range selection included the abstract base's shared00401038stub and hit
the150000instruction cap. Excluded that stub from range selection without raising
the cap or removing its metadata. Corrected dumpbin continuation-byte parsing,
false literal-acquisition candidates and a local survey import path. Added negative
tests; intermediate outputs retained. A synthetic test pointer needed the same
6–8digit representation as the actual disassembly. These were offline tooling
issues, not game/renderer failures.

## Files and repository discipline

New: inventory tool/test, canonical inventory, probe, curated JSON and this run.
Updated: docs/HANDOFF.md, docs/STATUS.md and rendering-family-map.md.
All prior Run163–172 uncommitted work preserved. HEADfd79ce5; index empty;
all changes unstaged/uncommitted, no push. Source assets, client, renderer/survey
binaries, configuration and runtime qualification unchanged. No cleanup/deletion;
small metadata outputs only, existing20GBaggregate cap retained. No owned runtime
process/channel or restart-dependent session. Fuel Guard existing hook attached;
no helper or agents used.

## Validation

- 27recon tests PASS0.014s, including15new inventory cases.
- 13survey parser tests PASS0.693s.
- 504existing Python regressions PASS9.684s. Existing Pillow deprecation warnings
  remain; intentional invalid-config rejection tests behaved as expected.
- Survey and normal multi-ship Performance read-only preflights PASS. No game or
  renderer started. Existing survey source/build lock remains qualified.
- Independent rerun to offline-render-inventory-20261025-recheck.json produces
  exactly the same SHA256 as the authoritative final inventory.
- Source AST, curated JSON, referenced paths and git diff --check checked at
  closeout. No native/GPU runtime requalification needed because no runtime
  component changed. Obsidian tracker differences reviewed as Run173-only, then
  synchronized with a concurrent-edit SHA guard and byte-identity check.

**Exact next action:** extract byte-backed phaser/plasma UV, width, drawing-state
and variant rules into a small renderer-neutral transient-primitive contract
proposal, comparing existing capture values. No new rendering implementation or
gameplay run unless a specific remaining live association requires one.

## Sponsor-authorized publication closeout — 2026-10-25

Sponsor subsequently requested notes, commit and push. Related Run163–173 pending
work reviewed as one coherent source/documentation checkpoint; original uncommitted
status above is historical. Publication set contains only Markdown, JSON, Python,
PowerShell and C++ source/headers (approximately1.2MB). No proprietary binaries,
images, desktop screenshots, raw captures, generated build output or credentials
included. Existing exclusion rules retained; credential-pattern scan had no matches.

Fresh checks:504existing +27recon +13survey +6effect-probe +5API packet tests =
555PASS; Python AST/JSON checks PASS. API remains parked; tests are not new GPU
or gameplay claims. Remote master verified atd40f8f2, an ancestor of current
fd79ce5, so normal fast-forward publication includes the existing two local
commits as well as this checkpoint; no history rewrite or force push. Commit and
push completion must be verified from Git, not assumed from this pre-commit note.
