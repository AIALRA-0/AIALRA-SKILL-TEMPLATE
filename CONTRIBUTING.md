# Contributing

## Change flow

1. Create or update a design spec in `catalog/` or `drafts/`.
2. Generate the runtime Skill with `scripts/new_skill.py`.
3. Add only the references, scripts, or assets declared by the spec.
4. Add or revise trigger and task eval cases.
5. Run repository validation, tests, and secret scanning.
6. Update the per-Skill version and root `CHANGELOG.md` when behavior changes.

## Review evidence

A Skill pull request should state:

- the user intents it adds or changes;
- at least one near-miss task that must not trigger it;
- baseline versus revised eval results;
- security or external-side-effect changes;
- whether resources or dependencies changed;
- the proposed SemVer bump.

Draft Skills may begin with three positive and three negative trigger cases. Candidate and stable Skills require at least eight of each, split between tuning and validation sets.

## Generated files

`SKILL.md`, `agents/openai.yaml`, and the two JSON eval indexes are generated. Edit the catalog entry instead. A validation failure showing generated drift means regeneration is required.
