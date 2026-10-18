# BLENDER-UV-COMPARE-001 — offline texture-origin comparison

Question: does the installed Blender OBJ/image path interpret the same raw UVs
differently from the pinned Remix SDK/DDS path? No SFC launch or hooks.

Tool: installed Blender 5.0 (exact patch recorded in result), Python script
`tools/remix_runtime/compare_blender_uv.py`. No build or extra privilege required.
Launch Blender with `--background --factory-startup --threads 2 --python` script,
then `-- OUTPUT_DIRECTORY EXISTING_OBJ`. Never save startup settings or source OBJ.
Output must be a new ignored artifacts/remix-runtime/runs directory.

Starts immediately; stops after importer readback and one 128x128 CPU render.
Caller enforces 90 seconds and 8 MiB directory cap, polling every 100 ms. On limit,
terminate only that owned Blender process. No repeated captures or screenshots.
Expected <4 MiB: imported per-corner material/position/UV JSON, asymmetric input
PNG, one rendered PNG, result JSON and stdout log. Multi-GB generation is not
expected under these fixed bounds. No rendering-thread code or game files involved.

Analysis: independently decode saved asymmetric PNG and sample rendered four
quadrants; compare against retained fenced Remix four-corner control. Read back
actual imported OBJ triangle corners/materials against source OBJ, tolerating
float32 importer rounding but not UV transforms or changed group associations.
This qualifies the two adapters' coordinate conventions, not native SFC visual
parity or a production correction. Existing Remix control's shutdown failure
remains PARTIAL even if its completed GPU images can answer the corner question.

Cleanup: process exits; no installed assets/configuration changed. Retain useful
small evidence and archive after adjudication; remove only owned failed temporary
output if no longer useful. No game-directory deployment to undo.
