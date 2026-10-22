# Run67 — native depth available; additive depth display PARTIAL

Date2026-10-19 America/New_York. Starting/current HEAD
`d29111f7a513c4510c4d33aeeda2c355d98443a5`;Run65/66 changes preserved,index empty.
Authority:Run66 and REMIX-SCENE-DEPTH-001. Sponsor reports "flickering mess" and
suspects copy too low. Flicker is CONFIRMED observation;low-placement cause remains
unconfirmed. No normal-gameplay/no-issues assertion inferred from this report.

Reviewed actual run`artifacts/remix-runtime/runs/20261019-222440-846106-in-game`:
result/manifest,fresh-asset association,host log,current receiver/depth/compositor,
offset calculation and transport. Fuel Guard exact-thread hook verified;no daemon,
helper,new gameplay,build or implementation edits during review.

## Direct runtime evidence

- Native1920x1080 8MSAA depth qualified3646of3652receiver frames;6ambiguous,
  wrong-thread0,unsupported0,depth failure0,one resource epoch.
-1227outputs rendered,1226acquired,1060drawn/displayed;166pose/camera mismatches,
  one late rejection,private failures0. Display count/qualified frames is29.1%,
  not a pixel-coverage or exact frame-time measurement. Main blank-frame source
  is NOT widespread failure to locate depth.
- Current source resets drawnAt each receiver step and displays only a newly
  acquired,qualified result.30Hz async producer cannot fill every faster game
  frame. This directly explains missing-frame cadence;166state mismatches add
  refusals. No need for another identical sponsor run to establish this defect.
- Run elapsed121.797s including startup/exit;capture limit90s unchanged. Normal
  game exit,gate unload/controller0,renderer0,proxy rollback,launcher settings
  and accepted critical-file hash checks PASS. Original suppressed=false.
  Existing SDK40common-object shutdown warning persists despite renderer exit0.

## Placement adjudication

Fresh association records world offset`[0,14.361175537109375,0]`,chosen as initial
camera-right displacement(screenfraction-0.2),not an intentional lower-screen
offset. Initial recorded composed transform changes horizontal translation only;
vertical homogeneous row unchanged. This does NOT prove later on-screen height
or clipping is correct:offset remains world-fixed as camera changes,and depth
filtering may hide parts. No screenshot/pixel-depth pair recorded in this mode
can independently confirm sponsor's low-placement impression. Do not equate the
world Y axis with screen down or adjust height by eye.

## Decision / exact next action

PARTIAL:actual native scene depth access is CONFIRMED;useful stable visual
occlusion/replacement is NOT demonstrated. Stop repeating current gameplay probe.
Next smallest implementation is receiver-owned cached RAW color/depth/picking
with bounded GPU-safe acquisition,then re-filter each current native frame only
while session/owner/revision/pose/camera and freshness still match. Do NOT hold a
previously depth-filtered image,read a released producer surface,relax identity,
or suppress originals. Offline steady paused-state and current-depth-change tests
must pass before another sponsor run;placement stays separately unresolved.

Only this record,HANDOFF and probe/readiness disposition changed in review.
No implementation fix applied yet. Original evidence unchanged,no image dump.
Final index empty;all prior/current changes unstaged/uncommitted,no push.
Validation:JSON fields checked against source/logs;documentation links and
`git diff --check`. No game/owned host process returned by process inventory.
