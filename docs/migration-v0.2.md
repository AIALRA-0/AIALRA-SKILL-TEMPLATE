# Migration from v0.1

Version 0.1 used a shared catalog, four profiles, shared eval directories, and generated multiple repo-local Skills. Tag `v0.1.0` retains that design.

Version 0.2 intentionally breaks that architecture:

- one universal repository template replaces all profiles;
- one Skill receives one independent Git repository;
- `workflow.yaml` becomes the execution source of truth;
- Runner replaces agent-selected sequencing;
- `.core-lock.json` freezes stable behavior;
- learning moves into each Skill repository;
- catalog metadata is removed;
- growth occurs through advisory events and reviewed promotion rather than direct core edits.

To migrate a v0.1 Skill:

1. Generate a new independent repository with the same Skill name and routing description.
2. Convert the old procedural sections into explicit workflow nodes.
3. Convert fixed operations into scripts and schemas.
4. Convert each safety rule into side-effect, confirmation, stop, validator, or fallback fields.
5. Move detailed references only when Runner-directed reasoning needs them.
6. Add regression tests for the old Skill's successful and failed cases.
7. Set `configured=true`, freeze core, and tag the independent repository.

Do not copy the old catalog or shared eval control plane into the new repository.
