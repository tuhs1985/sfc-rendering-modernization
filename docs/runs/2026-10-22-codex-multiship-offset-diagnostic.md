# Run115 — restore previous offset for multi-ship delivery inspection

2026-10-22 America/New_York. Sponsor authorizes common previous camera-left
offset before optimization/replacement. HEADd40f8f2,Run113implementation and
Run114review changes already unstaged,indexempty. FuelGuard attached through
trustedhook;no helper/agent. Reviewed HANDOFF,Run114,contract/probe,current relay,
host,output writer/compositor/qualification and accepted previous FCA run.

CONFIRMED previousrun`20261022-042653-754380-in-game/live-owner.analysis.json`
records`camera_offset=[-15.897722721099854,0,0]`. Restore exactly that requested
distance,not a new arbitrary amount or current first-selected enemy's smaller
mesh width. One common translation of all returned objects preserves relative
positions;camera-left conversion reused at backend/compositor. Worldheight,
model scale,source simulation/camera observations and original drawing untouched.
No suppression,extra buffering,prediction or delivery optimization in this run.

New`tools/d3d9_proof/multi_ship.toml`contains the diagnostic distance. Bounded4KiB
parser accepts finite0..1e6nativeunits and rejects unknownkeys/bools/nonfinite/
negative values. Zero remains separately qualified aligneddiagnostic option.
Receipt freezes this setting;runtime metadata saves accepted config and offset.
Native GPU metadata uses existing float32representation;qualifier compares the
same encoded representation. Union coverage stays explicit;no ownerpicking claim.

Changed source:this config;`multi_scene.py`,`live_owner_timing.py`,
`game_output_writer.h`,`d3d9_direct_host.cpp`,`multi_scene_relay.py`,
`qualify_multiship.py`,`run_return_game.py`,`start_d3d9_multiship_session.ps1`,
`tests/test_d3d9_multi_scene.py`. Documentation:contract/probe,this record,
authoritativeHANDOFF and curated offsetevidence. Priorwork preserved.

Validation in progress:433Python tests PASS including exactold-distance and
invalidplacement cases. Rebuildhost/receiver/addon,actual two-model standalone
GPU fixture,source-locked requalification and read-only preflight required before
returning launcher. No SFC game started in preparation. No stage/commit/push.

Next exact action:finish bounded offline offset qualification,then use the same
multi-ship launcher with different models;keep both alive,inspect returned copies
through camera/motion changes,exit after finaltwoLOWbeeps. Compare omissions
againstRun114,not just visual ease of observation.

## Final checkpoint — READY FOR SPONSOR RUNTIME TEST

433Python tests PASS. Host/receiver/addon rebuilt with existing strictcompiler
settings;native slot649,combinedpost65,loadedlight11,return37,source18,
calibration22/search13/broad14/worker checks PASS. No nativehook or transport
format redesign. Existing camera-left conversion at both renderer and compositor
agrees with configured float32offset`[-15.897722244262695,0,0]`.

Actual two-model standalone fixtures(dateprefixUTC20261023):

- `023729-602838-return-fixture`:581/600steadycohorts,731totalpaired,
  owner1/3draws805/910.
- `023920-264420-return-fixture`:550/600steadycohorts,668totalpaired,
  owner1/3draws748/849.

Both rendered FCA/RCA from historical capture packets with syntheticposes,
two assetACKs,zeroassetrejections,25919changedreturnedpixels,untouchedborder,
exactnativeHUD/scene,graphicsstate0errors,resize/recreation andnormalownedexit.
Existing≥90%600-frame gate unchanged;not proof of improvedactualSFCdelivery.
Imagebudget91,506,338bytes<128MiB;remaining originaldiagnosticbounds unchanged.
See [curated evidence](../reconnaissance/evidence/20261022-d3d9-multiship-offset.json).

Native-light dependency gate correctly rejected changedrunner source;reran its
actualoffline queue/observer tests with`light_discovery.py`,PASS. Then
`qualify_multiship.py --fixture artifacts/remix-runtime/runs/20261023-023729-602838-return-fixture`
passed,including actual native120update/onecapture/retirement/stop check.
Matchingearlyfixture separately inspected against currentlocks. Read-only
`run_return_game.py --multi-ship`preflightPASS. No game launched by Codex.
Clientoriginal/copySHA unchanged`4D6576…320C29`,copiedproxy`E35E4E…44CAB7`.

Prepared entry point remains
`tools/d3d9_proof/start_d3d9_multiship_session.ps1`;now says copies CAMERA LEFT,
not on top. Keepboth alive,brieflyshowboth,then move/turn/swapcamerasnormally,
observecopies forflicker andexitafterfinaltwoLOWbeeps. No deliveryoptimization,
suppression,z-bias,appearance tuning,sourceartifactchange,stage/commit/push.
HEAD/index unchanged;all priorRun113/114work retained. No activeowned fixture
or session required to resume. Next exact action:run prepared sponsor offsettest.
