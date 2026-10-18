# Codex run — broad depth discovery runtime review

Run SFC-RETURN-20261017-11,2026-10-17 EDT. Sponsor completed prepared run and asks
to analyze evidence. HEAD e96765a,existing dirty work/indexempty preserved. Read
HANDOFF,approved broad contract/probe,actual manifest/result/logs/binary trace and
pinned ReShade format/pipeline declarations. FuelGuard actual-thread recent-hook
verified;no daemon/helper/delegation/new game launch/staging/commit.

## Executive result

**CONFIRMED: a persistent full-screen D32_FLOAT depth view is bound during the
dominant observed draw path,then unbound before presentation.** Earlier negative
bound-getter observations did not establish absence of depth. This is a strong
tactical-depth candidate,NOT proof its values/coverage are usable for replacement.
No ship suppressed,new renderer output,or milestone PASS claimed.

Actual run20261017-182017-086947-in-game,verified copied PID16824. Tactical detail
10.0002166s,600Present notifications,141,285records,18,084,608Braw;zero dropped,
queue remaining0,error0,warning0,reason1duration. Full prepared execution38.438s.
Established2GB trace/1GB warning/32MiB ancillary/10GB overall bounds respected.
Native whole trace spans startup lifecycle/bindings plus tactical detail;do not
divide startup event counts by tactical time as an exact steady-state event rate.

## Exact evidence / confidence

|Evidence|Result|Confidence|
|---|---|---|
|Resource creation seq909,label0x0BF7B624,device0x0BB0A54C|1920x1080,R32_TYPELESS39,8samples,usage11504;not destroyed in captured window|CONFIRMED runtime descriptor + pinned SDK enum mapping|
|View seq912,label0x0BF66980|Same resource,D32_FLOAT40,depth-stencil usage48|CONFIRMED|
|View seq911,label0x0BF7200C|Same resource,R32_FLOAT41,shader-resource usage192|CONFIRMED view creation;GPU readability/use not exercised|
|DSV-associated draws|67,290nonzero draws:64,760indexed +2,530nonindexed;1,205other draws have no recorded boundDSV|CONFIRMED binding relationship,NOT proof depth testing/writes|
|DSV binds|703total:98startup/pre-gate,605after gate|CONFIRMED;not owner/object identity|
|600Present notifications|All600 have DSV unbound on context linked via explicit execute-command-list event|CONFIRMED recorded API state;not invented pointer-offset matching|
|599complete frames|Depth-associated drawing then unbind beforePresent;exactly2later unbound draws in each|CONFIRMED ordering;HUD versus composition roles unresolved|
|Four depth-stage pipeline handles|600/2,274/63,524/892draws;no dynamic depth enable/write/compare values observed|CONFIRMED handles/counts;static state descriptors unrecorded|

First capturedPresent falls partway through a frame after gate;no detailed prior
draws in that partial frame. Analyzer resets per-frame evidence,never carries an
old frame's draw into an empty new frame. Device/view/resource labels are process
local and must never be reused next run;creation sequences define associations.

Sample complete frame:seq4838last DSV-bound indexed draw;4839color resolve;
4840unbind;4853/4859non-depth four-vertex draws;4860resolve into backbuffer;
4861explicit queue/list link;4862Present. Context0x0680A308 andqueue0x0680A304
linked by record4861,not guessed from address proximity. Last logged unbind is
4857;first unbind4840 occurs earlier. Target changes between these are preserved
in raw trace. TwoMSAA color resources seq903/1055 each feed presented backbuffer
0x0BBB9D64 on300final resolves. Its creation descriptor is not observed (implicit
backbuffer),so do not invent one. No copy/resolve of the identified depth resource
appears in the enumerated captured transfer events;not an exhaustive GPU claim.

## Meaning / next missing facts

The depth resource survives while no longer bound;it was put aside,not shown to
be destroyed. An already-created shader-readable view provides a credible route
to test its contents without another translation wrapper. However 8sample data
must be handled explicitly,not treated as ordinary single-sample pixels.

Still unproven:actual depth values/ship silhouettes,depth enable/write/compare
for four static pipeline objects,correct frame/camera/depth interpretation,
which non-depth work contains HUD/effects,and owner-specific visibility/coverage.
No depth-clear callback appears;do not infer it is uncleared (shader/internal
clears are not excluded). No semantic owner was attached to these generic API
records. Candidate plus bound draws is not sufficient to suppress an original.

**Exact next action:** design/offline-validate one bounded read-only depth-content
snapshot and static depth-state observation for the proven path. Discover fresh
resources by current session/device/creation lifecycle,not labels above. Preserve
original graphics state and handle MSAA explicitly. Compare depth image with known
ship/camera view before composition/suppression. No new gameplay test is prepared
or started in this review;do not repeat broad capture unchanged just for volume.

## Mechanical validation / risks

Controller exited0:gate activated,hook bytes restored,DLL unloaded. Original
launcher CHILD_EXIT code0,observation-only host exit0. Result errornull,normal exit
true,gate clean true,proxy restored true,original critical/settings unchanged.
Copier restored original proxy/config;read-only broad preflight passes. Both
clients remainSHA2564D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29;
copied proxy E35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7.

Actual full-support ReShade log shutdown warning remains:
`Reference count for ID3D11Device0 object 0BB0A548 (0692B6F4) is inconsistent (67).`
Normal process exit/rollback is not warning-free internal cleanup;cause/impact
unresolved,not a quantified leak. Previous58warning and Remix40-object/driver
risks remain historical/open;no Remix runtime was loaded here. Sponsor subsequently
answered the explicit visible-behavior question: "Yes—normal, no issues" for game,
HUD,targeting,controls,new stutter and visual problems. CONFIRMED sponsor observation
for this bounded run,not instrumented equivalence or resolution of internal warnings.

## Reproducible offline analysis / files / tests

New tools/remix_runtime/inspect_broad_depth.py reconstructs bounded resource/view
lifetimes,context/pipeline state,explicit queue/list joins,per-frame ordering,
transfer edges and related SRV views. Never dereferences recorded native labels.
No instrumentation/component change. New tests/test_inspect_broad_depth.py covers
positive transient/srv association,stale-frame reset,unknown queue,implicit
backbuffer,explicit versus unknown state and device retirement. Full Python141
tests PASS2.307s,projectTEMP/TMP. No native rebuild needed. Existing capture
qualification remains current;read-only runtime preflight PASS.

BundledPython3.12.14 commands:

```text
tools/remix_runtime/inspect_broad_depth.py artifacts/remix-runtime/runs/20261017-182017-086947-in-game/broad.bin
-m unittest discover -s tests -p test_*.py
tools/remix_runtime/archive_broad_evidence.py artifacts/remix-runtime/archives/20261017-182017-broad-depth-evidence.zip artifacts/remix-runtime/runs/20261017-182017-086947-in-game
```

Generated broad.depth-path.json preserves full analysis,raw SHA256
CB10781A2940EFA1288F713316856826F4A0347A7F90E3B3147A4C9FB11D71C7.
Curated versionable evidence:docs/reconnaissance/evidence/20261017-broad-depth-runtime.json.
Also changed this record,HANDOFF,readiness map and probe conclusion. No original
manifest/result/packet overwritten,no image/geometry dumps. Verified ZIP:
1,865,077B,14entries,18,197,249Bsource,SHA256
DDB6C8159F63E26BC94FEBB7456ACB02AA17FC03FE65CA7A46EAE0A4A04915ED.
CRC verified;small18MB raw retained,not deleted. Total far below allowance.
Final indexempty,HEAD e96765a;all existing/new changes unstaged/untracked,no commit.

## Sponsor-confirmation follow-up — 2026-10-17

Closed the pending visual-behavior check using the explicit sponsor response above.
Updated only this record,HANDOFF,and curated evidence JSON;original runtime result,
logs and archive remain unchanged. FuelGuard attached to actual thread;no runtime,
implementation,staging or commit. JSON parse and git diff --check PASS;index remains
empty,HEAD e96765a,prior unstaged/untracked work preserved. Depth-content validation
and native reference-count warning remain unresolved;exact next action unchanged.
