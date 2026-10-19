# Run62 — reassess native Remix supersampling before custom implementation

Sponsor asks whether supersampling is already built in and therefore primarily
configuration. Read-only assessment;no implementation/config changes authorized.
Date2026-10-19 America/New_York. HEAD357bc70,prior changes remain unstaged.
Fuel Guard attached existing hook;no daemon/helper/game/GPU probe started.

Reviewed local remix_quality_controls.h,quality.toml,Run58,associated pinned
rtx_options.h/rtx_context.cpp/rtx_remix_api.cpp and official pinned source:
- https://raw.githubusercontent.com/NVIDIAGameWorks/dxvk-remix/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_context.cpp
- https://raw.githubusercontent.com/NVIDIAGameWorks/dxvk-remix/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_nis.cpp

CONFIRMED static:our adapter hard-codes resolutionScale1 and only exposes AAoff
or TAA. Associated pinned context uses resolutionScale for NIS/TAA internal render
dimensions,then dispatches native reconstruction to final output. Native scale
above1/non-temporal downsampling effectiveness is NOT dynamically qualified.
With upscaler OFF,the examined context uses output-sized rendering instead of
applying resolutionScale. Therefore an SS factor alone is not proven functional.

Correction to Run58/earlier discussion:CopyRenderingOutput's nearest copy does NOT
by itself prove a custom downsampler is necessary. If Remix resolves a larger
internal image into display-sized FINAL_COLOR first,the final1:1copy is irrelevant
to supersampling quality. Prior inference was too strong. Preserve historical
claims,but do not implement custom resolve solely on that basis.

STRONG HYPOTHESIS:existing native controls may reduce the integration work.
SPECULATIVE:the pinned native NIS/TAA path supports useful higher-than-output
rendering with correct edges,coverage and depth for our bridge. Need bounded
actual-runtime test and source-path validation,not assumption from accepted keys.
DLSS Super Resolution nomenclature alone is not proof of render-high/downsample.

Exact next action IF authorized:qualify native higher internal resolution/final
resolve first using standalone deterministic output and verify coverage/depth
alignment;prefer native solution. Do not build custom downsampling preemptively.
Current AAoff/native1x,sponsor baseline,qualification receipt and runtime binaries
unchanged. No visual test executed,no new supported knob/no milestone claim.
Validation:this documentation-only correction retains existing paths/source
observations;git diff --check. No staging,commit or push.
