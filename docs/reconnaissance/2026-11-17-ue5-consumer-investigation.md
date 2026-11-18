# UE5 consumer investigation

November 17, 2026. This is a read-only renderer feasibility review and an
offline reference run. No Unreal project, live attachment or package was built.

That describes the original investigation. The subsequent
[November 18 packaged proof](../runs/2026-11-18-codex-ue5-packaged-proof.md)
now verifies an actual UE project and package. Its measured results and next
action supersede the pending build steps below. Live attachment remains open.

## Local engine dependency

Target **Unreal Engine 5.8.4** for the initial Win64 Development proof.
Epic released 5.8.4 as a 5.8 hotfix. UE 5.8 supports the Visual Studio 2026
toolchain on this workstation. The installed patch is 5.8.4 at changelist
58902052, compatible changelist 55116800, branch `++UE5+Release-5.8`.
[Epic hotfix notes](https://forums.unrealengine.com/t/5-8-4-hotfix-released/2842775).
[Epic C++ toolchain requirements](https://dev.epicgames.com/documentation/en-us/unreal-engine/setting-up-visual-studio-development-environment-for-cplusplus-projects-in-unreal-engine?application_version=5.8).

Install one precompiled engine through Epic Games Launcher, using an external
local dependency directory such as `C:\Project\Dependencies\UE_5.8`.
Keep Windows/core components. Optional symbols, starter content and other
target-platform support are outside the first viewer proof. Check
`Engine\Build\Build.version` for major, minor, patch and changelist and verify
`Engine\Binaries\Win64\UnrealEditor.exe` and
`Engine\Build\BatchFiles\RunUAT.bat` before recording an installed pin.
Track project-authored source and setup in Git. Keep the engine, installers,
caches and generated build output local.
[Epic installation guide](https://dev.epicgames.com/documentation/en-us/unreal-engine/install-unreal-engine).
[Epic distribution terms](https://www.unrealengine.com/eula/unreal).

The official launcher bootstrap was downloaded and its Epic Games Inc.
Authenticode signature verified. Its local receipt and installer are under
`artifacts/ue5-bootstrap/`. Windows refused the unattended install under the
non-elevated token. The interactive installation and Epic account sign-in
are the next steps before the engine download.

## Starting input

The engine is installed at `C:\Project\Dependencies\UE_5.8`. The editor,
command-line editor, UAT and build scripts and DynamicMeshComponent headers
are present. `Build.bat -Help -NoMutex` completed with exit 0 using the
engine's bundled .NET 10.0 SDK. The restricted process could not open the
batch-file lock under its redirected temporary directory. The same check
passed from the desktop execution environment. The local engine hashes and
version receipt are in `artifacts/ue5-bootstrap/engine-receipt.json`.
Project compilation and a packaged renderer proof remain to be performed.

Use the validated SFC-07 scene view upstream of D3D9. The first fixture is the
captured Klingon Bird-of-Prey. It has 452 triangles, 240 referenced positions,
1,356 corners and five primary image bindings. The consumer can recover the
same source geometry, original images, pose, camera and 1720×1020 tactical
viewport at offset (200, 30). A separate CPU consumer compared the captured
model, view and projection against the independent native composed matrix
read from the checked source row. Maximum XY error over all referenced ship
positions was 0.000026 pixel. This is a projection check, with rasterization
and depth conventions left to the renderer proof.

The local reference under `artifacts/effect-probe/sfc07-wrap-20261117/`
contains the inspected scene arrays, topology census and five ship screen
landmarks. Keep the captures for the Bird-of-Prey and F-CA fragments in their
own sessions. The historic fragment pose numbers are sample ordinals.

## Smallest packaged proof

1. Pin an installed Unreal Engine version and build a Windows Development
   package that takes the existing offline scene view and resolves its
   original images from the tester's game copy. Keep source SFC files outside
   the package. Disable the need for the editor during the check.
2. Build runtime geometry once. `UDynamicMeshComponent` with `FDynamicMesh3`
   and corner UV/normal attributes is a candidate. Submit one vertex per
   original corner at first and assign the recorded groups to material slots.
   The census found six edges with more than two incident source triangles
   in each of three F-CA pieces. Epic's dynamic mesh can reject such
   triangles when they share topology. Per-corner expansion keeps triangle
   membership intact while the adapter is qualified.
   [Epic dynamic mesh component](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/GeometryFramework/UDynamicMeshComponent).
   [Epic mesh topology behavior](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/GeometryCore/FDynamicMesh3).
3. Convert the model and camera together into Unreal's Z-up left-handed basis.
   Apply any winding and depth convention conversion only in the adapter.
   Compare screen landmarks against the native reference, including viewport
   offsets. Validate UV orientation with an asymmetric texture and compare
   group assignments and source image hashes before applying lighting.
   `USceneCaptureComponent2D` exposes a render target and custom projection
   matrix. Confirm culling and depth in the actual packaged renderer.
   [Epic coordinate system](https://dev.epicgames.com/documentation/en-us/unreal-engine/coordinate-system-and-spaces-in-unreal-engine).
   [Epic scene capture component](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Engine/USceneCaptureComponent2D).
4. Measure process start to first textured frame and steady frame times.
   Compare captures driven by two different camera/pose samples and confirm
   that the content follows the expected frame. Add the fragment topology
   case after the intact ship passes. Record the engine, features, GPU and
   driver used. No standard UE installation or editor executable was found
   at the checked locations on this workstation.

## Later GPU return

Qualify Unreal's completed colour, depth and owner coverage with real frame
identity before connecting the game receiver. Start with a standalone GPU
exchange against the existing D3D11 consumer and changing content, including
resize and disconnect. Native suppression remains gated by matching output.
Trace dgVoodoo's remaining legacy draw, target and presentation
responsibilities separately. A standalone UE frame cannot demonstrate that
the game's HUD or effects survive replacing the wrapper.
