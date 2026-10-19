# Run53 — remove desktop screenshot from publishing history and publish privately

Sponsor explicitly authorizes sanitizing history after reviewing the image.
Date2026-10-18 America/New_York. Starting mastera08ed6280a638990c5aab895736b0d975e3219fd,
11commits;Run52 preparation is one modified HANDOFF/five untracked reviewed
publication files,index empty. No rendering work,user-setting changes or gameplay.
GitHub repo already PRIVATE/empty;origin configured. Preserve existing work.

## Backup,scope and engineering decision

Verified complete original master Git bundle,OUTSIDE active repository:
C:/Project/SFC-Modernize Engine Backups/20261018-231607-before-github-sanitize.bundle
SHA256829F6653632225EAA109BD473FCE28288E49A7F779FBD1CAE0ABC89ECF810AB3.
Also backed up all six Run52 pending files to20261018-231607-publication-preparation.zip,
same backup folder,SHA256CC31F63D68ED306F131BD44ECA7180561C3BE4CED088070B7CC3C8CB23BA27F1.
Neither backup is uploaded. Original master ancestry remains a local-only ref.

Fresh independent clone C:/Project/SFC-Modernize-Publish;only there rewrite history
to drop exact path docs/reconnaissance/images/20261016-live-camera-sponsor.png,
blobcbe09de36100a48eab37d68bd1d4a3f607946585. All ten remaining tracked PNGs visually
reviewed:game/renderer scenes only,no unrelated chat window. Scene names/HUD and
one Windows taskbar remain ordinary evidence,not credentials/private conversations.

Git2.50.0.windows.1,gh2.102.0,Python3.12.14. git-filter-repo not installed globally;
official portablev2.47.0 script downloaded ONLY to ignored artifacts/publication-tools,
official source commit6f79afc8c90c592a3052e6cc53c2ca8907515bca,
SHA25667447413E273FC76809289111748870B6F6072F08B17EFE94863A92D810B7D94,
reported versiona40bce548d2c. No global package/auth/security changes. Sandbox Git
shell help hit MSYS named-object access denied;scoped Git metadata/tool execution
uses authorized elevated execution instead. FuelGuard current-thread hook attached.

Review own Run52/53 publication code/docs and commit only those paths on original
master before cloning;never stage unrelated work. No proprietary originals,
captured mesh/texture assets,dependencies,binaries or bulk output. Git ignore policy
unchanged. Rewrite command in fresh clone:
python <pinned-tool> --path docs/reconnaissance/images/20261016-live-camera-sponsor.png
--invert-paths --prune-empty never --prune-degenerate never --preserve-commit-hashes

Keep commit sequence,authors/messages/times/topology;preserve textual old-hash
references and publish an explicit old→new commit map. Compare every paired tree
by path/object/mode:ONLY this image may differ. Scan full sanitized ancestry for
excluded paths,binaries,credential patterns and exact forbidden blob. Verify code,
configs and tentative baseline unchanged. No guessed recreation of the screenshot.

Import sanitized master as new codex/github-sanitized in the original workspace;
switch only with clean tree. Existing master stays LOCAL-ONLY,not rewritten.
Normal push refspec must be codex/github-sanitized→master;no other refs. Existing
ignored runtime dependencies stay put;no new GPU/renderer validation required for
docs-only changes,but run Python tests/read-only runtime preflight and client hashes.

## Publication/verification gates

Before push:verify GitHub PRIVATE and no existing heads,source/history audit clean,
forbidden image path/blob absent everywhere,reviewed metadata committed. Push exact
sanitized branch without tags/force. Set remote default master after first push.
Verify remoteSHA/count/private visibility,independently clone GitHub to an ignored
local verification directory and repeat forbidden-path/blob/full-history checks.
Remote API must not return the old blob. No hidden refs or unsanitized packs sent.

Durable files:this record,publication decision/README/HANDOFF,Run52 audited tool/test/
report,generated reviewed commit map and final curated publication verification.
No client/source-asset/config changes. Existing Run49 qualifiers and tentative
material/light values retained;SDK40and other technical uncertainties unchanged.
Results,actual source/sanitized IDs,branch state and final checks appended below.

Exact next action at this preparation checkpoint:commit reviewed publication
preparation,clone and filter safely,validate,adopt sanitized branch,push PRIVATE,
verify. Do not begin rendering implementation or reset appearance settings.

## Actual sanitization and pre-push verification

Reviewed preparation commitf0751b5c38cadfe72bb5efbeaf87233aa2bbf901 created on original
master;the preceding11commits unchanged. Complete source bundle same backup folder:
20261018-231607-publication-source-complete.bundle,SHA256
021DBDF16E55D2A9776039CDFF93C52ECB5CE623CB73B310013BCCFA6B615716,verified complete.

Independent --no-local/--single-branch/--no-tags master clone filtered successfully.
12commits retained;sanitized tip74dece9f1a16e269b22b1f964ef504008c6dbd18.
Four IDs change;all12paired trees,including path/mode/object IDs,identical after
removing only the approved PNG. Author/committer bytes,times,messages and ordered
parent topology match exactly. Old blob absent from every sanitized tree/ancestry
and even cat-file in repacked sanitized clone. No image editing/substitute asset.

Published map provenance:docs/reconnaissance/evidence/20261018-github-sanitized-commit-map.txt,
original filter-tool mapSHA25679ffe52a063b5d7c4c4dccda2184a39313bd88e151daf49f0dadb6cff03785d8.
Pre-metadata sanitized audit12commits/613historical paths/682blobs/9,008,031bytes,
no secret-pattern/credential-assignment/excluded binary/path findings;10remaining
PNGs visually reviewed. Final audit/remote proof follows publication metadata.

Original workspace fetched verified sanitized master into codex/github-sanitized
and switched with clean index/tree;old masterf0751b5unchanged. Only working-file
removal is approved PNG. Origin.push now explicitly sanitized branch→remote master;
push.followTags=false,remote.tagOpt=--no-tags. Old master is recovery-only. Added
*.bundle/exactPNG ignore protection and exact forbidden blob/path audit guards,
with regression test. No runtime implementation or sponsor-setting edits.

Current262Python tests PASS3.703s;read-only light-tuning preflight PASS;both client
hashes still4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29;
git diff --check PASS. Runtime/GPU qualifiers remain source/binary matched. No
game/renderer launched. Next:commit only reviewed publication metadata/guards,
audit that complete new ancestry,push explicit branch and independently verify.

## Completed publication and independent verification

Publication checkpoint b7371ef1e1d1489df8ea10b924e52369e14f35eb:
13 commits, 691 unique blobs, 9,302,367 bytes; ancestry audit has no blocked or
manual-text findings. Ten retained PNGs visually reviewed. Verified PRIVATE and
empty before first push. Used scoped GitHub credential helper without displaying
tokens or changing global credentials. Pushed only sanitized branch to master,
normal fast-forward, no tags/other refs/force. GitHub default branch is master.

Fresh actual GitHub clone artifacts/github-verify-20261018 independently matches
tip, ancestry audit and 13-commit API count. Removed path absent throughout;
removed blob absent from clone object store; GitHub blob API HTTP404. Private
visibility confirmed again. Screenshot removed from active worktree but recoverable
in original local master and external bundles. Do not share unsanitized backups.

This final documentation-only receipt is committed and pushed afterward; final
tip is verified through Git rather than embedding a self-referential commit hash.
Prior 262-test PASS, preflight and client hashes remain valid: no runtime code,
configuration or sponsor tuning changed. No game or renderer launched.

Published source, tests, documentation, configuration, provenance and reviewed
game/renderer images. Excluded proprietary game binaries/model/texture assets,
SDK/runtime binaries, raw captures, builds, caches, temporary files, credentials
and original local refs. Repository requires qualified local dependencies; it is
not a self-contained game distribution. Existing technical limitations unchanged.

Final expected state: clean codex/github-sanitized tracking origin/master, with
only reviewed publication work committed. Original master f0751b5 unchanged and
LOCAL-ONLY. Exact next action: await next sponsor-approved engineering task;
never merge/push the original master into sanitized history.
