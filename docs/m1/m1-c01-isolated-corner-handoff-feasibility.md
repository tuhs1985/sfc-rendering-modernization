# C-01 isolated corner handoff — bounded feasibility review

2026-10-12. **M1 CONTINUES; candidate feasible statically, runtime contract open.**
Review only, no clone/override/hook implementation or new gameplay. No C-02
enhancement/final renderer choice. Starting evidence:RT-004/005 and
[math adjudication](evidence/M1-C01-MATH-001-20261012.md).

## What the current Model0 invocation actually does

Exact client SHA2564D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29;
existing dumpbin disassembly windows0042E4B2..E64D,0042EB52..EBF6,
006AC5A0..C719,006ABFC0..C593. Extended byte verifier37 anchors including
two exact PE vtable slots corroborate static references.

| Step | Exact evidence | Scope/confidence |
| --- | --- | --- |
|Visual selected child call|0042FDD2, returns0042FDD5; Model0 ECX, manager/source/floats stacked; callee0042E64D ret10h|CONFIRMED static plus prior semantic runtime |
|Primary vertices|0042E517/51E pass Model0+C/+8 to manager+138 ->006ABF80; manager+554 stores position base|CONFIRMED static |
|Primary source|0042E529/52E passes argument2 to manager+13C ->006ABFB0; manager+558 caches source pointer|CONFIRMED static plus existing source-copy proof |
|Primary list|0042E54F..557 passes mode1,listModel0+14,countModel0+10 to manager+140|CONFIRMED static |
|List wrapper|PE007B8E8C (=manager vtable+140) contains006AC5A0, NOT006ABFC0 directly|CONFIRMED PE bytes/static |
|Preparation dispatch|wrapper006AC600/631/69F/719 invokes manager+180 with list/count/derived branch args|CONFIRMED static, live branch unobserved |
|Secondary path|0042E588 invokes Model0+3C;00798424 contains0042EB52; builder0042EB8B allocates/EB94 writes+18, creates headers/corners;0042E618/620 renders+18 list|CONFIRMED static conditional, not new runtime claim |

## Rejected shortcuts

1. Editing shared Model0+14, original polygon+18 or corner floats, even if later
   restored: exposes concurrent/reentrant consumers and violates isolation goal.
2. Shallow Model0 clone/ECX swap at current entry: inspected conditional virtual
   builder allocates/writes secondary state and calls other object methods. Header
   prefix sufficient for snapshot is not enough to establish clone-safe ownership,
   allocator/destructor/cache semantics. Reject rather than reverse-engineer object.
3. Whole-model clone or intercept every vertex/light response: excessive work or
   volume for this question, and unnecessary if list argument isolation works.
4. Using source tint lease as if it isolates geometry: it only substitutes source
   argument/cached source; polygon/corner graph remains original.

## Defensible candidate, not yet implementation selection

At manager list wrapper006AC5A0, preserve original manager ECX and other arguments;
substitute **only a caller-owned polygon-pointer list** for a validated primary
invocation. Correlate through current Model0 TLS owner/model scope, actualmanager,
exact caller return0042E55D, count and original list equality against selected
Model0+10/+14. Reject secondary return0042E626, known00509843 ownership path,
unknown owner/thread, reentrancy or mismatchedcount/list. No intervention retarget
on raw pointer reuse; fixed opaque owner epoch/ship/visual chain as previous proofs.

Entry stack before prologue: return atESP,countESP+4,listESP+8,modeESP+C;
wrapper ret0Ch. These are **CONFIRMED static** push/cleanup facts, not yet an
approved new runtime hook ABI. Existing thunks preserve flags/registers/FX state;
any additional entry/return interception requires separate offline adjudication.
Current five semantic hooks have no independent list argument to swap; using this
candidate needs a specific additional bounded interception point, not whole-model
reconstruction. No bytes have been patched in this review.

Proposed immutable-copy spans for later neutral proof:

- Full pointer list (countx4), retaining original polygon pointers for unmodified
  entries; no partiallist truncation or droppinggeometry.
- For chosen prefix, copy each complete28-byte polygon header preserving face,
  flags/sourceindex/unknownbytes; change only copied+18 corner pointer.
- Copy complete28-byte records for each chosen polygon's **full** corner count,
  preserving index/padding/vector/UV/unknownbytes. Sampling8 corners isn't permission
  to truncate an originalpolygon. Normal modification would be a later separateproof.
- Positions/base/source/textures remainoriginal and unmodified. Don't infer all
  geometry sharing from sampled prefixes or material groups.

An initial neutral copy budget can deliberately admit only the observed452-poly
model under a1,024-polygon list guard:<=4KiB pointers,64 headers (1,792 bytes),
<=8 corners per selectedpolygon (14,336 bytes), total<=20,224 bytes/scope.
If selectedpolygon exceeds8 corners, leave it original or decline atomically;
never truncate.6,370-poly model bypassed under this first proof, not reclassified
unsupported. This is a **proposal**, not a change to current probe limits or CDD.

## Consumption, cache and restoration obligations

006AC299..2E0 caches transformed **positions** by vertexindex;006AC2E2..2EF copies
UV from each current corner.006AC310..32E sends each current corner+4 vector to
lighting; the inspected position cache does not skip that lighting call. This
supports per-corner copy feasibility, not a guarantee for all branches.

Preparation loops pointer list to completion then returns; original headers and
corner vectors are consumed before numeric submission. This is strong support
for synchronous consumption, **not a complete pointer-nonretention proof** across
virtual calls, clipping, manager scratch/batching. Don't free at entry/assume
successful return. Neutral proof must validate consumption/lifetime before edits.

Hold fixed per-thread/per-invocation storage until original selected-child return
or a separately proven wrapper return boundary. No source/header-pointer lease
may escape; reject nested reuse, drain live scopes before hook restoration/stop;
on failure pass original list unmodified. Original Model0 must still build/use
secondary cache normally. Visual exit drains current source lease already, but
that doesn't prove new buffer lifetime. InertDLL normal exit/removal policy unchanged.

## Smallest next proof

Prepare a **neutral bounded wrapper observation**, first without list substitution:
correlate caller/count/list/manager with existing owner epoch and distinguish
primary vssecondary/other calls. Record finite counters/samples after detail
saturation, same90s fixture/geometryoff, no asset mutation. Offline fixtures must
exercise stackoffsets/ret0Ch, branch exclusions, nesting/thread mismatch, guards,
full-bytecopy/nonmutation and stop/return lifetime. Versioned probe before runtime.
Then a bit-identical isolated-copy pass-through can be considered only after
that provenance/ABI check. No requested sponsor gameplay now or enhancement build.

Unknowns remain precise: live wrapper routing/provenance, pointer retention/
return-lifetime and safe copiedgraph bounds. No broader engine archaeology needed.
