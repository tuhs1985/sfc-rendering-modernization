## ADDED Requirements

### Requirement: Explicit offline evidence maintenance
Development evidence maintenance SHALL default to read-only review and SHALL
require explicit application and an audit ledger before sharing file storage.

#### Scenario: Inventory older completed runs
- **WHEN** an operator inventories evidence before a specified date
- **THEN** only finalized successful older runs and recognized image payloads
  are considered, excluding already shared files and unrelated data

### Requirement: Preserve evidence content and boundaries
Sharing SHALL preserve reviewed file paths and bytes, reject changed or external
inputs, and use atomic replacement that leaves original data intact on failure.
Successful shared groups SHALL be read-only and repeated application SHALL not
create more copies.

#### Scenario: Changed input after inventory
- **WHEN** a reviewed image no longer has its expected size and SHA-256
- **THEN** that group is refused before any of its paths is replaced

#### Scenario: Repeated application
- **WHEN** the reviewed files already share their storage
- **THEN** their content remains unchanged without another replacement

### Requirement: Keep maintenance outside normal play
The tool SHALL NOT be imported or run by normal gameplay. Maintenance SHALL NOT
raise the evidence limit or change its logical-path accounting.

#### Scenario: Normal launcher verification
- **WHEN** the existing read-only launch preflight runs after maintenance
- **THEN** it validates the current application without invoking the maintenance
  tool or modifying retained user packages
