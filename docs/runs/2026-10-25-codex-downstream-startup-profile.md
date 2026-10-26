# Run178 — downstream startup attribution

Date: 2026-10-25 (America/New_York). Starting checkpoint committed as
`9ff2d3d` (`Measure early native model loading and qualify timing observer`),
28 reviewed text files; not pushed. Commit validation: 586 Python tests passed,
Python/JSON parsing and diff checks passed. No unreviewed binaries or captures
were committed. Sponsor's [delivery priority](../decisions/2026-10-25-progressive-material-readiness-priority.md)
is recorded: complete appearance fast first; prompt correct diffuse-textured
geometry with enhanced materials later is an acceptable secondary fallback.

## Evidence and method

Reexamined [Run163](2026-10-24-codex-initial-material-readiness.md), retained
`artifacts/initial-readiness/analysis.json`, and individual STARTUP_PROFILE marks
in the accepted reference `20261024-222711-351784-return-fixture` and single-Present
control `20261024-223011-587482-return-fixture`. Preserve stage **and index** when
matching marks: frame0 anchor output is not frame1 complete cohort output.

Performed a bounded CPU-only FCA replay using the reference's fresh binary mesh
packet and original images, frozen accepted material settings, and actual current
identify/scene-bundle/extent/material-binding functions. Source is captured data,
not a converted MOD file. Evidence:
`artifacts/initial-readiness/cpu-20261025-173730-049878/analysis.json` and
`cpu.pstats`; definition `artifacts/initial-readiness/profile_cpu_prepare.py`.
No SFC, Toolkit, Remix or GPU host launched. The native batch texture-hash utility
is a CPU subprocess. No original assets/settings changed.

## CONFIRMED — two distinct downstream gates

Reference discovery to first complete cohort GPU output: **5.1703892s**.
Parent activation occurs at **2.077316s**; three different asset preparations
already run concurrently. Native device creation overlaps preparation, so its
2.3124148s must not be added as a serial delay.

Relative to first discovery, native activation is 2.1023605s, renderer assets
start 2.146306s, anchor output completes 2.7052099s, first complete cohort drawing
ends 3.0069529s, and cohort output completes 5.1703892s. Thus the final
**2.1634363s** lies after cohort drawing submission and before complete output.
Existing Performance receipts do not split output-copy submission, GPU readiness,
and grading/coverage completion sufficiently to assign that entire interval.
It is not proven to be texture upload, shader compilation or a particular wait.

Initial 24-Present bootstrap spans **546.4606ms**, including 302.6479ms in
PresentEx intervals, 3.8666ms in drawing and 239.9461ms between iterations.
The source's per-pass Sleep(10) contributes, but removing it alone cannot explain
or remove the full multi-second difference. Receiver ACK intervals include peer
consumption/fixture work; they are not measurements of GPU copy alone.

Historical single-Present control reaches cohort output at **2.5775601s**,
but lacks enhanced material response and has poorer early delivery. It remains
an incomplete full-appearance result, not a ready production fix or sub-two-second
success. The newly approved fallback makes progressive readiness worth testing
without changing that historical adjudication. Pinned runtime's dynamic USD
watcher is relevant, but no public reload-completion barrier is available in the
qualified SDK; do not replace evidence with undocumented runtime calls.

## CONFIRMED — CPU replay and redundant work

| Actual preparation stage | Profiled elapsed |
| --- | ---: |
| Identify captured content and image identities | 383.64ms |
| Build scene bundle | 212.43ms |
| Output extent conversion | 48.43ms |
| Enhanced material binding | 1159.67ms |
| Total | 1804.17ms |

This single-asset cProfile replay has different cache state and concurrency from
the historical multi-asset run. It is attribution evidence, not a new gameplay
loading result or a controlled subtraction from SFC's native 91ms load.

Geometry hash, original image hashes, material-stage hash and **all derived image
metadata/hashes exactly match** the accepted reference. Generated evidence
77,671,185 bytes, admitted within existing aggregate20GB and replay bounds.
Raw captured packets and source assets remain unchanged.

Surrounding source confirms avoidable work:

- `owner_rebind.Content.image` resolves/stats a file before a cached hash hit.
  Whole replay performs404 image-resolution calls (425ms cumulative, overlapping
  stage totals; do not add cumulative times together).
- `material_binding.original` repeats source reading/decoding. Its existing
  `original_seen` accounts for the byte budget; it is not a decoded-image cache.
- `material_binding.save` performs DDS encoding and hashing **before** checking
  for an already generated image:147 encoding calls, about171ms cumulative.
  Reuse must preserve secondary-image roles and settings, not key on primary
  filename alone. Scene bundle also decodes primary images before this stage.
- The one batch hash subprocess takes529ms in the first profiled replay, but
  exact repeat invocations take41ms/34ms with all56 hashes matching. Startup,
  cache/profiling effects and scheduling remain mixed;529ms is not unavoidable
  hash-algorithm cost. This is already one batch, not one process per image.

Already removed expensive DDS pixel readback stays removed; current layout checks
are negligible. Four preparation workers already exist. More threads or deleting
checks without attribution is not the identified solution. No unsupported GPU
readback, alternate assets, material simplification or Remix UV change was used.

## Adjudication and next unit

**Investigation advanced; no startup fix or new runtime success claimed.**
Production hooks, renderer, settings and qualification receipts remain unchanged.
API remains parked. No stage/push/commit of this follow-on analysis; requested
checkpoint commit is complete. No active owned process/channel remains.

Next smallest action: test per-preparation immutable source-image and derived-image
reuse in an isolated CPU replay, keyed by content/role/settings, requiring exact
accepted material/image hashes and bounded memory. Then split the existing first
cohort output interval with low-volume timing around existing output-copy/fence/
postprocessing calls in an isolated host control. No gameplay discovery run is
needed. Keep fast complete appearance primary; evaluate decoupled provisional
diffuse delivery only as the explicitly recorded fallback.
