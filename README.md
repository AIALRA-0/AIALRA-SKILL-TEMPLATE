# Codex Skill Framework

一个面向长期维护的 Codex Skill 仓库模板。它把可被 Codex 加载的运行时文件与设计、评测、版本和安全控制分开，避免把每个 Skill 做成同一种空泛模板。

## 设计结论

- 每个 Skill 只完成一个连贯任务；如果需要两套独立触发条件或两种不同输出，应拆成两个 Skill。
- 每个 Skill 必须选择一个主 profile：`research`、`tool-integration`、`artifact-production` 或 `operational-workflow`。不提供无约束的 `generic` profile。
- `.agents/skills/<name>/` 是运行平面，只保留 `SKILL.md`、`agents/openai.yaml` 和真正需要的 `scripts/`、`references/`、`assets/`。
- `catalog/<name>.json` 是控制平面的单一设计源。不要直接编辑生成的 `SKILL.md`；更新 catalog 后重新生成。
- `evals/<name>/` 存放触发测试和任务质量测试，不随 Skill 运行时内容一起分发。
- Skill 的版本放在 catalog，不放进 Codex 的 `SKILL.md` frontmatter；frontmatter 只使用 `name` 与 `description`。
- 任何令牌、Cookie、密码、私钥、真实个人资料或含敏感信息的浏览器文件都不得进入 Git。

## 仓库结构

```text
.
├── .agents/skills/              # 可被 Codex 发现的生成结果
├── catalog/                     # 每个 Skill 的设计规范与版本
├── evals/                       # 触发与输出质量评测
├── templates/profiles/          # 四种非泛化模板
├── schemas/                     # catalog JSON Schema
├── scripts/                     # 生成、验证、密钥扫描
├── tests/                       # 框架自身测试
├── docs/                        # 仓库级架构与维护说明
├── AGENTS.md                    # Codex 在本仓库必须遵循的规则
├── SECURITY.md                  # 敏感信息政策与泄露处理
└── .github/workflows/           # 最小权限 CI
```

## 快速开始

1. 从示例复制一个设计规范：

   ```bash
   cp examples/research-skill.spec.json drafts/my-skill.json
   ```

2. 填写所有领域信息，尤其是正向触发、近邻反例、非目标、工作流、失败边界和验证标准。

3. 生成新 Skill：

   ```bash
   python3 scripts/new_skill.py --spec drafts/my-skill.json
   ```

4. 添加 catalog 中声明的真实资源文件，然后验证：

   ```bash
   python3 scripts/validate_repo.py
   python3 -m unittest discover -s tests -v
   python3 scripts/check_secrets.py
   ```

5. 更新已有 Skill：

   ```bash
   python3 scripts/new_skill.py --spec catalog/my-skill.json --update
   ```

生成器会优先调用本机 Codex 内置 `skill-creator` 的官方初始化脚本；CI 或其他没有该脚本的环境使用等价的可移植初始化路径。两条路径最后都由同一渲染器生成确定性的 `SKILL.md` 与 `agents/openai.yaml`。

## Profile 选择

| Profile | 适合 | 强制回答的问题 |
|---|---|---|
| `research` | 实时调查、资料核验、价格/政策/市场研究 | 来源优先级、时效、证据字段、冲突处理 |
| `tool-integration` | MCP、API、浏览器、登录态工作流 | 能力边界、认证、读写副作用、确认点、降级路径 |
| `artifact-production` | 文档、表格、演示、PDF、图片、代码制品 | 输入检查、生成方式、渲染/运行验证、交付标准 |
| `operational-workflow` | 发布、迁移、审查、修复、运维流程 | 前置条件、阶段门、回滚、完成定义 |

如果一个 Skill 同时需要两列中互不依赖的完整流程，优先拆分，并让 `AGENTS.md` 在适当时机编排它们。

## 质量门槛

- 名称必须是 1–64 个小写字母、数字和连字符，且目录名一致。
- `description` 必须说明“做什么、何时使用、边界是什么”，并通过近邻反例测试。
- `SKILL.md` 少于 500 行，引用只保持一层深度。
- `agents/openai.yaml` 的默认提示必须显式包含 `$skill-name`。
- `candidate` 与 `stable` Skill 至少要有 8 个正向和 8 个近邻负向触发样例。
- 资源只在确实复用、能降低错误率时加入；重复且确定的机械步骤才进入脚本。
- 发布前必须通过结构验证、单元测试、敏感信息扫描和人工评测记录。

更详细的设计见 [docs/architecture.md](docs/architecture.md)，维护与版本策略见 [docs/maintenance.md](docs/maintenance.md)，调查依据见 [docs/research-notes.md](docs/research-notes.md)。

## Git 与发布建议

- 初期使用私有仓库；确认没有内部信息后再决定是否公开。
- 开启 GitHub Secret Protection / push protection；本仓库的本地扫描只能作为第一道防线。
- CI 中第三方 Action 使用完整 commit SHA；Dependabot 负责提出升级 PR。
- 仓库版本使用 SemVer。单个 Skill 也在 catalog 中独立使用 SemVer。
- 公开分发前再选择许可证；没有明确许可证时，不要假设他人可以复制或再分发。
