## Why

Repeated completed-test images, superseded build output and resolved startup
traces consume disk space. The sponsor approved sharing identical immutable
assets first, then retiring resolved traces while preserving findings.

## What Changes

- Add an explicit offline inventory and hard-link sharing tool for completed,
  successful older runs, with a dry-run default and per-file ledger.
- Retire the resolved SFC-23 raw ETLs/full-system CSV and old proof build binaries;
  preserve their focused analysis and the packaged proof.
- Record disk recovery and verify existing package hashes and read-only preflight.

## Capabilities

### New Capabilities
- development-evidence-maintenance: explicit safe sharing and review of frozen
  development evidence without runtime overhead.

### Modified Capabilities
None. The UE insertion plan remains independently 17/30.

## Impact

Development-only tools/tests and maintenance records. No renderer, material,
timing, application launch or wire changes. The 20 GB evidence allowance and
logical-path accounting remain unchanged. No automatic deletion during play.
