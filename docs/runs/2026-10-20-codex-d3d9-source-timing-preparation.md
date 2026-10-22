# Run76 — read-only source lead/presentation timing preparation

Date2026-10-20 America/New_York. READY FOR SPONSOR READ-ONLY TIMING TEST;
no gameplay executed.
Authority:approved additive execution plan and sponsor continuation. Run75
established bounded ordinary-D3D9 output/receiver and short1080p throughput,
not how early SFC makes a coherent frame available. HEADd29111f7,index0;
all earlier dirty changes preserved,no stage/commit/push/helper/agents.

## Specific missing fact

Measure first and last same-state semantic offers relative to actual copied-game
Present and overlay callbacks,including repeated/changed frame,owner,revision,
pose,camera and thread association. No nearest-timestamp joins. Counter alone
is not a frame seal. Throughput~12ms does NOT establish adequate game-frame lead.
No whole-frame buffering,prediction or relaxed identity selected by this work.

## Implementation so far

Default-off SFC_D3D9_SOURCE_TIMING=1 annotates previously unused calibration-row
words89..93 with first/last QPC plus explicit extension magic. Existing96word
layout,Snapshot/header/version and reserved fields unchanged. Annotation only
when calibration active;existing17word state,pose/camera ranges and semantic hook
sites/ABI untouched. Same owner/frame repeated identical offers preserve first
timestamp and update last;conflicting states still become ambiguous,status3.

Metadata-only Observer reads existing verified16MiB current-user scene mapping.
Store at12MiB,128byte header+32768x80byte rows=2,621,568bytes;at most8detailed
owners/callback,counters after saturation. Callback path uses preallocated data,
one try-lock copy,QPC/hashes/stores only;no graphics state changes,file access,
allocation,waits or calls into viewer. Present and overlay stages distinct.
Device recreation preserves same-session evidence instead of resetting it.

New standalone fixture publisher stamps synthetic rows ONLY in return_fixture;
never supplies fake rows to SFC. Reuses verified startup/proxy fixture and checks
unchanged native graphics state,resize and device recreation. Native source
timing tests18checks PASS;build/source qualification ongoing. No sponsor test is
ready until offline fixture,parser,ABI/regressions and cleanup checks pass.

Changed existing component/source calibration headers mean old source-qualified
gameplay receipts must NOT be reused blindly. Preserve old evidence;requalify
relevant workflows before gameplay. Native builds currently active;inventory
tool/process sessions before restarting. No game/process started by this unit.

Exact next action:finish return/component builds and metadata-only standalone
fixture,then prepare bounded gameplay runner only if offline evidence passes.

The preceding next-action/build text is historical during this run;final prepared
state and exact next action are below.

First actual proxy fixture044913-635514:graphics state/resize/recreation and
normal exit pass,but418callbacks reject synthetic snapshot header,0records.
Cause found in fixture publisher:zeroed shared memory did not run Snapshot's
default member initializers;publisher failed to initialize magic/version/bytes.
The real component already initializes Snapshot correctly. Fixed ONLY fixture
initialization;do not weaken observer validation. Preserve first partial result.

## Final preparation / actual offline evidence

Corrected045048-901453fixture:418metadata records/209exact frame-owner pairs,
wrong-thread/invalid/drops0;actual native graphics state unchanged through resize
and device recreation. Final-source qualification050039-941168:416records,
208exact pairs,both stages,pose/camera changes between stages0,all loss/invalid
counters0,normal child/host exit0. These are SYNTHETIC standalone source rows;
their microsecond lead times are NOT SFC measurements. PID10628matches verified
suspended-path/hash child;host log confirms OBSERVATION_ONLY/no runtime loaded.

Native source timing18checks,return wire37,expanded wire13,broad metadata14,
calibration22and full M1 native build/contract/tint/shading/copy/mesh/forwarding
regressions PASS. Actual LiveScene capture/multi-owner/QPC-before-throttle/worker
tests PASS in qualification fixture,not merely isolated timestamp helper tests.
330Python tests PASS4.400s. PowerShell parsers/launcher qualification expression,
no-execute gameplay preflight and git diff --check PASS. Both client hashes
unchanged at4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.
No sponsor appearance TOML changes or source/proxy/install/security modifications.

Prepared mode --source-timing --observation-only uses existing verified copied-
game startup/auto tactical gate,90seconds,explicit prep/camera/movement cues,
normal hook restoration/unload/exit/hash checks. No image/Remix load/extra ship.
Runner retains32MiB combined cap/16MiB warning and reserves2.6MiB for final
metadata export;64MiB global reservation within10GB. Game/sponsor actions needed
only for real tactical state and visual/control observation. No timestamps/RE/UAC.

Exact source/binary qualification stored at
artifacts/d3d9-proof/source-timing-qualification.json. Startup verifies these
prepared files without rebuilding/invalidation during the gameplay budget.
Current add-on SHA2563AF7C07A3F2D66C11B924C0A80676F03407075CD6760EBF29C27755752761B92;
component250FB2D50498305F88246E273794C7D08B59CA184FA9AEDB1BD51BECCC13A5DD.
Old source-qualified SDK/private-gameplay receipts remain obsolete;do not reuse
those launchers blindly. This qualification authorizes only the read-only probe.

Three finished source fixtures'generated binary INPUT copies13,609,288B zipped
to6,278,400B;decompressed hashes verified before removing only those9copies.
Raw metadata,analyses,logs,original build outputs and all source captures remain.
Initial partial044913input copies retained because archive guard rejects its
nonzero observation-host shutdown;no safety guard weakened. All archives recoverable.
Counted output9,822,558,358B/10GB. No active game/host/fixture/build;no hidden session
must survive. HEADd29111f7,index0,18modified tracked/78untracked files after this
curated receipt;all previous/current work unstaged/uncommitted,no push.

## Files / checkpoint

Created:source_timing.h,start_source_timing_session.ps1,source_timing_addon.h,
source_timing_fixture.h,source_timing.py,qualify_source_timing.py,native/Python
source timing tests,D3D9-SOURCE-TIMING-001probe,this run and curated receipt.
Modified:m1_present_calibration.h,m1_live_scene.h,m1_live_scene_tests.cpp,
return_addon.cpp,return_fixture.cpp,run_return_fixture.py,run_return_game.py,
start_return_image_session.ps1,build_receiver.ps1,archive_fixture_binaries.ps1,
CLI regressions,README,HANDOFF and active execution-plan progress. No helper.

Decision:offline preparation CONFIRMED;real source-to-present lead/sealing UNKNOWN.
Do not implement current-frame presentation,prediction,buffering or relaxed
identity before this evidence. Unqualified1280x360output and runtime disposal
warning40from Run75 remain separate findings;fixed1920x1080pixels qualified.

Exact next action:sponsor runs tools/d3d9_proof/start_source_timing_session.ps1
from the existing elevated parent,enters familiar two-ship skirmish,keeps both
visible without pausing,follows high/low beep instructions,exits at two low beeps.
Then Codex adjudicates actual source timing. No additive image test yet.
