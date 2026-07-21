# [AIALRA-SKILL-TEMPLATE](https://github.com/AIALRA-0/AIALRA-SKILL-TEMPLATE)

一个通用的、可执行的 Agent Skill 仓库模板。它统一每个 Skill 必须遵循的运行协议：

- 图驱动工作流：使用明确的节点和有向边定义执行步骤、先后顺序与状态转换，使每次运行都遵循同一条可检查、可追踪的工作流。
- 结构化输入输出：使用 Schema 约束初始输入、节点输出和最终结果，使 Agent、脚本与外部工具之间通过明确的数据契约协作。
- 确定性执行：将固定、重复、可计算的操作交给参数化脚本执行，并将外部工具调用和语义判断限制在节点声明的范围内。
- 失败回退：为每个节点声明超时、最大重试次数、预定义回退节点、用户等待状态和停止条件，使失败按照受控路径处理。
- 最终验证：在节点执行后校验输出，并在工作流完成前执行最终 Schema 与 Validator 检查，只有通过验证的结果才能交付。
- 受控学习：每次运行后记录一条脱敏、限定范围的经验或教训，定期压缩活跃规则并完整归档原始事件，核心规则只能经过审查、测试和版本变更后更新。
- 独立 Git：每个 Skill 使用独立仓库管理提交历史、版本、测试、发布和回滚，使其能够单独演进并保持可追溯性。

## 核心模型

每个 Skill 都是一个独立 Git 仓库，由本模板生成。仓库中只有一个 Skill，不使用 catalog，也不使用多 profile。

```text
用户请求
   ↓
输入 Schema
   ↓
Runner 读取 workflow.yaml
   ↓
节点执行 → 节点输出 Schema → Validator
   ↓              ↘ retry / fallback / wait-user / stop
最终 Schema + Final Validator
   ↓
交付结果
   ↓
一条脱敏经验或教训 → ledger → archive + bounded active rules
```

Agent 不能自行决定下一个节点。Runner 保存状态、控制顺序、限制重试和总时长、执行脚本节点、阻止未经确认的写操作，并验证每个节点和最终输出。

## 执行器优先级

1. `script`：固定、重复、可计算的机械操作，由 Runner 直接执行。
2. `mcp`：使用明确工具和参数 Schema，不额外套脆弱脚本。
3. `browser-dom`：API/MCP 不足时使用结构化页面操作。
4. `computer-use`：只有无法结构化操作时使用；登录和验证码由用户完成。
5. `reasoning`：只用于无法脚本化的语义判断，仍必须返回 Schema 合规 JSON。

## 单 Skill 仓库结构

```text
my-skill/
├── .git/
├── .core-lock.json
├── AGENTS.md
├── VERSION
├── .agents/skills/my-skill/
│   ├── SKILL.md
│   ├── workflow.yaml
│   ├── agents/openai.yaml
│   ├── schemas/
│   └── scripts/
│       ├── runner.py
│       ├── runtime_lib.py
│       ├── learn.py
│       ├── compact.py
│       ├── promote.py
│       ├── freeze_core.py
│       └── validate_repo.py
├── learning/
│   ├── ledger.jsonl
│   ├── active-rules.json
│   ├── archive/
│   └── proposals/
├── scripts/
├── tests/
└── .github/workflows/validate.yml
```

领域需要时才添加 `executors/`、`validators/`、`references/` 或 `assets/`，不预先制造空目录和文档。

## 创建独立 Skill 仓库

```bash
python3 scripts/create_skill_repo.py \
  --name shopping-price-research \
  --output ../shopping-price-research \
  --display-name "Shopping Price Research" \
  --short-description "Compare live prices with verified evidence" \
  --description "Research current product offers with direct evidence. Use when the user asks for live price comparison or link verification. Do not use for purchasing actions or historical-price prediction." \
  --default-prompt 'Use $shopping-price-research to compare current offers for this exact product.'
```

生成器会：

- 优先调用 Codex 内置 `skill-creator` 官方初始化器；
- 创建新的独立 Git 仓库；
- 写入统一 Runner、学习系统、安全策略、测试和 CI；
- 生成核心 SHA-256 锁；
- 让工作流保持 `configured=false`，在领域图和回归测试完成前拒绝运行。

## 固化与成长

稳定核心包括工作流、Schema、脚本、验证器、Skill 指令、安全策略和强制执行文件。`.core-lock.json` 记录它们的哈希；任何未登记变更都会让 Runner 硬停止。

每次执行后只记录一条脱敏、限定 scope 的经验或教训。默认累计 32 条时：

- 原始事件完整移动到 `learning/archive/`，不依赖“已经提交到 Git”才保留；
- 重复规则被确定性合并，保留正负计数和事件哈希；
- 活跃规则最多 16 条，即活跃上下文减半；
- 未进入活跃集合的事件仍在归档和 Git 历史中，不丢失；
- 学习规则只能作为 advisory，不能改变流程、权限或安全边界。

晋升到核心只生成 proposal，不自动修改核心。至少需要 3 个独立支持案例，或一次用户确认的严重安全事件，并完成反例审查、回归测试、版本变更、人工批准和重新冻结。

## 验证模板自身

```bash
python3 scripts/validate_template.py
python3 -m unittest discover -s tests -v
python3 scripts/check_secrets.py
```

详细协议见 [docs/architecture.md](docs/architecture.md)，学习机制见 [docs/learning.md](docs/learning.md)，从 v0.1 迁移见 [docs/migration-v0.2.md](docs/migration-v0.2.md)。
