# Run111 — explain current pipeline and publish reviewed checkpoint

2026-10-22 America/New_York. Sponsor requests README explaining how information
leaves SFC,enters D3D9 and reaches Remix,then commit/push before generic-model
work. Starting HEAD0fc1300 oncodex/github-sanitized,indexempty;remote master
d29111f7a513c4510c4d33aeeda2c355d98443a5. Existing0fc1300is one local commit
ahead. Run103–110 source/tests/docs were pending and are the reviewed checkpoint
to preserve,not unrelated unreviewed work. No further rendering implementation.

Read HANDOFF/operating convention,Run103/105/108/109/110,publication safeguards,
scene/persistent/buffer contracts and actual native capture/adapter/receiver/
selector code. FuelGuard attached throughtrustedglobalhook;no daemon/helper/
agent started. GitHub API verifies repository PUBLIC,defaultmaster,as sponsor
previously disclosed;do not change visibility or reintroduce removed desktop
image/history. Existing push mapping sanitizedbranch→master preserved.

## Documentation changes

- RootREADME:current ordinaryD3D9 path,upstream reversible in-memory detours,
  semantic/runtime geometry versus on-disk original image resolution,bounded
  current-user bridge/worker preparation,persistent simulation pose andactive
  camera,ordinary VB/IB/texture/DrawIndexedPrimitive submission,Remix interception
  versus SDKmesh registration,GPU output copy andx86receiver,ReShadeD3D11return,
  exact prior-frame/depth/HUD pairing andfenceownership. NoOBJ/Toolkitrequired.
- Explicit FCA-only selection,multiownerregistry≠multiassetdisplay,nextgeneric
  coverage,remainingomissions,cleanup caveat,recordingcausalityunresolved,and
  no originalsuppression/replacement oraggregateTRL claim.
- Currentbuffered preflight/launcher inpreparedworkspace versus separateolder
  tuningworkflow;publicvisibilitycorrected;entrypoints andsource map linked.
- tools/d3d9_proof/README.md:clearly label earlier isolated proof sections as
  historical scopes andlinkcurrentoverview. No historical evidence overwritten.
- This run record and authoritative HANDOFFpublication checkpoint.

## Validation and publication boundary

425Python tests PASS. Existingnative persistent18checks eachx86/x64,slot649,
actualGPUbuffer33eachx86/x64 PASS;both buffered/unbufferedread-onlypreflights
PASS. NoSFCgameplayornewbuildnecessaryfordocumentation. Existingnativebuild/
hardwarequalification andactualrun evidence remain inRun103–110. READMErelative
links,JSON/PSsyntax/whitespace reviewed. Original/copied executable hashes both
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29unchanged.

Publication includes reviewed pending implementation/tests/contracts/probes/
curatedJSON/runrecords plus READMEupdates. Exact file inventory is the containing
commit's diff against0fc1300;do not publish localmaster,recoveryrefs/tags or
ignoredgeneratedfiles. No new screenshot/image/media files. Game Assets,
References,rawcaptures,extractedgeometry/textures,binaries,SDK/runtime downloads,
archives andcredentials remainexcluded. Entire sanitizedbranch ancestry is
scanned withtools/recon/audit_git_publication.py before push;old reviewed image
blobs are historical,not newly added screenshots. This heuristic audit does not
guarantee absenceofallpossibleprivacy/rights issues.

Commands (existing bundled Python used on this workstation):

```powershell
python -m unittest discover -s tests -p 'test_*.py'
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/d3d9_proof/start_d3d9_buffered_scene_session.ps1 -CheckOnly
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/d3d9_proof/start_d3d9_persistent_scene_session.ps1 -CheckOnly
git diff --check
git diff --cached --stat
git commit -m "Checkpoint persistent D3D9 return and document rendering pipeline"
python tools/recon/audit_git_publication.py --ref refs/heads/codex/github-sanitized
git push origin refs/heads/codex/github-sanitized:refs/heads/master
git ls-remote origin refs/heads/master
```

The containing commit identifies this checkpoint without embedding a circular
self-hash. Post-push remote SHA/status/audit result are recorded in the ignored
`artifacts/publication/20261022-d3d9-checkpoint-receipt.json`;no credentials or
private capture payloads are copied there for publication. Final response also
reports exact SHA. If push fails,retain localcommit andreportblocked rather than
forcepush or alterremotehistory. No sourcework beyond existingcheckpoint.

Exact next action after publication:define bounded generic-asset/multi-owner
D3D9 extension using currentcapture/registry,keeping FCA diagnostic baseline,
then prepare mixed-race/all-visible-ship tests. Do not claim that coverage now.
