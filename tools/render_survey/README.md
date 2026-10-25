# Metadata-only rendering-family survey

Default-off, read-only instrumentation for the separate SFC test installation.
No Remix/Toolkit renderer, extra ship, image readback, native geometry hook or
asset export. This implements observation, not new rendering-interface support.

Run171 expansion: sponsor authorizes a **2 GiB TOTAL per-run envelope**, including
native light updates and a global-effects-list type census. This build was
qualified in Run171 and used for the two complete Run172 captures; old Run165/169
receipts are historical. Source changes still require refreshed qualification.

Authority: [probe](../../docs/reconnaissance/probes/RENDER-FAMILY-SURVEY-001.md),
[family map](../../docs/reconnaissance/rendering-family-map.md),
[Run165](../../docs/runs/2026-10-24-codex-render-family-survey-preparation.md).

## Sponsor launch

From the established Administrator PowerShell:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\render_survey\start_render_family_survey.ps1"
```

`-CheckOnly` performs read-only preflight, no game or renderer launch. Do not
rebuild at gameplay launch: exact-source/native/GPU qualifications must already
exist. No new UAC or execution-policy change beyond this process invocation.

Enter a familiar skirmish promptly (gate observer bounded120seconds). After the
start beep, hold a quiet view about15seconds. Two beeps request camera movement;
three beeps at30seconds request normal combat. Use weapons/allow shield hits;
an explosion or damage is useful if practical. No need to keep both ships visible
throughout. No manual timestamps or RE. The final two-beep/console request asks
normal exit after90seconds. Nothing new should appear in the picture. Report
what actually occurred afterward; missing effect categories remain untested.

## Developer validation

- `build.ps1`: isolated x86 observer, bounded ring tests, graphics fixture and
  fixture-only launcher under `artifacts/render-survey/bin`. Normal binaries
  are never overwritten. The observer preserves x86 frame pointers (`/Oy-`)
  so Windows stack capture can walk its own callback frames.
- `run_survey.py --record-build`: freeze reviewed current inputs; not a GPU pass.
- `run_survey.py --fixture --fixture-seconds 90`: full-duration standalone test.
  `--fixture` alone uses10seconds. Neither launches SFC or edits a game install.
- `qualify.py <exact-current-10s-run> <exact-90s-run>`: require actual proxy
  callback/state/resize/recreation/call-origin/exit evidence and matching binaries.
- `python -B -m unittest discover -s tools/render_survey/tests -p 'test_*.py'`.
- `survey_capture.py <exact-broad.bin>`: bounded streaming analysis; raw evidence
  remains. No family is automatically called a weapon/shield/UI from draw counts.

Drivers are isolated snapshots of existing verified launch/supervision code,
restricted at argument parsing to observation-only broad mode. Differences:
survey parser/observer/provenance/qualification;90second game capture; quiet/
camera/combat instructions;120second gate-observer wait; no image toggle phase.
Standalone fixture and fixture-only launcher have100second ceilings to cover
the90second test. Normal game launch uses the unchanged300second owned launcher
and285second prepared supervision limit. Do not treat fixture timeout corrections
as fixes to SFC or as permission to change normal rendering limits.

## Wire and coverage

Independent magic0x53525631/version2,128-byte header and128-byte records. Parser
still accepts historical version1/events1–34. The
field layout follows the established broad metadata wire; this is a distinct
protocol and must not be parsed as old broad magic. It uses the existing private
channel extension at offset256. Header finalization precedes status3 publication.

Events1–22 retain the old enumerated metadata meanings,23reserved. Events24–34:
descriptor bindings;vertex buffers;index buffer;scissor;sampler creation;pipeline
creation state;pipeline retirement;sampled origin fragments;origin counters;
descriptor-table bindings;constant-range identity. Exact argument layout is in
`survey_events.h`/`survey_extra.h`. Shader, image, vertex, index, normal, UV and
constant data are NEVER read. Pipeline creation reads only selected scalar
depth/blend/rasterizer/topology descriptors. Resource dimensions/layout are
metadata, not contents. Known ship draws are not filtered out.

Origin fragments carry the exact parent draw sequence, address start/count and
up to8addresses. Sample every8th retained draw, max64walks per observed Present,
32addresses. Count eligible/captured/empty/budget-skipped and stack-walk QPC cost.
No callback symbol lookup, stack scanning, filesystem access, project allocation,
image work, resource retention or wait. All interception callbacks return false.
Module-range JSONL is polled by a separate worker once persecond, max256entries
per snapshot/4MiB total. Range membership is not an exact unload/owner claim.

Descriptor ranges limited256;vertex slots32;scissors16;pipeline subobjects64.
Raw metadata includes original count alongside capped ranges. Unsupported
descriptor types and unresolved tables remain explicit gaps, not empty bindings.
No indirect-draw trace, full deferred replay, shader interpretation, resource
filename recovery or OS/hardware-cursor capture. Origins remain sampled to avoid
stack-walking every graphics call. No draw/state family is excluded by ship type.

### Native light and effect-type metadata (version2 events35–38)

Four pinned Detours hooks, in this isolated observer only:
`0x006A9AB0` light record setter (thiscall,two arguments), `0x006A9C40` enable
setter (thiscall,two), `0x006A9C20` global gate (thiscall,one), and `0x004ECFB3`
global-effects dispatcher (cdecl,one manager). Prologues must match exactly;
the launcher independently verifies the copied executable hash/path. No manual
instruction patching or new geometry interception. Native enum/layout is not a
DirectX light structure.

- Light updates are observed AFTER the original setter returns, at call rate,
  retaining manager, caller, QPC, thread, globally unique observation token,
  slot, enable byte, global gate and all16raw light words. Two eight-word
  fragments share a token. A stable double-read rejects inconsistent values.
  A first-seen bank snapshot at dispatcher entry retains all64slots. At most
  eight banks are baselined; overflow/read faults are explicit. No guessed
  intensity, weapon name or physical light conversion.
- Dispatcher entry walks its existing global list, at most4096nodes, using a
  preallocated8192-entry cycle-detection table and a try-lock. Record each
  object's process-local address, concrete vtable/draw target, next link and
  raw flag word. This is membership BEFORE the original dispatch/visibility
  tests, not proof every member drew. No lifetime epoch, simulation owner or
  attached-trait coverage is fabricated. Original dispatch is always called.
- Event35 `object=manager,device=caller,args=[token,slot,word_offset,8words]`.
  Event36 same labels,args `[token,slot,enable,gate,kind,valid]`, kind1set/2enable/
  3gate/4initialslot; gate uses slotUINT32_MAX and no data fragments.
  Event37 `object=list_member,device=caller,args=[batch,manager,vtable,draw_target,
  next,raw_flags,ordinal]`. Event38 `object=manager,device=caller,args=[batch,
  list_count,cumulative_read_faults,busy,census_overflow]`.
- Native callbacks allocate/wait/write no files and preserve original arguments,
  return values, LastError and original exceptions. `/EHa` drains callback counts
  on structured exceptions. No floating-point interpretation occurs there.
  Worker detaches all4hooks, drains active callbacks, compares original12entry
  bytes and atomically publishes `broad.bin.native.json`. Runner checks this
  sidecar before the exit request. Process-resident storage is not hot-unloaded.
  Partial/lost fragments remain explicit; timestamps do not establish one-to-one
  effect/light/D3D11 ownership.

The streaming analyzer scopes resource/view references by device and observed creation
sequence, clears command reset state, retires pipelines/resources, groups draw
state and compares5second windows. Limits:65,536resource/view/origin labels,
4,096contexts/families; overflow yieldsPARTIAL. Summary retains512families,
16state/texture/descriptor examples each, max4origin samples/family/512total;
summary truncation is explicit and raw events remain. JSON hard16MiB. No semantic
owner is inferred from a graphics handle. Completed origin fragments are released
instead of retaining every sampled stack in memory (4096pending/512summary
samples). Native summaries retain512latest light records/520controls,256history
examples,4096types and65536process-local object addresses; full raw events remain.
An engine return address is not an
object pointer or recovered function name.

## Bounds and rollback

90second tactical detail;16MiB preallocated ring;2016MiB raw cap/warn1008MiB;
32MiB ancillary envelope, **2048MiB total**;existing20GB aggregate. Reserve source+archive headroom
including earlier D3D9/API evidence before execution. Full-rate enumerated events
continue until time/cap; drops/cap/unknown associations are reported, never hidden.

Pinned full-support proxy is installed ONLY in the test copy with existing
hash-verified rollback. Accepted client, disk assets and normal renderer settings
remain unchanged. The gate is restored/unloaded through the existing controller;
survey storage stays process-resident until normal exit. No hot FreeLibrary or
proxy replacement while SFC is running. Early exit/failure preserves partial
evidence; recover only the exact verified interrupted transaction. Existing full-
support/D3D11 shutdown warnings are not automatically resolved by normal exit.

After analysis use established verified archival discipline for useful raw
evidence; do not remove capture/source/rollback files speculatively. Nothing is
staged/committed by these tools and no runtime backend is selected or upgraded.

`archive_completed_images.ps1` is separate maintenance, dry-run by default. It
selects only finished owned runs and exact generated DDS paths, verifies each
ZIP entry by decompressed SHA256 and unchanged source SHA256, writes a restore
manifest, then removes only the verified loose duplicates. It preserves original
game images, mesh packets, logs and capture traces. No automatic gameplay-time
archival. Historical GPU inputs must be restored from that run's receipt before
replaying an archived experiment.
