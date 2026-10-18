# Remix depth/coverage — experimentally qualified standalone contract

Authority:approved in-game return-path investigation,not final renderer design or
milestone completion. See REMIX-COVERAGE-001 and Run16. Keep returned-image v2
wire unchanged;it is NOT this multi-output replacement contract.

## Current native-depth conversion — qualified 2026-10-17

[Run20](../runs/2026-10-17-codex-native-depth-conversion.md) replays fresh Run19
FCA poses through ACTUAL pinned runtime with SDKnear=b/a≈1.99993349,samefar.
All3maskIoU1.0,median nativeZerrors1.65e-7/1.65e-7/4.32e-7. Uncorrected near~1
control keeps maskIoU1.0 but error.0123745,as expected. Native game depth follows
native screenZ;old historical SDKnear used halfZ+.5. Historical experiment remains
valid for its declared reference,not a native-game-depth replacement convention.
Run19 direct native8MSAA comparison is separate from this256square replay;
no exact same-pixel/visibility claim. No game-side suppression or multi-output
frame-matched wire yet. SDK40/SFC54/67cleanup warnings remain unresolved.

## Observed outputs (pinned runtime1.5.2 / SDK0.6.4)

|Output|Native allocation/import|Interpretation qualified here|
|---|---|---|
|Color|D3D11 BGRA8 shared ->D3D9 A8R8G8B8|Genuine SDK color;diagnostic material/light only|
|Depth|D3D11 R32_FLOAT shared ->D3D9 R32F|Projected D3D normalized Z,not view/ray distance,for tested cameras|
|Picking|D3D11 R32_FLOAT shared ->D3D9 R32F|RAW uint32 bits preserved,NOT numeric float IDs|
|Local decode target|R32_UINT,private|10_1 ps_4_1 asuint(Texture2D<float>.Load) recovers exact tested IDs|

All256square,one mip/layer,non-MSAA. Three SDK output allocations plus local
decoder target<=1MiB. All18produced images compared byte-for-byte between
Remix readback and native D3D11 CopyResource/readback. All6picking images matched
GPU shader bit decode. No CPU-uploaded output image masquerades as returned GPU
output. These are standalone same-process/same-user shared resources,NOT yet
qualified multi-output x64-host→x86-SFC transport. Legacy KMT handles are held by
native texture leases;never CloseHandle them or cast a VkImage into HANDLE.

Output-copy API SUCCESS alone insufficient:initial picking call only enables
retention. Prime before scene production,render16frames/window,copy all three
outputs from one runtime frame,EVENT completion<=5s,then consume. Test background
is explicitly0for picking and-1234for depth. Every background pixel checked.
Never derive coverage from black pixels or final-color alpha. IDs7/11/13/23/29
are controlled test identifiers,NOT SFC native pointers or owner epochs. No
arbitrary32bit-ID/NaN bit-pattern claim from this small validated set.

## Camera/depth conversion observed

Known control planes at viewZ6,8,9 with near.1/far100 match
`z = far/(far-near) - near*far/((far-near)*viewZ)` within2e-5;
viewZ/ray-distance hypotheses rejected by measured errors. Smaller is nearer
for these ordinary projections;do not generalize to reversed/infinite projections.

Historical SFC replay uses validated native17word affine interpretation (not
blind standard-matrix reinterpretation). Native inverse view supplies camera
position,right=column0,up=column1,forward=-column2 for SDK LH parameterization.
FOVy=2atan(1/P11),aspect=P11/P00;near/far from existing validated conversion.
Reject off-axis/native unsupported camera math. Original model transform/units
retained,no centering/fit in replay. Fitting only in independent geometry control.

Asset captured on source frame4,revision2;model/camera observation frame5,owner
epoch2,matched model/source/revision within SAME historical run. This is reusable
rigid-asset association,not an assertion of same-frame geometry snapshot or
support for unobserved in-place deformation. Original references/packet unchanged.

At256square normalized native viewport,independent CPU rasterization of native
composed matrix and Remix ID29 mask overlap exactly478/478pixels. Median depth
difference1.8007762153660067e-7 after mapping native clipZ to `.5*z+.5`.
This confirms replay math against native composition,NOT an actual same-frame
SFC GPU-depth comparison. Run15 depth capture lacks those semantic fields.

## Before original-ship suppression

Still need one contemporaneous record tying session,owner epoch,asset revision,
selected LOD/model/source,model/camera/projection/viewport and native depth to a
specific displayed frame. Qualify depth convention with that GPU evidence;
do not combine Run15 pixels and historical frame5 and call it synchronized.
Original async30Hz preview transport not assumed sufficient. Future wire must
carry provenance+validity and native output ownership/fences,not only3handles.

No original textured material,alpha-test/translucency,culling/shield/weapon/UI
coverage qualified by default opaque,double-sided geometry.58group assignments
are retained in provenance but diagnostic SDK mesh uses one default material.
Replay color is dark under the deliberately unchanged control light;no appearance
tuning or normal-texture fidelity claimed. No original ship hidden or replaced.

Runtime shutdown returns API0/process0 after queued retirement fence,but existing
`[40] common device objects were not disposed of.` warning persists. Separate
SFC/ReShade warning67 also unresolved. Do not label overall cleanup warning-free.
