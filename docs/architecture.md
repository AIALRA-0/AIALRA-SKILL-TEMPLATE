# Runtime architecture

## One template, one protocol, one Skill per repository

The template standardizes execution semantics rather than domain headings. Each generated repository contains exactly one discoverable Skill and one independent Git history.

The domain author defines the minimum supported intent in `SKILL.md` and encodes its actual behavior as nodes in `workflow.yaml`. There is no catalog or profile selection layer.

## Workflow IR

`workflow.yaml` uses JSON-compatible YAML so the runtime has no YAML parser dependency. It is readable by YAML tools and parsed deterministically by Python's standard JSON parser.

Top-level contract:

```json
{
  "ir_version": 1,
  "skill_name": "example-skill",
  "configured": true,
  "entry_node": "normalize-input",
  "limits": {
    "max_nodes": 16,
    "total_timeout_seconds": 1800
  },
  "learning": {
    "compact_every": 32,
    "active_rule_limit": 16
  },
  "nodes": [],
  "final_output_schema": "schemas/final.schema.json",
  "final_validator": null
}
```

Every node declares:

- stable kebab-case `id`;
- input and output schemas;
- one executor;
- exact script argv or external action contract;
- side-effect class and confirmation requirement;
- timeout and retry limit;
- optional deterministic validator;
- success edge, fallback edge, and stop conditions.

Cycles across success or fallback edges are prohibited, and every node must be reachable from the entry. Repetition is represented by bounded retries, not open loops.

Text stop conditions constrain external executors and must be surfaced in every directive. A condition that can be decided mechanically belongs in an input/output schema or validator; prose is never treated as if the Runner could evaluate it deterministically.

## Runner state machine

The Runner supports these state transitions:

```text
running
  ├── script node ── validate ── next node / completed
  ├── external node ──────────── waiting-external
  ├── confirmed side effect ──── waiting-confirmation
  ├── user action required ───── waiting-user
  ├── retryable failure ──────── running, bounded by max_retries
  ├── fallback ───────────────── running at declared fallback node
  └── fatal or exhausted ─────── failed
```

Runtime state and node files live under ignored `.runtime/`. The Runner never stores complete subprocess logs in learning data. Script commands are argv arrays executed with `shell=false`.

## External executors

For MCP, browser DOM, Computer Use, and reasoning nodes, Runner emits a directive containing the executor, action, current input, output schema, side-effect class, confirmation state, timeout, stop conditions, and advisory rules. The agent may execute only this directive and must submit structured JSON.

MCP stays a native executor. Wrapping it in shell scripts would add failure points without improving determinism.

## Core lock

`.core-lock.json` hashes:

- `AGENTS.md`, `VERSION`, and `SECURITY.md`;
- enforcement configuration and CI workflow;
- root validation/security scripts;
- every file inside the runtime Skill.

The Runner verifies this manifest before starting or resuming work. Learning, tests, README files, and ignored runtime state are not core. A core edit requires review, tests, a version decision, and a new lock.

The lock detects drift; it is not an authorization or authenticity boundary because a process with local write access can regenerate it. Use reviewed commits, protected branches, signed releases where appropriate, and pinned CI to establish provenance. Likewise, a Runner confirmation pause records the protocol gate, while the host and agent remain responsible for obtaining the user's actual confirmation before invoking `approve`.

## Draft safety

Generated repositories contain a structurally valid but non-executable workflow with `configured=false`. This prevents a generic reasoning node from pretending to be a finished domain Skill. Only domain design and tests may change it to `true`.
