# 模板设计的研究依据

## 这份文档解决什么问题

这份文档记录模板设计依据、采用方式和复查日期；

它帮助维护者区分外部规范、模板自己的设计选择和未来需要重新验证的内容；

适合阅读这份文档的人是架构审计者、来源复查者和准备改变模板依据的维护者；

读完以后，你应该能够找到每项主要设计的来源，并判断何时需要重新复查；

日常创建 Skill 时不需要阅读这份文档；

最后复查日期为 2026-07-20；

## OpenAI Skill 构建文档

来源为 [Skill 构建文档](https://developers.openai.com/codex/build-skills)；

该文档把 Skill 定义为针对特定任务的指令，并允许 Skill 附带脚本和参考资料；

该文档采用渐进式披露原则，并建议每个 Skill 聚焦一项工作；

该文档还说明 `.agents/skills` 是仓库级 Skill 的发现位置；

本模板据此让每个生成后的仓库只包含一个 Skill，并把 `SKILL.md` 保持为简短运行入口；

## OpenAI 自定义功能概览

来源为 [自定义功能概览](https://developers.openai.com/codex/customization/overview)；

该文档区分持久仓库指导、Skill 和 MCP；

`AGENTS.md` 承载仓库规则，Skill 定义可重复工作流，MCP 提供实时外部能力；

本模板据此把仓库维护规则放入 `AGENTS.md`，把执行协议放入 Skill，把实时外部操作交给工作流节点指定的执行器；

## OpenAI Agents SDK 维护案例

来源为 [Agents SDK 维护案例](https://developers.openai.com/blog/skills-agents-sdk)；

该案例建议明确触发条件和具体输出；

它还建议把重复、确定性的机械操作迁移到脚本，把需要结合上下文的判断保留给模型；

本模板据此区分 `script`、`mcp`、`browser-dom`、`computer-use` 和 `reasoning` 节点；

## Agent Skills 最佳实践

来源为 [Agent Skills 最佳实践指南](https://agentskills.io/skill-creation/best-practices)；

该指南建议根据流程脆弱程度调整控制强度，建立验证循环，提供稳定默认值，并从真实执行中学习；

本模板据此使用 Schema、validator、重试、回退、停止条件、确认关卡和受控学习机制；

## Agent Skills 评估指南

来源为 [评估指南](https://agentskills.io/skill-creation/evaluating-skills)；

该指南建议使用干净上下文、可观察断言、基线比较和基于证据的评分；

本模板据此让每个 Skill 拥有独立测试边界和 Git 边界，并要求学习结论带有受控证据；

本模板没有引入共享 catalog，因为独立仓库已经提供发布、回滚和审计边界；

## GitHub Actions 安全指南

来源为 GitHub 的 [Actions 安全指南](https://docs.github.com/en/actions/reference/security/secure-use)；

该指南建议工作流使用最小权限，并使用完整提交 SHA 固定第三方 Actions；

模板工厂和生成后的 CI 都使用 `contents: read`，并通过完整提交 SHA 固定 checkout 动作；

## GitHub 推送保护

来源为 GitHub 的 [推送保护说明](https://docs.github.com/en/code-security/concepts/secret-security/push-protection)；

推送保护可以在凭据进入远端历史前阻止推送；

本模板建议同时启用远端密钥扫描和推送保护；

本地扫描器是即时关卡，不能替代远端保护和完整历史扫描；

## Gitleaks

来源为 [Gitleaks 项目](https://github.com/gitleaks/gitleaks)和 [Gitleaks 8.30.1 官方 Release](https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1)；

CI 从官方 Release 下载固定版本，验证官方归档校验和，并以脱敏方式扫描已获取的完整提交历史；

固定版本和校验和用于降低供应链内容被静默替换的风险；

## 复查规则

以下情况出现时需要重新检查相关来源；

- OpenAI 改变 Skill 的发现位置或文件格式；
- Codex 改变 `AGENTS.md`、Skill 或 MCP 的职责；
- Agent Skills 规范改变建议字段或评估方法；
- GitHub Actions 权限模型发生变化；
- Gitleaks 固定版本停止维护或出现安全问题；

复查后更新日期，并在 `CHANGELOG.md` 中记录对模板行为造成的变化；
