# Fresh debris ordinary-D3D9/Remix replay

November 7, 2026. Working-tree changes only; no SFC launch in this increment.

## Verified

Dedicated break-origin decoding and neutral preparation use the four fresh packets from `break-20261107-050659-161275`, with their original image associations. No MOD file supplies geometry. Array read-back preserves captured positions, corners, normals, UVs and groups. All32 native camera compositions pass; worst error is0.000286pixel.

The existing ordinary-D3D9 host is rebuilt into isolated artifact directories with the pinned1.6.1 headers/runtime. Existing material binding, image/quality settings, light packet consumer and physical hull depth are reused. Two opposed white directional lights are explicitly offline fixture lighting, not recovered SFC lighting.

All four independent pieces have shaded pixels inside returned hull coverage:703,355,297,410. Evidence: `artifacts/player-replacement/break-qualification-20261107.json`. Successful cases exited normally with zero remaining owned processes. Native piece tests29pass; returned-image tests4pass; strict x64 host compilation and `git diff --check` pass. A Windows system-D3D9 control renders piece0 and passes reset/retirement/reappearance checks.

## Diagnostic finding and limitations

Early successful API receipts returned blank pixels. Restoring normal visual controls/depth handling supplied valid hull depth; explicit offline lights and replacement materials supplied three textured pieces. Piece0 remained blank with enhanced materials disabled and across two captured poses. NVIDIA's `rtx.shader.enableAsyncCompilation = False` diagnostic control produced textured piece0. The local upstream `rtx_options.h` documents that asynchronous compilation can render no scene until compilation finishes, consistent with this control. The [official option reference](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/main/RtxOptions.md) describes this control; pinned runtime behavior was exercised locally. Blocking compilation was not enabled for gameplay.

Successful fixtures used the existing opt-in24-Present startup diagnostic. A one-Present synchronous control returned output and logged API shutdown but exceeded the60-second teardown bound. The job guard removed it with zero remaining owned processes. This is an unresolved short standalone-host teardown limitation, not a demonstrated regression of the prewarmed live renderer.

Returned colour/depth use full-output coordinates; the existing receiver maps both into SFC's tactical viewport once. The960-versus1920 extent hypothesis did not explain blank colour: the Renderer already scales its viewport. Original captures/assets, normal gameplay host and user settings remain untouched.

## Next exact work

Connect independent debris identity/lifetime and piece assets to normal scene transport/cohort. Keep indexed suppression disabled until source-frame identity and matching output are qualified. Normal owner admission/suppression still supports intact ships only. Independent replays do not prove simultaneous live debris, destruction continuity or alpha acceptance. No further discovery run is needed for FCA pose/lifetime.
