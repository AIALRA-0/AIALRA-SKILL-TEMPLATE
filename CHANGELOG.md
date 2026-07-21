# Changelog

## [0.3.0] - 2026-07-21

### Changed

- Grouped every `workflow.yaml` top-level field under `definition`, `execution`, or `learning`.
- Split execution settings into `limits`, `graph`, and `completion`, and learning settings into `compaction`.
- Upgraded the Workflow IR to version 2 and reject unclassified or unknown configuration fields.

## [0.2.0] - 2026-07-20

### Changed

- Replaced the multi-Skill catalog/profile architecture with one universal independent-repository template.
- Replaced document-driven generation with a graph IR and deterministic state-machine Runner.
- Added core SHA-256 locking, structured executor contracts, confirmation gates, retry/fallback control, and final validation.
- Added sanitized learning ledger, lossless archival compaction, bounded advisory rules, and proposal-only promotion.

### Removed

- Catalog control plane, shared eval directories, and four profile templates.

## [0.1.0] - 2026-07-20

### Added

- Initial catalog-driven multi-Skill framework, retained in Git tag `v0.1.0` for recovery.
