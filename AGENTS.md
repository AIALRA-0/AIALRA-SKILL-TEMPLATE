# Skill library rules

## Mandatory workflow

- Treat `catalog/<skill-name>.json` as the source of truth for generated skill instructions.
- Do not hand-create or directly edit `.agents/skills/*/SKILL.md` or `agents/openai.yaml`.
- Create or update skills with `python3 scripts/new_skill.py --spec <path> [--update]`.
- Run `python3 scripts/validate_repo.py`, `python3 -m unittest discover -s tests -v`, and `python3 scripts/check_secrets.py` after framework or skill changes.
- Keep each skill on exactly one primary profile. Split a skill when it needs separate trigger contracts or unrelated outputs.

## Skill content

- Put only `name` and `description` in Codex `SKILL.md` frontmatter.
- Keep `SKILL.md` under 500 lines and make every linked reference directly reachable from it.
- Keep repository documentation, version history, ownership, and eval data outside runtime skill folders.
- Add scripts only for deterministic repeated mechanics, and test every added script.
- Use imperative instructions with explicit inputs, outputs, validation, failure handling, and guardrails.
- Add corrections learned from real failures to the catalog `gotchas` list or the narrowest relevant reference.

## Security

- Never commit credentials, API keys, cookies, session files, browser profiles, private keys, real customer data, or unredacted personal information.
- Use placeholders such as `${SERVICE_TOKEN}` in examples. Do not use realistic-looking fake tokens.
- Do not weaken secret scanning or add an allowlist without a written explanation in the pull request.
- If a secret is found, stop, rotate or revoke it, then clean Git history following `SECURITY.md`.

## Review guidelines

- Reject broad descriptions that match adjacent tasks without a clear boundary.
- Reject stable releases without near-miss negative trigger cases and evidence-backed eval results.
- Reject generated-file drift: catalog, `SKILL.md`, UI metadata, declared resources, and eval files must agree.
- Treat changes to authentication, write actions, destructive steps, privacy boundaries, or fallback behavior as at least a minor version change and require focused review.
