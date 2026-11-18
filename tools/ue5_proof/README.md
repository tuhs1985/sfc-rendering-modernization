# Packaged UE captured-scene proof

Development-only preparation and build tools. The packaged executable does not
require the editor, Python, D3D9 or Remix. This is an offline consumer of SFC
capture packets, not a converter reading `.mod` files.

Use the existing independent reader to validate provenance and original images.
`prepare.py <replay directory> <game copy> <new artifacts/ue5-proof directory>`
stages authored project files and local input. It never modifies the capture or
game copy. The source positions, corner UVs and images remain unchanged.

Build the staged project with `build.ps1 -Engine <installed UE_5.8 directory>
-ProofRoot <prepared directory>`. The pinned engine is 5.8.4, changelist 58902052.
Development prerequisites include VS C++ tools, Windows SDK and .NET Framework
4.8 SDK/targeting pack. UE uses its bundled .NET SDK. Build workers are bounded
for this workstation. First shader cooking takes longer than an incremental build.

Run the generated `SFC-UE5-Proof.cmd`. Close its window normally. `-SFCExit`
exits after the single validation readback. The command line accepts explicit
`-SFCScene=<checked input>` and `-SFCOutput=<output folder>` for another fixture.
There is one BMP and JSON receipt per invocation, no continuous image recording.

The runtime expands original corners into procedural mesh sections and reads
back the constructed arrays. Captured model and view transforms use column
vectors. The adapter maps native camera space to UE forward/right/up as
`(-z,x,y)` and converts OpenGL depth to UE reversed depth. Original UVs use
original top-row-first BGRA images with nearest filtering. Diagnostic unlit
materials deliberately omit lighting, emission and enhancement generation.

`verify.py <scene.json> <ship00000.bmp> <existing output directory>` independently
rasterizes original source arrays with captured matrices, perspective-correct
UVs and a depth buffer. It writes `reference.png`, `difference.png` and a pixel
comparison receipt. Interior source pixels exclude triangle edges. Tiny distant
fixtures do not provide enough samples to establish texture correctness.

Game assets, staged inputs, cooked materials, packages and images stay under
ignored `artifacts/ue5-proof`. Do not distribute captured game content. This
proof does not qualify live IPC, UE GPU return, replacement, lighting, damage,
destruction motion or the final reusable DLL SDK.
