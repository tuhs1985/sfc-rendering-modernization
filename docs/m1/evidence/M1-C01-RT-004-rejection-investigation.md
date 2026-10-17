# RT-004 semantic-rejection investigation — 2026-10-12

**M1 CONTINUES; attribution unresolved.** Investigation only: no component
implementation, new gameplay, hook change or classification relaxation.

## Confirmed findings

Source tools/m1_component/m1_component.cpp, RecordHook:

| Branch | Address | Increments rejected_semantics when |
| --- | --- | --- |
|ship|004162B9|guarded ship/visual reads or exact vtable checks fail|
|visual|0042FD3F|ship/visual checks or ship+88 association fail|
|Model0|0042E4B2|not validated0042FDD5 mainline and not known00509843|

These count **observer classification exclusions**, not native rejected draws.
No rejection branch suppresses the original trampoline/render call. Model0
nonmainline clears model_scope; no visual modification is enabled. Retained
selected chains and all36 snapshots stay coherent; source review does not
identify a failure in their captured data.

Counts increment before tactical gating/detail checks. Failed ship/visual checks
are never appended to normal event CSV. Model0 events can be appended only while
detail_available, which stops at120 scene epochs. RT-004 CSV's final event is
2047ms/frame119: it covers roughly2.05s, not the whole90s. Therefore:

- Empty vtable_mismatch_sequences cannot exonerate rejected ship/visual paths:
  those failed validations are excluded before the analyzer sees them.
- Aggregate2,658 can include pre-gate or later activity. Earlier 'late rejection'
  wording is a coverage concern, **not proven rejection timing**.
- Detailed Model0 returns:237 at0042FDD5 and119 at00509843, no third earlycaller.
  This does not exclude later callers, failed associations or pre-gate activity.

## Discriminating hypothesis, not a conclusion

Full counters:visual calls12,108; Model0 calls17,502 minus knownexception5,394
=12,108; ship calls10,782; rejected2,658=2x1,329. A possible allocation is
1,329 visual-validation failures plus1,329 associated Model0 exclusions, leaving
10,779 mainline calls (three below total ship calls). This paired chain is
**SPECULATIVE**: multiple allocations/timings fit, no per-kind counters or
correlated rejected samples exist. No object/class identity is inferred.

Possible alternatives:ship-read/vtable failure, changed visual ownership,
non-ship caller of shared visual code, Model0 caller/vtable mismatch or missing
owner lookup. None is established; do not broaden RE to enumerate them all.

## Smallest proposed instrumentation (not built or ready to run)

At the same three rejection branches, preserve existing validation/control flow:

- Record first failed check using the **existing** guarded-read results, not
  extra speculative dereferences: unreadable ship, unexpected ship vtable,
  unreadable ship+88, unreadable visual, unexpected visual vtable, association
  mismatch; Model0 return/model/visual/owner failures separately. An unevaluated
  short-circuit check is unknown, never a proven secondary failure.
- Always-on fixed per-kind/per-reason counters with pre-gate vs tactical split,
  first/last elapsed time; total must reconcile with existing aggregate.
- Fixed32 signature buckets keyed by branch/reason/return/vtables, plus overflow
  count; at most64 example records across entire run and dropped count. Record
  raw ship/visual/model/source/owner/thread and relation to the two selected raw
  filters (match/neither/unknown), not persistent identity claims.
- First/last examples and phase counters continue after120-epoch CSV saturation;
  phase labels are requested intervals, not verified sponsor actions. No logging
  in hooks, heap growth, fresh hooks, geometry logging, intervention or retries.
- Serialize bounded diagnostic section/file <=64KiB after stop. Existing90s,
  36 snapshots/3MiB, CSV16–32MiB controls unchanged. Parser must flag truncation,
  count mismatch and selected-owner-related exclusions for lead adjudication.
- Before runtime: synthetic tests for every reason, unknown short-circuit,
  pre-gate/tactical split, saturation/overflow/reconciliation and post-detail
  accumulation; existing native build/state/cleanup tests and parser tests.

Tools remain MSVC14.51.36231 x86 C++17 /W4 /WX, PS7.6.5/Python3.12.14. A new
versioned probe and actual implementation/offline validation are required before
reuse of prepared elevated-parent entry. Current RT-004 executed definition must
not be retroactively edited to imply these diagnostics were present.

No sponsor gameplay requested now. Exact next action: implement this bounded
attribution if authorized, validate offline, then prepare a defined runtime.
Do not suppress exclusions, widen accepted RTTI, blame chase mode or reopen
settled M0 seam conclusions based only on this aggregate.
