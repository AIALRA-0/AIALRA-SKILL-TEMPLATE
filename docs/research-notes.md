# 研究依据

审查日期：2026-07-20。

OpenAI 的 [Skill 构建文档](https://developers.openai.com/codex/build-skills) 将 Skill 定义为针对特定任务的指令，并允许附带脚本和参考资料；该文档采用渐进式披露原则，并建议每个 Skill 聚焦于一项工作。文档还规定 `.agents/skills` 是仓库级 Skill 的发现位置。

[自定义功能概览](https://developers.openai.com/codex/customization/overview) 将持久仓库指导、Skill 和 MCP 分开：`AGENTS.md` 承载仓库约定，Skill 定义可重复工作流，MCP 提供实时外部能力。生成后的模板遵循这一职责划分。

OpenAI 的 [Agents SDK 维护案例](https://developers.openai.com/blog/skills-agents-sdk) 建议使用明确的触发条件和具体输出，并把重复、确定性的机械操作迁移到脚本中，同时把需要结合上下文的判断保留给模型。

[Agent Skills 最佳实践指南](https://agentskills.io/skill-creation/best-practices) 建议根据流程脆弱程度调整控制强度，建立验证循环和固定默认值，并从真实执行中学习。本模板将这些建议转换为由 Runner 强制执行的字段。

[评估指南](https://agentskills.io/skill-creation/evaluating-skills) 建议使用干净上下文运行、可观察断言、基线比较和基于证据的评分。生成后的独立仓库为这些评估提供测试边界和 Git 边界，同时不引入共享 catalog。

GitHub 的 [Actions 安全指南](https://docs.github.com/en/actions/reference/security/secure-use) 建议采用最小工作流权限，并使用完整提交 SHA 固定依赖。模板自身和生成后的 CI 都使用 `contents: read`，并通过完整 SHA 固定 checkout 动作。

GitHub 的[推送保护](https://docs.github.com/en/code-security/concepts/secret-security/push-protection)和 [Gitleaks](https://github.com/gitleaks/gitleaks)仍然是远端及完整历史安全层。本地扫描器只是即时关卡，不能替代它们。CI 从[官方 Release](https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1)下载 Gitleaks 8.30.1，验证官方发布的归档校验和，并以脱敏输出方式扫描所有已获取的提交。
