---
title: SFC Modernization — Status Tracker
updated: 2026-11-12
checkpoint: Rapid-pan correction enabled for pinned Remix and qualified through standalone target recreation. Alpha ZIP unchanged.
tags:
  - sfc-modernization
  - project-status
---

# SFC Modernization — Status Tracker

## November 12 — rapid camera pans

The Bird-of-Prey replay showed that Remix colour could follow the previous
camera pose while the hull mask and depth already followed the current pose.
Frame markers verified that the post-Present copy reads the previous image with
the default swap chain. The sponsor reproduced the patches during fast slews
and zooms in and out on the unchanged alpha. With the session-local correction
enabled in the development copy, the sponsor reported that it seemed to work.
The pinned adapter now uses that setting by default. Standalone checks passed
for the initial output, resize and device recreation. Packaged gameplay is pending.
[Replay and evidence](runs/2026-11-12-codex-rapid-pan-colour-lag.md).

## Committed alpha tester ZIP

The package built from `4d41a31` passed local extraction, preflight,
graphics setup and restoration. The existing test copy has been updated.
Next verify gameplay and restoration on a tester's PC.
[Build and qualification record](releases/DEPENDENCY_CLOSURE.md#committed-alpha-tester-zip).

## November 11 — tester-owned SFC and dgVoodoo settings

The updated private ZIP checks graphics compatibility and leaves the tester's
settings in place. The installed GPU, preflight, and restore checks preserved
all three config files. The sponsor confirmed revised-package gameplay.
Clean-machine and hybrid-GPU qualification remain open.
[Evidence](releases/DEPENDENCY_CLOSURE.md#tester-owned-game-and-wrapper-settings).

## November 11 — tester ReShade preferences

The sponsor confirmed the private ZIP worked in a separate SFC copy. The
revised ZIP preserves the original ReShade INI through first-run preparation,
session configuration generation and restoration. Gameplay of the revised
ZIP is open.
[Evidence](releases/DEPENDENCY_CLOSURE.md#tester-reshade-configuration).

## November 11 — private ZIP extraction verified

The allowlisted ZIP passed fresh extraction, first-run setup, preflight and
restoration on this workstation. Enhanced gameplay from that ZIP is the next
checkout. [ZIP evidence](releases/DEPENDENCY_CLOSURE.md#exact-zip-extraction-checkout).

## November 11 — reversible first-run graphics setup

The private package passed GPU matching, setup preview, declined and approved
preparation, and restoration on this workstation. The sponsor confirmed the
normal CMD launcher worked in gameplay, and preflight passed after exit.
Rapid camera panning reproduced the earlier gray-wing issue. Ship and mask
synchronization remains a hypothesis.
[Verification record](runs/2026-11-11-codex-reversible-graphics-setup.md).

## November 11 — setup-time GPU matching verified

The pinned Remix and dgVoodoo device probes reported the same LUID using the
existing setting. The candidate config was byte-identical to the input.
769 regressions passed. Reversible launcher preparation and hybrid gameplay
qualification remain open.
[Verification record](runs/2026-11-11-codex-graphics-adapter-matching.md).

## November 11 — standard ReShade x86 source verified

Both official endpoints supplied the same standard 6.7.1 installer. Its
embedded 6.7.1.2133 x86 DLL matches the pinned baseline hash. The
[download, extraction and hash procedure](releases/GRAPHICS_BASELINE_AUDIT.md#verified-source-for-the-standard-reshade-x86-dll)
is verified. Reversible preparation and clean-machine checkout remain open.

## November 11 — portable graphics candidate

Cache-only ReShade comparison preserved the generated profile and all 128
appearance inputs. Both dgVoodoo policies matched Remix's adapter on the
single-physical-GPU workstation. The sponsor completed the private cache-only checkout.
Hybrid selection, standard ReShade sourcing, reversible setup and clean-machine
qualification remain open.
[Evidence and checkout command](runs/2026-11-11-codex-portable-graphics-profile.md).

## November 11 — tester graphics preflight verified

The reorganization merged as `e324e5c`. Installed `--preflight` now lists
graphics mismatches together. 765 regressions passed, and the packaged launcher
reported five simultaneous issues without changing any files. The qualified
profile still passes. Portable preparation, rollback and clean-machine gameplay
are the next gates. [Test record](runs/2026-11-11-codex-tester-graphics-preflight.md).

## November 10 — main source reorganization implemented

Scene receipt, shared data, buffer ownership and shutdown now live under
`src/transport`. Renderer startup, backend selection and process lifecycle live
under `src/rendering`. Calibration, detailed renderer reports and runtime
acquisition remain in development tools. The private package ships 62 project
Python modules.

Fresh-package scene and catalog acknowledgements, payload lifetime and shutdown
passed. 764 Python regressions and both 600-frame native GPU policies passed.
The sponsor reports the gameplay checkout complete under
`artifacts/alpha/renderer-transport-game` and requests the commit.
[Verification and launch command](runs/2026-11-10-codex-transport-renderer-separation.md).

## November 10 — asset preparation and renderer/transfer review complete

Parent `7ae2c35`. Application preparation now lives in `src/assets`; capture
review/comparisons stay in developer tools. Neutral decoder separated from
transport; 61 shipped Python modules. 764 regressions, four review tests,
standalone workers/GPU, package/import and actual CPU material checks pass.
Renderer, settings, scheduling and loading order unchanged.

New private checkout: `artifacts/alpha/asset-preparation-game`, root
`SFCRemix-Launch.cmd`, recording off. Sponsor checkout complete; commit requested. [Evidence and command](runs/2026-11-10-codex-asset-preparation-separation.md).
[Renderer/transfer review](reconnaissance/2026-11-10-renderer-transfer-ownership.md)
recommends scene receipt/input transport as the next contained separation, then
normal renderer orchestration. No transfer redesign. Visible startup stages and
tester graphics preparation remain parked.

## November 10 — shared runtime support gameplay accepted

Moved six functional helpers into `src/runtime`, preserving developer entry
points and keeping 60 shipped Python modules. Fixed an interrupted-recovery-only
dependency on the excluded broad-capture module using the existing transaction
helper. Rendering, settings and timing unchanged. 761 regressions, actual file
recovery/restore, immediate relaunch fixture/preflights, native workers, both GPU
policies, installed import guard and CPU/GPU checks pass.

New private gameplay copy: `artifacts/alpha/runtime-support-game`, root
`SFCRemix-Launch.cmd`. Sponsor reports it looks good. Visible original → base
replacement → enhanced materials sequence completes within roughly three seconds
by observation, not a measured timing. No loading changes made. Previous accepted
copy is preserved. Sponsor requests this accepted increment be committed; no push.
Tester preparation remains
parked. [Evidence and command](runs/2026-11-10-codex-runtime-support-separation.md).

**Parked follow-up, requested November 10:** investigate why the startup stages
remain visibly separated. Reopen when reviewing startup performance after this
organization increment. First correlate existing capture/base-ready, first
replacement presentation, enhancement publication/consumption and presentation
timing before choosing a change. No cause or regression is established by the
approximately three-second visual observation. Recorded in Obsidian Parking Lot
as "Visible original/base/enhanced startup transitions"; distinct from SFC-23's
historical first-launch Defender stall. No new capture or loader change now.

## November 9 — diagnostic separation gameplay accepted

Committed prior acceptance as `4a0ce1e`, then separated normal native play from
optional capture/test/tuning orchestration. Startup, fallback, recovery and cleanup
remain shared application behavior. Sponsor confirms the new checkout passes
and requests its commit; no push requested.
758 regressions, existing command preflights, Strict/ExtraFrame GPU fixtures,
actual light-worker tests, guarded installed imports, CPU material preparation,
portable-path checks and installed GPU output/cancellation pass.

New private playable copy: `artifacts/alpha/diagnostic-split-game`; launch root
`SFCRemix-Launch.cmd`. Recording off, accepted appearance preserved. Sponsor
accepts this refactor as passing; previous organized
checkout is preserved. [Ownership, evidence and launch command](runs/2026-11-09-codex-session-diagnostic-separation.md).
Tester graphics preparation remains parked until repository organization finishes.

## Current priority — finish repository organization

**Latest verified result, November 9:** sponsor accepts the reorganized build's
gameplay checkout after approximately six minutes of stable play, with damage,
ship destruction and lights behaving correctly. This completes the hands-on
regression check for the two source separations. Normal recording was off;
no new instrumented timing or cleanup measurement is claimed.

Sponsor parked the verified external-tester graphics preparation issue until
organization is complete. Its reopening condition and first action are recorded
in the existing Obsidian Parking Lot, entry "Portable tester graphics preparation".
Keep that work deferred; preserve the audit and current runtime checks.

## Parked finding — external tester setup gap, November 9

Verified tester's graphics-profile rejection against actual alpha code and
manifest. DLL requirements exist beyond the supported EXE: dgVoodoo x86 2.86.5
and exact original ReShade32 6.7.1.2133. Whole-file ReShade configuration pin
includes a developer-specific cache path and UI state. Eight actual disposable
validator checks confirm incidental changes are rejected; PlayerName and matched
supported dimensions are the narrow exceptions. No tester-facing preparation
command exists. Referenced ReShade preset/shaders are not checked by this gate.
[Evidence and exact baseline](releases/GRAPHICS_BASELINE_AUDIT.md).

No runtime/game/profile changes. Required follow-up: reversible, documented
game-copy graphics preparation with portable profiles and qualified dependencies;
do not bypass checks or assume a different working stack is supported.

## Current playable checkout — November 9

Session separation committed as `0df894b`, without push/merge. Rebuilt candidate
matches the accepted fixed renderer exactly. Actual 600-frame native cohort GPU
fixtures under both policies and light-worker qualification pass; source receipts
renewed through existing tools, zero mismatches. Normal development preflight
works again. No guard weakened or unrelated old diagnostic receipt renewed.

Fresh actual playable checkout: `artifacts/alpha/organized-game`, root
`SFCRemix-Launch.cmd`. It has the new source layout and current appearance;
existing alpha and accepted game untouched. Installed asset prep, package and
coordinator preflight, real profiling-off GPU output/cancellation and 21 focused
release tests pass. [Details/launch](runs/2026-11-09-codex-organized-playable-checkout.md).

Sponsor has now accepted the six-minute gameplay checkout, as recorded above.
Continue repository organization. Untimed normal play, recording off; no SFC
was launched by Codex during preparation. New stager and documentation work
remains unstaged/uncommitted. No public release/push.

## Previous — session coordinator separated, November 9

Committed the first launcher/build separation as `8e69c93`, without pushing or
merging. The next bounded source move is implemented: `src/session` now owns the
coordinator, exit monitor and reports; old developer paths forward to the same
modules. Shipped bootstrap imports the application modules directly. Python
payload remains 59 files, excluding compatibility wrappers. Diagnostic branches
remain in the coordinator for a separately scoped extraction.

All 752 regressions, canonical/legacy CLI and state checks, source-body equivalence
and actual installed preflight before/after moving the reduced package pass.
[Record](runs/2026-11-09-codex-session-coordinator-separation.md). No new SFC/GPU
run. Existing alpha and settings untouched; no playable new package yet.

Developer source preflight already had a stale native-cohort receipt for
`live_light_binding.py` before this move. Do not disable or silently refresh it.
Next: review this increment and refresh qualification through the documented path
before a newly assembled gameplay checkout. Session changes remain unstaged.

## Previous — first physical separation, November 9

Five application launcher inputs moved to `src/launcher`; development-only
release/build tools remain in `tools/release`. Updated native build, installed
Python paths, manifest/staging roles, source allowlist, ZIP rules and tests.
The production Python count remains 59. Strict native build and all 749
regressions pass, plus real bundled-launcher preflight before and after moving
a reduced package through space/Unicode paths and installed coordinator preflight.
See the [verification record](runs/2026-11-09-codex-release-tooling-separation.md).

Existing alpha/game copies and settings remain unchanged. New layout and native
launcher must ship together; this is source organization, not a new rendering
feature or public alpha. No SFC/GPU gameplay validation claimed. Unstaged and
uncommitted on `codex/organize-repository-foundation`; no push/merge/archive.

## Previous — repository foundation, November 9

The sponsor authorized a scoped work branch from pushed `fe17b8d` and application
of `organize-repository-foundation`. Delivered
[contributor/Git conventions](../CONTRIBUTING.md), the
[repository map](REPOSITORY_MAP.md) and [migration roadmap](REPOSITORY_MIGRATION.md).
Documentation ownership and current-vs-historical entry points are explicit.
The sponsor's parent-folder clarification is accounted for in the
[external workspace inventory](REPOSITORY_MAP.md#project-workspace-outside-this-repository):
test copies, old publishing clone, backups, RemixJobs and Toolkit archives are
classified separately from Git branches. No external folders were moved/deleted.
The [task list](../openspec/changes/organize-repository-foundation/tasks.md) records
completion and verification. The sponsor reviewed the foundation and requested
a local commit on `codex/organize-repository-foundation`; no merge, push or release.

Focused checks pass: 76 links, 12 tracked root classifications, 784 source/build/test
files and 10 checked private package/settings/game inputs unchanged; strict OpenSpec
validation and whitespace checks pass. No new runtime/GPU/gameplay tests were
needed or claimed. All 14 tasks are complete; archival remains a separate action.

The runtime baseline remains `35fda1b`, with sponsor-confirmed restored
enhancements; `fe17b8d` records OpenSpec setup. Source/asset paths and the private
alpha are unchanged by this foundation. Prior tests are not being rerun or
claimed as new results of documentation work. Vendor/VC++ closure, clean-machine
and second-machine package checks, and candidate approval remain release gaps.

Next: review this foundation before a separate `separate-release-tooling` change.
No file relocation, deletion, CI implementation or rendering changes are included.

## Historical updates

The entries below preserve their dated status. Read the current handoff and the
section above before treating an older "pending", "parked" or "latest" as current.

**November9 — OpenSpec installed:** CLI1.16.1 with six local Codex core workflows;
SFC context and artifact rules configured. AGENTS.md preserved, telemetry off,
project health/templates/update dry-run verified. The repository-foundation
proposal/design/task list passes strict validation;14implementation tasks remain.
No game-behavior specs or historical migration. Development-only; alpha package
unchanged. [OpenSpec guide](OPENSPEC.md) and
[foundation proposal](../openspec/changes/organize-repository-foundation/proposal.md).
No foundation implementation or push.

**November9 — Cleanup startup regression fixed:** the profiling-off change hit
an old native warm-up requirement for profiling to be on. Removed that coupling,
rebuilt the renderer and updated the private alpha with rollback. Old-host off/on
control confirms the cause; corrected host starts with profiling off, transfers
three matching bootstrap GPU planes and exits cleanly. Passive cancellation,
749regressions and installed read-only preflight pass. Settings preserved; no SFC
launched. Sponsor confirmed enhancements work after the fix; immediate relaunch
was not separately reported.
[Evidence](runs/2026-11-09-codex-production-module-separation.md#gameplay-regression-and-correction).

**November9 — Production separation implemented:** sponsor reopened the work.
Committed checkpoint49373fd (not pushed). New uncommitted changes exclude all48
audited files from the alpha while keeping developer tools in Git. One helper
added: own files118→71, production Python59. Fresh reduced-package preflight,
real captured-asset/material/light CPU preparation and748tests pass. Private
checkout updated with rollback; original settings/game profile preserved.
Same EXE/CMD gameplay/exit/relaunch check remains.
[Record](runs/2026-11-09-codex-production-module-separation.md).

**November9 — Audit narrowed to our code:** all118 authored payload files reviewed;
48now flagged for exclusion/dependency separation,70provisionally retained.
New findings: displaced old preparation queue, diagnostic-only Python buffer
recorder, loading experiments and development evidence-budget module. Startup
profiling/task spans/cohort dump writing still happen internally with reports off;
diagnostic-only cleanup identified separately from synchronization/integrity.
[Detailed audit](releases/PROJECT_PAYLOAD_AUDIT.md). No refactor/deletion/runtime
change; implementation remains parked.

**November9 — Whole-package relevance review:** read-only inventory of3,901files.
Added2,555 candidates/about29MiB beyond tools; no deletion/refactor. Proven direct
Remix dependencies stay. Standard-name MSVCP140.dll is absent despite the native
import contract: resolve this packaging gap before clean-machine release checks.
[Expanded list](releases/PACKAGE_FILE_RELEVANCE_AUDIT.md).

**November9 — Parked by sponsor:** production-runtime/development-tool separation.
Preserve the working integration; no implementation until reopened. Scope and
restart action are in the existing Obsidian Parking Lot; the
[tools audit](releases/PACKAGED_TOOLS_AUDIT.md) is its technical starting point.

**November9 — Packaged tools audit (no deletions):** 105files/about785KiB.
34development-only module candidates, seven mixed modules and two diagnostic
profiles identified for staged removal from the distribution. Runtime helpers
are entangled with fixtures/qualification modules; do not delete whole folders
or remove the two profiles before correcting imports/reads.
[Exact list](releases/PACKAGED_TOOLS_AUDIT.md). Static audit only; package unchanged.

**November9 — Product folder cleanup:** removed unused data directories, old
restored runs, Python build folders and an unselected Remix build. About543MiB
removed; settings/game files preserved. New staging/ZIP rules prevent recurrence.
746 tests, installed preflight and asset/light initialization pass. Real trimmed
runtime renders/transfers; its standalone coverage oracle remains partial exactly
as in the untouched control. No SFC launched. Normal launcher unchanged.
[Record](runs/2026-11-09-codex-alpha-layout-cleanup.md).

**November8 — Private rendering confirmed; release recording controls added:**
normal launch now saves no run history; optional `SFCRemix/Troubleshoot.cmd` keeps
at most five 64KiB summaries (320KiB total). Temporary rendering/recovery files
clean after safe shutdown; incomplete recovery stays protected. Recording quotas
no longer terminate installed untimed play. Messages simplified; settings intact.
742 regressions plus final eight focused retention tests, actual guard quota
test and installed/moved-package checks pass. Gameplay cleanup/relaunch after
this change still needs confirmation. Changes remain uncommitted.
[Record](runs/2026-11-08-codex-alpha-recording-options.md).

**November8 — Latest private retry:** reached tactical asset preparation, then
failed on a development-only light config path. Corrected to package settings;
normal game exit/rollback confirmed. Expanded installed smoke through real
captured-asset initialization and light binding passes; 735 tests and exact CMD
preflight pass. Same CMD retry needed; gameplay rendering still unverified.
[Record](runs/2026-11-08-codex-alpha-light-context-fix.md).

**November8 — Private alpha scene startup repaired:** latest run failed before
capture because `multi_ship.toml` was absent. Added both scene profiles to the
explicit package inputs and parse them before launch. Generated environment
cache now stays under data. Interrupted graphics transaction recovered after game
exit; private package updated with rollback. Exact CMD preflight, installed scene
preparation through the process-launch boundary and 734 desktop tests pass.
Retry the same CMD; actual packaged enhancement rendering remains unverified.
[Record](runs/2026-11-08-codex-alpha-scene-startup-fix.md).

**November8 — Normal alpha launch uses CMD/native Windows:** private checkout's
`SFCRemix-Launch.cmd` directly invokes the native launcher and bundled runtime;
PowerShell removed from this launch path. Current administrator policy unchanged.
731tests, installed exact-CMD preflight and moved Unicode/spaced package checks
pass. Sponsor can double-click the same CMD file; gameplay retry remains pending.
[Entry-point record](runs/2026-11-08-codex-native-alpha-entrypoint.md).

**November8 — Normal-play elevation appears removable:** source audit identifies
our wrapper/Python checks as the enforced requirement. The actual controller's
operations pass against an owned unelevated child, and private game-copy file
access/replacement passes as a standard user. Full non-admin SFC gameplay remains
unqualified; current launcher unchanged. Recommend a scoped standard-user checkout
before making it the alpha default. [Assessment](releases/PRIVILEGE_ASSESSMENT.md).

**November8 — Packaged-launch failure corrected:** the first private launch was
rejected before game creation by a leftover native development-path restriction.
The package now validates its own game/launcher/add-on paths and hashes; installed
preflight invokes the same native check. Cleanup was confirmed,730Python tests
and14native checks pass, and actual Unicode Detours/GPU rendering passes600frames.
Private package updated with rollback copies; retry the same command. No packaged
gameplay or public release success claimed. [Review](runs/2026-11-08-codex-alpha-launcher-portability-fix.md).

**November8 — Private functional alpha checkout ready:** all six supported
native sizes pass600-frame multi-ship GPU tests. Resize plus device recreation
retains geometry and correct depth/text across three output generations.729Python
tests and both development timing policies pass; untimed BRK preflight is restored.
Installed package preflight passes after moving to `C:\Project\SFC-Alpha-Checkout`,
using bundled Python and pinned Remix, without Toolkit/Codex runtimes or test
receipts. Sponsor gameplay requested; no result yet. Final vendor/profile review,
reviewed-commit ZIP, second-machine checks and publication approval remain open.
No release ZIP/tag/commit/push. [Checkout command and evidence](releases/PORTABLE_ALPHA.md).

**November8 — Native-resolution alpha integration:** target dimensions/generations
now drive the existing renderer→receiver→native insertion path. Standalone tests
pass1024×768,1280×720,1366×768,1920×1080 and a live-output resize to1024×768,
including native depth/text and retained assets. Remaining sizes and portable
ReShade base relocation are being checked.727Python regressions passed before
the new shared-asset-order test. A discovered alias-first admission race is fixed
and under actual GPU validation. Alpha scope is the six supported SFC sizes
through1080p;1280×360 is a negative diagnostic, native1440p/4K deferred. No release
ZIP/tag exists; package closure and clean-directory/second-machine play remain.
[Details](releases/PORTABLE_ALPHA.md). Earlier entries below are historical.

**November 8 — Alpha transfer gate needs resolution:**723testsPASS; actual
application-local/WinPS5.1 read-only preflight passes Unicode/spaces and a moved
package. Existing development BRK/untimed preflight restored/passes; unchanged
native host hash. Isolated GPU tests identify1280×360shared-image corruption
between correct Remix D3D9 pixels and native D3D11 pixels.1440p/4Kquadrants match,
but full native-resolution output/resize/gameplay remain unqualified. No alpha
ZIP/tag/publication. No runtime patch or architecture change introduced.
[Details and remaining gates](releases/PORTABLE_ALPHA.md).

**November 8 — Portable alpha implementation started:** approved self-contained
ZIP/no installer, tester's game copy, native dimensions through4K. App-local
upstream Python and pinned packages work; shared path context, manifest/profile
checks, settings preservation, launch/recovery entry points and allowlist ZIP
builder implemented.718 tests pass; extent/target-contract native tests15/12pass.
The contracts are not yet connected to live output; no package, tag, gameplay
qualification or release published. Continue runtime closure, output generations
and actual GPU dimension tests before clean-directory/second-machine checkout.
[Current implementation record](releases/PORTABLE_ALPHA.md).

**November 8 — Live FCA break replacement works:** two separate FCA breakups,
eight fragments with successful insertion/suppression, cached content reused for
the second ship. Sponsor confirms correct motion and normal controls/HUD/effects.
No service error or deadline misses. Original client unchanged, proxy restored
and helpers exited. Controlled-unload PARTIAL reflects destroying the remaining
ship and ending the session before that step, per sponsor; no rendering failure.
Destruction feature demonstrated for FCA, BRK still opt-in. Alpha portability/
packaging work is next; universal model coverage is not claimed.
[Live result](runs/2026-11-08-codex-live-break-success.md).

**November 8 — Second BRK rejection fixed at receiver:** service drained an
intact-only receiver before reaching the corrected worker. Both now use explicit
strict debris admission when enabled. 66 tests and latest-run actual captures
pass through shared-memory reception and material preparation. Latest gameplay
exit/cleanup were normal; no debris reached Remix before the error. Same launcher
ready; downstream live rendering/suppression still needs checkout.
[Receiver fix and revised diagnosis](runs/2026-11-08-codex-break-receiver-fix.md).

**November 8 — BRK worker fixed:** production parallel preparation now uses the
strict opt-in debris decoder. 51 targeted tests pass, including real decode and
mixed submit-to-base/enhanced preparation. The failed run's actual captures now
prepare all four fragments/6,370 triangles and intact ships with shared reuse.
Build/qualification refreshed; read-only preflight PASS. Same BRK launcher is
ready. No live retry performed; destruction acceptance remains pending.
[Fix and verification](runs/2026-11-08-codex-break-worker-fix.md).

**November 8 — BRK failure diagnosed:** all four valid FCA fragments were captured,
but the active parallel worker still used intact-only mesh admission. Same saved
packets pass the dedicated debris decoder and fail the actual worker; no debris
reached Remix. This is our integration gap, not demonstrated renderer failure.
After SFC exited, exact-run recovery restored the copied proxy/configuration.
Next correct the active decoder and test its worker boundary; another discovery
capture is unnecessary. No source fix or live acceptance yet.
[Failure evidence and correction](runs/2026-11-08-codex-live-break-failure-review.md).

**November 7 — Alpha delivery assessment prepared:** approved replacement,
weapon-light, damage and fast-break scope retained. Live BRK checkout remains
pending; no alpha readiness claim. The actual delivery gaps are local paths and
Codex runtimes, development receipts, legacy bootstrap dependencies, fixed
1920x1080 assumptions, dependency/distribution review and clean-machine setup.
Next centralize installation roots and inventory the runtime dependency closure;
then stage an allowlisted package and prove setup/recovery/removal. Standard
ExtraFrame and untimed minimal-recording play stay the proposed baseline.
[Release assessment and sequence](releases/ALPHA_READINESS.md).

**November 7 — nxreliant research ingested:** original weapon/light handover
preserved with attribution/hash and linked to our effect inventory/light map.
Targeted 98-instruction checks corroborate upstream entity-light fields and RGB
storage. External version differs; two supplied addresses are not local
instruction boundaries. Owner/weapon attribution remains a lead, not proven
integration. Review finalized across all fourteen source sections. Sponsor
confirms nxreliant's client is his newer modified executable; address differences
are mapping concerns, not established contributor errors. No runtime changes;
live debris checkout awaits the sponsor's later run.
[Contribution review](reconnaissance/nxreliant-weapon-light-research.md).

**November 7 — Live debris checkout ready:** fresh indexed fragments now use
independent persistent identities, simulation poses and cached geometry through
ordinary D3D9/Remix and synchronized native insertion. Capture precedes precise
fragment suppression. Original break textures are retained; no intact damage UVs
are invented. Normal launcher/appearance are unchanged; break support is opt-in.
Native/transport tests, 90 targeted Python tests and both 600-frame insertion
regressions PASS; copied-game preflight PASS. Live gameplay remains unverified.
Next run `tools/native_insertion/start_native_break_session.ps1` with F-CA and a
surviving wingman, destroy the enhanced ship and check fragments/camera changes.
[Implementation, evidence and limits](runs/2026-11-07-codex-live-break-prepared.md).

**Player-name blocker removed:** saved names now survive startup,exit and
interrupted-run recovery. Client,graphics files and remaining INI settings stay
checked. Your current name is preserved;no game configuration overwritten.
694tests PASS;normal launcher preflight passes with your saved preference.
[Run296](runs/2026-11-04-codex-player-preference-baseline.md).

**Folder cleanup complete:**3.27GBobsolete generated files removed(~3.24GBdisk
reclaimed);current evidence,original captures,dependencies and settings retained.
684tests PASS. Next launcher is blocked by the already-known campaign-saved
player-name preference versus the frozen test INI check;neither preference nor
verification rules changed during cleanup.
[Run295](runs/2026-11-04-codex-artifact-cleanup.md).

**Untimed play checked across three missions:** sponsor reports stable behavior
with one ship-render dropout. About21minutes,8fresh revisions,0asset rejections,
normal renderer/receiver exits and owned-process cleanup. Grayish KFF wing
patches remain unresolved;damage blending and reflections are candidates,
not diagnoses. No settings changed. Harness PARTIAL is from a saved test-copy
player-name preference;original files unchanged and proxy restored.
[Run294](runs/2026-11-04-codex-three-mission-play-review.md).

**First untimed launch failure corrected:** the controller missed the session
flag and rejected duration0before capture. Explicit environment forwarding is
fixed and tested against the actual controller.684tests pass;copied setup
restored. Same launcher;live retry pending.
[Run293](runs/2026-11-04-codex-untimed-controller-startup-fix.md).

**Normal play is now untimed:** run the usual native multi-ship launcher without
diagnostic flags, enter battles when ready, and exit SFC normally when finished.
Current appearance, weapon lights and damage remain enabled. No continuous frame
trace or screenshots; required asset caches and compact records remain bounded.
Use `-TimedTest` for the old short checkout. Campaign transitions are the next
live checkout, not yet a demonstrated result.
[Run292](runs/2026-11-04-codex-untimed-play-session.md).

**Damage is now baseline:** the normal native multi-ship launcher enables it.
No extra flag needed. Use `-NoDamageTextures` for an explicit comparison;old
`-DamageTextures` still works. Diagnostics remain off by default.678tests pass.
[Run291](runs/2026-11-04-codex-damage-baseline.md).

**Damage layer visually confirmed:** two corrected KDD/FCA runs show no first-use
transparency; sponsor reports smoother damage blending/progression.733/1699damage
draws with0unqualified source states or timing misses. Files restored and owned
processes exited. Overall harness still marks process-exit summary limits partial;
that is separate from this visual result. [Run290](runs/2026-11-04-codex-damage-live-confirmation.md).

**Damage transparency correction prepared:** found a documented Remix mismatch:
our decal draw had blending disabled. Corrected it;GPU output now shows discrete
marks on a solid hull,including the first damage-bearing frame of an already
visible scene. Repair still removes the layer. Live transparency/glitch recheck
pending. All added diagnostic items are listed with disable routes in
[diagnostic reference](DIAGNOSTICS.md). [Run289](runs/2026-11-04-codex-damage-decal-blending.md).

**Workspace cleanup completed:** deleted23,722obsolete generated files and old
output archives(7.56GBlogical;7.24GBmeasured disk space recovered). Current
captures,dependencies,settings and source preserved. Launcher preflight and
673Python tests pass. [Run288](runs/2026-11-03-codex-artifact-cleanup.md).

**Damage checkout regression corrected:** both damage-enabled runs loaded assets
but rejected every hull because the real SFC getter differed from the synthetic
fixture. Added its pinned read-only accessor and separated optional decal
qualification from enhanced-hull drawing. GPU regression now keeps all three
hulls visible even with unavailable damage observations. Live retry pending.
[Run287](runs/2026-11-03-codex-damage-source-regression.md).

**Damage textures prepared for checkout:** separate original-image decals follow each
ship's current damage state, including repairs/removal. Standalone rendered tests
show undamaged→heavy→repaired; three-owner native insertion and damage-off
regressions pass. Actual SFC source agreement and gameplay appearance are still
pending. Default off; current lighting/material settings preserved.
[Run286 record](runs/2026-11-03-codex-live-damage-layer.md).

**Interface exposure reviewed:** geometry, ownership, persistent transforms,
camera and native replacement are reusable foundations. Remix materials, light
conversion and startup still have backend coupling; Windows GPU return needs
its own adapter. Other developers have source and documented attachment points,
but no stable drop-in SDK yet. Damage must expose per-owner state and future
change triggers, rather than exist only as a Remix material switch. No runtime
changes. [Run285 interface guide](reconnaissance/2026-11-03-renderer-interface-exposure-audit.md).

**Damage capture succeeded:** the F-CA progressed through light, medium and heavy damage, each linked to its original damage/SI images. We captured the separate damage mapping: same hull geometry, different texture coordinates. One mapping served all three stages, so it can be reused while damage state changes. No drops/read errors; cleanup and client checks passed. Next: finish the narrow blend/companion and first-use ordering work before adding this layer to Remix. [Run284](runs/2026-11-03-codex-damage-observation-review.md).

**Damage investigation:** SFC draws damage as a separate layer over the intact hull, using shared light/medium/heavy images and its own mapping. Our current fresh capture omits that second layer. Existing sampled logs do not retain the missing damage state. [Run282](runs/2026-11-03-codex-damage-texture-investigation.md).

**Weapon lights are visible:** radius2.0 is the tentative baseline. The sponsor could see photon-associated lights after slowing to speed1. Logs confirm brief moving lights reach Remix without recording gaps. Exact weapon-to-light ownership remains unproven. Video2 linked in README. [Run281](runs/2026-11-03-codex-effect-radius-and-moving-lights.md).

**First effect-light checkout:** the game supplied1,046active light submissions to Remix, with no missing or invalid records, but the sponsor saw no illumination. Most continuous active periods lasted long enough to see. The native falloff field is spatial range, not seconds. Internal placement/shadowing and brightness/falloff conversion remain possibilities; neither is proved yet. Next is a targeted visible-contribution check, not a guessed lifetime extension. [Run279](<C:/Project/SFC-Modernize Engine/docs/runs/2026-11-02-codex-first-effect-light-gameplay-review.md>).

**Effect lights ready to try:** SFC now drives the new lights' position, colour and on/off state in Remix. Existing scene lighting and visual settings are preserved. Native tests and both600frame rendering checks pass. First run should add `-LightDiagnostics` to save bounded evidence while firing weapons and taking hits. Sphere shape and brightness remain provisional; gameplay confirmation is next. [Run278](<C:/Project/SFC-Modernize Engine/docs/runs/2026-11-02-codex-effect-light-integration-checkout.md>).

**Accepted checkpoint:** sponsor accepts the ExtraFrame configuration as stable following the stress checkout. Commit and publication authorized. Continue with that explicit option; minor remaining findings stay tracked below.

**Ready for the next test:** ExtraFrame is now the launcher default. Leave off CompletionDiagnostics for the normal run. Cleanup reclaimed about1.23GB through verified, recoverable texture archives, leaving about1.71GB within the evidence allowance. Normal startup checks pass. [Run277](<C:/Project/SFC-Modernize Engine/docs/runs/2026-11-02-codex-cleanup-and-extraframe-default.md>).

**ExtraFrame stress worked:** all63tracked objects received replacements across15models, with zero deadline misses, compared with96in the earlier Strict run. Typical delivery delay stayed around19ms; the allowance does not impose a full-frame wait. Cleanup passed and materials had no errors. Two new-asset records lacked insertion, and separate whole-game hitches remain; the battles were different sizes. Recommend keeping the explicit ExtraFrame option for checkouts. Default launcher settings are unchanged. [Run276](<C:/Project/SFC-Modernize Engine/docs/runs/2026-11-02-codex-extraframe-stress-comparison.md>).

**Stress result:** all72tracked objects received replacements, sharing17model assets. Material updates had no errors or retries, and cleanup passed. First replacement appeared in about one second. Stability remains partial:96post-startup frames missed the strict deadline, including a10frame/0.29second burst. Most misses coincide with later asset activity, but two larger hitches have a separate, unresolved between-frame component. Next suggested comparison is the existing ExtraFrame policy, with settings unchanged. [Run275](<C:/Project/SFC-Modernize Engine/docs/runs/2026-11-02-codex-seventy-two-owner-stress-review.md>).

**Five-second stop rule removed:** delayed material updates now keep retrying while rendering continues with the last accepted materials. A deliberate seven-second delay passed the600frame rendering test, issued one warning and recovered automatically.80focused checks and both rendering policies pass; the same launcher is ready for stress testing. Windows replacement fix and current appearance are retained. [Run274](<C:/Project/SFC-Modernize Engine/docs/runs/2026-11-02-codex-nonfatal-material-retries.md>).

**Material update fix ready:** existing generated material files now use Windows' dedicated replacement function. It passed77 focused checks and both600frame standalone rendering tests, with no publication retries and clean shutdown. Materials, lighting and original assets are unchanged. The same launcher is ready for your larger stress test. The separate five-second stop policy was not changed in this increment. [Run273](<C:/Project/SFC-Modernize Engine/docs/runs/2026-11-02-codex-windows-material-replacement.md>).

**Gameplay review:** first run replaced26tracked objects across nine model types, with fast startup and five isolated single-frame misses after replacement began. It exited cleanly. The second run also displayed enhanced assets quickly, then stopped on the still-unmodified material-file update problem. Startup is a positive result in both; the second run still failed overall. Full stress test remains pending. [Run272](<C:/Project/SFC-Modernize Engine/docs/runs/2026-11-02-codex-prepared-dome-gameplay-review.md>).

**Material-file investigation:** our current file-replacement operation fails when the bundled reader keeps the old file open. A standard Windows alternative passed all four direct comparisons and a600frame standalone rendering test with no publication errors. Recommend changing that operation and retaining the last working materials while updates retry, rather than stopping the run after five seconds. These are proposals: normal code and the ready gameplay launcher are unchanged. Exact historical reader ownership is not proved; this failure is not attributed to Defender. [Run271](<C:/Project/SFC-Modernize Engine/docs/runs/2026-11-02-codex-material-publication-investigation.md>).

**Both fixes implemented:** the normal renderer prepares and reuses the actual project dome before gameplay. The separate 32-ship drawing cutoff is removed; it follows the existing 256-owner scene budget, and overflow leaves affected ships native without stopping other replacements. Both 600-frame timing-policy tests passed, plus a GPU check of 256 independent owner pixels. Your settings and original client are unchanged. Carrier/fighter gameplay checkout is next. The separate material-file permission problem remains open. [Run270](<C:/Project/SFC-Modernize Engine/docs/runs/2026-11-02-codex-prepared-dome-and-hull-capacity.md>).

**Dome preparation tested:** an isolated build prepares the actual configured light before gameplay and reuses its handle. Five first-live completion waits were about 6–8 ms; immediate and delayed full tests passed, but three other delayed tests later stopped on a separate material-file publication denial. Normal renderer/settings are unchanged. Next: turn the tested resource approach into a qualified startup change and resolve publication retry behavior. The 32-entry hull limit is still open; no new fleet checkout yet. [Run269](<C:/Project/SFC-Modernize Engine/docs/runs/2026-11-02-codex-dome-resource-preparation-prototype.md>).

**Startup cause identified:** the successful Windows trace shows Defender holding a Remix file-opening operation for 3.06 seconds while waiting for its scanning service's reply. That overlaps almost all of the 2.84-second first-live-frame delay. The exact internal scan reason remains unknown; this is not evidence of a malware flag or a new light-code regression. Next fix: reuse and fully prepare the actual environment resource before live rendering, keeping Defender and your lighting/settings unchanged. No production fix applied yet. [Run268](<C:/Project/SFC-Modernize Engine/docs/runs/2026-11-02-codex-dome-defender-wait-attribution.md>).

**Trace launcher corrected:** the last attempt reproduced a 2.6-second rendering wait but did not save a Windows trace. Our recording trigger used the wrong countdown. It now starts recording directly before the actual activation, with seven focused checks passing. Same Administrator PowerShell command as before; no game actions needed. Root cause remains unproved, and normal rendering/settings are unchanged. [Run267](<C:/Project/SFC-Modernize Engine/docs/runs/2026-11-02-codex-dome-trace-trigger-correction.md>).

**Startup investigation:** the test renderer without effects is an exact copy of our recorded pre-light executable. The same dome-file delay was recorded before the light additions. Current tests reproduce it without changing existing lighting, materials or runtime settings. Earlier reading/reusing the tiny dome image avoided that particular wait in two trials, but later material-file publication still stalled; no fix or full pass claimed. A short Windows trace needs your existing Administrator PowerShell to identify what is holding the files up. Prepared command: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\artifacts\player-replacement\run266\start_dome_wait_trace.ps1"`. No game actions needed. [Run266](<C:/Project/SFC-Modernize Engine/docs/runs/2026-11-02-codex-pre-light-dome-comparison.md>).

**Recent edits investigated:** replayed8captured model families with the current renderer and with the new effect-light code removed. Both worked immediately,but both failed after delayed startup while Remix opened the tiny dome/GI image. Startup warms a triangle,not that actual light resource. Next:prepare and verify the configured environment before gameplay,then fix the separate32-entry hull limit. No production rendering changes made during this comparison. [Run265](<C:/Project/SFC-Modernize Engine/docs/runs/codex-run265-recent-edit-startup-comparison.md>).

**Latest carrier failure:** the game data arrived,but the first real replacement image did not finish within the existing five-second limit. No replacement ship reached SFC. This attempt hit the rendering-completion wait before the separate32-entry hull limit. Effect lights were OFF,and cleanup passed. Investigate the first-frame wait using the existing dome-image lead;the exact cause is not yet proven. [Run264](<C:/Project/SFC-Modernize Engine/docs/runs/2026-11-01-codex-carrier-first-frame-timeout.md>).

**Storage cleaned:** removed redundant loose test copies through verified consolidation and cleared rebuildable symbol caches. Evidence usage fell from19.54GBto16.03GB,leaving roughly4GBunder the existing allowance. Useful captures,logs,rollback files and current dependencies are preserved. Launcher checks pass again. This does not fix the separate32-entry hull limit. [Run263](<C:/Project/SFC-Modernize Engine/docs/runs/2026-11-01-codex-evidence-storage-cleanup.md>).

**Carrier failure identified:** a separate depth/coverage helper still had an old32-entry limit. The larger ship registry had been expanded,but this helper was missed. Correct that limit and its failure handling before another fleet test. Test files have been restored and no owned processes remain. [Run262](<C:/Project/SFC-Modernize Engine/docs/runs/2026-11-01-codex-carrier-depth-cap-failure.md>).

**Light scope corrected:** additional effect lights are now OFF. Their code was prepared,but enabling them before the agreed integration test was premature. Existing scene/GI settings are preserved. Light integration and focused emission recording remain pending.

**Effect lights prepared:** the game now supplies transient light positions,colours and on/off state to Remix every frame. Scene lights and GI retain your settings. A separate section in lights.toml controls effect strength,colour and emitter size. Both real rendering checks passed;next is a weapons-fire checkout. Shape is a sphere approximation,and brightness still needs visual confirmation. [Run261](<C:/Project/SFC-Modernize Engine/docs/runs/2026-11-01-codex-game-driven-effect-lights.md>).

**Integration-test note:** collect more light-emission data during the checkout:colour/strength changes,range,position and fade/on/off timing,compared with what Remix receives. Prepare a small optional recorder first;the current tool saves totals only. Keep ordinary performance mode free of that recording overhead.

**Replacement recovery fixed:** routine submission changes now fall back for the affected ship/frame and retry automatically;they no longer shut off the entire enhanced scene. Other ships keep replacing. The real hook tests and both rendering checks pass;appearance is unchanged. Same launcher for a carrier checkout,then we can move forward from Remix wiring. [Run260](<C:/Project/SFC-Modernize Engine/docs/runs/2026-11-01-codex-replacement-frame-recovery.md>).

**Carrier stress test:** first replacement arrived in0.85seconds;29tracked objects used12shared model assets. All assets were accepted and cleanup passed. However,replacement silently stopped around78seconds,while SFC continued normally. The remaining timing records repeated the last replacement,so this is a partial result. Next:identify the stop condition and correct that reporting. [Run259](<C:/Project/SFC-Modernize Engine/docs/runs/2026-11-01-codex-carrier-stress-review.md>).

**Exit whenever finished:** a normal early game exit now stops the test and cleans up its renderer, workers and test files without waiting for the recording timer. The shortened evidence is saved. Exit/cleanup checks pass; the next gameplay run will confirm early exit and relaunch. Lighting and appearance are unchanged. [Run258](<C:/Project/SFC-Modernize Engine/docs/runs/2026-11-01-codex-normal-early-exit-cleanup.md>).

**Live loading confirmed:** the first replacement was inserted in0.88seconds. Both ships loaded,and all5,340recorded frames after the first replacement committed successfully. The game and renderer exited normally and client files were restored. [Run257](<C:/Project/SFC-Modernize Engine/docs/runs/2026-11-01-codex-subsecond-gameplay-and-relaunch.md>).

**Next-launch block fixed:** editing the lighting file triggered an overly strict launch check. Lighting and rendering profiles now pass their existing value checks without needing to match old appearance hashes;code/runtime checks remain intact. Your settings are preserved. The same launcher passes again;no manual reset required. The cold dome-image preparation work remains pending.

Previous checkpoint:

**Geometry handoff fixed:** models and textures now arrive together through protected memory. Large-ship preparation took26–35milliseconds in the new checks. Both normal rendering tests passed,with your visual settings unchanged. An optional recorder now keeps only slow completion events. [Run256](<C:/Project/SFC-Modernize Engine/docs/runs/2026-11-01-codex-memory-geometry-delivery.md>).

**Remaining delay identified:** Remix's command worker spent seconds opening the dome light's tiny160-byte environment image. The graphics card was waiting for that file operation. Next:prepare and retain that light resource before the first live frame needs it,without changing the light. That next fix is not implemented. Overall loading is not yet consistently fast. The existing launcher is prepared;`-CompletionDiagnostics` enables the bounded recorder for a test.

Previous checkpoint:

**Another delay identified:** a ship that normally takes about30milliseconds to prepare spent roughly4seconds waiting to open its small generated geometry file. We can remove that handoff by sending geometry through the same protected memory connection now used for textures. This is diagnosed,not implemented yet. [Run255](<C:/Project/SFC-Modernize Engine/docs/runs/2026-11-01-codex-remaining-startup-waits.md>).

**Rendering timeout still unresolved:** three observed standalone checks completed,but did not reproduce the earlier five-second failure. “Waiting for completion” can include unfinished CPU work inside Remix;it is not proof that drawing itself took five seconds. Normal code/settings are unchanged. No game run needed from you yet.

Previous checkpoint:

**Texture handoff fixed:** prepared textures now reach the renderer through protected memory for the first ship and later ships. Initial setup took about2–5milliseconds instead of3–6seconds. Texture mapping, materials and lighting settings are preserved. Both successful rendering checks and the memory-transfer tests passed. [Run254](<C:/Project/SFC-Modernize Engine/docs/runs/2026-11-01-codex-memory-texture-delivery.md>).

**Loading is not fully resolved:** two delayed-start checks hit a later five-second wait inside the rendering/output stage. Another run inserted its first ship in0.58seconds but loaded a later asset slowly. The exact remaining cause is not established. Failed evidence is retained;temporary diagnostics are removed from the normal build. Next:locate that later wait before asking you for another loading test. Changes remain uncommitted;Defender stays enabled.

Previous checkpoint:

**Four-second delay confirmed:** your live run took4.01seconds. About3seconds was in first-ship setup. A controlled reproduction caught Windows waiting to open the first generated texture file—only256KB—not drawing or converting the ship. The remaining file handoff must be replaced with bounded memory delivery of the already-prepared pixels. That fix is not implemented;no further loading test needed yet. Temporary diagnostics were removed from the normal path and evidence preserved. [Run253](<C:/Project/SFC-Modernize Engine/docs/runs/2026-11-01-codex-texture-open-regression.md>).

**Receiver preparation is moved earlier:** it now starts before ships are needed,waits without GPU output,and receives the exact accepted asset identity when available. Cancellation/failure/late activation checks and both real rendering tests passed. Activating the prepared receiver took0.13–0.41milliseconds. Defender remains enabled. Overall loading still varies:a separate later setup step took2.75seconds in one test. Existing multi-ship launcher is ready for gameplay checkout;changes uncommitted. [Run252](<C:/Project/SFC-Modernize Engine/docs/runs/2026-11-01-codex-early-passive-receiver.md>).

**Cause confirmed:** Defender held this receiver launch for3.276seconds while its service checked it,accounting for almost the entire delay. The corrected trace retained the wait and Defender's reply. No malware/block finding or exact internal rule established. Rendering tests/cleanup passed;Defender remains enabled. Next:prepare the receiver before ships need it,without bypassing protection. No more diagnostic runs needed. [Run251](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-31-codex-defender-receiver-cause.md>).

**Recording correction:** Windows saved the trace,but my buffer was too small and retained only the final second after the launch delay. Increased the circular buffer and removed unrelated event categories;recording now stops promptly when the receiver starts. Same standalone command needs another run from Administrator PowerShell. Game/rendering code and Defender remain unchanged. Exact Windows cause is still unknown. [Run250](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-31-codex-receiver-trace-retention.md>).

**Trace-tool correction:** the standalone test passed and reproduced the five-second delay,but my recording controller started its countdown too late and saved no Windows trace. It now uses the session identifier available before launch and the actual readiness timestamp. Same command,one repeat needed from Administrator PowerShell;no gameplay or production changes. [Run249](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-31-codex-receiver-observer-trigger-fix.md>).

**Investigating the startup cause:** fast/slow gameplay used identical binaries/settings. The receiver's launch ordering predates cleanup,but all four slow launches in297saved profiles are recent—cause remains unresolved. A short standalone Windows trace is prepared;it needs your existing Administrator PowerShell because this session lacks Windows profiling permission. No gameplay actions or security changes. [Run248 and command](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-31-codex-receiver-cause-investigation.md>).

**Larger battle caught the delay:** first replacement took6.06seconds;5.001seconds was Windows launching the receiver. Same renderer build launched it in4milliseconds in the previous run.22tracked objects delivered using5shared model assets;you confirmed normal gameplay after loading. Cleanup passed. The intermittent launch wait is now confirmed in the real game;its internal cause remains unknown. No code changes in this review. [Run247](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-31-codex-multimodel-receiver-delay.md>).

**Latest gameplay checkout passed:** you confirmed normal ships,lighting,shields,pause text,controls and camera switching. First replacement entered the game in0.70seconds;F-CA independently confirmed replaced by1.65seconds. Receiver launch took4milliseconds,so the separate five-second launch wait did not occur this time. A few brief fallbacks remain in logs without visible issues. Cleanup and unchanged-game checks passed. This is one successful run,not proof the intermittent startup delay is gone. [Run246](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-31-codex-startup-functional-checkout.md>).

**Later startup delay identified:** Windows spends about five seconds starting our receiving process from the renderer. Scene reading,texture work and diagnostics are not responsible for this measured wait. Both standalone reproductions passed rendering checks. The exact Windows-internal cause remains unknown;this is not another proven Defender finding. Next recommended change:start the receiver during launch preparation rather than after ships are ready. Not implemented yet. [Run245](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-31-codex-receiver-launch-stall.md>).

> [!summary] Where we are
> We can take live ships, textures, camera and lighting information from SFC, render through Remix, and put the result inside the game window. Gameplay and tactical UI remain native; the qualified player mesh can be replaced. The API experiment is parked. Current work reduces loading pauses while preserving the fresh-asset pipeline and accepted appearance.

**Current checkpoint:** your aggressive camera-switch checkout showed no visible native/enhanced swaps. All six ships (KDD, FDD, FFF, FCA, RCL and LFF) reached replacement. Their geometry was loaded once and reused. This validates the latest submission and persistent-light fixes in this mission. Shield replay remains parked.

**Startup ticket fixed:** the start-rendering signal now uses our existing protected memory connection. Activation fell from about5.5–6seconds to11–13milliseconds in standalone checks. The game's configuration/bootstrap order is preserved and Defender remains enabled. Both three-ship rendering checks passed. One produced output in0.48seconds from asset discovery;the other still took6.09seconds because of a separate5second delay later,around starting the output receiver. Consistent fast overall startup remains unresolved. Existing gameplay launcher is prepared;no new discovery trace needed. [Run244](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-31-codex-shared-startup-ticket.md>).

**Stress delivery:**26tracked identities,7unique assets and19content reuses;at least25tracked together in a sampled frame. After first insertion,all5,006recorded requests inserted with zero deadline misses. Cleanup passed. [Run239](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-31-codex-fighter-stress-review.md>).

**Fleet stress checkout ready:** the ninth-model stop is fixed. Active capture, preparation and replacement now agree on the shared memory layout:256 concurrent object slots and1,024 session asset revisions. Native/shared-memory tests cover160 independent objects;actual Remix integration passed both timing policies with three GPU instances. This is finite preallocated capacity,not unlimited storage or proof of100-object gameplay performance. Use the existing multi-ship launcher for your stress test. [Run237](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-31-codex-fleet-capacity-correction.md>).

**Latest implementation:** removed unused legacy draw/clear callbacks from native replacement. Ships sharing a completed scene now reuse its validated snapshot; unchanged GPU resources are checked once rather than repeatedly for every ship. Essential frame/owner matching and GPU ownership safeguards remain. Standalone checks passed under both timing policies, with exact pixels/depth and normal cleanup. Same launcher;the receiver limit is now corrected and the expanded path is prepared for checkout. No FPS improvement is claimed yet. [Run235](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-31-codex-normal-path-cleanup.md>).

**Cleanup still open:** separating detailed diagnostic recording into explicit toolsets (audit C05/C06), plus remaining matrix/asset/deployment checks. This increment did not silently disable those collectors. Weapon lighting remains the next planned functional alpha feature.

**Your settings:** lighting, materials, images, quality and reflections are unchanged. Registry lettering stays solid through the existing hull-depth fix.

**Current validation:** two isolated deadline misses occurred within the first 2.4 seconds; none occurred afterward during the remaining approximately 87 seconds. Five additional native frames occurred during initial Romulan asset preparation. Median frame time was 16.72 ms, about 60 frames/second. Cleanup, hook restoration and unchanged client checks passed. Detailed diagnostics reached their cap; functional gate records were not dropped. [Run234](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-31-codex-native-camera-stability-checkout.md>).

**Timing choice:** Strict remains the current baseline and delivered stable replacement in this checkout. ExtraFrame remains available. Rendering readiness is still about 12.4 ms; removing false scene rejections improved continuity without a demonstrated large GPU-speed change.

**Interface audit:** capture/identity foundations are reusable, but asset preparation still assumes Remix and output sharing assumes D3D11. Renderer interchangeability stays open; no refactor was made. [Findings](<C:/Project/SFC-Modernize Engine/docs/reconnaissance/2026-10-27-renderer-boundary-audit.md>).

**Alpha release scope:** replacement, weapon lighting, damage textures and a fast-loading destruction/break model are required. LOD models are optional. These are recorded requirements, not completed features. [Sponsor direction](<C:/Project/SFC-Modernize Engine/docs/decisions/2026-10-27-alpha-release-scope.md>).

**Latest checkout complete:** screen-position comparisons and diagnostic snapshot misses no longer block valid geometry. Scene lights0/1 and configuredGI retain accepted values through camera gaps; explicit config OFF remains available. One startup Present was confirmed, with the legacy24 workaround off. Small startup/admission exceptions remain documented. The earlier RDE cloak question remains open; this run used RCL. Per-light persistence controls remain pinned for later.

**Checks audit:** increment1(C01–C04)is implemented. The remaining optional diagnostics,caching and asset/launch cleanup are still separate increments. Keep frame/owner identity,GPU ownership and structural safety. [Audit C01–C15](<C:/Project/SFC-Modernize Engine/docs/reconnaissance/2026-10-31-runtime-checks-audit.md>).

**Startup workaround:** the24-render loop is **off by default**;startup now uses one render. Append `-LegacyStartupWarmup` to the native multi-ship launcher to restore it explicitly. Default and toggle both passed standalone GPU checks. Visual settings are unchanged.

**Pinned for later — light lifetime controls:** expose persistence/lifetime per light in `lights.toml`,rather than fixing scene-versus-temporary behavior in code. Preserve current scene0/1and GI persistence as defaults;temporary/effect lights need their own lifetime policy. Exact option names and timeout controls remain to be designed. This is recorded work only;no settings or runtime behavior changed.

Updated through **Run233,October31,2026**. Repository handoff and run records control resumption. The prior player checkpoint was committed/pushed; this multi-ship increment remains unstaged and uncommitted.

## Status key

- **NEXT / IN PROGRESS:** current work or its immediate continuation.
- **OPEN:** needed, not resolved.
- **PARKED:** deliberately deferred; restart condition is recorded below.
- **PROVED / LIMITED:** demonstrated within test conditions, not universally finished.
- **FIXED:** the specific defect was corrected and tested; broader issues may remain.

## Current work

### SFC-21 — Large fleets and fighter swarms

**CURRENT / PREPARED FOR STRESS CHECKOUT.**

-100+ simultaneous instances are a normal design requirement,including wingmen,fighters,pseudo-fighters and other supported objects. Shared model content must retain separate instance identity.
- Run237 fixes the old eight-revision stop and aligns the current transport budgets across capture,registry,preparation and replacement. Four workers/transfer slots limit concurrency,not scene size. Duplicate decoded-asset retention in the multi-ship sidecar is removed.
- Current finite preallocation:256 concurrent owner slots and1,024 session asset revisions within16MiB;renderer residency and disk budgets remain. Exhaustion must leave affected objects native and preserve supported rendering. Dynamically growing/paged scene capacity beyond these bounds remains unimplemented.
-160-owner transport/membership tests pass. Both600-frame Remix integration fixtures pass with three GPU instances. **Latest:** fighter-heavy gameplay passed steady delivery at26session identities,at least25concurrent tracked in a sampled frame. **Next:** resolve the observed startup activation gap and collect sponsor visual feedback. No claim of100-object GPU performance yet.

### SFC-22 — Fighter displays with multiple models

**PARKED / LATE ALPHA FOLLOW-UP — no investigation or fix authorized now.**

- Sponsor observation: fighters are often displayed as1,2,3or4 models. The engine's mechanism is unknown; do not assume these are separate simulation owners, repeated draws or a combined mesh.
- Do not infer fighter gameplay counts from visible model counts alone. This observation does not establish that the current replacement path handles every display arrangement correctly.
- **Reopen:** only after most of the alpha-release work is complete. **Next action then:** correlate one fighter entity with its model submissions and transforms to explain the1–4-model presentation,then determine whether interface support needs extending. No priority change to current fleet testing or alpha requirements.

### SFC-20 — Simple settings app

**PINNED / FUTURE — sponsor requested recording the need, not implementation now.**

- Provide a simple app for adjusting the project's existing settings without hand-editing TOML files.
- Start from the existing lighting, material, image and quality controls; keep the configuration files authoritative and preserve accepted baselines. Group related settings clearly and retain their descriptions. Live application should follow each control's existing reload support.
- Suggested conveniences for later scope review: sliders/number fields, enable switches, presets and restore-baseline. These are recommendations, not additional approved requirements.
- **Why parked:** rendering/interface work remains current. **Reopen:** sponsor chooses to build the settings app. **Next action:** inventory the current controls, ranges and reload behavior, then propose the smallest usable editor. No app framework or packaging decision yet.

### SFC-19 — Alpha mod release requirements

**RECORDED / OPEN — release scope, not authorization to expand the current test.**

- **Required:** ship replacement; weapon-generated lighting applied to replacements; damage textures read/applied; destruction/break model with fast loading.
- **November 8:** FCA destruction replacement demonstrated in live gameplay:
  two parent lifetimes/eight pieces with cached geometry sharing and native
  suppression. [Current result](runs/2026-11-08-codex-live-break-success.md).
  Broader break files remain unqualified. All four required feature areas now
  have scoped gameplay evidence; alpha deployment/packaging remains open.
- **November 7 current status:** replacement, weapon lights and baseline damage
  have scoped gameplay evidence. Live debris is implemented/offline-qualified;
  sponsor checkout pending. Historical unqualified-destruction wording below
  describes its earlier checkpoint, not a new discovery requirement. The
  [alpha delivery assessment](releases/ALPHA_READINESS.md) tracks portability,
  package membership, deployment checks and unresolved release decisions.
- Run290: standard-family damage source/application and transparency correction visually confirmed in two KDD/FCA skirmishes. Reversal/removal offline GPU-proven;live repairs/other families not yet confirmed. Damage is baseline in native multi-ship replacement. Break-model transition and loading need qualification;no arbitrary timing number set.
- **Break-model finding:** `_brk.mod` exists and SFC already loaded FCA/KFF break assets during setup, before tactical rendering. We may prepare their fresh in-memory data while the ship is alive; breakup-piece movement and transition remain unqualified. [Run212](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-27-codex-break-model-inspection.md>).
- **Optional:** LOD models. Their absence alone does not block alpha release.
- Supported multi-ship replacement and visible weapon lighting are demonstrated. Damage-layer capture/application and fast break-model transitions remain open. No alpha readiness or formal milestone PASS claimed.
- [Alpha scope](<C:/Project/SFC-Modernize Engine/docs/decisions/2026-10-27-alpha-release-scope.md>).

### SFC-18 — Player-ship replacement

**SUPPORTED MULTI-SHIP INSERTION DEMONSTRATED; TIMING AND CLOAK GAPS OPEN.**

- Registry lettering is solid in the accepted game run. Native shields and pause text now layer correctly over player replacement.
- Shield replay did not capture/replay actual game draws;that approach is parked.
- Earlier native colour/depth insertion resolves the previous late-composition ordering problem.
- Capture-first coordination,previous-batch closure and native colour/depth insertion passed offline and gameplay checks. Multi-ship sponsor checkout confirms supported owners,including shared-model KFT instances. Heavier mission has intermittent deadline/qualification fallbacks;cloaked Romulan admission/transparency is unqualified,not a demonstrated Remix failure.
- [Run229 gameplay review](runs/2026-10-31-codex-native-multiship-gameplay-review.md).
- **Research finding:** offscreen screen-position validation can reject living cached ships;the scheduling-anchor check can then withhold the whole scene. Actual checker reproduces this with captured LFF and KFF geometry. Fix/retest pending;late source-state arrival ruled out for the recorded90steady timeouts. [Run230](runs/2026-10-31-codex-camera-transition-root-cause.md).
- [Run228](runs/2026-10-31-codex-native-multiship-replacement.md),[multi-ship contract](decisions/2026-10-31-native-cohort-contract.md).
- [Run221](runs/2026-10-29-codex-native-insertion-reassessment.md),[replacement contract](reconnaissance/player-replacement-transaction.md).

### SFC-15 — Remaining rendering families

**ONE REAL EFFECTS CONNECTION CONFIRMED — other effect types remain to identify.**

- **Offline inventory complete:** 64 rendering-related classes, including 37 distinct effects plus their base class. Ten effects types also appear in the recent captures; the other 27 are possibilities, not proven gameplay coverage. Found specific photon/plasma images and shared effect sheets without running SFC again. Organian uses its own named image; the earlier guess about fx4 is superseded. Lighting changes also include drawing-pass overrides, not just physical lights. [Inventory and remaining questions](<C:/Project/SFC-Modernize Engine/docs/reconnaissance/rendering-executable-inventory.md>).

- Survey effects, sprites, beams, shields, explosions, damage, backgrounds and tactical UI. Preserve unknown/unassociated activity instead of assuming the ship hook covers everything.
- Exclude bulk mesh and image payloads; retain resource/lifecycle/state identities and bounded call-origin evidence. Distinguish common graphics paths from genuinely different interface needs.
- **Found:** different triangle, line and point drawing paths, with different blending/depth behavior. The second run has sustained late activity consistent with combat/destruction; exact explosion ownership is not yet proved.
- **Important:** many call sites show where queued drawing was flushed, not which object created it. A shared drawing path does not automatically mean effects work through our ship interface.
- **Bounds:** both256MiB traces filled at about85seconds of the requested90;195/323records dropped. Partial coverage, not failed/no-useful-data runs. Both exited/cleaned up normally and client hashes were unchanged. Mesh/image contents excluded.
- **New:** traced a missile-associated drawing routine to its shared fx0 texture, selected texture coordinates and four-corner drawing path. Confirmed38code/resource anchors against the actual client; no game changes.
- **Prepared:** targeted observer tested through the actual startup-loaded DLL, with clean hook restoration, texture-name association and pointer-reuse handling.44native checks and6parser checks passed; deliberately stalled writing did not hold up original calls.
- **Actual result:** first run linked a fresh effect instance to fx0.bmp and122,820four-corner primitives. It filled the16MiB log after35.2seconds; it did not stop because weapons were absent.
- **Other runs:** both completed90seconds, recording effects-list creation/removal and many native finalizer calls outside the selected routine. Those calls are not a count of visible effects or nonempty drawing. Faster combat does not prove the same path was used. All exits/hash checks passed and sponsor reports no issues.
- **Further analysis:** the captured effect can use both a burst image and a segmented trail from different parts of fx0. Exact image-row orientation is still unproved. Your atlas identifications are preserved as observations, not assumed engine mappings. These three runs did not capture synchronized lights. [Run170 details](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-25-codex-effect-atlas-followup.md>).
- **Prepared broader pull:** up to2GiB total, richer call-origin sampling, direct light definitions/on-off/global-gate changes and a census of concrete effect types. No model or texture-image payloads.21ring/119native/13parser/504existing checks passed; short and90second graphics fixtures passed with zero drops and clean hook restoration. No effects renderer implemented. [Run171](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-25-codex-expanded-survey-with-lights.md>).
- **Storage:** recoverably archived85completed runs' generated-image duplicates, saving3.84GB. Original assets, capture traces and mesh packets preserved. Existing20GB total cap remains.
- **New actual results:** Federation327MiB/Romulan207MiB, both full90seconds/zero dropped records/clean restoration and hashes. Ten named native effect classes identified, including phasers, photons, plasma, disruptor effects and explosions. Same-run light data includes changing temporary lights, but also drawing-time overrides; slot toggles are not automatically physical lights switching on/off. Sponsor confirms normal rendering/HUD/targeting/controls in both runs. [Run172](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-25-codex-expanded-survey-review.md>).
- **Third-launch block:** reproduced worst-case storage reservation over20GB, not leftover hooks/proxy. Archived another296MB of verified old generated-image duplicates; unchanged launcher preflight now passes. No need to rerun gameplay before more offline analysis.
- API development is paused; normal renderer/backend settings remain unchanged.

Map: [rendering families](<C:/Project/SFC-Modernize Engine/docs/reconnaissance/rendering-family-map.md>). Latest: [Run173](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-25-codex-offline-render-inventory.md>).

### SFC-16 — Renderer waiting in the menus

**OPEN — baseline CPU use; separate from the priming experiment.**

- The external renderer used about two CPU cores while waiting,both before and after material priming. The matched controls showed essentially identical CPU use. Its two busiest threads have not been attributed to a module or function.
- During a minute of primed waiting,private allocated memory and handle counts did not grow. Resident memory did rise by about154MiB. Priming reserves about1.9GBmore process memory earlier;that is a measured fixed preparation cost,not an indefinite stability guarantee.
- Primed idle and early cancellation exited normally. The unprimed control lacks a normal shutdown receipt;keep that limitation visible.
- Next investigation:attribute the existing busy threads with supported profiling. Do not add thread suspension or silently disable unrelated features. The current test remains bounded;this is not approval for an unattended infinite session. [Measurements](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-26-codex-material-startup-priming.md>).

### SFC-01 — Direct Remix API route

**PARKED — sponsor direction; isolated experiment, not selected for gameplay.**

- We register each ship's geometry and materials directly with Remix, then update its position and camera. D3D9 still supplies the device/presentation connection, but the experimental ship geometry does not use ordinary D3D9 draw calls.
- Four clean GPU controls covered four ship owners, three different model contents, shared geometry and a delayed ship. Illumination affected the first returned image.
- **Remaining:** camera placement/scale does not yet match the accepted D3D9 route; first-image appearance still changes as rendering settles. No complete visual-parity claim.
- **Resume when:** sponsor returns to the API/backend-readiness question after the rendering-family survey.
- **Exact restart action:** compare the API camera/viewport conversion with the existing recorded projection checks. Do not compensate by guessing a scale.
- **Game test needed now?** No.

Evidence: [Run164](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-24-codex-api-scene-proof.md>).

### SFC-02 — Initial loading below two seconds

- **Live material updates demonstrated (Run201):** enhanced materials now arrive without a shuttle/new-model trigger. Initial absence is difficult to notice except illumination. FCA enhanced files ready0.786s/library0.850s from discovery; not exact installed-pixel timing. Original glow currently shares the generated-roughness publication boundary. [Result and remaining work](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-26-codex-live-material-revision-result.md>).
- **Live confirmation (Run198):** first appearance correctly mapped/~1s; the enhancement is still delayed until later library activity. Ready CPU materials and installed renderer materials are separate states. Normal exit/cleanup/client checks pass; no reported visible frame loss, but small returned-image gaps are recorded. [Live result](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-26-codex-live-initial-mapping-result.md>).
- **Current result (Run196–197):** fast base-first display demonstrated in SFC; complete enhanced readiness still open. Initial mapping is now corrected in the Remix adapter and separately tested. Original settings/source data stay canonical. Initial GPU600/600; late595/600, only isolated misses. Shared-owner checker corrected without accepting arbitrary transforms. Failed notification and invalid emission-control experiments are recorded, not promoted. [Current evidence](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-26-codex-remix-initial-mapping.md>).
- **Optional checkout ready (Run194):** the supported single-file/asynchronous route is integrated behind `-AsyncMaterialCheckout`, with the shared-asset task lifetime bug fixed and a separate qualification gate.542Python tests, actual initial/shared/late graphics checks and both read-only preflights pass. Normal runtime remains available. First matching ship3.206s; last initial distinct asset admitted3.956s—target still OPEN. Next is one actual skirmish to confirm behavior before promotion. [Instructions and evidence](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-25-codex-async-material-checkout.md>).
- **Supported route tested (Run193):** fourteen offline attempts, twelve completed/two partial. The newer runtime can load and update materials asynchronously, but our layered library handoff did not preserve their appearance. The existing single-file publisher fixed that in isolation. Material controls and a later-arriving ship passed; final tests had only1/1/3 isolated returned-image misses, with no long gap. First output3.2–3.5s is not all ships loaded; last initial asset admitted about4.0s. Two-second startup still OPEN. A separate alias-preparation bug was corrected only in the diagnostic; integrate it before checkout. Normal runtime/settings unchanged. [Details](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-25-codex-candidate-hot-reload-qualification.md>).
- **Upstream fix identified (Run192):** NVIDIA's REMIX-5883 addresses freezing USD updates with background rebuilds and selective scene changes. Missing from our normal1.5.2source; included in release-linked1.6.1source. Earlier candidate workaround turns that route off; it also solved a real missing-material problem, so changing it needs an isolated regression test. This supported fix is now the next priority before more custom loader/profiling work. Exact SFC result unproven; normal baseline unchanged.
- **Completed-stage test (Run191):** three material-library writes instead of43; base assets still publish independently, final381assetfiles exact. Startup presentation0.70s but later2.78s gap remains. The diagnostic repeat caught3.42s waiting for queued rendering after a fast Present; it failed to finish resize checks and is partial. This is not a promoted fix. Next: prepare a bounded pinned-runtime NVIDIA trace, not another gameplay run.
- **Presentation investigation (Run190):** issuing draws is fast; material consumption is a strong remaining suspect. Pinned Remix source reloads its library and resets the scene when our master material file changes. A deferred-publication replay shortened bootstrap3.37→0.89s but shifted trouble later:2.8s returned-layer gap and520/600delivery. All381final asset files matched. A new normal-publication control crashed externally with0xC0000005; evidence retained, cause unassigned. Next offline test: one completed enhancement revision publication per asset, retaining immediate base textures. No launcher/default changes or startup target achieved.
- **Live checkout reviewed (Run189):** all61textures use initial pixels,0fallback, matching prior KFF/FCA content/settings. Sponsor sees no appearance-time improvement; measured first matching return3.68s versus3.89s. The specific upload fix works;2.84s startup draw/present remains. Existing standalone marks show individual Present-side waits over2.2s. Next attribution is offline; no more gameplay needed to verify activation.

- **Integrated for explicit checkout (Run188):** initial-pixel staging uses renderer-owned moved buffers; native D3D9/Ex exact-pixel/lifetime/reset tests pass in both architectures, and Remix confirms107fast/0fallback uploads. Normal default retained. Standalone first matching output6.27→6.11s is not a meaningful whole-pipeline speedup; late delivery gaps remain. The known lock is avoided; the larger startup target stays open.

- **Stall located (Run187):** more than99% of one1.48–1.85s resource admission was a16KiB staging texture lock. A documented initial-pixel creation route avoids it in isolated tests (~4ms construction) with accepted asset content. Normal adapter integration/native lifetime checks are next; other queue waits and late-material interruptions remain. One control's491/600 delivery fails qualification, so no overall startup/seamless claim or default change.

- **Latest live result:** faster asset production confirmed, no faster screen arrival. The renderer services new asset admission between render/output cycles, so it cannot admit while blocked in those output waits. That dependency is the next investigation; it does not yet explain every second. Client cleanup/hash checks passed. [Run185](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-25-codex-live-two-phase-result.md>).

- **Base-first split implemented:** no bundle wait for enhancement generation or secondary images; base submission precedes enhancement writes. Existing identity algorithms now run in memory, removing repeated helper launches/rereads. Captured FCA base0.51s; final images/materials unchanged.611checks passed.
- **Renderer limitation remains:** new-model test598/600 and delayed-material test599/600 looked good after settling, but full traces show roughly1–1.3second gaps during updates. No clean streaming claim/default promotion. Same experimental option remains explicit; no extra gameplay needed to diagnose this known issue. [Run184](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-25-codex-base-enhancement-split.md>).

- **Live parallel checkout worked:** correct new-path flags recorded; same ship content as prior stable run. First matching output4.49s→3.49s, both ships admitted by3.37s; sponsor reports~3s and no flicker or other issues. Five post-start omitted outputs versus22previously, with no invalid associations. Clean exit/hashes/settings passed. Materials prepared before first matching output, so the delayed-update stress gate remains open. [Run183](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-25-codex-live-parallel-checkout-result.md>).

- **Explicit experimental checkout ready:** normal launcher plus `-ExperimentalParallelAssets` now enables the new within-ship preparation and progressive materials for your requested live comparison. Known interruptions remain unresolved; default unchanged.521main checks and source/native qualifications passed. The preceding4–5s live run used stable mode with trims enabled, not this new route. [Run182 command and limits](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-25-codex-experimental-parallel-checkout.md>).

- **Parallel preparation implemented:** geometry and image work overlap within a ship as well as across ships. Ready ships no longer wait for the initial batch in the isolated path; completed materials publish by group. Exact final assets retained.600Python tests passed. Single captured-ship preparation2.58s→1.47s; full multi-ship visible loading still exceeds target.
- **Current blocker:** no-delay renderer delivered596/600 checked frames; delaying a material until ships were visible reduced delivery to538/600, below the existing540 minimum. New publication behavior stays offline-only. Stable gameplay path requalified at595/600; no SFC test needed yet. [Run180](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-25-codex-parallel-progressive-assets.md>).

- **Baseline implemented:** SFC's resource associations are authoritative. Performance default is consistent, repeated material source comparisons are Test-only, and bounded input/derivative reuse is in place.508main tests and standalone4-owner rendering check passed; gameplay qualification refreshed. Exact accepted material/image output retained. No overall startup improvement demonstrated yet; remaining rendering wait still needs attribution. [Run179](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-25-codex-performance-baseline.md>).

- **New investigation:** retained accepted run spends about2seconds preparing assets before activation, then another2.16seconds after submitting the first complete scene before its output is ready. The old startup warm-up accounts for only0.55seconds. A captured-FCA CPU replay reproduced the exact accepted materials/images and identified repeated file lookup, image decoding and duplicate encoding. No production optimization implemented yet. [Run178](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-25-codex-downstream-startup-profile.md>).

**OPEN — target not met.**

- **Sponsor priority:** make the complete scene fast first. If necessary, show the correct normally textured ship promptly and apply enhanced materials afterward, rather than leave it absent. This is an allowed fallback, not the primary performance fix or a claim that complete loading meets the target. [Decision](<C:/Project/SFC-Modernize Engine/docs/decisions/2026-10-25-progressive-material-readiness-priority.md>).
- **New earlier-data route:** traced ship creation to its model-name request, shared native cache, geometry/texture preparation and owner attachment. Native cache presence alone is unsafe: objects enter it before loading is complete. The best candidate is after the full loader returns, including optional scaling. We have not changed the rendering pipeline or measured a new speedup. Gameplay timing is next, before early capture. [Findings](<C:/Project/SFC-Modernize Engine/docs/reconnaissance/early-model-availability.md>).
- **Observer ready:** 58 native checks and the actual startup-loaded standalone fixture passed; four complete named model-to-owner timing chains, zero lost records, clean restoration and unchanged files. Ready for one normal gameplay measurement, not proof of faster loading. [Instructions and limits](<C:/Project/SFC-Modernize Engine/tools/early_model_probe/README.md>).
- **Launcher fix:** the first attempt stopped because our launcher read its status incorrectly—not because of SFC or its models. Fixed and requalified; the standalone test now exercises that same startup check. Retry the same command. [Run176](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-25-codex-early-model-launcher-fix.md>).
- **Actual timing result:** clean90second capture,94records/about47KiB. FCA native preparation91ms, KFF14ms; complete data leads their first recorded drawing by117ms/14ms. Normal game behavior confirmed; hooks restored and files unchanged. This supports focusing on our downstream delivery/material-readiness work, not finding more native loading time. Earlier metadata is useful, but no speedup implemented. [Run177](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-25-codex-early-model-timing-result.md>).

- Latest complete API ship set reached GPU output in **4.22–4.24 seconds** from first captured discovery. Earlier accepted D3D9 reference: **5.17 seconds**.
- The faster D3D9 experiment (~2.58 seconds) was not accepted: enhanced materials were missing in its first image.
- File-based material delivery and first-use work are confirmed concerns, but no single cause accounts for every millisecond. Moving to the API does not eliminate all startup costs.
- **API restart action (parked):** establish correct API camera/appearance before comparing quality-equivalent startup timings. Current investigation is the earlier native model-loading route above, independent of backend choice.
- Do not mark complete merely because a model, material handle or texture upload was accepted.

Evidence: [Run163](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-24-codex-initial-material-readiness.md>), [Run164](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-24-codex-api-scene-proof.md>).

### SFC-03 — Flicker and missed returned frames

**OPEN — greatly improved in earlier work, not eliminated.**

- Persistent ship tracking and synchronized whole-frame buffering are implemented. Looking away no longer means a living ship must be discarded and reconstructed.
- Independent hiccups were found outside shuttle arrivals. Late asset introduction can also interrupt the returned scene.
- The API controls still omitted some output frames: normal early windows delivered **592/600 and 594/600**; the delayed-asset control delivered **564/600**. These counts do not describe continuous freezes or original-game failure.
- **Resume:** once the backend choice is qualified, measure the remaining render/transfer/admission delays. Do not blame every interruption on camera movement or new ships.
- NVIDIA recording appeared to stabilize some sponsor tests; its causal effect remains **a hypothesis**, not a required fix.

Evidence: [hiccup review](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-24-codex-steady-hiccup-hypotheses.md>), [Run164](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-24-codex-api-scene-proof.md>).

## Pins — deliberately deferred, not forgotten

| ID | Item / status | Why it is parked | What brings it back |
| --- | --- | --- | --- |
| SFC-17 | **Current D3D9 live tuning — READY FOR SPONSOR CHECKOUT** | Live controls now use the fast1.6.1 ordinary-D3D9 return path; latest appearance R3 preserved with an external ZIP. Original ships remain. | Run5–10minutes, save edits and exit normally; inspect behavior and cleanup. ReShade preset contribution/extended gameplay not newly proved; do not silently change the saved baseline. |
| SFC-04 | **Original-ship replacement — PARKED** | Current proof adds a returned ship; disabling original drawing needs reliable matching output and correct depth/coverage. | Delivery and camera alignment qualified; prove one stationary replacement, safe fallback, then motion. |
| SFC-05 | **Grid, shields, weapons and overlapping objects — OPEN** | A ship image alone does not prove correct visibility against every retained game effect. | Before replacement acceptance: verify depth, grid crossing and effects layering, not just the ship's silhouette. |
| SFC-06 | **Simpler image-return connection — PARKED** | Current ReShade compositor and owned receiver work, but serial copy/acknowledgment may add overhead. Their ownership safeguards cannot simply be deleted. | Measured transport bottleneck or next interface increment; qualify any replacement with synchronization and state-preservation tests. |
| SFC-07 | **Renderer-independent interface / D3D12 — OPEN TECH GATE** | Run285: reusable capture/identity/camera/D3D9 foundation and per-owner replacement now demonstrated. Materials/lights/startup still partly Remix-specific; live source rows and D3D11 sharing need adapters. Current replacement has per-owner physical hull coverage; older union-mask-only claim is historical. | Package existing decoded scene/backend operations and completed-frame semantics for consumers; expose damage state independently when implemented. Document capabilities and validate an independent consumer. D3D12 needs its own qualified transfer adapter. |
| SFC-08 | **Supersampling — PARKED** | You prefer a higher-resolution render reduced to the display size; tested AA looked too soft. | After stable replacement/delivery: qualify resolution, memory and performance. Keep quality controls independent within the shared rendering profile; lighting remains separate. |
| SFC-09 | **Appearance tuning — PARKED for engineering** | Your latest accepted temporary settings remain the comparison baseline. More tweaking must not hide transport, camera or texture faults. | Once delivery/replacement is stable, resume lighting/material/image tuning against a fixed reference. |
| SFC-10 | **Longer identity survey / larger stress mission — PARKED; initial survey now SFC-15** | The prepared90second metadata survey begins broader coverage, but does not establish a whole-mission or universal survey. | Review SFC-15 results, then justify a longer/broader bounded mission if needed. |
| SFC-11 | **Remix1.6.1 candidate — ISOLATED** | Installed Toolkit updates do not automatically upgrade the pinned rendering runtime. Candidate binaries need qualification against current source. | A documented benefit justifies a separately pinned upgrade; rebuild and compare before promotion. Normal path remains1.5.2/API0.6.4. |
| SFC-12 | **Device-loss recovery / vendor shutdown warning — OPEN** | Clean process exits and tested resource rebuilding do not establish automatic renderer-host recovery. Vendor warning also occurs on the normal route. | A lifecycle/recovery increment; preserve ownership rules and qualify restart/resource generations. Do not guess COM reference-count fixes. |
| SFC-13 | **All light types / effects-light coverage — LIMITED** | Qualified native lighting is wired; full coverage of dynamic effects is not implied by editable controls. | Broader scene/effects integration requires measured light identity/state and correspondence. |
| SFC-14 | **Arbitrary dynamic/damage geometry — UNQUALIFIED** | Supported captured rigid meshes and observable revisions work; unannounced in-place deformation is not established. | A mission reveals such changes, or broader model support requires a focused change-detection test. |

References: [interface audit](<C:/Project/SFC-Modernize Engine/docs/reconnaissance/2026-10-24-live-interface-second-audit.md>), [future-renderer gate](<C:/Project/SFC-Modernize Engine/docs/decisions/2026-10-18-renderer-independent-boundary-gate.md>).

### SFC-23 — First launch after restart or long idle — RESOLVED LOCALLY, PARKED

November 6, 2026. The post-reboot trace attributed 19.11 seconds of main-thread
waits to Defender. The sponsor confirmed the usual pause was gone on the first
launch after a fresh restart with a folder exclusion scoped to the test copy's
mission scripts. The reason for the unusually long scan remains unknown.
[Capture procedure and findings](reconnaissance/sfc23-startup-capture.md).

## Already demonstrated — do not rediscover blindly

- **PROVED / LIMITED:** semantic ship/model ownership, supported fresh in-memory geometry, original texture associations and live transforms. Geometry is not supplied by exporting installed model files to OBJ.
- **PROVED / LIMITED:** game-camera observation, simulation-driven tracking, geometry reuse and distinguishable retained ship owners. Camera visibility is not object lifetime.
- **PROVED / LIMITED:** multiple different ships through the D3D9 in-game route; supported fighters also appeared. Older single-FCA README statements are historical, not the newest coverage record.
- **PROVED / LIMITED:** genuine Remix pixels returned inside SFC's frame through our ReShade add-on; this is not a desktop overlay. Original gameplay and drawing remain available.
- **PROVED / LIMITED:** adjustable lighting, materials, image controls and quality configuration. Those controls are separate systems; a lighting ratio is not automatically valid for every light type.
- **FIXED:** corrected D3D9Ex resource/upload policy and removed unnecessary live diagnostic work in the interface cleanup.
- **FIXED:** removed the live renderer's6,001-iteration stop; explicit source stop and elapsed safety limits now govern lifetime. This did not resolve startup or every hiccup.

Evidence: [authoritative handoff](<C:/Project/SFC-Modernize Engine/docs/HANDOFF.md>), [Run160](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-24-codex-interface-cleanup-first-pass.md>), [Run162](<C:/Project/SFC-Modernize Engine/docs/runs/2026-10-24-codex-live-lifetime-cutoff.md>).

## Milestones and guardrails

- M1's recorded disposition is **technical validation complete; sponsor closure review pending** in the approved plan. Do not infer formal closure from later graphics experiments.
- M1 integration evidence is not overall TRL4. The approved amendment assigns combined enhancement/visual-benefit evidence to the later M2 checkpoint.
- No full renderer replacement, universal model support, seamless delivery or finished graphics mod is claimed.
- Preserve the accepted Community Edition installation and original assets. Use the verified separate test installation.
- Normal gameplay path is unchanged by the isolated experiments. Run163–169 work remains **unstaged and uncommitted** at checkpoint `fd79ce5`; no push.
- Existing evidence cap: **20GB**, with approximately **19.00GB** used by governed evidence plus isolated API/survey/effects builds at Run169 review. This is a dated snapshot, not a live disk gauge; launch checks include archive reservation.

Authority: [M1 plan](<C:/Project/SFC-Modernize Engine/docs/m1/m1-trl4-integrated-component-validation-plan.md>), [approved gate amendment](<C:/Project/SFC-Modernize Engine/docs/decisions/2026-10-14-m1-m2-gate-allocation-amendment.md>).

## How to keep this useful

1. Keep the stable SFC-IDs when an item moves between current, parked and completed.
2. When putting a pin in something, record **why**, **what reopens it**, and **one exact next action**. Link its evidence where available.
3. When closing an item, retain its outcome and evidence; do not delete the history or silently mark related work complete.
4. Update this tracker with the repository handoff after a meaningful result, decision or newly parked item. Keep technical detail in run records.
5. The repository master is `docs/STATUS.md`. The Obsidian note is a copied snapshot, **not automatically synchronized**. Refresh both together; preserve any user notes before replacing the Obsidian copy.

## Checkpoint history

- **2026-10-25 — Run169:** first real effects run proved one native producer/texture/primitive connection and hit its byte cap early. Two faster-combat runs completed but used other, still-unclassified paths. All games normal; no repeat unchanged capture requested.

- **2026-10-25 — Run168:** targeted effects observer implemented/offline-qualified. No proxy or renderer changes; actual game test ready. Fixed a startup-loader export defect in the isolated fixture. No SFC gameplay launched during preparation.

- **2026-10-24 — Run167:** concrete missile-associated effects routine traced to shared fx0 resource selection and four-corner submission.38static anchors verified; live owner/resource join defined but not implemented. API parked, no gameplay required yet.

- **2026-10-24 — Run166:** both actual surveys reviewed, including sponsor-reported enemy destruction in the second. Confirmed graphics-state families and native call sites; producer/owner joins remain open. Both captures reached their byte cap around85s; clean exits/restoration and unchanged hashes. No new broad run required.

- **2026-10-24 — Run165 started:** sponsor parked the API experiment and authorized broader rendering-interface characterization. SFC-15 is current; SFC-01 retains its exact restart point.

- **2026-10-24 — Run164:** API submission proved offline; startup target, camera parity and late-delivery continuity remain open. Normal gameplay backend retained.
- **2026-10-24 — Run163:** confirmed that the fast ordinary-D3D9 first image lacked the enhanced material response. Preserved accepted startup behavior; sponsor then authorized the isolated API experiment.
- **2026-10-24 — Tracker created:** current work and parked decisions consolidated from repository handoff, audits, approved decisions and run evidence. No new rendering work or milestone decision.
