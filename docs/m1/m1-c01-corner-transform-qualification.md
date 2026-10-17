# C-01 — corner vectors and transform qualification, 2026-10-11

## Disposition

**Newest mathematical adjudication:** [MATH-001](evidence/M1-C01-MATH-001-20261012.md)
confirms sampled geometric normal alignment/sign and nearproperrotations;
model-local interpretation strengthened by static/live/numeric evidence. Non-unit
normals/signs retained, full light/override contract open. No more gameplay just
for same prefixes; next isolated-copy handoff feasibility review, not implementation.

**Newest RT-005:** [evidence](evidence/M1-C01-RT-005-20261012-attribution.md)
trackingoff,34 valid samples through85s,retirement/freshID recovery confirmed,
zero exclusions(non-reproduction,not priorcausefixed). Fixed corners under
angular changes strengthens model-local interpretation; next step mathematical
adjudication against existing static anchors, not blindgameplay repeat. Historical
status entries below preserved. M1/C-01 CONTINUES, no enhancement/fullTRL4PASS.

**Newest RT-004:** [temporal evidence](evidence/M1-C01-RT-004-20261012-epoch-observation.md)
both owners0–85s/36 valid samples. Fixed corners under owner2 supplied angular
basis change supports model-local inputs (STRONG HYPOTHESIS). Chase camera limits
separation, normal-space contract unresolved. No fresh epochs;2,658 aggregate
semantic rejections need bounded attribution. Earlier proposals remain history.

**RT-003 repeat update:** both models now yield valid samples;6,370 count guard
issue resolved. [Second attempt](evidence/M1-C01-RT-003-20261012-repeat.md) remains
partial because original epochs stop sampling after15s. Sponsor confirms both
visible/moved/turned, including camera view switches. Need explicit read-only
epoch-transition observability; no source change/full numeric qualification yet.

**Runtime update:** [M1-C01-RT-002 evidence](evidence/M1-C01-RT-002-20261011-corner-inputs.md)
narrows sharing/numeric vector data but remains PARTIAL: successful owner1 samples
under translation/composed changes, owner2 count-guard rejection, no angular
change captured. Preserve raw magnitudes; revise only read-only guard/schedule
before next proof. No enhancement contract or normal-space PASS yet.

**Preparation update:** [M1-C01-RT-002](probes/M1-C01-RT-002.md) now implements
the read-only proposal with six5s windows/two requested samples per10s action
phase, fixed bounds and audio cues. Offline validation passes; gameplay has not
run. The proposal wording below is preserved as pre-build evidence/history.

**M1 CONTINUES — static layout materially narrowed; live qualification required.**
Sponsor authorized continuation, parking monitor troubleshooting as an operational
assumption. Baseline reproduction/clean screenshot supports display-path suspicion,
not a diagnosed monitor/cable fault. No game/display configuration changed here.
Shading-off runtime proves existing vertex-light participation; it does not qualify
the numeric space or an enhancement. C-02 remains separately gated.

## Exact evidence

Read-only exact-build dumpbin windows, independently checked against reference
PE SHA256 with extended `verify_m1_c01_shading_bytes.py` (29 matched anchors).
These are static relationships, not dynamic numeric proof. Helper names below
are descriptive labels only, not evidence.

| Relationship | Exact evidence | Classification |
| --- | --- | --- |
| Polygon header count/source/corners | `006AC02A/02D`: +4 source index/+0 corner count; `006AC042/045`: +18 corner pointer | CONFIRMED static |
| Corner record stride | `006AC299..2A6` reads WORD vertex index; `006AC3FA` advances record by1Ch | CONFIRMED static,28-byte corner records |
| Corner vector | `006AC310..32E` sends record+4 as third lighting argument; helper `006A980D/0F` negates scaled dot-product with that vector | CONFIRMED vector usage; surface-normal meaning STRONG HYPOTHESIS |
| Indexed positions | manager+554 holds base; `006AC2B9..2C1` resolves base+12×WORD index | CONFIRMED static float-triplet access, numeric space pending |
| Face vector | polygon+8 passed at `006AC1B4/1BA/1D0`; also used in culling dot at `006AC08F/097` | CONFIRMED vector/call relation; normal interpretation STRONG HYPOTHESIS |
| Position transform | `006AC2C9/2CF`: manager+6B0 via `0069CA30`; scalar branch rows at offsets00/10/20, translations0C/1C/2C, optional fourth output | CONFIRMED scalar arithmetic/layout, active implementation pending |
| Ship transform handoff | virtual ship+6C return passed to manager+E4 at `00416318..323`; alternative copied68-byte path `004164B5..4E9` | CONFIRMED static plus existing M0 pointer evidence |
| Manager transform setter | vtable+E4 at `007B8E30` = `006AA550`; copies17 DWORDs to manager+6F4 at `006AA55D..570` | CONFIRMED exact PE pointer/static copy |
| Composed transforms | `006AA57C`: manager+628 × supplied transform into+66C; `006AA58F`: +5E4 × supplied transform into+6B0 via0069BAF0 | CONFIRMED operand/output addresses; camera/view/projection labels remain hypotheses |
| Light-space preparation | setter reads64 slots at+788, writes triples at+17B8/+1AB8; type-dispatch paths006AA63F..674 call0069CBC0/CC40 | CONFIRMED static, no live light-type claim |
| Reverse point/vector algebra |0069CBC0 subtracts translation then multiplies transposed3×3;0069CC40 scalar branch transposed3×3 without translation | CONFIRMED arithmetic; treating transpose as inverse requires orthonormality evidence |
| Runtime math dispatch | globalsC69FF0 (position),C69FF4 (composition),C74058 (reverse vector) can select alternate implementations | CONFIRMED static branches; live targets/behavior UNKNOWN |
| Light response gate | manager vtable+94 at007B8DE0 =0069F190, returns byte manager+1EB8 | CONFIRMED static; name alone not sufficient semantics |

The third lighting argument follows the original corner vector, while lighting
directions/positions are transformed by the supplied object matrix before the
dot-product response. This supports a **STRONG HYPOTHESIS** that model geometry
and corner normals remain model-local, with lights mapped into that space.
No claim that the cached position matrix is a pure world transform or that the
matrix uses a named external API's convention. Alternate dispatches and live
normal lengths/scales must be checked before using this contract numerically.

## Feasibility implication

Source index belongs to the polygon; each polygon has its own corner records and
vectors. Therefore **one source entry is not one vertex or guaranteed one surface
orientation**. Five lit source entries in the observed enemy are material-like
groups, not five known normals. Actual sharing counts across differing vectors
remain uncaptured. Do not implement a source-RGB directional term by averaging
or guessing normals; it could color broad groups instead of shade surfaces.

The inspected path provides a credible finer-grained input route. Its use would
need an explicitly reviewed owner-local data/lifetime mechanism, not silent
writes to shared Model0/corner storage or a new high-volume response hook.
No enhancement/corner mutation/hook architecture is selected in this run.

## Smallest discriminating next proof (definition proposal, not armed)

Prepare an opt-in read-only extension at existing validated Model0 entry only:

- Capture original manager+6F4 transform (68 bytes), composed+6B0 transform,
  identity tuple, three dispatch pointers, model vertex count/base (+8/+C,
  corroborated by existing source-init call), and primary polygon fields.
- Guard every address/count/index; preserve all calling state and original data.
  Validate Model0 count/list/source and manager vtable just as existing component.
- Proposed ceiling: two selected live owner epochs, maximumsix snapshots each
  (12 total), at least1s spacing; each at most64 polygons/eight corners each.
  Cap model vertex indices against the read count and a reviewed sanity ceiling;
  copy only referenced position/vector triples. Record truncated/invalid samples,
  never extrapolate sampled sharing to the whole model. Fixed buffers/1MiB packet
  hard cap, default120 semantic epochs/10,000 events; geometry hookoff.
- Match stationary, camera-only motion, and ship heading/movement observations.
  Six snapshots must be phase-labelled by a prepared workflow, not guessed from
  manual timestamps. Numeric finite/unit-length/orthonormal checks are evidence
  tests, not permission to normalize, transpose or otherwise alter game state.
- Compare raw corner vectors/indexed positions versus transform changes and
  source-group membership. Read-only camera/object discrimination can settle the
  model-local hypothesis; it cannot establish visual uplift.
- Detailed tool/version/start/stop/output/cleanup and offline tests must be in a
  versioned probe definition before any runtime. This proposal is **not** a ready
  probe and sets no new CDD requirements. No gameplay requested yet.

Decision: reject unsafe assumptions/source-entry-as-normal mapping; preserve the
credible corner-vector route. Prepare the bounded read-only probe next, validate
offline, then request sponsor gameplay only when the workflow is ready. No final
renderer selection, broad engine analysis, monitor troubleshooting or C-02 work.
