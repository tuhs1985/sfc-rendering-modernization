# Experimental owner-frame inbox — offline qualification

2026-10-20,Run78. Renderer-neutral input prototype,NOT a complete-scene seal,
production live bridge revision or closure of the renderer-independent gate.
Existing source hooks/30Hz diagnostic bridge remain unchanged.

## Meanings and wire

tools/d3d9_proof/frame_ingress.h defines a296byte,version1 immutable OWNER packet:
magic/version/size/reserved;session,publication sequence,source frame,state hash,
asset hash,owner epoch,asset revision;offer and deadline QPC;52finite floats
(model/view/projection16each,viewport4);checksum. No addresses,SDK types,COM
interfaces,resource IDs or GPU handles. Explicit layout assertions on x86/x64.
Matrices use the already-qualified neutral replay convention;no17word cast,
new orientation/UV/normal correction or geometry conversion introduced here.

State FNV covers exactly the208matrix/viewport bytes. Whole-packet FNV covers
header,identity,time and state. These detect corruption,NOT malicious same-user
authentication. Replay asset FNV covers decoded vertices/indices/groups and
ordered unique decoded image files,excluding poses,viewport and filenames.
Original SHA256 provenance remains in scene.json. Live asset qualification is
still an upstream obligation;FNV alone is not a proven fresh asset association.

One preallocated1,344byte channel contains a fixed header and four320byte slots.
No pointers or process-local locks. A single producer publishes monotonically
increasing sequences;single consumer acquires READY slots via Interlocked CAS.
All copying occurs while owning the slot. Producer scans bounded Free then Ready
slots,never overwrites Reading/Writing. It may replace unclaimed Ready packets;
no allocation,wait,I/O,unbounded retries or GPU calls in publish/take. Consumer
retains highest sequence among its bounded sweep and discards older/expired
packets. New arrivals after that sweep are handled next time,not magically
included in an atomic global-latest snapshot. Sequence gaps remain explicit.

Offer time can be later than the consumer's pre-acquisition clock sample due to
concurrent publication. That is NOT inherently malformed. Final usability checks
current time again;future/expired results cannot pass final admission.

For a completed result,usable requires exact current expected session,sequence,
source frame,epoch,revision,state hash and asset hash,plus eligible=true and
offer<=now<deadline. Retirement,conflict or unqualified assets set eligibility
false. Pointer reuse must have a new epoch. GPU resource-generation/ownership
remains in the separate qualified output wire. All participants must stop/join
before unmapping or unloading. A stopped channel never resumes by clearing a
flag;create a new session. Deliberate blocking is only in standalone test workers.

## What the actual tests do

- x86/x64 native tests:142checks each,100,000concurrent publications each,
  malformed/nonfinite/hash/viewport rejection,identity/revision mismatch,
  retirement eligibility,false future/expired admission,all-owned saturation,
  immutable reading slots,stop,late result followed by newer valid result.
- Actual x86 producer/x64 receiver fixture uses unique GUID-named Local mapping
  and protected current-user SID DACL,explicit name/session handoff and bounded
  owned child process. It transfers deterministic matrices and checks exact bytes.
  Normal,35ms slow receiver,producer disconnect,malformed injection and stop all
  pass. Receiver catches up without an accumulating FIFO. These are synthetic
  state tests,not GPU rendering or actual SFC lifecycle proof.
- Default-off --latest-input in run_direct64.py drives the ACTUAL ordinary-D3D9
  Renderer and Remix output copy/x86 GPU receiver with an independent300update
  source thread at synthetic60Hz. It cycles three previously captured FCA states;
  it is NOT original-rate playback or a real SFC source. First24warm presents
  finish before starting timed source publication. Subsequent states use1present.
  No USD/OBJ/SDK geometry APIs. Legacy default replay mode remains available.
- --inject-lag-ms35or60 deliberately pauses the renderer worker at input75.
  Source thread continues. Record every completed offer-to-GPU-receiver-ACK cost,
  including late results. input-timing.csv identifies source sequence separately
  from the existing output wire's contiguous transport sequence. The legacy
  output sequence must NOT be reinterpreted as a live source publication sequence.

## Limits and next binding

Prototype mapping1,344bytes,four packets;source300updates,5seconds nominal;
progress10s limit;owned GPU workflow90s/128MiB scratch/2MiB console,outer100s;
original output limit1920x1080/128MiB unchanged. No CPU images in timing runs.
Logs/CSV bounded and analyzed generated payloads recoverably ZIP-compacted.

Late timing packets DO reach the standalone receiver's private cache so their
full cost is measured;there is NO onscreen compositor in this test. Unit tests
exercise the admission function,not a game-facing implementation of it. Do not
claim runtime display omitted all late packets or full end-to-end live matching.
In replay the expected key used for deadline accounting is the input packet key,
not an independently observed current SFC frame. Source seal/current-frame
authority and raw-to-neutral binding remain the next work.

Next:bind fresh validated semantic owner snapshots to this immutable input path
outside the inherited30Hz cap,then qualify authoritative Present-side expected
identity/conflict invalidation and raw-state conversion offline. Only afterward
measure simultaneous SFC/renderer load without extra-ship drawing. No whole-frame
buffering,prediction,stale pixels or original suppression authorized by this unit.
