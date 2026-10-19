# Private GitHub publication — sanitized history approved

## Current disposition — sponsor approval2026-10-18

Sanitization verified:12/12paired commit trees match exactly after removing only
the approved image;authors,messages,timestamps and parent topology unchanged.
Four commit IDs changed. Source masterf0751b5c38cadfe72bb5efbeaf87233aa2bbf901 is
LOCAL-ONLY;sanitized counterpart74dece9f1a16e269b22b1f964ef504008c6dbd18.
Working branch is now codex/github-sanitized. Normal origin push is explicitly
restricted to refs/heads/codex/github-sanitized:refs/heads/master. Preserve this.
Do not merge original master into it. See reviewed commit map/final audit inRun53.

Sponsor: “ok, sanitize the history then, that image sadly has to go”. Remove
docs/reconnaissance/images/20261016-live-camera-sponsor.png from every published
commit. No cropping/replacement image;retain the remaining reviewed game/preview
evidence. History sanitization changes affected hashes,not code or tuning values.

Original master ancestry stays local and in a verified offline bundle. Rewrite
only a fresh independent publishing clone at C:/Project/SFC-Modernize-Publish.
After verification,the working project uses new codex/github-sanitized tracking
origin/master. Original master remains LOCAL-ONLY;never merge/push it into the
sanitized branch. Configure origin.push explicitly for sanitized branch→master;
never --mirror/--all/force push or publish Codex refs,backup bundles or reflogs.
This preserves original historical commits without making future normal pushes
reintroduce the image. All existing development files/dependencies stay in place.

Run53 records execution,backup/tool pins,commit map/audit and remote verification.
No push until the sanitized branch passes the history/privacy checks. Repository
stays private;no license or third-party redistribution grant is added.

## Historical preparation before approval — superseded hold

Repository:https://github.com/tuhs1985/sfc-rendering-modernization
Owner:existing authenticated personal account tuhs1985. Visibility **PRIVATE**,
independently verified through GitHub API/repository metadata. Origin configured
over HTTPS. Created without README/license/initial commit to preserve local history.
**No branch/history uploaded.** GitHub Git-ref API returns409 “Git Repository is empty.”

## Intended publication boundary

Publish reviewed master history only,unchanged;never --mirror/--all/force push.
At review:11commits,608historical paths,675unique blobs,10,646,304uncompressed blob
bytes;largest1,930,589B. No LFS necessary. Include project source/tests,approved
planning references,curated maps/evidence,probe/run/handoff documentation,selected
configs and tentative baseline. Existing authored commit email is GitHub noreply.

Existing .gitignore keeps Game Assets/References,downloaded runtimes/SDKs,compiled
outputs,raw captures/traces,extracted meshes/textures,archives,caches,temp files and
credentials local. History scan,not just current .gitignore,found no excluded
paths/non-PNG binary blobs/recognized token/private-key/credential assignments.
This is heuristic evidence,not a guarantee of no possible secrets. No original
game files or packaged third-party dependencies may be added to make a clone build.
Private repository is not a redistribution license;no license invented here.
Existing source/documentation includes local Windows paths/usernames.

Only refs/heads/master ancestry was audited. App-local refs/codex/*,reflogs and
unreachable objects were deliberately NOT selected and must not be mirrored.

## Consequential privacy conflict — sponsor decision required

Directly inspected image
docs/reconnaissance/images/20261016-live-camera-sponsor.png,blob
cbe09de36100a48eab37d68bd1d4a3f607946585,introduced in e96765a. It contains the
desired game/preview evidence but also unrelated chat content and sidebar titles.
No credential was identified in it,but unrelated personal desktop content must
not be uploaded inadvertently.

User requested BOTH history preservation AND sensitive-information exclusion.
Removing/cropping the image in a new commit cannot remove the old blob from pushed
history. Sanitizing existing published ancestry changes commit hashes;that is not
authorized. No image edit,history rewrite or data push performed.

Next exact action:ask sponsor whether that historical image may remain in the
private repository. If yes,finish remaining visual review/audit of final reviewed
publication docs,commit only reviewed new publication files,and push explicit master
without tags/other refs;verify private visibility,remoteSHA and commit count.
If no,obtain approval for a separately sanitized publishing history while preserving
the original local repository;do not silently rewrite or squash local history.

See [audit](../reconnaissance/evidence/20261018-github-publication-audit.json) and
[run record](../runs/2026-10-18-codex-private-github-preparation.md).
