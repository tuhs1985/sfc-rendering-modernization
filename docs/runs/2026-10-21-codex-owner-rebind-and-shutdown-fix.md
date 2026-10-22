# Run96 — bounded resident-asset rebind and correct removal wait

2026-10-21 America/New_York. Sponsor "go" authorizes Run95next work:fix runner
shutdown scheduling,then safe fresh-epoch reconnection. Read authoritative HANDOFF,
Run95evidence,live source/worker/relay,light collector,controller/runner wait logic.
Approved component/adapter gate allocation unchanged;no new formal TRL claim.
HEADd29111f7,index empty,existing dirty work preserved. Fuel Guard trusted recent
hook receipt;20% advisory later received,continued existing bounded authorized
work. No helper/agents/SFC launch/stage/commit/push or accepted install changes.

## Engineering judgments / implementation

CONFIRMED Run95camera return has identical fresh geometry/groups/images,new epoch.
Old lifetime absence is NOT native death. Chosen approach:full content qualification
plus acknowledged worker binding,retaining resident assets. Rejected bypassing
retirement,matching pointers alone,stale pixel holds,restarting/reconverting the
renderer on every return,broad engine RE/new hooks. No ABI/calling-convention change.
Contract and probe capture exact bounds/protocol in durable form.

Controller already waits120s after gate. Prior runner waited only15s after90s
formal plus variable prep. Replaced with gate-relative120s+35s bounded stop/unload
allowance,clamped to existing workflow deadline. Stop owned renderer before wait,
so orderly renderer exit is not rejected while controller is still waiting.
Existing controller code unchanged,gate/byte restoration/unload checks preserved.

New control128bytes in verified mapping gap;session/PID,guard,monotonic generation,
fresh labels,checksum,resident cookie and worker ACK. No expansion of16MiB map.
Full content signature includes geometry,LOD,group flags,resolved original primary/
secondary image hashes/role;secondaryID0 treated absent,nonzero missing rejected.
Image hash cache uses unchanged file stat identity;no repeat decode or conversion
on recovery. Initial content verification still required,not pointer authority.
Worker changes selection between submits,retains sequence watermark/Scene/GPU
resources,discards former-owner input and relies on unchanged exact output checks.
Python <=10Hz scan excludes stale>8frame owner rows;unique known-fixture content
only,ambiguity/changed content explicit partial. No generic native player flag.

Found additional CONFIRMED blocker:light observer permanently held first two
epochs,so fresh owner3could never receive fresh light snapshot. Added live-D3D9-only
fixed two-slot retirement release/stale-slot recovery;new capture always labelled
fresh epoch/model/source. Old queued files cannot qualify. No light replay fallback
in SFC,no global expansion of collector. Native tests explicitly exercise this.

Dedicated alive-only camera-recovery launcher adds two away/return cycles;existing
destruction runner retained. State/journal capture full window remains default-off;
original offset entry file unchanged. Current settings/texture origin/viewport/gap
and source client hashes preserved. Original rendering remains ON.

## Files changed in this run

- New tools/remix_runtime/controller_shutdown.py
- New tools/d3d9_proof/owner_rebind.h and owner_rebind.py
- tools/d3d9_proof/live_owner_input.h
- tools/remix_runtime/live_owner_timing.py
- tools/remix_runtime/additive_qualification.py
- tools/remix_runtime/run_return_game.py and start_return_image_session.ps1
- tools/m1_component/native_light_observer.h and m1_live_scene.h
- tools/remix_runtime/light_discovery.py
- tools/remix_runtime/source_timing_fixture.h and run_return_fixture.py
- tools/remix_runtime/lifecycle_capture.py
- New tools/d3d9_proof/start_d3d9_camera_recovery_session.ps1
- tests/d3d9_live_owner_tests.cpp,native_light_observer_tests.cpp,test_lifecycle_capture.py
- New tests/test_controller_shutdown.py,test_owner_rebind.py,test_owner_recovery_relay.py
- New contract/probe,this run record and HANDOFF.

## Validation to date

Native ordinary-D3D9 worker build PASS;loaded lights11checks,private timer and
deferred diagnostics PASS. x86/x64 ingress142checks and owner46checks each PASS
(stable store sizes,session/checksum/guard/generation/cookie/late completion).
Dedicated observer native core9/observer17checks each architecture plus actual
normal/tuning/lifecycle worker tests PASS. No new runtime hook test claimed.
Final393Python tests PASS,including shutdown timeout/failed-exit/safety enforcement,
ACK-before-light-retarget,ambiguous/mismatched content,resource-ID independence.

Fresh actual Run95FCA2/2and3/3 content signatures both
60db5ad77a07374cf83a0997c09d889ffbd27740c306b31c382f5920f8342eda.
Signature excludes pointer/resourceID/provenance changes;unit tests reject changed
images/geometry-token or ambiguity and require ACK before light retarget.

Standalone060658fixture initial binding599/600,state/resize/shutdown PASS.
Standalone061019fixture switched actual resident worker to synthetic12/12then13/13,
ACK generations2/3,native output780valid packets,invalid0/unqualified0,588/600
displayed across switches,state_errors0,resize/recreation,normal owned exit. No
renderer restart/asset rebuild;synthetic historical light directions labelled as
such,not a gameplay lighting claim. Further final fixture/evidence export pending.

Initial content-signature probe correctly rejected secondaryID0 as unresolved;
inspection confirmed it is the existing absent-secondary path. Corrected to
explicit None,not guessed image/glow. Nonzero missing image remains unsupported.

No continuous screenshots/readbacks/extra geometry logging. Partial runtime053837
retained unchanged,including its honest cleanup failure. No data relabelled PASS.

## Final checkpoint

Final actual-proxy fixture061525-988799:591/600displayed during two rebinds,
152367changed pixels,border untouched,state_errors0,resize/recreation,normal
owned renderer/receiver/fixture exit.782valid input packets,invalid0/unqualified0.
Matched presentation audits:initial owner3:122,owner12:180,owner13:292. Source
rejected0,audit drops0,completion invalid0;final control ACK3/rejected0. Resident
asset retained;no renderer restart. Binary control evidence saved128bytes. No
gameplay success claim. Final additive qualification now REQUIRES both synthetic
rebinds plus matched current-frame presentation,not merely request ACKs.

Fresh light and actual lifecycle-worker qualifications current;native worker
393Python/parser/state/frame tests above PASS. Windows PowerShell5new-launcher
CheckOnly PASS,no game started. Python/PS parsers and git diff --check PASS.
Native callback state-preservation/hook code unchanged;actual controlled SFC
unload still requires next sponsor test,not inferred from clock unit tests.

Three fixture generated-input sets compacted recoverably after analysis,all
199entries/fixture decompressed and hash-verified before removal. Final archive:
artifacts/remix-runtime/archives/20261021-061525-988799-return-fixture-binaries.zip,
SHA256300AB4A0A5053F86921411EBA94F6AE88B4D55BD7B980ECDEC1B8ACB5144DD56;
82188024B->6861823B. Other two receipts stay in their run folders. Raw source
packets/logs/metadata and control evidence kept. Aggregate10273219877B/20GB.
No partial actual game evidence cleaned through the clean-game archive guard.

Both supported client executables freshly verified unchanged SHA256
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.
No SFC or owned worker active,handles/jobs from checks closed. HEADd29111f7,index
empty,prior and new work entirely unstaged/uncommitted. No commit/push.
READY dedicated camera-return launcher. Next test is alive camera return,NOT
destruction/replacement. Wait for two LOW exit beeps after restoration message.
Real SFC recovery latency,correct fresh light retarget and controlled live unload
remain runtime uncertainties;initial~14s preparation still separate unresolved
optimization. Native vendor disposal warning40 remains open.
