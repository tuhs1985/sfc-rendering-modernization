# C-01 — private-copy lifetime review

2026-10-13. **M1 CONTINUES; review complete, copy implementation not started.**
Sponsor authorized next lifetime review and requests plain-language explanations.
Exact technical details belong here/runbook; sponsor procedures stay concise.

## Sponsor-facing result

The original renderer appears to turn polygon data into its own drawing values
before submitting them. We have not proved that every branch forgets every input
pointer immediately. The first controlled copy test can avoid an early-release
guess:use one private copy once, keep its small buffer alive until normal game
exit, and never reuse it. Rendering should look unchanged. This tests whether SFC
can consume our private data safely, not whether a faster reusable copy system
or improved lighting has been completed.

## Reviewed boundaries and exact evidence

Sources: [RT-006](evidence/M1-C01-RT-006-20261013-wrapper.md),
[handoff feasibility](m1-c01-isolated-corner-handoff-feasibility.md), existing
exact-build dumpbin windows006AC5A0..C754,006ABFC0..C593,
006A9790..9A78,006B8190 prefix,006AB50C..B619.

| Boundary | Observation | Confidence |
| --- | --- | --- |
|wrapper->prep|manager vtable007B8ECC(+180) points006ABFC0; caller passes list/count, wrapper returnsret0Ch|CONFIRMED static, RT-006 primary invocation dynamicallycorroborated |
|prep input|006AC024..045 iterates original pointerlist/header/currentcorners; consumes header+0/+4/+8/+18|CONFIRMED static inspected path |
|corner->prepared cache|006AC2B4 tests positioncached;006AC2E2..2EF copiesUV,006AC310..32E passes currentnormal; no copiedModel0 needed|CONFIRMED static |
|lighting output|006A9A5D..72 writes computedfloattriple to caller-suppliedoutput (stack in prep)|CONFIRMED static, not full pointerescape analysis |
|clipping input|006AC414..418 passes numericcount/indexscratch to006B8190;006B81DE..81FE indexes manager preparedvertexcache|CONFIRMED static prefix, entireclipper not reconstructed |
|prep->accumulation|manager+184 at007B8ED0 points006AB410|CONFIRMED exactPE pointer |
|batch output|006AB520..52C gets preparedvertex viaWORDindex;006AB5E0..5EC copies eightDWORDs from numericvertex+14 into batchoutput|CONFIRMED static normal output branch |

No original polygon-header/corner pointer appears in that inspected numeric
output copy. This is meaningful support for synchronous consumption, **not proof
of no pointer retention** across all manager state, virtual callbacks, alternate
paths or nested calls. Do not claim a safe free-at-wrapper-return contract yet.
Existingparentreturn accounting alone doesn't prove this either.

Read-only verifier now41 exactbyteanchors/referencehash match; anchors corroborate
locations and smallprefixes, not a comprehensive symbolicdataflow analysis.

## Conservative first-proof proposal (not implemented)

Use the already-qualified primarywrapperentry and originalrenderer, no new
renderer/normal mutation. Exactly **one successful substitution per game process**,
one fixed opaqueowner epoch chosen from a validatedsmallmodel path, no retarget.
Originalgraph remains untouched. Originalcount/manager/source/mode/positions stay
unchanged. Replace only that invocation's stacklistpointer after all validation/
copy checks finish. No Model0 clone, originalheader/list-pointer swapping or
manager state modification by project code.

Copy the complete pointerlist (guard<=1,024), and at most64 complete28-byte
polygonheaders plus allcornerrecords for each copiedpolygon (guard<=8corners).
Budget<=20,224bytes (+smallprovenance/canary metadata), one fixedstorage slot.
Observed452-poly model eligible;6,370-poly model passes through unchanged. For
oversized/malformed selectedprefix, decline atomically rather than truncate.
Uncopiedpolygons retainoriginal pointers, inoriginalorder. Allcopiedrender payload
bytes must compareequal; only copiedlist/headercornerpointers are relocated.
Thus 'bit-identical' means render payload, **not relocatedaddresses**.

Mark slotimmutable/used after successful handoff. Do not free/reuse/zero on
wrapperreturn, parentreturn, ownerretirement, capturestop or hookrestoration.
Keepcomponent mapped until **normal process exit**, which reclaims thebuffer.
No new allocationsperframe, no growingcapturememory, no owneraddressreuse lease.
Existingcontroller default unload_after_stop=false supports this lifetime;
futurecopy mode must explicitly reject forced-unload requests and document that
disabledmeans hooksremoved but tinybuffer stillresident. Don't use a dynamically
unloaded module/stackbuffer for copieddata. Abnormal termination frees process
memory too, but isn't acceptable runtime success.

This makes early-free/use-after-free of the copied graph avoidable without
exhaustive reverse engineering. It does **not** qualify buffer recycling,
per-frame mutation, reentrant overrides, generalmodel lifetime or long-running
enhancement. A renderer retaining an address afterprocess exit cannotuse that
process memory normally; no such externalbehavior is established or assumed.

## Necessary checks before a build/test is prepared

- Bound every size/index/address and every completecornerrecord; copy unknown
  bytes/padding/UV as-is. No speculative normalizing/windingflip or materialaverage.
- Require livevalidated owner/model/visual/manager and primaryreturn0042E55D,
  originalcount/list match. Bypass unscoped/non-ship/secondary/nested calls.
- Exactly-once handoff only after full copy validation; first-failure original
  input remainsunchanged. No publication of partialcopy or premature usedflag.
- Offline fixtures:full-byte equivalence except pointers, originalnonmutation,
  addressoverflow/unreadabledata, rejectedcounts/corners, fixedmemorycap,
  retirement/reuse doesn't rearm, stop doesn't clearbuffer/forceunload, no nesting.
- Runtimeevidence should record owner/model/list originals/copy, payloadhashes,
  singleapplicationcount and retainedslot/canaries atstop, parentreturn,
  normalrendering/control/exit/clienthash/restore. No hotgeometry transcript.
- A new versionedprobe/runner must describe limits, disabled/removed/pinned
  states and concise sponsorinstructions. Phase-window tests use separate
  setup/settle/capture cues; don't silentlyreuse RT-006 timing for a newphaseproof.

## Decision and next action

**First neutral copy proof is feasible under bounded process-lifetime pinning
(STRONG HYPOTHESIS), not runtime-proven.** No need for broad renderer archaeology
merely to prove aggressive early release. Precise remaining uncertainties are
copygraph validity/nonmutation, stable single-call substitution and runtime
behavior with relocatedinputaddresses; these are testable by offlinefixtures and
one neutral gameplay proof. Generalreturn-release/recycling remainsdeferred.

Nextsmallestaction:prepare an explicitlybounded one-shot privatecopy build and
probe under this conservativepolicy, **if sponsor authorizes implementation**.
No runtime or copycode was started in this review. C-02/visualbenefit/fullTRL4
stillseparate; no requirements change/waiver or finalarchitecture selected.
