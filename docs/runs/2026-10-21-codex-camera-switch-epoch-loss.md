# Run92 — camera switch hides copy permanently;epoch recovery missing

2026-10-21 America/New_York. Sponsor reports switching camera to target and back
loses overlay. Diagnosis only:no request to implement a new identity protocol.
Read HANDOFF/Run91,latest actual run/source tracking/relay/input code. Fuel Guard
attached via trusted hook,no daemon. HEADd29111f7,index empty,prior dirty work
preserved. No SFC/renderer launch,helper/agents/stage/commit/push.

## Direct evidence

artifacts/remix-runtime/runs/20261021-044306-807238-in-game selected owner2/revision2
FCA,accepted asset hash3aa4a80fa4eadfdabee6632e0c8fd05476e3b2c3787e25cbc271c4dd95863a36,
new reduced camera-left gap15.8977227units.1443pool draws,last source frame1798.
Native transport received1508,invalid0,unqualified0,source rejected0. Observer1444
matched,66old/different,1no completion,914ineligible. Pool46stale,zero invalid/
resource/depth errors. No light omissions;host/receiver normal exit0,not a crash.

Fresh gate capture has original FCA owner2/revision2packet and later FCA owner4/
revision4packet(firstframe1864). KFF also reappears with owner3atframe1799. All
captured original2and returning4geometry hashes identical:
16981bd6f5b84f8d9f17f1395a92b34011387ddba5e1a64fbff4b21bd81e65a5.
Decoded rendering groups AND resource association records compare exactly equal.
Model/visual/source process pointers in packet headers also match,but pointer
equality is NOT accepted proof of persistent object identity or permission to revive
an old epoch. Captured state logs are bounded first~100records/owner;owner2state
rows ending292do NOT mean rendering stopped there. Host/pool receipts establish
continued selected-owner rendering through1798.

## Cause / confidence

CONFIRMED code:m1_component.cpp kScene calls g_owners.retire_before(frame-2),
then live scene retires that owner. This is conservative observation-lifetime policy,
not proof game object was destroyed. Once ship returns to semantic path,new epoch
and fresh asset revision are allocated. Camera change can therefore invalidate
selection even when original game model/pointers still exist.

CONFIRMED mismatch:live_owner::Source::offer only publishes selected(owner,revision).
LiveOwnerInput::start binds initial2/2and next only accepts matching owner,revision,
model/source. Relay::poll returns early whenever renderer process already exists;
there is no current reselect/requalification/rebind path for4/4. Thus fresh returning
ship was captured,but renderer remains waiting for2/2. Hiding stale output is correct;
failure to qualify and reconnect the returning epoch is the missing behavior.
Sponsor camera-switch trigger plus sequence is direct evidence;precise action
timestamps not captured,so do not label every gap as a specific button press.

Not a texture flip,projection scaling or GPU timing failure. Do not weaken exact
frame/epoch checks,disable retirement,extend lifetime arbitrarily or reuse cached
pixels to mask this. No original-render suppression or capture-seam invalidation.

## Bounded correction proposed,NOT implemented

Safely hide retired selection;observe fresh unique configured FCA owner;qualify
fresh mesh/groups/image provenance against accepted content,not native IDs/pointers.
If content is identical,resident GPU assets can be reused with NEW owner/revision
identity. Acknowledged rebind/generation transition must invalidate queued old
input/output/lighting state before new frames can display. Different geometry/LOD,
ambiguous same-model owners or insufficient provenance remain explicit unsupported
until qualified. No enemy substitution or multi-owner expansion as a shortcut.

Test camera-away/return with fresh epochs,delayed old completions,pointer reuse,
asset mismatch,ambiguous owners,repeated transitions and disconnect/shutdown.
Retain bounded memory,nonblocking SFC callbacks and current visual/scale corrections.
No protocol/design implementation done in this diagnosis. Exact next action:
implement and offline-validate the bounded fresh-epoch requalification/rebind path.

## Runtime safety / repository state

Normal game exit0/renderer0,critical files/settings unchanged,proxy restored.
Run ended before requested tactical window completed;result error
"Game exited before the requested tactical observation completed". Controller8,
controlled live-hook unload NOT confirmed;process-exit reclamation only. No generic
gameplay-normal/full-duration/cleanup PASS claim. Do not discard valid lifetime
evidence because the run is partial. Raw capture/manifests/logs retained unaltered;
no CompletedGame archival attempted. Vendor warning40still unresolved.

Files:this record,curated JSON,HANDOFF/probe status note only. Validation:packet
decoder/checksum validations,old/new geometry/group/resource equality,host/pool/
controller/result review,JSON/path/diff checks. No native/Python changes or new test
suite run;previous377tests historical,not a recovery test. Index empty,all work
unstaged/uncommitted,no active owned runtime. Existing launcher can reproduce bug,
but is NOT READY as a corrected camera-recovery test. M1 CONTINUES,recovery OPEN.
