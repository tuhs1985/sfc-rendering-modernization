# Run283 — focused damage observer prepared

Sponsor request: prepare the observation run after Run282 identified the second
native polygon list. Pure black transparency on damage images is established
from the sponsor's model-authoring experience. It is not generalized to hull
diffuse images or treated as a question requiring another test.

## Changes

Added `tools/damage_probe`: separate x86 startup observer, native fixture, decoder,
focused decoder tests, qualification and sponsor launcher. Reuses the existing
early observer's supervisor, current-user channel, owner/visual epochs, named
loader observations, bounded ring and hook restoration. Small profile parameters
share the runner without duplicating its process/cleanup workflow.

The `SFC_DAMAGE_PROBE` compile guard adds the existing polygon-wrapper boundary
and damage-only state/snapshots. Normal nine-hook observer builds omit this code;
normal M1, D3D9 renderer, runtime host, material/light/image settings and gameplay
launchers are untouched. No ship suppression or damage rendering is introduced.

Records model selector/family and list state on change; copies temporary material
words and same-session resource tables before return; takes one fresh secondary
mapping per visual epoch/model/list. Geometry includes original positions and
damage-specific corner UVs/normals, not a converted game-folder model. At most
four2MiB mapping slots and16MiB metadata; omissions are counted partial evidence.
All disk writes happen on the worker. Original native calls/arguments continue.

Offline resource joins use the existing eighteen filename/slot/hash relationships.
Four raw native manager words remain explicitly opaque; this observation does
not claim to capture every downstream D3D alpha/blend state. First lazy mapping
creation is recorded around the model call; the earlier primary insertion cannot
retroactively consume a layer first observed afterward.

## Validation

Strict x86 `/W4 /WX /EHa /O2` builds pass. Damage native and actual startup-injected
fixtures pass, observing undamaged then damaged submissions, copied stack-backed
IDs99/100, exact secondary UVs0.25/0.75, two distinct asset epochs, unowned-wrapper
pass-through, original return/LastError/SSE preservation and ten byte-exact hook
restorations. Both complete with two immutable mapping packets and no decoder
issues. Qualification receipts under `artifacts/render-survey/damage-probe` pin
all source/dependency/binary hashes and point to exact fixture runs.

Fourteen damage decoder tests and22existing early-observer Python tests pass.
Cases cover corrupt checksums, nonfinite UVs, bad indices/counts/material groups,
native pointers where portable ordinals belong, missing maps, mismatched image
IDs, retired owner identity and missing restoration. Windows sandbox temp-path
denial was resolved by using workspace temporary storage; it was not a code test
failure. Launcher-registry reads/injected fixtures run with sandbox approval.

Final damage native36checks and actual injected27checks pass. Injected evidence:
`artifacts/remix-runtime/runs/damage-20261103-201321-468321`; error null, normal
exit true, host0, accepted/copied client and launcher settings unchanged.
The original nine-hook native/injected qualification also passes as a regression
check (`early-20261103-201336-302914`), including its slow-receiver and in-flight
stop controls. Final qualification/preflight receipts are local ignored evidence; no
gameplay acceptance is claimed. No SFC gameplay, GPU render campaign, Defender
changes, staging or commit performed.

## Sponsor checkout and next step

[Probe contract](../reconnaissance/probes/DAMAGE-LAYER-001.md),
[launcher/workflow](../../tools/damage_probe/README.md).
Familiar F-CA battle, let hull take damage, rotate briefly, normal exit at two
beeps after90tactical seconds. Only native SFC is visible during this observation.

Afterward analyze scalar/family transitions, selected original damage pair,
secondary UVs, first-use ordering and cleanup. Then implement the smallest
per-owner damage-layer extension; exact companion/blend handling must remain
evidence-backed. Break models remain a separate alpha requirement.
