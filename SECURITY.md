# Security policy

The template and all generated Skill repositories prohibit committed credentials, tokens, passwords, cookies, browser profiles, session exports, private keys, addresses, order histories, personal data, private messages, or unredacted runtime artifacts.

Runtime defenses:

- JSON Schema validation at initial input, every node output, and final output.
- No shell command construction; script commands use argv with `shell=false`.
- Explicit executor and action contracts for external nodes.
- Mandatory user confirmation for write and destructive actions.
- Time, retry, node-count, fallback, and stop limits.
- SHA-256 core lock covering workflow, instructions, scripts, schemas, security enforcement, and CI.
- Learning writes only to `learning/` and cannot mutate stable core.
- Learning accepts only sanitized one-sentence events backed by controlled evidence prefixes.

`.core-lock.json` is a deterministic drift detector, not proof of authorship. Protect provenance with reviewed commits, branch protection, and signed releases when the risk warrants it. Runner confirmation states prevent accidental continuation in the protocol; the host must still ensure that `approve` is invoked only after real user confirmation.

Before pushing, run the repository scanner. CI fetches complete history and runs a checksum-pinned Gitleaks release against `--all`; also enable remote secret scanning and push protection.

If a credential is exposed, revoke or rotate it first. Removing the current file or rewriting Git history does not invalidate the leaked credential.
