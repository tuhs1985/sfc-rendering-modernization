# Proposal

## Why
The accepted pipeline still keeps production geometry/image/material preparation among development proof tools, with a few capture-review and comparison functions in shared modules. Establish application ownership without changing appearance, loading order or scheduling.

## What Changes
Move nine preparation helpers into src/assets and extract neutral mesh decoding there. Put capture-review classes, snapshot selection, break-capture analysis, streaming experiments and test-only source/upload comparisons into tools/asset_diagnostics. Preserve legacy development imports and normal package boundaries. After implementation, document renderer/transfer ownership and the smallest next separation; do not redesign those systems.

## Capabilities
No new rendering behavior or spec changes; skip_specs. Keep worker/cache limits, fallback, geometry, original images, material rules and timing unchanged. Startup-delay investigation stays parked.

## Impact
Asset helpers and compatibility entries, shared live scene decoding exports, launcher/coordinator search paths, explicit package list, qualification inventories and tests. Prepare a distinct gameplay checkout; no automatic game launch, commit, push, asset authoring or renderer feature.
