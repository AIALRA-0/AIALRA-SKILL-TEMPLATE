# Research notes

Reviewed 2026-07-20. These notes explain the framework decisions and should be refreshed when Codex or the Agent Skills specification changes.

## Codex loading and distribution

OpenAI's [Build skills](https://developers.openai.com/codex/build-skills) documentation states that Codex first sees Skill name, description, and path, then loads `SKILL.md` only after selection. The initial Skill list is limited to 2% of the model context window, or 8,000 characters when the context size is unknown. This makes short, front-loaded routing descriptions and a controlled Skill count architectural requirements, not style preferences.

The same page documents `.agents/skills` as the repository discovery location and distinguishes direct Skill authoring from plugin distribution. The [Customization overview](https://developers.openai.com/codex/customization/overview) recommends `AGENTS.md` for durable repository conventions, Skills for reusable workflows, and MCP for external systems. This framework therefore keeps mandatory authoring rules in `AGENTS.md`, workflows in Skills, and authenticated live capabilities out of static Skill instructions.

OpenAI's [Agents SDK maintenance case study](https://developers.openai.com/blog/skills-agents-sdk) reports a practical pattern of narrow Skills with clear triggers and concrete outputs, enforced at the right times by short `AGENTS.md` rules. It also recommends keeping interpretation with the model and moving repeated deterministic mechanics into scripts.

## Format and progressive disclosure

The [Agent Skills specification](https://agentskills.io/specification) requires `SKILL.md`, a kebab-case name of at most 64 characters, and a description of at most 1,024 characters. It recommends keeping `SKILL.md` below 500 lines, keeping references one level deep, and using `scripts/`, `references/`, and `assets/` on demand.

The open specification permits optional frontmatter fields, but Codex's current built-in `skill-creator` requires only `name` and `description` for Codex-authored Skills. The framework follows the narrower Codex contract and keeps version, ownership, maturity, risk, and evaluation metadata in `catalog/`.

The [Skill creator best-practices guide](https://agentskills.io/skill-creation/best-practices) warns that Skills generated without real domain context tend to become vague. It recommends grounding them in actual artifacts, corrections, failure cases, and execution traces; using validation loops; and selecting defaults instead of presenting menus of equivalent choices. This is why the framework has no generic profile and requires profile-specific failure controls.

## Routing and task evaluation

The [description optimization guide](https://agentskills.io/skill-creation/optimizing-descriptions) recommends realistic positive and near-miss negative prompts, approximately 8–10 of each, multiple runs because routing is nondeterministic, and a fixed train/validation split to avoid overfitting. This framework requires 8 positive and 8 negative cases for candidate or stable Skills, records three runs per query by default, and generates a 60/40 split.

The [Skill evaluation guide](https://agentskills.io/skill-creation/evaluating-skills) recommends comparing a Skill against no Skill or a previous version, using observable assertions with evidence, and measuring the quality delta together with time and token cost. The catalog therefore records baseline state, last evaluation date, run count, and a summary; candidate and stable states cannot claim an unrun baseline.

## Security and reproducibility

GitHub documents [push protection](https://docs.github.com/en/code-security/concepts/secret-security/push-protection) as a preventive control that blocks supported secrets before they enter a repository. It is stronger than a `.gitignore` or a post-commit scan, so remote push protection remains required even though this repository ships a local scanner.

GitHub's [Actions security guidance](https://docs.github.com/en/actions/reference/security/secure-use) recommends least-privilege workflow permissions and full commit SHA pins for immutable third-party Action references. The validation workflow grants only `contents: read` and pins `actions/checkout` to a verified full SHA. Dependabot is configured to propose controlled updates.

[Gitleaks](https://github.com/gitleaks/gitleaks) supports working-tree and Git-history scans plus pre-commit integration. The included dependency-free scanner gives immediate baseline protection; Gitleaks remains the recommended full-history layer.

The framework and each Skill use [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html). A Skill's public API is interpreted as its trigger boundary, required inputs, observable outputs, safety/side-effect behavior, and declared dependencies.
