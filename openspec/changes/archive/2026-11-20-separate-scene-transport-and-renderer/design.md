# Design

Use src/transport for the existing scene receiver, channels, catalog, startup tickets, light/input data, rebind messages and worker lifecycle. Keep content identity in src/assets. Preserve shared-memory layouts, resource ownership, acknowledgement order and worker shutdown. Calibration and preview comparisons remain development tools. Verify actual mapping writes, acknowledgements and closure in the intermediate package.

Use src/rendering for the existing Relay hierarchy and verified backend selection. Preserve pins, configuration, process lifetime and fallback. Move detailed renderer reports and experimental runtime acquisition to development tools. Keep legacy entry points and native executable/build contracts. Validate the final package with the installed CPU pipeline, standalone GPU output and cancellation, native fixtures and read-only preflight. Prepare the gameplay copy and record the evidence.
