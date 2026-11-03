# Run253 — four-second gameplay delay narrowed to first texture-file open

## Sponsor run and comparison

Sponsor reports approximately4seconds in `20261101-140030-910390-in-game`. Native gate confirms first insertion **4005.489ms** after first recorded tactical frame (3958.475ms after first asset discovery). Accepted-ticket activation takes0.332ms;receiver was ready35.414s before activation. Receiver launch is not this run's late bottleneck.

**3009.810ms lies between materials_enabled and renderer_assets_started.** CPU base assets are ready in199.296ms(KFF)and288.263ms(FCA);enhanced derivatives399.789/668.084ms. Profiler memory queries max0.639ms. Both owners ultimately insert,normal game exit/unload/renderer0 and unchanged accepted client pass. This is a loading-performance regression;do not describe the overall startup issue as fixed because receiver activation became fast.

Compared fast gameplayRun246(031833)with this run:accepted image,quality,materials,lights and rtx.conf hashes match;build dependency/pipeline policies match apart from the intentionally rebuilt host. No evidence of reenabled verification,changed appearance or an enhancement-completion gate. Reviewed308retained resource-setup profiles;three exceed1second,all recent Run252/253cases. This supports the observed recent regression,but not a particular security-policy/code-change causal claim.

## Narrow reproduction

One standalone600-frame three-owner fixture `20261101-141007-444050-return-fixture` with startup-only operation timings and30local main-thread samples. No SFC/system trace/new symbols. Temporary measurements distinguish initial Renderer,physical hull,lights and scene-start calls,then buffer/index/texture read/create/upload operations. They are bounded64slow operations(at least1ms),recorded only for bootstrap construction;no callbacks or per-frame logging.

- Initial Renderer construction6052.135ms.
- First texture read interval **6019.816ms**,index0. Includes open/seek/read/close;do not state this as an independently timed full6019msCreateFile call.
-29/30samples directly show `NtCreateFile -> CreateFileW -> stream construction` with OBJECT_ATTRIBUTES filename ending in this exact session's `gpu/texture-0.bin`. Initial sample precedes construction. This establishes a prolonged Windows file-open wait inside that read interval.
- File is **262160bytes**,256x256BGRA plus16-byte header;not a high-poly/large-texture processing explanation. Other four texture reads total approximately31.6ms. No GPU resource operation exceeds the1ms recording threshold;hull/lights/cohort startup are also sub-millisecond.
- First sample suspended the owned standalone thread62.276ms;later samples are short. This reproduction is diagnostic,not an unperturbed benchmark. It explains the resource block at a concrete operation;the live run did not record per-file operation durations and is not assumed identical.

The kernel filter/lock responsible for **this texture file** remains unproven by user-mode samples. Earlier Defender activation-file/process-creation attribution does not automatically establish Defender caused this file wait. No security exclusions or claims of a malware flag. Further kernel discovery is not required to identify/remove this critical filesystem dependency.

## Architectural gap

Initial Renderer is still constructed with `prepared=nullptr`,so it opens generated texture-N.bin files on its critical startup thread. Preparation has already decoded/adapted those same pixels in the supervisor before writing the files. Later Renderer instances can accept prepared pixel vectors,but their current native preparation worker also obtains those vectors by reading files. Thus placing the first read on another worker alone would still leave first textured output waiting for it.

This file transport existed before the latest receiver change;it was not newly added or a reverted validation policy. However component timings previously stopped short of these later opens,so they could look fast while actual insertion remained slow. Earlier fixes removed particular blocking operations,not the remaining file dependency. Moving another open earlier,adding waits or changing materials is not a complete correction.

**Smallest reliable next increment:** carry the already-adapted primary texture bytes through a bounded,current-user,session-owned memory transport into the existing prepared-texture Renderer input. Keep exact content/session/asset association and bounds. Cover initial and subsequent assets;avoid a one-model exception. Generated file packets can remain optional off-critical-path evidence,not a prerequisite to first output. Preserve all pixel/UV/material conversions and GPU upload/ownership. This cross-process pixel handoff is not implemented in this investigation.

## Evidence, restored baseline and next action

`artifacts/player-replacement/run253/regression-summary.json`,historical-resource-setup.json,local sample output,diagnostic-source snapshots/build receipt and diagnostic-host.bin preserve the probe definition and measured build. Fixture pixels/depth/text/state,normal child/host exit and sampler0 pass.

Temporary profiling changes in startup_profile.h,d3d9_replay.cpp and d3d9_direct_host.cpp were removed after analysis. Each restored file exactly matches the qualified Run252 source hash;host rebuilt byte-identically to5885D74826A8DCB9FF9FC17A2A183E8213C047C82757FA4D0B947BC913D5EAF9. Existing early-receiver implementation remains intact. No extra diagnostics retained in normal startup,appearance changes or claim of a production fix.

Closed converted texture packets archived losslessly with hashes to restore the existing evidence reservation;original images/geometry/logs intact. Normal launcher preflight restored,not a request for another sponsor test. Keep changes unstaged/uncommitted.

**Next:** implement the bounded memory texture handoff above before another loading-time gameplay checkout. No additional sponsor run needed to rediscover the blocking call. Current four-second performance remains unresolved.
