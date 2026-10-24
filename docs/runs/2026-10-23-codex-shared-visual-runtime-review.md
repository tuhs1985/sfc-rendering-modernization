# Run122 — actual shared-visual owner collapse CONFIRMED

2026-10-23 America/New_York. Read-only technical review of completed
artifacts/remix-runtime/runs/20261023-191630-707670-in-game. Sponsor reports two
distinct Klingon models this time,one Klingon missing;asks whether FCA remains
unfixed. No source/config/budget change,game launch,helper or subagent.
Starting/final HEADd40f8f230fc7504023e4a052c99a81b5a08ce6b4,indexempty,all inherited
work preserved unstaged/untracked. FuelGuard attached via trusted hook.

## CONFIRMED findings

The new native census retained47tuples/114,287observations,zero omitted,covering
0–119,985ms and7198frames. Approximately10.6KiB JSON. Six distinct native ship
addresses,NOT11ships:11ship/epoch pairs include repeated retirement/readmission
of the SAME missing ship. The render callback/source chain was not capacity-full.

| Captured owner | Model | Result |
| --- | --- | --- |
| 1 | KDD | admitted,5266draws |
| 2 | FDD | admitted,5265draws |
| 3 | FCA | captured,but conservative aggregate image-output budget blocked |
| 4 | FFF | admitted,5263draws |
| 5,then7–11 | second KDD native ship | observed,but model lookup selected owner1 |
| 6 | KFF | admitted,4345draws |

Actual shared identity,all within this one session:
- First KDD native ship0x18FB37A8,owner1.
- Second KDD native ship0x18F84F88,initial owner5.
- Both visual0x18D676B8,model0x17A503BC,source0x04CF35A8.
- Atframe1273/time21,250ms,ship and visual observations assign second shipowner5;
  immediately following mainline model callback enters with that qualified
  context,but existing first-match visual lookup selects owner1 and rewrites
  event/thread ship to0x18FB37A8. Native vtable guards pass.
- Six aggregated mismatch tuples,4482model callbacks total,contextowners
  5,7,8,9,10,11all wrongly choose1. This is direct runtime corroboration of
  Run119's static first-match ambiguity,not merely similar filenames/content.

Missing ship never reaches persistent registry/asset capture as its own instance.
Render-observation owner epochs5,7,8,9,10retire atframes2036,2680,2863,4081,5315;
same native ship reappears under later epochs. Static path confirms only admitted
persistent entries receive visibility-independent retention;unadmitted duplicate
has no such protection. This churn is our bookkeeping,NOT evidence of six native
ships or native identity change. No tracked native destruction in persistent
registry;seven destroy-hook invocations do not prove seven ship deaths.

FCA untouched by prior instrumentation changes. Fresh asset3JSON explicitly names
assets/models/fca/fca.mod and owner3;backend partial reason remains
`Cohort conservative image budget;asset postponed as partial`. Aggregate image
accounting133,335,826of134,217,728bytes,881,902remaining;115unique original images.
Do not call this GPU-memory exhaustion or increase cap under cover of this review.

## Delivery and cleanup

Five captures/transfers,zero capture failures,owner overflow,invalid records or IO
failures. Persistent5admitted,34,705publications/27,507offscreen,zerofailed updates.
Four assets admitted;four distinct owner instances drawn. No cohort header/packet/
identity lookup failures or input-admission rejection.41projection rejections
remain recorded;not adjudicated as caused by ownership without further evidence.
Paired5244of5514synchronizedrecords,268withoutship,onewarmup/onereset;zero failed
or dropped synchronized audits. This is not a seamless-delivery or universal
coverage PASS;known late-material stalls remain separate.

Final report complete,errornull,PARTIAL due unsupported coverage/budget. Normal
game exit,controller duration stop,hook restoration/unload,rendererexit0,
launcher settings and all original/copied critical hashes restoredPASS.
Sponsor did not separately report HUD/control behavior in this message;do not
invent a new all-behavior acceptance. Actual duration174.828seconds,within285.
Run folder140,621,943bytes;native eventlog613,857bytes,nottruncated. Raw captures
remain ignored,preserved for the fix. No cleanup/deletion necessary this review.

## Engineering disposition / exact next action

Enough evidence exists to implement a bounded contextual-owner correction:
preserve the validated incoming native ship/owner through the model callback,
allow shared visual/asset identity without merging instances,and retain existing
native guards and epoch/lifetime checks. A visual-only fallback must not silently
choose among multiple matching living ships. This is the next proposed change,
NOT implemented or authorized by this sponsor result-report alone.

Separately audit conservative image accounting and content sharing to admit FCA
within existing budgets before considering any cap change. Earlier preload is
still an unimplemented optimization;not a prerequisite to fixing confirmed wrong
owner association. No further discovery gameplay run needed for shared-visual
root cause. Validate two shared-asset owners plus distinct thirdasset offline,
then repeat six-ship runtime after sponsor authorizes the fix.

Validation:reviewed raw census,asset3references,capture/registry/lifecycle/output
summary,controllerlog and production lookup/retirement source. Versionable
evidence alongside this record preserves hashes;gitdiff--checkPASS. Onlythis
record,evidence and HANDOFF changed;no staging/commit/push.
