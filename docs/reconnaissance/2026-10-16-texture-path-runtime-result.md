# Texture-path runtime review — fallback family selected

Date2026-10-16. Current texture-recovery result remains **PARTIAL**; no milestone
promotion, final renderer decision or game visual change. Authoritative fresh run:
`artifacts/m1/runs/20261016-165955-enabled`, component0.16.

## CONFIRMED observations

- Automatic tactical gate/normal exit; hooks restored by component AND controller;
  no remaining game/controller process or owned game-directory proxy/config files.
- One complete mesh/reference snapshot at frame3/46ms, owner epoch1, kff.mod.
  Packet SHA256 `60de172e6b1cc8ae9c838c65a7dc6b2c0b7da702c091253007a5260b3ea50b99`;
  57744bytes/452triangles/254positions/1356corners/five groups.
- `textures_enabled=1`, `manager_secondary_path_word=511`,
  `manager_multitexture_flag=0`, status1. Read/recheck stable at capture.
- New same-epoch resource IDs174–183, not old170–179. Same ten original filenames/
  hashes and **identical OBJ position/UV/normal/face/group records** to the accepted
  kff capture. Primary-image derivative1177434bytes, no image warning.
- 4792 frames observed/1180 detailed events/339458-byte event CSV; no truncation,
  owner/thread overflow, rejected semantics or vtable mismatch. Known00509843
  exception4789 counted, not expanded. Two coherent owner epochs. Full summary
  has2 retirements while saturated detailed CSV has0 retirement records; do not
  confuse omitted detailed events with absence of lifetime activity.
- Installed/reference SHA256 unchanged:
  `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.

Visible behavior for this particular run was not separately described beyond
sponsor reporting completion; do not invent a new visual acceptance. Earlier
"Looks right from here" applies to the provisional offline preview.

## Branch adjudication and correction

511 at+3D58 enables wrapper feature bit20 via0069D3B0–3C4. Zero at+8009 is
returned by0069F260 and takes006AC61A ->006AC63F. Thus **fallback family is
selected**, NOT combined multi-texture mode0. Confidence CONFIRMED for recorded
inputs plus exact-build static branch. This is not direct GPU-state/pass tracing.

Remaining fallback choice at006AC63F–6AC uses validation mask manager+800C
(getter0069F270, manager vtable+17C) and previous state manager+3F54 (returned by
0069E9C0).0069EA4E/6E/88 writes render states15/25/15: this cache is
alpha-test state, NOT alpha blending. Earlier provisional tooling label
"previous_blend" was corrected offline before0.17 runtime. Those inputs were
not recorded in0.16. Therefore:

- Do not claim two-pass execution from zero +8009 alone.
- Do not claim secondary images were unused from zero +8009 alone.
- Wrapper secondary-list outcome counts are NOT texture-pass counts.

If validation permits,006AC6AD–719 requests preparation mode2 then mode1. Mode2
selects the secondary image with ADD against vertex color; then the primary pass
uses framebuffer multiplication. Exact engine blend(1,4) mapping decoded from PE:
source jump table0069E904 index0 ->0069E729 ->D3DBLEND_ZERO(1);
destination table0069E92C index3 ->0069E7CF ->D3DBLEND_SRCCOLOR(3).
Setter0069E890–8D3 writes render states19/20;0069E6EA writes alpha-enable27.
Installed SDK d3dtypes.h independently corroborates enum/state values.
Thus the **eligible fallback's intended** operation is again
`primary * clamp(secondary + vertex_lighting)`, with intermediate framebuffer
quantization/clamping qualifications. Static code supports the provisional product
interpretation; actual eligible pass sequence and physical equivalence remain
unverified. Preview not silently promoted/replaced by this finding.

This is a useful narrowing, but the original five-byte instrumentation did not
fully cover the fallback decision. Record that gap rather than asking the sponsor
to repeat the same test without an improved observation.

## Prepared final eligibility observation, not executed

Collector0.17 now adds +800C DWORD and +3F54 byte/read-recheck alongside existing
inputs, preserving optional JSON provenance. Same hook/ABI/default-off one-shot
capture, ten scalar bytes read twice total, no COM/native calls/writes/image dump.
Analyzer predicts conditional requests only, not completed GPU work. New native
mutation/identity and Python legacy-absence/branch tests pass. No additional game
run launched/requested during analysis; use this small extension with the next
convenient normal fixture, not another unchanged probe. Same90s/bounded output/
elevation/cleanup/hash procedure in [probe](probes/TEXTURE-EXPORT-001.md).

## Other attempt / preserved evidence

Earlier20261016-165819-enabled failed startup: OpenThread/thread19396/error87,
M1StartW failed5, rollback_resume_failures0. Consistent with a thread vanishing
during enumeration, not proven root cause. No mesh/texture evidence from it;
retry165955 is authoritative. No retry-loop/security/thread-management redesign.

Curated [path-review JSON](evidence/20261016-texture-path-review.json) is the final
adjudicated analysis with correct alpha-test naming; generated capture-folder
path-review JSONs are preliminary history. Raw two-run archive below predates this
small final versionable JSON but preserves every original input.
Earlier generated reports remain intact as preliminary history. Useful two-run archive:
`artifacts/remix-ingest/evidence/20261016-texture-path-runtime.zip`,870797bytes,
53 entries SHA256-verified against sources; archive SHA256
`16a201328f1b5fee0bc397db0ab276378fbb167263c141b624da514b71a1971d`.
No original deletion/cache cleanup. [Run record](../runs/2026-10-16-codex-texture-path-runtime-review.md).
# Latest eligibility result — component0.17

Run20261016-171830-enabled captures previously missing mask3/previous alpha-test0,
alongside textures1,+3D58=511,+8009=0. CONFIRMED runtime inputs plus exact-build
branch select mode2 then mode1 requests; no missing eligibility inputs remain.
Actual GPU pass completion/color-space/physical emission remain unobserved.
This supersedes the missing-input blocker below, not historical0.16 evidence.
[Run record](../runs/2026-10-16-codex-texture-eligibility-runtime.md) and
[curated analysis](evidence/20261016-texture-eligibility-review.json).
Normal exit/hook restoration/client unchanged; geometry hook OFF. No new gameplay
needed merely to recapture these settings. Provisional preview/fidelity still PARTIAL.
