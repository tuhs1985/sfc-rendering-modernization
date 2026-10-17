# C-01 — fresh-epoch qualification contract

2026-10-13; sponsor authorized continuation after RT-008. M1 CONTINUES.
This records the engineering decision before implementation, not live proof.

## Evidence and narrow question

[RT-008](evidence/M1-C01-RT-008-20261013-repeated-copy.md) confirmed30 fresh
handoffs, then correctly stopped when epoch1 retired and new epoch4 appeared.
An observed render gap is not proof of object destruction or physical continuity.
Do not merge IDs, loosen retirement or retrospectively change RT-008 acceptance.

Can an independently revalidated new epoch receive fresh unused copy slots while
old slot provenance/data remain unchanged? This is not safe buffer recycling or
permission to retain a stale semantic identity across a gap.

## Selected bounded policy

- Opt-in new mode only; existing RT-007/008 defaults remain unchanged. No new
  hooks, ABI, renderer, visual effect or hot generic geometry observation.
- Preserve the first selected raw-address filter: ship, visual, model, source,
  manager, original list/count and thread. These constrain the experiment; they
  are **not** proof that two epochs denote the same physical object.
- A new epoch is eligible only after the current selected epoch has an explicit
  retirement record and is absent from the active owner table. The new owner table
  entry must match current ship/visual; freshly read ship/visual/model vtables and
  ship+88 visual link must match the already-established exact-build contract.
- Observe that candidate's validated mainline primary wrapper on at least three
  distinct frames spanning >=250ms. No elapsed-only qualification and no transfer
  while old epoch remains active. The usual source/model/list/count/manager,
  nonnested scope, one-second interval, prior receipt/parent guards still apply.
- On acceptance, use a **new unused slot** built from current validated input.
  Record its owner ID, prior retired owner/time/frame, qualification start/time/
  frames. Commit the new selection only after complete graph validation and
  successful publication. At most two new-epoch qualifications per process,
  32 total fresh slots, <=700KiB fixed storage; no slot reuse/free/retarget growth.
- Preparation receipts and parent completion use each slot's owner ID, never a
  mutable global owner label. Earlier slot identities, bytes and addresses stay
  unchanged. A failed copy/publication or mismatched receipt halts new copying;
  every bypass continues the original game path.
- Source/mesh/manager changes beyond this fixed filter remain bypassed. Pointer
  reuse, identical payload and matching raw addresses never establish semantic
  identity continuity. No cross-epoch kinematic or lifetime inference is allowed.

## Proof design and boundaries

Offline tests must cover an old-active rejection, retirement plus new candidate,
insufficient time/frame observations, wrong link/vtable/source, fresh provenance,
old-copy nonmutation, two-qualification ceiling, exhaustion, failure and stop.
Native real-thunk ABI fixtures remain unchanged. Analyzer must reject fabricated
retirement/dwell/provenance, ID merging and fresh-pointer reuse; old evidence
continues to receive its original RT-007/008 decision.

Prepare RT-009: same two-ship skirmish,20s setup, normal copies/mild motion, then
at40s a three-tone instruction to briefly point a free camera away from both
ships for about5s and return. This requests an observation gap, not destruction.
If the fixture cannot induce the gap or qualify a fresh epoch, report it; don't
weaken the rule. Normal appearance, exit, hashes and capture bounds still apply.
No timestamps/manual RE/UAC duties for sponsor. Original capture and process-pin
cleanup rules remain. Runtime must corroborate a new epoch and original control
flow; offline success alone is not a semantic integration or formal TRL4 PASS.
