# Research basis

Reviewed 2026-07-20.

OpenAI's [Build skills](https://developers.openai.com/codex/build-skills) documentation defines Skills as task-specific instructions with optional scripts and references, uses progressive disclosure, and recommends keeping each Skill focused on one job. It also documents `.agents/skills` as the repository discovery location.

The [Customization overview](https://developers.openai.com/codex/customization/overview) separates durable repository guidance, Skills, and MCP: `AGENTS.md` carries repository conventions, Skills define repeatable workflows, and MCP supplies live external capabilities. The generated template follows that split.

OpenAI's [Agents SDK maintenance case study](https://developers.openai.com/blog/skills-agents-sdk) recommends clear triggers, concrete outputs, and moving repeated deterministic mechanics into scripts while leaving contextual judgment to the model.

The [Agent Skills best-practices guide](https://agentskills.io/skill-creation/best-practices) recommends calibrating control to fragility, validation loops, fixed defaults, and learning from real execution. This template turns those recommendations into Runner-enforced fields.

The [evaluation guide](https://agentskills.io/skill-creation/evaluating-skills) recommends clean-context runs, observable assertions, baseline comparison, and evidence-backed grading. Generated repositories provide the test and Git boundaries for those evaluations without embedding a shared catalog.

GitHub's [Actions security guidance](https://docs.github.com/en/actions/reference/security/secure-use) recommends minimum workflow permissions and full commit SHA pins. Both template and generated CI use `contents: read` and a full SHA for checkout.

GitHub [push protection](https://docs.github.com/en/code-security/concepts/secret-security/push-protection) and [Gitleaks](https://github.com/gitleaks/gitleaks) remain remote and full-history security layers. The included local scanner is an immediate gate, not a substitute for them. CI downloads Gitleaks 8.30.1 from its [official release](https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1), verifies the published archive checksum, and scans all fetched commits with redacted output.
