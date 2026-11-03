# Run264 —18-carrier test stopped before first live ship output

Reviewed latest `20261102-044108-514298-in-game` (November1local). Sponsor reports18carriers plus fighters,and no replacement ship ever appeared.

## Confirmed failure

`DIRECT64_FAILED offline GPU completion5s limit` at the first live cohort,sourceframe48. Bootstrap output was delivered once;the first real ship scene did not complete. Receiver retired with1frame,gate records303/commits0. The visual report matches the saved output evidence.

Slow completion recorder captures id3/source48:total4,996,020µs,query calls3,494µs total/max58µs,asset servicing91,166µs,and4,899,898µs in polling pauses across8,983polls. This proves an outstanding rendering/output-completion wait,not five seconds spent computing geometry or a proven five-second GPU execution duration. Sleeping while waiting does not itself establish the cause of missing completion.

Source captured28asset associations across8model names:FCV3,LDD2,LFA1,RFA1,KCL1,FFT4,RFT6,LPFT10. Renderer admitted8unique assets plus20shared references;first live scene submitted8instances,with4temporarily omitted. Native asset CPU prep0.786–22.779ms,per-assetGPU admission0.006–5.049ms. About50.75MBretained asset resources. These are observed identities,not proof of every physical ship/fighter in the sponsor's mission.

The physical-hull32-entry limit from Run262 was not hit in this attempt:only8live instances were submitted,versus the explicit hull-submission exception previously. That unresolved defect remains and still needs correction before claiming larger fleet support. Native gate terminalpartial0/terminalreason0;recoverable submission changes did not permanently disable replacement.

## Lights,cleanup and limits

Accepted configuration confirms **effects.enabled=false**. New weapon-light integration was off. Existing native scene0/1 and project_fill were applied at first live frame;project_fill is the accepted dome using the160byte uniform-white DDS `f5d105dd91e20553315a24d5ea412d94a0560a58f5fd8d230a6ae04cd7d1e062`. No appearance setting was changed during analysis.

Earlier Run256 independently sampled a long first-cohort completion wait with the runtime command thread blocked opening that dome DDS. This is a concrete existing investigation lead,not proof the same file/function caused this run. Current slow counters do not identify the runtime worker's blocking operation. Do not attribute this failure to Defender,VRAM exhaustion,the carrier count or weapon-light API work without additional evidence.

Game exited normally;controller8means target-process reclamation,not controlled hook unload. Controller no longer running,proxy restored,all copied critical hashes match the pre-run manifest,accepted installation unchanged,and no owned game/renderer/controller processes remain. Renderer exit1is a real completion failure;do not hide it as an early-exit success. Guard reports no remaining owned GPU processes.

## Next exact action

Investigate first-live-frame runtime completion using existing Run256 dome-file attribution and this new failed-wait timing. Split actual runtime worker/file/shader/upload progress at the narrow wait,not another broad gameplay discovery capture. Do not silently increase5s guard or turn off sponsor lighting. Correct the separate hull32limit before the next large fleet checkout. No runtime edits/new gameplay were performed for this analysis;effect integration/emission recorder remain parked/off.
