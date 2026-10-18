# REMIX-TEXTURE-CONTROL-001 — offline image direction / emission control

2026-10-18;diagnostic only,no SFC/gameplay/hook/client modification.
Question:does pinned Remix SDK/DDS sample a known asymmetric image at the supplied
UVs,and how does whole-primary emission change the same fixed light/geometry?
It cannot by itself establish native SFC BMP row origin or face selection.

Tools:pinned Remix1.5.2/SDK0.6.4,VS2026Community18.7.3 x64 /std:c++20 /W4 /WX,
Python3.12.14/Pillow/numpy. Same process-local NRC/DLSS/RR off ENV as return fixtures.
Sources `tools/remix_runtime/texture_orientation_probe.cpp` and
`tools/remix_runtime/run_texture_orientation_probe.py`.
No elevated-parent gameplay needed;scoped GPU execution access only,no security/UAC
changes. Build using vcvars64.bat then cl source with pinned deps/include,
/Fe:artifacts/remix-runtime/live-return-bin/texture_orientation_probe.exe,
/link user32.lib. Never build over production host or accepted client.

Launch bundled Python `tools/remix_runtime/run_texture_orientation_probe.py`.
It creates unique UTC `artifacts/remix-runtime/runs/*-texture-control` workdir.
64-square lossless RGBA DDS has four asymmetrically labelled colour quadrants;
fixed quad with known UVs at z6,identity transform and camera basis.32frames
emissionOFF then32frames emissionON,same albedo/light. Two GPU fence-completed
256-square readbacks total524288B;two lossless review PNGs,one input DDS,
bounded logs/manifest/results. No continuous image dumps,no multi-GB mechanism.
Runner enforces60s/8MiB total;native GPU waits capped5s. Expected <2MiB output.
No wall-clock/manual triggers. On failure terminate only owned probe;retain partial
results. Native resources destroyed then SDK Shutdown;known SDK40 tracked separately.

Analyze four interior screen sample patches versus red/green/blue/yellow input.
Full-frame colour means support relative emitted-light diagnosis,not an absolute
colour-parity claim or physical native-light strength. Inspect camera screen axis
and texture convention together before interpreting orientation. No blanket asset
flip or production material correction is authorized by this test alone.
Cleanup leaves no installed files/mappings/hooks;preserve versionable evidence
summary and archive useful workdir;raw assets untouched. No staging/commit.
