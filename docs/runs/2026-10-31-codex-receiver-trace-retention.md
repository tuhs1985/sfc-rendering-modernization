# Run250 — ETL saved but circular retention excluded the wait

Reviewed sponsor capture artifacts/player-replacement/run248/trace-20261101-034605,fixture20261101-034609-002871-return-fixture. Observer attached before activation,started trace at readiness age50.118s and saved7,697,393bytes. Fixture600-frame pixels/depth/text/state/normal child/host exit pass. CreateProcessW again5001.711ms;no SFC launched.

## Coverage correction

WPR reports zero lost events/buffers and a17.071s header interval. That does **not** establish retention of the whole interval in circular mode. Raw ETW decoder confirms all retained global CSwitch events are in QPC5567221865171..5567232858343 (~1.099s). The measured launch wait is5567151205080..5567201222189. Earliest retained context switch is2.064s after launch returned;zero global CSwitch events exist inside the wait. Host stack events likewise begin after the interval. The32MiB circular buffer retained only the tail,rather than the process wait. Do not attribute a nearby later stack or the zero-loss counter to a cause inside the missing interval.

Host40464 main thread41504 identified by recorded thread start in d3d9_direct_host.exe. Local native OpenTrace/ProcessTrace decoding succeeds(status0);raw events/decoder retained in run250. xperf local-symbol stack summary contains106hits but none in the wait. Existing local ntkrnlmp symbols only;no new symbol downloads. xperf reports one unrelated invalid-event warning for another process;raw decoder coverage result is independent of that summary warning. No MiniFilter Delay records in this retained interval. Do not call this evidence against Defender.

## Corrected recorder

Updated same run248 observer/profile,no production changes:

-256MiB circular kernel buffers instead of32MiB.
-Only process/thread,loader,CSwitch and ReadyThread events/stacks. Removed broad sampled CPU,file/filter categories to reduce traffic;wait/ready stacks remain the mechanism for attribution.
-Stop0.25s after existing gpu/receiver.log appears (child main is running),with existing activation+8s or20s trace fallback. This avoids recording several unnecessary seconds after process startup. No renderer-side diagnostic notification or new startup file introduced.
-Reserve672MiB under20GB:288MiB existing player fixture+256MiB possible raw finalization+128MiB compressed output. Final128MiB check still reports partial if exceeded;not a guarantee about merge size. Recorder retains refusal of existing trace,running SFC/nonadmin/insufficient budget and owned-trace cleanup.
-Early fixture manifest/native-ready QPC trigger fix fromRun249 remains. WPR profile-details accepts Memory/256buffers and only expected categories;Python parser passes. Live elevated retention still requires validation;do not promise success before raw coverage check.

Current token still lacks full Administrator/profiling permission. WPR status confirms no recording left running. No production implementation/material/driver/Defender edits,new runtime campaign or staging/commit.

To retain this reservation,losslessly archived567MiB of generated DDS copies from117closed successful historical runs,reclaiming530.9MiB. Per-file and archive hashes checked before exact loose-copy removal. Source game images,captures,geometry and logs unchanged. Restorable receipts per closed run and artifacts/player-replacement/run250/dds-archive-receipt.json. These generated-file archives must be restored if a historical comparison needs loose DDS paths.

**Next:** sponsor repeats the same run248/trace_receiver_startup.ps1 command once from existing Administrator PowerShell,no gameplay. Review actual raw wait-interval coverage first. Current evidence still proves only the five-second Windows process-creation wait,not its internal owner. Earlier claim that successful save/no-loss meant the wait was captured is withdrawn.
