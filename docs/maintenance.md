# Maintenance and release policy

## Maturity states

- `draft`: design is changing; at least 3 positive and 3 near-miss negative trigger prompts.
- `candidate`: workflow is complete; at least 8 positive and 8 negative prompts plus task evals.
- `stable`: candidate criteria, documented baseline comparison, successful real use, and named owner.
- `deprecated`: remains discoverable only when migration guidance is required; implicit invocation should normally be disabled.

## Per-Skill SemVer

Treat the Skill's observable contract as its public API:

- `PATCH`: wording, examples, or validation fixes that preserve triggers, inputs, outputs, and safety behavior.
- `MINOR`: backward-compatible capability, new optional resource, broader intentional trigger, or stronger validation.
- `MAJOR`: removed capability, changed required input/output, incompatible trigger boundary, changed side-effect policy, or a migration requiring user action.

Pre-1.0 versions may move faster, but every behavior change still needs a deliberate bump. Root framework releases use the same rules independently of Skill versions.

## Evaluation ladder

1. Static: frontmatter, naming, file references, UI metadata, profile fields, generated drift, and secret scan.
2. Unit: generator, validator, and bundled deterministic scripts.
3. Routing: positive and near-miss negative prompts, repeated when possible; tune on the train split and choose changes using the validation split.
4. Task quality: compare with-Skill results against no-Skill or the previous version using observable assertions and evidence.
5. Canary: use the candidate on real low-risk tasks and add every correction to `gotchas`, profile rules, or eval cases.

Record timing and token use when the environment exposes them. A Skill that adds substantial cost without a meaningful quality delta should be simplified or removed.

The catalog `evaluation` object is the release receipt. Keep `baseline`, `last_run`, `routing_runs_per_query`, and `summary` current. `candidate` and `stable` entries may not use `baseline: not-run`.

## Review cadence

- Volatile research and third-party integration Skills: normally 30–90 days.
- Stable artifact or repository workflow Skills: normally 90–180 days.
- Review immediately after an API change, repeated failure, security incident, tool deprecation, or user correction.

The catalog's `last_reviewed` date records a substantive review, not a mechanical reformat.

## Retirement

Before removing a Skill, mark it deprecated, disable implicit invocation when appropriate, name its replacement, and keep a migration window. Remove it in a later major release after evals and repository rules no longer depend on it.
