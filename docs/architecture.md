# Architecture

## Two planes

The runtime plane is `.agents/skills/`. Codex discovers metadata there and loads full instructions only after a Skill is selected. Runtime files therefore optimize for precise routing, small context cost, and reliable execution.

The control plane is `catalog/`, `evals/`, `templates/`, `schemas/`, and `scripts/`. It optimizes for ownership, review, reproducibility, versioning, and evidence. Control-plane material must not be copied into `SKILL.md` unless every invocation needs it.

```text
catalog spec
    │
    ├── profile-specific template
    │       └── .agents/skills/<name>/SKILL.md
    │
    ├── UI contract
    │       └── .agents/skills/<name>/agents/openai.yaml
    │
    └── eval contract
            └── evals/<name>/*.json
```

## Why there is no generic profile

A universal template tends to produce the same headings with domain nouns substituted. This framework instead requires one primary failure model:

- `research`: stale, indirect, conflicting, or unverifiable evidence.
- `tool-integration`: authentication, capability mismatch, unsafe side effects, or tool failure.
- `artifact-production`: bad input inspection, malformed output, or missing render/run verification.
- `operational-workflow`: skipped prerequisites, unsafe sequencing, no rollback, or an ambiguous completion state.

Each profile changes mandatory fields and generated instructions. If two failure models are equally dominant and form independent workflows, split the Skill.

## Structured design contract

Every catalog spec records:

- routing contract: description, positive prompts, and near-miss negative prompts;
- task contract: goal, inputs, outputs, and explicit non-goals;
- operational contract: workflow, guardrails, gotchas, and verification;
- profile contract: mandatory domain-specific failure controls;
- resource contract: every reference, script, asset, and MCP dependency;
- maintenance contract: owner, maturity, SemVer, review cadence, and last review date.

Generated-file equality is checked in CI. This makes catalog changes reviewable and prevents a Skill from silently drifting away from its tested design.

## Degrees of freedom

- Use prose and heuristics where context determines the right answer.
- Use parameterized scripts where a preferred repeatable method exists.
- Use fixed commands and validation gates for fragile or destructive operations.

Do not turn contextual judgment into a brittle script. Do not make the model rediscover the same deterministic command sequence on every run.

## Distribution boundary

Keep Skills repo-local while authoring. Package stable Skills as a plugin when users need installation, multiple Skills need one distribution unit, or the workflow includes MCP/app wiring, hooks, or marketplace metadata. Live external data and authenticated actions belong in MCP/apps or a user-controlled browser session; the Skill defines how to use them safely.
