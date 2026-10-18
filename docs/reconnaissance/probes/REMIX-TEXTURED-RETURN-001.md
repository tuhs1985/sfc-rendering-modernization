# REMIX-TEXTURED-RETURN-001 — original textures / full-HD buffered additive copy

Status: READY FOR SPONSOR RUNTIME TEST, 2026-10-18.
Run34 sponsor-authorized washout comparison:whole-primary emission is OFF;
primary maps remain reflected surface colour. Texture images,UVs,camera,geometry
and continuous90s schedule unchanged. Old tiny world-origin point light proved
ineffective with emissionOFF in offline testing;replaced in textured mode by one
white directional inspection light (radiance1,direction0,-sqrt(.5),-sqrt(.5),.53deg).
This is not recovered SFC lighting. Expect a less white/self-lit hull,with different
shading possible under the provisional light. Secondary
glow remains unapplied. Saucer-orientation defect deliberately untouched. Compare
the EXTRA copy,not original;report whether panel colours/detail improve or become
too dark. No need for precise timestamps or another ON/OFF proof.
Run31 corrects hidden256-square producer HWND:SDK Present resized rendering despite
full-HD shared buffers. Native-size client and post-Present swapchain checks plus
internal scale1.0 now required;offline textured silhouette IoU>=0.98. See
[correction](../../runs/2026-10-18-codex-textured-resolution-correction.md).
Same launch command/cues/bounds;original ships remain. No screenshot-tool work.
Compatibility telemetry still emits REMIX-LIVE-RETURN-001; distinguish this test
by `-TexturedShip`, triplet v4 and recorded delayed-additive display policy.

Question: does full-HD original-textured output remain visible between producer
updates without changing native SFC rendering? Not a return-path re-proof or
original-ship replacement. [Contract](../textured-additive-delivery-contract.md)
defines source-age and texture-role limitations.

## Exact preparation and launch

Pinned Remix 1.5.2 / SDK 0.6.4, ReShade 6.7.1.2133; VS2026 Community 18.7.3,
compiler 19.51.36248, PS7.6.5, Python3.12.14. Windows11 build26200,
RTX4070Ti driver617.42 frozen baseline. Process-local NRC/DLSS/RR OFF unchanged.
No Toolkit. Dependency and binary hashes: [Run30](../../runs/2026-10-18-codex-textured-hd-delivery.md).

From the already elevated validated testing parent:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\remix_runtime\start_return_image_session.ps1" -TexturedShip
```

PS5 forwards to bundled PS7. Runner builds isolated live host/addon/fixture and
existing controller; validates qualification pins and both installations before
launching only `C:\Project\SFC-Remix-Return-Test`. No global policy changes,
routine new UAC or accepted-install proxy changes. Unprivileged launch aborts
rather than opening administrative prompts. Do not combine profile switches.

## Sponsor actions and expected picture

Enter familiar two-ship skirmish. Hold the initial camera briefly. Look beside
the native ships for one extra **normally textured**, potentially brightly lit
copy, selected by first qualified owner (not necessarily player). No magenta.
The existing fixed WORLD offset puts it beside its original; later camera motion
projects that offset naturally. No additional screen-space repositioning.

At the single camera cue (~10 s), change camera gently then hold. At the movement
cue (~20 s), accelerate and turn normally. Original ships always remain visible.
Sponsor-approved routine policy (Run32):extra copy remains ON for the entire
90-second tactical window,then stops before cleanup/exit request. No scheduled
disappearance or restart. Historical ON/OFF cycling remains in legacy diagnostic
modes for specifically requested fallback tests,not routine textured observation.
Keep playing until
the **two-beep exit request**, then exit normally. No manual timestamps. Report
whether the added ship is steady/sharp and any native HUD/control/render issue.
Brief initial preparation or <=100 ms source-request-age lag is possible; this
does not promise replacement synchronization or instant loading.

## Trigger, filters, output and cleanup

Automatic tactical `tEntityShip::render` 0x004162B9 gate, selected qualified owner
only; semantic path retained, diagnostic geometry hook OFF. Existing 90 s tactical
observation; Python budget <=285 s, entire prepared workflow <=300 s.
GPU images 1920x1080; four surfaces <=128 MiB. Detailed output is bounded, not an
unlimited geometry trace: non-image evidence <=32 MiB, warn16; image output
<=128 MiB, warn64; <=256 images at <=4096x4096. No per-frame image dumps. This
profile reserves384 MiB disk allowance before starting; aggregate <=10 GB.

Session output: `artifacts/remix-runtime/runs/<UTC>-in-game`, including fresh
mesh/resources, `textures/`, `texture-manifest.json`, `live-materials.bin`, bounded
host/controller/addon logs, metadata and result. Offline sessions suffix
`-live-private`. Observed offline complete textured session ~55.5 MB, of which
46,367,290 bytes are original/derived images. No rapid multi-GB output observed
in this mode; unrestricted downstream geometry tracing remains prohibited.

Normal exit stops host/controller, restores hooks, unloads observation component,
removes only owned transient proxy/component files and checks original hashes.
Receiver/renderer failure omits extra image; SFC continues. Use runner cleanup,
not manual proxy deletion or killing unrelated processes. Preserve partial evidence
on failure. Archive useful evidence after analysis; do not delete reference assets.

Compare actual SDK sequences/source frame/age and owner/revision hashes with
display submissions and ON/OFF phases; confirm original images against installation
hashes, native response via sponsor, output bounds and cleanup/client hashes.
Do not infer exact simulation-frame or scene-depth correctness from visibility.
