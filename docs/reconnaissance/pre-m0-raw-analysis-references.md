# Pre-M0 Raw Analysis References

Generated bulk output stays outside normal Git tracking. The local evidence used
for this pass is:

| Local artifact | Purpose | Tracking policy |
|---|---|---|
| artifacts/pre-m0/raw/StarFleetOP-2.5.6.4.dumpbin-disasm.txt | Full static x86 disassembly produced by Visual Studio dumpbin /disasm; 70,181,824 bytes | ignored |
| docs/reconnaissance/data/pre-m0/analysis-summary.json | analysis counts | tracked |
| docs/reconnaissance/data/pre-m0/function-map.csv | automatic heuristic function/call/data map | tracked |
| docs/reconnaissance/data/pre-m0/landmark-function-correlations.csv | .text landmark-to-containing-function correlations | tracked |
| docs/reconnaissance/data/pre-m0/string-anchor-xrefs.csv | selected graphics/model/camera/sprite string xrefs | tracked |
| docs/reconnaissance/data/pre-m0/major-function-map.csv | lead-adjudicated major functions and confidence | tracked |

The automatic function boundaries are candidates derived from direct-call
targets and common EBP prologues. They are labeled STRONG HYPOTHESIS and should
not be confused with recovered symbols. The curated map refines only the
high-value regions using aligned boundaries, returns/NOPs, exact diagnostics,
imports, COM calls, and cross-references.

## Reproduction

The following project helpers perform read-only analysis:

- tools/recon/inspect_pe.py — PE metadata, sections, imports, and IAT entries.
- tools/recon/extract_strings.py — addressable ASCII/UTF-16 string inventory.
- tools/recon/parse_landmarks.py — normalize hash-bound SFC Editor maps and
  correlate baseline bytes with PE sections/addresses.
- tools/recon/parse_launcher_landmarks.py — extract the launcher’s compiled
  service-redirection offset templates into a separate catalog.
- tools/recon/analyze_disassembly.py — correlate disassembly, landmarks,
  imports, calls, globals, and selected string anchors.
- tools/recon/extract_disasm_ranges.py — print bounded address ranges for
  manual review without copying the full dump into reports.

No game executable, asset, reference archive, launcher configuration, or runtime
rendering stack was changed to produce these artifacts.
