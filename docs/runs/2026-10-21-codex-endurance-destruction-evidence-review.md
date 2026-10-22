# Run93 — historical endurance destruction evidence review

2026-10-21 America/New_York. Sponsor asks check earlier endurance enemy explosion
before requesting a short player-ship destruction test. Read HANDOFF/Run92,original
endurance run/evidence/probe/config,retained raw CSV/summary and archive. Fuel Guard
attached trusted hook,no daemon. HEADd29111f7,index empty,existing dirty work
preserved. Read-only evidence review;no SFC/renderer/helper/agents/stage/commit/push.

## Verified existing evidence

Identified correct run:artifacts/m1/runs/20261014-005117-enabled,component0.13,
M1-CLOSE-ENDURE-001. Sponsor previously reported enemy destruction near end.
Main archive artifacts/m1/archives/M1-CLOSE-ENDURE-001-20261014-005117.zip has
SHA2562380E4A9C905EC7550621F7E02C377531424739D273428B1EC1EFBB1095E7220,
matches original record. All22ZIP entries independently compared with retained
raw files by SHA256;all match. No extraction,archive edit or source removal.

Detailed semantic CSV1189records covers elapsed0..2109ms,frames0..119 ONLY.
Counts:ship_owner240,visual_model237,model0356,visual_exit237,scene_begin119.
No owner_retired event in this initial detail. Summary confirms detailed_saturated
true,frames_observed109688,owner_retired9,geometry hook OFF. No per-owner final
lifetime table or destruction-specific state exists in summary. Config MaxFrames120,
MaxEvents10000,MaxOwners8;detail ceased by frame cap intentionally,not corruption.

Frame/memory telemetry persists through1800s but does not identify destroyed ships,
gameplay hull/death state or object release. Component continued1830s;last30s have
no frame telemetry. No explosion timestamp links sponsor observation to a frame.
Nine summary retirements cannot distinguish camera gaps from actual destruction.
Relevant existing semantic maps contain no already-qualified tEntityShip death/
destructor relationship found in narrow read-only search. No new RE performed.

## Result / next action

CONFIRMED:archive intact and valid endurance success on original intended scope.
INSUFFICIENT for a destruction-vs-visibility discriminator. Do not reinterpret any
of9retirements or performance changes as confirmed explosion. No need to repeat
30minute endurance or discard its successful non-interference evidence.

Sponsor offers short run destroying their own selected ship. That is the right
comparison object,but existing first100state snapshots/owner and absence-based
retirement alone would not establish a death signal. Do not ask sponsor to launch
unchanged test expecting it to answer this missing relationship.

Exact next action:prepare bounded lifecycle comparison with retained before/
during/after detail and identify/qualify the smallest native lifetime or destruction
observation needed to distinguish actual death from simply not rendering. Avoid
broad engine archaeology,unknown-pointer reads or guessed death flags. Then use
brief camera-away/back while alive,followed by selected player-ship destruction.
If no native distinction is available,use safe fresh-epoch requalification for
recovery rather than claiming destruction detection. Run92rebind remains OPEN;
no recovery fix/new lifecycle probe implemented here. NO NEW LAUNCHER READY.

Files:this record,curated receipt,HANDOFF. Validation:archive SHA/all22entry hashes,
CSV elapsed/frame ranges/event histogram,config/summary/schema inspection and
existing documentation cross-check,JSON/path/diff checks. No runtime source/client
changes or fresh suite execution;prior377tests historical. Raw archives/evidence
unchanged,index empty,all work unstaged/uncommitted,no active owned runtime.
