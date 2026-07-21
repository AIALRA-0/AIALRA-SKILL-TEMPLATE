# Runtime 架构

## 一个模板、一套协议、每个仓库一个 Skill

本模板统一的是执行语义，而不是领域章节。每个生成的仓库只包含一个可被发现的 Skill，并拥有一套独立的 Git 历史。

领域作者在 `SKILL.md` 中定义最小支持意图，并将实际行为编码为 `workflow.yaml` 中的节点。整个架构不存在 catalog 或 profile 选择层。

## 工作流 IR

`workflow.yaml` 使用兼容 JSON 的 YAML，因此 Runtime 不依赖 YAML 解析器。YAML 工具仍然可以读取该文件，而 Runtime 则使用 Python 标准库的 JSON 解析器进行确定性解析。

顶层契约如下：

```json
{
  "ir_version": 1,
  "skill_name": "example-skill",
  "configured": true,
  "entry_node": "normalize-input",
  "limits": {
    "max_nodes": 16,
    "total_timeout_seconds": 1800
  },
  "learning": {
    "compact_every": 32,
    "active_rule_limit": 16
  },
  "nodes": [],
  "final_output_schema": "schemas/final.schema.json",
  "final_validator": null
}
```

每个节点都必须声明：

- 稳定的 kebab-case `id`；
- 输入和输出 Schema；
- 一个执行器；
- 精确的脚本 argv，或者外部动作契约；
- 副作用类别和确认要求；
- 超时时间和重试上限；
- 可选的确定性 validator；
- 成功边、回退边和停止条件。

成功边或回退边都不允许形成环路，而且每个节点都必须可以从入口节点到达。需要重复执行时，应使用有界重试，而不是开放式循环。

文本停止条件用于约束外部执行器，并且必须出现在 Runner 发出的每一条指令中。能够由机器判定的条件必须写入输入/输出 Schema 或 validator；不得把普通文本描述伪装成 Runner 能够确定性执行的判断。

## Runner 状态机

Runner 支持以下状态转换：

```text
running
  ├── script 节点 ── 校验 ── 下一节点 / completed
  ├── 外部节点 ───────────── waiting-external
  ├── 需要确认的副作用 ───── waiting-confirmation
  ├── 需要用户操作 ───────── waiting-user
  ├── 可重试失败 ─────────── running，由 max_retries 限制
  ├── fallback ────────────── running，并进入已声明的回退节点
  └── 致命失败或重试耗尽 ─── failed
```

Runtime 状态和节点文件保存在已被忽略的 `.runtime/` 目录中。Runner 不会把完整的子进程日志写入学习数据。脚本命令必须表示为 argv 数组，并通过 `shell=false` 执行。

## 外部执行器

对于 MCP、浏览器 DOM、Computer Use 和 reasoning 节点，Runner 会发出一条结构化指令，其中包含执行器、动作、当前输入、输出 Schema、副作用类别、确认状态、超时时间、停止条件和建议规则。Agent 只能执行该指令声明的动作，并且必须提交结构化 JSON。

MCP 始终作为原生执行器使用。将 MCP 再包装进 shell 脚本只会增加故障点，并不能提高确定性。

## 核心锁

`.core-lock.json` 对以下内容计算哈希：

- `AGENTS.md`、`VERSION` 和 `SECURITY.md`；
- 强制执行配置和 CI 工作流；
- 根目录下的验证与安全脚本；
- Runtime Skill 内的每一个文件。

Runner 会在开始或恢复执行前验证这份清单。学习数据、测试、README 文件和被忽略的 Runtime 状态不属于稳定核心。修改核心必须经过审查、测试、版本决策，并重新生成核心锁。

核心锁用于检测漂移，而不是授权或真实性边界，因为拥有本地写权限的进程可以重新生成它。应通过已审查的提交、受保护分支、必要时的签名发布，以及固定依赖版本的 CI 来建立来源可信度。同样，Runner 的确认暂停只记录协议关卡；在调用 `approve` 之前，宿主和 Agent 仍有责任取得用户的真实确认。

## 草稿安全

生成的新仓库包含一份结构有效、但不可执行的工作流，其 `configured=false`。这样可以防止一个通用 reasoning 节点冒充已完成的领域 Skill。只有完成领域设计和测试后，才可以将它改为 `true`。
