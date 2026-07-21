# Version and maintenance policy

Each generated Skill repository owns its own commits, tags, releases, rollback history, tests, and learning records.

Treat the Skill's public contract as its supported intent, excluded adjacent intents, required inputs, observable outputs, executor permissions, side effects, confirmation gates, fallback behavior, and validation guarantees.

- PATCH: instruction or implementation fixes that preserve this contract.
- MINOR: backward-compatible new node, optional capability, or stronger validation.
- MAJOR: changed trigger boundary, required input/output, permissions, side effects, graph order, or migration requirement.

Learning-only commits do not automatically change the core version. Promoting learning into stable core requires an appropriate version bump.

Recommended lifecycle:

1. Draft: `configured=false`; structural validation only.
2. Candidate: configured graph, deterministic tests, adjacent non-trigger tests, and clean core lock.
3. Stable: repeated task evaluation, failure-path tests, real low-risk use, version tag, and rollback point.
4. Deprecated: implicit invocation disabled or replacement guidance supplied before removal.

Do not place multiple generated repositories inside this template repository. If unified discovery is later required, use a thin external registry containing repository URLs and versions only.
