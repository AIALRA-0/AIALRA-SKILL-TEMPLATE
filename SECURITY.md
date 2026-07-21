# Security policy

## Never commit

- API keys, passwords, access or refresh tokens, OAuth client secrets, private keys, seed phrases, one-time codes, session IDs, cookies, or authorization headers.
- Browser profiles, cookie databases, password stores, logged-in session exports, CAPTCHA artifacts, or saved authentication state.
- Real customer records, private messages, addresses, phone numbers, personal email addresses, order histories, payment data, or unredacted screenshots.
- `.env` files, cloud credential files, production configuration, raw logs, or eval outputs copied from a private environment.

Use environment-variable names and non-secret placeholders only, for example `${SERVICE_TOKEN}` and `https://api.example.invalid`.

## Preventive controls

1. Keep the remote repository private until a disclosure review is complete.
2. Install local hooks with `pre-commit install`.
3. Run `python3 scripts/check_secrets.py` before every push.
4. Install Gitleaks and run `gitleaks git --redact` to scan Git history.
5. Enable the host's secret scanning and push protection. Local checks do not replace server-side protection.
6. Give CI `contents: read` only unless a workflow has a documented reason for more access.

## If a secret is committed

1. Stop sharing or pushing the branch.
2. Revoke or rotate the credential immediately. Removing the text does not make an exposed credential safe.
3. Identify every branch, tag, fork, artifact, log, cache, and pull request that may contain it.
4. Remove it from the current tree and rewrite history with an appropriate reviewed procedure.
5. Force-push only after coordinating with all repository users; history rewriting is disruptive.
6. Re-scan the full history and invalidate old clones where practical.
7. Record the incident without copying the secret into an issue, chat, or commit message.

Do not add a scanner allowlist merely to make CI pass. A false positive must use an obviously non-secret placeholder and a narrowly scoped explanation.

## Reporting

Report a suspected leak privately to the repository owner or security contact configured for the eventual remote repository. Do not open a public issue containing sensitive values.
