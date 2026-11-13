## ADDED Requirements

### Requirement: Report graphics mismatches in read-only preflight

For an intact package beside a supported SFC executable, launcher preflight
SHALL report all detected graphics profile mismatches and leave game and
package files unchanged.

#### Scenario: Multiple graphics inputs fail qualification

- **WHEN** preflight finds a missing required graphics DLL, a mismatched
  wrapper, incompatible resolution settings or an unrecognized proxy
- **THEN** it identifies the affected files and exits with failure without
  starting SFC or changing the game copy

#### Scenario: The qualified game copy passes

- **WHEN** preflight finds the qualified graphics stack and passes the native
  launch check
- **THEN** it returns the existing preflight success receipt without starting SFC
