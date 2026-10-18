# Run31 — diagnose blocky textured return and correct actual rendering size

SFC-RETURN-20261018-31;2026-10-18 America/New_York.
Authority: sponsor supplies two completed `-TexturedShip` runs and screenshot;
explicitly requests troubleshooting blockiness only, not SFC screenshot tooling.
No new gameplay run started by Codex. No original suppression/requirements change.

## Starting baseline and observations

HEAD e96765a1a34c15212ed22f11edeb9a708b9fc18d;dirty prior work preserved,index
empty. Read HANDOFF,Run30,texture/additive contract,actual producer/compositor,
fixture and SDK source/options. FuelGuard attached actual thread via hook;no daemon.
No helper/delegation. Scoped offline build/GPU access only.

Actual runs under `artifacts/remix-runtime/runs/`:

| UTC run (-in-game) | Produced | Acquired | Failures | Bytes |
|---|---:|---:|---:|---:|
|20261018-184126-281063|738|737|0|53,839,075|
|20261018-184419-628232|737|734|0|54,494,080|

Both fresh FCA owner2/revision2,original textures,reported1920x1080 transport.
Normal game exit,controller0,renderer0,clean hook unload,original critical and
launcher checks true. Sponsor screenshot shows visibly coarse extra ship;do NOT
promote transport descriptors into actual internal-render resolution proof.
No comprehensive new sponsor gameplay checklist claimed from this report.

Screenshot preserved unchanged at
`docs/reconnaissance/images/20261018-textured-blocky-runtime.png`,SHA256
`D867102DB533957AECD1DE8FA0BBAC91D9D1AC3DB00B8967CE7C3635102A775F`.
Capture-tool functionality deliberately not investigated.

## Root cause and correction

**CONFIRMED implementation defect:**the producer created a256x256 hidden HWND
even in the full-HD profile. Local SDK source
`artifacts/remix-runtime/deps/rtx_remix_api.cpp:1642` shows `Present` reads that
HWND's client area and resets the swapchain to it;output-copy code blits with
nearest filtering. Thus1920x1080 destination textures did not ensure full-HD
rendering. Static source SHA256
`9C9FDA8A9F020878D5363FDEAE7D93051E6404A39A7F8A05729996318CFDE552`.

`tools/remix_runtime/ship_live_host.cpp` now creates its hidden client at actual
output dimensions,verifies client area,and checks swapchain presentation parameters
AFTER EVERY SDK Present. Mismatch stops the external producer;native SFC continues.
One bounded log marker records verified client/swapchain dimensions. Textured mode
explicitly sets `rtx.resolutionScale=1.0`;local options default0.75 was another
unqualified internal scale. No new supersampling/upscaler or texture/material edit.
Legacy256-square mode still has256-square client. Hidden window remains hidden.

`tools/remix_runtime/qualify_live_return.py` now requires the actual post-Present
1920x1080/scale1 marker AND native silhouette IoU>=0.98 for textured qualification,
in addition to existing edge/centroid/background limits. This supersedes Run30's
relaxed textured-only silhouette acceptance;the old coarse test should not have
been treated as adequate sharpness validation. Strict magenta gate unchanged.
`tests/test_live_return.py` adds regression for window dimensions,client check,
post-Present drift check and explicit native scale.

**Corroboration:**first corrected bounded GPU fixture
`20261018-184913-727722-live-private` logs actual client/swapchain1920x1080,
scale1.0. Same recorded geometry/camera:maskIoU improves0.920925→0.998869;
centroid error0.340621→0.038876px;out-of-band unexpected/missing1/5→0/0;
quantized image colours113→244.59/59 synthetic-motion callbacks display;127/130
new images acquired,0 private failures. These are offline findings,not a claim
that screenshot brightness or native-game lighting parity is fixed.

## Reproduction, limits and evidence

Bundled PS7 `-NoProfile -File tools/remix_runtime/build_live_return.ps1`:PASS,
native request89checks eachx86/x64,/W4 /WX. Bundled Python with TEMP/TMP set to
ignored `artifacts/test-temp`: `-m unittest discover -s tests -p test_*.py`,
206PASS/4.232s. Final eight gated GPU runs and hashes recorded in
[evidence](../reconnaissance/evidence/20261018-textured-resolution-correction.json).
All eight final gates PASS:185001-913204 textured,185023-502843 slow textured,
185046-594729 disconnected textured,185110-494728 direct,185118-642449 callback,
185127-696521 slow,185137-336230 disconnected,185145-204249 strict visible
(all20261018 prefixes and-live-private suffixes). Final textured normal131/129,
slow129/127,disconnected3/2 produced/acquired;0private failures throughout.
Normal/slow footprintIoU0.998869;legacy visible0.994603. Disconnected host1 is
intentional,not a normal-exit claim. Qualification and read-only preflight PASS.
New host SHA256 `94B3B77A6343AB2C2F0AD5261FD127499E465706D092BCD137F364AA8B753243`;
qualification SHA `36282C11ED4700D29AB73C734DEA4392F8044355A849A6D23EBA4FB9AEBE5187`.
Flags: `qualify_live_return.py --execute` with
`--addon --textured`,same+`--slow`,same+`--disconnect`,direct,
`--addon`,`--slow`,`--disconnect`,`--addon --visible`;then `--qualify` those paths.
Source/binary qualification must match before gameplay. No SFC launched by fixtures.

Probe remains [REMIX-TEXTURED-RETURN-001](../reconnaissance/probes/REMIX-TEXTURED-RETURN-001.md).
Same90s tactical/285s Python/300s prepared limit,100ms source-request-age policy,
four surfaces<=128MiB,32MiB non-image evidence,128MiB image output,10GB aggregate.
One fixture pixel mask only;no continuous screenshots or geometry firehose.
Same current-user transport,elevated parent and cleanup policy;no new UAC/security
or accepted-install modification. Lighting/fullbright,secondary images,SDK40,
scene-depth/UI overlap,exact replacement synchronization remain separate findings.

Two actual runs archived (raw retained,no deletion):
`artifacts/remix-runtime/archives/20261018-textured-blocky-runtime.zip`,
12,825,052B,SHA256
`C9A09EA2DB04ADBFAD60A0BA019A87F92BEEAE74911A6CCD0CBF3299A3916407`.
All new source/doc files listed above plus this record,evidence JSON,probe/contract
updates and HANDOFF. No unrelated edits,index empty,no stage/commit.
Final eight GPU sessions archived at
`artifacts/remix-runtime/archives/20261018-textured-resolution-correction.zip`,
28,714,575B,SHA256
`A1909870E86EA3A68CB4431319EB69E5BFE481FD419441859CD4B37120402BF5`.
Both new archives CRC-checked. Raw retained;no deletions. New Markdown references,
evidence JSON and git diff --check PASS. Screenshot copied unchanged as curated
evidence;no reference-original or original game file edited.

## Result / exact next action

**Blockiness cause and correction corroborated offline.**Actual sharpness on the
next SFC run remains sponsor-verified;not a milestone or replacement PASS.
No persistent runtime session needed to resume. Use rebuilt qualified binaries.
Exact next action:from usual validated elevated parent,run the unchanged
`start_return_image_session.ps1 -TexturedShip` command;observe extra ship edges
and texture detail,follow cues,and exit normally at two-beep request.
