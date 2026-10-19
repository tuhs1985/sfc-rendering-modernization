# Run41 — prepared native-light discovery launch

SFC-RETURN-20261018-41;2026-10-18 America/New_York. Sponsor requests launch link
and proposes three lights and/or global illumination. Capture does NOT filter to
three or infer GI from apparent brightness. Current extra ship uses one provisional
inspection light;native SFC bank and Remix indirect lighting are distinct questions.

## Baseline / work / engineering judgment

HEAD2fa8032,indexempty,Run40 scoped uncommitted preparation retained. Read HANDOFF,
native light map/probe,existing semantic producer/worker,component build,runner
and pinned qualification paths. FuelGuard attached actual thread via hook;no
daemon/helper/subagent. Reuse same qualified MeshIdentity callback,no new hook
addresses,calling convention or register/state preservation scheme.

Dedicated compile-time SFC_NATIVE_LIGHT_DISCOVERY variant emits read-only light
snapshots through fixed8slot queue at5Hz/owner,max2epochs/900records90s. Raw64slot
bank,enables,derivatives,supplied/view/rawcontext preserved;stable double reads,
existing owner-validity check,nonwaiting queue;no render-thread allocation,IO,
SDK or waits. Existing worker writes/drains before storage removal. Busy/read
failure drops/counts;logging failure disables capture,not original rendering.
No native light override,config application or original ship suppression.

Build output dedicated native-light-tests/m1_light_component.dll. Accepted
artifacts/m1/bin/m1_component.dll NOT rebuilt/overwritten;SHA256 remains
`BCC3BB19276A740E514D5CA4C0A1CF09ACF0169416251C1F552384AE069B8FE1`.
Environment reset by runner;only explicit --capture-native-lights activates new
variant. Current user access/session inherited existing bounded scene bridge.
No pointer used as persistent config ID. Analyzer preserves enable holes,raw
types/words and per-bank changes;bank IDs process-local,not named sun/effects.
Native roles/intensity units/world conversion and GI remain unresolved.

## Tools / reproducibility / validation

VS2026Community18.7.3,C++17 /W4 /WX,production /O2 /MT /arch:SSE2 /Brepro;
PS7.6.5,bundled Python3.12.14. No dependency install. Commands:

```text
pwsh -NoProfile -File tools/m1_component/build_light_discovery.ps1
python -m unittest discover -s tests -p test_*.py
python tools/remix_runtime/run_return_game.py --capture-native-lights
```

9core and10queue tests eachx86/x64 PASS. Actual existing LiveScene producer/worker
compiled as observer variant PASS,2synthetic owner snapshots decoded after drain.
These are synthetic validation,NOT runtime light identification. 235Python tests
PASS4.760s;PowerShell parser/diff checks PASS. Read-only new-mode preflight PASS.
Full accepted8standaloneGPU gates refreshed for modified launcher sources,all
PASS,visible/textured/prepared_image flags true. Existing textured/mask/fallback
behavior retained. No gameplay launched by Codex.

Native observer componentSHA256
`8c839c48974b0eee6bd4c339bf7ef0afeaf3bf309aa8a159708d151da3a01d18`.
Observer qualification receiptSHA256
`EFC315E1537BF2E7C3A66977E31D1BF07575BA8FF1F358324D6F95F8A64AEB06`.
Rendering qualification receiptSHA256
`07696717F4C95D57160CBAEA6EAF7A7B5A0FB39534A5867CA1F6B392096F387A`.
Observer receipt pins source/headers/tests/scripts and binary. GPU evidence exact
folders in rendering receipt;20261018-221254-361196 through221437-045469.
Archived28,811,164B,raw retained,no deletion:
`artifacts/remix-runtime/archives/20261018-native-lights-launch-safety.zip`,SHA256
`42736E200D348CE41A38932152F47CBBE305F5DC3BBA337D6886DCA17A27A081`.
Both clients independently retainSHA256
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.

### Preparation deficiencies retained

First dedicated DLL definition reused LIBRARYm1_component,link warning4070;
separate native_light_component.def corrects module label. Subsequent sandbox
overwrite failed LNK1114,error5;scoped approved build escalation fixed access,
no global security/ACL/UAC change. Unoptimized scene-test build failed before
output with original native exit not recorded;root unproven. Rebuilt with same
/O2 /MT /arch:SSE2 as established producer tests,passed. Future native scene-test
exit now preserved in exit.json. Do NOT declare an established game defect or
silently invent stack-overflow diagnosis from that preparation failure.

## Capture/launch contract and files

[NATIVE-LIGHTS-001](../reconnaissance/probes/NATIVE-LIGHTS-001.md) now documents
actual workflow. Raw6156Brecords<=5,540,400B;16MiB new discovery evidence cap,
8MiB warning proposed within existing32MiB combined nontexture hard cap. Actual
writer is structurally capped900records;combined runner budget enforced as before.
Textures128MiB separate,no new images/continuous screenshots/geometry hook.
Existing90s tactical/300s prepared budget;worker join within established5s.
Sub200ms effects may be missed;not exhaustive weapon-light coverage.

Created native_light_observer.h,native_light_observer_tests.cpp,
native_light_component.def,build_light_discovery.ps1,light_discovery.py,
start_light_discovery_session.ps1,test_light_discovery.py,this record.
Modified m1_live_scene.h behind compile flag,run_return_game.py,
start_return_image_session.ps1,probe,active increment,HANDOFF. Prior Run40 work
preserved. No staging/commit,reference/client writes or active sessions.

**READY FOR SPONSOR RUNTIME TEST**,not actual-light classification/integration
PASS. Exact next action:run prepared launcher from established elevated parent;
usual two-ship skirmish,hold briefly then camera/movement/fire normally,exit at
two-beep cue. Collect native-lights.bin/summary/result and adjudicate. Editable
controls and per-light-ray capability gap remain pending,not silently resolved.
