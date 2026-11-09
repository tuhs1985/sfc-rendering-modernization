# Proposal

## Why

The portable launcher's application source shares a directory with development-only release tools. Separating them makes package ownership clear without changing gameplay or the rendering pipeline.

## What Changes

- Move the five launcher inputs into `src/launcher` and update their consumers together.
- Keep building, packaging, dependency inventories and standalone qualification under `tools/release`.
- Mirror the new launcher location under installed `code/src/launcher`; rebuild the native entry point and qualify the installed layout.
- Preserve the existing private alpha checkout, appearance, recovery behavior and default recording policy.

## Capabilities

### New Capabilities

None. Pure source/package-layout refactor; `skip_specs: true`.

### Modified Capabilities

None. Existing release behavior and requirements remain unchanged.

## Impact

Launcher source, isolated Python import paths, release allowlist, native build, staging and ZIP tooling, focused tests and current documentation. No vendor updates, renderer edits, external-folder migration, commits or publication.
