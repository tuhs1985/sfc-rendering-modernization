# REMIX-OUTPUT-001 — standalone runtime output qualification

Status: development prerequisite, no SFC interception permitted by this probe.
Question: can pinned Remix output be copied into an actual shared D3D9 render
target and opened/consumed on native D3D11 with explicit GPU completion?

Dependency: official rtx-remix remix-1.5.2 release; dxvk-remix submodule
b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4; SDK0.6.4. Setup script
tools/remix_runtime/prepare_runtime.ps1 verifies upstream archive SHA256 and
extracts only under ignored artifacts/remix-runtime/deps. Archive231778218B,
download250MiB/180s cap; extraction2GiB/4096entry cap. No Toolkit/installed game
DLL changes. Reuse downloaded dependencies; do not mix SDK/main headers.

Static basis: pinned rtx_remix_api.cpp CopyRenderingOutput enqueues final-output
blit to D3D9Surface image; it returns success even when no source image exists.
Therefore API success alone is NOT proof of rendered pixels. Pinned
d3d9_common_texture.cpp CreatePrimaryImage exports OPAQUE_WIN32_KMT memory and
ExportImageInfo writes D3D11 texture metadata. This suggests a public shared
render-target route, not yet an interoperability claim. External-swapchain raw
VkImage/semaphores are not Win32 shared handles.

Launch: PowerShell7, tools/remix_runtime/build_output_probe.ps1 followed by
tools/remix_runtime/run_output_probe.ps1 from established host shell. Build uses
VS2026 x64 compiler and Windows SDK; no driver/install/security-policy edits.
No elevation intrinsically required; host shell execution may be needed to
access desktop/GPU outside sandbox. No SFC gameplay or UAC interaction required.

Runner -Mode sharing (default) omits rendering to isolate transfer failures.
-Mode rendering first creates an emissive green triangle through
CreateMaterial/CreateMesh/SetupCamera/DrawInstance/Present. Two fixed validation
readbacks initially at frames7/15, revised to15/31 after black output: two fixed
256square BMP snapshots (<513KiB total), green pixel counts/maxima and hashes,
different poses. A sphere light, native message pump, 20ms pacing and a visible
nonactivating256square standalone window align the SDK example's execution loop.
This diagnostic window is NOT the requested in-game returned-image proof.
Latest diagnostic uses explicit triangle indices0/1/2 rather than the vendor
example's nonindexed mesh, and bounded info-level vendor logging in rendering
mode to distinguish accepted submission from produced pixels. A black snapshot
is a failure, regardless of API return success. Destroy owned native window
before unloading runtime DLL, so a runtime-installed window procedure cannot be
called after unload; abnormal exit remains a separate failure if still observed.
Then tries sequential256x256 RGBA8/BGRA8/RGBA16F shared textures
and native D3D11 import. If all fail, tests native D3D11-to-D3D11 sharing as a
control and imports a native BGRA8 shared resource into Remix as the bounded
reverse-direction alternative. Only one exported candidate is retained at once.
D3D9 EVENT query completion fences producer
writes; D3D11 EVENT query fences consumption before reuse. Up to32 rendered
frames; small fixed readbacks only for offline pixel verification, NEVER an
image-return implementation or continuous screenshot fallback. Failure of share
creation/import is preserved as a specific prerequisite failure. Cross-process
handoff, ACLs, sequence handling and crash recovery still require separate tests
before this can qualify the full output gate.

Runner timeout120s, combined stdout/stderr/vendor logs32MiB hard stop/warn16MiB;
checks every250ms; only owned process killed on cap/timeout. Runtime environment
DXVK_LOG_LEVEL=error, DXVK_LOG_PATH=run directory; process-local preset4 and
RTX_INTEGRATE_INDIRECT_MODE=0 retain NRC-off diagnostic policy. No system config.
After a device-loss failure during the fifth attempted DrawInstance with the
default DLSS/RR settings, subsequent probes explicitly request
DXVK_UPSCALER_TYPE=0, DXVK_RAY_RECONSTRUCTION=False, RTX_DLSS_PRESET=0 (pinned
rtx_options.h declarations). This is a bounded configuration isolation, not a
confirmed cause/fix. Do not repeatedly rerun device-loss without new evidence.
Pinned RtxContext::injectRTX explicitly skips ray tracing while asynchronous
shader compilation is active. Initial32frame black-output tests therefore do
not distinguish failed submission from shader warmup. The next configuration
sets RTX_ENABLE_ASYNC_COMPILATION=False (rtx_options.h:386), allowing required
compilation to block only the standalone host under the same120s watchdog.
This is not a game-thread policy. Do not infer actual pixels from timing alone.
Subsequent source review of pinned remix.h default constructor found our C
material had alphaTestType=0 with useDrawCallAlphaState=false, rather than the
constructor's7/ALWAYS. Correct that field before interpreting black pixels as a
runtime limitation. Restore only the probe-owned window's original procedure
before SDK Shutdown, then destroy it before DLL unload; no SFC window subclass
exists in this probe. Keep earlier failed output/shutdown results as evidence.

Vendor control: build script also compiles pinned, UNMODIFIED
remixapi_example_c.c as C11/x64. run_vendor_example.ps1 runs it with32frame
argument, same120s/32MiB bounds and diagnostic environment. It creates a run-local
hardlink to the verified runtime DLL (not modified; exclude this immutable
190838384B alias from log/output budget and evidence ZIP). Dependencies are
found through process-local PATH. Vendor window is1600x900 and may appear; not
an in-game compositor. Process success alone does not prove correct pixels.
No source changes to the vendor example; exact SHA recorded. Purpose is to
distinguish project-host defects from SDK/runtime/driver compatibility failures.
After vendor control exits0, the next project-host control uses the sample's
default material (null material handle) with the existing sphere light. Explicit
material registration is deferred, not declared unsupported; this isolates it
from output transfer and keeps the original256square device unchanged.

Cross-process qualification: -Mode crossprocess; contract
../remix-output-contract.md. Separate owned child allocates D3D11 shared texture,
host imports it, SDK copies genuine final output, GPU completion precedes IPC
publication, child verifies exact output hash and ACKs before reuse. No CPU image
transport. Two sequences; child startup/ACK5s, overall110s, owned kill-on-close
job. Native output_contract_tests verifies immutable header/counts/sequence,
stale ACK/busy slot/disconnect rejection and actual current-user-only mapping
DACL. No GPU loaded by those tests.

Fault runs -Mode crossprocess-slow delays owned consumer6s against host5s ACK
deadline; -Mode crossprocess-exit exits owned child during first published
transfer. Expected: probe exits nonzero with disconnected/timeout error, SDK
teardown returns, owned child terminates; NOT a successful-rendering claim.
Same120s/32MiB envelope, no SFC. Run each once, then re-run positive crossprocess
to establish recovery/new unique session rather than accepting a stale ACK.

-Mode crossprocess-x86 runs the same actual output proof into a separately
compiled32bit D3D11 consumer, matching SFC's bitness. output_consumer.cpp never
loads the64bit Remix DLL. Same128B wire/4KiB mapping, two ACKed frames, limits,
GPU completion and pixel/orientation checks; no game interception. Only the
explicit sibling output_consumer_x86.exe may replace the self-child executable.
Expected output artifacts/remix-runtime/runs/<UTC-ID>, normally<1MiB textual
evidence. Vendor tools can grow large logs/crash dumps; runner bounds monitored
run-directory logs, not an OS disk quota. No verbose GPU captures enabled.

Cleanup: process owns device/queries/textures and releases resources before SDK
Shutdown; runner terminates only its owned probe on failure. Keep dependency
cache and concise logs for analysis; no game/proxy cleanup needed. No daemon,
shared mapping or game hook installed. Hash original client before/after later
game probes; this probe never opens it for writing.

Success of this preliminary import test is not RETURN PATH DEMONSTRATED. The
full first gate needs actual deterministic Remix pixels, reusable transfer,
cross-process current-user-only ownership/synchronization and failure tests.
